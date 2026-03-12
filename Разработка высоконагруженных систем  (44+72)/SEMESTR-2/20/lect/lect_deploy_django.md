# Текст лекции: Управление нагрузкой Django в production

*Презентация для студентов. Лектор: синьор, кандидат наук. Стиль: академический + сленг разработчиков, тонкий юмор. ~4–5 минут на слайд.*

---

## Слайд 1: Django в production — другая реальность

Когда вы пишете `python manage.py runserver`, Django поднимает однопоточный сервер, который сам авторы фреймворка называют «для разработки». Он не умеет обрабатывать параллельные запросы, не раздаёт статику эффективно и падает под любой осмысленной нагрузкой. На проде `runserver` — это как ехать на формуле-1 на картонном болиде.

Production — это совсем другой стек: WSGI/ASGI-сервер (gunicorn, uvicorn), reverse proxy (nginx), база данных в отдельном контейнере, переменные окружения вместо `settings.py` с хардкодом, и CI/CD пайплайн, который деплоит новую версию за 30 секунд после `git push`.

В этой лекции мы пройдём весь путь: от голого Django до оптимизированного продакшена с бенчмарками. Будет и теория, и реальные цифры.

---

## Слайд 2: Архитектура production Django

В продакшене Django никогда не стоит один. Классическая архитектура — четыре слоя:

```
Браузер → Nginx (порт 80/443) → Gunicorn (порт 8000) → Django → PostgreSQL
```

**Nginx** — принимает HTTP-запросы, раздаёт статику, терминирует SSL. **Gunicorn** — WSGI-сервер, запускает несколько воркеров Django. **Django** — бизнес-логика, ORM, шаблоны. **PostgreSQL** — база данных, а не SQLite.

Почему не напрямую? Gunicorn не умеет раздавать файлы эффективно, не понимает SSL, не защищает от slowloris-атак. Nginx делает всё это за него. Gunicorn не умеет хостить сайт — он умеет быстро обрабатывать Python-код.

Сленг: «прокси», «реверс-прокси» — Nginx перед приложением. «Воркер» — рабочий процесс Gunicorn. «Поднять стек» — запустить всю цепочку.

---

## Слайд 3: Что меняется по сравнению с dev-режимом

Давайте чётко зафиксируем разницу:

| Параметр | Development | Production |
|----------|-------------|------------|
| Сервер | `runserver` | gunicorn / uvicorn |
| База данных | SQLite | PostgreSQL / MySQL |
| Статика | Django раздаёт | Nginx раздаёт |
| DEBUG | `True` | `False` |
| ALLOWED_HOSTS | `*` | конкретный домен |
| SECRET_KEY | в settings.py | в переменной окружения |
| HTTPS | нет | Let's Encrypt |
| Логи | в консоль | в файлы / journald |

Когда `DEBUG=True`, Django при ошибке показывает полный traceback с переменными — включая пароли от базы. На проде это как оставить ключи от квартиры в замке с надписью «добро пожаловать».

`ALLOWED_HOSTS` — это не безопасность, а защита от Host header attacks. Если оставить `*`, любой может подставить свой домен в заголовок и получить невалидные ссылки в письмах.

---

## Слайд 4: settings.py для production

На проде настройки читаются из переменных окружения, а не хардкодятся:

```python
import os
import dj_database_url

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/shop',
        conn_max_age=600,
    )
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

`dj_database_url` — библиотека, которая парсит строку подключения `DATABASE_URL` в формат Django. Одна переменная вместо пяти параметров.

`conn_max_age=600` — не закрывать соединение к БД 10 минут. Экономит время на переподключение. Но с async-сервером это бомба замедленного действия — об этом позже.

`STATIC_ROOT` — папка, куда `collectstatic` соберёт все статические файлы. Nginx будет раздавать их напрямую, минуя Django.

---

## Слайд 5: Порядок деплоя Django (ручной)

Ручной деплой — это чек-лист из 8 шагов. Запомните последовательность, она одинаковая для 90% проектов:

1. **SSH на сервер** — `ssh root@81.90.182.174`
2. **Установка зависимостей** — Python, pip, venv, git
3. **Клонирование репозитория** — `git clone` в `/opt/project`
4. **Виртуальное окружение** — `python3 -m venv venv && pip install -r requirements.txt`
5. **Переменные окружения** — `.env` файл или export
6. **Миграции** — `python manage.py migrate`
7. **Статика** — `python manage.py collectstatic`
8. **Запуск** — через systemd или Docker

Каждый шаг можно автоматизировать, но логика не меняется. Если что-то не работает — идите по чек-листу сверху вниз. В 80% случаев проблема в забытом шаге.

---

## Слайд 6: Systemd — автозапуск без Docker

Если не используете Docker, Django нужно запускать через **systemd** — менеджер служб Linux. Без него закроете SSH-сессию — приложение умрёт.

```ini
[Unit]
Description=Django Shop API
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/shop
ExecStart=/opt/shop/venv/bin/gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`After=network.target` — ждать пока поднимется сеть. `Restart=always` — перезапускать при падении. `RestartSec=5` — с паузой 5 секунд (чтобы не уйти в цикл перезапусков). `bind 127.0.0.1` — слушать только локально, снаружи — только через Nginx.

