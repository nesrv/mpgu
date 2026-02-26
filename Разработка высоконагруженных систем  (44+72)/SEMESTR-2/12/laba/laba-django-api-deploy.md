Лабораторная работа: 
Создание и настройка Django-приложения с REST API на основе Django Ninja с использованием CI/CD

**Цели:**
- Создать Django-приложение e-shop с REST API (Django Ninja)
- Настроить деплой и CI/CD на Railway
- Провести нагрузочное тестирование (ab, wrk)
- Исследовать влияние параметров Gunicorn (workers, threads) на метрики

---

## 1. Исходные данные (e-shop)

### Таблица `video_cards`

```sql
CREATE TABLE IF NOT EXISTS video_cards (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    price       REAL NOT NULL,
    description TEXT,
    created_at  TEXT DEFAULT (datetime('now'))
);
```

### Таблица `cart`

```sql
CREATE TABLE IF NOT EXISTS cart (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL REFERENCES video_cards(id),
    qty         INTEGER NOT NULL DEFAULT 1,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    total       REAL NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_name TEXT NOT NULL,
    qty         INTEGER NOT NULL,
    price       REAL NOT NULL
);

-- Минимальные данные для тестов и локального запуска (дублируем shop.json)
DELETE FROM video_cards;
INSERT INTO video_cards (name, price, description, created_at) VALUES
  ('NVIDIA GeForce RTX 5090', 230000.00, 'Флагманская видеокарта 2026 года.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4090', 165000.00, 'Мощная видеокарта для рейтрейсинга.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 5080', 130000.00, 'Высокая производительность для 4K.', '2026-01-15 10:00:00'),
  ('AMD Radeon RX 9070 XT', 95000.00, 'Лучшее соотношение цена/производительность.', '2026-01-15 10:00:00'),
  ('NVIDIA GeForce RTX 4080 Super', 115000.00, 'Мощная видеокарта для 4K с DLSS.', '2026-01-15 10:00:00');

```

---

## 2. Развёртывание стенда (стек: Python 3.13+, Django 5+, Ninja, sqlite)

### 2.1 Создание проекта

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS

pip install django django-ninja gunicorn psycopg[binary]
django-admin startproject config .
python manage.py startapp shop
```

### 2.2 Зависимости (`requirements.txt`)

```text
Django>=5.0
django-ninja>=1.0
gunicorn>=21.0
uvicorn>=0.28.0
psycopg[binary]>=3.1
```

### 2.3 Подключение приложения и БД

В `config/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "shop",
]

# SQLite для локального запуска (по умолчанию)
# Для PostgreSQL: ENGINE="django.db.backends.postgresql", NAME, USER, PASSWORD, HOST из env
```

### 2.4 Запуск локально (SQLite)

```bash
python manage.py makemigrations shop
python manage.py migrate
python manage.py runserver 8000
```

### 2.5 Запуск с CI/CD на Railway

1. Создай проект на [railway.app](https://railway.app), подключи GitHub-репозиторий.
2. Добавь переменные: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`.
3. Для PostgreSQL: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
4. В `railway.json` или Procfile:

```json
{
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 1",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

---

## 3. Проектирование API для e-shop

### 3.1 Модели Django (`shop/models.py`)

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

### 3.2 API Ninja (`shop/api.py`)

```python
from ninja import NinjaAPI, Schema
from .models import VideoCard

api = NinjaAPI(urls_namespace="api")

class ProductOut(Schema):
    id: int
    name: str
    price: float
    description: str

@api.get("/products", response=list[ProductOut])
def list_products(request):
    return list(VideoCard.objects.values("id", "name", "price", "description"))

@api.get("/products/{product_id}", response=ProductOut)
def get_product(request, product_id: int):
    p = VideoCard.objects.get(id=product_id)
    return {"id": p.id, "name": p.name, "price": float(p.price), "description": p.description or ""}

@api.get("/health")
def health(request):
    return {"status": "ok"}
```

### 3.3 Обычный Django view (для сравнения производительности)

```python
# shop/views.py
from django.http import JsonResponse
from .models import VideoCard

def products_django(request):
    data = list(VideoCard.objects.values("id", "name", "price", "description"))
    return JsonResponse({"products": data})
```

### 3.4 URL-маршруты (`config/urls.py`)

```python
from django.urls import path
from shop.api import api
from shop.views import products_django

urlpatterns = [
    path("api/", api.urls),
    path("products-django/", products_django),
]
```

---

## 4. Тестирование метрик с ab и wrk

### 4.1 Нагрузочный SQL-запрос (для анализа БД)

```sql
-- Запрос каталога товаров (используется эндпоинтом /api/products)
SELECT id, name, price, description FROM video_cards ORDER BY id;
```

### 4.2 Три тестовых URL

| № | URL | Описание |
|---|-----|----------|
| 1 | `http://127.0.0.1:8000/api/products` | API Ninja (JSON) |
| 2 | `http://127.0.0.1:8000/products-django/` | Обычный Django view (JSON) |
| 3 | `http://127.0.0.1:8000/api/health` или простой эндпоинт без БД | Минимальная нагрузка |

### 4.3 Тестирование с ab

```bash
# Apache Bench: 10000 запросов, 100 одновременных соединений
ab -n 10000 -c 100 http://127.0.0.1:8000/api/products
ab -n 10000 -c 100 http://127.0.0.1:8000/products-django/
ab -n 10000 -c 100 http://127.0.0.1:8000/api/health
```

