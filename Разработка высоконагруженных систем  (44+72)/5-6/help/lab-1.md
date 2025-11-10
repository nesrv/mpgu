# Лабораторная работа "Изучение Pydantic для RESTful API"

## Описание

В этой лабораторной работе вы создадите RESTful API для управления студентами и курсами.

**Предметная область:**
- **Student** (Студент) - информация о студентах
- **Course** (Курс) - информация о курсах

## Теория

Pydantic:


Пример 1. Простая модель

```py
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# Создание экземпляра
user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())  # Конвертация в dict

```

Описание


Пример 2. Простая модель

```py
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int | None = None

# Создание экземпляра
user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())  # Конвертация в dict

```


Описание


Пример 3. 

```py
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int | None = None
```

Описание

Детальная настройка атрибутов и класс Field

Для более детальной настройки атрибутов модели применяется класс pydantic.Field. 
Например, он позволяет задать значение по умолчанию и правила валдации значений с помощью следующих параметров конструктора:

* default: устанавливает значение по умолчанию
* min_length: устанавливает минимальное количество символов в значении параметра
* max_length: устанавливает максимальное количество символов в значении параметра
* pattern: устанавливает регулярное выражение, которому должно соответствовать значение параметра
* lt: значение параметра должно быть меньше определенного значения
* le: значение параметра должно быть меньше или равно определенному значению
* gt: значение параметра должно быть больше определенного значения
* ge: значение параметра должно быть больше или равно определенному значению


Пример 4. Модель с валидацией

```py
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int = Field(gt=0, description="ID должен быть положительным")
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=120, default=None)

# Использование
user = User(id=1, name="John", email="john@example.com")
```

Описание


Пример 5. 

```py
class Person(BaseModel):
    name: str
    languages: list = []
```





## 1. Базовое использование Pydantic

### Простая модель
```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

# Создание экземпляра
user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())  # Конвертация в dict
```

### Модель с валидацией
```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int = Field(gt=0, description="ID должен быть положительным")
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=120, default=None)

# Использование
user = User(id=1, name="John", email="john@example.com")
```

## 2. FastAPI - Простой пример

### Базовое приложение
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
```

## 3. CRUD API с валидацией

### Полный пример
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

app = FastAPI(title="User API")

# Модели Pydantic
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=120)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# "База данных"
users_db = []
current_id = 1

# Эндпоинты
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global current_id
    user_data = user.model_dump()
    user_data["id"] = current_id
    users_db.append(user_data)
    current_id += 1
    return user_data

@app.get("/users/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 10):
    return users_db[skip:skip + limit]

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## 4. Расширенная валидация Pydantic

### Кастомные валидаторы
```python
from pydantic import BaseModel, Field, validator
import re

class AdvancedUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8)
    phone: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match('^[a-zA-Z0-9_]+$', v):
            raise ValueError('Имя пользователя должно содержать только буквы, цифры и подчеркивания')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v
    
    @validator('phone')
    def phone_format(cls, v):
        if v and not re.match(r'^\+?1?\d{9,15}$', v):
            raise ValueError('Неверный формат телефона')
        return v
```

## 5. Сложные модели и отношения

### Вложенные модели
```python
from typing import List, Optional
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class Product(BaseModel):
    id: int
    name: str
    price: float

class OrderItem(BaseModel):
    product: Product
    quantity: int = Field(ge=1)

class Order(BaseModel):
    id: int
    user_id: int
    items: List[OrderItem]
    shipping_address: Address
    total: float
    
    @validator('total')
    def validate_total(cls, v, values):
        if 'items' in values:
            calculated_total = sum(item.product.price * item.quantity for item in values['items'])
            if abs(v - calculated_total) > 0.01:
                raise ValueError('Общая сумма не соответствует стоимости товаров')
        return v
```

## 6. FastAPI с зависимостями

### Dependency Injection
```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Логика аутентификации
    user = authenticate_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/items/")
def create_item(
    item: Item,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Логика создания item
    return {"item": item, "user": current_user}
```

## 7. Обработка ошибок и middleware

### Кастомные обработчики ошибок
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        },
    )

class CustomException(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=400,
        content={"message": exc.message},
    )
```

## 8. Фоновые задачи и WebSockets

### Фоновые задачи + WebSockets
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel

app = FastAPI()

class Notification(BaseModel):
    message: str
    user_id: int

def send_notification(email: str, message: str):
    # Логика отправки уведомления
    print(f"Sending email to {email}: {message}")

@app.post("/notify/{user_id}")
def notify_user(
    user_id: int,
    notification: Notification,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        send_notification, 
        f"user{user_id}@example.com", 
        notification.message
    )
    return {"message": "Notification sent"}

# WebSocket
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

## 9. Тестирование FastAPI приложения

### Тесты с pytest
```python
from fastapi.testclient import TestClient
import pytest
from main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data

def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
```

## 10. Продвинутые фичи Pydantic

### Generic модели и конфигурация
```python
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'  # Запрещает дополнительные поля
    )
    
    id: int
    name: str
    email: str

# Использование
users_response = PaginatedResponse[User](
    items=[User(id=1, name="John", email="john@example.com")],
    total=1,
    page=1,
    size=10,
    pages=1
)
```

## 11. Миграция на Pydantic v2

### Основные изменения
```python
# Pydantic v1
class UserV1(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# Pydantic v2
class UserV2(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,  # замена orm_mode
        populate_by_name=True,  # замена allow_population_by_field_name
        str_strip_whitespace=True
    )

# Методы v1 vs v2
user_v1.dict()          # -> user_v2.model_dump()
user_v1.json()          # -> user_v2.model_dump_json()
UserV1.parse_obj()      # -> UserV2.model_validate()
UserV1.update_forward_refs()  # -> UserV2.model_rebuild()
```

## Быстрые команды для запуска

### Установка
```bash
pip install "fastapi[all]" pydantic
```

