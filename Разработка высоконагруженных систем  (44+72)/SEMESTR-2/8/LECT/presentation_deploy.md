# Презентация: Деплой Python-проектов (40–60 слайдов)

## Слайд 1

# Деплой Python-проектов: Django & FastAPI

### Цели изучения
- Понять модели деплоя
- Выбрать подход под задачу
- Разобраться «под капотом»
- Получить базу для продакшена

---

## Слайд 2

# Что такое деплой

Процесс доставки приложения в production

Делает приложение доступным пользователям

Включает:

* сервер
* окружение
* конфигурацию
* безопасность

---

## Слайд 3

# 1. Введение в деплой

### Что такое деплой?

**Deploy** — развёртывание приложения на сервер для доступа пользователей.

- Это **не** `python manage.py runserver`
- Это **production** — боевое окружение
- Требует: стабильность, безопасность, масштабируемость

### Зачем изучать деплой

* Код ≠ работающий сервис
* Ошибки чаще всего именно в деплое
* Понимание деплоя = уверенность разработчика

---

## Слайд 4

# Чем production отличается от dev?

| Аспект        | Development           | Production              |
| ------------- | --------------------- | ----------------------- |
| Сервер       | localhost             | Удалённый сервер        |
| Отладка      | Включена              | Отключена               |
| HTTPS        | Часто нет             | Обязателен              |
| Перезапуск   | Вручную               | Автоматически           |
| Логи         | Консоль               | Файлы / система         |

---

## Слайд 5

# Компоненты продакшен-архитектуры

```
Browser
   ↓
Nginx (reverse proxy, статика)
   ↓
Gunicorn / Uvicorn (ASGI/WSGI сервер)
   ↓
Django / FastAPI приложение
   ↓
PostgreSQL, Redis, ...
```

---

## Слайд 6

# Ключевые роли

- **Web-сервер (Nginx)** — принимает HTTP, раздаёт статику, проксирует в приложение
- **Application server (Gunicorn/Uvicorn)** — запускает Python-код
- **База данных** — хранение данных
- **Переменные окружения** — секреты, настройки (не в коде!)

## Этапы деплоя

* Подготовка кода
* Сборка окружения
* Настройка сервера
* Запуск приложения
* Мониторинг и обновления
---

## Слайд 7

# 2. Особенности деплоя Python-проектов

### Почему Python — особенный?

- **Интерпретируемый** — нужен runtime
- **Зависимости** — pip, virtualenv, poetry, uv
- **Миграции** — Django, Alembic
- **Статика** — сборка фронта, collectstatic

---

## Слайд 8

# Типичные шаги деплоя Python

1. Установить Python + зависимости
2. Настроить виртуальное окружение
3. Применить миграции
4. Собрать статику (Django)
5. Запустить ASGI/WSGI сервер
6. Настроить reverse proxy
7. Выставить переменные окружения

---

## Слайд 9

# 3. Uvicorn & Gunicorn

### Зачем нужен отдельный сервер?

`runserver` — только для разработки!

- Не масштабируется
- Не поддерживает HTTPS
- Однопоточный (Django)
- Не production-ready

---

## Слайд 10

## WSGI vs ASGI

* WSGI — синхронный стандарт
* ASGI — асинхронный стандарт
* Выбор влияет на сервер и архитектуру


# Gunicorn (WSGI)

- **WSGI** — стандарт для синхронных приложений (Django, Flask)
- Работает с несколькими worker-процессами
- Стабильный, проверенный временем

```bash
gunicorn myproject.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4
```

---

## Слайд 11

# Uvicorn (ASGI)

- **ASGI** — асинхронный стандарт (FastAPI, Starlette)
- Поддержка WebSocket, HTTP/2
- Один процесс, много задач (async)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```


## Gunicorn + Uvicorn workers

Комбинация:

* Gunicorn = менеджер процессов
* Uvicorn = async worker

Часто в production
---

## Слайд 12

### Что такое сервер приложения

* Запускает Python-код
* Обрабатывает HTTP-запросы
* Работает за Nginx

# Gunicorn + Uvicorn (рекомендация для FastAPI)

Gunicorn как мастер, Uvicorn как worker:

```bash
gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 \
  --bind 0.0.0.0:8000
```

- Устойчивость к падениям
- Несколько воркеров
- ASGI-возможности

---

## Слайд 13

# 4. Nginx

### Роль Nginx

1. **Reverse proxy** — направляет запросы к приложению
2. **Статика** — отдаёт CSS, JS, изображения
3. **SSL/TLS** — терминация HTTPS
4. **Балансировка** — несколько инстансов приложения

---

## Слайд 14

## Типичная схема

Client → Nginx → Gunicorn/Uvicorn → App


# Пример конфига Nginx (проксирование)

```nginx
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /var/www/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Слайд 15

# Почему Nginx, а не прямой доступ к приложению?

