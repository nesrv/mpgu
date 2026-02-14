продолжение 
# слайд 36

## 🎯 Часть 4: Нефункциональные требования (25 минут)

### 4.1 Performance - делаем систему быстрой

**Метрики производительности:**

**Latency (задержка):**
- P50 (медиана) - 50% запросов быстрее
- P95 - 95% запросов быстрее
- P99 - 99% запросов быстрее
- P99.9 - 99.9% запросов быстрее

**Пример:**
```
API endpoint /users
P50: 50ms
P95: 200ms
P99: 500ms
P99.9: 2000ms
```

Что это значит? 50% запросов отвечают за 50ms, но 0.1% запросов тормозят до 2 секунд. Надо разбираться почему.

**Throughput (пропускная способность):**
- RPS (Requests Per Second)
- TPS (Transactions Per Second)

**Пример:**
```
Наш API выдерживает 10,000 RPS
При 15,000 RPS начинает падать latency
При 20,000 RPS сервер умирает
```
# слайд 37

**Как улучшить производительность:**

**1. Кэширование:**
```python
# Плохо - каждый раз в БД
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return await db.users.find_one({"id": user_id})

# Хорошо - с кэшем
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    user = await db.users.find_one({"id": user_id})
    await redis.setex(f"user:{user_id}", 300, json.dumps(user))
    return user
```
# слайд 38

**2. Индексы в БД:**
```sql
-- Плохо - full table scan
SELECT * FROM users WHERE email = 'test@example.com';

-- Хорошо - с индексом
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'test@example.com';
```

# слайд 39

**3. Асинхронность:**
```python
# Плохо - синхронно
def send_email(user):
    smtp.send(user.email, "Welcome!")  # Ждем 2 секунды
    return {"status": "ok"}

# Хорошо - асинхронно
async def send_email(user):
    await queue.publish("email", {
        "to": user.email,
        "subject": "Welcome!"
    })
    return {"status": "queued"}
```

# слайд 40

**4. Connection pooling:**
```python
# Плохо - новое соединение каждый раз
async def get_user(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    await conn.close()
    return user

# Хорошо - пул соединений
pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=50)

async def get_user(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
```
# слайд 41


**5. Батчинг:**
```python
# Плохо - N+1 проблема
users = await db.users.find()
for user in users:
    user.posts = await db.posts.find({"user_id": user.id})

# Хорошо - один запрос
users = await db.users.find()
user_ids = [u.id for u in users]
posts = await db.posts.find({"user_id": {"$in": user_ids}})
posts_by_user = defaultdict(list)
for post in posts:
    posts_by_user[post.user_id].append(post)
for user in users:
    user.posts = posts_by_user[user.id]
```

**Интерактив:** У вас API, который отвечает 2 секунды. Как будете искать проблему? (Обсуждение 3 минуты)

# слайд 42

### 4.2 Scalability - масштабируем систему

**Вертикальное масштабирование:**
- Больше CPU, RAM, диск
- Просто
- Ограничено железом
- Дорого

**Горизонтальное масштабирование:**
- Больше серверов
- Сложнее
- Почти безгранично
- Дешевле (на единицу мощности)

# слайд 43


**Stateless vs Stateful:**

**Stateless сервисы:**
```python
# Хорошо - stateless
@app.get("/users/{user_id}")
async def get_user(user_id: int, token: str = Header()):
    user = verify_token(token)  # Токен в запросе
    return await db.users.find_one({"id": user_id})
```

**Stateful сервисы:**
```python
# Плохо - stateful
sessions = {}  # В памяти сервера

@app.post("/login")
async def login(credentials):
    session_id = generate_session()
    sessions[session_id] = user  # Проблема при масштабировании!
    return {"session_id": session_id}
```

**Решение - вынести state:**
```python
# Хорошо - state в Redis
@app.post("/login")
async def login(credentials):
    session_id = generate_session()
    await redis.setex(f"session:{session_id}", 3600, json.dumps(user))
    return {"session_id": session_id}
```

# слайд 44

**Load Balancing:**

```
                    Load Balancer
                    /    |    \
                   /     |     \
              Server1 Server2 Server3
                   \     |     /
                    \    |    /
                     Database
```

**Алгоритмы балансировки:**
- Round Robin - по очереди
- Least Connections - на наименее загруженный
- IP Hash - один клиент всегда на один сервер
- Weighted - с учетом мощности серверов


# слайд 45
**Database sharding:**

