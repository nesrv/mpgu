# Презентация: JWT-аутентификация в FastAPI

## Слайд 1: Титульный
- Заголовок: JWT-аутентификация в FastAPI микросервисах
- Подзаголовок: Проектирование и разработка высоконагруженных сервисов
- Автор/Дата

## Слайд 2: Проблемы традиционной аутентификации
- **Session-based аутентификация:**
  - Сервер хранит сессии в памяти/БД
  - Проблемы масштабирования (sticky sessions)
  - Сложность в микросервисной архитектуре
  - Необходимость синхронизации между серверами
- **Cookies:**
  - CSRF уязвимости
  - Ограничения кросс-доменных запросов
  - Проблемы с мобильными приложениями

## Слайд 3: Что такое JWT?
- **Определение:** JSON Web Token (RFC 7519) — открытый стандарт для безопасной передачи информации между сторонами в виде JSON-объекта
- **Структура токена:** `xxxxx.yyyyy.zzzzz`
  - **Header** — метаданные (алгоритм подписи, тип токена)
  - **Payload** — полезная нагрузка (claims/утверждения)
  - **Signature** — цифровая подпись для проверки целостности
- **Пример:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

## Слайд 4: Структура JWT подробно
- **Header (заголовок):**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```
- **Payload (полезная нагрузка):**
```json
{
  "sub": "user123",
  "name": "John Doe",
  "iat": 1516239022,
  "exp": 1516242622,
  "role": "admin"
}
```
- **Стандартные claims:** sub, iss, aud, exp, nbf, iat, jti
- **Signature:** HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)

## Слайд 5: Преимущества JWT
- **Stateless:** сервер не хранит состояние сессий
- **Масштабируемость:** легко горизонтальное масштабирование
- **Микросервисы:** один токен для всех сервисов
- **Кросс-доменность:** работает между разными доменами
- **Мобильные приложения:** нет зависимости от cookies
- **Производительность:** не требуется обращение к БД для проверки
- **Декодируемость:** payload читается без секрета
- **Компактность:** передается через URL, POST, HTTP Header

## Слайд 6: Алгоритмы подписи JWT
- **Симметричные (HMAC):**
  - HS256 (HMAC + SHA256) — самый популярный
  - HS384, HS512
  - Один секретный ключ для подписи и проверки
  - Быстрые, но требуют защищенной передачи ключа
- **Асимметричные (RSA, ECDSA):**
  - RS256 (RSA + SHA256)
  - ES256 (ECDSA + SHA256)
  - Приватный ключ для подписи, публичный для проверки
  - Безопаснее для распределенных систем
- **Выбор алгоритма:** HS256 для простых случаев, RS256 для микросервисов

## Слайд 7: Установка зависимостей
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
```
- **fastapi** — веб-фреймворк
- **uvicorn** — ASGI сервер
- **python-jose** — создание и проверка JWT
- **passlib** — хеширование паролей (bcrypt)
- **python-multipart** — обработка форм OAuth2

## Слайд 8: Структура проекта
```
project/
├── main.py              # Точка входа
├── auth/
│   ├── __init__.py
│   ├── jwt_handler.py   # Работа с JWT
│   ├── hash.py          # Хеширование паролей
│   └── dependencies.py  # Зависимости FastAPI
├── models/
│   └── user.py          # Модели пользователей
├── routes/
│   ├── auth.py          # Эндпоинты авторизации
│   └── users.py         # Защищенные эндпоинты
└── config.py            # Конфигурация
```

## Слайд 9: Конфигурация (config.py)
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
settings = Settings()
```
- Используйте переменные окружения
- Никогда не коммитьте SECRET_KEY в репозиторий
- Генерация ключа: `openssl rand -hex 32`
```

## Слайд 10: Хеширование паролей (auth/hash.py)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)
```
- **bcrypt** — стойкий к brute-force атакам
- Автоматическая соль (salt)
- Настраиваемая сложность (rounds)
```

