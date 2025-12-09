## Продолжение MongoDB - Агрегация и практика

**Слайды 18-19: Агрегация - это мощь!**

Агрегация в MongoDB - это как SQL запросы на стероидах. Работает как конвейер (pipeline) - данные проходят через стадии.

### Простой пример - считаем средний балл

Задача: найти средний балл студентов по каждому курсу.

```python
pipeline = [
    # Стадия 1: Фильтрация (WHERE в SQL)
    {"$match": {"age": {"$gte": 20}}},  # Только студенты 20+
    
    # Стадия 2: Группировка (GROUP BY в SQL)
    {"$group": {
        "_id": "$course",  # Группируем по полю course
        "avg_grade": {"$avg": "$grade"},  # Средний балл
        "count": {"$sum": 1},  # Количество студентов
        "max_grade": {"$max": "$grade"},  # Максимальный балл
        "min_grade": {"$min": "$grade"}  # Минимальный балл
    }},
    
    # Стадия 3: Сортировка (ORDER BY в SQL)
    {"$sort": {"avg_grade": -1}},  # -1 = DESC, 1 = ASC
    
    # Стадия 4: Ограничение (LIMIT в SQL)
    {"$limit": 10}  # Топ-10 курсов
]

# Выполняем агрегацию
results = await collection.aggregate(pipeline).to_list(None)

# Результат:
# [
#   {"_id": "Программирование", "avg_grade": 4.8, "count": 50, ...},
#   {"_id": "Математика", "avg_grade": 4.5, "count": 45, ...},
#   ...
# ]
```

Это аналог SQL:
```sql
SELECT 
    course as _id,
    AVG(grade) as avg_grade,
    COUNT(*) as count,
    MAX(grade) as max_grade,
    MIN(grade) as min_grade
FROM students
WHERE age >= 20
GROUP BY course
ORDER BY avg_grade DESC
LIMIT 10
```

### Основные стадии - разбираем подробно

**$match** - фильтрация документов (WHERE)

```python
# Простой фильтр
{"$match": {"age": 20}}

# С операторами
{"$match": {"age": {"$gte": 20, "$lte": 30}}}  # 20 <= age <= 30

# Логические операторы
{"$match": {
    "$or": [
        {"city": "Москва"},
        {"city": "Питер"}
    ]
}}
```

**$group** - группировка (GROUP BY)

```python
{"$group": {
    "_id": "$city",  # Группируем по городу
    
    # Агрегатные функции:
    "total": {"$sum": "$amount"},  # Сумма
    "avg": {"$avg": "$amount"},  # Среднее
    "min": {"$min": "$amount"},  # Минимум
    "max": {"$max": "$amount"},  # Максимум
    "count": {"$sum": 1},  # Количество
    
    # Собрать значения в массив
    "names": {"$push": "$name"},  # Все имена в массив
    
    # Первый/последний элемент группы
    "first_name": {"$first": "$name"},
    "last_name": {"$last": "$name"}
}}
```

**$sort** - сортировка (ORDER BY)

```python
{"$sort": {"age": 1}}  # По возрастанию (ASC)
{"$sort": {"age": -1}}  # По убыванию (DESC)

# Сортировка по нескольким полям
{"$sort": {"city": 1, "age": -1}}  # Сначала по городу, потом по возрасту
```

**$limit** и **$skip** - пагинация

```python
{"$skip": 20},  # Пропустить первые 20
{"$limit": 10}  # Взять 10

# Страница 1: skip=0, limit=10
# Страница 2: skip=10, limit=10
# Страница 3: skip=20, limit=10
```

**$project** - выбор полей (SELECT)

```python
{"$project": {
    "name": 1,  # Включить поле name
    "age": 1,  # Включить поле age
    "_id": 0,  # Исключить _id
    
    # Переименовать поле
    "fullName": "$name",
    
    # Вычисляемые поля
    "ageInMonths": {"$multiply": ["$age", 12]},
    "year": {"$year": "$birthDate"},
    
    # Условия
    "status": {
        "$cond": {
            "if": {"$gte": ["$age", 18]},
            "then": "adult",
            "else": "minor"
        }
    }
}}
```

**$lookup** - JOIN с другой коллекцией

```python
# У нас есть коллекции: students и courses
# В students есть поле courseId

{"$lookup": {
    "from": "courses",  # Из какой коллекции джойним
    "localField": "courseId",  # Поле в students
    "foreignField": "_id",  # Поле в courses
    "as": "courseInfo"  # Имя нового поля (будет массив)
}}

# Результат:
# {
#   "name": "Иван",
#   "courseId": ObjectId("..."),
#   "courseInfo": [  # Массив!
#     {"_id": ObjectId("..."), "title": "Математика", ...}
#   ]
# }
```

**$unwind** - развернуть массив

