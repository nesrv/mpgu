Учебный проект 
изучение RQ, Django Tasks, Celery

**Предусловия:** установлен [uv](https://docs.astral.sh/uv/), Python **3.13** (или совместимый с Django 6), ОС Linux/macOS/WSL. Команды — из корня проекта в терминале.

**шаг 0. Создание проекта**

```bash
mkdir RQ && cd RQ
uv init
uv add django
```

Далее шаг 1 можно начать с `uv run django-admin startproject config .` (если `django` уже добавлен — как в шаге 0).

---

шаг 1. Установка Django

Если шаг 0 пропущен: `mkdir RQ && cd RQ && uv init && uv add django`.

- `uv add django` (если ещё не добавлен на шаге 0)
- `uv run django-admin startproject config .`
- `uv run python manage.py startapp core`
- Добавить `core` в `INSTALLED_APPS` (config/settings.py)

шаг 2. Веб-интерфейс (HTMX)

- `uv add django-htmx` (версия `>=1.27` — v2 не существует)
- Добавить `django_htmx` и `core` в `INSTALLED_APPS` (config/settings.py)
- Добавить `django_htmx.middleware.HtmxMiddleware` в `MIDDLEWARE` (после SessionMiddleware)

**config/urls.py** — подключить core:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]
```

**core/urls.py**:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
]
```

**core/views.py**:
```python
from django.core.mail import send_mail
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


def _parse_emails(text):
    return [p.strip() for p in text.splitlines() if p.strip()]


def _send_to_list(emails, message):
    if not emails:
        return "Список email пуст. Введите получателей (по одному на строку)."
    if not message.strip():
        return "Введите текст сообщения."
    try:
        # Успех = SMTP-сервер принял письмо (250 OK); доставка в ящик не гарантирована
        send_mail("Сообщение", message, None, emails, fail_silently=False)
        return f"Отправлено {len(emails)} писем (принято сервером 250 OK)"
    except Exception as e:
        return f"Ошибка: {e}"


@require_http_methods(["GET", "POST"])
def index(request):
    success_message = None

    if request.method == "POST":
        message = request.POST.get("message", "")
        email_text = request.POST.get("email", "")
        emails = _parse_emails(email_text)
        success_message = _send_to_list(emails, message)

        if request.htmx:
            ctx = {"emails": emails, "success_message": success_message}
            return render(request, "core/partials/email_list.html", ctx)
        return render(
            request,
            "core/index.html",
            {"emails": emails, "success_message": success_message},
        )

    return render(request, "core/index.html", {"emails": [], "success_message": None})
```

**core/templates/core/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Сообщения и email</title>
    <script src="https://unpkg.com/htmx.org@2"></script>
</head>
<body>
    <h1>Рассылка по email</h1>

    <form hx-post="{% url 'index' %}" hx-target="#email-list" hx-swap="innerHTML" hx-trigger="submit">
        {% csrf_token %}
        <textarea name="message" placeholder="Сообщение" rows="4" cols="50"></textarea>
        <textarea name="email" placeholder="Email (по одному на строку)" rows="6" cols="50"></textarea>
        <button type="submit">Отправить</button>
    </form>

    <h2>Список email</h2>
    <div id="email-list">
        {% include "core/partials/email_list.html" %}
    </div>
</body>
</html>
```

**core/templates/core/partials/email_list.html**:
```html
{% if success_message %}<p>{{ success_message }}</p>{% endif %}
<ul>
    {% for email in emails %}
    <li>{{ email }}</li>
    {% empty %}
    <li>Пока пусто</li>
    {% endfor %}