Команды: `systemctl start shop`, `systemctl enable shop` (автозапуск), `journalctl -u shop -f` (логи).

---

## Слайд 7: Порядок деплоя с CI/CD

Ручной деплой — это хорошо для понимания. Но делать это каждый раз руками — это как мыть посуду в ресторане без посудомойки. CI/CD автоматизирует весь процесс:

```
git push → GitHub Actions → SSH на VPS → git pull → docker compose up
```

Пушишь в `master` — через 30 секунд новая версия уже на сервере. Без SSH-подключения, без ручных команд, без человеческого фактора.

Что для этого нужно:
1. **GitHub Secrets** — хранить пароли от сервера в зашифрованном виде
2. **Workflow файл** — `.github/workflows/deploy.yml`
3. **SSH-доступ** — GitHub Actions подключается к VPS по SSH

Сленг: «пайплайн» — цепочка действий CI/CD. «Воркфлоу» — файл с описанием пайплайна. «Секреты» — зашифрованные переменные в GitHub. «Триггер» — событие, запускающее пайплайн (push, PR, расписание).

---

## Слайд 8: GitHub Actions — deploy.yml

```yaml
name: Deploy to VPS

on:
  push:
    branches: [master]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          password: ${{ secrets.VPS_PASSWORD }}
          script: |
            cd /opt/shop
            git pull origin master
            docker compose -f docker-compose.prod.yml up --build -d
```

`on: push: branches: [master]` — запускается только при push в master. Не при создании PR, не при комментарии — только при мерже в master.

`appleboy/ssh-action` — готовый action для SSH. Подключается к VPS, выполняет скрипт. Секреты берутся из GitHub Settings → Secrets.

Этот подход — «серверная сборка»: код собирается на VPS, а не на GitHub. Для продакшена лучше собирать Docker-образ на CI и пушить в registry, но для учебных проектов — более чем достаточно.

---

## Слайд 9: GitHub Secrets — безопасность CI/CD

Секреты — это переменные, которые GitHub шифрует и не показывает в логах. Даже если кто-то форкнет ваш репозиторий, секреты не скопируются.

Settings → Secrets and variables → Actions → New repository secret:

| Имя | Значение | Зачем |
|-----|----------|-------|
| `VPS_HOST` | `81.90.182.174` | IP сервера |
| `VPS_USER` | `deploy` | SSH-пользователь |
| `VPS_PASSWORD` | `***` | SSH-пароль |

В логах Actions секреты заменяются на `***`. Но будьте внимательны: если написать `echo ${{ secrets.VPS_PASSWORD }}`, GitHub замаскирует. А если `echo ${{ secrets.VPS_PASSWORD }} | base64`, уже может не замаскировать декодированную версию.

Продвинутый подход — SSH-ключи вместо пароля. Но для старта пароль проще.

---

## Слайд 10: Docker при деплое — зачем?

Можно деплоить без Docker: virtualenv + systemd + nginx. Работает. Но есть проблемы:
- «У меня Python 3.12, а на сервере 3.9» — классика
- «Я поставил libpq-dev, а оно конфликтует с другим проектом»
- «На моём маке всё работало!»

Docker решает: вы описываете окружение в `Dockerfile`, собираете образ, и он одинаково работает везде — на маке, на линуксе, на VPS, на Kubernetes.

Для Django-проекта Docker даёт:
- **Изоляция** — PostgreSQL, Django, Redis в отдельных контейнерах
- **Воспроизводимость** — `docker compose up` и всё работает
- **Масштабирование** — легко добавить воркеры, реплики
- **Откат** — вернуться к предыдущему образу за секунду

Сленг: «контейнер» — изолированный процесс. «Образ» — шаблон для создания контейнера. «Билдить» — собирать образ. «Поднять контейнер» — запустить.

---

## Слайд 11: Dockerfile для Django

```dockerfile
FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

Ключевые моменты:
- **`python:3.14-slim`** — минимальный образ, без компиляторов и документации (~150 МБ vs ~1 ГБ для полного)
- **`libpq-dev`** — нужна для `psycopg2`. Без неё — `pip install` упадёт с ошибкой компиляции
- **`COPY requirements.txt .` отдельно** — Docker кэширует слои. Если код изменился, но зависимости — нет, `pip install` не перезапустится. Это экономит минуты при каждой сборке.
- **`collectstatic || true`** — не падать, если статика не настроена. На этапе сборки БД ещё нет.

---

## Слайд 12: docker-compose.prod.yml

```yaml
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_DB: shop
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    command: postgres -c max_connections=300
    volumes:
      - pg_data:/var/lib/postgresql/data

  web:
    build: .
    restart: unless-stopped
    ports:
      - "8080:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD:-postgres}@db:5432/shop
      DEBUG: "False"
    command: >
      sh -c "python manage.py migrate &&
             python load_data.py &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8 --threads 4"
