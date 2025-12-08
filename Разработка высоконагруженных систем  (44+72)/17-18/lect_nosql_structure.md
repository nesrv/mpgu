
# Лекция NoSQL-СУБД: MongoDB и Elasticsearch/OpenSearch в Python (FastAPI)

### Блок 1: Введение в NoSQL (10 мин, слайды 1-5)

**Слайд 1: Титульный**
- Название: NoSQL-СУБД: MongoDB и Elasticsearch/OpenSearch
- Подзаголовок: Практическое применение в Python (FastAPI)


**Слайд 2: Проблемы реляционных БД**
- Вертикальное масштабирование (дорого)
- Жёсткая схема данных
- Сложность работы с иерархическими данными
- Низкая производительность при больших объёмах

**Слайд 3: Что такое NoSQL?**
- Not Only SQL
- Горизонтальное масштабирование
- Гибкая схема данных
- CAP-теорема (Consistency, Availability, Partition tolerance)

**Слайд 4: Типы NoSQL-СУБД**
- Document Store (MongoDB, Couchbase)
- Key-Value (Redis, Memcached)
- Column Family (Cassandra, HBase)
- Graph (Neo4j, ArangoDB)
- Search Engine (Elasticsearch, OpenSearch)

**Слайд 5: Когда использовать NoSQL?**
- Большие объёмы неструктурированных данных
- Высокая скорость записи/чтения
- Гибкая схема (частые изменения структуры)
- Полнотекстовый поиск
- Аналитика в реальном времени

---

### Блок 2: MongoDB (35 мин, слайды 6-21)

**Слайд 6: Что такое MongoDB?**
- Document-oriented NoSQL СУБД
- Хранение данных в формате BSON (Binary JSON)
- Гибкая схема
- Горизонтальное масштабирование (sharding)

**Слайд 7: Архитектура MongoDB**

```
┌─────────────────────────────────────────┐
│           Application Layer             │
│    (Python, Node.js, Java drivers)      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         MongoDB Server (mongod)         │
├─────────────────────────────────────────┤
│  Query Router (mongos) - для sharding  │
├─────────────────────────────────────────┤
│         Storage Engine Layer            │
│  ┌─────────────┐  ┌─────────────┐      │
│  │  WiredTiger │  │  In-Memory  │      │
│  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────┘
```

**Компоненты:**
- **mongod** — основной процесс сервера
- **mongos** — маршрутизатор запросов (при sharding)
- **WiredTiger** — движок хранения (по умолчанию)
- **Replica Set** — набор реплик для отказоустойчивости
- **Sharding** — горизонтальное разделение данных

**Слайд 8: Основные концепции**
- Database → Collection → Document
- Document = JSON-подобный объект
- _id — уникальный идентификатор
- Индексы для ускорения запросов

**Слайд 9: Системные базы данных MongoDB**

**admin** — административная БД
- Хранит пользователей и роли
- Команды для управления сервером
- Создание пользователей с правами на все БД

**config** — конфигурация sharding
- Метаданные о шардах
- Информация о распределении данных
- Используется только при sharding

**local** — локальные данные
- Не реплицируется между серверами
- Oplog (журнал операций для репликации)
- Временные данные

> ⚠️ Эти БД создаются автоматически и не должны удаляться

**Слайд 10: Установка MongoDB в РФ**
```bash
# Docker (рекомендуется)
docker run -d -p 27017:27017 --name mongodb mongo:7

# Альтернатива: Percona Server for MongoDB (совместимая замена)
docker run -d -p 27017:27017 percona/percona-server-mongodb:7.0
```

**Слайд 9: Подключение к MongoDB из Python**
```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["university_db"]
collection = db["students"]
```