</ul>
```

Перед запуском: `uv run python manage.py migrate` (сессии по умолчанию используют БД).

шаг 3. Настройка SMTP для отправки почты

Для Yandex и Mail.ru нужен **пароль приложения** (не обычный пароль).

**Яндекс — разрешить доступ почтовым клиентам:**
1. Почта Яндекса → Настройки (⚙) → вкладка «Почтовые программы»
2. Включить «Разрешить доступ к почтовому ящику с помощью почтовых клиентов»
3. Отметить «С сервера imap.yandex.ru по протоколу IMAP»
4. Включить «Пароли приложений и OAuth-токены»
5. Сохранить

**Пароль приложения (Яндекс):** [Пароли приложений](https://id.yandex.ru/security/app-passwords) → тип «Почта» → создать. Использовать в `EMAIL_HOST_PASSWORD`.

**config/settings.py** — добавить в конец:

```python
# Email
DEFAULT_FROM_EMAIL = "your-email@yandex.ru"  # или @mail.ru
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
```

**Yandex:**
```python
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@yandex.ru"
EMAIL_HOST_PASSWORD = "пароль-приложения"
```

**Mail.ru:**
```python
EMAIL_HOST = "smtp.mail.ru"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "your-email@mail.ru"
EMAIL_HOST_PASSWORD = "пароль-приложения"
```

**Безопасность** — лучше через переменные окружения:
```python
import os
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.yandex.ru")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
```

**Интеграция с формой:** одна кнопка «Отправить», emails вводятся построчно в textarea (парсинг через `splitlines()`). Без сессии — список получателей берётся из формы при отправке. View использует хелперы `_parse_emails`, `_send_to_list`; при ошибке показывает `Exception`.

**250 OK:** Успешная отправка = SMTP-сервер (Yandex) принял письмо и вернул код 250. Это не гарантия доставки в почтовый ящик получателя — только факт принятия на стороне сервера отправителя.

шаг 4. Собственный SMTP на VPS (mail.alekseeva.h1n.ru)

VPS, домен alekseeva.h1n.ru, почтовый сервер mail.alekseeva.h1n.ru.

**config/settings.py** — заменить или дополнить настройки email (нужен `import os` в начале файла, если его ещё нет):

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "mail.alekseeva.h1n.ru")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
# Для Dovecot SASL: alekseeva. Для Cyrus: alekseeva@mail.alekseeva.h1n.ru
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "alekseeva")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "alekseeva")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@alekseeva.h1n.ru")
```

**Тестовые email** (для проверки рассылки):

```
test1@example.com
test2@example.com
user1@example.org
user2@example.org
demo@example.net
sample@example.com
check@example.org
verify@example.net
mail1@example.com
mail2@example.com
recipient@example.org
sender@example.net
inbox@example.com
contact@example.org
info@example.net
```

шаг 5. Django 6 @task — фоновые задачи

Django 6 встроил Tasks framework. Декоратор `@task` + `.enqueue()` ставят задачу в очередь. По умолчанию `ImmediateBackend` выполняет синхронно; для фона — `django-tasks-local`.

**Базовое использование (без доп. пакетов):**
```python
from django.tasks import task

@task
def send_email_task(emails, message):
    send_mail("Сообщение", message, None, emails, fail_silently=False)

# В view: send_email_task.enqueue(emails=emails, message=message)
```

**Фоновое выполнение — django-tasks-local:**
```bash
uv add django-tasks-local
```

**config/settings.py:**
```python
TASKS = {
    "default": {
        "BACKEND": "django_tasks_local.ThreadPoolBackend",
        "OPTIONS": {
            "MAX_WORKERS": 10,
            "MAX_RESULTS": 1000,
        },
    }
}
```

**core/tasks.py** (создать файл):
```python
from django.core.mail import send_mail
from django.tasks import task


@task
def send_email_task(emails, message):
    send_mail("Сообщение", message, None, emails, fail_silently=False)
```

**core/tasks.py** — пауза 1 сек в задаче (для демонстрации фона):
```python
import time
from django.core.mail import send_mail
from django.tasks import task

@task
def send_email_task(emails, message):
    time.sleep(1)  # искусственная пауза
    send_mail("Сообщение", message, None, emails, fail_silently=False)
```

**Важно:** этот вариант всё ещё отправляет **все** адреса **одним** вызовом `send_mail`. Для посекундного прогресса «Отправлено X из Y» в **шаге 5.1** задача **переписывается**: цикл по одному письму с паузой 1 сек и запись прогресса в кэш.

**core/views.py** — заменить вызов `_send_to_list` на фоновую постановку: переименуйте хелпер в `_send` (или оставьте имя и вызывайте новую логику из `index`):
```python
from core.tasks import send_email_task

def _send(emails, message):
    if not emails:
        return "Список email пуст."
    if not message.strip():
        return "Введите текст сообщения."
    try:
        send_email_task.enqueue(emails=emails, message=message)
        return f"В очередь: {len(emails)} писем"
    except Exception as e:
        return f"Ошибка: {e}"
```

**Ограничения django-tasks-local:** очередь в памяти, задачи теряются при перезапуске; отдельный worker не нужен — потоки в том же процессе.