volumes:
  pg_data:
```

Два сервиса, одна сеть. Docker создаёт DNS: сервис `db` доступен по имени `db`. Не нужен `localhost`, не нужен IP — просто `db:5432`.

---

## Слайд 13: Разбор docker-compose по строкам

| Параметр | Что делает |
|----------|-----------|
| `restart: unless-stopped` | Перезапуск при падении и после ребута сервера |
| `${DB_PASSWORD:-postgres}` | Переменная окружения с дефолтом |
| `max_connections=300` | Увеличение лимита PostgreSQL (дефолт — 100) |
| `pg_data:/var/lib/postgresql/data` | Именованный volume — данные БД переживают `docker compose down` |
| `build: .` | Собрать образ из Dockerfile в текущей директории |
| `ports: "8080:8000"` | Хост 8080 → контейнер 8000 |
| `depends_on: db` | Запускать web после db (но не ждать готовности БД!) |

Важный нюанс: `depends_on` гарантирует порядок старта контейнеров, но НЕ ждёт, пока PostgreSQL будет готов принимать подключения. Поэтому `command` начинается с `migrate` — если БД ещё не готова, команда подождёт или упадёт, и `restart: unless-stopped` перезапустит контейнер.

---

## Слайд 14: Docker volumes — где живут данные

Контейнеры эфемерны: `docker compose down` — и всё содержимое исчезает. Но данные базы должны выживать. Для этого — **volumes**.

```yaml
volumes:
  - pg_data:/var/lib/postgresql/data
```

`pg_data` — именованный volume. Docker хранит его в `/var/lib/docker/volumes/` на хосте. При `docker compose down` volume сохраняется. При `docker compose down -v` — удаляется (осторожно!).

Три типа volumes:
- **Именованные** (`pg_data:`) — управляются Docker, переживают пересоздание контейнера
- **Bind mount** (`./data:/app/data`) — монтируют папку хоста в контейнер
- **Anonymous** — создаются автоматически, привязаны к контейнеру, удаляются с ним

Для баз данных — только именованные. Для кода в development — bind mount (чтобы видеть изменения без пересборки).

---

## Слайд 15: Первый запуск на VPS

```bash
# Под root
ssh root@81.90.182.174
curl -fsSL https://get.docker.com | sh

# Создать пользователя
adduser --disabled-password deploy
usermod -aG docker deploy

# Директория проекта
mkdir -p /opt/shop && chown deploy:deploy /opt/shop

# Под deploy
su - deploy
cd /opt/shop
git clone https://github.com/user/shop.git .
docker compose -f docker-compose.prod.yml up --build -d

# Проверка
curl http://localhost:8080/api/health
# {"status": "ok"}
```

`curl -fsSL https://get.docker.com | sh` — официальный скрипт установки Docker. Один лайнер, ставит Docker Engine + Docker Compose. Для прода используйте, для банковских серверов — лучше ручная установка из репозитория.

`usermod -aG docker deploy` — добавить пользователя в группу docker, чтобы не писать `sudo` перед каждой командой.

---

## Слайд 16: Nginx — зачем он нужен Django

Gunicorn обрабатывает Python-код. Но он НЕ умеет:
- **Раздавать статику** (CSS, JS, картинки) — он для каждого файла запустит Python, это в 100 раз медленнее
- **Терминировать SSL** — HTTPS расшифровка нагружает CPU
- **Буферизовать запросы** — медленный клиент займёт воркер на всё время загрузки
- **Ограничивать rate** — защита от DDoS
- **Кэшировать ответы** — отдавать повторные запросы без обращения к Django

Nginx — это «охранник на входе». Он быстрый, легковесный, обрабатывает тысячи соединений в одном процессе (event-driven). Gunicorn — «специалист внутри», который занимается только бизнес-логикой.

Без Nginx gunicorn торчит голым в интернет. Это работает, но любой скрипт-кидди положит ваш сервис slowloris-атакой за минуту.

---

## Слайд 17: Конфиг Nginx для Django

```nginx
server {
    listen 80;
    server_name django.h1n.ru;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/shop/staticfiles/;
    }
}
```

`proxy_pass` — перенаправить запрос на Gunicorn. `proxy_set_header Host` — передать оригинальный домен (иначе Django увидит `127.0.0.1` и вернёт 400). `X-Real-IP` — передать IP клиента (иначе в логах Django все запросы — от `127.0.0.1`). `location /static/` — Nginx отдаёт статику напрямую, не трогая Django.

