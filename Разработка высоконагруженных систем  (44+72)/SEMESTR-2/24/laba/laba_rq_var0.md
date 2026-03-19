## Лабораторная работа 

# Изучение фоновых задач и очередей (RQ, Django Tasks, Celery)

## Стенд


### 1. Архитектура приложения

Приложение разделено на три слоя:

| Слой | URL | Что возвращает | Файл |
|------|-----|----------------|------|
| Страница | `/` | Полный HTML | `views.py` → `home.html` |
| HTMX component | `/components/products/` | Фрагмент HTML | `views.py` → `products_list.html` |
| JSON API | `/api/products` | JSON | `api.py` (Django Ninja) |


### 2. Структура проекта

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
│   ├── views.py             # Страницы и HTMX components
│   ├── tasks.py             # Фоновые задачи (создаётся в лабораторной)
│   └── templates/shop/
│       ├── home.html         # Главная страница
│       ├── products_list.html # Список товаров (component)
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



# 3. JSON API — Django Ninja (`shop/api.py`)


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

###  4. Views — страницы и HTMX components (`shop/views.py`)

```python
from django.shortcuts import render
from .models import VideoCard


def home(request):
    return render(request, "shop/home.html")


def products_component(request):
    products = VideoCard.objects.all()
    return render(request, "shop/products_list.html", {"products": products})
```

- **`home`** — отдаёт полную HTML-страницу. Сама страница не содержит данных — они подгружаются через HTMX.
- **`products_component`** — возвращает HTML-фрагмент (не полную страницу). HTMX вставляет этот фрагмент внутрь `<div>` на главной странице.

---

###  5. Шаблоны

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
  <div hx-get="/components/products/" hx-trigger="load" hx-swap="innerHTML" class="loading">
    Загрузка…
  </div>
</body>
</html>
```

#### 6. Список товаров — component (`shop/templates/shop/products_list.html`)

```html
{% for product in products %}
  {% include "shop/components/product_card.html" %}
{% empty %}
  <p>Нет товаров</p>
{% endfor %}
```

#### 7. Компонент карточки (`shop/templates/shop/components/product_card.html`)

```html
<article class="product">
  <div class="name">{{ product.name }}</div>
  <div class="price">{{ product.price|floatformat:0 }} ₽</div>
  {% if product.description %}<p>{{ product.description }}</p>{% endif %}
</article>
```

### 8. Маршрутизация (`config/urls.py`)

```python
from django.urls import path
from shop.api import api
from shop.views import home, products_component

urlpatterns = [
    path("", home),
    path("components/products/", products_component),
    path("api/", api.urls),
]
```

### 9. requirements.txt

```
Django>=6.0
django-ninja>=1.0
gunicorn>=21.0
reportlab>=4.0
```

**Примечание.** Требуется Django 6.0+ (Tasks API). В проекте должна быть модель `VideoCard` (name, price, description) — см. data.sql и laba_rq.md. Модели Order, Cart нужны только для продвинутых сценариев.

---

# Вариант заданий: фоновые задачи (эволюционный подход)

**Логика:** сначала осваиваем новый API Django 6 (`@task`, `.enqueue()`), потом подключаем реальную очередь (django-rq). Код задач не меняется — меняется только бэкенд в настройках. Формы и кнопки используют **HTMX** (как в стенде) — ответы подставляются без перезагрузки.

---

## Часть 1. Django 6 Tasks — контракт и Immediate

### Задание 1.1. Кнопка «Скачать каталог в PDF» и первая Django Task

**Цель:** познакомиться с единым контрактом Django для фоновых задач. Добавляем на главную страницу кнопку, по нажатию ставится задача генерации PDF. С бэкендом по умолчанию (Immediate) задача выполняется сразу в том же потоке — отдельный воркер не нужен.

**Шаги:**

1. **Проверьте версию Django.** В корне проекта: `python manage.py version` или в shell: `import django; print(django.VERSION)`. Должна быть 6.0 и выше.

2. **Установите reportlab** (для генерации PDF):

```bash
pip install reportlab
```

3. **Проверьте настройки.** В `settings.py` должны быть `MEDIA_ROOT` и `MEDIA_URL`. Если их нет: `MEDIA_ROOT = BASE_DIR / "media"`, `MEDIA_URL = "media/"`. Папка `media/exports/` создаётся в коде задачи.

4. **Создайте файл `shop/tasks.py`** с задачей экспорта каталога:

```python
from django.tasks import task
import os
from django.conf import settings