**Итог шага 5:** в `settings.py` — `TASKS` с `ThreadPoolBackend`; файл `core/tasks.py`; в `views` — `_send` с `send_email_task.enqueue(...)`; `index` при необходимости обновить под новый хелпер (полная версия `index` — в шаге 5.1).

---

**шаг 5.1. HTMX polling — посекундный статус отправки**

Цель: показывать «Отправлено X из Y» в реальном времени, пока задача выполняется в фоне.

**Замена логики задачи:** в `core/tasks.py` функция `send_email_task` должна принимать `job_id`, отправлять письма **по одному** с паузой 1 сек между письмами и обновлять кэш `job_{job_id}` после каждого письма (см. блок кода ниже). Предыдущие варианты задачи из шага 5 на этот код **заменяются**.

**Поток работы:**
1. Пользователь отправляет форму → POST → view создаёт `job_id`, ставит задачу в очередь, возвращает partial с `job_id`.
2. Partial `email_list.html` рендерит блок с `hx-get="/status/<job_id>/"` и `hx-trigger="load, every 1s"`.
3. HTMX при загрузке (load) и далее каждую секунду запрашивает `/status/<job_id>/`.
4. View `status` читает из кэша `job_{job_id}` → `{total, sent}` и рендерит partial `status.html`.
5. Ответ подменяет блок (`hx-swap="outerHTML"`). Если в ответе снова есть div с `hx-get` и `hx-trigger="every 1s"`, HTMX продолжит опрос. Когда `done=True`, возвращаем финальный текст без polling — опрос останавливается.

---

**1. config/settings.py** — кэш для хранения прогресса:
```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
```

---

**2. core/tasks.py** — задача пишет прогресс в кэш:

- Принимает `job_id`, при старте кладёт в кэш `{total, sent: 0}`.
- Отправляет письма по одному с паузой 1 сек; после каждого обновляет `sent` в кэше.
- `timeout=300` — данные держим 5 минут, затем кэш протухнет.

```python
import time

from django.core.cache import cache
from django.core.mail import send_mail
from django.tasks import task


@task
def send_email_task(emails, message, job_id):
    total = len(emails)
    cache.set(f"job_{job_id}", {"total": total, "sent": 0}, timeout=300)
    for i, email in enumerate(emails):
        if i > 0:
            time.sleep(1)
        send_mail("Сообщение", message, None, [email], fail_silently=False)
        cache.set(f"job_{job_id}", {"total": total, "sent": i + 1}, timeout=300)
```

---

**3. core/views.py** — `_send` возвращает `(msg, job_id)`; новый view `status`:

- `_send`: генерирует `uuid4` как `job_id`, передаёт его в `send_email_task.enqueue()`, возвращает `(msg, job_id)`.
- `index`: при POST рендерит partial с контекстом `job_id`.
- `status`: читает `cache.get("job_{job_id}")`; при промахе — `sent=0, total=0, done=False`; при попадании — `done = sent >= total`, рендерит `status.html`.

```python
import uuid

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.tasks import send_email_task


def _parse_emails(text):
    return [p.strip() for p in text.splitlines() if p.strip()]


def _send(emails, message):
    if not emails:
        return "Список email пуст.", None
    if not message.strip():
        return "Введите текст сообщения.", None
    try:
        job_id = str(uuid.uuid4())
        send_email_task.enqueue(emails=emails, message=message, job_id=job_id)
        return f"В очередь: {len(emails)} писем", job_id
    except Exception as e:
        return f"Ошибка: {e}", None


@require_http_methods(["GET", "POST"])
def index(request):
    emails = []
    msg = None
    job_id = None
    if request.method == "POST":
        emails = _parse_emails(request.POST.get("email", ""))
        msg, job_id = _send(emails, request.POST.get("message", ""))
    ctx = {"emails": emails, "success_message": msg, "job_id": job_id}
    tpl = "core/partials/email_list.html" if request.htmx and request.method == "POST" else "core/index.html"
    return render(request, tpl, ctx)


@require_http_methods(["GET"])
def status(request, job_id):
    from django.core.cache import cache

    data = cache.get(f"job_{job_id}")
    if not data:
        return render(request, "core/partials/status.html", {"sent": 0, "total": 0, "done": False, "job_id": job_id})
    sent, total = data["sent"], data["total"]
    done = sent >= total
    return render(request, "core/partials/status.html", {"sent": sent, "total": total, "done": done, "job_id": job_id})
```

---

**4. core/urls.py** — маршрут для статуса:
```python
path("status/<str:job_id>/", views.status, name="status"),
```