---

## Слайд 18: Nginx — активация и проверка

```bash
# Создать конфиг
sudo nano /etc/nginx/sites-available/django.h1n.ru

# Включить (симлинк)
sudo ln -s /etc/nginx/sites-available/django.h1n.ru /etc/nginx/sites-enabled/

# Проверить синтаксис (ОБЯЗАТЕЛЬНО!)
sudo nginx -t

# Применить без остановки
sudo systemctl reload nginx
```

**Схема sites-available / sites-enabled:** все конфиги лежат в `sites-available`, активные — симлинки в `sites-enabled`. Хотите отключить сайт — удалите симлинк, конфиг останется. Хотите включить — создайте симлинк обратно.

`nginx -t` — проверка перед применением. Если пропустить и в конфиге ошибка — `reload` уронит Nginx, и ВСЕ сайты на сервере перестанут работать. Правило: `nginx -t` перед каждым `reload`. Без исключений.

---

## Слайд 19: HTTPS — Let's Encrypt + Certbot

HTTP — открытый текст. Пароли, куки, персональные данные видны всем в цепочке. HTTPS — шифрование. Let's Encrypt — бесплатные SSL-сертификаты. Certbot — утилита для автоматического получения и обновления.

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d django.h1n.ru
```

Certbot автоматически:
- Получит сертификат (проверит, что домен указывает на этот сервер)
- Изменит конфиг Nginx (добавит `listen 443 ssl`, пути к сертификатам)
- Настроит редирект HTTP → HTTPS
- Добавит cron для автообновления (каждые 90 дней)

После этого: `https://django.h1n.ru` — зелёный замочек. Без этого браузер показывает «Не безопасно» и Google понижает в выдаче.

---

## Слайд 20: Полная схема production Django

```
Браузер → django.h1n.ru
         ↓
   DNS → 81.90.182.174 (A-запись)
         ↓
   Nginx (порт 80 → 443, SSL)
    ├── /static/ → файлы напрямую
    └── / → proxy_pass
         ↓
   Docker: Gunicorn (порт 8080)
    ├── 8 воркеров × 4 потока = 32 параллельных запроса
    └── Django ORM
         ↓
   Docker: PostgreSQL (порт 5432)
    └── max_connections=300
```

Запрос проходит 4 слоя: DNS → Nginx → Gunicorn → PostgreSQL. Каждый слой можно масштабировать независимо: добавить ещё один Nginx (load balancer), ещё один Gunicorn (горизонтальное масштабирование), реплику PostgreSQL (read replica).

Сленг: «стек» — вся эта цепочка. «Ботлнек» (bottleneck) — узкое место. «Скейлить» — масштабировать. «Горизонтально» — больше серверов. «Вертикально» — мощнее сервер.

---

## Слайд 21: Бенчмарки — зачем измерять

«Premature optimization is the root of all evil» — Дональд Кнут. Но оптимизация без измерений — это гадание на кофейной гуще. Сначала измеряем, потом оптимизируем.

Два инструмента:
- **wrk** — генератор нагрузки на C, умеет создавать тысячи соединений
- **ab** (Apache Benchmark) — классика, проще в использовании

```bash
# wrk: 4 потока, 200 соединений, 30 секунд
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

# ab: 10000 запросов, 100 параллельных
ab -n 10000 -c 100 http://81.90.182.174:8080/api/products
```

Что смотреть в результатах:
- **Requests/sec** — пропускная способность (главная метрика)
- **Latency** — время ответа (что чувствует пользователь)
- **Timeouts** — сколько запросов не дождались ответа
- **Errors** — сколько запросов получили ошибку (5xx)

---

## Слайд 22: Baseline — Gunicorn 3 воркера

Стартовая конфигурация: дефолтный Gunicorn, 3 синхронных воркера, PostgreSQL с дефолтными настройками.

```
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

Requests/sec:     50.08
Avg Latency:      1.06s
Timeouts:         1531 из 1658
Errors:           0
```

**50 запросов в секунду** при 200 соединениях. 92% запросов — таймауты. Это катастрофа.

Почему так плохо? 3 синхронных воркера — это 3 параллельных запроса. Остальные 197 соединений стоят в очереди. Каждый запрос к PostgreSQL — новое подключение (conn_max_age по умолчанию = 0). Подключение к БД — это TCP handshake + аутентификация — ~5-10 мс overhead на каждый запрос.

Это наш «замер до оптимизации» — от него будем отталкиваться.

---

## Слайд 23: Попытка 1 — uvicorn (async)

Идея: переключиться на асинхронный сервер. Django Ninja поддерживает async, uvicorn обрабатывает множество соединений в одном процессе.

