## Продолжение лекции MongoDB

**Слайды 18-19: Агрегация**

Агрегация - это мощнейший инструмент MongoDB для аналитики. Работает как конвейер - данные проходят через стадии и трансформируются.

### Простой пример

Задача: найти средний возраст студентов по курсам.

```python
pipeline = [
    # Стадия 1: Фильтрация (аналог WHERE)
    {"$match": {"age": {"$gte": 20}}},  # Только студенты 20+
    
    # Стадия 2: Группировка (аналог GROUP BY)
    {"$group": {
        "_id": "$course",  # Группируем по полю course
        "avg_age": {"$avg": "$age"},  # Средний возраст
        "count": {"$sum": 1}  # Количество студентов
    }},
    
    # Стадия 3: Сортировка (аналог ORDER BY)
    {"$sort": {"avg_age": -1}},  # -1 = по убыванию
    
    # Стадия 4: Ограничение (аналог LIMIT)
    {"$limit": 10}
]

results = await collection.aggregate(pipeline).to_list(None)
```

Это аналог SQL:
```sql
SELECT course, AVG(age) as avg_age, COUNT(*) as count
FROM students
WHERE age >= 20
GROUP BY course
ORDER BY avg_age DESC
LIMIT 10
```

### Основные стадии агрегации

**$match** - фильтрация документов
```python
{"$match": {"age": {"$gte": 20}}}  # Только возраст >= 20
```

**$group** - группировка
```python
{"$group": {
    "_id": "$city",  # Группируем по городу
    "total": {"$sum": "$amount"},  # Сумма
    "avg": {"$avg": "$amount"},  # Среднее
    "min": {"$min": "$amount"},  # Минимум
    "max": {"$max": "$amount"}  # Максимум
}}
```

**$sort** - сортировка
```python
{"$sort": {"age": 1}}  # 1 = по возрастанию, -1 = по убыванию
```

**$limit** и **$skip** - пагинация
```python
{"$skip": 20},  # Пропустить первые 20
{"$limit": 10}  # Взять 10
```

**$project** - выбор полей
```python
{"$project": {
    "name": 1,  # Включить поле name
    "age": 1,  # Включить поле age
    "_id": 0,  # Исключить _id
    "year": {"$year": "$birthDate"}  # Вычисляемое поле
}}
```

**$lookup** - JOIN с другой коллекцией
```python
{"$lookup": {
    "from": "courses",  # Из какой коллекции
    "localField": "courseId",  # Поле в текущей коллекции
    "foreignField": "_id",  # Поле в courses
    "as": "courseInfo"  # Имя нового поля (массив)
}}
```

**$unwind** - развернуть массив
```python
# До: {"name": "Иван", "courses": ["Math", "CS"]}
{"$unwind": "$courses"}
# После: 
# {"name": "Иван", "courses": "Math"}
# {"name": "Иван", "courses": "CS"}
```

**Слайд 20: Индексы**

Индексы - это то, что делает MongoDB быстрым. Без индексов MongoDB сканирует всю коллекцию (collection scan) - медленно.

### Простой индекс

```python
# Создать индекс по полю name
await collection.create_index("name")

# Теперь поиск по name будет быстрым
await collection.find_one({"name": "Иван"})  # Использует индекс
```

### Составной индекс

```python
# Индекс по двум полям
await collection.create_index([
    ("age", 1),  # 1 = по возрастанию
    ("name", -1)  # -1 = по убыванию
])

# Этот запрос использует индекс
await collection.find({"age": 20, "name": "Иван"})
```

### Уникальный индекс

```python
# Email должен быть уникальным
await collection.create_index("email", unique=True)

# Попытка вставить дубликат вызовет ошибку
await collection.insert_one({"email": "test@test.com"})  # OK
await collection.insert_one({"email": "test@test.com"})  # ERROR!
```

### Текстовый индекс

```python
# Для полнотекстового поиска
await collection.create_index([("description", "text")])

# Поиск по тексту
cursor = collection.find({"$text": {"$search": "python mongodb"}})
```

**Слайды 21-22: FastAPI + MongoDB**

Интеграция с FastAPI простая и понятная.

```python
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict

app = FastAPI()

# Подключение к MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.university_db

# Модель данных
class Student(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str | None = Field(default=None, alias="_id")
    name: str
    age: int
    courses: list[str] = []

# CREATE
@app.post("/students/")
async def create_student(student: Student):
    result = await db.students.insert_one(
        student.model_dump(by_alias=True, exclude=["id"])
    )
    student.id = str(result.inserted_id)
    return student

# READ
@app.get("/students/{student_id}")
async def get_student(student_id: str):
    from bson import ObjectId
    student = await db.students.find_one({"_id": ObjectId(student_id)})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student["_id"] = str(student["_id"])
    return student

# UPDATE
@app.put("/students/{student_id}")
async def update_student(student_id: str, student: Student):
    from bson import ObjectId
    result = await db.students.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": student.model_dump(exclude=["id"])}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Updated"}

# DELETE
@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    from bson import ObjectId
    result = await db.students.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Deleted"}
```

