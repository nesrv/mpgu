# FastAPI: Маршрутизация, Архитектура и Безопасность

## 📌 Слайд 1: Введение

### FastAPI. Маршрутизация. Разделение на слои. Автоматизированное тестирование

**Что мы изучим:**
- 🛣️ Продвинутая маршрутизация с APIRouter
- 🏗️ Архитектурные паттерны и разделение на слои
- 🔐 Аутентификация и авторизация (Basic Auth, OAuth2, JWT)
- 🧪 Автоматизированное тестирование API

**Почему это важно для высоконагруженных систем?**
- Правильная архитектура = масштабируемость
- Разделение на слои = легкость поддержки
- Безопасность = защита от атак
- Тестирование = стабильность в продакшене

---

## 📌 Слайд 2: Маршрутизация с помощью APIRouter

### Зачем нужен APIRouter?

**Проблема монолитного приложения:**
```python
# ❌ Плохо: всё в одном файле
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users(): ...

@app.get("/products")
def get_products(): ...

@app.get("/orders")
def get_orders(): ...
# ... 100+ эндпоинтов
```

**Решение: модульная структура с APIRouter**
```python
# ✅ Хорошо: разделение по модулям
# main.py
from fastapi import FastAPI
from routers import users, products, orders

app = FastAPI()
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
```

### Структура проекта

```
project/
├── main.py
├── routers/
│   ├── __init__.py
│   ├── users.py      # /api/v1/users
│   ├── products.py   # /api/v1/products
│   └── orders.py     # /api/v1/orders
├── services/
│   ├── user_service.py
│   └── product_service.py
└── models/
    ├── user.py
    └── product.py
```

### Пример реализации роутера

```python
# routers/users.py
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[User])
async def get_users():
    return await user_service.get_all()

@router.get("/{user_id}")
async def get_user(user_id: int):
    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/", status_code=201)
async def create_user(user: UserCreate):
    return await user_service.create(user)
```

### Визуализация маршрутизации

```
HTTP Request → FastAPI App → APIRouter → Endpoint Handler
                    ↓
            /api/v1/users → users.router → get_users()
            /api/v1/products → products.router → get_products()
            /api/v1/orders → orders.router → get_orders()
```

---

## 📌 Слайд 3: Архитектурные паттерны

### MVC (Model-View-Controller)

**Классический веб-паттерн:**
- **Model** - данные и бизнес-логика
- **View** - представление (HTML, JSON)
- **Controller** - обработка запросов

```
User Request → Controller → Model → Database
                    ↓
                  View → Response
```

### MTV (Model-Template-View) - Django подход

- **Model** - данные
- **Template** - шаблоны HTML
- **View** - логика обработки

### Layered Architecture для FastAPI

**Современный подход для API:**

```
┌─────────────────────────────────┐
│   API Layer (Routers)           │  ← HTTP запросы/ответы
├─────────────────────────────────┤
│   Service Layer (Business)      │  ← Бизнес-логика
├─────────────────────────────────┤
│   Repository Layer (Data)       │  ← Работа с БД
├─────────────────────────────────┤
│   Database                      │  ← Хранение данных
└─────────────────────────────────┘
```

**Преимущества:**
- ✅ Разделение ответственности (SRP)
- ✅ Легкое тестирование каждого слоя
- ✅ Возможность замены компонентов
- ✅ Масштабируемость

---

## 📌 Слайд 4: Слои в FastAPI - Взаимодействие

### Анимация потока данных

```
┌──────────────────────────────────────────────────────┐
│  1. CLIENT                                           │
│     POST /api/users {"name": "Anna", "age": 25}      │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  2. API LAYER (Router)                               │
│     @router.post("/users")                           │
│     - Валидация входных данных (Pydantic)            │
│     - Проверка прав доступа                          │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  3. SERVICE LAYER (Business Logic)                   │
│     user_service.create_user(data)                   │
│     - Проверка бизнес-правил                         │
│     - Хеширование пароля                             │
│     - Отправка email                                 │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  4. REPOSITORY LAYER (Data Access)                   │
│     user_repository.save(user)                       │
│     - SQL запросы                                    │
│     - Кеширование                                    │
└────────────────────┬─────────────────────────────────┘
                     ↓
┌──────────────────────────────────────────────────────┐
│  5. DATABASE                                         │
│     INSERT INTO users ...                            │
└──────────────────────────────────────────────────────┘
```

