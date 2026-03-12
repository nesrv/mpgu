# Профилирование Django-проекта

---

# Часть 1. Django Silk

## Что такое Django Silk

Django Silk — инструмент для анализа производительности Django-приложений.
Он перехватывает каждый HTTP-запрос и записывает:

- **Время выполнения** запроса
- **SQL-запросы** — сколько их, сколько времени заняли, есть ли дубликаты
- **Профиль Python-кода** — какие функции сколько времени занимают
- **Тело запроса и ответа** — что пришло и что ушло

Silk отлично подходит для API (Django Ninja, DRF), в отличие от Django Debug Toolbar,
который работает только с HTML-страницами.

---

## 1. Установка

```bash
pip install django-silk
```

## 2. Подключение

### settings.py

```python
INSTALLED_APPS = [
    ...
    'silk',
]

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',   # первым в списке
    'django.middleware.security.SecurityMiddleware',
    ...
]

# Настройки Silk (в конце файла)
SILKY_PYTHON_PROFILER = True            # профилирование Python-кода
SILKY_PYTHON_PROFILER_BINARY = True     # бинарный формат (для визуализации)
SILKY_MAX_RECORDED_REQUESTS = 1000      # максимум записей в БД
SILKY_META = True                       # замерять overhead самого Silk
```

### urls.py

```python
from django.urls import path, include

urlpatterns = [
    ...
    path("silk/", include("silk.urls", namespace="silk")),
]
```

### Применить миграции

```bash
python manage.py migrate
```

Silk создаст свои таблицы в БД для хранения данных о запросах.

---

## 3. Использование

### Открыть панель Silk

Запустите сервер и откройте в браузере:

```
http://127.0.0.1:8000/silk/
```

### Что вы увидите

Панель Silk содержит несколько разделов:

#### Requests (Запросы)

Список всех HTTP-запросов к вашему приложению:

| Колонка | Что показывает |
|---------|---------------|
| Path | URL запроса (`/api/products`) |
| Time | Общее время выполнения (мс) |
| Num. Queries | Количество SQL-запросов |
| Time on queries | Время, потраченное на SQL |
| Method | GET, POST, PUT, DELETE |

**На что смотреть:**
- Запросы с большим **Num. Queries** — возможна N+1 проблема
- Запросы с большим **Time** — узкое место
- Если **Time on queries** ≈ **Time** — тормозит БД, не Python

#### SQL (SQL-запросы)

Для каждого запроса можно увидеть:
- Текст каждого SQL-запроса
- Время выполнения
- **Дубликаты** — одинаковые запросы, выполненные несколько раз

#### Profiling (Профилирование)

Граф вызовов Python-функций — какая функция сколько времени заняла.
Помогает найти медленный код, не связанный с БД.

---

## 4. Практика: анализ API

### Шаг 1 — Сделать запросы

Откройте в браузере или через curl:

```bash
curl http://127.0.0.1:8000/api/products
curl http://127.0.0.1:8000/api/products/1
curl http://127.0.0.1:8000/api/health
```

### Шаг 2 — Открыть Silk

Перейдите на `http://127.0.0.1:8000/silk/`

### Шаг 3 — Сравнить запросы

Посмотрите на три запроса:

| Endpoint | Ожидание |
|----------|----------|
| `/api/products` | 1 SQL-запрос (`SELECT * FROM video_cards`) |
| `/api/products/1` | 1 SQL-запрос (`SELECT ... WHERE id=1`) |
| `/api/health` | 0 SQL-запросов |

Если у `/api/products` больше 1 SQL-запроса — это **проблема** (N+1).

---

## 5. Типичные проблемы, которые находит Silk

### N+1 проблема

**Что это:** вместо одного запроса на все объекты, Django делает 1 + N запросов
(1 для списка + по 1 на каждый связанный объект).

**Как выглядит в Silk:**
```
GET /api/orders — 51 queries, 120ms

SELECT * FROM orders                          -- 1 запрос
SELECT * FROM video_cards WHERE id = 1        -- N запросов
SELECT * FROM video_cards WHERE id = 2
SELECT * FROM video_cards WHERE id = 3
... (ещё 47 таких же)
```

**Как исправить:**
```python
# Плохо — N+1:
orders = Order.objects.all()

# Хорошо — 2 запроса:
orders = Order.objects.select_related('product').all()

# Для ManyToMany:
orders = Order.objects.prefetch_related('items').all()
```

### Дублирующиеся запросы

**Как выглядит в Silk:**
```
GET /api/products — 5 queries (3 duplicates)
```

Silk подсвечивает одинаковые запросы. Это значит, что один и тот же `SELECT`
выполняется несколько раз — нужно закэшировать результат или пересмотреть логику.

---

## 6. Полезные настройки

```python
# Записывать только запросы длиннее 100мс
SILKY_INTERCEPT_PERCENT = 100       # процент запросов для записи (100 = все)

# Не записывать тела запросов/ответов (экономит место в БД)
SILKY_MAX_REQUEST_BODY_SIZE = 0
SILKY_MAX_RESPONSE_BODY_SIZE = 0

# Очистка старых записей
SILKY_MAX_RECORDED_REQUESTS = 1000  # хранить максимум 1000 записей

# Включить только для DEBUG
SILKY_AUTHENTICATION = True         # требовать авторизацию
SILKY_AUTHORISATION = True          # только для staff-пользователей
```

---

## 7. Очистка данных Silk

