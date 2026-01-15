> **«Почему PostgreSQL “хромает” под высокой конкурентной нагрузкой и как Redis помогает сохранить данные»**

---

## 🎯 Цель занятия
Показать на практике:
1. Как PostgreSQL **не справляется с большим числом одновременных запросов на запись**.
2. Как это приводит к **потере данных**, **таймаутам** или **зависанию**.
3. Как **Redis как буфер/очередь** решает проблему и обеспечивает надёжную обработку.

---

## 🧰 Технологии
- **FastAPI** — веб-сервер
- **PostgreSQL** — основная БД (в Docker)
- **Redis** — буфер/очередь (в Docker)
- **Docker + Docker Compose** — для развёртывания
- **Python-клиенты**: `asyncpg`, `aioredis`
- **ab (Apache Bench)** или **locust** — для генерации нагрузки

---

## 📁 Структура проекта

```
stress-demo/
├── docker-compose.yml
├── app/
│   ├── main.py
│   └── models.py
├── load_test.py        # или используем ab/locust
└── README.md
```

---

## 1️⃣ Шаг 1: Подготовка среды (Docker Compose)


```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ .

EXPOSE 8000

CMD ["python", "-c", "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"]

```



**`docker-compose.yml`**
```yaml
version: '3.8'
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: student_db
      POSTGRES_USER: student
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    command: >
      postgres -c max_connections=20

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgresql+asyncpg://student:password@db:5432/student_db
      REDIS_URL: redis://redis:6379
```



> ⚠️ Обратите внимание: `max_connections=20` — **намеренно уменьшено**, чтобы быстрее достичь лимита.

---

## 2️⃣ Шаг 2: FastAPI-приложение без Redis (уязвимая версия)

**`app/models.py`**
```python
from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@db:5432/demo"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Counter(Base):
    __tablename__ = "counter"
    id = Column(Integer, primary_key=True, default=1)
    value = Column(Integer, default=0)
```

**`app/main.py` (без Redis)**  
```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models import Counter, SessionLocal, engine, Base
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.post("/hit")
async def hit(db: AsyncSession = Depends(get_db)):
    counter = await db.get(Counter, 1)
    if not counter:
        counter = Counter(id=1, value=0)
        db.add(counter)
    counter.value += 1
    await db.commit()
    return {"count": counter.value}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

---

## 3️⃣ Шаг 3: Демонстрация проблемы PostgreSQL

### Запуск:
```bash
docker-compose up --build
docker-compose up --build -d
docker-compose up app --build
```

### Нагрузочный тест (в другом терминале):
```bash
# Создать файл с пустыми POST данными
echo '{}' > post_data.json

# Тест POST эндпоинта
ab -n 1000 -c 50 -p post_data.json -T "application/json" http://localhost:8000/hit

ab -n 10000 -c 500 -p post_data.json -T "application/json" http://localhost:8000/hit


```

### 🔴 Что увидят студенты:
- Множество ошибок **500** (connection timeout, too many connections)
- В логах FastAPI:  
  `asyncpg.exceptions.TooManyConnectionsError`
- В логах PostgreSQL:  
  `FATAL: remaining connection slots are reserved for non-replication superuser connections`
- **Итоговое значение в `counter.value` << 1000** → **данные потеряны!**

> 💡 Объяснение: каждое соединение — ресурс. При 50 параллельных запросах и `max_connections=20` — большинство запросов падают.

---

## 4️⃣ Шаг 4: Внедрение Redis как буфера

### Изменения в `app/main.py`:

```python
import aioredis
from fastapi import FastAPI
from .models import Counter, SessionLocal, engine, Base

app = FastAPI()
redis: aioredis.Redis

@app.on_event("startup")
async def startup():
    global redis
    redis = aioredis.from_url("redis://redis:6379", decode_responses=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/hit")
async def hit():
    # Быстро кладём в Redis — без ожидания БД
    await redis.incr("pending_hits")
    return {"status": "queued"}

@app.get("/process")
async def process(db: AsyncSession = Depends(get_db)):
    """Фоновая обработка (можно вызывать по расписанию или в фоне)"""
    pending = await redis.get("pending_hits")
    if not pending:
        return {"processed": 0}
    count = int(pending)
    counter = await db.get(Counter, 1)
    if not counter:
        counter = Counter(id=1, value=0)
        db.add(counter)
    counter.value += count
    await redis.delete("pending_hits")
    await db.commit()
    return {"processed": count}
```

> ⚠️ В реальном проекте обработка должна быть в **фоновой задаче** (Celery, APScheduler, или отдельный worker). Здесь — для простоты через GET.

---

## 5️⃣ Шаг 5: Повторный тест с Redis

### Нагрузка:
```bash
ab -n 1000 -c 100 http://localhost:8000/hit
```

### Результат:
- Все запросы возвращают **200 OK** мгновенно.
- Redis хранит `pending_hits = 1000`.
- Затем вызываем:
  ```bash
  curl http://localhost:8000/process
  ```
- В БД появляется **точно 1000** → **нет потерь!**

---

## 6️⃣ Шаг 6: Обсуждение

### Вопросы для студентов:
- Почему PostgreSQL не справился?
- Что такое **connection pool** и почему он ограничен?
- Почему Redis выдержал нагрузку? (однопоточный, in-memory, O(1) операции)
- Всегда ли нужен Redis? (нет — если нагрузка умеренная)
- Какие есть альтернативы? (Kafka, RabbitMQ, фоновые воркеры)

### Ключевые выводы:
| PostgreSQL | Redis |
|-----------|-------|
| Надёжное хранение | Быстрый буфер |
| Дорогие соединения | Лёгкие операции |
| ACID | Не ACID, но быстр |
| Не для высокой записи | Идеален для инкрементов, очередей |

---