**Слайд 10: CRUD операции - Create**
```python
# Вставка одного документа
student = {
    "name": "Иван Иванов",
    "age": 21,
    "courses": ["Математика", "Программирование"],
    "grades": {"Математика": 5, "Программирование": 4}
}
result = await collection.insert_one(student)

# Вставка нескольких
students = [{"name": "Мария"}, {"name": "Петр"}]
await collection.insert_many(students)
```

**Слайд 11: CRUD операции - Read**
```python
# Найти один документ
student = await collection.find_one({"name": "Иван Иванов"})

# Найти все с условием
cursor = collection.find({"age": {"$gte": 20}})
students = await cursor.to_list(length=100)

# Проекция (выбор полей)
cursor = collection.find({}, {"name": 1, "age": 1, "_id": 0})
```

**Слайд 12: CRUD операции - Update**
```python
# Обновить один документ
await collection.update_one(
    {"name": "Иван Иванов"},
    {"$set": {"age": 22}}
)

# Обновить несколько
await collection.update_many(
    {"age": {"$lt": 20}},
    {"$inc": {"age": 1}}
)

# Upsert (создать если не существует)
await collection.update_one(
    {"name": "Новый студент"},
    {"$set": {"age": 19}},
    upsert=True
)
```

**Слайд 13: CRUD операции - Delete**
```python
# Удалить один документ
await collection.delete_one({"name": "Иван Иванов"})

# Удалить несколько
await collection.delete_many({"age": {"$lt": 18}})
```

**Слайд 14: Операторы запросов**
```python
# Сравнение
{"age": {"$gt": 20}}  # больше
{"age": {"$gte": 20}} # больше или равно
{"age": {"$lt": 25}}  # меньше
{"age": {"$lte": 25}} # меньше или равно
{"age": {"$ne": 20}}  # не равно

# Логические
{"$and": [{"age": {"$gte": 20}}, {"age": {"$lte": 25}}]}
{"$or": [{"name": "Иван"}, {"name": "Петр"}]}
{"age": {"$in": [20, 21, 22]}}
{"age": {"$nin": [18, 19]}}
```

**Слайд 15: Работа с массивами**
```python
# Поиск в массиве
{"courses": "Математика"}
{"courses": {"$all": ["Математика", "Физика"]}}
{"courses": {"$size": 3}}

# Обновление массивов
{"$push": {"courses": "Новый курс"}}
{"$pull": {"courses": "Старый курс"}}
{"$addToSet": {"courses": "Уникальный курс"}}
```

**Слайд 16: Агрегация (Aggregation Pipeline) - Концепция**

**Что это:** Конвейер обработки данных — документы проходят через последовательность стадий

```python
pipeline = [
    # Стадия 1: Фильтрация (как WHERE в SQL)
    {"$match": {"age": {"$gte": 20}}},
    
    # Стадия 2: Группировка (как GROUP BY в SQL)
    {"$group": {
        "_id": "$course",              # группировать по полю course
        "avg_grade": {"$avg": "$grade"},  # средний балл
        "count": {"$sum": 1}              # количество студентов
    }},
    
    # Стадия 3: Сортировка (как ORDER BY в SQL)
    {"$sort": {"avg_grade": -1}},  # -1 = по убыванию
    
    # Стадия 4: Ограничение (как LIMIT в SQL)
    {"$limit": 10}
]
results = await collection.aggregate(pipeline).to_list(None)
```

**Аналогия с SQL:**
```sql
SELECT course, AVG(grade) as avg_grade, COUNT(*) as count
FROM students
WHERE age >= 20
GROUP BY course
ORDER BY avg_grade DESC
LIMIT 10
```

**Слайд 17: Агрегация - Основные стадии**

**Базовые стадии:**
- `$match` — фильтрация документов (WHERE)
- `$group` — группировка с агрегатными функциями
- `$sort` — сортировка (1 = asc, -1 = desc)
- `$limit` / `$skip` — пагинация
- `$project` — выбор и преобразование полей