@task()
def export_catalog_pdf() -> str:
    """Генерирует PDF-каталог товаров и сохраняет в media/exports/."""
    from .models import VideoCard
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = os.path.join(settings.MEDIA_ROOT, "exports", "catalog.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, "Каталог видеокарт")
    for i, p in enumerate(VideoCard.objects.all()):
        c.drawString(50, 770 - i * 20, f"{p.name} — {p.price:.0f} ₽")
    c.save()
    return path
```

**Почему задача без аргументов:** для простоты первая задача не принимает параметров. В следующих заданиях узнаем, что аргументы должны быть сериализуемы (примитивы, id моделей).

5. **Создайте view для кнопки** в `shop/views.py`:

```python
from django.shortcuts import redirect
from shop.tasks import export_catalog_pdf

def export_catalog(request):
    """По нажатию кнопки ставит задачу и возвращает ответ."""
    export_catalog_pdf.enqueue()
    return redirect("home")  # или render с сообщением «Экспорт запущен»
```

6. **Добавьте маршрут** в `config/urls.py`:

```python
path("export-catalog/", export_catalog, name="export_catalog"),
path("", home, name="home"),
```

7. **Добавьте кнопку на главную страницу** `shop/templates/shop/home.html` — перед блоком с товарами или рядом с заголовком:

```html
<p>
  <a href="{% url 'export_catalog' %}" style="display:inline-block; padding:0.5rem 1rem; background:#333; color:white; text-decoration:none; border-radius:4px;">
    Скачать каталог в PDF
  </a>
</p>
```

9. **Проверка.** С бэкендом Immediate при нажатии кнопки файл `media/exports/catalog.pdf` будет создан, сообщение «Экспорт запущен» появится без перезагрузки (HTMX). При django-rq ответ станет быстрее, PDF генерируется в фоне.

**Итог:** вы используете `@task` и `.enqueue()`. Код одинаков для Immediate, Dummy и будущего RQ — меняется только настройка бэкенда.

---

### Задание 1.2. Сериализация аргументов — что можно и нельзя передавать

**Цель:** понять, почему в задачу передаём примитивы и id, а не ORM-объекты. Наглядно: две кнопки — одна даёт ошибку, другая работает.

**Шаги:**

1. **Добавьте в `shop/tasks.py` вторую задачу** с аргументом:

```python
@task()
def export_product_pdf(product_id: int) -> str:
    """Экспорт одного товара — пример задачи с аргументом."""
    from .models import VideoCard
    p = VideoCard.objects.get(pk=product_id)
    return f"ok: {p.name}"
```

2. **Создайте страницу демонстрации** и два view в `shop/views.py`:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

def demo_serialization(request):
    """Страница с двумя кнопками: неправильно / правильно."""
    from .models import VideoCard
    product = VideoCard.objects.first()
    return render(request, "shop/demo_serialization.html", {"product": product})


@require_POST
def demo_serialization_wrong(request):
    """Передаём объект вместо id — будет ошибка сериализации."""
    from .models import VideoCard
    from .tasks import export_product_pdf
    product = get_object_or_404(VideoCard, pk=request.POST.get("product_id"))
    export_product_pdf.enqueue(product)  # объект — ошибка!
    return redirect("demo_serialization")


@require_POST
def demo_serialization_ok(request):
    """Передаём id — правильно."""
    from .models import VideoCard
    from .tasks import export_product_pdf
    product = get_object_or_404(VideoCard, pk=request.POST.get("product_id"))
    export_product_pdf.enqueue(product.id)  # id — ок
    if request.headers.get("HX-Request"):
        return render(request, "shop/components/demo_result.html", {"ok": True})
    return redirect("demo_serialization")
```

3. **Создайте фрагмент** `shop/templates/shop/components/demo_result.html`:

```html
<p id="demo-result" class="demo-ok">Задача поставлена (id передан корректно).</p>
```

4. **Создайте шаблон** `shop/templates/shop/demo_serialization.html` с HTMX (формы с `hx-post`, ответ подставляется в `#demo-result`):

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Демо сериализации</title>
  <script src="https://unpkg.com/htmx.org@2.0.3"></script>
</head>
<body>
  <h1>Сериализация аргументов задач</h1>
  {% if product %}
  <p>Товар: <strong>{{ product.name }}</strong> (id={{ product.id }})</p>
  <div id="demo-result"><!-- сюда HTMX подставит ответ --></div>
  <form method="post" action="{% url 'demo_serialization_wrong' %}" style="display:inline;"
        hx-post="{% url 'demo_serialization_wrong' %}" hx-target="#demo-result" hx-swap="innerHTML">
    {% csrf_token %}
    <input type="hidden" name="product_id" value="{{ product.id }}">
    <button type="submit" style="background:#c00;color:white;padding:0.5rem 1rem;">
      Неправильно: передать объект (→ ошибка)
    </button>
  </form>
  <form method="post" action="{% url 'demo_serialization_ok' %}" style="display:inline;"
        hx-post="{% url 'demo_serialization_ok' %}" hx-target="#demo-result" hx-swap="innerHTML">
    {% csrf_token %}
    <input type="hidden" name="product_id" value="{{ product.id }}">
    <button type="submit" style="background:#0a0;color:white;padding:0.5rem 1rem;">
      Правильно: передать id (→ ок)
    </button>
  </form>
  {% else %}
  <p>Нет товаров в каталоге.</p>
  {% endif %}
  <p><a href="{% url 'home' %}">← На главную</a></p>
</body>
</html>
```

5. **Добавьте маршруты** в `config/urls.py` (и импорт view):

```python
from shop.views import (
    home, products_component, export_catalog,
    demo_serialization, demo_serialization_wrong, demo_serialization_ok,
)
# ...
path("demo-serialization/", demo_serialization, name="demo_serialization"),
path("demo-serialization/wrong/", demo_serialization_wrong, name="demo_serialization_wrong"),
path("demo-serialization/ok/", demo_serialization_ok, name="demo_serialization_ok"),
```

6. **Добавьте ссылку на главной** (в `home.html`):  
   `<a href="{% url 'demo_serialization' %}">Демо: сериализация</a>`

7. **Проверка.** Откройте `/demo-serialization/`. Кнопка «Неправильно» — в `#demo-result` появится traceback (500). Кнопка «Правильно» — «Задача поставлена» без перезагрузки. Задача выполнится (Immediate).

8. **В отчёте ответьте:**
   - Какую ошибку вы увидели при нажатии «Неправильно»?
   - Почему объект ORM нельзя передать в очередь?
   - Какие типы данных можно передавать? (Числа, строки, списки, словари, id.)

**Итог:** правило «только примитивы и id» — основа работы с очередями.

---

### Задание 1.3. DummyBackend в тестах

**Цель:** научиться тестировать код с задачами так, чтобы сами задачи не выполнялись — без Redis, без реальных писем и файлов.

**Зачем это нужно.** При вызове `export_catalog_pdf.enqueue()` поведение зависит от бэкенда:
- **Immediate** — задача выполняется сразу (генерирует PDF, отправляет письмо и т.д.)
- **RQ/Celery** — задача попадает в очередь и выполняется воркером
- **Dummy** — задача не выполняется, только фиксируется факт вызова `enqueue`

Если в тестах оставить Immediate или поднимать Redis, при проверке view или API задачи будут реально выполняться: пойдут письма, создадутся файлы. Тесты станут медленными, хрупкими и потребуют внешних сервисов.

С **DummyBackend** в тестах `enqueue` вызывается, но код задачи не запускается. Можно проверить, что «задачу поставили в очередь с правильными аргументами», без побочных эффектов. Переключение — только в настройках, код не меняется.

**Шаги:**

1. **Создайте или дополните тестовый модуль** (например, `shop/tests.py`).

2. **Переопределите настройки для тестов.** В `shop/tests.py`:

```python
from django.test import TestCase, override_settings

@override_settings(
    TASKS={
        "default": {
            "BACKEND": "django.tasks.backends.dummy.DummyBackend",
        },
    }
)
class ExportTasksTest(TestCase):
    def test_export_catalog_enqueue_does_not_run_task(self):
        """При DummyBackend enqueue не выполняет задачу, но не падает."""
        from shop.tasks import export_catalog_pdf
        result = export_catalog_pdf.enqueue()
        self.assertIsNotNone(result)
        # Код задачи не выполнялся — PDF не генерировался, в консоли нет [TASK]
```

3. **Запустите тесты:** `python manage.py test shop.tests.ExportTasksTest`

4. **Проверка:** тест проходит, PDF не создаётся — значит, код задачи не выполнялся. DummyBackend лишь фиксирует факт вызова `enqueue`.

**Итог:** в проде — Immediate или RQ (реальное выполнение), в тестах — Dummy (ничего не выполняется). В CI не нужен Redis; тесты быстрые и изолированные.

---

## Часть 2. Реальный фон — django-rq

### Задание 2.1. Установка django-rq и Redis

**Цель:** подключить реальную очередь на Redis. Задачи будут выполняться в отдельном процессе (воркере).

**Шаги:**

1. **Установите пакеты:**

```bash
pip install django-rq redis
```

Добавьте в `requirements.txt`:

```
django-rq>=2.10
redis>=5.0
```

2. **Настройте `settings.py`:**

```python
INSTALLED_APPS = [
    # ...
    "django_rq",
]

RQ_QUEUES = {
    "default": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0,
    },
}
```

Для гибкости лучше брать из переменных окружения:

```python
import os
RQ_QUEUES = {
    "default": {
        "URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    },
}
```

3. **Запустите Redis.**

- **Локально:** установите Redis (Windows: WSL или Redis для Windows; Linux/macOS: `redis-server`).
- **Docker:** добавьте в `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  web:
    # ... ваш сервис
    environment:
      - REDIS_URL=redis://redis:6379/0
```

4. **Переведите задачи на django-rq.** Используйте «чистый» django-rq: задача — обычная функция (без `@task`), постановка — через `get_queue().enqueue()`.

- Задача `export_catalog_pdf` остаётся обычной функцией (уберите декоратор `@task`):

```python
# shop/tasks.py — для django-rq убираем @task()
def export_catalog_pdf() -> str:
    # ... тот же код, что в задании 1.1
```

- В view `export_catalog` заменяете вызов (сохраняйте проверку `HX-Request` для HTMX):

```python
from django_rq import get_queue
from shop.tasks import export_catalog_pdf

queue = get_queue("default")
queue.enqueue(export_catalog_pdf)
if request.headers.get("HX-Request"):
    return render(request, "shop/components/export_status.html", {"message": "Экспорт запущен"})
return redirect("home")
```

5. **Проверка:** команда `python manage.py rqworker default` запускается без ошибок (Redis должен быть запущен).

---

### Задание 2.2. Запуск воркера и проверка фона

**Цель:** убедиться, что задача выполняется в отдельном процессе, а не в веб-воркере.

**Шаги:**

1. **Запустите Redis** (если ещё не запущен).

2. **В первом терминале** запустите веб-сервер:

```bash
python manage.py runserver
```

3. **Во втором терминале** запустите воркер RQ:

```bash
python manage.py rqworker default
```

4. **Нажмите кнопку «Скачать каталог в PDF»** на главной странице.

5. **Наблюдение:**
   - Файл `media/exports/catalog.pdf` **создаётся воркером**, а не процессом runserver.
   - HTTP-ответ приходит быстро (без ожидания генерации PDF).

**Объяснение:** веб-сервер только кладёт задачу в Redis и возвращает ответ. Воркер забирает задачу из Redis и выполняет `export_catalog_pdf` в своём процессе. Это и есть «настоящий» фон.

---

### Задание 2.3. Веб-интерфейс django-rq

**Цель:** научиться смотреть очереди и упавшие задачи через браузер.

**Шаги:**

1. **Подключите URL** django-rq в `config/urls.py`:

```python
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("rq/", include("django_rq.urls")),
    # ... остальные маршруты
]
```

2. **Откройте в браузере:** `http://127.0.0.1:8000/rq/` (или ваш хост/порт).

3. **Изучите интерфейс:**
   - Список очередей (default, high, low и т.д.)
   - Количество задач в очереди, выполняемых, завершённых, упавших
   - Клик по очереди — список джобов
   - Клик по джобу — аргументы, результат, traceback при ошибке

4. **В отчёте** (или скриншоте) опишите: сколько очередей, что видно в default, есть ли failed jobs и можно ли перезапустить упавшую задачу.

**Важно:** в проде URL `/rq/` нужно закрыть от посторонних (только для админов, по VPN и т.п.).

---

### Задание 2.4. Retry при ошибке

**Цель:** настроить автоматический повтор при временных сбоях.

**Шаги:**

1. **Добавьте в `shop/tasks.py` задачу для демонстрации retry** (или измените `export_product_pdf`):

```python
def demo_retry_task(value: int) -> str:
    """При value=999 имитирует сетевую ошибку — для проверки retry."""
    if value == 999:
        raise ConnectionError("Имитация сетевой ошибки")
    return "ok"
```

2. **Поставьте задачу с retry** (в Django shell или во временном view):

```python
from rq import Retry
from django_rq import get_queue

queue = get_queue("default")
queue.enqueue(demo_retry_task, 999, retry=Retry(max=3))
```

3. **Наблюдение в веб-интерфейсе django-rq:**
   - Задача перейдёт в failed после нескольких попыток
   - В истории джоба видно количество попыток
   - Можно вручную перезапустить (Requeue)

4. **В отчёте** опишите: сколько попыток сделал RQ, как выглядит failed job, зачем нужен retry в проде (сетевые сбои, временная недоступность API).

---

## Часть 3. Практические сценарии

### Задание 3.1. Экспорт каталога в PDF (в фоне)

**Цель:** тяжёлую операцию (генерация PDF) вынести в фон, чтобы HTTP-ответ был быстрым.

**Шаги:**

1. **Установите библиотеку для PDF** (одну на выбор):

```bash
pip install reportlab
# или
pip install weasyprint
```

2. **Задача** `export_catalog_pdf` уже реализована в задании 1.1. Для django-rq уберите декоратор `@task()` — оставьте обычную функцию. Если задача ещё с `@task`, замените вызов `enqueue()` на `get_queue().enqueue()`.

3. **Добавьте API-эндпоинт** в `shop/api.py`:

```python
@api.post("/export-catalog")
def api_export_catalog(request):
    from django_rq import get_queue
    from shop.tasks import export_catalog_pdf
    queue = get_queue("default")
    job = queue.enqueue(export_catalog_pdf)
    return {"status": "queued", "job_id": job.id, "message": "Экспорт запущен"}
```

4. **Проверка:**
   - POST на `/api/export-catalog` возвращает ответ за миллисекунды
   - Файл `media/exports/catalog.pdf` появляется после выполнения воркером

**Итог:** пользователь не ждёт генерацию PDF; тяжёлая работа — в фоне.

---

### Задание 3.2. Результат и статус задачи (опционально)

**Цель:** дать пользователю возможность проверять статус долгой задачи по id.

**Шаги:**

1. **Создайте модель** (опционально) для хранения `job_id`:

```python
# shop/models.py
class ExportJob(models.Model):
    job_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20, default="queued")
    created_at = models.DateTimeField(auto_now_add=True)
```

2. **При постановке задачи** сохраняйте `job.id` и возвращайте его в ответе (как в 3.1).

3. **Добавьте эндпоинт статуса:**

```python
@api.get("/export-status/{job_id}")
def export_status(request, job_id: str):
    from django_rq import get_queue
    from rq.job import Job
    queue = get_queue("default")
    try:
        job = Job.fetch(job_id, connection=queue.connection)
        return {"job_id": job_id, "status": job.get_status()}
    except Exception:
        return {"job_id": job_id, "status": "unknown"}
```

4. **Проверка:** после POST на export-catalog получите `job_id`, затем GET на `/api/export-status/{job_id}` — статусы `queued`, `started`, `finished`, `failed`.

---

### Задание 3.3. Несколько очередей (опционально)

**Цель:** разделить срочные и фоновые задачи по разным очередям.

**Шаги:**

1. **Добавьте очереди** в `settings.py`:

```python
RQ_QUEUES = {
    "high": {"URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0")},
    "default": {"URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0")},
    "low": {"URL": os.environ.get("REDIS_URL", "redis://localhost:6379/0")},
}
```

Можно использовать разные DB Redis (0, 1, 2) для изоляции.

2. **Быстрые задачи** — в `high`, тяжёлый экспорт — в `default`. Для RQ нужны обычные функции (без `@task`). Добавьте `quick_log` и используйте:

```python
# shop/tasks.py
def quick_log(msg: str) -> str:
    import logging
    logging.info(f"[HIGH] {msg}")
    return "ok"
```

```python
from django_rq import get_queue
get_queue("high").enqueue(quick_log, "срочное")
get_queue("default").enqueue(export_catalog_pdf)
```

3. **Запустите воркер** с приоритетом: `python manage.py rqworker high default low` — сначала обрабатываются задачи из high.

4. **Проверка:** при одновременных задачах в high и default сначала выполнится задача из high.

---

### Задание 3.4. «Пожаловаться» — отправка письма через реальный SMTP

**Цель:** научиться отправлять письма из фоновой задачи через реальный SMTP (Gmail, Yandex, Mail.ru). Пользователь нажимает «Пожаловаться», вводит текст — письмо уходит в фоне.

**Шаги:**

1. **Настройте SMTP** в `settings.py` по руководству `mailer.md`:

```python
# Пример для Yandex (или Gmail, Mail.ru — см. mailer.md)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your@yandex.ru')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

Для Gmail: 2FA + App Password. Пароли храните в переменных окружения, не в коде.

2. **Создайте задачу** в `shop/tasks.py`:

```python
def send_complaint(complaint_text: str, product_id: int | None = None, admin_email: str = None) -> str:
    """Отправляет жалобу на почту админу."""
    from django.core.mail import send_mail
    from django.conf import settings

    if not admin_email:
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else settings.EMAIL_HOST_USER

    subject = f"Жалоба на товар #{product_id}" if product_id else "Жалоба (общая)"
    message = complaint_text
    if product_id:
        from .models import VideoCard
        try:
            p = VideoCard.objects.get(pk=product_id)
            message = f"Товар: {p.name} (id={product_id})\n\n{complaint_text}"
        except VideoCard.DoesNotExist:
            pass

    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=[admin_email],
        fail_silently=False,
    )
    return "sent"
