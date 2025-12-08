with open('lect-nosql.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Slide 11 - Connection
content = content.replace(
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 11: Подключение Python</h2><div style="text-align:left;font-size:.7em"><pre><code class="python">from motor.motor_asyncio import AsyncIOMotorClient\r\n\r\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\r\ndb = client["university_db"]\r\ncollection = db["students"]</code></pre></div></section>',
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 11: Подключение Python</h2><div style="text-align:left;font-size:.7em"><pre><code class="python"># Асинхронный драйвер для MongoDB\nfrom motor.motor_asyncio import AsyncIOMotorClient\n\n# Подключение к MongoDB\nclient = AsyncIOMotorClient("mongodb://localhost:27017")\ndb = client["university_db"]  # Выбор БД\ncollection = db["students"]  # Выбор коллекции</code></pre></div></section>'
)

# Slide 12 - Create
content = content.replace(
    '<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 12: CRUD - Create</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">student = {\r\n    "name": "Иван Иванов",\r\n    "age": 21,\r\n    "courses": ["Математика", "Программирование"]\r\n}\r\nresult = await collection.insert_one(student)\r\n\r\nstudents = [{"name": "Мария"}, {"name": "Петр"}]\r\nawait collection.insert_many(students)</code></pre></div></section>',
    '<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 12: CRUD - Create</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Создаем документ (JSON-объект)\nstudent = {\n    "name": "Иван Иванов",\n    "age": 21,\n    "courses": ["Математика", "Программирование"]\n}\n# Вставка одного документа\nresult = await collection.insert_one(student)\n\n# Вставка нескольких документов\nstudents = [{"name": "Мария"}, {"name": "Петр"}]\nawait collection.insert_many(students)</code></pre></div></section>'
)

# Slide 13 - Read
content = content.replace(
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 13: CRUD - Read</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Один документ\r\nstudent = await collection.find_one({"name": "Иван"})\r\n\r\n# Все с условием\r\ncursor = collection.find({"age": {"$gte": 20}})\r\nstudents = await cursor.to_list(length=100)\r\n\r\n# Проекция\r\ncursor = collection.find({}, {"name": 1, "age": 1, "_id": 0})</code></pre></div></section>',
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 13: CRUD - Read</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Найти один документ\nstudent = await collection.find_one({"name": "Иван"})\n\n# Найти все с условием (возраст >= 20)\ncursor = collection.find({"age": {"$gte": 20}})\nstudents = await cursor.to_list(length=100)\n\n# Проекция (выбор полей: 1=включить, 0=исключить)\ncursor = collection.find({}, {"name": 1, "age": 1, "_id": 0})</code></pre></div></section>'
)

# Slide 14 - Update
content = content.replace(
    '<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 14: CRUD - Update</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">await collection.update_one(\r\n    {"name": "Иван"},\r\n    {"$set": {"age": 22}}\r\n)\r\n\r\nawait collection.update_many(\r\n    {"age": {"$lt": 20}},\r\n    {"$inc": {"age": 1}}\r\n)</code></pre></div></section>',
    '<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 14: CRUD - Update</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Обновить один документ\nawait collection.update_one(\n    {"name": "Иван"},  # Фильтр\n    {"$set": {"age": 22}}  # $set - установить значение\n)\n\n# Обновить несколько документов\nawait collection.update_many(\n    {"age": {"$lt": 20}},  # Возраст < 20\n    {"$inc": {"age": 1}}  # $inc - увеличить на 1\n)</code></pre></div></section>'
)

# Slide 15 - Delete
content = content.replace(
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 15: CRUD - Delete</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">await collection.delete_one({"name": "Иван"})\r\n\r\nawait collection.delete_many({"age": {"$lt": 18}})</code></pre></div></section>',
    '<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 15: CRUD - Delete</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Удалить один документ\nawait collection.delete_one({"name": "Иван"})\n\n# Удалить несколько документов (возраст < 18)\nawait collection.delete_many({"age": {"$lt": 18}})</code></pre></div></section>'
)

with open('lect-nosql.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Comments fixed!")