Silk хранит данные в БД. Чтобы очистить:

```bash
python manage.py silk_clear_request_log
```

---

## 8. Отключение для продакшена

Silk добавляет overhead (~5-10мс на запрос). На продакшене его лучше отключить.

Способ 1 — убрать middleware в `settings.py`:
```python
MIDDLEWARE = [
    # 'silk.middleware.SilkyMiddleware',  # закомментировать
    ...
]
```

Способ 2 — через переменную окружения:
```python
if DEBUG:
    INSTALLED_APPS += ['silk']
    MIDDLEWARE.insert(0, 'silk.middleware.SilkyMiddleware')
    SILKY_PYTHON_PROFILER = True
```

---

## Шпаргалка

| Действие | Команда / URL |
|----------|--------------|
| Установить | `pip install django-silk` |
| Панель | `http://127.0.0.1:8000/silk/` |
| Миграции | `python manage.py migrate` |
| Очистить логи | `python manage.py silk_clear_request_log` |
| Найти N+1 | Silk → Requests → кликнуть запрос → SQL tab |
| Профилирование | Silk → Requests → кликнуть запрос → Profiling tab |

---

# Часть 2. Django Debug Toolbar

## Что такое Django Debug Toolbar

Панель отладки, которая встраивается прямо в HTML-страницу.
Показывает подробную информацию о запросе: SQL, шаблоны, кэш, сигналы, настройки.

**Важно:** Debug Toolbar работает только с HTML-ответами (нужен тег `</body>`).
Для JSON API (Django Ninja, DRF) он **не отображается** — для этого используйте Silk.

---

## 1. Установка

```bash
pip install django-debug-toolbar
```

## 2. Подключение

### settings.py

```python
INSTALLED_APPS = [
    ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # как можно раньше
    'django.middleware.security.SecurityMiddleware',
    ...
]

# Для кого показывать панель (только localhost)
INTERNAL_IPS = ['127.0.0.1']
```

### urls.py

```python
from django.conf import settings
from django.urls import path, include

urlpatterns = [
    ...
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
```

---

## 3. Использование

Откройте любую HTML-страницу проекта в браузере:

```
http://127.0.0.1:8000/
```

Справа появится **боковая панель** с разделами.

### Разделы панели

| Раздел | Что показывает |
|--------|---------------|
| **SQL** | Все SQL-запросы: текст, время, EXPLAIN, дубликаты |
| **Time** | Общее время: CPU, user, total |
| **Templates** | Какие шаблоны использовались, контекст |
| **Cache** | Обращения к кэшу (hit/miss) |
| **Signals** | Django-сигналы и их обработчики |
| **Settings** | Все настройки Django |
| **Headers** | HTTP-заголовки запроса и ответа |
| **Request** | Данные запроса: GET, POST, cookies, session |
| **Static files** | Загруженные статические файлы |

### На что обращать внимание

1. **SQL** — главный раздел. Смотрите:
   - Количество запросов (больше 10 — повод задуматься)
   - Дубликаты (Similar/Duplicate) — одинаковые запросы
   - Время каждого запроса
   - Кнопка **Explain** — показывает план выполнения запроса

2. **Time** — если SQL быстрый, а страница медленная — проблема в Python-коде или шаблонах

3. **Templates** — какие шаблоны рендерятся и с каким контекстом

---

## 4. Практика

### Шаг 1 — Откройте главную страницу

```
http://127.0.0.1:8000/
```

### Шаг 2 — Раскройте раздел SQL

Кликните на **SQL** в правой панели. Вы увидите:

```
2 queries in 1.5ms

SELECT ⋯ FROM "video_cards"               0.8ms
SELECT ⋯ FROM "django_session" WHERE ⋯    0.3ms
```

### Шаг 3 — Нажмите Explain

Для любого запроса нажмите **Explain** — увидите план выполнения PostgreSQL:

```
Seq Scan on video_cards  (cost=0.00..1.05 rows=5 width=...)
```

`Seq Scan` на 5 записей — нормально. Если увидите `Seq Scan` на тысячах строк — нужен индекс.

---

## 5. Когда НЕ работает

| Ситуация | Причина | Решение |
|----------|---------|---------|
| Панель не появляется | Ответ не HTML (JSON API) | Используйте Silk |
| Панель не появляется | IP не в `INTERNAL_IPS` | Добавьте свой IP |
| Панель не появляется | `DEBUG = False` | Включите DEBUG |
| Панель не появляется | Нет тега `</body>` | Добавьте в шаблон |

---

## 6. Отключение для продакшена

Debug Toolbar **автоматически** отключается при `DEBUG = False`.
Дополнительно можно подключать только в DEBUG:

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']
```

---

# Silk vs Debug Toolbar — когда что использовать

| Критерий | Django Silk | Django Debug Toolbar |
|----------|-------------|---------------------|
| **JSON API** | Да | Нет |
| **HTML-страницы** | Да | Да |
| **История запросов** | Да (в БД) | Нет (только текущий) |
| **SQL-анализ** | Да + дубликаты | Да + EXPLAIN |
| **Профилирование Python** | Да (cProfile) | Нет |
| **Шаблоны и контекст** | Нет | Да |
| **Кэш** | Нет | Да |
| **Overhead** | ~5-10мс | ~2-5мс |
| **Нужна БД** | Да (миграции) | Нет |

**Рекомендация:** используйте оба — Silk для API, Debug Toolbar для HTML-страниц.