```yaml
command: uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

Результат с `conn_max_age=600`:

```
Requests/sec:     55.34
Timeouts:         1418
Non-2xx responses: 1415  ← ОШИБКИ 500!
```

Стало ХУЖЕ. 1415 запросов вернули 500:
```
FATAL: sorry, too many clients already
```

`conn_max_age=600` с async-воркерами — бомба. Каждый async-поток создаёт соединение к PostgreSQL и держит его 10 минут. Потоков — сотни. PostgreSQL по умолчанию держит 100 соединений. Результат — переполнение.

**Урок:** не все «оптимизации» улучшают ситуацию. Измеряйте.

---

## Слайд 24: Попытка 2 — uvicorn + conn_max_age=0

Исправляем: закрываем соединения сразу после запроса.

```python
# settings.py
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:postgres@localhost:5432/shop',
        conn_max_age=0,  # закрывать сразу
    )
}
```

```yaml
# docker-compose.prod.yml
db:
  command: postgres -c max_connections=300
```

Результат:
```
Requests/sec:     34.00
Timeouts:         864
Errors:           0
```

Ошибки пропали, но 34 req/s — ещё хуже, чем Gunicorn с 50! Почему?

Uvicorn оборачивает синхронные ORM-вызовы Django в `sync_to_async`. Это добавляет overhead: переключение между event loop и thread pool. Для синхронных views — чистый проигрыш.

**Вывод:** uvicorn быстрее только для `async def` views. Для обычного Django ORM — gunicorn выигрывает.

---

## Слайд 25: conn_max_age — sync vs async

Почему один параметр работает по-разному:

**Gunicorn (sync), conn_max_age=600:**
```
Воркер 1 → соединение к БД (держит 10 мин, переиспользует)
Воркер 2 → соединение к БД (держит 10 мин, переиспользует)
Воркер 3 → соединение к БД (держит 10 мин, переиспользует)
= 3 соединения (стабильно)
```

**Uvicorn (async), conn_max_age=600:**
```
async task 1 → соединение (не отпускает 10 мин)
async task 2 → соединение (не отпускает 10 мин)
...
async task 200 → соединение (не отпускает 10 мин)
= 200 соединений → PostgreSQL: "too many clients"
```

В sync — 1 поток = 1 соединение, их мало. В async — event loop создаёт сотни потоков через `sync_to_async`, каждый держит соединение.

**Правило:** `conn_max_age=600` — только с sync Gunicorn. С async — либо `conn_max_age=0`, либо пул соединений (pgbouncer, django-db-connection-pool).

---

## Слайд 26: Финальная оптимизация — Gunicorn 8w + 4t

Возвращаемся к Gunicorn, но правильно настроенному:

```yaml
command: gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 8 \
    --threads 4
```

```python
conn_max_age=600  # безопасно с sync gunicorn
```

8 воркеров × 4 потока = **32 параллельных запроса**. `conn_max_age=600` переиспользует соединения — максимум 32 соединения к БД (по одному на поток).

Формула для workers: `2 × CPU_cores + 1`. На 4-ядерном VPS: `2 × 4 + 1 = 9 ≈ 8`. Потоки — `2-4` для I/O-bound задач (ORM-запросы к БД).

Больше воркеров ≠ лучше. 20 воркеров на 2-ядерном VPS будут конкурировать за CPU и работать медленнее, чем 5.

---

## Слайд 27: Результат после оптимизации

```
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products

Requests/sec:    269.32
Avg Latency:     592ms
Timeouts:        361
Errors:          0
```

Стабильный тест (меньше соединений):
```
ab -n 5000 -c 50