**Продвинутые стадии:**
- `$lookup` — JOIN с другой коллекцией
- `$unwind` — разворачивание массивов
- `$addFields` — добавление вычисляемых полей
- `$facet` — множественные агрегации параллельно

**Агрегатные операторы:**
- `$sum`, `$avg`, `$min`, `$max` — математические
- `$first`, `$last` — первый/последний элемент
- `$push`, `$addToSet` — формирование массивов

**Слайд 18: Индексы**
```python
# Создание индекса
await collection.create_index("name")
await collection.create_index([("age", 1), ("name", -1)])

# Уникальный индекс
await collection.create_index("email", unique=True)

# Текстовый индекс
await collection.create_index([("description", "text")])

# Поиск по тексту
cursor = collection.find({"$text": {"$search": "python"}})
```

**Слайд 19: FastAPI + MongoDB - Модели**
```python
from pydantic import BaseModel, Field, ConfigDict

class Student(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str | None = Field(default=None, alias="_id")
    name: str
    age: int
    courses: list[str] = []
```

**Слайд 20: FastAPI + MongoDB - Эндпоинты**
```python
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.university_db

@app.post("/students/", response_model=Student)
async def create_student(student: Student):
    result = await db.students.insert_one(student.model_dump(by_alias=True))
    student.id = str(result.inserted_id)
    return student

@app.get("/students/{student_id}")
async def get_student(student_id: str):
    student = await db.students.find_one({"_id": student_id})
    if not student:
        raise HTTPException(status_code=404)
    return student
```

**Слайд 21: MongoDB - Плюсы и минусы**
**Плюсы:**
- Гибкая схема данных
- Высокая производительность чтения
- Горизонтальное масштабирование
- Богатый язык запросов

**Минусы:**
- Нет транзакций между документами (до версии 4.0)
- Больше потребление памяти
- Нет JOIN (нужна денормализация)

---

### Блок 3: Elasticsearch / OpenSearch (35 мин, слайды 22-36)

**Слайд 22: Что такое Elasticsearch?**
- Распределённая поисковая система
- Основана на Apache Lucene
- Полнотекстовый поиск
- Аналитика в реальном времени
- RESTful API

**Слайд 23: OpenSearch - альтернатива для РФ**
- Fork Elasticsearch 7.10.2 (Apache 2.0)
- Поддержка AWS
- Совместимость с Elasticsearch API
- Активное сообщество
- Рекомендуется для использования в РФ

**Слайд 24: Установка OpenSearch**
```bash
# Docker
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0

# Проверка
curl http://localhost:9200
```

**Слайд 25: Основные концепции**
- Index (индекс) ≈ Database
- Document (документ) ≈ Row
- Field (поле) ≈ Column
- Mapping (маппинг) ≈ Schema
- Shard (шард) — часть индекса
- Replica (реплика) — копия шарда

**Слайд 26: Подключение из Python**
```python
from opensearchpy import AsyncOpenSearch

client = AsyncOpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)
```

**Слайд 27: Создание индекса и маппинга**
```python
index_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "author": {"type": "keyword"},
            "created_at": {"type": "date"},
            "views": {"type": "integer"}
        }
    }
}

await client.indices.create(index="articles", body=index_body)
```

**Слайд 28: Индексация документов**
```python
# Индексация одного документа
doc = {
    "title": "Введение в NoSQL",
    "content": "NoSQL базы данных...",
    "author": "Иван Иванов",
    "created_at": "2025-01-15",
    "views": 100
}

await client.index(
    index="articles",
    id="1",
    body=doc
)

# Bulk индексация
from opensearchpy.helpers import async_bulk

actions = [
    {"_index": "articles", "_id": i, "_source": doc}
    for i, doc in enumerate(documents)
]
await async_bulk(client, actions)
```

**Слайд 29: Поиск - Match Query**
```python
# Полнотекстовый поиск
query = {
    "query": {
        "match": {
            "content": "NoSQL базы данных"
        }
    }
}

response = await client.search(index="articles", body=query)
hits = response["hits"]["hits"]
```