---

**5. core/templates/core/partials/email_list.html** — блок polling при наличии `job_id`:

При успешной постановке в очередь показываем div, который при загрузке и каждую секунду запрашивает статус. `hx-swap="outerHTML"` — ответ полностью заменяет этот div.

```html
{% if success_message %}<p>{{ success_message }}</p>{% endif %}
{% if job_id %}
<div hx-get="{% url 'status' job_id %}" hx-trigger="load, every 1s" hx-swap="outerHTML">
    <p>Отправка...</p>
</div>
{% endif %}
<ul>
    {% for email in emails %}
    <li>{{ email }}</li>
    {% empty %}
    <li>Пока пусто</li>
    {% endfor %}
</ul>
```

---

**6. core/templates/core/partials/status.html** — ответ view `status`:

**Важно:** HTMX polling работает так: каждый ответ заменяет элемент с `hx-get`. Если в ответе нет нового элемента с `hx-get` и `hx-trigger`, опрос прекращается. Поэтому, пока `done=False`, нужно всегда возвращать div с `hx-get` и `hx-trigger="every 1s"`. При кэш-промахе (задача ещё не записала данные) нельзя возвращать только `<p>Отправка...</p>` — иначе polling сразу остановится. Обёртка div обязательна.

- `done=True` → финальное сообщение без polling.
- `done=False` → div с `hx-get` и `hx-trigger="every 1s"`; внутри — «Отправлено X из Y» или «Отправка...» при `total=0`.

```html
{% if done %}
<p>Готово: {{ total }} писем</p>
{% else %}
<div hx-get="{% url 'status' job_id %}" hx-trigger="every 1s" hx-swap="outerHTML">
    <p>{% if total %}Отправлено {{ sent }} из {{ total }}{% else %}Отправка...{% endif %}</p>
</div>
{% endif %}
```

**Итог шага 5.1:** `CACHES` (LocMemCache), `tasks.py` с `job_id` и циклом по письмам, `views` с `(msg, job_id)` и view `status`, `urls` — `status/<job_id>/`, обновлены `email_list.html` и `status.html`.

---

шаг 6. RQ (Redis Queue) — фоновые задачи с Redis

RQ — очередь задач на Redis. Отличие от django-tasks-local: задачи хранятся в Redis и не теряются при перезапуске; требуется отдельный worker-процесс.

**Переход с шага 5.1:** в `core/views.py` уберите импорт и вызов `send_email_task` (Django Tasks), подключите `get_queue` и `send_email_job` из RQ, как в примере ниже. Шаблоны и `status` не меняются.

**Установка пакетов:**
```bash
uv add django-rq django-redis
```
Пакет `rq` подтянется как зависимость. **Важно:** если проект в `pyproject.toml` называется `rq`, переименуйте в `rq-lab` — иначе конфликт с пакетом `rq`.

**Redis:**
- Linux/WSL: `sudo apt update && sudo apt install -y redis-server`, затем `sudo service redis-server start`
- Docker: `docker run -d -p 6379:6379 redis`
- На VPS: установить Redis, проверить `redis-cli ping` → `PONG`

**config/settings.py** — добавить приложение и настройки очередей:
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
    }
}

# Для удалённого Redis (VPS):
# RQ_QUEUES = {"default": {"URL": "redis://user:pass@host:6379/0"}}
```

**Кэш для polling — обязательно Redis.** Worker и runserver — разные процессы. `LocMemCache` хранит данные в памяти процесса, поэтому view не видит прогресс, который пишет worker. Нужен общий кэш — Redis. **config/settings.py** (заменить `CACHES`):
```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
```
DB 1 — чтобы не пересекаться с RQ, который использует DB 0.

**core/rq_jobs.py** (создать файл) — задача для RQ. Логика та же: пауза 1 сек, запись прогресса в кэш:
```python
import time

from django.core.cache import cache
from django.core.mail import send_mail


def send_email_job(emails, message, job_id):
    total = len(emails)
    cache.set(f"job_{job_id}", {"total": total, "sent": 0}, timeout=300)
    for i, email in enumerate(emails):
        if i > 0:
            time.sleep(1)
        send_mail("Сообщение", message, None, [email], fail_silently=False)
        cache.set(f"job_{job_id}", {"total": total, "sent": i + 1}, timeout=300)
```

**core/views.py** — изменить `_send`, чтобы ставить задачу в RQ вместо Django Tasks:
```python
from django_rq import get_queue

