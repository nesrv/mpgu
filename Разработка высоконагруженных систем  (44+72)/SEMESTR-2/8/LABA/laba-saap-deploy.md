# Практическое занятие
## Изучение CI/CD

## Часть 2 Continius Delivery/Deployment (CD)

## Цели

- Объяснить процесс деплоя приложения на Railway и настройку CI/CD через GitHub Actions.
- Показать, как перейти на PostgreSQL: docker-compose, изменения в приложении, обновление workflow (сервис Postgres, Init), настройка БД на Railway.
- Дать практические задания для закрепления: деплой на Railway, подключение БД, проверка CI после изменений.



## Структура проекта (корневая)

- `main.py` — основное FastAPI приложение
- `shop.json` — данные товаров
- `requirements.txt` — зависимости (fastapi, uvicorn, pydantic, pytest, httpx, black)
- `railway.json` — конфиг Railway (команда запуска, билдер)
- `test_main.py` — тесты (pytest)
- `.github/workflows/deploy.yml` — CI/CD: тесты + деплой на Railway (отдельного `ci.yml` нет)


## Деплой на Railway

Railway — платформа для деплоя приложений прямо с GitHub. Ниже — настройка с учётом вашего репозитория

### Шаг 0: Как Railway узнаёт, как запускать приложение

В проекте используется `railway.json` (а не Procfile): в корне файл с полем `deploy.startCommand`:

```json
"startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

`$PORT` — переменная окружения, которую Railway выделяет приложению.

### Шаг 1: Создать аккаунт на Railway

1. Перейдите на [railway.app](https://railway.app)
2. Нажмите `Start New Project`
3. Выберите `Deploy from GitHub Repo`
4. Авторизуйте GitHub (дайте Railway доступ к вашим репозиториям)

### Шаг 2: Выбрать репозиторий и ветку

1. Выберите свой репозиторий `name_repo`
2. Выберите ветку `main`
3. Railway автоматически обнаружит что это Python проект

### Шаг 3: Добавить requirements.txt (важно!)

Railway нужно знать, какие зависимости установить. В текущем проекте в корне уже есть `requirements.txt`, например:

```
fastapi==0.110.0
uvicorn==0.28.0
pydantic==2.8.0
pytest==7.4.4
httpx==0.25.2
black==24.10.0
```

### Шаг 4: Добавить переменные окружения (опционально)

На странице **сервиса приложения** в Railway:

- Нажмите `Variables`
- Добавьте переменные (если нужны, например для логирования)

### Шаг 5: Дождитесь деплоя

1. Railway автоматически запустит деплой
2. Включит ваше приложение на публичный URL
3. Вы увидите что-то вроде: `https://your-app-xxxx.railway.app`

### Проверка

После деплоя приложение будет доступно по URL:

```
https://your-app-xxxx.railway.app/health
```

А документация (Swagger UI):

```
https://your-app-xxxx.railway.app/docs
```

### Автоматический деплой

После первого деплоя: каждый пуш в `main` автоматически обновит приложение на Railway!

### Деплой через GitHub Actions (CI-CD-SIMPLE)

Отдельного `ci.yml` нет — используется единый `.github/workflows/deploy.yml`:

- **Job `test`:** checkout → Python 3.13 → `pip install -r requirements.txt` → при необходимости инициализация БД → `pytest -v test_main.py`.
- **Job `deploy`:** зависит от `test`, ставит Node.js → `npm install -g @railway/cli` → `railway up --service web` (или значение из `RAILWAY_SERVICE`).

Шаг деплоя:

```yaml
- name: Deploy to Railway
  run: |
    railway up --service ${{ secrets.RAILWAY_SERVICE || 'web' }}
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

**Секреты в GitHub (Settings → Secrets and variables → Actions):**

1. **RAILWAY_TOKEN** (обязательно) — токен с Railway: Settings → Tokens → Create Token.
2. **RAILWAY_SERVICE** (необязательно) — имя сервиса в проекте Railway. Если не задан, подставляется `web` (как при выборе сервиса в `railway link`).

**Важно:** аргумент `--service <SERVICE>` обязателен; без него — ошибка «a value is required for '--service'». **Проект** (project, например `luminous-curiosity`) и **сервис** (service, например `web`) в Railway — разные сущности; в `railway up` указывается имя сервиса.

---

## Часть 3 Подключение базы данных

> **Запуск CI после изменений (по необходимости):** после каждого изменения в проект — пуш в `main` или «Re-run all jobs» в GitHub Actions (вкладка Actions → выбранный workflow run). Так проверяется, что тесты и проверки проходят.

### 3.1 Скрипт для наполнения БД scripts\init_db.sql

```sql
-- Таблица видеокарт (совпадает с docker-compose + Railway Postgres)
CREATE TABLE IF NOT EXISTS video_cards (
    id          BIGSERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    price       NUMERIC(12,2) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL
);