```python
# До $unwind:
# {"name": "Иван", "courses": ["Math", "CS", "Physics"]}

{"$unwind": "$courses"}

# После $unwind (3 документа):
# {"name": "Иван", "courses": "Math"}
# {"name": "Иван", "courses": "CS"}
# {"name": "Иван", "courses": "Physics"}
```

Зачем это нужно? Чтобы группировать по элементам массива!

### Реальный пример - книги с авторами

```python
# Коллекции: books и authors
# В books есть поле authorId

pipeline = [
    # 1. Джойним авторов
    {"$lookup": {
        "from": "authors",
        "localField": "authorId",
        "foreignField": "_id",
        "as": "author"
    }},
    
    # 2. Разворачиваем массив author в объект
    {"$unwind": "$author"},
    
    # 3. Выбираем нужные поля
    {"$project": {
        "title": 1,
        "pages": 1,
        "authorName": "$author.name",
        "authorCountry": "$author.country"
    }},
    
    # 4. Сортируем по количеству страниц
    {"$sort": {"pages": -1}},
    
    # 5. Берем топ-10
    {"$limit": 10}
]

books = await db.books.aggregate(pipeline).to_list(None)
```

**Слайд 20: Индексы - делаем MongoDB быстрым**

Индексы - это то, что отличает быструю базу от медленной.

### Без индекса - collection scan

```python
# Ищем студента по имени
await collection.find_one({"name": "Иван"})
```

Что происходит: MongoDB сканирует ВСЮ коллекцию, проверяя каждый документ. Если в коллекции миллион документов - проверит миллион.

### С индексом - index scan

```python
# Создаем индекс
await collection.create_index("name")

# Теперь поиск быстрый
await collection.find_one({"name": "Иван"})
```

Что происходит: MongoDB смотрит в индекс (отсортированный список), находит "Иван" за O(log N) операций. Если миллион документов - проверит ~20.

### Составной индекс

```python
# Индекс по двум полям
await collection.create_index([
    ("city", 1),  # 1 = по возрастанию
    ("age", -1)  # -1 = по убыванию
])

# Этот запрос использует индекс
await collection.find({"city": "Москва", "age": 25})

# Этот тоже (префикс индекса)
await collection.find({"city": "Москва"})

# А этот НЕ использует (нет префикса)
await collection.find({"age": 25})  # Нет city в фильтре
```

Правило: составной индекс работает слева направо.

### Уникальный индекс

```python
# Email должен быть уникальным
await collection.create_index("email", unique=True)

# Первая вставка - OK
await collection.insert_one({"email": "test@test.com", "name": "Иван"})

# Вторая вставка - ERROR!
await collection.insert_one({"email": "test@test.com", "name": "Петр"})
# DuplicateKeyError: E11000 duplicate key error
```

### Текстовый индекс

```python
# Для полнотекстового поиска
await collection.create_index([("description", "text"), ("title", "text")])

# Поиск по тексту
cursor = collection.find({"$text": {"$search": "python mongodb"}})
students = await cursor.to_list(100)
```

⚠️ Текстовый поиск в MongoDB базовый. Для серьезного поиска юзайте OpenSearch!

**Слайды 21-22: FastAPI + MongoDB - полная интеграция**

Теперь соберем все вместе - FastAPI приложение с MongoDB.

### Модель данных

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Student(BaseModel):
    # Конфигурация для работы с MongoDB
    model_config = ConfigDict(populate_by_name=True)
    
    # _id в MongoDB, но id в API
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    age: int
    email: str
    courses: list[str] = []
    grades: dict[str, int] = {}  # {"Математика": 5, "Физика": 4}
```

### Подключение к MongoDB

```python
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Подключение при старте приложения
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    app.mongodb = app.mongodb_client.university_db

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
```

### CRUD эндпоинты

```python
# CREATE - создать студента
@app.post("/students/", response_model=Student)
async def create_student(student: Student):
    # Конвертируем Pydantic модель в dict
    student_dict = student.model_dump(by_alias=True, exclude=["id"])
    
    # Вставляем в MongoDB
    result = await app.mongodb.students.insert_one(student_dict)
    
    # Возвращаем с ID
    student.id = str(result.inserted_id)
    return student