### Обратный поток (Response)

```
Database → Repository → Service → Router → Client
   ↓           ↓          ↓         ↓        ↓
  User      User DTO   UserOut   JSON    {"id": 1, ...}
```


---

## 📌 Слайд 5: Слои в FastAPI - Примеры кода

### 4 колонки с кодом слоев

#### 1️⃣ API Layer (Router)
```python
# routers/users.py
from fastapi import APIRouter, Depends
from services.user_service import UserService
from schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserOut)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends()
):
    return await service.create_user(user_data)

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    service: UserService = Depends()
):
    return await service.get_user(user_id)
```

#### 2️⃣ Service Layer (Business Logic)
```python
# services/user_service.py
from repositories.user_repository import UserRepository
from schemas.user import UserCreate
from utils.security import hash_password

class UserService:
    def __init__(self, repo: UserRepository = Depends()):
        self.repo = repo
    
    async def create_user(self, data: UserCreate):
        # Бизнес-логика
        if await self.repo.exists_by_email(data.email):
            raise ValueError("Email already exists")
        
        # Хеширование пароля
        hashed_pwd = hash_password(data.password)
        
        # Сохранение
        user = await self.repo.create({
            **data.dict(),
            "password": hashed_pwd
        })
        
        # Отправка welcome email
        await send_welcome_email(user.email)
        
        return user
    
    async def get_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user
```

#### 3️⃣ Repository Layer (Data Access)
```python
# repositories/user_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
    
    async def create(self, data: dict):
        user = User(**data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int):
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def exists_by_email(self, email: str) -> bool:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None
```

#### 4️⃣ Model Layer (Database)
```python
# models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

---

## 📌 Слайд 6: Сервисный уровень - Примеры реализации

### Зачем нужен Service Layer?

**Без Service Layer (плохо):**
```python
@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends()):
    # ❌ Роутер содержит бизнес-логику
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Email exists")
    
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    db_user = User(email=user.email, password=hashed)
    db.add(db_user)
    db.commit()
    
    send_email(user.email, "Welcome!")
    return db_user
```

**С Service Layer (хорошо):**
```python
@router.post("/users")
async def create_user(
    user: UserCreate, 
    service: UserService = Depends()
):
    # ✅ Роутер только вызывает сервис
    return await service.create_user(user)
```

### Примеры сложной бизнес-логики в Service

#### Пример 1: Создание заказа
```python
class OrderService:
    async def create_order(self, user_id: int, items: List[OrderItem]):
        # 1. Проверка наличия товаров
        for item in items:
            product = await self.product_repo.get(item.product_id)
            if product.stock < item.quantity:
                raise InsufficientStockError(product.name)
        
        # 2. Расчет стоимости
        total = sum(item.price * item.quantity for item in items)
        
        # 3. Применение скидок
        discount = await self.discount_service.calculate(user_id, total)
        final_total = total - discount
        
        # 4. Создание заказа
        order = await self.order_repo.create({
            "user_id": user_id,
            "total": final_total,
            "status": "pending"
        })
        
        # 5. Резервирование товаров
        await self.inventory_service.reserve(items)
        
        # 6. Отправка уведомлений
        await self.notification_service.send_order_confirmation(order)
        
        return order
```

#### Пример 2: Аналитика пользователя
```python
class AnalyticsService:
    async def get_user_stats(self, user_id: int):
        # Параллельные запросы
        orders, reviews, wishlist = await asyncio.gather(
            self.order_repo.count_by_user(user_id),
            self.review_repo.count_by_user(user_id),
            self.wishlist_repo.get_by_user(user_id)
        )
        
        # Кеширование результата
        stats = {
            "total_orders": orders,
            "total_reviews": reviews,
            "wishlist_items": len(wishlist),
            "loyalty_points": await self.calculate_loyalty(user_id)
        }
        
        await self.cache.set(f"user_stats:{user_id}", stats, ttl=3600)
        return stats
