with open('lect-nosql.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # Slide 11
    ('from motor.motor_asyncio import AsyncIOMotorClient\r\n\r\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\r\ndb = client["university_db"]\r\ncollection = db["students"]',
     '# Асинхронный драйвер для MongoDB\r\nfrom motor.motor_asyncio import AsyncIOMotorClient\r\n\r\n# Подключение к MongoDB\r\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\r\ndb = client["university_db"]  # Выбор БД\r\ncollection = db["students"]  # Выбор коллекции'),
    
    # Slide 12
    ('student = {\r\n    "name": "Иван Иванов",\r\n    "age": 21,\r\n    "courses": ["Математика", "Программирование"]\r\n}\r\nresult = await collection.insert_one(student)\r\n\r\nstudents = [{"name": "Мария"}, {"name": "Петр"}]\r\nawait collection.insert_many(students)',
     '# Создаем документ (JSON-объект)\r\nstudent = {\r\n    "name": "Иван Иванов",\r\n    "age": 21,\r\n    "courses": ["Математика", "Программирование"]\r\n}\r\n# Вставка одного документа\r\nresult = await collection.insert_one(student)\r\n\r\n# Вставка нескольких документов\r\nstudents = [{"name": "Мария"}, {"name": "Петр"}]\r\nawait collection.insert_many(students)'),
    
    # Slide 14
    ('await collection.update_one(\r\n    {"name": "Иван"},\r\n    {"$set": {"age": 22}}\r\n)\r\n\r\nawait collection.update_many(\r\n    {"age": {"$lt": 20}},\r\n    {"$inc": {"age": 1}}\r\n)',
     '# Обновить один документ\r\nawait collection.update_one(\r\n    {"name": "Иван"},  # Фильтр\r\n    {"$set": {"age": 22}}  # $set - установить значение\r\n)\r\n\r\n# Обновить несколько документов\r\nawait collection.update_many(\r\n    {"age": {"$lt": 20}},  # Возраст меньше 20\r\n    {"$inc": {"age": 1}}  # $inc - увеличить на 1\r\n)'),
    
    # Slide 15
    ('await collection.delete_one({"name": "Иван"})\r\n\r\nawait collection.delete_many({"age": {"$lt": 18}})',
     '# Удалить один документ\r\nawait collection.delete_one({"name": "Иван"})\r\n\r\n# Удалить несколько документов\r\nawait collection.delete_many({"age": {"$lt": 18}})'),
    
    # Slide 18
    ('pipeline = [\r\n    {"$match": {"age": {"$gte": 20}}},\r\n    {"$group": {\r\n        "_id": "$course",\r\n        "avg_grade": {"$avg": "$grade"},\r\n        "count": {"$sum": 1}\r\n    }},\r\n    {"$sort": {"avg_grade": -1}},\r\n    {"$limit": 10}\r\n]\r\nresults = await collection.aggregate(pipeline).to_list(None)',
     'pipeline = [\r\n    # Стадия 1: Фильтрация (WHERE)\r\n    {"$match": {"age": {"$gte": 20}}},\r\n    # Стадия 2: Группировка (GROUP BY)\r\n    {"$group": {\r\n        "_id": "$course",  # Группировать по курсу\r\n        "avg_grade": {"$avg": "$grade"},  # Средний балл\r\n        "count": {"$sum": 1}  # Подсчет\r\n    }},\r\n    # Стадия 3: Сортировка (ORDER BY)\r\n    {"$sort": {"avg_grade": -1}},  # -1 = по убыванию\r\n    # Стадия 4: Ограничение (LIMIT)\r\n    {"$limit": 10}\r\n]\r\nresults = await collection.aggregate(pipeline).to_list(None)'),
    
    # Slide 20
    ('await collection.create_index("name")\r\nawait collection.create_index([("age", 1), ("name", -1)])\r\n\r\nawait collection.create_index("email", unique=True)\r\n\r\nawait collection.create_index([("description", "text")])\r\ncursor = collection.find({"$text": {"$search": "python"}})',
     '# Простой индекс по одному полю\r\nawait collection.create_index("name")\r\n# Составной индекс (1 = asc, -1 = desc)\r\nawait collection.create_index([("age", 1), ("name", -1)])\r\n\r\n# Уникальный индекс\r\nawait collection.create_index("email", unique=True)\r\n\r\n# Текстовый индекс для полнотекстового поиска\r\nawait collection.create_index([("description", "text")])\r\ncursor = collection.find({"$text": {"$search": "python"}})'),
    
    # Slide 21
    ('from pydantic import BaseModel, Field, ConfigDict\r\n\r\nclass Student(BaseModel):\r\n    model_config = ConfigDict(populate_by_name=True)\r\n    \r\n    id: str | None = Field(default=None, alias="_id")\r\n    name: str\r\n    age: int\r\n    courses: list[str] = []',
     'from pydantic import BaseModel, Field, ConfigDict\r\n\r\nclass Student(BaseModel):\r\n    # Конфигурация для работы с MongoDB\r\n    model_config = ConfigDict(populate_by_name=True)\r\n    \r\n    id: str | None = Field(default=None, alias="_id")  # MongoDB _id\r\n    name: str\r\n    age: int\r\n    courses: list[str] = []  # Python 3.10+ синтаксис'),
    
    # Slide 22
    ('from fastapi import FastAPI, HTTPException\r\nfrom motor.motor_asyncio import AsyncIOMotorClient\r\n\r\napp = FastAPI()\r\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\r\ndb = client.university_db\r\n\r\n@app.post("/students/")\r\nasync def create_student(student: Student):\r\n    result = await db.students.insert_one(student.model_dump(by_alias=True))\r\n    student.id = str(result.inserted_id)\r\n    return student',
     'from fastapi import FastAPI, HTTPException\r\nfrom motor.motor_asyncio import AsyncIOMotorClient\r\n\r\napp = FastAPI()\r\n# Подключение к MongoDB\r\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\r\ndb = client.university_db\r\n\r\n@app.post("/students/")\r\nasync def create_student(student: Student):\r\n    # Конвертируем Pydantic модель в dict с alias (_id)\r\n    result = await db.students.insert_one(student.model_dump(by_alias=True))\r\n    student.id = str(result.inserted_id)  # Возвращаем ID\r\n    return student'),
    
    # Slide 28
    ('from opensearchpy import AsyncOpenSearch\r\n\r\nclient = AsyncOpenSearch(\r\n    hosts=[{"host": "localhost", "port": 9200}],\r\n    http_auth=("admin", "admin"),\r\n    use_ssl=False,\r\n    verify_certs=False\r\n)',
     '# Асинхронный клиент для OpenSearch\r\nfrom opensearchpy import AsyncOpenSearch\r\n\r\nclient = AsyncOpenSearch(\r\n    hosts=[{"host": "localhost", "port": 9200}],\r\n    http_auth=("admin", "admin"),  # Логин/пароль\r\n    use_ssl=False,  # Без SSL для разработки\r\n    verify_certs=False\r\n)'),
    
    # Slide 29
    ('index_body = {\r\n    "settings": {\r\n        "number_of_shards": 1,\r\n        "number_of_replicas": 0\r\n    },\r\n    "mappings": {\r\n        "properties": {\r\n            "title": {"type": "text"},\r\n            "content": {"type": "text"},\r\n            "author": {"type": "keyword"},\r\n            "created_at": {"type": "date"},\r\n            "views": {"type": "integer"}\r\n        }\r\n    }\r\n}\r\nawait client.indices.create(index="articles", body=index_body)',
     'index_body = {\r\n    "settings": {\r\n        "number_of_shards": 1,  # Количество шардов\r\n        "number_of_replicas": 0  # Без реплик\r\n    },\r\n    "mappings": {  # Схема данных\r\n        "properties": {\r\n            "title": {"type": "text"},  # Полнотекстовый поиск\r\n            "content": {"type": "text"},\r\n            "author": {"type": "keyword"},  # Точное совпадение\r\n            "created_at": {"type": "date"},\r\n            "views": {"type": "integer"}\r\n        }\r\n    }\r\n}\r\nawait client.indices.create(index="articles", body=index_body)'),
    
    # Slide 30
    ('doc = {\r\n    "title": "Введение в NoSQL",\r\n    "content": "NoSQL базы данных...",\r\n    "author": "Иван Иванов",\r\n    "created_at": "2025-01-15",\r\n    "views": 100\r\n}\r\n\r\nawait client.index(index="articles", id="1", body=doc)',
     '# Создаем документ для индексации\r\ndoc = {\r\n    "title": "Введение в NoSQL",\r\n    "content": "NoSQL базы данных...",\r\n    "author": "Иван Иванов",\r\n    "created_at": "2025-01-15",\r\n    "views": 100\r\n}\r\n\r\n# Индексируем документ с ID=1\r\nawait client.index(index="articles", id="1", body=doc)'),
    
    # Slide 31
    ('query = {\r\n    "query": {\r\n        "match": {\r\n            "content": "NoSQL базы данных"\r\n        }\r\n    }\r\n}\r\n\r\nresponse = await client.search(index="articles", body=query)\r\nhits = response["hits"]["hits"]',
     'query = {\r\n    "query": {\r\n        "match": {  # Полнотекстовый поиск\r\n            "content": "NoSQL базы данных"\r\n        }\r\n    }\r\n}\r\n\r\n# Выполняем поиск\r\nresponse = await client.search(index="articles", body=query)\r\nhits = response["hits"]["hits"]  # Результаты'),
    
    # Slide 32
    ('query = {\r\n    "query": {\r\n        "bool": {\r\n            "must": [{"match": {"content": "NoSQL"}}],\r\n            "filter": [\r\n                {"term": {"author": "Иван"}},\r\n                {"range": {"views": {"gte": 50}}}\r\n            ],\r\n            "should": [{"match": {"title": "MongoDB"}}],\r\n            "must_not": [{"term": {"status": "draft"}}]\r\n        }\r\n    }\r\n}',
     'query = {\r\n    "query": {\r\n        "bool": {  # Булев запрос\r\n            "must": [{"match": {"content": "NoSQL"}}],  # Обязательно\r\n            "filter": [  # Фильтры (не влияют на score)\r\n                {"term": {"author": "Иван"}},  # Точное совпадение\r\n                {"range": {"views": {"gte": 50}}}  # Диапазон\r\n            ],\r\n            "should": [{"match": {"title": "MongoDB"}}],  # Желательно\r\n            "must_not": [{"term": {"status": "draft"}}]  # Исключить\r\n        }\r\n    }\r\n}'),
    
    # Slide 34
    ('query = {\r\n    "size": 0,\r\n    "aggs": {\r\n        "authors": {\r\n            "terms": {"field": "author"},\r\n            "aggs": {\r\n                "avg_views": {"avg": {"field": "views"}}\r\n            }\r\n        },\r\n        "views_stats": {"stats": {"field": "views"}}\r\n    }\r\n}\r\nresponse = await client.search(index="articles", body=query)',
     'query = {\r\n    "size": 0,  # Не возвращать документы, только агрегации\r\n    "aggs": {\r\n        "authors": {  # Группировка по авторам\r\n            "terms": {"field": "author"},\r\n            "aggs": {  # Вложенная агрегация\r\n                "avg_views": {"avg": {"field": "views"}}  # Средние просмотры\r\n            }\r\n        },\r\n        "views_stats": {"stats": {"field": "views"}}  # Статистика\r\n    }\r\n}\r\nresponse = await client.search(index="articles", body=query)'),
    
    # Slide 35
    ('query = {\r\n    "query": {"match_all": {}},\r\n    "sort": [\r\n        {"created_at": {"order": "desc"}},\r\n        {"views": {"order": "desc"}}\r\n    ],\r\n    "from": 0,\r\n    "size": 10\r\n}',
     'query = {\r\n    "query": {"match_all": {}},  # Все документы\r\n    "sort": [  # Сортировка\r\n        {"created_at": {"order": "desc"}},  # По дате (новые первые)\r\n        {"views": {"order": "desc"}}  # Затем по просмотрам\r\n    ],\r\n    "from": 0,  # Offset (пропустить)\r\n    "size": 10  # Limit (вернуть)\r\n}'),
]

for old, new in replacements:
    content = content.replace(old, new)

with open('lect-nosql.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comments added to all code slides!")
