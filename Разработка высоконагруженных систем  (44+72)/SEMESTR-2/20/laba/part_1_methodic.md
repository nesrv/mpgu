# CI/CD: GitHub Actions → VPS

## Схема работы

```
git push → GitHub Actions → SSH на VPS (deploy user) → git pull → docker compose up
```

Пушишь в `master` — через ~30 сек новая версия уже на сервере.

---

## 1. Первоначальная настройка VPS (один раз, под root)

### Подключиться к VPS:
```bash
ssh root@81.90.182.174
```

### Установить Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

### Создать пользователя (если ещё нет) и дать доступ к Docker:
```bash
id alekseeva || adduser --disabled-password --gecos "" alekseeva
echo "alekseeva:alekseeva" | chpasswd
usermod -aG docker alekseeva
```

### Создать директорию проекта и отдать deploy:
```bash
mkdir -p /opt/shop
chown alekseeva:alekseeva /opt/shop
```

### Переключиться на deploy и склонировать:
```bash
su - alekseeva
cd /opt/shop
git clone https://github.com/nesrv/cd-cd-django-ninja.git .
```

### Запустить:
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Проверить:
```bash
curl http://localhost:8080/api/health
# {"status": "ok"}
```

Сайт доступен по адресу: `http://81.90.182.174:8080`

---

## 2. Настройка GitHub Secrets

В репозитории на GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Добавить три секрета:

| Имя              | Значение          |
|------------------|-------------------|
| `VPS_HOST`       | `81.90.182.174`   |
| `VPS_USER`       | `alekseeva`       |
| `VPS_PASSWORD`   | `alekseeva`       |

---

## 3. Как работает деплой

После настройки — всё автоматически:

1. Делаешь `git push origin master`
2. GitHub Actions подключается к VPS по SSH
3. Выполняет `git pull` + `docker compose up --build -d`
4. Новая версия запущена

### Файл workflow: `.github/workflows/deploy.yml`

---

## 4. Полезные команды на VPS

```bash
# Посмотреть логи
docker compose -f docker-compose.prod.yml logs -f

# Перезапустить
docker compose -f docker-compose.prod.yml restart

# Остановить
docker compose -f docker-compose.prod.yml down

# Пересобрать с нуля
docker compose -f docker-compose.prod.yml up --build -d

# Зайти в контейнер Django
docker compose -f docker-compose.prod.yml exec web bash

# Зайти в PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U postgres shop
```

---

## 5. Структура файлов

```
docker-compose.yml        ← для локальной разработки (порт 8000)
docker-compose.prod.yml   ← для VPS (порт 8080)
Dockerfile                ← сборка Django-приложения
.github/workflows/deploy.yml  ← CI/CD pipeline
```

---

## Бенчмарки

```bash
ab -n 10000 -c 100 http://81.90.182.174:8080/api/products
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/health
```

### Результат wrk (gunicorn, 3 воркера, PostgreSQL):

```
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

  4 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.06s   560.98ms   1.99s    60.63%
    Req/Sec    17.51     11.34    60.00     59.31%
  1658 requests in 33.11s, 2.54MB read
  Socket errors: connect 0, read 0, write 0, timeout 1531
Requests/sec:     50.08
Transfer/sec:     78.45KB
```

### Результат ab (gunicorn, 3 воркера, PostgreSQL):

```
ab -n 10000 -c 100 http://81.90.182.174:8080/api/products

Server Software:        gunicorn
Concurrency Level:      100
Time taken for tests:   301.733 seconds
Complete requests:      10000
Failed requests:        0
Requests per second:    33.14 [#/sec] (mean)
Time per request:       3017.333 [ms] (mean)

  50%   2084
  66%   2359
  75%   3217
  90%   5224
  95%   7192
  99%  13388
 100%  17572 (longest request)
```

**Проблемы:**
- **50 req/s** — мало, 1531 таймаут из 1658 запросов
- 3 синхронных воркера Gunicorn не справляются с 200 соединениями
- Нет пула соединений к PostgreSQL — каждый запрос открывает новое подключение

---

## Оптимизация

### 1. Увеличить воркеры и переключить на uvicorn (асинхронный режим)

В `docker-compose.prod.yml` заменить command:
```yaml
command: >
  sh -c "python manage.py migrate &&
         python load_data.py &&
         uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4"
```