```

---

## 📌 Слайд 7: Уровень данных - Примеры реализации

### Repository Pattern

**Преимущества:**
- 🔄 Легкая замена БД (PostgreSQL → MongoDB)
- 🧪 Простое тестирование (mock repository)
- 📦 Переиспользование запросов

### Базовый Generic Repository

```python
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> Optional[T]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, data: dict) -> T:
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def update(self, id: int, data: dict) -> Optional[T]:
        instance = await self.get(id)
        if not instance:
            return None
        
        for key, value in data.items():
            setattr(instance, key, value)
        
        await self.db.commit()
        await self.db.refresh(instance)
        return instance
    
    async def delete(self, id: int) -> bool:
        instance = await self.get(id)
        if not instance:
            return False
        
        await self.db.delete(instance)
        await self.db.commit()
        return True
```

### Специализированный Repository

```python
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[User]:
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()
    
    async def search(self, query: str) -> List[User]:
        result = await self.db.execute(
            select(User).where(
                User.username.ilike(f"%{query}%") |
                User.email.ilike(f"%{query}%")
            )
        )
        return result.scalars().all()
```

### Работа с транзакциями

```python
class OrderRepository:
    async def create_order_with_items(
        self, 
        order_data: dict, 
        items: List[dict]
    ):
        async with self.db.begin():  # Транзакция
            # Создаем заказ
            order = Order(**order_data)
            self.db.add(order)
            await self.db.flush()  # Получаем ID
            
            # Создаем позиции заказа
            for item_data in items:
                item = OrderItem(**item_data, order_id=order.id)
                self.db.add(item)
            
            # Обновляем остатки
            for item_data in items:
                product = await self.db.get(Product, item_data['product_id'])
                product.stock -= item_data['quantity']
            
            await self.db.commit()
            return order
```


---

## 📌 Слайд 8: Аутентификация и авторизация - Актуальность

### Почему это критично для высоконагруженных систем?

**Статистика атак:**
- 🔴 81% взломов связаны со слабыми паролями
- 🔴 43% кибератак направлены на малый бизнес
- 🔴 95% утечек данных можно было предотвратить

**Последствия отсутствия безопасности:**
```
Нет аутентификации → Любой может получить доступ
Нет авторизации → Пользователь видит чужие данные
Слабое шифрование → Утечка паролей
Нет rate limiting → DDoS атаки
```

### Разница между Authentication и Authorization

```
┌─────────────────────────────────────────────────────┐
│  AUTHENTICATION (Аутентификация)                    │
│  "Кто ты?"                                          │
│  ✓ Проверка логина/пароля                           │
│  ✓ Проверка токена                                  │
│  ✓ Биометрия, 2FA                                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  AUTHORIZATION (Авторизация)                        │
│  "Что ты можешь делать?"                            │
│  ✓ Проверка прав доступа                            │
│  ✓ Роли (admin, user, guest)                        │
│  ✓ Permissions (read, write, delete)                │
└─────────────────────────────────────────────────────┘
```

### Примеры из реальной жизни

**Аутентификация:**
- Вход в Instagram по логину/паролю
- Face ID на iPhone
- Код из SMS

**Авторизация:**
- Админ может удалять посты, обычный пользователь - нет
- Премиум подписка дает доступ к эксклюзивному контенту
- Модератор может банить пользователей

---

## 📌 Слайд 9: Методы аутентификации

### 1. HTTP Basic Authentication
```
Клиент отправляет: Authorization: Basic base64(username:password)
Сервер проверяет: декодирует и сравнивает с БД
```

**Плюсы:** Простота  
**Минусы:** Небезопасно без HTTPS, пароль в каждом запросе

### 2. Session-Based Authentication
```
1. Пользователь логинится → Сервер создает сессию
2. Сервер отправляет session_id в cookie
3. Клиент отправляет cookie в каждом запросе
4. Сервер проверяет session_id в хранилище (Redis)
```

**Плюсы:** Безопасно, можно отозвать сессию  
**Минусы:** Не подходит для микросервисов, нужно хранилище

### 3. Token-Based Authentication (JWT)
```
1. Пользователь логинится → Сервер создает JWT токен
2. Клиент сохраняет токен (localStorage/cookie)
3. Клиент отправляет: Authorization: Bearer <token>
4. Сервер проверяет подпись токена
```

**Плюсы:** Stateless, подходит для микросервисов  
**Минусы:** Нельзя отозвать до истечения срока

### 4. OAuth 2.0
```
1. Пользователь нажимает "Войти через Google"
2. Редирект на Google → пользователь разрешает доступ
3. Google возвращает authorization code
4. Сервер обменивает code на access token
5. Используем token для доступа к API Google
```

**Плюсы:** Не нужно хранить пароли, удобно для пользователей  
**Минусы:** Сложная реализация

### Сравнительная таблица

| Метод | Безопасность | Сложность | Stateless | Для микросервисов |
|-------|--------------|-----------|-----------|-------------------|
| Basic Auth | ⭐ | ⭐ | ✅ | ❌ |
| Session | ⭐⭐⭐ | ⭐⭐ | ❌ | ❌ |
| JWT | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ | ✅ |
| OAuth2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | ✅ |

---

## 📌 Слайд 10: HTTP Basic Auth - Применение

### Когда использовать?

✅ **Подходит для:**
- Внутренние API (не публичные)
- Простые скрипты и CLI инструменты
- Прототипы и MVP
- Защита админ-панелей

❌ **Не подходит для:**
- Публичные API
- Мобильные приложения
- Веб-приложения с множеством пользователей

### Как работает?

```
1. Клиент отправляет запрос без авторизации
   GET /api/users

