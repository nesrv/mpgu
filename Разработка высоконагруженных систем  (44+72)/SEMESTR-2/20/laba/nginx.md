# Настройка Nginx для django.h1n.ru

Nginx уже установлен на VPS и работает на порту 80.
Django-приложение запущено в Docker на порту 8080.
Нужно настроить проксирование: `django.h1n.ru` → `localhost:8080`.

---

## 1. Подключиться к VPS

```bash
ssh ssh alekseeva@81.90.182.174@81.90.182.174
```

---

## 2. Создать конфиг Nginx

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

## 3. Включить конфиг

Создать символическую ссылку в `sites-enabled` (нужен `sudo`):

```bash
sudo ln -s /etc/nginx/sites-available/django.h1n.ru /etc/nginx/sites-enabled/
```

---

## 4. Проверить конфигурацию

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

## 5. Перезагрузить Nginx

```bash
sudo systemctl reload nginx
```

---

## 6. Настроить DNS

В панели управления доменом `h1n.ru` добавить **A-запись**:

| Тип | Имя | Значение |
|-----|-----|----------|
| A | django | 81.90.182.174 |

DNS обновляется от 5 минут до 24 часов.

---

## 7. Проверить

```bash
curl http://django.h1n.ru/api/health
# {"status": "ok"}
```

Или открыть в браузере: `http://django.h1n.ru`

---

## 8. Добавить HTTPS (Let's Encrypt)

### Установить Certbot:

```bash
apt install certbot python3-certbot-nginx -y
```

### Получить сертификат:

```bash
certbot --nginx -d django.h1n.ru
```

Certbot автоматически:
- Получит SSL-сертификат
- Изменит конфиг Nginx (добавит `listen 443 ssl`)
- Настроит редирект с HTTP на HTTPS
- Добавит автообновление сертификата (раз в 90 дней)

### Проверить автообновление:

```bash
certbot renew --dry-run
```

### Результат:

Сайт будет доступен по `https://django.h1n.ru`

---

## 9. Обновить ALLOWED_HOSTS

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

## Полезные команды

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

## Итоговая схема

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