```

3. **Создайте view и форму** в `shop/views.py`:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def complaint(request, product_id):
    """product_id из URL /complaint/<product_id>/."""
    from django_rq import get_queue
    from .tasks import send_complaint
    from .models import VideoCard

    product = get_object_or_404(VideoCard, pk=product_id)

    if request.method == "POST":
        text = request.POST.get("complaint_text", "").strip()
        if text:
            queue = get_queue("default")
            queue.enqueue(send_complaint, text, product_id)
            if request.headers.get("HX-Request"):
                return render(request, "shop/components/complaint_success.html")
            return redirect("home")

    return render(request, "shop/complaint.html", {"product": product})
```

4. **Создайте фрагмент** `shop/templates/shop/components/complaint_success.html`:

```html
<p class="complaint-ok">Жалоба отправлена. Письмо уйдёт в фоне.</p>
```

5. **Создайте шаблон** `shop/templates/shop/complaint.html` с HTMX:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Пожаловаться</title>
  <script src="https://unpkg.com/htmx.org@2.0.3"></script>
</head>
<body>
  <h1>Пожаловаться</h1>
  {% if product %}<p>По товару: <strong>{{ product.name }}</strong></p>{% endif %}
  <div id="complaint-result"></div>
  <form method="post" hx-post="{% url 'complaint' product.id %}" hx-target="#complaint-result" hx-swap="innerHTML">
    {% csrf_token %}
    <textarea name="complaint_text" rows="4" cols="50" placeholder="Опишите проблему..." required></textarea><br>
    <button type="submit">Отправить</button>
  </form>
  <p><a href="{% url 'home' %}">← Назад</a></p>