2. Сервер отвечает 401 Unauthorized
   WWW-Authenticate: Basic realm="API"

3. Клиент отправляет credentials
   Authorization: Basic dXNlcjpwYXNzd29yZA==
   (base64 кодировка "user:password")

4. Сервер декодирует и проверяет
   - Декодирует base64
   - Сравнивает с БД
   - Возвращает 200 OK или 401
```

### Безопасность

⚠️ **Важно:**
- Всегда использовать HTTPS
- Пароль передается в каждом запросе
- Base64 - это НЕ шифрование, а кодировка

```python
# Декодирование Basic Auth
import base64

auth_header = "Basic dXNlcjpwYXNzd29yZA=="
encoded = auth_header.split(" ")[1]
decoded = base64.b64decode(encoded).decode()
username, password = decoded.split(":")
# username = "user", password = "password"
```

---

## 📌 Слайд 11: HTTP Basic Auth - Пример в FastAPI

### Простая реализация

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

# Хардкод для примера (в реальности - БД)
USERS = {
    "admin": "secret123",
    "user": "password456"
}

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    # Получаем username и password из заголовка
    username = credentials.username
    password = credentials.password
    
    # Проверяем существование пользователя
    if username not in USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Безопасное сравнение паролей (защита от timing attacks)
    correct_password = USERS[username]
    if not secrets.compare_digest(password, correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return username

@app.get("/")
def public_endpoint():
    return {"message": "Public endpoint - no auth required"}

@app.get("/protected")
def protected_endpoint(username: str = Depends(verify_credentials)):
    return {"message": f"Hello, {username}! This is protected."}

@app.get("/admin")
def admin_endpoint(username: str = Depends(verify_credentials)):
    if username != "admin":
        raise HTTPException(403, "Admin access required")
    return {"message": "Admin panel"}
```

### Реализация с БД

```python
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_from_db(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

async def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = await get_user_from_db(credentials.username, db)
    
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    if not await verify_password(credentials.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    
    return user

@app.get("/me")
async def get_current_user(user: User = Depends(authenticate_user)):
    return {
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    }
```

### Тестирование через curl

