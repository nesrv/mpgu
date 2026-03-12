# Методичка: Django Ninja + HTMX

Создание веб-приложения «Магазин видеокарт» с JSON API и HTMX-фронтом.

---

## Архитектура приложения

Приложение разделено на три слоя:

| Слой | URL | Что возвращает | Файл |
|------|-----|----------------|------|
| Страница | `/` | Полный HTML | `views.py` → `home.html` |
| HTMX partial | `/partials/products/` | Фрагмент HTML | `views.py` → `products_list.html` |
| JSON API | `/api/products` | JSON | `api.py` (Django Ninja) |

### Почему именно так?

- **JSON API** (`api.py`) — данные для внешних клиентов (мобильное приложение, Postman, другие сервисы). Возвращает чистый JSON.
- **HTMX partials** (`views.py`) — HTML-фрагменты для подгрузки в страницу без JavaScript. Возвращает готовый HTML.
- **Страницы** (`views.py`) — полные HTML-страницы с подключённым HTMX.

Главный принцип: **API не должен возвращать HTML, views не должны возвращать JSON.** Каждый слой отвечает за своё.

---

## Структура проекта

```
CI-CD-DJANGO-NINJA/
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
├── data.sql                 # Тестовые данные
├── requirements.txt
└── manage.py
```

---

## Шаг 1. Создание проекта

```bash
mkdir CI-CD-DJANGO-NINJA && cd CI-CD-DJANGO-NINJA
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

## Шаг 2. Модели (`shop/models.py`)

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

## Шаг 3. JSON API — Django Ninja (`shop/api.py`)

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

### Что здесь происходит:

- **`Schema`** — описывает формат JSON-ответа (как сериализатор в DRF). Django Ninja автоматически преобразует QuerySet в JSON по этой схеме.
- **`@api.get("/products", response=list[ProductOut])`** — декоратор создаёт GET-endpoint. Параметр `response` указывает схему ответа.
- **`get_object_or_404`** — если объект не найден, вернёт 404 вместо ошибки 500.
- **`/health`** — endpoint для проверки работоспособности приложения (используется при деплое).

### Результат:

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

## Шаг 4. Views — страницы и HTMX partials (`shop/views.py`)

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

## Шаг 5. Шаблоны

### Главная страница (`shop/templates/shop/home.html`)

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

### Как работает HTMX (без JavaScript):

```html
<div hx-get="/partials/products/" hx-trigger="load" hx-swap="innerHTML">
```

- **`hx-get`** — при срабатывании триггера отправить GET-запрос на указанный URL
- **`hx-trigger="load"`** — триггер: выполнить запрос сразу при загрузке страницы
- **`hx-swap="innerHTML"`** — полученный HTML вставить внутрь этого `<div>`

Результат: страница загружается → HTMX запрашивает `/partials/products/` → сервер возвращает HTML-фрагмент → HTMX вставляет его в `<div>`. Никакого JavaScript не нужно.

### Список товаров — partial (`shop/templates/shop/products_list.html`)

```html
{% for product in products %}
  {% include "shop/components/product_card.html" %}
{% empty %}
  <p>Нет товаров</p>
{% endfor %}
```

Это не полная страница, а фрагмент. `{% include %}` подключает компонент карточки для каждого товара.

### Компонент карточки (`shop/templates/shop/components/product_card.html`)

```html
<article class="product">
  <div class="name">{{ product.name }}</div>
  <div class="price">{{ product.price|floatformat:0 }} ₽</div>
  {% if product.description %}<p>{{ product.description }}</p>{% endif %}
</article>
```

Вынесен в отдельный файл, чтобы можно было переиспользовать в других местах (например, в корзине или на странице заказа).

---

## Шаг 6. Маршрутизация (`config/urls.py`)

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

## Шаг 7. Тестовые данные

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

## Шаг 8. Запуск и проверка

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

## Шаг 9. requirements.txt

```
Django>=5.0
django-ninja>=1.0
gunicorn>=21.0
```

---

## Принципы проектирования

### 1. Разделение API и представления

```
api.py   → только JSON (данные)
views.py → только HTML (представление)
```

API не знает про HTML. Views не формирует JSON. Каждый файл отвечает за свой формат.

### 2. HTMX вместо JavaScript

Классический подход: сервер отдаёт JSON → клиент на JS парсит и строит DOM.

HTMX-подход: сервер отдаёт готовый HTML → HTMX вставляет его в страницу. Не нужно писать JavaScript.

### 3. Компоненты шаблонов

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