</body>
</html>
```

6. **Добавьте кнопку и маршрут.** В карточку товара `product_card.html`:

```html
<a href="{% url 'complaint' product.id %}">Пожаловаться</a>
```

В `config/urls.py`:

```python
from shop.views import ..., complaint
path("complaint/<int:product_id>/", complaint, name="complaint"),
```

7. **Проверка:** нажмите «Пожаловаться», введите текст, отправьте. Сообщение «Жалоба отправлена» появится без перезагрузки (HTMX). Письмо уйдёт воркером — проверьте почту.

**Итог:** письма из фоновой задачи через реальный SMTP. В проде — то же: задача в очереди, воркер отправляет письмо.

---

### Задание 3.5. Celery — альтернатива django-rq (опционально)

**Цель:** познакомиться с Celery — более мощной системой очередей. Переписать одну задачу с django-rq на Celery.

**Когда использовать Celery:** сложные пайплайны (цепочки, группы), расписание (beat), RabbitMQ, большая нагрузка. Для простых задач (письмо, PDF) django-rq достаточно.

**Шаги:**

1. **Установите Celery** и django-celery-results (для хранения результатов в БД):

```bash
pip install celery django-celery-results
```

2. **Создайте конфигурацию Celery** — файл `config/celery.py`:

```python
from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