Requests/sec:    233.02
Avg Latency:     215ms
Timeouts:        0
Errors:          0
```

**233 req/s без ошибок и таймаутов** — стабильная пропускная способность. С 50 req/s мы выросли до 233 — в **4.7 раза**.

И всё это на одном VPS, без Redis, без кэширования, без CDN. Только правильная настройка Gunicorn и PostgreSQL.

---

## Слайд 28: Итоговое сравнение конфигураций

| Конфигурация | Req/sec | Avg Latency | Timeouts | Errors |
|---|---|---|---|---|
| Gunicorn 3 воркера | 50 | 1.06s | 1531 | 0 |
| Uvicorn 4w (conn_max_age=600) | 55 | 1.53s | 1418 | 1415 |
| Uvicorn 4w (conn_max_age=0) | 34 | 1.54s | 864 | 0 |
| **Gunicorn 8w+4t (conn_max_age=600)** | **269** | **592ms** | **361** | **0** |
| **Gunicorn 8w+4t (ab, c=50)** | **233** | **215ms** | **0** | **0** |

Выводы:
1. **Uvicorn хуже для синхронного Django ORM** — overhead на `sync_to_async`
2. **conn_max_age=600 опасен с async** — переполнение соединений
3. **Больше воркеров + потоки** — самый эффективный путь для sync Django
4. **Измеряйте, не угадывайте** — интуиция обманывает

---

## Слайд 29: Сколько пользователей выдержит

233 req/s — это абстрактная цифра. Переведём в людей:

Средний пользователь: **2-5 запросов** при загрузке страницы, затем **1 запрос каждые 5-30 секунд** при просмотре.

| Сценарий | Одновременных пользователей |
|---|---|
| Активный просмотр (5 rps на пользователя) | ~45 |
| Обычный просмотр (1 rps) | ~230 |
| Чтение с паузами (0.2 rps) | ~1000 |
| **В минуту (пиковый трафик)** | **~3000–5000 уникальных** |

Для учебного проекта на одном VPS — более чем. Для стартапа — хватит на первые месяцы. Для масштабирования — добавляйте кэш (Redis), CDN (Cloudflare), read-реплики PostgreSQL.

Следующий уровень оптимизации — это уже не конфигурация, а архитектура: кэширование, очереди задач (Celery), асинхронные views, горизонтальное масштабирование.

---

## Слайд 30: Чек-лист production Django

Перед выкаткой Django на prod — пройдите по списку:

**Безопасность:**
- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` из переменной окружения
- [ ] `ALLOWED_HOSTS` — конкретный домен
- [ ] HTTPS (Certbot)

**Производительность:**
- [ ] Gunicorn с правильным числом воркеров (`2 × CPU + 1`)
- [ ] `conn_max_age=600` (для sync)
- [ ] `collectstatic` + Nginx для статики
- [ ] PostgreSQL `max_connections` ≥ число воркеров × 2

**Надёжность:**
- [ ] `restart: unless-stopped` или systemd
- [ ] CI/CD пайплайн (GitHub Actions)
- [ ] Мониторинг (хотя бы `curl /health` по cron)
- [ ] Бэкапы базы данных

**Итог:** Production — это не «код работает». Production — это «код работает надёжно, быстро, безопасно и обновляется автоматически». Разница — как между прототипом и серийным автомобилем.

---

## Слайд 31: Инструменты профилирования Django

Мы оптимизировали Gunicorn, но это «внешняя» оптимизация — мы увеличили пропускную способность сервера. А что если тормозит сам код? N+1 запросы, медленные ORM-вызовы, неоптимальные шаблоны. Для этого нужны инструменты профилирования.

| Инструмент | Для чего | Формат ответа |
|------------|----------|---------------|
| **Django Silk** | SQL-запросы, время запросов, профилирование Python | JSON API, HTML |
| **Django Debug Toolbar** | SQL, шаблоны, кэш, сигналы, настройки | Только HTML |
| **django-querycount** | Счётчик SQL в логах (без UI) | Любой |
| **runprofileserver** | Профилирование каждого запроса в файл | Любой |
| **line_profiler / cProfile** | Построчное / функциональное профилирование Python | Скрипты |
| **django-prometheus** | Метрики для Grafana (Prometheus-формат) | Мониторинг |

Ключевой принцип: **сначала профилируйте, потом оптимизируйте**. Без замеров вы чините то, что не сломано, и игнорируете то, что на самом деле тормозит. Silk и Debug Toolbar — два главных инструмента в арсенале Django-разработчика.

---

## Слайд 32: Django Silk — профилирование API

Django Silk перехватывает каждый HTTP-запрос и записывает в БД: время выполнения, SQL-запросы, профиль Python-кода, тело запроса и ответа.

**Главное преимущество:** работает с JSON API (Django Ninja, DRF). Debug Toolbar не может — ему нужен HTML с тегом `</body>`.

Установка:
```bash
pip install django-silk
```

Подключение в `settings.py`:
```python
INSTALLED_APPS = [..., 'silk']

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',   # первым в списке!
    'django.middleware.security.SecurityMiddleware',
    ...
]

SILKY_PYTHON_PROFILER = True
SILKY_MAX_RECORDED_REQUESTS = 1000
SILKY_META = True   # замерять overhead самого Silk
```

URL-маршрут в `urls.py`:
```python
path("silk/", include("silk.urls", namespace="silk")),
```

После `python manage.py migrate` — панель доступна по `http://127.0.0.1:8000/silk/`. Сделайте пару запросов к API и заходите смотреть.

---

## Слайд 33: Silk — что смотреть в панели

Панель Silk — это три раздела, каждый отвечает на свой вопрос:

**Requests** — «Какие запросы медленные?»

| Колонка | На что смотреть |
|---------|----------------|
| Time | Общее время > 100мс — повод разобраться |
| Num. Queries | Больше 5-10 — возможна N+1 проблема |
| Time on queries | Если ≈ Time — тормозит БД, не Python |