Django Ninja нативно поддерживает async — uvicorn обрабатывает множество соединений в одном процессе без блокировки.

### 2. Первый результат uvicorn (с ошибкой conn_max_age=600):

```
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

  4 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.53s   276.58ms   2.00s    70.64%
    Req/Sec    20.06     15.95   110.00     78.83%
  1837 requests in 33.19s, 1.21MB read
  Socket errors: connect 0, read 0, write 0, timeout 1418
  Non-2xx or 3xx responses: 1415
Requests/sec:     55.34
```

**Проблема:** 1415 запросов вернули ошибку 500:
```
FATAL: sorry, too many clients already
```

`conn_max_age=600` с async-воркерами держит соединения открытыми — каждый async-поток
создаёт соединение и не отпускает его 10 минут. PostgreSQL (по умолчанию 100 соединений)
быстро исчерпывается.

### 3. Исправление: conn_max_age=0 + max_connections

В `settings.py`:
```python
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/shop',
        conn_max_age=0,  # закрывать соединение сразу после запроса
    )
}
```

В `docker-compose.prod.yml` — увеличить лимит PostgreSQL:
```yaml
db:
  image: postgres:17
  command: postgres -c max_connections=300
```

**Почему `conn_max_age=0` для async:**
- Gunicorn (sync) — `conn_max_age=600` работает, т.к. 1 поток = 1 соединение
- Uvicorn (async) — пул потоков создаёт много соединений параллельно,
  `conn_max_age=600` не даёт их закрыть → переполнение

### 4. Вывод: uvicorn хуже для синхронных views

```
wrk -t4 -c200 -d30s (uvicorn, 4 воркера, conn_max_age=0)

Requests/sec:     34.00
Timeouts:         864
```

Uvicorn оборачивает sync ORM-вызовы в `sync_to_async` — лишний overhead.
Для синхронных views **gunicorn быстрее**.

### 5. Финальная оптимизация: gunicorn 8 воркеров + 4 потока + conn_max_age=600

```yaml
# docker-compose.prod.yml
command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8 --threads 4
```

```python
# settings.py
conn_max_age=600  # безопасно с sync gunicorn
```

8 воркеров × 4 потока = 32 параллельных запроса.
`conn_max_age=600` переиспользует соединения к БД.

### 6. Результат после оптимизации

```
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

  4 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   591.63ms  495.56ms   1.78s    52.46%
    Req/Sec    82.85     35.78   191.00     66.50%
  8485 requests in 31.50s, 13.02MB read
  Socket errors: connect 0, read 0, write 0, timeout 361
Requests/sec:    269.32
Transfer/sec:    423.18KB
```

### Стабильный тест (ab, 50 соединений):

```
ab -n 5000 -c 50 http://81.90.182.174:8080/api/products

Server Software:        gunicorn
Concurrency Level:      50
Complete requests:      5000
Failed requests:        0
Requests per second:    233.02 [#/sec] (mean)
Time per request:       214.576 [ms] (mean)

  50%    107
  66%    130
  75%    149
  80%    166
  90%    310
  95%   1096
  99%   2147
```

### Итоговое сравнение

| Конфигурация                          | Req/sec | Avg Latency | Timeouts | Errors |
|---------------------------------------|---------|-------------|----------|--------|
| Gunicorn 3 воркера                    | 50      | 1.06s       | 1531     | 0      |
| Uvicorn 4 воркера (conn_max_age=600)  | 55      | 1.53s       | 1418     | 1415   |
| Uvicorn 4 воркера (conn_max_age=0)    | 34      | 1.54s       | 864      | 0      |
| **Gunicorn 8w + 4t (conn_max_age=600)** | **269** | **592ms** | **361** | **0** |
| **Gunicorn 8w + 4t (ab, c=50)**       | **233** | **215ms**  | **0**   | **0** |

---

## Сколько пользователей выдержит

**233 req/s** — стабильная пропускная способность без ошибок.

Средний пользователь делает **2-5 запросов** при загрузке страницы,
затем **1 запрос каждые 5-30 секунд** при просмотре.

| Сценарий                    | Одновременных пользователей |
|-----------------------------|-----------------------------|
| Активный просмотр (5 rps)   | ~45                         |
| Обычный просмотр (1 rps)    | ~230                        |
| Чтение с паузами (0.2 rps)  | ~1000                       |
| **В минуту (пиковый трафик)** | **~3000–5000 уникальных**  |