В `config/__init__.py`:

```python
from .celery import app as celery_app
__all__ = ("celery_app",)
```

3. **Настройте** `settings.py` и выполните миграции:

```python
INSTALLED_APPS += ["django_celery_results"]

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = "django-db"  # или "redis://localhost:6379/2"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
```

```bash
python manage.py migrate django_celery_results
```

4. **Создайте Celery-задачу** в `shop/tasks.py` (или отдельный модуль `shop/celery_tasks.py`):

```python
from config.celery import app

@app.task
def export_catalog_pdf_celery() -> str:
    """Тот же экспорт PDF, но через Celery."""
    from .models import VideoCard
    import os
    from django.conf import settings
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path = os.path.join(settings.MEDIA_ROOT, "exports", "catalog_celery.pdf")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica", 14)
    c.drawString(50, 800, "Каталог видеокарт (Celery)")
    for i, p in enumerate(VideoCard.objects.all()):
        c.drawString(50, 770 - i * 20, f"{p.name} — {p.price:.0f} ₽")
    c.save()
    return path
```

5. **Вызовите задачу** в view или API — вместо `get_queue().enqueue(...)`:

```python
from shop.tasks import export_catalog_pdf_celery
export_catalog_pdf_celery.delay()
```

6. **Запустите воркер Celery** (в отдельном терминале):

