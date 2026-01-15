# Параллельные вычисления в FastAPI

## GIL (Global Interpreter Lock)

**GIL** - механизм CPython, позволяющий только одному потоку выполнять код одновременно.

![1761908839258](image/parallel_computing/1761908839258.png)

- **CPU-задачи** (вычисления) → потоки НЕ помогают
- **I/O-задачи** (сеть, БД) → потоки работают

## Три подхода

### 1. Async/await (для I/O: сеть, БД)

```py
from fastapi import FastAPI
import httpx, asyncio

app = FastAPI()

@app.get("/fetch")
async def fetch():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get("https://api1.com"),
            client.get("https://api2.com")
        )
    return {"data": [r.json() for r in results]}
```

### 2. ProcessPoolExecutor (для CPU: вычисления)

```py
from concurrent.futures import ProcessPoolExecutor
import asyncio

executor = ProcessPoolExecutor(max_workers=4)

def compute(n):
    return sum(i * i for i in range(n))

@app.get("/compute/{n}")
async def calc(n: int):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, compute, n)
    return {"result": result}
```

### 3. BackgroundTasks (фоновые задачи)

```py
from fastapi import BackgroundTasks

def log_action(msg: str):
    with open("log.txt", "a") as f:
        f.write(msg)

@app.post("/action")
async def action(bg: BackgroundTasks):
    bg.add_task(log_action, "Action done")
    return {"status": "ok"}  # Ответ сразу
```

## Сравнение времени выполнения

```py
# Последовательно: T1 + T2 + T3
@app.get("/seq")
def seq():
    r1 = task1()
    r2 = task2()
    r3 = task3()
    return [r1, r2, r3]

# Конкурентно: max(T1, T2, T3)
@app.get("/async")
async def async_tasks():
    return await asyncio.gather(task1(), task2(), task3())

# Параллельно: max(T1, T2, T3) / ядра
@app.get("/parallel")
async def parallel():
    loop = asyncio.get_event_loop()
    return await asyncio.gather(
        loop.run_in_executor(pool, cpu_task1),
        loop.run_in_executor(pool, cpu_task2)
    )
```

## Что использовать?

| Задача | Решение |
|--------|--------|
| Сеть, БД | `async/await` |
| Вычисления | `ProcessPoolExecutor` |
| Фон | `BackgroundTasks` |
| Долгие задачи | `Celery + Redis` |

## Комбинированный пример

```py
from fastapi import FastAPI, BackgroundTasks
from concurrent.futures import ProcessPoolExecutor
import asyncio, httpx

app = FastAPI()
pool = ProcessPoolExecutor(max_workers=4)

def process_image(data):
    return {"processed": True}

async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        return (await client.get(url)).json()

def save_db(data):
    pass  # Сохранение

@app.post("/process")
async def process(bg: BackgroundTasks):
    # 1. Async: получаем данные
    data = await fetch_data("https://api.com/data")
    
    # 2. Process: обрабатываем
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(pool, process_image, data)
    
    # 3. Background: сохраняем
    bg.add_task(save_db, result)
    
    return {"status": "ok"}
```

## Celery для долгих задач

```py
from celery import Celery

celery = Celery('tasks', broker='redis://localhost')

@celery.task
def long_task(data):
    # 60 секунд работы
    return {"done": True}

@app.post("/start")
async def start(data: dict):
    task = long_task.delay(data)
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def status(task_id: str):
    task = celery.AsyncResult(task_id)
    return {"status": task.status, "result": task.result}
```

## Выводы

- **GIL** блокирует только CPU-задачи в потоках
- **async/await** → для I/O (сеть, БД)
- **ProcessPoolExecutor** → для CPU (вычисления)
- **BackgroundTasks** → для простых фоновых задач
- **Celery** → для распределенных задач