**SQL** — «Какие SQL-запросы выполняются?»
- Текст каждого запроса
- Время выполнения
- **Дубликаты** — один и тот же SELECT выполняется 50 раз

**Profiling** — «Какие Python-функции медленные?»
- Граф вызовов — какая функция сколько CPU съела
- Помогает найти тормоза, не связанные с БД (сериализация, валидация, вычисления)

Практический пример: `GET /api/products` показывает 1 SQL-запрос за 0.8мс — отлично. `GET /api/orders` показывает 51 SQL-запрос за 120мс — N+1 проблема, надо добавить `select_related`.

---

## Слайд 34: N+1 проблема — главный враг производительности

N+1 — самый частый баг производительности в Django ORM. Silk находит его моментально.

**Как выглядит в Silk:**
```
GET /api/orders — 51 queries, 120ms

SELECT * FROM orders                          -- 1 запрос
SELECT * FROM video_cards WHERE id = 1        -- N запросов
SELECT * FROM video_cards WHERE id = 2
SELECT * FROM video_cards WHERE id = 3
... (ещё 47 штук)
```

Django делает 1 запрос на список заказов + по 1 запросу на каждый связанный товар. 50 заказов = 51 запрос. 1000 заказов = 1001 запрос.

**Исправление:**
```python
# Плохо — N+1:
orders = Order.objects.all()

# Хорошо — 2 запроса вместо 51:
orders = Order.objects.select_related('product').all()

# Для ManyToMany:
orders = Order.objects.prefetch_related('items').all()
```

`select_related` — JOIN на уровне SQL, 1 запрос. `prefetch_related` — 2 запроса, связывание в Python. Silk покажет разницу: было 51 запрос, стало 2. Время: было 120мс, стало 3мс. В 40 раз быстрее от одной строчки.

---

## Слайд 35: Silk — настройки для разных окружений

На dev Silk полезен, на проде — опасен. Он добавляет 5-10мс на каждый запрос и пишет в БД. Правильная конфигурация:

```python
# settings.py — включать только в DEBUG
if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')
    SILKY_PYTHON_PROFILER = True
    SILKY_PYTHON_PROFILER_BINARY = True
    SILKY_MAX_RECORDED_REQUESTS = 1000
```

Полезные настройки:
```python
SILKY_INTERCEPT_PERCENT = 100       # записывать 100% запросов (или 10 для sampling)
SILKY_MAX_REQUEST_BODY_SIZE = 0     # не записывать тело запроса (экономит место)
SILKY_MAX_RESPONSE_BODY_SIZE = 0    # не записывать тело ответа
SILKY_AUTHENTICATION = True         # требовать авторизацию
SILKY_AUTHORISATION = True          # только для staff-пользователей
```

Очистка данных (Silk забивает БД):
```bash
python manage.py silk_clear_request_log
```

---

## Слайд 36: Django Debug Toolbar — профилирование HTML-страниц

Debug Toolbar встраивается в HTML-страницу — боковая панель справа с разделами.

```bash
pip install django-debug-toolbar
```

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']

# urls.py
if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
```

Открываете HTML-страницу — справа появляется панель. Разделы:

| Раздел | Что показывает |
|--------|---------------|
| **SQL** | Все запросы + кнопка EXPLAIN для каждого |
| **Time** | CPU time, total time |
| **Templates** | Какие шаблоны рендерились, контекст переменных |
| **Cache** | Hit/miss кэша |
| **Signals** | Django-сигналы и обработчики |
| **Static files** | Загруженные CSS/JS файлы |

**Ограничение:** работает ТОЛЬКО с HTML-ответами. Для JSON API (`/api/products`) — панель не появится. Для этого есть Silk.

---

## Слайд 37: Debug Toolbar — SQL и EXPLAIN

Главный раздел — **SQL**. Кликните на него и увидите:

```
2 queries in 1.5ms