```python
# Шардинг по user_id
def get_shard(user_id):
    return user_id % 4  # 4 шарда

# Запись
shard = get_shard(user.id)
await db_shards[shard].users.insert_one(user)

# Чтение
shard = get_shard(user_id)
user = await db_shards[shard].users.find_one({"id": user_id})
```

# слайд 46

**Проблемы шардинга:**
- Сложные JOIN'ы
- Ребалансировка при добавлении шардов
- Hotspots (один шард перегружен)

**Интерактив:** Как бы вы шардировали Instagram? По чему делить? (Обсуждение 3 минуты)


# слайд 47

**Паттерны надежности:**

**1. Retry (повтор):**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_external_api():
    response = await httpx.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

**2. Circuit Breaker (предохранитель):**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None
    
    async def call(self, func):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen()
        
        try:
            result = await func()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

**3. Bulkhead (изоляция):**
```python
# Разные пулы соединений для разных сервисов
payment_pool = asyncpg.create_pool(PAYMENT_DB_URL, max_size=10)
analytics_pool = asyncpg.create_pool(ANALYTICS_DB_URL, max_size=5)

# Если аналитика упала, платежи работают
```

**4. Timeout:**
```python
# Плохо - висим вечно
response = await httpx.get("https://slow-api.com")

# Хорошо - таймаут
try:
    response = await asyncio.wait_for(
        httpx.get("https://slow-api.com"),
        timeout=5.0
    )
except asyncio.TimeoutError:
    logger.error("API timeout")
    return {"error": "Service unavailable"}
```

**5. Graceful Degradation:**
```python
async def get_recommendations(user_id):
    try:
        # Пытаемся получить персональные рекомендации
        return await ml_service.get_recommendations(user_id)
    except Exception as e:
        logger.error(f"ML service failed: {e}")
        # Возвращаем популярные товары
        return await db.products.find().sort("views", -1).limit(10)
```

**Интерактив:** Ваш платежный сервис упал. Что делать? (Обсуждение 3 минуты)

### 4.4 Security - защищаем систему

**OWASP Top 10 (что нужно знать):**

**1. Injection (SQL, NoSQL, Command):**
```python
# Плохо - SQL injection
query = f"SELECT * FROM users WHERE email = '{email}'"

# Хорошо - параметризованный запрос
query = "SELECT * FROM users WHERE email = $1"
result = await conn.fetchrow(query, email)
```

**2. Broken Authentication:**
```python
# Плохо - пароль в plaintext
user.password = password

# Хорошо - хэширование
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user.password = pwd_context.hash(password)
```

**3. Sensitive Data Exposure:**
```python
# Плохо - возвращаем все
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return await db.users.find_one({"id": user_id})
    # Вернули password_hash, email, phone!

# Хорошо - только нужное
class UserResponse(BaseModel):
    id: int
    username: str
    avatar: str

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    return await db.users.find_one({"id": user_id})
```

**4. XML External Entities (XXE):**
```python
# Плохо - парсим XML без защиты
import xml.etree.ElementTree as ET
tree = ET.parse(user_input)

# Хорошо - используем defusedxml
from defusedxml import ElementTree as ET
tree = ET.parse(user_input)
```

**5. Broken Access Control:**
```python
# Плохо - не проверяем права
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    await db.posts.delete_one({"id": post_id})

# Хорошо - проверяем владельца
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user)):
    post = await db.posts.find_one({"id": post_id})
    if post.author_id != current_user.id:
        raise HTTPException(403, "Not your post")
    await db.posts.delete_one({"id": post_id})
```

**6. Security Misconfiguration:**
```python
# Плохо - дебаг в проде
app = FastAPI(debug=True)  # Показывает стектрейсы!

# Хорошо
app = FastAPI(debug=False)
```

**7. Cross-Site Scripting (XSS):**
```python
# Плохо - не экранируем
return f"<h1>Hello, {username}</h1>"

# Хорошо - используем шаблонизатор
from jinja2 import Template
template = Template("<h1>Hello, {{ username }}</h1>")
return template.render(username=username)
```

**8. Insecure Deserialization:**
```python
# Плохо - pickle небезопасен
import pickle
data = pickle.loads(user_input)

# Хорошо - используем JSON
import json
data = json.loads(user_input)
```

**9. Using Components with Known Vulnerabilities:**
```bash
# Проверяем зависимости
pip install safety
safety check

# Обновляем регулярно
pip list --outdated
```