- Приложение слушает localhost (безопасность)
- Nginx обрабатывает статику быстрее
- Один порт 80/443 для нескольких сервисов
- Кеширование, сжатие, rate limiting

---
## Что НЕ делает Nginx

* Не запускает Python
* Не знает Django/FastAPI
* Только проксирует


## Слайд 16

# 5. Деплой FastAPI

### Минимальный стек

- FastAPI приложение
- Uvicorn (или Gunicorn + UvicornWorker)
- Nginx
- База данных (PostgreSQL)
- Переменные окружения (.env)

---

## Слайд 17

# FastAPI: структура проекта

```
/app
  main.py          # FastAPI app
  requirements.txt
  .env
Dockerfile
docker-compose.yml (опционально)
```

---

## Слайд 18

# FastAPI: запуск в production

```bash
# Через Uvicorn напрямую
uvicorn main:app --host 0.0.0.0 --port 8000

# Через Gunicorn + Uvicorn (рекомендуется)
gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  -w 4 --bind 0.0.0.0:8000
```

## FastAPI в production

* Gunicorn + Uvicorn workers
* Docker / Kubernetes
* Отлично подходит для API

---

## Слайд 19

# 6. Деплой Django

## Особенности Django

* Монолит
* ORM + миграции
* Админка
* Статика

### Отличия от FastAPI

- **collectstatic** — сборка статики
- **migrate** — миграции БД
- **WSGI** — Gunicorn без Uvicorn
- **ALLOWED_HOSTS**, **SECRET_KEY** в настройках

---

## Слайд 20

## Минимальный стек Django

* Django
* Gunicorn
* Nginx

