# Append remaining sections to the HTML file

sections = []

# Section 1: Project Structure
sections.append('''
        <div class="section">
            <h2>📁 Структура проекта</h2>
            <div class="code-block">stress-demo/
├── docker-compose.yml
├── app/
│   ├── main.py
│   └── models.py
├── load_test.py
└── README.md</div>
        </div>
''')

# Section 2: Docker Setup
sections.append('''
        <div class="section">
            <h2>1️⃣ Шаг 1: Подготовка среды (Docker Compose)</h2>
            
            <h3>Dockerfile</h3>
            <div class="code-block"><span class="keyword">FROM</span> python:3.11-slim

<span class="keyword">WORKDIR</span> /app

<span class="keyword">COPY</span> requirements.txt .
<span class="keyword">RUN</span> pip install -r requirements.txt

<span class="keyword">COPY</span> app/ .

<span class="keyword">EXPOSE</span> 8000

<span class="keyword">CMD</span> [<span class="string">"python"</span>, <span class="string">"-c"</span>, <span class="string">"import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8000)"</span>]</div>

            <h3>docker-compose.yml</h3>
            <div class="code-block"><span class="keyword">version:</span> <span class="string">'3.8'</span>
<span class="keyword">services:</span>
  <span class="keyword">db:</span>
    <span class="keyword">image:</span> postgres:17
    <span class="keyword">environment:</span>
      <span class="keyword">POSTGRES_DB:</span> student_db
      <span class="keyword">POSTGRES_USER:</span> student
      <span class="keyword">POSTGRES_PASSWORD:</span> password
    <span class="keyword">ports:</span>
      - <span class="string">"5432:5432"</span>
    <span class="keyword">command:</span> >
      postgres -c max_connections=20

  <span class="keyword">redis:</span>
    <span class="keyword">image:</span> redis:7-alpine
    <span class="keyword">ports:</span>
      - <span class="string">"6379:6379"</span>

  <span class="keyword">app:</span>
    <span class="keyword">build:</span> .
    <span class="keyword">ports:</span>
      - <span class="string">"8000:8000"</span>
    <span class="keyword">depends_on:</span>
      - db
      - redis
    <span class="keyword">environment:</span>
      <span class="keyword">DATABASE_URL:</span> postgresql+asyncpg://student:password@db:5432/student_db
      <span class="keyword">REDIS_URL:</span> redis://redis:6379</div>

            <p>⚠️ Обратите внимание: <code>max_connections=20</code> — <strong>намеренно уменьшено</strong>, чтобы быстрее достичь лимита.</p>

            <div class="checkbox-item">
                <input type="checkbox" id="task1">
                <label for="task1">Шаг 1: Docker Compose настроен</label>
            </div>
        </div>
''')

# Section 3: FastAPI without Redis
sections.append('''
        <div class="section">
            <h2>2️⃣ Шаг 2: FastAPI-приложение без Redis (уязвимая версия)</h2>
            
            <h3>app/models.py</h3>
            <div class="code-block"><span class="keyword">from</span> sqlalchemy <span class="keyword">import</span> Column, Integer
<span class="keyword">from</span> sqlalchemy.ext.asyncio <span class="keyword">import</span> create_async_engine, AsyncSession
<span class="keyword">from</span> sqlalchemy.orm <span class="keyword">import</span> declarative_base, sessionmaker

<span class="class">DATABASE_URL</span> <span class="operator">=</span> <span class="string">"postgresql+asyncpg://user:pass@db:5432/demo"</span>

engine <span class="operator">=</span> <span class="function">create_async_engine</span>(<span class="class">DATABASE_URL</span>, echo<span class="operator">=</span><span class="keyword">False</span>)
<span class="class">SessionLocal</span> <span class="operator">=</span> <span class="function">sessionmaker</span>(engine, class_<span class="operator">=</span>AsyncSession, expire_on_commit<span class="operator">=</span><span class="keyword">False</span>)
Base <span class="operator">=</span> <span class="function">declarative_base</span>()

<span class="keyword">class</span> <span class="class">Counter</span>(<span class="class">Base</span>):
    __tablename__ <span class="operator">=</span> <span class="string">"counter"</span>
    id <span class="operator">=</span> <span class="function">Column</span>(Integer, primary_key<span class="operator">=</span><span class="keyword">True</span>, default<span class="operator">=</span><span class="number">1</span>)
    value <span class="operator">=</span> <span class="function">Column</span>(Integer, default<span class="operator">=</span><span class="number">0</span>)</div>

            <h3>app/main.py (без Redis)</h3>
            <div class="code-block"><span class="keyword">from</span> fastapi <span class="keyword">import</span> FastAPI, Depends
<span class="keyword">from</span> sqlalchemy.ext.asyncio <span class="keyword">import</span> AsyncSession
<span class="keyword">from</span> models <span class="keyword">import</span> Counter, SessionLocal, engine, Base
<span class="keyword">import</span> uvicorn

app <span class="operator">=</span> <span class="function">FastAPI</span>()

<span class="decorator">@app.on_event</span>(<span class="string">"startup"</span>)
<span class="keyword">async def</span> <span class="function">init_db</span>():
    <span class="keyword">async with</span> engine.<span class="function">begin</span>() <span class="keyword">as</span> conn:
        <span class="keyword">await</span> conn.<span class="function">run_sync</span>(Base.metadata.create_all)

<span class="keyword">async def</span> <span class="function">get_db</span>():
    <span class="keyword">async with</span> <span class="function">SessionLocal</span>() <span class="keyword">as</span> session:
        <span class="keyword">yield</span> session

<span class="decorator">@app.post</span>(<span class="string">"/hit"</span>)
<span class="keyword">async def</span> <span class="function">hit</span>(db: AsyncSession <span class="operator">=</span> <span class="function">Depends</span>(get_db)):
    counter <span class="operator">=</span> <span class="keyword">await</span> db.<span class="function">get</span>(Counter, <span class="number">1</span>)
    <span class="keyword">if not</span> counter:
        counter <span class="operator">=</span> <span class="function">Counter</span>(id<span class="operator">=</span><span class="number">1</span>, value<span class="operator">=</span><span class="number">0</span>)
        db.<span class="function">add</span>(counter)
    counter.value <span class="operator">+=</span> <span class="number">1</span>
    <span class="keyword">await</span> db.<span class="function">commit</span>()
    <span class="keyword">return</span> {<span class="string">"count"</span>: counter.value}

<span class="keyword">if</span> __name__ <span class="operator">==</span> <span class="string">"__main__"</span>:
    uvicorn.<span class="function">run</span>(app, host<span class="operator">=</span><span class="string">"127.0.0.1"</span>, port<span class="operator">=</span><span class="number">8000</span>)</div>

            <div class="checkbox-item">
                <input type="checkbox" id="task2">
                <label for="task2">Шаг 2: FastAPI без Redis реализован</label>
            </div>
        </div>
''')

# Write all sections
with open('lab-broker-redis-metodichka.html', 'a', encoding='utf-8') as f:
    f.write(''.join(sections))

print("Sections appended successfully!")