from core.rq_jobs import send_email_job

def _send(emails, message):
    # ... проверки ...
    try:
        job_id = str(uuid.uuid4())
        queue = get_queue("default")
        queue.enqueue(send_email_job, emails, message, job_id)
        return f"В очередь RQ: {len(emails)} писем", job_id
    except Exception as e:
        return f"Ошибка: {e}", None
```

View `status` и шаблоны (polling) остаются без изменений — по-прежнему читаем прогресс из кэша.

**Запуск worker** — обязательно в отдельном терминале (параллельно с runserver):
```bash
uv run python manage.py rqworker default
```

Без запущенного worker задачи будут лежать в Redis и не выполняться; письма не отправятся, статус «Отправка...» не изменится.

**Порядок запуска:** 1) Redis (`redis-server` или `sudo service redis-server start`), 2) worker (`uv run python manage.py rqworker default`), 3) сервер (`uv run python manage.py runserver`).

**Миграции:**
```bash
uv run python manage.py migrate
```
django-rq создаёт модели для хранения метаданных джобов.

**RQ Dashboard** (опционально) — просмотр очередей. **config/urls.py**:
```python
path("admin/django_rq/", include("django_rq.urls")),
```
Доступ: http://127.0.0.1:8000/admin/django_rq/

**Fallback при недоступности Redis** — при `Connection refused` можно добавить переключение на Django Tasks, чтобы рассылка работала без Redis (см. реализацию в `core/views.py`).

**Сравнение с django-tasks-local:**
| | django-tasks-local | RQ |
|---|---|---|
| Брокер | память процесса | Redis |
| Worker | потоки в том же процессе | отдельный процесс |
| Кэш для polling | LocMemCache (общий процесс) | Redis (разные процессы) |
| Устойчивость | задачи теряются при рестарте | задачи в Redis сохраняются |
| Зависимости | только Django | Redis, django-redis |

**Итог шага 6:** `django_rq` + `django-redis`, Redis-кэш, `rq_jobs.py`, `views._send` через `queue.enqueue`, worker `rqworker default`, при необходимости миграции и URL django_rq.

---

шаг 7. Celery — продвинутые фоновые задачи

Celery — полнофункциональная очередь задач: цепочки, группы, retry, отложенный запуск, расписание (Beat). Брокер — Redis или RabbitMQ. Redis уже установлен (шаг 6).

**Переход с шага 6:** в `views.py` замените RQ (`get_queue`, `send_email_job`) на вызов Celery-задачи (`send_email_celery_task.apply_async`), добавьте выбор очереди `high`/`low` в форму и в `_send`.

**Установка:**
```bash
uv add "celery[redis]"
```

**config/celery.py** (создать файл):
```python
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

**config/__init__.py** — загрузить Celery при старте Django:
```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

**config/settings.py** — настройки Celery:
```python
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/2"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_TASK_DEFAULT_QUEUE = "low"
```
DB 0 — брокер (можно шарить с RQ, разные ключи). DB 2 — результаты, чтобы не пересекаться с кэшем (DB 1).

**core/celery_tasks.py** (создать файл) — задача Celery:
```python
import time

from config.celery import app
from django.core.cache import cache
from django.core.mail import send_mail


@app.task
def send_email_celery_task(emails, message, job_id):
    total = len(emails)
    cache.set(f"job_{job_id}", {"total": total, "sent": 0}, timeout=300)
    for i, email in enumerate(emails):
        if i > 0:
            time.sleep(1)
        send_mail("Сообщение", message, None, [email], fail_silently=False)
        cache.set(f"job_{job_id}", {"total": total, "sent": i + 1}, timeout=300)
```

**core/views.py** — `_send` ставит задачу в Celery, с поддержкой выбора очереди:
```python
from core.celery_tasks import send_email_celery_task

def _send(emails, message, queue="low"):
    # ... проверки ...
    if queue not in ("high", "low"):
        queue = "low"
    try:
        job_id = str(uuid.uuid4())
        send_email_celery_task.apply_async((emails, message, job_id), queue=queue)
        return f"В очередь Celery ({queue}): {len(emails)} писем", job_id
    except Exception as e:
        return f"Ошибка: {e}", None

# В index при POST:
queue = request.POST.get("queue", "low")
msg, job_id = _send(emails, request.POST.get("message", ""), queue=queue)
```

**Форма** — выбор очереди (index.html):
```html
<p>
    <label><input type="radio" name="queue" value="high"> Высокий приоритет</label>
    <label><input type="radio" name="queue" value="low" checked> Низкий приоритет</label>