**Слайд 30: Поиск - Bool Query**
```python
query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"content": "NoSQL"}}
            ],
            "filter": [
                {"term": {"author": "Иван Иванов"}},
                {"range": {"views": {"gte": 50}}}
            ],
            "should": [
                {"match": {"title": "MongoDB"}}
            ],
            "must_not": [
                {"term": {"status": "draft"}}
            ]
        }
    }
}
```

**Слайд 31: Поиск - Fuzzy и Wildcard**
```python
# Нечёткий поиск (опечатки)
{"query": {"fuzzy": {"title": {"value": "databse", "fuzziness": 2}}}}

# Wildcard
{"query": {"wildcard": {"title": "data*"}}}

# Prefix
{"query": {"prefix": {"title": "no"}}}

# Regexp
{"query": {"regexp": {"title": "no[a-z]+"}}}
```

**Слайд 32: Агрегации**
```python
query = {
    "size": 0,
    "aggs": {
        "authors": {
            "terms": {"field": "author"},
            "aggs": {
                "avg_views": {"avg": {"field": "views"}}
            }
        },
        "views_stats": {
            "stats": {"field": "views"}
        },
        "views_histogram": {
            "histogram": {"field": "views", "interval": 100}
        }
    }
}

response = await client.search(index="articles", body=query)
```

**Слайд 33: Сортировка и пагинация**
```python
query = {
    "query": {"match_all": {}},
    "sort": [
        {"created_at": {"order": "desc"}},
        {"views": {"order": "desc"}}
    ],
    "from": 0,
    "size": 10
}

# Search After (для больших объёмов)
query = {
    "query": {"match_all": {}},
    "sort": [{"_id": "asc"}],
    "search_after": [last_id],
    "size": 10
}
```

**Слайд 34: FastAPI + OpenSearch**
```python
from fastapi import FastAPI, Query
from opensearchpy import AsyncOpenSearch

app = FastAPI()
client = AsyncOpenSearch([{"host": "localhost", "port": 9200}])

@app.get("/search")
async def search_articles(
    q: str = Query(..., description="Поисковый запрос"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = {
        "query": {"match": {"content": q}},
        "from": (page - 1) * size,
        "size": size,
        "highlight": {"fields": {"content": {}}}
    }
    
    response = await client.search(index="articles", body=query)
    
    return {
        "total": response["hits"]["total"]["value"],
        "results": [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"],
                "highlight": hit.get("highlight", {})
            }
            for hit in response["hits"]["hits"]
        ]
    }
```

**Слайд 35: Анализаторы (Analyzers)**
```python
# Создание кастомного анализатора для русского языка
index_body = {
    "settings": {
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                }
            },
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "russian_analyzer"
            }
        }
    }
}
```

**Слайд 36: OpenSearch - Плюсы и минусы**
**Плюсы:**
- Мощный полнотекстовый поиск
- Аналитика в реальном времени
- Горизонтальное масштабирование
- Богатые возможности агрегации

**Минусы:**
- Высокое потребление ресурсов
- Сложность настройки
- Не подходит для транзакционных операций
- Near real-time (не мгновенная индексация)

---

### Блок 4: Сравнение и выбор решения (8 мин, слайды 37-40)

**Слайд 37: MongoDB vs OpenSearch**

| Критерий | MongoDB | OpenSearch |
|----------|---------|------------|
| Назначение | Общего назначения | Поиск и аналитика |
| Схема | Гибкая | Требует маппинга |
| Поиск | Базовый | Полнотекстовый |
| Производительность записи | Высокая | Средняя |
| Производительность чтения | Высокая | Очень высокая (поиск) |
| Агрегации | Хорошие | Отличные |
| Транзакции | Есть (с 4.0) | Нет |