```bash
# Без авторизации - получим 401
curl http://localhost:8000/protected

# С авторизацией
curl -u admin:secret123 http://localhost:8000/protected

# Или с заголовком
curl -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz" http://localhost:8000/protected
```


---

## 📌 Слайд 12: OAuth2 - Применение

### Что такое OAuth 2.0?

**OAuth 2.0** - это протокол авторизации, который позволяет приложениям получать ограниченный доступ к ресурсам пользователя без передачи пароля.

### Реальные примеры

```
"Войти через Google" → OAuth 2.0
"Войти через Facebook" → OAuth 2.0
"Войти через GitHub" → OAuth 2.0
Telegram Bot API → OAuth 2.0
```

### Роли в OAuth 2.0

```
┌─────────────────────────────────────────────────────┐
│  Resource Owner (Владелец ресурса)                  │
│  Пользователь, который владеет данными              │
│  Пример: Вы, владелец аккаунта Google               │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Client (Клиент)                                    │
│  Приложение, которое хочет получить доступ          │
│  Пример: Ваше веб-приложение                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Authorization Server (Сервер авторизации)          │
│  Выдает токены после аутентификации                 │
│  Пример: accounts.google.com                        │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Resource Server (Сервер ресурсов)                  │
│  Хранит защищенные данные                           │
│  Пример: Gmail API, Google Drive API               │
└─────────────────────────────────────────────────────┘
```

### Типы OAuth 2.0 Flow

#### 1. Authorization Code Flow (самый безопасный)
```
Используется для: Веб-приложения с backend
Шаги:
1. Редирект на сервер авторизации
2. Пользователь логинится и разрешает доступ
3. Получаем authorization code
4. Обмениваем code на access token (на backend)
5. Используем token для API запросов
```

#### 2. Implicit Flow (устаревший)
```
Используется для: SPA без backend (НЕ РЕКОМЕНДУЕТСЯ)
Проблема: Token виден в URL
```

#### 3. Client Credentials Flow
```
Используется для: Сервер-сервер коммуникация
Пример: Ваш backend → API другого сервиса
```

#### 4. Password Flow (устаревший)
```
Используется для: Доверенные приложения
Проблема: Передача пароля третьей стороне
```

### Когда использовать OAuth 2.0?

✅ **Подходит для:**
- "Войти через..." (Social Login)
- Интеграция с внешними API (Google, GitHub, Stripe)
- Делегирование доступа (приложение получает доступ к вашим данным)

❌ **Не подходит для:**
- Простая аутентификация username/password
- Внутренние API без внешних интеграций

---

## 📌 Слайд 13: OAuth2 - Пример в FastAPI

### OAuth2 с Password Flow (для собственного API)

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# OAuth2 схема - указываем URL для получения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Фейковая БД
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    # В реальности здесь проверка JWT
    user = get_user(fake_users_db, token)
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(400, "Inactive user")
    return current_user

