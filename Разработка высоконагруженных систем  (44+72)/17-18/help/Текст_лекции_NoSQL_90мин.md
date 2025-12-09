# Текст лекции: NoSQL - MongoDB и OpenSearch (90 минут)

## Введение (5 минут)

Добрый день! Сегодня мы поговорим о NoSQL базах данных, а конкретно о MongoDB и OpenSearch. Это две совершенно разные системы, но обе относятся к NoSQL и решают разные задачи в высоконагруженных системах.

**Слайд 1: Титульный**

Тема нашей лекции: NoSQL-СУБД - MongoDB и OpenSearch. Мы рассмотрим, когда и зачем их использовать, как с ними работать через Python и FastAPI.

---

## Часть 1: Введение в NoSQL (10 минут)

**Слайд 2: Проблемы реляционных БД**

Давайте начнем с того, почему вообще появились NoSQL базы данных. Реляционные СУБД типа PostgreSQL или MySQL отлично работают, но у них есть ограничения:

1. **Вертикальное масштабирование** - когда данных становится много, приходится покупать более мощный сервер. Это дорого и имеет физический предел.

2. **Жёсткая схема** - нужно заранее определить все таблицы и колонки. Если структура данных часто меняется, это становится проблемой.

3. **Иерархические данные** - JSON, вложенные объекты, массивы - всё это неудобно хранить в таблицах. Приходится делать множество JOIN'ов.

4. **Производительность** - при миллионах записей и сложных JOIN'ах скорость падает.

**Слайд 3: Что такое NoSQL?**

NoSQL расшифровывается как "Not Only SQL" - не только SQL. Это целый класс баз данных, которые решают проблемы реляционных СУБД:

- **Горизонтальное масштабирование** - можно добавлять обычные серверы, распределяя данные между ними
- **Гибкая схема** - можно хранить документы с разной структурой в одной коллекции
- **CAP-теорема** - это компромисс между консистентностью, доступностью и устойчивостью к разделению. NoSQL базы выбирают 2 из 3.

**Слайд 4: Типы NoSQL-СУБД**

NoSQL - это не одна технология, а целое семейство:

1. **Document Store** (MongoDB, Couchbase) - хранят JSON-подобные документы
2. **Key-Value** (Redis, Memcached) - простейшая структура, ключ-значение
3. **Column Family** (Cassandra, HBase) - данные хранятся по колонкам, а не по строкам
4. **Graph** (Neo4j) - для связанных данных, социальных графов
5. **Search Engine** (Elasticsearch, OpenSearch) - для полнотекстового поиска

Сегодня мы подробно разберем Document Store (MongoDB) и Search Engine (OpenSearch).

**Слайд 5: Когда использовать NoSQL?**

NoSQL подходит когда:
- Большие объёмы неструктурированных данных (логи, JSON API)
- Нужна высокая скорость записи (миллионы событий в секунду)
- Схема данных часто меняется (стартапы, прототипы)
- Нужен полнотекстовый поиск
- Аналитика в реальном времени

---

## Часть 2: MongoDB (35 минут)

**Слайд 6: MongoDB**

MongoDB - это document-oriented NoSQL СУБД. Что это значит?

- Данные хранятся в формате BSON (Binary JSON) - это JSON с дополнительными типами
- Гибкая схема - каждый документ может иметь свою структуру
- Горизонтальное масштабирование через sharding - данные автоматически распределяются по серверам

**Слайд 7: Архитектура MongoDB**

Посмотрите на архитектуру. Сверху - ваше приложение на Python, Node.js или Java. Оно подключается к MongoDB Server (процесс mongod). 

Если у вас кластер с шардингом, между приложением и серверами стоит Query Router (mongos) - он определяет, на какой сервер отправить запрос.

Внизу - Storage Engine. По умолчанию используется WiredTiger - он сжимает данные и поддерживает транзакции. Есть также In-Memory движок для максимальной скорости.

**Слайд 8: Основные концепции**

В MongoDB иерархия такая:
- **Database** (база данных) - аналог БД в PostgreSQL
- **Collection** (коллекция) - аналог таблицы
- **Document** (документ) - аналог строки, но это JSON-объект

Каждый документ имеет поле `_id` - уникальный идентификатор. Если вы его не укажете, MongoDB создаст автоматически (ObjectId).