## Слайд 11: Создание JWT токенов (auth/jwt_handler.py)
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import settings

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Создание access токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Создание refresh токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

## Слайд 12: Модель пользователя (models/user.py)
```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
```

## Слайд 13: Эндпоинт авторизации (routes/auth.py)
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_handler import create_access_token, create_refresh_token
from auth.hash import verify_password
from models.user import Token

router = APIRouter(prefix="/auth", tags=["auth"])

# Имитация БД
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$...",  # bcrypt hash
        "disabled": False,
    }
}

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

## Слайд 14: Проверка токена (auth/dependencies.py)
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config import settings
from models.user import TokenData, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Получение пользователя из БД
    user = get_user_from_db(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

## Слайд 15: Защищенные эндпоинты (routes/users.py)
```python
from fastapi import APIRouter, Depends
from auth.dependencies import get_current_active_user
from models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получить информацию о текущем пользователе"""
    return current_user

@router.get("/me/items")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    """Получить элементы пользователя"""
    return [{"item_id": 1, "owner": current_user.username}]

@router.put("/me")
async def update_user(user_update: dict, current_user: User = Depends(get_current_active_user)):
    """Обновить профиль пользователя"""
    return {"message": "User updated", "user": current_user.username}
```
- Используйте `Depends(get_current_active_user)` для защиты эндпоинтов

## Слайд 16: Главный файл приложения (main.py)
```python
from fastapi import FastAPI
from routes import auth, users

app = FastAPI(
    title="JWT Authentication API",
    description="FastAPI микросервис с JWT аутентификацией",
    version="1.0.0"
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "JWT Authentication Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Слайд 17: Refresh Token механизм
```python
@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        username = payload.get("sub")
        # Проверка токена в whitelist/blacklist
        
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```
- Access token — короткий срок (15-30 мин)
- Refresh token — длинный срок (7-30 дней)

## Слайд 18: Тестирование API
```bash
# Запуск сервера
uvicorn main:app --reload

# Получение токена
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"

# Ответ
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}

# Использование токена
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGc..."
```

## Слайд 19: Безопасность и лучшие практики
- **Хранение SECRET_KEY:**
  - Переменные окружения (.env)
  - Secrets Manager (AWS, Azure, GCP)
  - Никогда в коде!
- **HTTPS обязателен** — токены передаются в открытом виде
- **Короткое время жизни** access токенов (15-30 мин)
- **Refresh tokens** для обновления без повторной авторизации
- **Token Blacklist** при logout (Redis)
- **Не храните чувствительные данные** в payload
- **Валидация всех claims:** exp, iat, nbf, aud, iss
- **Rate limiting** на эндпоинт login
- **CORS** настройки для фронтенда

## Слайд 20: Продвинутые возможности
- **Role-Based Access Control (RBAC):**
```python
def require_role(required_role: str):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: User = Depends(require_role("admin"))):
    return {"message": "User deleted"}
```
- **Token Blacklist (Redis):**
```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # Добавить токен в blacklist до истечения срока
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    exp = payload.get("exp")
    ttl = exp - datetime.utcnow().timestamp()
    redis_client.setex(f"blacklist:{token}", int(ttl), "1")
    return {"message": "Successfully logged out"}
```

## Слайд 21: Заключение
- **JWT** — современный стандарт аутентификации для API
- **FastAPI** предоставляет удобные инструменты для работы с JWT
- **Stateless** архитектура идеальна для микросервисов
- **Безопасность** требует правильной реализации:
  - HTTPS
  - Короткие токены
  - Refresh механизм
  - Blacklist
- **Масштабируемость** — легко добавлять новые сервисы

**Полезные ресурсы:**
- https://jwt.io — декодирование и отладка JWT
- https://fastapi.tiangolo.com/tutorial/security/
- RFC 7519 — спецификация JWT