# Эндпоинт для получения токена
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(400, "Incorrect username or password")
    
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    
    if not hashed_password == user.hashed_password:
        raise HTTPException(400, "Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}

# Защищенный эндпоинт
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/items")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token, "items": ["item1", "item2"]}
```

### Интеграция с Google OAuth

```python
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get('/login/google')
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/google')
async def auth_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    # Создаем или обновляем пользователя в БД
    user = await create_or_update_user(user_info)
    
    # Создаем JWT токен для нашего приложения
    access_token = create_access_token(user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## 📌 Слайд 14: JWT (JSON Web Token) - Применение

### Что такое JWT?

**JWT** - это компактный, URL-безопасный способ передачи информации между сторонами в виде JSON объекта.

### Структура JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

├─────────── HEADER ──────────┤├────────── PAYLOAD ─────────┤├─── SIGNATURE ───┤
```

#### 1. Header (Заголовок)
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

#### 2. Payload (Полезная нагрузка)
```json
{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622,
  "role": "admin"
}
```

#### 3. Signature (Подпись)
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret_key
)
```

### Как работает JWT?

```
1. Пользователь логинится (POST /login)
   ↓
2. Сервер проверяет credentials
   ↓
3. Сервер создает JWT токен
   {
     "user_id": 123,
     "username": "john",
     "exp": 1234567890
   }
   ↓
4. Сервер подписывает токен секретным ключом
   ↓
5. Клиент получает токен и сохраняет (localStorage)
   ↓
6. Клиент отправляет токен в каждом запросе
   Authorization: Bearer <token>
   ↓
7. Сервер проверяет подпись токена
   ↓
8. Если подпись валидна → доступ разрешен
```

### Преимущества JWT

✅ **Stateless** - не нужно хранить сессии на сервере  
✅ **Масштабируемость** - подходит для микросервисов  
✅ **Кросс-доменность** - работает между разными доменами  
✅ **Мобильные приложения** - удобно для iOS/Android  
✅ **Производительность** - не нужны запросы к БД для проверки

### Недостатки JWT

❌ **Нельзя отозвать** - токен валиден до истечения срока  
❌ **Размер** - больше, чем session ID  
❌ **Безопасность** - если токен украден, его можно использовать

### Решения проблем

```python
# Проблема: Нельзя отозвать токен
# Решение: Blacklist токенов в Redis
blacklist = redis.Redis()

def is_token_blacklisted(token: str) -> bool:
    return blacklist.exists(f"blacklist:{token}")

def revoke_token(token: str):
    # Добавляем в blacklist до истечения срока
    exp = decode_token(token)['exp']
    ttl = exp - time.time()
    blacklist.setex(f"blacklist:{token}", int(ttl), "1")

# Проблема: Токен украден
# Решение: Refresh tokens
# Access token - короткий срок (15 минут)
# Refresh token - длинный срок (7 дней)
```

---

## 📌 Слайд 15: JWT - Пример в FastAPI

### Полная реализация JWT аутентификации

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

# Конфигурация
SECRET_KEY = "your-secret-key-keep-it-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Фейковая БД
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

# Утилиты
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Эндпоинты
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
```

### Тестирование JWT

```bash
# 1. Получить токен
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=johndoe&password=secret"

# Ответ:
# {"access_token":"eyJhbGc...","token_type":"bearer"}

# 2. Использовать токен
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGc..."

# Ответ:
# {"username":"johndoe","email":"johndoe@example.com",...}
```


---

## 📌 Слайд 16: Авторизация (Permissions & Roles)

### Разница между Authentication и Authorization

```
Authentication (Аутентификация)     Authorization (Авторизация)
         ↓                                    ↓
    "Кто ты?"                           "Что можешь?"
         ↓                                    ↓
  Проверка логина/пароля              Проверка прав доступа
         ↓                                    ↓
    user = get_user()                  if user.role == "admin"
```

### Модели авторизации

#### 1. Role-Based Access Control (RBAC)
```python
# Роли
ROLES = {
    "admin": ["read", "write", "delete", "manage_users"],
    "moderator": ["read", "write", "delete"],
    "user": ["read", "write"],
    "guest": ["read"]
}

# Проверка
def has_permission(user_role: str, permission: str) -> bool:
    return permission in ROLES.get(user_role, [])
```

#### 2. Permission-Based Access Control
```python
# Права напрямую у пользователя
user.permissions = ["posts:read", "posts:write", "comments:delete"]

# Проверка
def can_user(user: User, action: str, resource: str) -> bool:
    permission = f"{resource}:{action}"
    return permission in user.permissions
```

#### 3. Attribute-Based Access Control (ABAC)
```python
# Проверка на основе атрибутов
def can_edit_post(user: User, post: Post) -> bool:
    # Автор может редактировать
    if post.author_id == user.id:
        return True
    
    # Админ может редактировать всё
    if user.role == "admin":
        return True
    
    # Модератор может редактировать опубликованные посты
    if user.role == "moderator" and post.status == "published":
        return True
    
    return False
```

### Реализация RBAC в FastAPI

```python
from enum import Enum
from fastapi import Depends, HTTPException

class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

class User(BaseModel):
    username: str
    role: Role

# Dependency для проверки роли
def require_role(required_role: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        role_hierarchy = {
            Role.ADMIN: 4,
            Role.MODERATOR: 3,
            Role.USER: 2,
            Role.GUEST: 1
        }
        
        if role_hierarchy[current_user.role] < role_hierarchy[required_role]:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    return role_checker

# Использование
@app.get("/admin/users")
async def get_all_users(user: User = Depends(require_role(Role.ADMIN))):
    return {"users": [...]}

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(require_role(Role.MODERATOR))
):
    return {"message": "Post deleted"}

@app.get("/posts")
async def get_posts(user: User = Depends(require_role(Role.GUEST))):
    return {"posts": [...]}
```

### Реализация Permission-Based

```python
from typing import List

class Permission(str, Enum):
    READ_POSTS = "posts:read"
    WRITE_POSTS = "posts:write"
    DELETE_POSTS = "posts:delete"
    MANAGE_USERS = "users:manage"

class User(BaseModel):
    username: str
    permissions: List[Permission]

def require_permission(required_permission: Permission):
    def permission_checker(current_user: User = Depends(get_current_user)):
        if required_permission not in current_user.permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing permission: {required_permission}"
            )
        return current_user
    return permission_checker

@app.post("/posts")
async def create_post(
    post: PostCreate,
    user: User = Depends(require_permission(Permission.WRITE_POSTS))
):
    return {"message": "Post created"}

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(require_permission(Permission.DELETE_POSTS))
):
    return {"message": "Post deleted"}