```bash
celery -A config worker -l info
```

7. **Проверка:** кнопка или API ставит задачу, Celery worker выполняет, файл `catalog_celery.pdf` создаётся.

**Итог:** Celery использует тот же Redis (или RabbitMQ), но свой API: `@app.task` и `.delay()`. В проде — отдельный процесс `celery worker` и, при необходимости, `celery beat` для расписания.

---

## Часть 4. Деплой

### Задание 4.1. Воркер в Docker Compose

**Цель:** в проде воркер должен работать как отдельный контейнер и перезапускаться при падении.

**Шаги:**

1. **Откройте `docker-compose.prod.yml`** (или создайте, если его нет).

2. **Добавьте сервисы** `redis` и `rq-worker`:

```yaml
services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8080
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  rq-worker:
    build: .
    command: python manage.py rqworker default
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
      - web

volumes:
  redis_data: {}
```

3. **В `settings.py`** убедитесь, что `RQ_QUEUES` использует `REDIS_URL` из окружения.

4. **Проверка:** `docker-compose -f docker-compose.prod.yml up` — поднимаются web, redis и rq-worker. При нажатии кнопки PDF или POST на `/api/export-catalog` задача выполняется в контейнере `rq-worker`.

---

### Задание 4.2. Unit-файл systemd (опционально)

