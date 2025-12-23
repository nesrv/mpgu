# Новые возможности Django 6.0

## Основные нововведения

| Возможность | Описание | Пример использования | Преимущества |
|-------------|----------|---------------------|--------------|
| **Template Partials** | Модуляризация шаблонов с помощью небольших именованных фрагментов | `{% partial "header" %}` | Более чистый и поддерживаемый код шаблонов |
| **Background Tasks** | Встроенный фреймворк для выполнения задач вне HTTP request-response цикла | `@background_task` | Гибкая система фоновых задач без внешних зависимостей |
| **Content Security Policy (CSP)** | Встроенная поддержка настройки и применения политик безопасности браузера | `CSP_MIDDLEWARE` | Защита от атак инъекции контента на уровне браузера |
| **Modernized Email API** | Использование Python `EmailMessage` для составления и отправки email | `EmailMessage()` | Более чистый, Unicode-friendly интерфейс |

---

## Template Partials

**Что это?**
Модульная система для создания переиспользуемых фрагментов шаблонов.

**До Django 6:**
```django
{# Нужно было использовать include или наследование #}
{% include "partials/header.html" %}
```

**В Django 6:**
```django
{# Определение partial #}
{% partial "header" %}
    <header>
        <h1>{{ site_name }}</h1>
    </header>
{% endpartial %}

{# Использование partial #}
{% partial "header" %}
```

**Преимущества:**
- ✅ Более чистый синтаксис
- ✅ Лучшая организация кода
- ✅ Переиспользование фрагментов
- ✅ Упрощенное тестирование

---

## Background Tasks

**Что это?**
Встроенный фреймворк для выполнения фоновых задач без внешних зависимостей (Celery, RQ).

**Пример использования:**
```python
from django.tasks import background_task

@background_task
def send_notification_email(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(
        subject='Notification',
        message=message,
        from_email='noreply@example.com',
        recipient_list=[user.email],
    )

# Вызов задачи
send_notification_email.delay(user.id, "Welcome!")
```

**Преимущества:**
- ✅ Не требует внешних зависимостей
- ✅ Простая настройка
- ✅ Интеграция с Django ORM
- ✅ Поддержка отложенных задач

**Настройка:**
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.tasks',  # Новое приложение
    # ...
]

# Настройка брокера (Redis, RabbitMQ и т.д.)
TASK_BROKER = 'redis://localhost:6379/0'
```

---

## Content Security Policy (CSP)

**Что это?**
Встроенная поддержка CSP для защиты от XSS и других атак инъекции контента.

**Настройка:**
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.ContentSecurityPolicyMiddleware',
    # ...
]

# Политика CSP
CSP_DEFAULT_SRC = "'self'"
CSP_SCRIPT_SRC = "'self' 'unsafe-inline'"
CSP_STYLE_SRC = "'self' 'unsafe-inline'"
CSP_IMG_SRC = "'self' data: https:"
```

**Пример конфигурации:**
```python
CSP_REPORT_URI = '/csp-report/'
CSP_REPORT_ONLY = False  # True для тестирования
```

**Преимущества:**
- ✅ Защита от XSS атак
- ✅ Контроль загружаемых ресурсов
- ✅ Встроенная поддержка
- ✅ Гибкая настройка политик

---

## Modernized Email API

**Что это?**
Обновленный API для работы с email на основе Python `EmailMessage`.

**До Django 6:**
```python
from django.core.mail import send_mail

send_mail(
    subject='Hello',
    message='Body',
    from_email='from@example.com',
    recipient_list=['to@example.com'],
)
```

**В Django 6:**
```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='Hello',
    body='Body',
    from_email='from@example.com',
    to=['to@example.com'],
)
email.send()

# Или с HTML
email = EmailMessage(
    subject='Hello',
    body='<h1>HTML Body</h1>',
    from_email='from@example.com',
    to=['to@example.com'],
)
email.content_subtype = 'html'
email.send()
```

