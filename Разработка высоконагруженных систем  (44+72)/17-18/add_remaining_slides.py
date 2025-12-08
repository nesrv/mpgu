with open('lect-nosql.html', 'r', encoding='utf-8') as f:
    content = f.read()

remaining_slides = '''
<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 14: CRUD - Update</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">await collection.update_one(
    {"name": "Иван"},
    {"$set": {"age": 22}}
)

await collection.update_many(
    {"age": {"$lt": 20}},
    {"$inc": {"age": 1}}
)</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 15: CRUD - Delete</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">await collection.delete_one({"name": "Иван"})

await collection.delete_many({"age": {"$lt": 18}})</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 16: Операторы запросов</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">{"age": {"$gt": 20}}   # больше
{"age": {"$gte": 20}}  # больше или равно
{"age": {"$lt": 25}}   # меньше
{"age": {"$ne": 20}}   # не равно

{"$and": [{"age": {"$gte": 20}}, {"age": {"$lte": 25}}]}
{"$or": [{"name": "Иван"}, {"name": "Петр"}]}
{"age": {"$in": [20, 21, 22]}}</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 17: Работа с массивами</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Поиск
{"courses": "Математика"}
{"courses": {"$all": ["Математика", "Физика"]}}

# Обновление
{"$push": {"courses": "Новый курс"}}
{"$pull": {"courses": "Старый курс"}}
{"$addToSet": {"courses": "Уникальный"}}</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 18: Агрегация - Концепция</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">pipeline = [
    {"$match": {"age": {"$gte": 20}}},
    {"$group": {
        "_id": "$course",
        "avg_grade": {"$avg": "$grade"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_grade": -1}},
    {"$limit": 10}
]
results = await collection.aggregate(pipeline).to_list(None)</code></pre><p style="margin-top:10px;font-size:.9em">SQL: <code>SELECT course, AVG(grade), COUNT(*) FROM students WHERE age >= 20 GROUP BY course ORDER BY avg_grade DESC LIMIT 10</code></p></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 19: Агрегация - Стадии</h2><div style="text-align:left;font-size:.7em"><p><strong>Базовые:</strong> $match, $group, $sort, $limit, $project</p><p style="margin-top:10px"><strong>Продвинутые:</strong> $lookup (JOIN), $unwind, $addFields, $facet</p><p style="margin-top:10px"><strong>Операторы:</strong> $sum, $avg, $min, $max, $first, $last, $push</p></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 20: Индексы</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">await collection.create_index("name")
await collection.create_index([("age", 1), ("name", -1)])

await collection.create_index("email", unique=True)

await collection.create_index([("description", "text")])
cursor = collection.find({"$text": {"$search": "python"}})</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 21: FastAPI + MongoDB - Модели</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">from pydantic import BaseModel, Field, ConfigDict

class Student(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str | None = Field(default=None, alias="_id")
    name: str
    age: int
    courses: list[str] = []</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 22: FastAPI + MongoDB - Эндпоинты</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.university_db

@app.post("/students/")
async def create_student(student: Student):
    result = await db.students.insert_one(student.model_dump(by_alias=True))
    student.id = str(result.inserted_id)
    return student</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 23: MongoDB - Плюсы и минусы</h2><div style="font-size:.7em"><div style="text-align:left"><h3 style="color:#2ecc71">Плюсы:</h3><ul style="margin-left:40px"><li>✅ Гибкая схема</li><li>✅ Высокая производительность</li><li>✅ Горизонтальное масштабирование</li></ul></div><div style="text-align:left;margin-top:15px"><h3 style="color:#e74c3c">Минусы:</h3><ul style="margin-left:40px"><li>❌ Нет JOIN</li><li>❌ Больше памяти</li><li>❌ Нет транзакций (до 4.0)</li></ul></div></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 24: OpenSearch</h2><div style="text-align:left;font-size:.7em"><p style="margin-left:20px"><strong>Распределённая поисковая система</strong></p><ul style="margin-left:40px"><li class="fragment">🔍 Полнотекстовый поиск</li><li class="fragment">📊 Аналитика в реальном времени</li><li class="fragment">🌐 RESTful API</li><li class="fragment">⚡ Основана на Apache Lucene</li></ul></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 25: OpenSearch для РФ</h2><div style="text-align:left;font-size:.7em"><p style="margin-left:20px">Fork Elasticsearch 7.10.2 (Apache 2.0)</p><ul style="margin-left:40px"><li class="fragment">✅ Поддержка AWS</li><li class="fragment">✅ Совместимость с Elasticsearch API</li><li class="fragment">✅ Активное сообщество</li><li class="fragment">✅ Рекомендуется для РФ</li></ul></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 26: Установка OpenSearch</h2><div style="text-align:left;font-size:.7em"><pre><code class="bash">docker run -d -p 9200:9200 -p 9600:9600 \\
  -e "discovery.type=single-node" \\
  -e "DISABLE_SECURITY_PLUGIN=true" \\
  opensearchproject/opensearch:2.11.0

curl http://localhost:9200</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 27: Основные концепции</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">Index (индекс) ≈ Database</li><li class="fragment">Document (документ) ≈ Row</li><li class="fragment">Field (поле) ≈ Column</li><li class="fragment">Mapping (маппинг) ≈ Schema</li><li class="fragment">Shard (шард) — часть индекса</li><li class="fragment">Replica (реплика) — копия шарда</li></ul></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 28: Подключение Python</h2><div style="text-align:left;font-size:.7em"><pre><code class="python">from opensearchpy import AsyncOpenSearch

client = AsyncOpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 29: Создание индекса</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">index_body = {
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
await client.indices.create(index="articles", body=index_body)</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 30: Индексация документов</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">doc = {
    "title": "Введение в NoSQL",
    "content": "NoSQL базы данных...",
    "author": "Иван Иванов",
    "created_at": "2025-01-15",
    "views": 100
}

await client.index(index="articles", id="1", body=doc)</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 31: Поиск - Match Query</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">query = {
    "query": {
        "match": {
            "content": "NoSQL базы данных"
        }
    }
}

response = await client.search(index="articles", body=query)
hits = response["hits"]["hits"]</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 32: Поиск - Bool Query</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">query = {
    "query": {
        "bool": {
            "must": [{"match": {"content": "NoSQL"}}],
            "filter": [
                {"term": {"author": "Иван"}},
                {"range": {"views": {"gte": 50}}}
            ],
            "should": [{"match": {"title": "MongoDB"}}],
            "must_not": [{"term": {"status": "draft"}}]
        }
    }
}</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 33: Поиск - Fuzzy и Wildcard</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Нечёткий поиск (опечатки)
{"query": {"fuzzy": {"title": {"value": "databse", "fuzziness": 2}}}}

# Wildcard
{"query": {"wildcard": {"title": "data*"}}}

# Prefix
{"query": {"prefix": {"title": "no"}}}

# Regexp
{"query": {"regexp": {"title": "no[a-z]+"}}}</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 34: Агрегации</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">query = {
    "size": 0,
    "aggs": {
        "authors": {
            "terms": {"field": "author"},
            "aggs": {
                "avg_views": {"avg": {"field": "views"}}
            }
        },
        "views_stats": {"stats": {"field": "views"}}
    }
}
response = await client.search(index="articles", body=query)</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 35: Сортировка и пагинация</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">query = {
    "query": {"match_all": {}},
    "sort": [
        {"created_at": {"order": "desc"}},
        {"views": {"order": "desc"}}
    ],
    "from": 0,
    "size": 10
}</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 36: FastAPI + OpenSearch</h2><div style="text-align:left;font-size:.6em"><pre><code class="python">from fastapi import FastAPI, Query
from opensearchpy import AsyncOpenSearch

app = FastAPI()
client = AsyncOpenSearch([{"host": "localhost", "port": 9200}])

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
    return {"total": response["hits"]["total"]["value"], "results": response["hits"]["hits"]}</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 37: Анализаторы для русского</h2><div style="text-align:left;font-size:.55em"><pre><code class="python">index_body = {
    "settings": {
        "analysis": {
            "analyzer": {
                "russian_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "russian_stop", "russian_stemmer"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "content": {"type": "text", "analyzer": "russian_analyzer"}
        }
    }
}</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 38: OpenSearch - Плюсы и минусы</h2><div style="font-size:.7em"><div style="text-align:left"><h3 style="color:#2ecc71">Плюсы:</h3><ul style="margin-left:40px"><li>✅ Мощный полнотекстовый поиск</li><li>✅ Аналитика в реальном времени</li><li>✅ Богатые агрегации</li></ul></div><div style="text-align:left;margin-top:15px"><h3 style="color:#e74c3c">Минусы:</h3><ul style="margin-left:40px"><li>❌ Высокое потребление ресурсов</li><li>❌ Сложность настройки</li><li>❌ Near real-time (не мгновенно)</li></ul></div></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 39: MongoDB vs OpenSearch</h2><div style="font-size:.65em"><table style="width:100%;border-collapse:collapse"><tr style="background:rgba(52,152,219,0.3)"><th style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Критерий</th><th style="padding:8px;border:2px solid rgba(255,255,255,0.3)">MongoDB</th><th style="padding:8px;border:2px solid rgba(255,255,255,0.3)">OpenSearch</th></tr><tr><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Назначение</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Общего назначения</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Поиск и аналитика</td></tr><tr><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Схема</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Гибкая</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Требует маппинга</td></tr><tr><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Поиск</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Базовый</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Полнотекстовый</td></tr><tr><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Транзакции</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Есть (с 4.0)</td><td style="padding:8px;border:2px solid rgba(255,255,255,0.3)">Нет</td></tr></table></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 40: Когда использовать MongoDB?</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">📦 Основное хранилище данных</li><li class="fragment">🔄 Гибкая схема данных</li><li class="fragment">⚡ Высокая скорость записи</li><li class="fragment">🌳 Иерархические данные</li></ul><p class="fragment" style="margin-top:15px;color:#3498db"><strong>Примеры:</strong> Каталог товаров, Профили пользователей, CMS, IoT</p></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 41: Когда использовать OpenSearch?</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">🔍 Полнотекстовый поиск</li><li class="fragment">📝 Логирование и мониторинг</li><li class="fragment">📊 Аналитика в реальном времени</li><li class="fragment">📄 Поиск по документам</li></ul><p class="fragment" style="margin-top:15px;color:#3498db"><strong>Примеры:</strong> Поиск по сайту, ELK stack, Мониторинг метрик</p></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 42: Гибридный подход</h2><div style="font-size:.7em"><pre style="margin-top:10px"><code>┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
┌──▼──┐  ┌──▼────────┐
│MongoDB│  │OpenSearch│
└─────┘  └───────────┘
Primary     Search
Storage     Index</code></pre><p style="margin-top:15px;text-align:left"><strong>Паттерн:</strong></p><ol style="margin-left:40px;font-size:.9em"><li>Данные в MongoDB</li><li>При изменении → синхронизация в OpenSearch</li><li>Поиск → OpenSearch</li><li>Полные данные → MongoDB</li></ol></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 43: Итоги</h2><div style="text-align:left;font-size:.7em"><div class="fragment"><h3 style="color:#3498db">Ключевые выводы:</h3><ul style="margin-left:40px"><li>NoSQL решает проблемы масштабирования</li><li>MongoDB — для гибкого хранения</li><li>OpenSearch — для поиска и аналитики</li><li>Выбор зависит от задачи</li></ul></div><div class="fragment" style="margin-top:15px"><h3 style="color:#2ecc71">Ресурсы:</h3><ul style="margin-left:40px"><li>MongoDB University</li><li>OpenSearch Documentation</li><li>Motor, opensearch-py</li></ul></div></div></section>
'''

closing = '</div></div><script src="../15-16/js/reveal.min.js"></script>'
content = content.replace(closing, remaining_slides + '\n' + closing)

with open('lect-nosql.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("All 43 slides completed!")