-- Минимальные данные для тестов и локального запуска (дублируем shop.json)
TRUNCATE video_cards RESTART IDENTITY;
INSERT INTO video_cards (name, price, description, created_at) VALUES
  ('NVIDIA GeForce RTX 5090', 230000.00, 'Флагманская видеокарта 2026 года.', '2026-01-15 10:00:00+00'),
  ('NVIDIA GeForce RTX 4090', 165000.00, 'Мощная видеокарта для рейтрейсинга.', '2026-01-15 10:00:00+00'),
  ('NVIDIA GeForce RTX 5080', 130000.00, 'Высокая производительность для 4K.', '2026-01-15 10:00:00+00'),
  ('AMD Radeon RX 9070 XT', 95000.00, 'Лучшее соотношение цена/производительность.', '2026-01-15 10:00:00+00'),
  ('NVIDIA GeForce RTX 4080 Super', 115000.00, 'Мощная видеокарта для 4K с DLSS.', '2026-01-15 10:00:00+00')
;
```

## 3.2 Запустите postgres-17(18) в докере (или используйте предыдушую бд)

```sh
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: eshop
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/01_init.sql

volumes:
  pgdata:
```


## 3.3 Внесите изменения в main.py

```py
import psycopg
from psycopg.rows import dict_row

# Параметры подключения к PostgreSQL (из env или значения по умолчанию для docker-compose)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "app"),
    "password": os.getenv("DB_PASSWORD", "app"),
    "dbname": os.getenv("DB_NAME", "eshop"),
}


def get_db_connection():
    """Создаёт подключение к PostgreSQL (psycopg v3)."""
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)