Индексы работают так же, как в реляционных БД - ускоряют поиск.

**Слайд 9: Системные БД**

MongoDB создает 3 системные базы данных автоматически:

1. **admin** - пользователи, роли, административные команды
2. **config** - метаданные о шардах (только если включен sharding)
3. **local** - не реплицируется между серверами, хранит oplog и временные данные

Эти базы нельзя удалять!

**Слайд 10: Установка MongoDB**

Для разработки проще всего использовать Docker:

```bash
docker run -d -p 27017:27017 mongo:7
```

Для России есть альтернатива - Percona Server for MongoDB (полностью совместимый форк):

```bash
docker run -d -p 27017:27017 percona/percona-server-mongodb:7.0
```

**Слайд 11: Подключение Python**

Для работы с MongoDB из Python используем асинхронный драйвер Motor:

```python
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["university_db"]  # Выбираем БД
collection = db["students"]  # Выбираем коллекцию
```

Motor построен поверх PyMongo и работает с asyncio.

**Слайды 12-15: CRUD операции**

Теперь разберем основные операции. Это важно понять на практике.

**CREATE** - создание документов:
```python
student = {
    "name": "Иван Иванов",
    "age": 21,
    "courses": ["Математика", "Программирование"]
}
result = await collection.insert_one(student)
```

Обратите внимание - мы просто передаем Python словарь. Никаких схем заранее определять не нужно.

**READ** - чтение:
```python
# Один документ
student = await collection.find_one({"name": "Иван"})

# Много документов с условием
cursor = collection.find({"age": {"$gte": 20}})
students = await cursor.to_list(length=100)
```

`$gte` - это оператор "больше или равно". Таких операторов много.

**UPDATE** - обновление:
```python
await collection.update_one(
    {"name": "Иван"},  # Фильтр - что обновляем
    {"$set": {"age": 22}}  # $set - установить значение
)
```

`$set` - оператор обновления. Есть также `$inc` (увеличить), `$push` (добавить в массив) и другие.

**DELETE** - удаление:
```python
await collection.delete_one({"name": "Иван"})
await collection.delete_many({"age": {"$lt": 18}})
```

**Слайд 16: Операторы запросов**

MongoDB имеет богатый язык запросов:

- `$gt`, `$gte`, `$lt`, `$lte` - сравнения
- `$ne` - не равно
- `$and`, `$or` - логические операторы
- `$in` - значение в списке

Пример: найти студентов от 20 до 25 лет:
```python
{"$and": [{"age": {"$gte": 20}}, {"age": {"$lte": 25}}]}
```

**Слайд 17: Работа с массивами**

MongoDB отлично работает с массивами:

```python
# Найти студентов, изучающих математику
{"courses": "Математика"}

# Найти тех, кто изучает И математику, И физику
{"courses": {"$all": ["Математика", "Физика"]}}

# Добавить курс
{"$push": {"courses": "Новый курс"}}

# Удалить курс
{"$pull": {"courses": "Старый курс"}}
```

**Слайды 18-19: Агрегация**

Агрегация - это мощный инструмент для аналитики. Работает как конвейер (pipeline) - данные проходят через стадии:

```python
pipeline = [
    {"$match": {"age": {"$gte": 20}}},  # Фильтрация (WHERE)
    {"$group": {  # Группировка (GROUP BY)
        "_id": "$course",
        "avg_grade": {"$avg": "$grade"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_grade": -1}},  # Сортировка
    {"$limit": 10}  # Ограничение
]
```

Это аналог SQL:
```sql
SELECT course, AVG(grade), COUNT(*) 
FROM students 
WHERE age >= 20 
GROUP BY course 
ORDER BY avg_grade DESC 
LIMIT 10
```

Основные стадии:
- `$match` - фильтрация (WHERE)
- `$group` - группировка (GROUP BY)
- `$sort` - сортировка (ORDER BY)
- `$limit` - ограничение (LIMIT)
- `$project` - выбор полей (SELECT)
- `$lookup` - объединение коллекций (JOIN)

**Слайд 20: Индексы**

Индексы ускоряют поиск:

```python
# Простой индекс
await collection.create_index("name")

# Составной индекс
await collection.create_index([("age", 1), ("name", -1)])

# Уникальный индекс
await collection.create_index("email", unique=True)

# Текстовый индекс для полнотекстового поиска
await collection.create_index([("description", "text")])
```

**Слайды 21-22: FastAPI + MongoDB**

Интеграция с FastAPI простая:

```python
from pydantic import BaseModel, Field

class Student(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    name: str
    age: int
    courses: list[str] = []

@app.post("/students/")
async def create_student(student: Student):
    result = await db.students.insert_one(student.model_dump(by_alias=True))
    student.id = str(result.inserted_id)
    return student
```

**Слайд 23: MongoDB - Плюсы и минусы**

Плюсы:
- Гибкая схема - можно менять структуру на лету
- Высокая производительность для чтения/записи
- Горизонтальное масштабирование

Минусы:
- Нет JOIN (есть $lookup, но медленный)
- Больше потребление памяти из-за дублирования данных
- Нет транзакций (до версии 4.0, сейчас есть)

---

## Часть 3: OpenSearch (35 минут)

**Слайд 24: OpenSearch**

OpenSearch - это распределённая поисковая система и аналитическая платформа. Основные возможности:

- Полнотекстовый поиск с поддержкой морфологии
- Аналитика в реальном времени
- RESTful API
- Основана на Apache Lucene

**Слайд 25: OpenSearch для РФ**

OpenSearch - это форк Elasticsearch 7.10.2 с лицензией Apache 2.0. Почему это важно для России?

- Поддерживается AWS и сообществом
- Полная совместимость с Elasticsearch API
- Активное развитие
- Рекомендуется для использования в РФ (нет санкционных рисков)

**Слайд 26: Установка OpenSearch**

Docker команда:

```bash
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0
```

Параметры:
- `9200` - REST API
- `9600` - Performance Analyzer
- `single-node` - одиночный узел (для разработки)
- `DISABLE_SECURITY_PLUGIN` - отключаем аутентификацию (только для dev!)

**Слайд 27: Основные концепции**

Терминология OpenSearch:
- **Index** (индекс) ≈ Database в MongoDB
- **Document** (документ) ≈ Row в SQL
- **Field** (поле) ≈ Column
- **Mapping** (маппинг) ≈ Schema
- **Shard** (шард) - часть индекса для распределения данных
- **Replica** (реплика) - копия шарда для отказоустойчивости

**Слайд 28: Подключение Python**

```python
from opensearchpy import AsyncOpenSearch

client = AsyncOpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)
```

Для продакшена обязательно включайте SSL!

**Слайд 29: Создание индекса**

Индекс нужно создать с маппингом - описанием типов полей:

```python
index_body = {
    "settings": {
        "number_of_shards": 1,  # Количество шардов
        "number_of_replicas": 0  # Реплики
    },
    "mappings": {
        "properties": {
            "title": {"type": "text"},  # Полнотекстовый поиск
            "author": {"type": "keyword"},  # Точное совпадение
            "created_at": {"type": "date"},
            "views": {"type": "integer"}
        }
    }
}
```

Типы полей:
- `text` - анализируется для поиска (токенизация, стемминг)
- `keyword` - хранится как есть, для фильтрации
- `date`, `integer`, `float` - числовые типы

**Слайд 30: Индексация документов**

```python
doc = {
    "title": "Введение в NoSQL",
    "content": "NoSQL базы данных...",
    "author": "Иван Иванов",
    "created_at": "2025-01-15",
    "views": 100
}

# Добавить документ
await client.index(index="articles", id="1", body=doc)

# Массовая индексация (bulk) - в 10-100 раз быстрее
from opensearchpy.helpers import async_bulk
actions = [{"_index": "articles", "_id": i, "_source": doc} for i in range(100)]
await async_bulk(client, actions)
```