SELECT ⋯ FROM "video_cards"               0.8ms
SELECT ⋯ FROM "django_session" WHERE ⋯    0.3ms
```

Для каждого запроса есть кнопка **Explain**. Нажимаете — видите план выполнения PostgreSQL:
```
Seq Scan on video_cards  (cost=0.00..1.05 rows=5 width=...)
```

`Seq Scan` на 5 строках — нормально. `Seq Scan` на 100 000 строках — нужен индекс. `Index Scan` — PostgreSQL использует индекс, запрос быстрый.

Ещё Debug Toolbar подсвечивает **Similar** и **Duplicate** запросы. Similar — запросы с одинаковой структурой, но разными параметрами (могут быть N+1). Duplicate — полностью идентичные запросы (точно баг).

Когда панель не появляется: ответ не HTML, IP не в `INTERNAL_IPS`, `DEBUG = False`, в шаблоне нет `</body>`. Это четыре причины и других нет — проверяйте по списку.

---

## Слайд 38: django-querycount и runprofileserver

Два лёгких инструмента, когда Silk и Debug Toolbar — overkill.

**django-querycount** — middleware, который пишет в логи количество SQL-запросов:
```bash
pip install django-querycount
```
```python
MIDDLEWARE += ['querycount.middleware.QueryCountMiddleware']
```
В логах: `[QueryCount] 3 queries in 2.1ms`. Без UI, без БД — просто строчка в консоли на каждый запрос. Идеально для быстрой проверки: «а сколько запросов делает этот endpoint?»

**runprofileserver** (из django-extensions) — запускает dev-сервер с cProfile:
```bash
pip install django-extensions
python manage.py runprofileserver --use-cprofile --prof-path=/tmp/profiles/
```
Каждый запрос сохраняется как `.prof` файл. Открываете в `snakeviz`:
```bash
pip install snakeviz
snakeviz /tmp/profiles/GET.api.products.prof
```
В браузере — интерактивный flamegraph: какие функции сколько CPU заняли. Полезно для тяжёлых вычислений, сериализации, обработки файлов.

---

## Слайд 39: cProfile, line_profiler, django-prometheus

**cProfile** — встроенный профилировщик Python. Показывает время каждой функции:
```python
import cProfile
cProfile.run('my_function()', sort='cumulative')
```
Выдаёт таблицу: функция, количество вызовов, время. Грубый, но бесплатный и всегда доступен.

**line_profiler** — построчное профилирование (какая строка сколько заняла):
```bash
pip install line_profiler
```
```python
@profile
def list_products(request):
    products = VideoCard.objects.all()  # 0.3ms
    data = serialize(products)           # 12.5ms  ← bottleneck!
    return data
```
Декоратор `@profile` + команда `kernprof -l -v script.py`. Показывает время КАЖДОЙ строки. Незаменим, когда нужно найти конкретную строку, которая тормозит.

**django-prometheus** — экспорт метрик для мониторинга:
```bash
pip install django-prometheus
```
Эндпоинт `/metrics` отдаёт данные в формате Prometheus: количество запросов, латенси, ошибки, SQL-запросы. Подключаете Grafana — и видите графики в реальном времени. Это уже не отладка, а мониторинг production.

---

## Слайд 40: Silk vs Debug Toolbar — когда что использовать

| Критерий | Django Silk | Django Debug Toolbar |
|----------|-------------|---------------------|
| **JSON API** | Да | Нет |
| **HTML-страницы** | Да | Да |
| **История запросов** | Да (хранит в БД) | Нет (только текущий) |
| **SQL-анализ** | Да + дубликаты | Да + EXPLAIN |
| **Профилирование Python** | Да (cProfile) | Нет |
| **Шаблоны и контекст** | Нет | Да |
| **Кэш** | Нет | Да |
| **Overhead** | ~5-10мс | ~2-5мс |
| **Нужна БД** | Да (миграции) | Нет |

**Рекомендация:** используйте оба одновременно. Silk — для API и истории запросов. Debug Toolbar — для HTML-страниц и EXPLAIN. Вместе они покрывают 95% задач профилирования.

В production не забудьте отключить оба — через `if DEBUG`. Silk пишет в базу на каждый запрос. Debug Toolbar показывает внутренности приложения. На проде это и тормоз, и дыра в безопасности.

---

## Слайд 41: Как использовать связку инструментов правильно

Каждый инструмент закрывает свой этап жизненного цикла приложения. Не нужно выбирать один — нужно использовать правильный в правильный момент:

| Цель | Инструмент | Когда |
|------|-----------|-------|
| Быстрый анализ запроса при разработке | Debug Toolbar / Silk | dev, каждый день |
| Найти «горячие» места в коде | line_profiler / cProfile | dev, при обнаружении тормозов |
| Мониторинг производительности в проде | Prometheus + Grafana | prod, 24/7 |
| Алерты при ухудшении метрик | Prometheus Alertmanager + Grafana | prod, автоматически |
| История performance и SLA-метрики | Grafana Dashboards | prod, ретроспективы |

**Цепочка на практике:**

```
1. Разработка    →  Debug Toolbar + Silk
                    (нашли N+1, медленный запрос)

2. Локальная     →  line_profiler / cProfile
   оптимизация      (нашли строку, которая тормозит)

3. Деплой        →  django-prometheus
                    (метрики экспортируются в /metrics)

4. Мониторинг    →  Grafana дашборд
                    (графики latency, rps, ошибок)

5. Инцидент      →  Alertmanager → Telegram/Slack
                    ("p95 latency > 500ms, check it")
```

На dev — профилируете и чините. На prod — мониторите и реагируете. Silk и Debug Toolbar на проде отключены, Prometheus и Grafana на dev не нужны. Каждый инструмент на своём месте — и вы спите спокойно.
