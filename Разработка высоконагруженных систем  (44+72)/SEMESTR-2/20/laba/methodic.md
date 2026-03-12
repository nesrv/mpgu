# Django Ninja + HTMX: от разработки до деплоя на VPS

Создание веб-приложения «Магазин видеокарт» с JSON API, HTMX-фронтом и автоматическим деплоем через GitHub Actions.

---

## Часть 1. Разработка приложения

---

### Архитектура приложения

Приложение разделено на три слоя:

| Слой | URL | Что возвращает | Файл |
|------|-----|----------------|------|
| Страница | `/` | Полный HTML | `views.py` → `home.html` |
| HTMX partial | `/partials/products/` | Фрагмент HTML | `views.py` → `products_list.html` |
| JSON API | `/api/products` | JSON | `api.py` (Django Ninja) |

#### Почему именно так?

- **JSON API** (`api.py`) — данные для внешних клиентов (мобильное приложение, Postman, другие сервисы). Возвращает чистый JSON.
- **HTMX partials** (`views.py`) — HTML-фрагменты для подгрузки в страницу без JavaScript. Возвращает готовый HTML.
- **Страницы** (`views.py`) — полные HTML-страницы с подключённым HTMX.

Главный принцип: **API не должен возвращать HTML, views не должны возвращать JSON.** Каждый слой отвечает за своё.

---

### Структура проекта

```
PROJECT/
├── config/
│   ├── settings.py          # Настройки Django
│   ├── urls.py              # Маршрутизация
│   ├── wsgi.py
│   └── asgi.py
├── shop/
│   ├── models.py            # Модели данных
│   ├── api.py               # JSON API (Django Ninja)
│   ├── views.py             # Страницы и HTMX partials
│   └── templates/shop/
│       ├── home.html         # Главная страница
│       ├── products_list.html # Список товаров (partial)
│       └── components/
│           └── product_card.html  # Компонент карточки
├── docker-compose.yml        # Для локальной разработки (порт 8000)
├── docker-compose.prod.yml   # Для VPS (порт 8080)
├── Dockerfile                # Сборка Django-приложения
├── .github/workflows/deploy.yml  # CI/CD pipeline
├── data.sql                 # Тестовые данные
├── load_data.py             # Скрипт загрузки данных
├── requirements.txt
└── manage.py
```

---

### Шаг 1. Создание проекта

```bash
mkdir PROJECT && cd PROJECT
python -m venv .venv
```

Активация виртуального окружения:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate

# Linux/Mac
source .venv/bin/activate
```

Установка зависимостей:

```bash
pip install django django-ninja gunicorn
```

Создание проекта Django:

```bash
django-admin startproject config .
python manage.py startapp shop
```

Добавить `'shop'` в `INSTALLED_APPS` в файле `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'shop'
]
```

---

### Шаг 2. Модели (`shop/models.py`)

```python
from django.db import models