**Слайд 38: Когда использовать MongoDB?**
- Основное хранилище данных
- Гибкая схема данных
- Высокая скорость записи
- Иерархические данные
- Транзакции между документами

**Примеры:**
- Каталог товаров
- Профили пользователей
- Контент-менеджмент системы
- IoT данные

**Слайд 39: Когда использовать OpenSearch?**
- Полнотекстовый поиск
- Логирование и мониторинг
- Аналитика в реальном времени
- Поиск по большим объёмам текста

**Примеры:**
- Поиск по сайту
- Анализ логов (ELK stack)
- Мониторинг метрик
- Поиск по документам

**Слайд 40: Гибридный подход**
```
┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼────────┐
│MongoDB│  │OpenSearch│
└─────┘  └───────────┘
Primary     Search
Storage     Index
```

**Паттерн:**
1. Данные хранятся в MongoDB
2. При изменении → синхронизация в OpenSearch
3. Поиск → OpenSearch
4. Получение полных данных → MongoDB

---

### Блок 5: Заключение (2 мин, слайд 43)

**Слайд 43: Итоги и ресурсы**

**Ключевые выводы:**
- NoSQL решает проблемы масштабирования
- MongoDB — для гибкого хранения данных
- OpenSearch — для поиска и аналитики
- Выбор зависит от задачи

**Ресурсы для изучения:**
- MongoDB University (бесплатные курсы)
- OpenSearch Documentation
- Motor (async MongoDB driver)
- opensearch-py (Python client)

**Практика:**
- Лабораторная работа: создание API с MongoDB и OpenSearch
- Задание: реализовать поиск по каталогу товаров

**Вопросы?**

---

## Дополнительные материалы для преподавателя

### Демо-код для показа на лекции

**demo_mongodb.py:**
```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def demo():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.demo_db
    
    # Вставка
    await db.students.insert_one({"name": "Иван", "age": 21})
    
    # Поиск
    student = await db.students.find_one({"name": "Иван"})
    print(student)
    
    # Обновление
    await db.students.update_one(
        {"name": "Иван"},
        {"$set": {"age": 22}}
    )
    
    # Агрегация
    pipeline = [
        {"$group": {"_id": None, "avg_age": {"$avg": "$age"}}}
    ]
    async for result in db.students.aggregate(pipeline):
        print(result)

if __name__ == "__main__":
    asyncio.run(demo())
```

**demo_opensearch.py:**
```python
from opensearchpy import AsyncOpenSearch
import asyncio

async def demo():
    client = AsyncOpenSearch([{"host": "localhost", "port": 9200}])
    
    # Индексация
    await client.index(
        index="articles",
        id="1",
        body={"title": "NoSQL", "content": "Введение в NoSQL базы данных"}
    )
    
    # Поиск
    response = await client.search(
        index="articles",
        body={"query": {"match": {"content": "NoSQL"}}}
    )
    print(response["hits"]["hits"])
    
    await client.close()

asyncio.run(demo())
```

### Вопросы для проверки понимания

1. В чём основное отличие MongoDB от реляционных БД?
2. Что такое CAP-теорема и как она применима к NoSQL?
3. Когда стоит использовать OpenSearch вместо MongoDB?
4. Как реализовать полнотекстовый поиск в MongoDB?
5. Что такое sharding и зачем он нужен?
6. Объясните разницу между match и term запросами в OpenSearch
7. Как синхронизировать данные между MongoDB и OpenSearch?

### Практические задания

**Задание 1 (MongoDB):**
Создать API для управления библиотекой книг с полями: название, автор, год, жанры (массив), рейтинг. Реализовать CRUD операции и поиск по жанрам.

**Задание 2 (OpenSearch):**
Создать поисковую систему по статьям с поддержкой фильтров (автор, дата), сортировки и подсветки найденных фрагментов.

**Задание 3 (Гибридное):**
Реализовать каталог товаров: данные в MongoDB, поиск через OpenSearch с автоматической синхронизацией.
