# LAB-REDIS


## 📁 Структура проекта

```
LAB-REDIS/
├── docker-compose.yml
├── app/
│   ├── main.py
│   └── models.py
├── load_test.py        # или используем ab/locust
└── README.md
```



## 1️⃣ Шаг 1: Подготовка среды (Docker Compose)

**`docker-compose.yml`**
```yaml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: demo
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
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
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/demo
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
from .models import Counter, SessionLocal, engine, Base

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
```