**Преимущества:**
- ✅ Более Pythonic API
- ✅ Лучшая поддержка Unicode
- ✅ Гибкость в настройке
- ✅ Совместимость с Python email стандартами

---

## Изменения в поддержке Python

| Версия Python | Статус в Django 6 |
|---------------|-------------------|
| Python 3.10   | ❌ Не поддерживается |
| Python 3.11   | ❌ Не поддерживается |
| Python 3.12   | ✅ Поддерживается |
| Python 3.13   | ✅ Поддерживается |
| Python 3.14   | ✅ Поддерживается |

**Минимальная версия:** Python 3.12

---

## Другие улучшения

| Область | Улучшение | Описание |
|---------|-----------|----------|
| **ORM** | Улучшенные запросы | Оптимизация `select_related()` и `prefetch_related()` |
| **Admin** | Новый UI компонент | Улучшенный интерфейс админ-панели |
| **Forms** | Валидация | Расширенные возможности валидации форм |
| **Security** | Улучшенная защита | Дополнительные меры безопасности по умолчанию |
| **Performance** | Оптимизации | Улучшения производительности запросов |

---

## Миграция с Django 5.x

**Шаги миграции:**

1. **Обновление Python:**
   ```bash
   python --version  # Должно быть 3.12+
   ```

2. **Обновление зависимостей:**
   ```bash
   pip install --upgrade Django==6.0
   ```

3. **Проверка устаревших функций:**
   ```bash
   python manage.py check --deploy
   ```

4. **Обновление кода:**
   - Заменить `send_mail()` на `EmailMessage()` (опционально)
   - Обновить шаблоны для использования `{% partial %}`
   - Настроить CSP middleware (если нужно)

5. **Тестирование:**
   ```bash
   python manage.py test
   ```

---

## Сравнение с предыдущими версиями

| Функция | Django 4.x | Django 5.x | Django 6.0 |
|---------|-----------|-----------|-------------|
| Template Partials | ❌ | ❌ | ✅ |
| Background Tasks | ❌ | ❌ | ✅ |
| CSP Support | ❌ | ❌ | ✅ |
| Modern Email API | ❌ | ❌ | ✅ |
| Python 3.12+ | ✅ | ✅ | ✅ |
| Python 3.10-3.11 | ✅ | ✅ | ❌ |

---

## Рекомендации по использованию

**Используйте Template Partials, если:**
- ✅ У вас много повторяющихся фрагментов в шаблонах
- ✅ Нужна лучшая организация кода шаблонов
- ✅ Хотите упростить поддержку

**Используйте Background Tasks, если:**
- ✅ Нужны простые фоновые задачи
- ✅ Не хотите настраивать Celery/RQ
- ✅ Задачи не требуют сложной оркестрации

**Используйте CSP, если:**
- ✅ Нужна дополнительная защита от XSS
- ✅ Хотите контролировать загружаемые ресурсы
- ✅ Работаете с пользовательским контентом

**Используйте Modern Email API, если:**
- ✅ Нужна лучшая поддержка Unicode
- ✅ Хотите более гибкую настройку email
- ✅ Работаете с HTML email

---

## Полезные ссылки

- [Официальный релиз Django 6.0](https://www.djangoproject.com/weblog/2025/dec/03/django-60-released/)
- [Release Notes](https://docs.djangoproject.com/en/6.0/releases/6.0/)
- [Migration Guide](https://docs.djangoproject.com/en/6.0/releases/6.0/#backwards-incompatible-changes)
- [Template Partials Documentation](https://docs.djangoproject.com/en/6.0/topics/templates/#partials)
- [Background Tasks Documentation](https://docs.djangoproject.com/en/6.0/topics/tasks/)

---

**Дата релиза:** 3 декабря 2025  
**Версия:** Django 6.0  
**Минимальная версия Python:** 3.12