```

### Комбинированный подход (Роли + Права)

```python
# Роли с правами
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_POSTS,
        Permission.WRITE_POSTS,
        Permission.DELETE_POSTS,
        Permission.MANAGE_USERS
    ],
    Role.MODERATOR: [
        Permission.READ_POSTS,
        Permission.WRITE_POSTS,
        Permission.DELETE_POSTS
    ],
    Role.USER: [
        Permission.READ_POSTS,
        Permission.WRITE_POSTS
    ],
    Role.GUEST: [
        Permission.READ_POSTS
    ]
}

def get_user_permissions(user: User) -> List[Permission]:
    return ROLE_PERMISSIONS.get(user.role, [])

def has_permission(user: User, permission: Permission) -> bool:
    user_permissions = get_user_permissions(user)
    return permission in user_permissions

# Dependency
def require_any_permission(*required_permissions: Permission):
    def checker(current_user: User = Depends(get_current_user)):
        user_perms = get_user_permissions(current_user)
        
        if not any(perm in user_perms for perm in required_permissions):
            raise HTTPException(403, "Insufficient permissions")
        
        return current_user
    return checker

@app.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    post: PostUpdate,
    user: User = Depends(require_any_permission(
        Permission.WRITE_POSTS,
        Permission.DELETE_POSTS
    ))
):
    return {"message": "Post updated"}
```

---

## 📌 Слайд 17: Middleware и CORS

### Что такое Middleware?

**Middleware** - это функция, которая выполняется перед/после обработки каждого запроса.

```
Request → Middleware 1 → Middleware 2 → Endpoint Handler
                                              ↓
Response ← Middleware 1 ← Middleware 2 ← Return
```

### Примеры использования Middleware

1. **Логирование запросов**
2. **Измерение времени выполнения**
3. **Добавление заголовков безопасности**
4. **CORS (Cross-Origin Resource Sharing)**
5. **Rate Limiting**
6. **Аутентификация**

### Создание собственного Middleware

```python
from fastapi import FastAPI, Request
import time
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # ДО обработки запроса
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url}")
    
    # Обработка запроса
    response = await call_next(request)
    
    # ПОСЛЕ обработки запроса
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Response: {response.status_code} ({process_time:.2f}s)")
    
    return response

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

### CORS (Cross-Origin Resource Sharing)

**Проблема:**
```
Frontend (http://localhost:3000) → Backend (http://localhost:8000)
                                         ↓
                                    ❌ CORS Error
```