@app.get("/products")
async def get_products():
    """Возвращает список видеокарт из таблицы video_cards."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, price, description, created_at FROM video_cards ORDER BY id")
            return [{**dict(r), "price": float(r["price"])} for r in cur.fetchall()]
    finally:
        conn.close()

```

## 3.4 Меняем процесс CI (.github\workflows\ci.yml)

При переходе на PostgreSQL в CI нужно:

1. **Сервис Postgres** — job должен поднимать контейнер с БД, чтобы тесты и smoke-тест подключались к реальной базе.
2. **Переменные окружения** — `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (совпадают с `docker-compose`).
3. **Зависимости** — устанавливать из `requirements.txt` (с `psycopg[binary]`).
4. **Шаг Init PostgreSQL** — после установки зависимостей выполнить `scripts/init_db.sql`, иначе таблица `video_cards` не будет создана, и тесты (например `/products`) упадут.

### 1. Добавляем сервис Postgres и переменные окружения в job

```yaml
 services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: app
          POSTGRES_PASSWORD: app
          POSTGRES_DB: eshop
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U app -d eshop"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5

    env:
      DB_HOST: 127.0.0.1
      DB_PORT: 5432
      DB_USER: app
      DB_PASSWORD: app
      DB_NAME: eshop

```

Шаг **Install dependencies** меняем на `pip install -r requirements.txt` (вместо перечисления пакетов).

### 2. Добавляем шаг Init PostgreSQL

Шаг ставим **после** установки зависимостей и **до** Black/tests. Он ждёт готовности Postgres, затем выполняет `scripts/init_db.sql` (создание таблицы и вставка тестовых данных).

**Упрощённый вариант** (через `psql` в контейнере; GHA runner имеет Docker):

```yaml
- name: Init PostgreSQL
  run: |
    docker run --rm --network host -e PGPASSWORD=app -v $PWD/scripts:/scripts postgres:17 \
      psql -h 127.0.0.1 -U app -d eshop -f /scripts/init_db.sql
```

**Полный вариант** (через Python и `psycopg`, с ожиданием готовности БД и обходом комментариев в SQL):

```yaml
- name: Init PostgreSQL
        run: |
          python -c "
          import psycopg
          import time
          for _ in range(10):
              try:
                  c = psycopg.connect(host='127.0.0.1', port=5432, user='app', password='app', dbname='eshop')
                  c.close()
                  break
              except Exception:
                  time.sleep(1)
          else:
              raise SystemExit('Postgres not ready')
          with open('scripts/init_db.sql') as f:
              sql = f.read()
          sql = '\n'.join(l for l in sql.split('\n') if not l.strip().startswith('--'))
          conn = psycopg.connect(host='127.0.0.1', port=5432, user='app', password='app', dbname='eshop')
          conn.autocommit = True
          for stmt in sql.split(';'):
              s = stmt.strip()
              if s:
                  conn.cursor().execute(s)
          conn.close()
          "
```

**Порядок шагов:** Checkout → Setup Python → Install dependencies (из `requirements.txt`) → **Init PostgreSQL** → Black check → Syntax check → Import app → Run tests → Uvicorn smoke test.

Без Init PostgreSQL тесты `test_products` и `test_health` завершатся ошибкой (таблица `video_cards` отсутствует или пуста).

---

## 3.5 Все эндпоинты в main.py замени на хранимые в бд sql(или pl/pgsql функции)

```py
# код main.py


```


```sql
-- хранимые функции postgresql


```


## 3.6 Job deploy — деплой на Railway

После успешного прохождения job `test` запускается job `deploy`. Он не поднимает Postgres — деплоит только приложение. БД на Railway должна быть настроена отдельно (плагин PostgreSQL + переменные `DB_*`).

**Содержимое job `deploy` в `.github/workflows/deploy.yml`:**

```yaml
deploy:
  name: Deploy to Railway
  needs: test
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install Railway CLI
      run: npm install -g @railway/cli

    - name: Deploy to Railway
      run: |
        railway up --service ${{ secrets.RAILWAY_SERVICE || 'web' }}
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

**Шаги:**
1. **Checkout** — клонирование репозитория.
2. **Setup Node.js** — Railway CLI устанавливается через npm, поэтому нужен Node.js.
3. **Install Railway CLI** — глобальная установка `@railway/cli`.
4. **Deploy to Railway** — `railway up` загружает код в Railway. Аргумент `--service` обязателен (по умолчанию `web`, если не задан секрет `RAILWAY_SERVICE`). Переменная `RAILWAY_TOKEN` берётся из GitHub Secrets.

**Секреты:** `RAILWAY_TOKEN` (обязательно), `RAILWAY_SERVICE` (опционально, по умолчанию `web`).

---

## 3.7 Настройка БД на Railway

Для работы `/products` приложению нужна PostgreSQL. На Railway БД настраивается отдельно от деплоя кода.

### Шаг 1: Добавить PostgreSQL в проект

1. Откройте проект в [railway.app](https://railway.app).
2. Нажмите **New** → **Database** → **PostgreSQL**.
3. Railway создаст сервис с БД. Дождитесь статуса готовности.

### Шаг 2: Связать БД с сервисом приложения

1. Откройте сервис **PostgreSQL**.
2. Вкладка **Variables** или **Connect** — там будут `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` (или аналогичные).
3. Откройте сервис приложения (**web**).
4. Вкладка **Variables** → **New Variable** (или **Add from Reference**, если Railway предлагает подставить переменные из Postgres).

Добавьте переменные вручную, если нужно:

| Переменная | Значение | Пример |
|------------|----------|--------|
| `DB_HOST` | хост из Postgres | `monolith.proxy.rlwy.net` |
| `DB_PORT` | порт | `12345` |
| `DB_USER` | пользователь | `postgres` |
| `DB_PASSWORD` | пароль | из Variables Postgres |
| `DB_NAME` | имя БД | `railway` |

Имена совпадают с `main.py` (читает `os.getenv("DB_HOST", ...)` и т.д.).

### Шаг 3: Создать таблицу и данные (один раз)

Таблица `video_cards` не создаётся автоматически. Выполните `scripts/init_db.sql` на прод-БД:

**Вариант A — через Railway Data/Query:**
- Откройте Postgres → вкладка **Data** или **Query**.
- Вставьте содержимое `scripts/init_db.sql` (CREATE TABLE, TRUNCATE, INSERT).
- Выполните запрос.

**Вариант B — через psql локально:**
```bash
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d <DB_NAME> -f scripts/init_db.sql
```
Подставьте значения из Variables Postgres. Пароль запросит интерактивно.

### Проверка

После деплоя откройте `https://your-app.railway.app/products`. Если видите JSON со списком видеокарт — БД настроена. Если **500** или **503** — проверьте переменные `DB_*` и наличие таблицы `video_cards`.



