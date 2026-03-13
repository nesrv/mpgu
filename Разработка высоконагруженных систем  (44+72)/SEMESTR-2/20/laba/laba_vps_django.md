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
| `RUN apt-get ... libpq-dev` | Устанавливает системную библиотеку для работы с PostgreSQL (см. разбор ниже) |
| `COPY requirements.txt .` | Копирует зависимости отдельно (для кэширования слоёв Docker) |
| `RUN pip install ...` | Устанавливает Python-зависимости. `--no-cache-dir` — не хранить кэш pip |
| `COPY . .` | Копирует весь проект в контейнер |
| `RUN collectstatic` | Собирает статику Django (см. разбор ниже) |
| `EXPOSE 8000` | Документирует порт (информационно, не открывает его) |
| `CMD [...]` | Команда запуска по умолчанию — gunicorn с 3 воркерами |

#### Подробный разбор `RUN apt-get`:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*
```

| Часть команды | Что делает |
|---------------|-----------|
| `apt-get update` | Обновляет список пакетов из репозиториев. Без этого `install` не знает, откуда качать |
| `apt-get install -y` | Устанавливает пакеты. `-y` — автоматически отвечает «да» на все вопросы |
| `--no-install-recommends` | Не ставить рекомендуемые (необязательные) пакеты — уменьшает размер образа |
| `libpq-dev` | C-библиотека для подключения к PostgreSQL. Нужна для компиляции `psycopg2` при `pip install` |
| `rm -rf /var/lib/apt/lists/*` | Удаляет скачанные списки пакетов (~30 МБ) — они больше не нужны |
| `&&` (всё в одном `RUN`) | Объединяет команды в один слой Docker. Если разбить на 3 `RUN`, каждый создаст отдельный слой, и удалённые файлы всё равно останутся в предыдущих слоях |

#### Подробный разбор `RUN collectstatic`:

```dockerfile
RUN python manage.py collectstatic --noinput 2>/dev/null || true
```

| Часть команды | Что делает |
|---------------|-----------|
| `python manage.py collectstatic` | Собирает все статические файлы (CSS, JS, картинки) из приложений Django в одну папку `STATIC_ROOT`. В продакшене gunicorn не раздаёт статику сам — это делает nginx или CDN |
| `--noinput` | Не спрашивать подтверждение «перезаписать файлы?». В Docker некому отвечать на вопросы |
| `2>/dev/null` | Перенаправляет stderr (поток ошибок) в «никуда». Если команда выведет предупреждения — они не засорят лог сборки |
| `\|\| true` | Если `collectstatic` завершится с ошибкой (код != 0), выполнить `true` (всегда возвращает 0). Без этого Docker остановит сборку при любой ошибке. Ошибка возможна, если `STATIC_ROOT` не настроен или статики ещё нет |

**Зачем такая защита?** На этапе сборки образа база данных ещё не доступна. Некоторые приложения Django при `collectstatic` пытаются обратиться к БД — и падают. `2>/dev/null || true` позволяет пропустить эту ошибку и продолжить сборку.

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
wrk -t4 -c200 -d30s http://<ваш_IP>:8080/api/products

  4 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     ___       ___       ___     ___
    Req/Sec     ___       ___       ___     ___
  ___ requests in ___s, ___MB read
  Socket errors: connect ___, read ___, write ___, timeout ___
Requests/sec:     ___
Transfer/sec:     ___
```

#### Результат ab (gunicorn, 3 воркера, PostgreSQL):

```
ab -n 10000 -c 100 http://<ваш_IP>:8080/api/products

Server Software:        ___
Concurrency Level:      100
Time taken for tests:   ___ seconds
Complete requests:      10000
Failed requests:        ___
Requests per second:    ___ [#/sec] (mean)
Time per request:       ___ [ms] (mean)

  50%   ___
  66%   ___
  75%   ___
  90%   ___
  95%   ___
  99%   ___
 100%   ___ (longest request)
```

**Запишите проблемы, которые вы наблюдаете:**
- Req/sec: ___
- Таймауты: ___
- Вывод: ___

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
wrk -t4 -c200 -d30s http://<ваш_IP>:8080/api/products

  4 threads and 200 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     ___       ___       ___     ___
    Req/Sec     ___       ___       ___     ___
  ___ requests in ___s, ___MB read
  Socket errors: connect ___, read ___, write ___, timeout ___
Requests/sec:     ___
Transfer/sec:     ___
```

#### Стабильный тест (ab, 50 соединений):

```
ab -n 5000 -c 50 http://<ваш_IP>:8080/api/products

Server Software:        ___
Concurrency Level:      50
Complete requests:      5000
Failed requests:        ___
Requests per second:    ___ [#/sec] (mean)
Time per request:       ___ [ms] (mean)

  50%   ___
  66%   ___
  75%   ___
  80%   ___
  90%   ___
  95%   ___
  99%   ___
```

---

### Итоговое сравнение

| Конфигурация                          | Req/sec | Avg Latency | Timeouts | Errors |
|---------------------------------------|---------|-------------|----------|--------|
| Gunicorn 3 воркера                    |         |             |          |        |
| Uvicorn 4 воркера (conn_max_age=600)  |         |             |          |        |
| Uvicorn 4 воркера (conn_max_age=0)    |         |             |          |        |
| Gunicorn 8w + 4t (conn_max_age=600)   |         |             |          |        |
| Gunicorn 8w + 4t (ab, c=50)           |         |             |          |        |

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

---

## Часть 4. Настройка Nginx для django.h1n.ru

Nginx уже установлен на VPS и работает на порту 80.
Django-приложение запущено в Docker на порту 8080.
Нужно настроить проксирование: `django.h1n.ru` → `localhost:8080`.

---

### Шаг 15. Подключиться к VPS

```bash
ssh alekseeva@81.90.182.174
```

---

### Шаг 16. Создать конфиг Nginx

```bash
nano /etc/nginx/sites-available/django.h1n.ru
```

Вставить:

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

**Что делает каждая строка:**

| Строка | Назначение |
|--------|-----------|
| `listen 80` | Слушать порт 80 (HTTP) |
| `server_name django.h1n.ru` | Реагировать только на этот домен |
| `proxy_pass http://127.0.0.1:8080` | Перенаправить запросы на Django в Docker |
| `proxy_set_header Host $host` | Передать оригинальный домен в Django |
| `proxy_set_header X-Real-IP` | Передать реальный IP клиента |
| `location /static/` | Отдавать статику напрямую через Nginx (быстрее) |

---

### Шаг 17. Включить конфиг

Создать символическую ссылку в `sites-enabled` (нужен `sudo`):

```bash
sudo ln -s /etc/nginx/sites-available/django.h1n.ru /etc/nginx/sites-enabled/
```

---

### Шаг 18. Проверить конфигурацию

```bash
sudo nginx -t
```

> **Важно:** без `sudo` не работает — nginx не может прочитать SSL-сертификаты других сайтов.

Должно быть:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Если ошибка — проверьте синтаксис в конфиге.

---

### Шаг 19. Перезагрузить Nginx

```bash
sudo systemctl reload nginx
```

---

### Шаг 20. Настроить DNS

В панели управления доменом `h1n.ru` добавить **A-запись**:

| Тип | Имя | Значение |
|-----|-----|----------|
| A | django | 81.90.182.174 |

DNS обновляется от 5 минут до 24 часов.

---

### Шаг 21. Проверить

```bash
curl http://django.h1n.ru/api/health
# {"status": "ok"}
```

Или открыть в браузере: `http://django.h1n.ru`

---

### Шаг 22. Добавить HTTPS (Let's Encrypt)

#### Установить Certbot:

```bash
apt install certbot python3-certbot-nginx -y
```

#### Получить сертификат:

```bash
certbot --nginx -d django.h1n.ru
```

Certbot автоматически:
- Получит SSL-сертификат
- Изменит конфиг Nginx (добавит `listen 443 ssl`)
- Настроит редирект с HTTP на HTTPS
- Добавит автообновление сертификата (раз в 90 дней)

#### Проверить автообновление:

```bash
certbot renew --dry-run
```

#### Результат:

Сайт будет доступен по `https://django.h1n.ru`

---

### Шаг 23. Обновить ALLOWED_HOSTS

В `docker-compose.prod.yml` добавить домен:

```yaml
environment:
  ALLOWED_HOSTS: django.h1n.ru,81.90.182.174
```

Пересобрать:

```bash
cd /opt/shop
docker compose -f docker-compose.prod.yml up -d
```

---

### Полезные команды Nginx

| Действие | Команда |
|----------|---------|
| Статус Nginx | `systemctl status nginx` |
| Перезагрузить | `systemctl reload nginx` |
| Логи ошибок | `tail -f /var/log/nginx/error.log` |
| Логи доступа | `tail -f /var/log/nginx/access.log` |
| Проверить конфиг | `nginx -t` |
| Список сайтов | `ls /etc/nginx/sites-enabled/` |
| Сертификаты | `certbot certificates` |

---

### Итоговая схема

```
Браузер → django.h1n.ru
         ↓
   DNS → 81.90.182.174
         ↓
   Nginx (порт 80/443)
         ↓ proxy_pass
   Docker: gunicorn (порт 8080)
         ↓
   PostgreSQL (внутри Docker)
```

---

## Часть 5. Профилирование с помощью Django Silk

**Цель:** N+1 и лишние SQL по панели **Silk** на debug-эндпоинтах API. Только `DEBUG=True`.

### Шаг 24. Установка Silk

```bash
pip install django-silk
```

**`settings.py`:** `INSTALLED_APPS += ["silk"]`, `MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")`, при желании `SILKY_PYTHON_PROFILER = True`. **`urls.py`:** `path("silk/", include("silk.urls", namespace="silk"))`. Затем `migrate`. Панель: `http://127.0.0.1:8000/silk/`.

### Шаг 25. Эндпоинт N+1 (пример; у Order должен быть FK `product`, иначе замените логику)

```python
@router.get("/debug/orders-naive", tags=["debug"])
def orders_naive(request):
    orders = Order.objects.all()[:50]
    return [{"order_id": o.id, "product": o.product.name} for o in orders]
```

### Шаг 26. Эндпоинт COUNT в цикле

```python
@router.get("/debug/products-count-bad", tags=["debug"])
def products_count_bad(request):
    return [{"id": c.id, "name": c.name, "n": Order.objects.filter(product=c).count()}
            for c in VideoCard.objects.all()[:30]]
```

### Шаг 27. Эндпоинт тяжёлая выборка

```python
@router.get("/debug/products-dump", tags=["debug"])
def products_dump(request):
    return [{"id": p.id, "name": p.name} for p in VideoCard.objects.all()]
```

### Шаг 28. Задание

Зафиксировать в Silk **Num. Queries** для каждого URL; описать исправления (`select_related`, `annotate`, пагинация).

### Шаг 29. Очистка

```bash
python manage.py silk_clear_request_log
```

После Silk удобно перейти к Debug Toolbar на тех же идеях N+1, но на HTML-страницах.

---

## Часть 6. Профилирование с помощью Django Debug Toolbar

**Цель:** N+1 на HTML/HTMX (корзины, заказы). Данные — **`data.sql`**. Только `DEBUG=True`.

> Полный код шаблонов и views — в **`laba_vps_django.html`** (часть 6).

> На продакшене Toolbar не включать.

### Шаг 30. Установка

```bash
pip install django-debug-toolbar
```

**`config/settings.py`** (при `DEBUG=True`):

```python
if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "127.0.0.2"]
```

**`config/urls.py`:**

```python
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    # ... api, shop ...
]
if settings.DEBUG:
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns
```

### Шаг 31. «Плохие» views (намеренный N+1)

В **`shop/views.py`** добавьте импорты: `Cart`, `Order`. Два сценария:

1. **Корзины** — в шаблоне для каждой строки корзины обращение к `cart.product.name` без `select_related("product")`.
2. **Заказы** — в шаблоне для каждого заказа цикл по `order.orderitem_set.all` без `prefetch_related`.

```python
from django.shortcuts import render
from .models import VideoCard, Cart, Order


def home(request):
    return render(request, "shop/home.html")


def products_partial(request):
    products = VideoCard.objects.all()
    return render(request, "shop/products_list.html", {"products": products})


# --- Debug Toolbar: плохие partials (N+1) ---
def partial_carts_bad(request):
    carts = Cart.objects.all().order_by("-created_at")[:20]
    return render(request, "shop/partials/carts_bad.html", {"carts": carts})


def partial_orders_bad(request):
    orders = Order.objects.all().order_by("-created_at")[:12]
    return render(request, "shop/partials/orders_bad.html", {"orders": orders})


def debug_htmx_lab(request):
    """Страница с HTMX: два запроса partial — в каждом свой всплеск SQL."""
    return render(request, "shop/debug_htmx_lab.html")


def debug_profile_full(request):
    """Один запрос: корзины + заказы в одном ответе — много SQL сразу в Toolbar."""
    carts = Cart.objects.all().order_by("-created_at")[:15]
    orders = Order.objects.all().order_by("-created_at")[:10]
    return render(request, "shop/debug_profile_full.html", {
        "carts": carts,
        "orders": orders,
    })
```

### Шаг 32. Шаблоны partial (проблемные)

**`shop/templates/shop/partials/carts_bad.html`** — N+1 по `product`:

```html
{% for c in carts %}
<div class="cart-row">
  <strong>{{ c.product.name }}</strong> × {{ c.qty }}
  <span class="muted">{{ c.created_at|date:"d.m H:i" }}</span>
</div>
{% empty %}<p>Корзины пусты (залейте data.sql).</p>{% endfor %}
```

**`shop/templates/shop/partials/orders_bad.html`** — N+1 по позициям заказа:

```html
{% for o in orders %}
<section class="order">
  <header>Заказ #{{ o.id }} — {{ o.total }} ₽ <small>{{ o.created_at|date:"d.m.Y" }}</small></header>
  {% for line in o.orderitem_set.all %}
    <div class="line">{{ line.product_name }} × {{ line.qty }} @ {{ line.price }} ₽</div>
  {% endfor %}
</section>
{% empty %}<p>Нет заказов.</p>{% endfor %}
```

### Шаг 33. HTMX-страница лаборатории

**`shop/templates/shop/debug_htmx_lab.html`**

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Debug Toolbar + HTMX</title>
  <script src="https://unpkg.com/htmx.org@2.0.3"></script>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 1.5rem auto; padding: 0 1rem; }
    .panel { border: 1px solid #ccc; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; min-height: 3rem; }
    h1 { font-size: 1.25rem; }
  </style>
</head>
<body>
  <h1>Лаб: две «плохие» подгрузки (смотри SQL в Toolbar на каждый запрос partial)</h1>
  <p>Открой по отдельности в новой вкладке: <code>/partials/carts-bad/</code> и <code>/partials/orders-bad/</code> — панель Toolbar покажет число запросов.</p>
  <div class="panel">
    <h2>Корзины (HTMX)</h2>
    <div hx-get="/partials/carts-bad/" hx-trigger="load" hx-swap="innerHTML">Загрузка…</div>
  </div>
  <div class="panel">
    <h2>Заказы (HTMX)</h2>
    <div hx-get="/partials/orders-bad/" hx-trigger="load" hx-swap="innerHTML">Загрузка…</div>
  </div>
</body>
</html>
```

### Шаг 34. Одна страница — максимум запросов

**`shop/templates/shop/debug_profile_full.html`** — один GET, в шаблоне и корзины, и заказы (оба антипаттерна):

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Полный профиль (плохо нарочно)</title>
  <style> body { font-family: system-ui; max-width: 800px; margin: 1rem auto; } section { margin-bottom: 2rem; } </style>
</head>
<body>
  <h1>Корзины (N+1 по product)</h1>
  {% include "shop/partials/carts_bad.html" with carts=carts %}
  <h1>Заказы (N+1 по orderitem_set)</h1>
  {% include "shop/partials/orders_bad.html" with orders=orders %}
</body>
</html>
```

### Шаг 35. Маршруты

В **`config/urls.py`** (рядом с `home`, `products_partial`):

```python
from shop.views import (
    home, products_partial,
    partial_carts_bad, partial_orders_bad, debug_htmx_lab, debug_profile_full,
)

urlpatterns += [
    path("partials/carts-bad/", partial_carts_bad),
    path("partials/orders-bad/", partial_orders_bad),
    path("debug/htmx-lab/", debug_htmx_lab),
    path("debug/profile-full/", debug_profile_full),
]
```

### Задание

1. Залить **`data.sql`** (корзины и заказы уже есть).
2. Открыть **`/debug/profile-full/`** — в Toolbar записать **число SQL** до оптимизации.
3. Исправить views: `Cart.objects.select_related("product")…`, `Order.objects.prefetch_related("orderitem_set")…` — снова открыть страницу и сравнить.
4. Кратко описать разницу для отчёта.

