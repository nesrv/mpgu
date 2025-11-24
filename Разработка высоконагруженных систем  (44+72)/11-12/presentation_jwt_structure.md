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

## Слайд 4: Установка зависимостей
```bash
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
```
- python-jose — работа с JWT
- passlib — хеширование паролей
- python-multipart — обработка форм

## Слайд 5: Конфигурация JWT
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Слайд 6: Хеширование паролей
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
```

## Слайд 7: Эндпоинт авторизации
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Слайд 8: Проверка токена
```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username
```

## Слайд 9: Защищенные эндпоинты
```python
@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

@app.get("/items/")
async def read_items(current_user: str = Depends(get_current_user)):
    return [{"item_id": 1, "owner": current_user}]
```
- Используйте Depends(get_current_user) для защиты эндпоинтов

## Слайд 10: Лучшие практики
- Храните SECRET_KEY в переменных окружения
- Используйте HTTPS для передачи токенов
- Короткое время жизни токенов
- Реализуйте refresh tokens
- Добавьте blacklist при logout
- Валидируйте все claims в payload
