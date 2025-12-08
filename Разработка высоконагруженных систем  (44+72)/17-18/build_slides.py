# Build complete presentation
with open('lect-nosql.html', 'r', encoding='utf-8') as f:
    content = f.read()

# MongoDB slides to append
mongodb_slides = '''
<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 6: MongoDB</h2><div style="text-align:left;font-size:.7em"><p style="margin-left:20px"><strong>Document-oriented NoSQL СУБД</strong></p><ul style="margin-left:40px"><li class="fragment">📄 Хранение в формате BSON (Binary JSON)</li><li class="fragment">🔄 Гибкая схема</li><li class="fragment">📈 Горизонтальное масштабирование (sharding)</li></ul></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 7: Архитектура MongoDB</h2><div style="font-size:.65em"><pre style="margin-top:10px"><code>┌─────────────────────────────────────────┐
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
└─────────────────────────────────────────┘</code></pre><p style="margin-top:15px;font-size:.9em"><strong>mongod</strong> - сервер | <strong>mongos</strong> - роутер | <strong>WiredTiger</strong> - движок</p></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 8: Основные концепции</h2><div style="text-align:left;font-size:.7em"><ul style="margin-left:40px"><li class="fragment">🗄️ Database → Collection → Document</li><li class="fragment">📝 Document = JSON-подобный объект</li><li class="fragment">🔑 _id — уникальный идентификатор</li><li class="fragment">⚡ Индексы для ускорения запросов</li></ul></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 9: Системные БД</h2><div style="text-align:left;font-size:.65em"><div class="fragment"><h3 style="color:#3498db">admin</h3><p style="margin-left:20px">Пользователи, роли, команды управления</p></div><div class="fragment" style="margin-top:15px"><h3 style="color:#2ecc71">config</h3><p style="margin-left:20px">Метаданные о шардах (только при sharding)</p></div><div class="fragment" style="margin-top:15px"><h3 style="color:#f39c12">local</h3><p style="margin-left:20px">Не реплицируется, oplog, временные данные</p></div><p class="fragment" style="margin-top:20px;color:#e74c3c;text-align:center">⚠️ Создаются автоматически, не удалять!</p></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 10: Установка MongoDB</h2><div style="text-align:left;font-size:.7em"><pre><code class="bash"># Docker
docker run -d -p 27017:27017 mongo:7

# Percona (альтернатива для РФ)
docker run -d -p 27017:27017 percona/percona-server-mongodb:7.0</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 11: Подключение Python</h2><div style="text-align:left;font-size:.7em"><pre><code class="python">from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["university_db"]
collection = db["students"]</code></pre></div></section>

<section data-background-color="#16213e"><h2 style="color:#FFD700">Слайд 12: CRUD - Create</h2><div style="text-align:left;font-size:.65em"><pre><code class="python">student = {
    "name": "Иван Иванов",
    "age": 21,
    "courses": ["Математика", "Программирование"]
}
result = await collection.insert_one(student)

students = [{"name": "Мария"}, {"name": "Петр"}]
await collection.insert_many(students)</code></pre></div></section>

<section data-background-color="#2c3e50"><h2 style="color:#FFD700">Слайд 13: CRUD - Read</h2><div style="text-align:left;font-size:.65em"><pre><code class="python"># Один документ
student = await collection.find_one({"name": "Иван"})

# Все с условием
cursor = collection.find({"age": {"$gte": 20}})
students = await cursor.to_list(length=100)

# Проекция
cursor = collection.find({}, {"name": 1, "age": 1, "_id": 0})</code></pre></div></section>
'''

# Insert before closing tags
closing = '</div></div><script src="../15-16/js/reveal.min.js"></script>'
if closing in content:
    content = content.replace(closing, mongodb_slides + '\n' + closing)
    
with open('lect-nosql.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("MongoDB slides added (6-13)")