# READ - получить студента по ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    # Конвертируем строку в ObjectId
    try:
        obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Ищем в MongoDB
    student = await app.mongodb.students.find_one({"_id": obj_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Конвертируем ObjectId в строку для JSON
    student["_id"] = str(student["_id"])
    return student

# READ - получить всех студентов с фильтрами
@app.get("/students/", response_model=list[Student])
async def get_students(
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    course: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    # Строим фильтр
    filter_query = {}
    
    if min_age:
        filter_query["age"] = {"$gte": min_age}
    if max_age:
        filter_query.setdefault("age", {})["$lte"] = max_age
    if course:
        filter_query["courses"] = course
    
    # Выполняем запрос
    cursor = app.mongodb.students.find(filter_query).skip(skip).limit(limit)
    students = await cursor.to_list(length=limit)
    
    # Конвертируем ObjectId в строки
    for student in students:
        student["_id"] = str(student["_id"])
    
    return students

# UPDATE - обновить студента
@app.put("/students/{student_id}")
async def update_student(student_id: str, student: Student):
    try:
        obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    # Обновляем
    result = await app.mongodb.students.update_one(
        {"_id": obj_id},
        {"$set": student.model_dump(exclude=["id"])}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Updated successfully"}

# DELETE - удалить студента
@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    try:
        obj_id = ObjectId(student_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    result = await app.mongodb.students.delete_one({"_id": obj_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Deleted successfully"}
```

### Эндпоинт с агрегацией

```python
@app.get("/stats/courses")
async def get_course_stats():
    """Статистика по курсам"""
    pipeline = [
        {"$unwind": "$courses"},  # Разворачиваем массив courses
        {"$group": {
            "_id": "$courses",
            "student_count": {"$sum": 1},
            "avg_age": {"$avg": "$age"}
        }},
        {"$sort": {"student_count": -1}}
    ]
    
    results = await app.mongodb.students.aggregate(pipeline).to_list(None)
    return results
```

**Слайд 23: MongoDB - Плюсы и минусы (честно)**

Давайте честно - у MongoDB есть и плюсы, и минусы. Не бывает серебряной пули.

### Плюсы (когда MongoDB рулит)

✅ **Гибкая схема** - добавил поле и все, никаких ALTER TABLE

Пример: у вас коллекция пользователей. Решили добавить поле `phone`. Просто вставляете документ с этим полем:
```python
await db.users.insert_one({"name": "Иван", "phone": "+7123456789"})
```
Все. Никаких миграций.

✅ **Высокая производительность** - особенно для чтения

MongoDB держит индексы в RAM. Если индекс влезает в память - запросы летают.

✅ **Горизонтальное масштабирование** - добавил сервер и все

Настроил шардинг один раз - дальше MongoDB сам распределяет данные.

✅ **Работа с JSON** - нативная поддержка

Получили JSON от API? Сохранили как есть. Не нужно парсить, раскладывать по таблицам.

✅ **Богатый язык запросов** - агрегации, операторы, все есть

Агрегации в MongoDB мощнее, чем в большинстве SQL баз.

### Минусы (когда MongoDB не подходит)

❌ **Нет нормальных JOIN** - есть $lookup, но он медленный

$lookup работает, но:
- Медленнее, чем JOIN в PostgreSQL
- Нет оптимизатора запросов
- Нельзя делать сложные JOIN

Если у вас много связанных данных - лучше PostgreSQL.

❌ **Больше памяти** - из-за дублирования данных

В реляционной БД данные нормализованы. В MongoDB часто дублируются для скорости.

Пример:
```javascript
// Вместо JOIN дублируем данные
{
  "title": "Война и мир",
  "author": {  // Дублируем информацию об авторе
    "name": "Толстой",
    "country": "Россия"
  }
}
```

❌ **Нет транзакций** - до версии 4.0

С версии 4.0 транзакции есть, но:
- Работают только в replica set
- Медленнее, чем в PostgreSQL
- Не рекомендуются для частого использования

❌ **Eventual consistency** - данные могут быть не синхронизированы

При репликации данные копируются асинхронно. Может быть задержка.

❌ **Сложность шардинга** - настроить непросто

Шардинг - это мощно, но:
- Нужно выбрать shard key (ключ для распределения)
- Неправильный shard key = неравномерное распределение
- Сложно мигрировать на шардинг потом

### Когда НЕ использовать MongoDB

- Много связанных данных (JOIN'ов)
- Нужны строгие транзакции (банки, финансы)
- Данные строго структурированы
- Небольшой объем данных (PostgreSQL проще)

### Когда использовать MongoDB

- Гибкая схема данных
- Большие объемы данных
- Высокая скорость записи
- Иерархические данные (JSON)
- Прототипирование (быстрый старт)

---

## Переходим к OpenSearch (следующая часть лекции)

Окей, с MongoDB разобрались. Теперь переходим к OpenSearch - это совсем другая история.

MongoDB - это база данных общего назначения. OpenSearch - это специализированная поисковая система.

Представьте: у вас сайт с миллионом статей. Пользователь вводит "как настроить mongodb". Как искать?

В MongoDB:
```python
# Медленно и плохо работает
await db.articles.find({"content": {"$regex": "mongodb", "$options": "i"}})
```

В OpenSearch:
```python
# Быстро и с ранжированием
await client.search(index="articles", body={
    "query": {"match": {"content": "как настроить mongodb"}}
})
```

OpenSearch найдет статьи с этими словами, учтет морфологию ("настроить" = "настройка"), отсортирует по релевантности.

Поехали разбираться!