**Слайд 23: MongoDB - Плюсы и минусы**

Давайте честно - у MongoDB есть и плюсы, и минусы.

### Плюсы

✅ **Гибкая схема** - добавил поле и все, никаких миграций
✅ **Высокая производительность** - особенно для чтения
✅ **Горизонтальное масштабирование** - добавил сервер и все
✅ **Работа с JSON** - нативная поддержка, не нужно парсить
✅ **Богатый язык запросов** - агрегации, операторы, все есть

### Минусы

❌ **Нет JOIN** - есть $lookup, но он медленный
❌ **Больше памяти** - из-за дублирования данных
❌ **Нет транзакций** - до версии 4.0 (сейчас есть, но медленные)
❌ **Eventual consistency** - данные могут быть не синхронизированы
❌ **Сложность шардинга** - настроить непросто

---

## Часть 3: OpenSearch (35 минут)

**Слайд 24: OpenSearch**

OpenSearch - это поисковая система и аналитическая платформа. Основана на Apache Lucene.

Что умеет:
- **Полнотекстовый поиск** - с морфологией, опечатками, ранжированием
- **Аналитика в реальном времени** - агрегации за миллисекунды
- **RESTful API** - все через HTTP запросы
- **Горизонтальное масштабирование** - шарды и реплики

**Слайд 25: OpenSearch для РФ**

OpenSearch - это форк Elasticsearch 7.10.2. История такая:

1. Elasticsearch был open-source (Apache 2.0)
2. В 2021 Elastic изменила лицензию на SSPL (проприетарная)
3. AWS сделала форк Elasticsearch 7.10.2 → OpenSearch
4. OpenSearch остался Apache 2.0 (полностью open-source)

Почему это важно для России:
- Нет санкционных рисков
- Поддерживается AWS и сообществом
- Полная совместимость с Elasticsearch API
- Активное развитие

**Слайд 26: Установка OpenSearch**

Docker команда:

```bash
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0
```

Параметры:
- `-p 9200:9200` - REST API (HTTP)
- `-p 9600:9600` - Performance Analyzer
- `discovery.type=single-node` - одиночный узел (для dev)
- `DISABLE_SECURITY_PLUGIN=true` - отключить аутентификацию (только для dev!)

Проверка:
```bash
curl http://localhost:9200
```

**Слайд 27: Основные концепции**

Терминология OpenSearch vs MongoDB vs SQL:

| OpenSearch | MongoDB | SQL |
|------------|---------|-----|
| Index | Database | Database |
| Document | Document | Row |
| Field | Field | Column |
| Mapping | Schema | Schema |
| Shard | Shard | Partition |
| Replica | Replica | Replica |

**Shard** - это часть индекса. Данные распределяются по шардам.

**Replica** - это копия шарда. Для отказоустойчивости.

Пример: индекс с 3 шардами и 1 репликой = 6 шардов (3 primary + 3 replica).

**Слайд 28: Подключение Python**

```python
from opensearchpy import AsyncOpenSearch

client = AsyncOpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),  # Логин/пароль
    use_ssl=False,  # Без SSL для dev
    verify_certs=False  # Не проверять сертификаты
)
```

Для продакшена:
```python
client = AsyncOpenSearch(
    hosts=[{"host": "prod.example.com", "port": 9200}],
    http_auth=("admin", "strong_password"),
    use_ssl=True,  # Обязательно SSL!
    verify_certs=True  # Проверять сертификаты
)
```

**Слайд 29: Создание индекса**

Индекс нужно создать с маппингом - описанием типов полей.

```python
index_body = {
    "settings": {
        "number_of_shards": 1,  # Количество шардов
        "number_of_replicas": 0  # Реплики (0 для dev)
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},  # Полнотекстовый поиск
            "content": {"type": "text"},
            "author": {"type": "keyword"},  # Точное совпадение
            "created_at": {"type": "date"},
            "views": {"type": "integer"}
        }
    }
}

await client.indices.create(index="articles", body=index_body)
```

Типы полей:
- **text** - анализируется (токенизация, стемминг) для поиска
- **keyword** - хранится как есть, для фильтрации и сортировки
- **date** - дата/время
- **integer**, **long**, **float**, **double** - числа
- **boolean** - true/false

**Слайд 30: Индексация документов**

```python
doc = {
    "title": "Введение в NoSQL",
    "content": "NoSQL базы данных решают проблемы масштабирования...",
    "author": "Иван Иванов",
    "created_at": "2025-01-15",
    "views": 100
}

# Добавить документ с ID=1
await client.index(index="articles", id="1", body=doc)

# Массовая индексация (bulk) - в 10-100 раз быстрее!
from opensearchpy.helpers import async_bulk

actions = [
    {"_index": "articles", "_id": i, "_source": doc}
    for i in range(1000)
]
await async_bulk(client, actions)
```