Что происходит при индексации:
1. Документ разбивается на токены (слова)
2. Создаётся инвертированный индекс: слово → список документов
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
hits = response["hits"]["hits"]
```

`match` ищет по словам - найдет документы с любым из слов.

**Слайд 32: Поиск - Bool Query**

Сложные запросы с логикой:

```python
query = {
    "query": {
        "bool": {
            "must": [{"match": {"content": "NoSQL"}}],  # Обязательно (AND)
            "filter": [  # Фильтры (не влияют на score)
                {"term": {"author": "Иван"}},
                {"range": {"views": {"gte": 50}}}
            ],
            "should": [{"match": {"title": "MongoDB"}}],  # Желательно (OR)
            "must_not": [{"term": {"status": "draft"}}]  # Исключить (NOT)
        }
    }
}
```

Логика:
- `must` - документ ОБЯЗАН соответствовать, увеличивает score
- `filter` - ОБЯЗАН соответствовать, НЕ влияет на score (быстрее)
- `should` - необязательно, но повышает score
- `must_not` - НЕ ДОЛЖЕН соответствовать

**Слайд 33: Fuzzy и Wildcard**

Нечёткий поиск и шаблоны:

```python
# Нечёткий поиск (опечатки)
{"query": {"fuzzy": {"title": {"value": "databse", "fuzziness": 2}}}}

# Wildcard (* = любые символы)
{"query": {"wildcard": {"title": "data*"}}}

# Prefix (автодополнение)
{"query": {"prefix": {"title": "no"}}}
```

Когда использовать:
- `fuzzy` - поиск с опечатками
- `wildcard` - поиск по шаблону
- `prefix` - автодополнение

⚠️ wildcard/regexp медленные - комбинируйте с filter!

**Слайд 34: Агрегации**

Аналитика в реальном времени:

```python
query = {
    "size": 0,  # Не возвращать документы
    "aggs": {
        "authors": {
            "terms": {"field": "author"},  # TOP авторов
            "aggs": {
                "avg_views": {"avg": {"field": "views"}}
            }
        },
        "views_stats": {"stats": {"field": "views"}}
    }
}
```

Получим:
- TOP авторов с количеством статей
- Для каждого автора - средние просмотры
- Полную статистику по просмотрам (min, max, avg, sum)

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

⚠️ При `from > 10000` производительность падает!

**Слайд 36: FastAPI + OpenSearch**

```python
@app.get("/search")
async def search_articles(
    q: str = Query(...),
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

Процесс: "Я бежал по улице" → ["беж", "улиц"]

Теперь "бежал", "бежит", "бегу" найдут одинаковые документы!

**Слайд 38: OpenSearch - Плюсы и минусы**

Плюсы:
- Мощный полнотекстовый поиск
- Аналитика в реальном времени
- Богатые агрегации
- Горизонтальное масштабирование

Минусы:
- Высокое потребление ресурсов (RAM, CPU)
- Сложность настройки
- Near real-time (~1 сек задержка)
- Не подходит для транзакций

---

## Часть 4: Сравнение и выводы (5 минут)

**Слайд 39: MongoDB vs OpenSearch**

Сравнительная таблица показывает ключевые различия:

- **Назначение**: MongoDB - общего назначения, OpenSearch - поиск
- **Схема**: MongoDB - гибкая, OpenSearch - требует маппинга
- **Поиск**: MongoDB - базовый, OpenSearch - полнотекстовый
- **Транзакции**: MongoDB - есть, OpenSearch - нет
- **Ресурсы**: MongoDB - умеренные, OpenSearch - высокие

**Слайд 40-41: Когда использовать?**

MongoDB:
- Основное хранилище данных
- Гибкая схема
- Высокая скорость записи
- Примеры: каталог товаров, профили пользователей, CMS

OpenSearch:
- Полнотекстовый поиск
- Логирование и мониторинг
- Аналитика в реальном времени
- Примеры: поиск по сайту, ELK stack

**Слайд 42: Гибридный подход**

На практике часто используют обе системы:

1. Основные данные хранятся в MongoDB
2. При изменении данные синхронизируются в OpenSearch
3. Поиск выполняется через OpenSearch
4. Полные данные загружаются из MongoDB

Это даёт лучшее из обоих миров!

**Слайд 43: Итоги**

Ключевые выводы:
- NoSQL решает проблемы масштабирования реляционных БД
- MongoDB - для гибкого хранения документов
- OpenSearch - для поиска и аналитики
- Выбор зависит от конкретной задачи
- Часто используют гибридный подход

Ресурсы для изучения:
- MongoDB University (бесплатные курсы)
- OpenSearch Documentation
- Библиотеки: motor, opensearch-py

Спасибо за внимание! Вопросы?