**10. Insufficient Logging & Monitoring:**
```python
# Плохо - нет логов
@app.post("/login")
async def login(credentials):
    user = await authenticate(credentials)
    return {"token": create_token(user)}

# Хорошо - логируем важное
@app.post("/login")
async def login(credentials, request: Request):
    try:
        user = await authenticate(credentials)
        logger.info(f"Successful login: user={user.id}, ip={request.client.host}")
        return {"token": create_token(user)}
    except AuthenticationError:
        logger.warning(f"Failed login: email={credentials.email}, ip={request.client.host}")
        raise HTTPException(401, "Invalid credentials")
```

**Best practices:**

**Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials):
    # Максимум 5 попыток в минуту
    pass
```

**CORS:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],  # Не "*"!
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**HTTPS only:**
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

**Интерактив:** Найдите уязвимости в этом коде (показываю код с проблемами, 5 минут)

---

## 🔄 Часть 5: Архитектор в разных процессах (15 минут)

### 5.1 Архитектор в Scrum

**Sprint Planning:**
- Оценивает техническую сложность User Stories
- Предлагает технические решения
- Выявляет технические риски
- Помогает декомпозировать задачи

**Daily Standup:**
- Слушает блокеры команды
- Помогает решать технические проблемы
- Синхронизируется с другими командами

**Sprint Review:**
- Демонстрирует архитектурные решения
- Объясняет технические компромиссы
- Собирает фидбек

**Sprint Retrospective:**
- Предлагает улучшения процесса
- Обсуждает технический долг
- Планирует рефакторинг

**Backlog Refinement:**
- Помогает продакту формулировать требования
- Оценивает feasibility
- Предлагает альтернативы

**Пример из жизни:**

Product Owner: "Нам нужен real-time чат для 1 миллиона пользователей за 2 недели"

Архитектор: "Окей, давайте разберем:
- 1М пользователей одновременно или всего?
- Какие требования к latency?
- Нужна ли история сообщений?
- Есть ли у нас опыт с WebSocket?

Предлагаю:
- Sprint 1: PoC на 1000 пользователей, измеряем метрики
- Sprint 2: Оптимизация и масштабирование
- Sprint 3: Production-ready решение

Риски:
- WebSocket держит соединения, нужно много памяти
- Нужен Redis для pub/sub
- Возможно, понадобится Kafka для истории"

### 5.2 Архитектор в Waterfall

**Requirements Phase:**
- Собирает нефункциональные требования
- Оценивает технические ограничения
- Выбирает технологии

**Design Phase:**
- Создает архитектурную документацию
- Рисует диаграммы (UML, C4)
- Пишет технические спецификации
- Проводит Architecture Review

**Implementation Phase:**
- Консультирует разработчиков
- Делает code review критичных частей
- Решает технические проблемы

**Testing Phase:**
- Проверяет нефункциональные требования
- Участвует в performance testing
- Анализирует результаты нагрузочного тестирования

**Deployment Phase:**
- Планирует деплой
- Готовит rollback план
- Мониторит метрики

**Maintenance Phase:**
- Анализирует production issues
- Планирует технические улучшения
- Управляет техническим долгом

**Проблемы Waterfall:**
- Долгая фаза дизайна (можно переделать)
- Сложно менять архитектуру в середине
- Риск overengineering

### 5.3 Архитектор в гибких методологиях (Kanban, XP)

**Kanban:**
- Архитектурные задачи в бэклоге
- WIP limits для архитектурных работ
- Continuous improvement архитектуры
- Эволюционный дизайн

**Extreme Programming (XP):**
- Pair programming с архитектором
- Refactoring как часть процесса
- Simple design (YAGNI)
- Collective code ownership

**Lean:**
- Минимизация waste
- Just-in-time архитектура
- Быстрая обратная связь
- Continuous learning

**Пример эволюционной архитектуры:**

**Итерация 1:** Монолит на Django
- Быстро запустились
- Все работает

**Итерация 2:** Выделили платежный сервис
- Платежи критичны
- Нужна изоляция

**Итерация 3:** Добавили Redis для кэша
- Нагрузка выросла
- БД не справляется

**Итерация 4:** Разделили на микросервисы
- Команда выросла до 30 человек
- Нужна независимая разработка

**Интерактив:** Какой процесс вам ближе и почему? (Обсуждение 3 минуты)

---

## 🎓 Заключение и Q&A (10 минут)

### Ключевые выводы

**1. Архитектор это не просто "рисовальщик диаграмм"**
- Это технический лидер
- Принимает важные решения
- Несет ответственность за систему

**2. Нет идеальной архитектуры**
- Все решения это trade-offs
- Контекст важнее паттернов
- Простота > сложность

**3. Архитектура эволюционирует**
- Начинайте с простого
- Усложняйте по необходимости
- Рефакторинг это нормально

**4. Коммуникация важнее технологий**
- Объясняйте решения команде
- Слушайте разработчиков
- Документируйте важное

**5. Учитесь постоянно**
- Технологии меняются
- Паттерны эволюционируют
- Опыт приходит с практикой

### Как стать архитектором

**Путь:**
1. Junior (1-2 года) - учитесь писать код
2. Middle (2-4 года) - понимаете систему целиком
3. Senior (4-6 лет) - проектируете компоненты
4. Architect (6+ лет) - проектируете системы

**Что делать:**
- Читайте код других проектов
- Изучайте open source архитектуры
- Пробуйте разные технологии
- Делайте pet projects
- Читайте книги (список ниже)
- Ходите на конференции
- Общайтесь с другими архитекторами

**Книги must-read:**
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Clean Architecture" - Robert Martin
- "Building Microservices" - Sam Newman
- "Domain-Driven Design" - Eric Evans
- "Site Reliability Engineering" - Google
- "Release It!" - Michael Nygard

### Практические советы

**1. Начинайте с малого**
- Не пытайтесь спроектировать все сразу
- MVP > идеальная архитектура
- Итерируйте

**2. Измеряйте все**
- Метрики не врут
- Профилируйте перед оптимизацией
- A/B тестируйте решения

**3. Документируйте решения**
- ADR (Architecture Decision Records)
- Диаграммы (C4 model)
- README в каждом репозитории

**4. Автоматизируйте**
- CI/CD обязателен
- Тесты обязательны
- Мониторинг критичен

**5. Думайте о людях**
- Код пишут люди
- Код читают люди
- Код поддерживают люди

### Вопросы и ответы

**Q: Нужно ли знать все технологии?**
A: Нет. Нужно знать принципы и уметь быстро изучать новое. Глубина важнее ширины.

**Q: Как выбрать между монолитом и микросервисами?**
A: Начинайте с монолита. Переходите на микросервисы, когда появятся реальные проблемы (команда >20 человек, разные части системы масштабируются по-разному).

**Q: Сколько времени тратить на проектирование?**
A: В Scrum - 10-20% времени спринта. В Waterfall - отдельная фаза. Главное - не переделывать.

**Q: Как убедить команду в своем решении?**
A: Объясните trade-offs. Покажите альтернативы. Сделайте PoC. Слушайте возражения.

**Q: Что делать с техническим долгом?**
A: Выделяйте время на рефакторинг (20% спринта). Приоритизируйте критичные части. Не копите.

**Q: Нужно ли архитектору писать код?**
A: Да! Иначе потеряете связь с реальностью. Но меньше, чем раньше.

**Q: Как оценить архитектуру?**
A: Метрики (performance, availability), отзывы команды, количество инцидентов, скорость разработки.

---

## 🎯 Домашнее задание

**Задание 1: Спроектируйте архитектуру**

Вам нужно спроектировать систему для онлайн-кинотеатра:
- 1 миллион пользователей
- 10,000 фильмов
- Стриминг видео
- Рекомендации
- Платежи
- Комментарии и рейтинги

**Что нужно:**
1. Выбрать технологии (язык, фреймворк, БД)
2. Нарисовать high-level архитектуру
3. Описать, как будете масштабировать
4. Описать, как обеспечите надежность
5. Написать ADR для ключевых решений

**Задание 2: Найдите проблемы**

Дан код API (предоставлю на следующей паре). Найдите:
- Проблемы с производительностью
- Уязвимости безопасности
- Проблемы с масштабируемостью
- Нарушения best practices

**Задание 3: Исследование**

Выберите одну из тем и подготовьте доклад на 10 минут:
- Event-driven архитектура
- CQRS и Event Sourcing
- Serverless архитектура
- Service Mesh (Istio, Linkerd)
- GraphQL vs REST
- Distributed tracing

---

## 📚 Дополнительные материалы

**Блоги:**
- Martin Fowler - martinfowler.com
- High Scalability - highscalability.com
- Netflix Tech Blog
- Uber Engineering Blog
- AWS Architecture Blog

**YouTube каналы:**
- Hussein Nasser
- Gaurav Sen
- System Design Interview
- Tech Dummies

**Подкасты:**
- Software Engineering Daily
- The Changelog
- Coding Blocks

**Инструменты:**
- draw.io - диаграммы
- PlantUML - диаграммы как код
- Structurizr - C4 model
- Miro - коллаборация

---

Спасибо за внимание! Вопросы?

**Контакты:**
- Email: [ваш email]
- Telegram: [ваш telegram]
- GitHub: [ваш github]

**Следующая лекция:** Микросервисы и распределенные системы

До встречи! 🚀