</p>
```

View `status` и шаблоны без изменений — прогресс по-прежнему в Redis-кэше.

**Запуск worker** (отдельный терминал). С двумя очередями — `high` обрабатывается раньше `low`:
```bash
uv run celery -A config worker -Q high,low -l info
```

**Порядок запуска:** Redis → Celery worker → runserver.

**Дополнительно Celery:**
- **Celery Beat** — периодические задачи: `celery -A config beat -l info`
- **Отложенный запуск:** `task.apply_async(countdown=60)`
- **Retry при ошибке:** `@app.task(bind=True, max_retries=3)` и `self.retry(exc=e)`

**шаг 7.1. Flower — веб-мониторинг Celery**

Flower — веб-интерфейс для просмотра очередей, воркеров, задач и их статусов.

**Установка:**
```bash
uv add flower
```

**Запуск** (отдельный терминал, после Celery worker):
```bash
uv run celery -A config flower
```

По умолчанию: http://localhost:5555

**Что показывает Flower:**
- **Dashboard** — воркеры, активные/завершённые задачи
- **Tasks** — список задач, их аргументы, результат, время выполнения
- **Workers** — состояние воркеров, обрабатываемые задачи
- **Broker** — очереди, количество сообщений
- **Monitor** — обновление в реальном времени

**С базовой аутентификацией** (опционально):
```bash
uv run celery -A config flower --basic_auth=user:password
```

**Итог шага 7:** Celery с Redis-брокером, `config/celery.py` и импорт в `config/__init__.py`, `core/celery_tasks.py`, `views` с `apply_async` и radio `queue` high/low, worker `celery -A config worker -Q high,low`, по желанию Flower.

**Сравнение RQ и Celery:**
| | RQ | Celery |
|---|---|---|
| Сложность | проще | сложнее |
| Брокер | только Redis | Redis, RabbitMQ |
| Расписание | нет (нужен cron) | Celery Beat |
| Цепочки/группы | нет | есть |
| Retry | базовый | гибкий |
| Мониторинг | django-rq | Flower |

---

шаг 8. CI/CD (GitHub Actions)

В репозитории: **`.github/workflows/`** — GitHub Actions **не** читает `deploy.yml` из корня проекта.

**8.1. CI — `.github/workflows/ci.yml`**

Запуск при push и pull request в ветки `master` и `main`:

- checkout, установка **uv**, Python **3.13**, `uv sync`
- `python manage.py migrate --check`
- `python manage.py check`

**8.2. Deploy — `.github/workflows/deploy.yml`**

Запуск при push в **`master`**:

- SSH на сервер (по умолчанию **alekseeva.h1n.ru**, пользователь **root**)
- На сервере: `cd` в **`DEPLOY_PATH`** (по умолчанию `/root/RQ`), `git pull`, `uv sync`, `migrate`, `collectstatic`, перезапуск **systemd**

**Secrets в GitHub** (Settings → Secrets and variables → Actions):

| Secret | Назначение |
|---|---|
| `SSH_PRIVATE_KEY` | приватный ключ SSH для доступа к серверу (обязательно) |
| `DB_PASSWORD` | опционально, для `PGPASSWORD` при PostgreSQL на сервере |

**Переменные в workflow** (править в `deploy.yml` при необходимости):

- `DEPLOY_SERVER` — хост VPS
- `DEPLOY_PATH` — путь к клону репозитория на сервере
- systemd: **`rq-lab`** (веб), **`rq-lab-celery`** (Celery worker; если unit нет — шаг игнорируется)

**Подготовка сервера:**

1. Клон репозитория в `DEPLOY_PATH`, установлен **uv** в PATH (`/root/.local/bin`).
2. Unit-файлы systemd для приложения и при необходимости Celery (см. также `deploy.md`).
3. На GitHub — репозиторий с Actions, добавлен secret `SSH_PRIVATE_KEY`.

**Локальный черновик** `deploy.yml` в корне не участвует в Actions; актуальная логика — только в `.github/workflows/deploy.yml`.

**Итог шага 8:** в репозитории есть `.github/workflows/ci.yml` и `deploy.yml`; в GitHub задан secret `SSH_PRIVATE_KEY`; на сервере — клон проекта, uv, systemd-сервисы (см. `deploy.md`).