# Django: типовой порядок деплоя

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn project.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4
```

---

## Слайд 21

# Django: критичные настройки production

```python
DEBUG = False
ALLOWED_HOSTS = ['example.com', 'www.example.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASES = { ... }  # из переменных окружения
STATIC_ROOT = '/var/www/static/'
```

---

## Слайд 22

# 7. PaaS — Platform as a Service

### Что это?

Платформа, где **инфраструктура скрыта** от разработчика.

- Railway, Render, Fly.io, Heroku
- `git push` → build → run
- Минимум настройки

---

## Слайд 23

# PaaS: плюсы и минусы

**Плюсы:**
- Быстрый старт
- Встроенный CI/CD
- Нет DevOps-экспертизы

**Минусы:**
- Меньше контроля
- Ограничения и лимиты
- Цена растёт с нагрузкой

**Когда:** MVP, обучение, демо

---

## Слайд 24

# 8. cPanel-хостинг

### Что это?

Классический shared-хостинг с GUI.

- Ограниченный доступ
- Часто Passenger для Python
- Python — не основной сценарий

---

## Слайд 25

# cPanel: когда использовать

**Плюсы:** дёшево, GUI, без DevOps  
**Минусы:** плохо масштабируется, устаревший подход

**Подходит для:**
- Простых Django-сайтов
- Legacy-проектов
- Низкого трафика

---

## Слайд 26

# 9. VPS — Virtual Private Server

* Полный контроль
* SSH-доступ

### Что это?

Полный контроль над Linux-сервером.

- DigitalOcean, Hetzner, EC2
- Свой Nginx, Gunicorn, PostgreSQL, Redis
- systemd для автозапуска

---

## Слайд 27

# VPS: типовая архитектура

```
Nginx (порт 80/443)
   ↓
Gunicorn / Uvicorn (порт 8000)
   ↓
Django / FastAPI
   ↓
PostgreSQL, Redis
```

systemd-юниты для автозапуска при перезагрузке.

---

## Слайд 28

# VPS: плюсы и минусы

**Плюсы:**
- Гибкость
- Дешевле PaaS при росте
- Продакшен-подход

**Минусы:**
- Ручная настройка
- Ответственность за безопасность и обновления

---

## Слайд 29

# 10. VPS + Docker

### Зачем Docker?

- **Одинаковое окружение** — dev = prod
- **Быстрый деплой** — образ готов
- **Изоляция** — сервисы в контейнерах

---

## Слайд 30

# Docker: архитектура типового стека

```
Docker Compose
 ├─ web (Django / FastAPI)
 ├─ db (PostgreSQL)
 ├─ redis
 └─ nginx
```

volumes для данных, ports для доступа.

---

## Слайд 31

# Docker: ключевые файлы

- **Dockerfile** — сборка образа приложения
- **docker-compose.yml** — оркестрация сервисов
- **.env** — переменные окружения
- **volumes** — персистентность БД

---

## Слайд 32

# Docker: плюсы и минусы

**Плюсы:**
- Стандарт индустрии
- Удобно масштабировать
- Идеально для CI/CD

**Минусы:**
- Дополнительный порог входа

> Docker — не магия, а упаковка процессов.

---

## Слайд 33

# 11. CI/CD

### Что такое CI/CD?

- **CI** (Continuous Integration) — автоматические тесты при каждом коммите
- **CD** (Continuous Deployment) — автоматический деплой после успешных проверок

---

## Слайд 34

# CI/CD: типовой pipeline

```
git push
  → tests (pytest, lint)
  → build (Docker image)
  → push to registry
  → deploy (VPS, K8s, ...)
```

---

## Слайд 35

# CI/CD: инструменты

- **GitHub Actions**
- **GitLab CI**
- **Jenkins**
- **Bitbucket Pipelines**

---

## Слайд 36

# CI/CD: пример сценария

1. Push в `main`
2. Запуск тестов
3. Сборка Docker-образа
4. Публикация в registry
5. Деплой на VPS / Kubernetes
6. Health-check

---

## Слайд 37

# 12. Django и Docker Compose

### Структура

```
├── Dockerfile
├── docker-compose.yml
├── django_project/
│   ├── manage.py
│   └── ...
├── nginx/
│   └── default.conf
└── .env
```

---

## Слайд 38

# Django + Docker Compose: docker-compose.yml (фрагмент)

```yaml
services:
  web:
    build: .
    command: gunicorn project.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/static
    depends_on:
      - db

  db:
    image: postgres:17
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb
```

---

## Слайд 39

# Django + Docker: типовые команды

```bash
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

---

## Слайд 40

# 13. FastAPI и Kubernetes

### Зачем Kubernetes?

- Оркестрация множества контейнеров
- Автомасштабирование
- Self-healing
- Rolling updates без даунтайма

---
### FastAPI + Kubernetes

* Stateless API
* Horizontal scaling
* Cloud-native подход

## Слайд 41

# Kubernetes: основные объекты

- **Pod** — один или несколько контейнеров
- **Deployment** — управление репликами
- **Service** — доступ к подам
- **Ingress** — маршрутизация HTTP-трафика

---

## Слайд 42

# FastAPI в Kubernetes: Deployment (фрагмент)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    spec:
      containers:
      - name: fastapi
        image: myregistry/fastapi-app:latest
        ports:
        - containerPort: 8000
```

## Когда нужен Kubernetes

* High-load
* Микросервисы
* Большие команды

## Когда НЕ нужен

* MVP
* Маленькие проекты
* Один сервер

---

## Слайд 43

# Сравнительная таблица подходов

| Подход              | Контроль  | Сложность | Продакшен |
| ------------------- | --------- | --------- | --------- |
| PaaS                | низкий    | ⭐         | ⚠         |
| cPanel              | низкий    | ⭐⭐        | ❌         |
| VPS                 | высокий   | ⭐⭐⭐       | ✅         |
| VPS + Docker        | высокий   | ⭐⭐⭐⭐      | ✅         |
| VPS + Docker + CI/CD| высокий   | ⭐⭐⭐⭐⭐     | 🚀         |
| Kubernetes          | максимальный | ⭐⭐⭐⭐⭐ | 🚀         |

---

## Слайд 44

# Итоги: что выбрать?

- **MVP / учёба** → PaaS (Railway, Render)
- **Небольшой проект** → VPS + Docker Compose
- **Средний/крупный** → VPS + Docker + CI/CD
- **Масштаб, микросервисы** → Kubernetes

---

## Слайд 45

# Ключевые тезисы

1. **Нет "лучшего" деплоя** — есть подходящий под задачу
2. Начинай с простого → иди к автоматизации
3. Docker + CI/CD = современный стандарт
4. DevOps — часть профессии backend-разработчика

---

## Слайд 46

## Краткое сравнение

* Django → сайты, админки, монолиты
* FastAPI → API, микросервисы
* VPS + Docker → золотой стандарт
* Kubernetes → enterprise

## Что изучать дальше

* Linux basics
* Networking
* Security
* Monitoring (Prometheus, Grafana)
---

## Слайд 47

# Дополнительные темы для изучения

- Мониторинг (Prometheus, Grafana)
- Логирование (Loki, ELK)
- Бэкапы БД
- SSL (Let's Encrypt)
- Secrets management

---

## Слайд 48

# Полезные ресурсы

- Документация: Django Deployment, FastAPI Deployment
- Gunicorn, Uvicorn, Nginx — официальные docs
- Docker & Kubernetes — документация и tutorials
- GitHub Actions / GitLab CI — примеры пайплайнов

---

## Слайд 49

# Чек-лист перед деплоем

- [ ] DEBUG = False
- [ ] SECRET_KEY из переменных окружения
- [ ] Миграции применены
- [ ] Статика собрана (Django)
- [ ] HTTPS настроен
- [ ] Логирование работает

---

## Слайд 50

# Спасибо за внимание!

### Вопросы?

**Темы:** Введение в деплой • Python • Uvicorn • Gunicorn • Nginx • FastAPI • Django • PaaS • cPanel • VPS • Docker • CI/CD • Kubernetes
