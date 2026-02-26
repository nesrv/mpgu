Лекция 

Настройка производительности FastAPI и Django. Деплой и тестирование на PaaS.



Слайд 1 Архитектурные метрики



- **RPS / QPS** — запросы в секунду
- **Peak RPS** — пиковая нагрузка
- **Read/Write ratio** — соотношение чтения и записи
- **Payload size (avg / p95)** — размер полезной нагрузки (средний / 95‑й перцентиль)



Слайд 2 Масштабируемость

- **Horizontal scalability** (можно ли масштабироваться без боли)
- **Statefulness** (stateless vs stateful) — состояние (без состояния vs с хранением состояния)
- **Fan-out** — сколько RPC вызывает один запрос



Слайд 3 **Сравнение производительности популярных Python-фреймворков API** (VPS ~2 ядра / 4 ГБ RAM)

---


| Фреймворк                   | Архитектура      | Sync / Async                             | Примерная пропускная способность        | Комментарии                                                                                                                                                                                                          |
| --------------------------- | ---------------- | ---------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI**                 | ASGI (Starlette) | Async по умолчанию                       | ~20 000–40 000+ RPS в простых API       | Высокая пропускная способность, низкая задержка для IO-bound задач; эффективен при высоких нагрузках. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com)) |
| **Django (без API-слоя)**   | ASGI / WSGI      | Синхронный (частичная async-поддержка)   | ~1 000–5 000 RPS                        | Встроенный ORM и middleware дают бОльший overhead. ([manikandaraj.com](https://manikandaraj.com/2025/09/python-rest-api-frameworks-comparison-2025/?utm_source=chatgpt.com))                                         |
| **Django + DRF**            | WSGI (обычно)    | Синхронный                               | ~2 000–12 000 RPS (зависит от нагрузки) | Усложняет сериализацию и routing, средний throughput ниже FastAPI. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com))                                    |
| **Django + Ninja**          | ASGI / WSGI      | Частично async                           | ~почти FastAPI-уровни                   | Более легковесная обёртка над Django ORM с FastAPI-подобным API. ([django-ninja-aio.com](https://django-ninja-aio.com/latest/comparison/?utm_source=chatgpt.com))                                                    |
| **Django 6 (новая версия)** | ASGI / WSGI      | Синхронный с улучшенной async-поддержкой | Похож на классический Django            | Новые async возможности есть, но реальный выигрыш в API-скорости ограничен (по сравнению с FastAPI).                                                                                                                 |


👉 **RPS = Requests per second** (число запросов в секунду), ориентировочные данные для API-эндпоинтов с JSON-ответами без тяжёлых DB-операций.

---

## Слайд 4 Детали по ⭐ **FastAPI**

- Очень высокие показатели throughput и низкая задержка — часто **в 3–5× быстрее, чем Django/DRF** по простым API-эндпоинтам. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com))
- Асинхронность встроена по умолчанию → эффективное использование событийного цикла и низкая нагрузка на память. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com))
- Отлично подходит для **микросервисов, real-time API, WebSockets, высоких нагрузок**.

📊 На VPS 2 ядра, 4 ГБ FastAPI обычно устойчиво обрабатывает десятки тысяч запросов в секунду при простых API (без тяжёлых запросов к БД), хотя реальные цифры зависят от типа нагрузки и deployment (Uvicorn/Gunicorn workers).

---

## Слайд 5 Детали по 🐍 **Django + DRF**