**Решение:**
```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://myapp.com"       # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Authorization, Content-Type, etc.
)

# Или разрешить всё (только для разработки!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting Middleware

```python
from fastapi import HTTPException
from collections import defaultdict
import time

# Хранилище запросов
request_counts = defaultdict(list)
RATE_LIMIT = 10  # запросов
TIME_WINDOW = 60  # секунд

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Очистка старых запросов
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < TIME_WINDOW
    ]
    
    # Проверка лимита
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )
    
    # Добавление текущего запроса
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response
```

### Популярные сторонние Middleware

```python
# 1. Gzip сжатие
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. Trusted Host (защита от Host header атак)
from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# 3. HTTPS Redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)

# 4. Sentry (мониторинг ошибок)
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

sentry_sdk.init(dsn="your-sentry-dsn")
app.add_middleware(SentryAsgiMiddleware)
```

---

## 📌 Слайд 18: Автоматизированное тестирование FastAPI

### Зачем нужны тесты?

```
Без тестов:
Изменил код → Запустил вручную → Проверил 5 эндпоинтов → 30 минут

С тестами:
Изменил код → pytest → Проверил 100 эндпоинтов → 5 секунд ✅
```

### Типы тестов

```
┌─────────────────────────────────────────────────────┐
│  Unit Tests (Модульные)                             │
│  Тестируют отдельные функции                        │
│  Пример: test_hash_password()                       │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  Integration Tests (Интеграционные)                 │
│  Тестируют взаимодействие компонентов               │
│  Пример: test_create_user_in_db()                   │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│  End-to-End Tests (E2E)                             │
│  Тестируют весь flow                                │
│  Пример: test_user_registration_flow()              │
└─────────────────────────────────────────────────────┘
```

### Настройка тестирования

```bash
# Установка зависимостей
pip install pytest pytest-asyncio httpx
```

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base

# Тестовая БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

### Примеры тестов

```python
# test_users.py
def test_create_user(client):
    response = client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "secret"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_get_user(client):
    # Создаем пользователя
    create_response = client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "secret"}
    )
    user_id = create_response.json()["id"]
    
    # Получаем пользователя
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_get_nonexistent_user(client):
    response = client.get("/users/999")
    assert response.status_code == 404

def test_login(client):
    # Создаем пользователя
    client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com", "password": "secret"}
    )
    
    # Логинимся
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_endpoint(client):
    # Без токена
    response = client.get("/users/me")
    assert response.status_code == 401
    
    # С токеном
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "secret"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

### Тестирование через Swagger UI

```
1. Откройте http://localhost:8000/docs
2. Нажмите "Try it out" на эндпоинте
3. Заполните параметры
4. Нажмите "Execute"
5. Проверьте Response
```

### Автоматизация с GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: pytest -v
```

---

## 🎯 Заключение

### Что мы изучили:

1. ✅ **Маршрутизация** - APIRouter для модульной структуры
2. ✅ **Архитектура** - разделение на слои (API, Service, Repository)
3. ✅ **Аутентификация** - Basic Auth, OAuth2, JWT
4. ✅ **Авторизация** - RBAC, Permissions
5. ✅ **Middleware** - CORS, Rate Limiting, Logging
6. ✅ **Тестирование** - Unit, Integration, E2E тесты

### Лучшие практики для высоконагруженных систем:

- 🚀 Используйте async/await для I/O операций
- 🔐 Всегда используйте HTTPS в продакшене
- 📊 Логируйте все запросы и ошибки
- 🧪 Покрывайте код тестами (минимум 80%)
- 🔄 Используйте кеширование (Redis)
- 📈 Мониторьте производительность (Prometheus, Grafana)
- 🛡️ Защищайтесь от атак (Rate Limiting, CORS, SQL Injection)

### Дополнительные материалы:

- 📚 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 📚 [JWT.io](https://jwt.io/)
- 📚 [OAuth 2.0 Simplified](https://www.oauth.com/)
- 📚 [Python Testing with pytest](https://docs.pytest.org/)
