В **Django 6** отправка писем делается через встроенный модуль **django.core.mail**. 
Ниже — практическое и актуальное руководство.

---

## 1️⃣ Базовая настройка почты (`settings.py`)

### Пример для SMTP (Gmail)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'app_password'  # НЕ обычный пароль!
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

🔐 **Важно для Gmail**:

* включи 2FA
* создай **App Password**
* обычный пароль не будет работать

---

## 2️⃣ Простая отправка письма

```python
from django.core.mail import send_mail

send_mail(
    subject='Привет!',
    message='Это тестовое письмо',
    from_email=None,  # возьмётся DEFAULT_FROM_EMAIL
    recipient_list=['user@example.com'],
    fail_silently=False,
)
```

---

## 3️⃣ HTML-письмо

```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='HTML письмо',
    body='<h1>Здравствуйте!</h1><p>Это HTML</p>',
    to=['user@example.com'],
)
email.content_subtype = 'html'
email.send()
```

---

## 4️⃣ Письмо из шаблона (рекомендуется)

### `templates/email/welcome.html`

```html
<h1>Добро пожаловать, {{ username }}!</h1>
```

### Отправка

```python
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

html = render_to_string('email/welcome.html', {
    'username': 'Alex'
})

email = EmailMessage(
    'Добро пожаловать',
    html,
    to=['user@example.com'],
)
email.content_subtype = 'html'
email.send()
```

---

## 5️⃣ Отправка с вложениями

```python
email = EmailMessage(
    'Документ',
    'См. вложение',
    to=['user@example.com'],
)

email.attach_file('files/report.pdf')
email.send()
```

---

## 6️⃣ Для разработки (чтобы письма не уходили)

### Вывод писем в консоль

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Или в файл

```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

---

## 7️⃣ Асинхронная отправка (лучше для продакшена)

Используют:

* **Celery**
* **django-q**
* **Huey**

Принцип:

```python
send_email.delay()
```

(могу показать пример с Celery, если нужно)

---

## 8️⃣ Частые ошибки

❌ `SMTPAuthenticationError` → неправильный пароль / нет App Password
❌ письма в спаме → нет SPF / DKIM / плохой from_email
❌ блокировка → слишком много писем подряд

---

Ниже — **готовые SMTP-настройки для Django** под самые популярные почтовые сервисы. Копируй нужный блок в `settings.py`.

---

## 📧 **Gmail**

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'APP_PASSWORD'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

⚠️ **Важно**:

* включи **2FA**
* создай **App Password**
* обычный пароль ❌ не работает

👉 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## 📧 **Yandex Mail**

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'your_email@yandex.ru'
EMAIL_HOST_PASSWORD = 'PASSWORD_OR_APP_PASSWORD'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

✅ Можно использовать:

* обычный пароль
* или **пароль приложения** (рекомендуется)

👉 [https://id.yandex.ru/security/app-passwords](https://id.yandex.ru/security/app-passwords)

---

## 📧 **Mail.ru**

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'your_email@mail.ru'
EMAIL_HOST_PASSWORD = 'PASSWORD'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

⚠️ Если включена 2FA — нужен **пароль приложения**

👉 [https://account.mail.ru/user/security](https://account.mail.ru/user/security)

---

## 🧪 Для разработки (чтобы письма не отправлялись)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## 🧠 Советы для продакшена

✔ Лучше использовать:

* отдельный email для отправки
* SPF / DKIM / DMARC
* сервисы типа SendGrid / Mailgun (если массово)

---