### 4.4 Тестирование с wrk

```bash
# wrk: 4 потока, 200 соединений, 30 секунд
wrk -t4 -c200 -d30s http://127.0.0.1:8000/api/products
wrk -t4 -c200 -d30s http://127.0.0.1:8000/products-django/
wrk -t4 -c200 -d30s http://127.0.0.1:8000/api/health
```

### 4.5 Таблица результатов

| Инструмент | URL | RPS | Latency (avg/ms) | Latency (p95/ms) | Примечания |
|------------|-----|-----|------------------|------------------|------------|
| ab | /api/products | | | | |
| ab | /products-django/ | | | | |
| ab | /api/health | | | | |
| wrk | /api/products | | | | |
| wrk | /products-django/ | | | | |
| wrk | /api/health | | | | |


## 5. Экспериментальная часть

### 5.1 Разбор параметров Gunicorn

```bash
gunicorn config.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --threads ?
```

| Параметр | Значение | Описание |
|----------|----------|----------|
| `--bind` | 127.0.0.1:8000 | Адрес и порт для прослушивания |
| `--workers` | 3 | Число рабочих процессов. Итого одновременно: `workers × threads` запросов |
| `--threads` | ? (по умолчанию 1) | Число потоков на worker. Если не указан — `1` |

👉 **Итого при `workers=3`, `threads=1`:** максимум 3 одновременных запроса. При WSGI каждый запрос блокирует worker до ответа.

### 5.1b ASGI (Gunicorn + UvicornWorker)

```bash
pip install uvicorn
```

```bash
gunicorn config.asgi:application \
  --bind 127.0.0.1:8000 \
  --workers 4 \
  -k uvicorn.workers.UvicornWorker
```

- **`config.asgi:application`** — точка входа ASGI (событийная модель, async).
- **`-k uvicorn.workers.UvicornWorker`** — worker-класс Uvicorn вместо стандартного sync.
- **`threads`** для ASGI не задаётся — Uvicorn обрабатывает множество запросов асинхронно в одном процессе.

👉 **Итого:** ASGI даёт существенно больший RPS при той же нагрузке, особенно для IO-bound эндпоинтов.

### 5.2 Конфигурации для эксперимента (URL-ы см. в разделе 4)

Выполни ab/wrk для каждой конфигурации. Перед тестом запусти Gunicorn с нужными параметрами.

**WSGI:**

| № | Конфигурация | Команда |
|---|--------------|---------|
| 1 | workers 2 | `gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2` |
| 2 | workers 2, threads 3 | `gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --threads 3` |
| 3 | workers 5, threads 10 | `gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 5 --threads 10` |
| 4 | оптимизированная WSGI | см. п. 5.3 |

**ASGI:**

| № | Конфигурация | Команда |
|---|--------------|---------|
| 5 | ASGI, 2 workers | `gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 2` |
| 6 | ASGI, 4 workers | `gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 4` |
| 7 | ASGI, оптимизированная | см. п. 5.3b |

Результаты занеси в сводную таблицу (п. 5.4).



### 5.3 Оптимизированная конфигурация

```bash
gunicorn config.wsgi:application \
  --workers 5 \
  --threads 2 \
  --timeout 30 \
  --max-requests 10000 \
  --max-requests-jitter 1000
```

- `--timeout 30` — макс. время ожидания ответа (сек)
- `--max-requests 10000` — перезапуск worker после 10000 запросов (снижение утечек памяти)
- `--max-requests-jitter 1000` — разброс, чтобы воркеры не перезапускались одновременно

### 5.3b Оптимизированная конфигурация ASGI

```bash
gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --workers 4 \
  --timeout 30 \
  --max-requests 10000 \
  --max-requests-jitter 1000
```

Для Railway: `startCommand` с `config.asgi:application` и `-k uvicorn.workers.UvicornWorker`.

Измени в CI/CD (`railway.json`, Procfile) команду запуска: WSGI (workers 2, workers 2 threads 3, workers 5 threads 10, оптимизированная), затем ASGI (workers 2, workers 4, оптимизированная). После каждого изменения исследуй метрики.

### 5.4 Сводная таблица метрик

| Конфигурация | RPS (/api/products) | RPS (/products-django/) | Latency p95 |
|--------------|---------------------|-------------------------|-------------|
| WSGI workers 2 | | | |
| WSGI workers 2, threads 3 | | | |
| WSGI workers 5, threads 10 | | | |
| WSGI workers 5, threads 2, max-requests | | | |
| **ASGI workers 2** | | | |
| **ASGI workers 4** | | | |
| **ASGI workers 4, max-requests** | | | |

---

## Выводы

1. **Django Ninja vs обычный Django view** — Ninja даёт меньший overhead и обычно более высокий RPS.
2. **Workers и threads** — для WSGI: `workers = CPU × 2 + 1`. Рост `threads` до 2–4 полезен, дальше — GIL ухудшает latency.
3. **Оптимальная конфигурация** — для 2 vCPU: 5 workers, 2 threads, `max-requests` для стабильности.
4. **ASGI (Gunicorn + UvicornWorker)** — существенно выше RPS, рекомендуется для API на Django Ninja.