- Built-in Django ORM, но **DRF значительно увеличивает overhead** из-за сериализации, middleware и sync-обработки. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com))
- Производительность ощутимо ниже FastAPI, особенно при больших потоках запросов: типично **в 2–5× медленнее** для API-эндпоинтов без оптимизаций. ([manikandaraj.com](https://manikandaraj.com/2025/09/python-rest-api-frameworks-comparison-2025/?utm_source=chatgpt.com))
- DRF чаще всего синхронен — асинхронные преимущества Django 6 на него почти не распространяются.

💡 Подходит для проектов, где важны **экосистема Django**, встроенные инструменты (auth, admin) и богатые интерфейсы API.

---

## Слайд 6 Детали по ⚡ **Django + Ninja**

- По данным независимых бенчмарков, **Django Ninja быстрее DRF** и близок к производительности FastAPI на уровне CRUD-операций. ([django-ninja-aio.com](https://django-ninja-aio.com/latest/comparison/?utm_source=chatgpt.com))
- Благодаря использованию Pydantic-сериализации и лёгкой структуре DSL-маршрутов, из-за меньшего overhead быстрее обрабатывает запросы.

📌 На практике это делает Ninja хорошим компромиссом: сохраняешь ORM и многое из Django, но с высокой скоростью API.

---

## Слайд 7 Детали по 🏁 **Django (чистый, без DRF/Ninja)**

- При обычных веб-эндпоинтах и шаблонах — вполне достаточен для страниц, admin-панелей, формирования HTML-ответов.
- В API-контексте синхронный характер обработки и нагрузка middleware дают более низкие RPS по сравнению с FastAPI. ([manikandaraj.com](https://manikandaraj.com/2025/09/python-rest-api-frameworks-comparison-2025/?utm_source=chatgpt.com))

---

## Слайд 8 📊 Примерные ориентиры (грубо)

> Эти цифры — обобщение разных независимых бенчмарков и тестов при простых GET/POST JSON API без тяжёлой логики или сложных ORM-запросов:


| Фреймворк                                                                                                                     | RPS (порядочный диапазон) | Среднее время ответа |
| ----------------------------------------------------------------------------------------------------------------------------- | ------------------------- | -------------------- |
| FastAPI                                                                                                                       | **~20 000–40 000+**       | ~10–30 ms            |
| Django + Ninja                                                                                                                | ~15 000–30 000            | ~15–40 ms            |
| Django + DRF                                                                                                                  | ~7 000–15 000             | ~50–120 ms           |
| Django (без API-слоя)                                                                                                         | ~2 000–10 000             | ~80–150 ms           |
| *(Ориентация на нагрузочные тесты в 2025–2026; реальные цифры могут отличаться в зависимости от кода, БД, кэша и deployment)* |                           |                      |


---

## Слайд 9 🧠 Практические соображения

### 📌 Если тебе важна **максимальная пропускная способность**

👉 **FastAPI** (или Django + Ninja) — лучшие варианты благодаря async-первому подходу и минимальному overhead.

### 📌 Если важны **функциональность и экосистема**

👉 **Django + DRF / Django 6** — отличное сочетание зрелой архитектуры, ORM, админки и множества готовых решений.

### 📌 Если нужен **баланс скорости и удобства разработки**

👉 **Django + Ninja** — близкий к FastAPI перформанс с сохранением Django-стека.

---

## Слайд 10 📌 Почему Django 6 тоже упоминается отдельно

Django 6 расширяет поддержку async, но **большинство API-слоёв (особенно DRF) по-прежнему работают синхронно**, поэтому чистый прирост скорости на Django 6 vs Django 5/4 невелик в API-нагрузке по сравнению с фреймворками, изначально построенными на ASGI. ([FastLaunchAPI](https://fastlaunchapi.dev/blog/fastapi-vs-django-rest-framework-2026?utm_source=chatgpt.com))

---

### Слайд 11 🎯 Цель по железу (2 ядра / 4 GB)

Реалистичные ориентиры для **Django API**:

- **Django + Ninja**: 15–30k RPS (без тяжёлой БД)
- **Django + DRF**: 7–15k RPS
- **Средний p95 latency**: 30–120 ms
- **CPU ≈ 70–85% под нагрузкой**, RAM ≈ 1.5–2.5 GB

---

## Слайд 12 🧱 Архитектура (обязательный минимум)

```
Client
  ↓
Nginx
  ↓
Gunicorn (workers)
  ↓
Django (ASGI)
  ↓
PostgreSQL / Redis
```

---

## Слайд 13 ОС и базовая оптимизация VPS для Django

### Ubuntu 22.04 / 24.04

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  python3-pip python3-venv \
  nginx redis-server \
  postgresql postgresql-contrib \
  build-essential
```

### 🔧 sysctl (очень важно)

```bash
sudo nano /etc/sysctl.conf
```

Добавь:

```ini
net.core.somaxconn = 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65000
fs.file-max = 100000
```

Применить:

```bash
sudo sysctl -p
```

---

## Слайд 14 Django: ключевые настройки

### ⚙️ `settings.py`

```python
DEBUG = False

ALLOWED_HOSTS = ["your-domain.com"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

USE_TZ = False  # быстрее для API

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "app",
        "USER": "app",
        "PASSWORD": "strongpassword",
        "HOST": "127.0.0.1",
        "PORT": "5432",
        "CONN_MAX_AGE": 60,  # ВАЖНО
    }
}
```

### 🔥 Middleware — убери всё лишнее

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]
```

❌ Убрать, если не нужно:

- Sessions
- CSRF (для чистого API)
- Messages
- Locale

---

## Слайд 15 ASGI + Gunicorn (критично)

### Почему не WSGI?

- **WSGI** — блокирующая модель → хуже масштабируется
- **ASGI** — событийная модель → лучше загрузка CPU

---

## 📦 Установка

```bash
pip install gunicorn uvicorn
```

---

## ⚙️ Gunicorn config (`gunicorn.conf.py`)

```python
bind = "127.0.0.1:8000"

workers = 4              # 2 CPU × 2
worker_class = "uvicorn.workers.UvicornWorker"

threads = 1
timeout = 30
keepalive = 5

max_requests = 10000
max_requests_jitter = 1000

accesslog = "-"
errorlog = "-"
loglevel = "warning"
```

📌 **Почему 4 воркера?** Для IO-bound (API, БД): `workers = CPU × 2` — типичный ориентир.

---

## Слайд 16  Запуск

```bash
gunicorn config.asgi:application \
  --config gunicorn.conf.py
```

---

## Слайд 17 Nginx (огромный буст)

### `/etc/nginx/nginx.conf`

```nginx
worker_processes auto;
worker_connections 8192;
multi_accept on;
```

---

### Site config

```nginx
upstream django {
    server 127.0.0.1:8000;
    keepalive 64;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://django;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_read_timeout 30;
    }
}
```

📈 **Nginx + keepalive** даёт +20–30% RPS.

---

## Слайд 18 PostgreSQL (узкое место №1)

### `/etc/postgresql/*/main/postgresql.conf`

```ini
shared_buffers = 1GB
effective_cache_size = 3GB
work_mem = 16MB
maintenance_work_mem = 256MB
max_connections = 100
```

### Индексы — обязательно

```sql
CREATE INDEX CONCURRENTLY idx_user_email ON users(email);
```

❗ 80% «медленного Django» — это плохие SQL-запросы.

---

## Слайд 19 Redis (обязательно для скорости)

Используй для:

- кэша
- rate-limit
- session storage

```python
CACHES = {
  "default": {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": "redis://127.0.0.1:6379/1",
    "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
  }
}
```

---

## Слайд 20 Django Ninja / DRF — разница

## Django + Ninja (рекомендуется)

```python
@api.get("/users")
def users(request):
    return list(User.objects.values("id", "email"))
```

✔ Pydantic
✔ Минимальный overhead
✔ Async-friendly

---

## DRF — если нужен

- `SerializerMethodField` → ❌
- `.select_related()` / `.prefetch_related()` → ✅
- Pagination — отключить, если не нужна

---

## Слайд 21 Нагрузочное тестирование

```bash
wrk -t4 -c200 -d30s http://your-domain.com/api/users
```

Ожидаемо на 2 vCPU / 4 GB RAM:

| Стек           | RPS    |
| -------------- | ------ |
| Django + Ninja | 20–30k |
| Django + DRF   | 8–15k  |
| Django (views) | 5–10k  |


---

## Слайд 22 Частые ошибки (убивают производительность)

❌ DEBUG=True
❌ WSGI вместо ASGI
❌ 1 worker
❌ ORM в цикле
❌ Отсутствие индексов
❌ Нет Redis
❌ Gunicorn без `max_requests`

---

## Слайд 23 Краткий рецепт «максимум из Django»

> **Если коротко:**

- ASGI + Gunicorn + UvicornWorker
- 4 workers
- Nginx keepalive
- PostgreSQL с индексами
- Redis
- Django Ninja вместо DRF
- Минимум middleware

---

## Слайд 24 Что именно ты запускаешь

```bash
gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --threads ?
```

Это означает:

- ✅ **WSGI** (строго синхронная модель)
- ✅ **3 процесса (workers)**
- ❓ **threads** — если не указано, Gunicorn ставит `threads = 1`

👉 **Фактически:** `3 workers × 1 thread = 3 одновременных запроса`

---

## Слайд 25 Ожидаемая производительность (2 CPU / 4 GB)

### 1️⃣ Если `--threads` не указан (по умолчанию = 1)

**Итого:** 3 одновременных запроса

### 📊 Реалистичные цифры


| Тип эндпоинта         | RPS              | p95 latency |
| --------------------- | ---------------- | ----------- |
| Простой JSON (без БД) | **2–4k RPS**     | 80–150 ms   |
| ORM SELECT            | **1–2k RPS**     | 150–300 ms  |
| DRF сериализация      | **500–1.2k RPS** | 250–500 ms  |


💥 CPU будет **недогружен**, потому что:

- WSGI блокируется на I/O
- 3 workers мало для 2 ядер
- нет async-конкурентности

---

## Слайд 26 Ожидаемая производительность (2 CPU / 4 GB)

### 2️⃣ Если `--threads 2`

```bash
--workers 3 --threads 2
```

**Итого:** 6 одновременных запросов


| Тип          | RPS              |
| ------------ | ---------------- |
| Простой API  | **4–7k RPS**     |
| Django + ORM | **2–3k RPS**     |
| Django + DRF | **1.5–2.5k RPS** |


⚠️ Но:

- GIL ограничивает реальную параллельность
- рост latency
- хуже предсказуемость под нагрузкой

---

## Слайд 27 Ожидаемая производительность (2 CPU / 4 GB)

### 3️⃣ Если `--threads 4` (частая ошибка)

```bash
--workers 3 --threads 4
```

**Итого:** 12 потоков

❌ Обычно **хуже**, чем `threads=2`:

- context switch
- GIL contention
- p95/p99 latency растёт
- CPU «пилит», но RPS почти не растёт

---

## Почему эта схема ограничена

### ❌ WSGI = блокирующая модель

- каждый запрос держит worker
- БД / Redis / HTTP → блок
- масштабирование только количеством процессов

### ❌ 3 workers для 2 CPU — мало

Золотое правило для WSGI:

```text
workers = CPU × 2 + 1
```

👉 Для тебя минимум **5 workers**

---

## Слайд 28 Ожидаемая производительность (2 CPU / 4 GB)

### Что ты реально получишь в проде

Если оставить **как есть**:

```bash
--workers 3 --threads 1
```

➡️ **2–4k RPS потолок**, дальше:

- рост latency
- 502 от Nginx
- очередь запросов

---

## Слайд 29 Как выжать максимум из WSGI (если нельзя ASGI)

```bash
gunicorn config.wsgi:application \
  --workers 5 \
  --threads 2 \
  --timeout 30 \
  --max-requests 10000 \
  --max-requests-jitter 1000
```

📈 Это даст примерно:


| Стек           | RPS      |
| -------------- | -------- |
| Django (views) | **6–9k** |
| Django + DRF   | **3–5k** |


Но это **предел WSGI**.

---

## Слайд 30 Сравнение WSGI и ASGI (для понимания масштаба)


| Конфигурация         | RPS        |
| -------------------- | ---------- |
| WSGI (3w,1t)         | 2–4k       |
| WSGI (5w,2t)         | 6–9k       |
| **ASGI (4 workers)** | **15–30k** |


---

## Короткий вывод

> 🔴 **gunicorn + wsgi + 3 workers**
> = нормально для админки и low-traffic
> = плохо для high-load API



## Слайд 31 Системный дизайн (System Design) при проектировании бэкенда веб-приложений

### 🎯 Ключевые вопросы на старте

- **Load estimation** — сколько RPS ожидаем? Read/Write ratio (соотношение чтения/записи)?
- **Latency SLA** — p95, p99, какие допустимы?
- **Data volume** — объём данных, рост, retention
- **Consistency** — нужна строгая консистентность или eventual OK?

### 🧩 Типичные блоки при проектировании API

| Компонент       | Роль в системе                | Что учесть                          |
| --------------- | ------------------------------ | ----------------------------------- |
| API Gateway     | Маршрутизация, rate limit      | Nginx, Kong, AWS ALB                |
| App server      | Бизнес-логика, сериализация    | FastAPI / Django Ninja / DRF        |
| Database        | Источник истины                | Индексы, репликация, шардинг        |
| Cache           | Снижение нагрузки на БД        | Redis, in-memory                    |
| Queue           | Асинхронные задачи, буфер      | Celery, RabbitMQ, Kafka             |

### 📐 Простой стек для MVP vs High-load

- **MVP**: Django + Ninja + PostgreSQL + Redis
- **High-load**: Nginx → Gunicorn/ASGI → Django Ninja → PG (read replicas) + Redis

---

## Слайд 32 Системный дизайн (System Design) при проектировании Django-Ninja

### 🐍 Где Django-Ninja вписывается в дизайн системы

- **Monolith API** — один сервис, много эндпоинтов, ORM, admin
- **API-first** — быстрый JSON API, Pydantic-схемы, низкий overhead
- **Hybrid** — Django views + Ninja API в одном проекте

### 📌 Когда выбирать Django-Ninja

| Сценарий                               | Выбор           |
| -------------------------------------- | --------------- |
| Нужен ORM + admin + быстрый API        | Django + Ninja  |
| Максимум RPS, минимум Django-зависимостей | FastAPI         |
| Сложные сериализаторы, Browsable API   | Django + DRF    |

### 🔧 Паттерны при проектировании

- **Stateless API** — сессии в Redis, не в памяти воркера
- **Read-heavy** — `select_related` / `prefetch_related`, кэш в Redis
- **Write-heavy** — Celery для фоновых задач, батчинг операций
- **Горизонтальное масштабирование** — несколько инстансов за Nginx/ALB

---

## Слайд 33 Проектирование и создание бэкенда на Django Ninja — обзор

### Что охватим

1. Установка и первый API
2. Структура проекта
3. Роутеры и эндпоинты
4. Схемы (Pydantic)
5. CRUD и ORM
6. Аутентификация
7. Валидация и обработка ошибок
8. Async vs Sync
9. Тестирование
10. Чеклист деплоя

---

## Слайд 34 Установка и первый API

```bash
pip install django-ninja
```

### `urls.py`

```python
from ninja import NinjaAPI

api = NinjaAPI()

@api.get("/hello")
def hello(request):
    return {"message": "Hello, Django Ninja!"}
```

### Подключение в проект

```python
# urls.py проекта
from django.urls import path
from .api import api

urlpatterns = [
    path("api/", api.urls),
]
```

👉 Запуск: `python manage.py runserver` → `GET /api/hello`

---

## Слайд 35 Структура проекта

### Рекомендуемая структура

```
myproject/
├── config/           # settings, urls
├── api/
│   ├── __init__.py   # главный NinjaAPI
│   ├── v1/
│   │   ├── users.py
│   │   ├── products.py
│   │   └── __init__.py
│   └── deps.py       # зависимости (auth, db)
├── apps/
│   ├── users/
│   └── catalog/
└── manage.py
```

### Модульные роутеры

```python
# api/__init__.py
from ninja import NinjaAPI
from .v1 import router as v1_router

api = NinjaAPI(version="1.0")
api.add_router("/v1", v1_router)
```

---

## Слайд 36 Роутеры и эндпоинты

### Версионирование

```python
from ninja import Router

router = Router(tags=["users"])

@router.get("/users")
def list_users(request):
    return User.objects.all()

@router.get("/users/{user_id}")
def get_user(request, user_id: int):
    return User.objects.get(id=user_id)

@router.post("/users")
def create_user(request, payload: UserCreateSchema):
    return User.objects.create(**payload.dict())
```

### HTTP-методы

- `@router.get`, `@router.post`, `@router.put`, `@router.patch`, `@router.delete`
- Path-параметры: `{user_id}`, `{slug}` в URL
- Query-параметры — через аргументы функции

---

## Слайд 37 Схемы (Pydantic)

### Определение схем

```python
from ninja import Schema
from pydantic import validator

class UserCreate(Schema):
    email: str
    name: str
    password: str

    @validator("email")
    def email_must_be_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v

class UserOut(Schema):
    id: int
    email: str
    name: str
```

### Зачем отдельные In/Out-схемы

- **In** — валидация входящих данных, без полей вроде `id`, `created_at`
- **Out** — контроль, что уходит клиенту (без пароля и т.п.)

---

## Слайд 38 CRUD и ORM

### Типичный CRUD-эндпоинт

```python
@router.get("/users", response=List[UserOut])
def list_users(request, limit: int = 20, offset: int = 0):
    return list(User.objects.all()[offset:offset+limit])

@router.get("/users/{user_id}", response=UserOut)
def get_user(request, user_id: int):
    user = get_object_or_404(User, id=user_id)
    return user

@router.post("/users", response=UserOut)
def create_user(request, payload: UserCreate):
    return User.objects.create(**payload.dict())
```

### Оптимизация запросов

```python
User.objects.select_related("profile").prefetch_related("orders")[:20]
```

---

## Слайд 39 Аутентификация

### API Key

```python
from ninja.security import APIKeyHeader

class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        if key == settings.API_KEY:
            return key
        return None

api = NinjaAPI(auth=ApiKey())
```

### JWT

```python
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if validate_jwt(token):
            return token
        return None
```

### Per-route auth

```python
@router.get("/me", auth=AuthBearer())
def me(request):
    return request.auth
```

---

## Слайд 40 Валидация и обработка ошибок

### Автоматическая валидация

Pydantic проверяет типы и constraints — при ошибке Ninja возвращает `422 Unprocessable Entity` с деталями.

### Кастомные исключения

```python
from ninja.responses import Response

@router.get("/users/{user_id}")
def get_user(request, user_id: int):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
```

### Глобальный обработчик

```python
def custom_exception_handler(request, exc):
    return api.create_response(request, {"error": str(exc)}, status=400)

api = NinjaAPI()
api.add_exception_handler(ValueError, custom_exception_handler)
```

---

## Слайд 41 Async vs Sync

### Async-эндпоинт

```python
@router.get("/users/async")
async def list_users_async(request):
    return [u async for u in User.objects.all()]
```

### Когда async даёт выигрыш

- IO-bound: запросы к БД, внешние API
- Django 4.1+ поддерживает `sync_to_async` для ORM

### Смешивание sync и async

```python
@router.get("/sync")
def sync_endpoint(request):
    return {"type": "sync"}

@router.get("/async")
async def async_endpoint(request):
    return {"type": "async"}
```

⚠️ ASGI-сервер (Uvicorn) нужен для async.

---

## Слайд 42 Тестирование Django Ninja

```python
from ninja.testing import TestClient

from api import api

client = TestClient(api)

def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json()["message"] == "Hello, Django Ninja!"

def test_create_user():
    response = client.post("/v1/users", json={
        "email": "test@example.com",
        "name": "Test",
        "password": "secret"
    })
    assert response.status_code == 201
```

### Паттерны

- `TestClient` — без HTTP, быстрее
- `django.test.Client` — полный запрос, middleware

---

## Слайд 43 Чеклист деплоя Django Ninja

- [ ] `DEBUG = False`, `ALLOWED_HOSTS` настроены
- [ ] ASGI: Gunicorn + UvicornWorker
- [ ] Nginx перед приложением
- [ ] PostgreSQL + индексы
- [ ] Redis для кэша/сессий (если нужны)
- [ ] Минимум middleware
- [ ] `select_related` / `prefetch_related` для тяжёлых эндпоинтов
- [ ] Rate limiting (Nginx или django-ratelimit)
- [ ] Логирование и мониторинг