class VideoCard(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "video_cards"

class Cart(models.Model):
    product = models.ForeignKey(VideoCard, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_name = models.TextField()
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
```

Применить миграции:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Шаг 3. JSON API — Django Ninja (`shop/api.py`)

Django Ninja — это фреймворк для создания API поверх Django. Аналог Django REST Framework, но быстрее и проще.

```python
from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from .models import VideoCard

api = NinjaAPI(urls_namespace="api")


class ProductOut(Schema):
    id: int
    name: str
    price: float
    description: str


@api.get("/products", response=list[ProductOut])
def list_products(request):
    return VideoCard.objects.all()


@api.get("/products/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    return get_object_or_404(VideoCard, id=product_id)


@api.get("/health")
def health(request):
    return {"status": "ok"}
```

#### Что здесь происходит:

- **`Schema`** — описывает формат JSON-ответа (как сериализатор в DRF). Django Ninja автоматически преобразует QuerySet в JSON по этой схеме.
- **`@api.get("/products", response=list[ProductOut])`** — декоратор создаёт GET-endpoint. Параметр `response` указывает схему ответа.
- **`get_object_or_404`** — если объект не найден, вернёт 404 вместо ошибки 500.
- **`/health`** — endpoint для проверки работоспособности приложения (используется при деплое).

#### Результат:

```
GET /api/products →
[
  {"id": 1, "name": "NVIDIA GeForce RTX 5090", "price": 230000.0, "description": "..."},
  ...
]

GET /api/products/1 →
{"id": 1, "name": "NVIDIA GeForce RTX 5090", "price": 230000.0, "description": "..."}

GET /api/health →
{"status": "ok"}
```

Django Ninja также автоматически генерирует документацию: `GET /api/docs`

---

### Шаг 4. Views — страницы и HTMX partials (`shop/views.py`)

```python
from django.shortcuts import render
from .models import VideoCard


def home(request):
    return render(request, "shop/home.html")


def products_partial(request):
    products = VideoCard.objects.all()
    return render(request, "shop/products_list.html", {"products": products})
```

- **`home`** — отдаёт полную HTML-страницу. Сама страница не содержит данных — они подгружаются через HTMX.
- **`products_partial`** — возвращает HTML-фрагмент (не полную страницу). HTMX вставляет этот фрагмент внутрь `<div>` на главной странице.

---

### Шаг 5. Шаблоны

#### Главная страница (`shop/templates/shop/home.html`)

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Продукты</title>
  <script src="https://unpkg.com/htmx.org@2.0.3"></script>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 600px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-weight: 400; }
    .product { border-bottom: 1px solid #eee; padding: 1rem 0; }
    .product:last-child { border: none; }
    .price { font-weight: 600; color: #333; }
    .loading { color: #888; }
  </style>
</head>
<body>
  <h1>Продукты</h1>
  <div hx-get="/partials/products/" hx-trigger="load" hx-swap="innerHTML" class="loading">
    Загрузка…
  </div>
</body>
</html>
```

#### Как работает HTMX (без JavaScript):

```html
<div hx-get="/partials/products/" hx-trigger="load" hx-swap="innerHTML">
```

- **`hx-get`** — при срабатывании триггера отправить GET-запрос на указанный URL
- **`hx-trigger="load"`** — триггер: выполнить запрос сразу при загрузке страницы
- **`hx-swap="innerHTML"`** — полученный HTML вставить внутрь этого `<div>`

Результат: страница загружается → HTMX запрашивает `/partials/products/` → сервер возвращает HTML-фрагмент → HTMX вставляет его в `<div>`. Никакого JavaScript не нужно.

#### Список товаров — partial (`shop/templates/shop/products_list.html`)

```html
{% for product in products %}
  {% include "shop/components/product_card.html" %}
{% empty %}
  <p>Нет товаров</p>
{% endfor %}
```

Это не полная страница, а фрагмент. `{% include %}` подключает компонент карточки для каждого товара.

#### Компонент карточки (`shop/templates/shop/components/product_card.html`)

```html
<article class="product">
  <div class="name">{{ product.name }}</div>
  <div class="price">{{ product.price|floatformat:0 }} ₽</div>
  {% if product.description %}<p>{{ product.description }}</p>{% endif %}
</article>
```

Вынесен в отдельный файл, чтобы можно было переиспользовать в других местах (например, в корзине или на странице заказа).

---

### Шаг 6. Маршрутизация (`config/urls.py`)

```python
from django.urls import path
from shop.api import api
from shop.views import home, products_partial

urlpatterns = [
    path("", home),
    path("partials/products/", products_partial),
    path("api/", api.urls),
]
```

Итоговая карта маршрутов:

| URL | View | Тип ответа |
|-----|------|-----------|
| `/` | `home` | Полный HTML |
| `/partials/products/` | `products_partial` | HTML-фрагмент |
| `/api/products` | `list_products` | JSON |
| `/api/products/{id}` | `get_product` | JSON |
| `/api/health` | `health` | JSON |
| `/api/docs` | (авто) | Swagger UI |

---

### Шаг 7. Тестовые данные

Файл `data.sql`:

```sql
INSERT INTO video_cards (name, price, description, created_at) VALUES
  ('NVIDIA GeForce RTX 5090', 230000.00, 'Флагманская видеокарта 2026 года.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4090', 165000.00, 'Мощная видеокарта для рейтрейсинга.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 5080', 130000.00, 'Высокая производительность для 4K.', '2026-01-15 10:00:00'),
  ('AMD Radeon RX 9070 XT', 95000.00, 'Лучшее соотношение цена/производительность.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4080 Super', 115000.00, 'Мощная видеокарта для 4K с DLSS.', '2026-01-15 10:00:00');
```

Скрипт загрузки `load_data.py`:

```python
import sqlite3

conn = sqlite3.connect('db.sqlite3')
with open('data.sql', encoding='utf-8') as f:
    conn.executescript(f.read())
conn.close()
print('Данные загружены.')
```

Загрузить данные:

```bash
python manage.py migrate
python load_data.py
```

---

### Шаг 8. Запуск и проверка

```bash
python manage.py runserver
```

Проверить:

| URL | Ожидаемый результат |
|-----|-------------------|
| http://127.0.0.1:8000/ | Страница со списком видеокарт |
| http://127.0.0.1:8000/api/products | JSON-массив товаров |
| http://127.0.0.1:8000/api/products/1 | JSON одного товара |
| http://127.0.0.1:8000/api/health | `{"status": "ok"}` |
| http://127.0.0.1:8000/api/docs | Swagger-документация |

---

### Шаг 9. requirements.txt

```
Django>=5.0
django-ninja>=1.0
gunicorn>=21.0
```

---

### Принципы проектирования

#### 1. Разделение API и представления

```
api.py   → только JSON (данные)
views.py → только HTML (представление)
```

API не знает про HTML. Views не формирует JSON. Каждый файл отвечает за свой формат.

#### 2. HTMX вместо JavaScript

Классический подход: сервер отдаёт JSON → клиент на JS парсит и строит DOM.

HTMX-подход: сервер отдаёт готовый HTML → HTMX вставляет его в страницу. Не нужно писать JavaScript.

#### 3. Компоненты шаблонов

```
templates/shop/
├── home.html                    ← полная страница
├── products_list.html           ← partial (фрагмент для HTMX)
└── components/
    └── product_card.html        ← переиспользуемый компонент
```

- **Страницы** — полный HTML с `<!DOCTYPE>`, `<head>`, `<body>`
- **Partials** — фрагменты для подгрузки через HTMX (без `<html>`, `<head>`)
- **Components** — мелкие блоки, подключаемые через `{% include %}`

---

## Часть 2. Деплой на VPS через CI/CD

---

### Схема работы

```
git push → GitHub Actions → SSH на VPS (deploy user) → git pull → docker compose up
```

Пушишь в `master` — через ~30 сек новая версия уже на сервере.

---

### Шаг 10. Dockerfile

Dockerfile описывает, как собрать Docker-образ приложения:

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

#### Разбор по строкам:

| Инструкция | Что делает |
|------------|-----------|
| `FROM python:3.14-slim` | Базовый образ — минимальный Python без лишних пакетов |
| `WORKDIR /app` | Рабочая директория внутри контейнера |
| `RUN apt-get ... libpq-dev` | Устанавливает библиотеку для работы с PostgreSQL (`psycopg2`) |
| `COPY requirements.txt .` | Копирует зависимости отдельно (для кэширования слоёв Docker) |
| `RUN pip install ...` | Устанавливает Python-зависимости. `--no-cache-dir` — не хранить кэш pip |
| `COPY . .` | Копирует весь проект в контейнер |
| `RUN collectstatic` | Собирает статику Django. `2>/dev/null || true` — не падать, если статики нет |
| `EXPOSE 8000` | Документирует порт (информационно, не открывает его) |
| `CMD [...]` | Команда запуска по умолчанию — gunicorn с 3 воркерами |

**Почему `requirements.txt` копируется отдельно?** Docker кэширует слои. Если код изменился, но `requirements.txt` — нет, зависимости не будут переустанавливаться. Это ускоряет сборку.

---

### Шаг 11. docker-compose.prod.yml

Файл описывает два сервиса — базу данных и веб-приложение — и связывает их в одну сеть:

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
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-*}
    command: >
      sh -c "python manage.py migrate &&
             python load_data.py &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 8 --threads 4"

volumes:
  pg_data:
```

#### Разбор:

| Параметр | Что делает |
|----------|-----------|
| `image: postgres:17` | Использует готовый образ PostgreSQL 17 |
| `restart: unless-stopped` | Автоматический перезапуск при падении или перезагрузке сервера |
| `${DB_PASSWORD:-postgres}` | Переменная окружения с дефолтным значением `postgres` |
| `max_connections=300` | Увеличенный лимит соединений к БД (по умолчанию 100) |
| `pg_data:/var/lib/postgresql/data` | Именованный volume — данные БД сохраняются между перезапусками |
| `build: .` | Собирает образ из Dockerfile в текущей директории |
| `ports: "8080:8000"` | Проброс порта: хост `8080` → контейнер `8000` |
| `depends_on: db` | Сервис `web` запускается после `db` |
| `DATABASE_URL` | Строка подключения к PostgreSQL. `db` — имя сервиса (Docker DNS) |
| `command: sh -c "..."` | Переопределяет CMD из Dockerfile: миграции → данные → gunicorn |

**Отличие от локальной разработки:**
- Локально — `python manage.py runserver` + SQLite
- На VPS — gunicorn (8 воркеров, 4 потока) + PostgreSQL в Docker

---

### Шаг 12. Настройка VPS (один раз, под root)

#### Подключиться к VPS:
```bash
ssh root@81.90.182.174
```

#### Установить Docker:
```bash
curl -fsSL https://get.docker.com | sh
```

#### Создать пользователя (если ещё нет) и дать доступ к Docker:
```bash
id alekseeva || adduser --disabled-password --gecos "" alekseeva
echo "alekseeva:alekseeva" | chpasswd
usermod -aG docker alekseeva
```

#### Создать директорию проекта и отдать deploy:
```bash
mkdir -p /opt/shop
chown alekseeva:alekseeva/opt/shop
```

#### Переключиться на deploy и склонировать:
```bash
su - alekseeva
cd /opt/shop
git clone https://github.com/alekseeva/cd-cd-django-ninja.git .
```

#### Запустить:
```bash
docker compose -f docker-compose.prod.yml up --build -d
```

#### Проверить:
```bash
curl http://localhost:8080/api/health
# {"status": "ok"}
```

Сайт доступен по адресу: `http://81.90.182.174:8080`

---

### Шаг 13. Настройка GitHub Secrets

В репозитории на GitHub: **Settings → Secrets and variables → Actions → New repository secret**

Добавить три секрета:

| Имя              | Значение          |
|------------------|-------------------|
| `VPS_HOST`       | `81.90.182.174`   |
| `VPS_USER`       | `alekseeva`       |
| `VPS_PASSWORD`   | `alekseeva`       |

---

### Шаг 14. Как работает деплой

После настройки — всё автоматически:

1. Делаешь `git push origin master`
2. GitHub Actions подключается к VPS по SSH
3. Выполняет `git pull` + `docker compose up --build -d`
4. Новая версия запущена

#### Файл workflow: `.github/workflows/deploy.yml`

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

#### Разбор:

| Параметр | Что делает |
|----------|-----------|
| `on: push: branches: [master]` | Запускается только при push в ветку `master` |
| `runs-on: ubuntu-latest` | Выполняется на виртуальной машине GitHub |
| `appleboy/ssh-action@v1` | Готовое действие для подключения по SSH |
| `secrets.VPS_HOST` | Берёт значения из GitHub Secrets (настроены в шаге 13) |
| `git pull origin master` | Обновляет код на VPS |
| `docker compose up --build -d` | Пересобирает и перезапускает контейнеры в фоне |

Workflow не собирает образ на стороне GitHub — он подключается по SSH к VPS и запускает сборку там. Это простой подход для учебных проектов.

---

### Полезные команды на VPS

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

## Часть 3. Бенчмарки и оптимизация

---

### Нагрузочное тестирование

```bash
ab -n 10000 -c 100 http://81.90.182.174:8080/api/products
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/products
wrk -t4 -c200 -d30s http://81.90.182.174:8080/api/health
```

#### Результат wrk (gunicorn, 3 воркера, PostgreSQL):

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

#### Результат ab (gunicorn, 3 воркера, PostgreSQL):

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

### Оптимизация

#### 1. Увеличить воркеры и переключить на uvicorn (асинхронный режим)

В `docker-compose.prod.yml` заменить command:
```yaml
command: >
  sh -c "python manage.py migrate &&
         python load_data.py &&
         uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4"
```

Django Ninja нативно поддерживает async — uvicorn обрабатывает множество соединений в одном процессе без блокировки.

#### 2. Первый результат uvicorn (с ошибкой conn_max_age=600):

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

#### 3. Исправление: conn_max_age=0 + max_connections

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

#### 4. Вывод: uvicorn хуже для синхронных views

```
wrk -t4 -c200 -d30s (uvicorn, 4 воркера, conn_max_age=0)

Requests/sec:     34.00
Timeouts:         864
```

Uvicorn оборачивает sync ORM-вызовы в `sync_to_async` — лишний overhead.
Для синхронных views **gunicorn быстрее**.

#### 5. Финальная оптимизация: gunicorn 8 воркеров + 4 потока + conn_max_age=600

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

#### 6. Результат после оптимизации

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

#### Стабильный тест (ab, 50 соединений):

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

---

### Итоговое сравнение

| Конфигурация                          | Req/sec | Avg Latency | Timeouts | Errors |
|---------------------------------------|---------|-------------|----------|--------|
| Gunicorn 3 воркера                    | 50      | 1.06s       | 1531     | 0      |
| Uvicorn 4 воркера (conn_max_age=600)  | 55      | 1.53s       | 1418     | 1415   |
| Uvicorn 4 воркера (conn_max_age=0)    | 34      | 1.54s       | 864      | 0      |
| **Gunicorn 8w + 4t (conn_max_age=600)** | **269** | **592ms** | **361** | **0** |
| **Gunicorn 8w + 4t (ab, c=50)**       | **233** | **215ms**  | **0**   | **0** |

---

### Сколько пользователей выдержит

**233 req/s** — стабильная пропускная способность без ошибок.

Средний пользователь делает **2-5 запросов** при загрузке страницы,
затем **1 запрос каждые 5-30 секунд** при просмотре.

| Сценарий                    | Одновременных пользователей |
|-----------------------------|-----------------------------|
| Активный просмотр (5 rps)   | ~45                         |
| Обычный просмотр (1 rps)    | ~230                        |
| Чтение с паузами (0.2 rps)  | ~1000                       |
| **В минуту (пиковый трафик)** | **~3000–5000 уникальных**  |