Что происходит при индексации:
1. Текст разбивается на токены (слова)
2. Создаётся инвертированный индекс: слово → [doc1, doc2, ...]
3. Документ становится доступен для поиска (~1 сек задержка)

**Слайд 31: Поиск - Match Query**

Простейший полнотекстовый поиск:

```python
query = {
    "query": {
        "match": {
            "content": "NoSQL базы данных"
        }
    }
}

response = await client.search(index="articles", body=query)
hits = response["hits"]["hits"]  # Массив результатов
total = response["hits"]["total"]["value"]  # Всего найдено
```

`match` ищет по словам - найдет документы с любым из слов "NoSQL", "базы", "данных".

**Слайд 32: Поиск - Bool Query**

Сложные запросы с логикой:

```python
query = {
    "query": {
        "bool": {
            "must": [  # Обязательно (AND)
                {"match": {"content": "NoSQL"}}
            ],
            "filter": [  # Фильтры (не влияют на score)
                {"term": {"author": "Иван"}},
                {"range": {"views": {"gte": 50}}}
            ],
            "should": [  # Желательно (OR, +score)
                {"match": {"title": "MongoDB"}}
            ],
            "must_not": [  # Исключить (NOT)
                {"term": {"status": "draft"}}
            ]
        }
    }
}
```

Логика работы:
- **must** - документ ОБЯЗАН соответствовать, увеличивает score (релевантность)
- **filter** - документ ОБЯЗАН соответствовать, НЕ влияет на score (быстрее, кешируется)
- **should** - необязательно, но если совпадает - повышает score
- **must_not** - документ НЕ ДОЛЖЕН соответствовать

**Слайд 33: Fuzzy и Wildcard**

```python
# Нечёткий поиск (опечатки, до 2 символов)
{"query": {"fuzzy": {"title": {"value": "databse", "fuzziness": 2}}}}
# Найдет "database"

# Wildcard (* = любые символы, ? = один символ)
{"query": {"wildcard": {"title": "data*"}}}
# Найдет "database", "data", "datastore"

# Prefix (начинается с...)
{"query": {"prefix": {"title": "no"}}}
# Найдет "nosql", "node", "notebook"

# Regexp (регулярные выражения)
{"query": {"regexp": {"title": "no[a-z]+"}}}
# Найдет "nosql", "node", но не "no123"
```

⚠️ **wildcard/regexp медленные** - сканируют весь индекс. Комбинируйте с filter!

**Слайд 34: Агрегации**

Аналитика в реальном времени:

```python
query = {
    "size": 0,  # Не возвращать документы, только агрегации
    "aggs": {
        "authors": {  # Группировка по авторам
            "terms": {"field": "author"},  # TOP авторов
            "aggs": {  # Вложенная агрегация
                "avg_views": {"avg": {"field": "views"}}
            }
        },
        "views_stats": {"stats": {"field": "views"}}
    }
}

response = await client.search(index="articles", body=query)
aggs = response["aggregations"]
```

Получим:
- TOP-10 авторов с количеством статей
- Для каждого автора - средние просмотры
- Полную статистику по просмотрам (min, max, avg, sum, count)

**Слайд 35: Сортировка и пагинация**

```python
query = {
    "query": {"match_all": {}},
    "sort": [
        {"created_at": {"order": "desc"}},
        {"views": {"order": "desc"}}
    ],
    "from": 0,  # Offset
    "size": 10  # Limit
}
```

Пагинация:
- Страница 1: `from: 0, size: 10`
- Страница 2: `from: 10, size: 10`
- Страница 3: `from: 20, size: 10`

⚠️ При `from > 10000` производительность падает!

**Слайд 36: FastAPI + OpenSearch**

```python
@app.get("/search")
async def search_articles(
    q: str = Query(..., description="Поисковый запрос"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = {
        "query": {"match": {"content": q}},
        "from": (page - 1) * size,
        "size": size
    }
    response = await client.search(index="articles", body=query)
    return {
        "total": response["hits"]["total"]["value"],
        "results": response["hits"]["hits"]
    }
```

**Слайд 37: Анализаторы для русского**

Для качественного поиска на русском нужен анализатор:

```python
"analysis": {
    "analyzer": {
        "russian_analyzer": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["lowercase", "russian_stop", "russian_stemmer"]
        }
    }
}
```

Процесс анализа "Я бежал по улице":
1. **tokenizer**: ["Я", "бежал", "по", "улице"]
2. **lowercase**: ["я", "бежал", "по", "улице"]
3. **russian_stop**: ["бежал", "улице"] (удалены "я", "по")
4. **russian_stemmer**: ["беж", "улиц"] (корни слов)

Теперь "бежал", "бежит", "бегу" найдут одинаковые документы!

**Слайд 38-43: Итоги**

MongoDB vs OpenSearch - выбирайте по задаче:
- MongoDB - для хранения данных
- OpenSearch - для поиска и аналитики
- Часто используют вместе (гибридный подход)

Спасибо за внимание!