**Цель:** запускать воркер как службу на голой VM (без Docker).

**Шаги:**

1. **Создайте файл** `/etc/systemd/system/rq-worker.service` (или в проекте `deploy/rq-worker.service`):

```ini
[Unit]
Description=RQ worker for Django shop
After=network.target redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/shop
ExecStart=/opt/shop/venv/bin/python manage.py rqworker default
Environment="REDIS_URL=redis://localhost:6379/0"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Команды для активации** (на сервере):

```bash
sudo systemctl daemon-reload
sudo systemctl enable rq-worker
sudo systemctl start rq-worker
sudo systemctl status rq-worker
```

3. **Логи:** `journalctl -u rq-worker -f`

---

## Минимальный набор для зачёта

- **Часть 1:** задания 1.1, 1.2, 1.3  
- **Часть 2:** задания 2.1, 2.2, 2.3  
- **Часть 3:** одно из 3.1, 3.2, 3.3, 3.4; 3.5 (Celery) — по желанию  
- **Часть 4:** задание 4.1  

---

## Чек-лист сдачи

| № | Задание | Статус |
|---|---------|--------|
| 1.1 | Кнопка «Скачать каталог в PDF» и задача `export_catalog_pdf` с `@task` | ☐ |
| 1.2 | Ошибка сериализации зафиксирована и объяснена | ☐ |
| 1.3 | Тест с DummyBackend | ☐ |
| 2.1 | django-rq и Redis настроены | ☐ |
| 2.2 | Воркер запущен, задача выполняется в фоне | ☐ |
| 2.3 | Веб-интерфейс django-rq изучен | ☐ |
| 2.4 | Retry продемонстрирован | ☐ |
| 3.1 | Экспорт каталога в фоне | ☐ |
| 3.2 | API статуса по job_id | ☐ |
| 3.3 | Несколько очередей | ☐ |
| 3.4 | «Пожаловаться» — письмо через реальный SMTP | ☐ |
| 3.5 | Celery — задача с .delay() (опционально) | ☐ |
| 4.1 | rq-worker в docker-compose | ☐ |
| 4.2 | Unit-файл systemd | ☐ |

