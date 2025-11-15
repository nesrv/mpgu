# Лабораторная работа: FastAPI - Маршрутизация, Архитектура и Безопасность

## 🎯 Цель работы
Изучить принципы построения масштабируемых API с использованием FastAPI, включая маршрутизацию, архитектурные паттерны и методы аутентификации.

## 📋 Исходный код

**Дан монолитный код в одном файле:**

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = None

_students: list[Student] = []

@app.get("/students")
def get_all() -> list[Student]:
    return _students

@app.get("/students/{name}")
def get_one(name: str) -> Student:
    for student in _students:
        if student.name == name:
            return student
    raise HTTPException(404, "Student not found")

@app.post("/students")
def create(student: Student) -> Student:
    _students.append(student)
    return student

@app.patch("/students/{name}")
def update(name: str, update: StudentUpdate) -> Student:
    for i, student in enumerate(_students):
        if student.name == name:
            data = student.model_dump()
            data.update(update.model_dump(exclude_unset=True))
            _students[i] = Student(**data)
            return _students[i]
    raise HTTPException(404, "Student not found")

@app.delete("/students/{name}")
def delete(name: str):
    for i, student in enumerate(_students):
        if student.name == name:
            _students.pop(i)
            return {"message": "Student deleted"}
    raise HTTPException(404, "Student not found")
```

---

## 📝 Задание 1: Маршрутизация с APIRouter

**Задача:** Разделить монолитный код на модули с использованием APIRouter.

**Структура проекта:**
```
project/
├── main.py
├── routers/
│   └── students.py
├── models/
│   └── student.py
└── services/
    └── student_service.py
```

**Решение:**

```python
# models/student.py
from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = None

# services/student_service.py
from models.student import Student, StudentUpdate

_students: list[Student] = []

def get_all() -> list[Student]:
    return _students

def get_by_name(name: str) -> Student | None:
    return next((s for s in _students if s.name == name), None)

def create(student: Student) -> Student:
    _students.append(student)
    return student

def update(name: str, data: StudentUpdate) -> Student | None:
    for i, s in enumerate(_students):
        if s.name == name:
            updated = s.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _students[i] = Student(**updated)
            return _students[i]
    return None

def delete(name: str) -> bool:
    for i, s in enumerate(_students):
        if s.name == name:
            _students.pop(i)
            return True
    return False

# routers/students.py
from fastapi import APIRouter, HTTPException
from models.student import Student, StudentUpdate
from services import student_service as service

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
def get_all() -> list[Student]:
    return service.get_all()

@router.get("/{name}")
def get_one(name: str) -> Student:
    student = service.get_by_name(name)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/")
def create(student: Student) -> Student:
    return service.create(student)

@router.patch("/{name}")
def update(name: str, data: StudentUpdate) -> Student:
    student = service.update(name, data)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.delete("/{name}")
def delete(name: str):
    if not service.delete(name):
        raise HTTPException(404, "Student not found")
    return {"message": "Deleted"}

# main.py
from fastapi import FastAPI
from routers import students

app = FastAPI()
app.include_router(students.router)
```

---

## 📝 Задание 2: Layered Architecture

**Задача:** Реорганизовать код согласно слоистой архитектуре:
- API Layer (Routers) ← HTTP
- Service Layer (Business) ← Логика
- Repository Layer (Data) ← БД
- Database ← Данные

**Структура проекта:**
```
project/
├── main.py
├── api/
│   └── students.py
├── services/
│   └── student_service.py
├── repositories/
│   └── student_repository.py
├── models/
│   └── student.py
└── schemas/
    └── student.py
```

**Решение:**

```python
# schemas/student.py
from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = None

# repositories/student_repository.py
from schemas.student import Student

class StudentRepository:
    def __init__(self):
        self._students: list[Student] = []
    
    def get_all(self) -> list[Student]:
        return self._students
    
    def get_by_name(self, name: str) -> Student | None:
        return next((s for s in self._students if s.name == name), None)
    
    def create(self, student: Student) -> Student:
        self._students.append(student)
        return student
    
    def update(self, name: str, data: dict) -> Student | None:
        for i, s in enumerate(self._students):
            if s.name == name:
                updated = s.model_dump()
                updated.update(data)
                self._students[i] = Student(**updated)
                return self._students[i]
        return None
    
    def delete(self, name: str) -> bool:
        for i, s in enumerate(self._students):
            if s.name == name:
                self._students.pop(i)
                return True
        return False

# services/student_service.py
from repositories.student_repository import StudentRepository
from schemas.student import Student, StudentUpdate

class StudentService:
    def __init__(self, repo: StudentRepository):
        self.repo = repo
    
    def get_all(self) -> list[Student]:
        return self.repo.get_all()
    
    def get_by_name(self, name: str) -> Student | None:
        return self.repo.get_by_name(name)
    
    def create(self, student: Student) -> Student:
        if self.repo.get_by_name(student.name):
            raise ValueError("Student exists")
        return self.repo.create(student)
    
    def update(self, name: str, data: StudentUpdate) -> Student | None:
        return self.repo.update(name, data.model_dump(exclude_unset=True))
    
    def delete(self, name: str) -> bool:
        return self.repo.delete(name)

# api/students.py
from fastapi import APIRouter, HTTPException, Depends
from schemas.student import Student, StudentUpdate
from services.student_service import StudentService
from repositories.student_repository import StudentRepository

def get_service() -> StudentService:
    return StudentService(StudentRepository())

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/")
def get_all(service: StudentService = Depends(get_service)) -> list[Student]:
    return service.get_all()

@router.get("/{name}")
def get_one(name: str, service: StudentService = Depends(get_service)) -> Student:
    student = service.get_by_name(name)
    if not student:
        raise HTTPException(404, "Not found")
    return student

@router.post("/")
def create(student: Student, service: StudentService = Depends(get_service)) -> Student:
    try:
        return service.create(student)
    except ValueError:
        raise HTTPException(400, "Student exists")

@router.patch("/{name}")
def update(name: str, data: StudentUpdate, service: StudentService = Depends(get_service)) -> Student:
    student = service.update(name, data)
    if not student:
        raise HTTPException(404, "Not found")
    return student

@router.delete("/{name}")
def delete(name: str, service: StudentService = Depends(get_service)):
    if not service.delete(name):
        raise HTTPException(404, "Not found")
    return {"message": "Deleted"}

# main.py
from fastapi import FastAPI
from api import students

app = FastAPI()
app.include_router(students.router)
```

---

## 📝 Задание 3: Подключение PostgreSQL

**Задача:** Заменить in-memory хранилище на PostgreSQL в Docker контейнере.

**Файлы конфигурации:**

```python
# database.py
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://student:password@localhost:5432/students_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    group = Column(String)
    year = Column(Integer)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```

```dockerfile
# Dockerfile
FROM postgres:15
ENV POSTGRES_DB=students_db
ENV POSTGRES_USER=student
ENV POSTGRES_PASSWORD=password
EXPOSE 5432
```

```bash
# Команды для запуска
docker build -t my-postgres .
docker run -d -p 5432:5432 my-postgres
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: students_db
      POSTGRES_USER: student
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

```txt
# requirements.txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
```

---

## 📝 Задание 4а: Dependency Injection для БД

**Теория:** Dependency Injection (DI) - паттерн, позволяющий передавать зависимости в объект извне, а не создавать их внутри объекта.

**Практика:**

```python
# repositories/student_repository.py
from sqlalchemy.orm import Session
from database import StudentModel
from schemas.student import Student

class StudentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> list[StudentModel]:
        return self.db.query(StudentModel).all()
    
    def get_by_name(self, name: str) -> StudentModel | None:
        return self.db.query(StudentModel).filter(StudentModel.name == name).first()
    
    def create(self, student: Student) -> StudentModel:
        db_student = StudentModel(**student.model_dump())
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return db_student
    
    def update(self, db_student: StudentModel, data: dict) -> StudentModel:
        for key, value in data.items():
            setattr(db_student, key, value)
        self.db.commit()
        return db_student
    
    def delete(self, db_student: StudentModel):
        self.db.delete(db_student)
        self.db.commit()

# api/students.py (обновленная)
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db

def get_repository(db: Session = Depends(get_db)):
    return StudentRepository(db)

@router.get("/")
def get_all(repo = Depends(get_repository)):
    return repo.get_all()
```

---

## 📝 Задание 4б: DI для логирования

**Задача:** Использовать DI для внедрения логгера.

```python
# utils/logger.py
import logging

class Logger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def info(self, msg: str):
        self.logger.info(msg)

def get_logger():
    return Logger()

# services/student_service.py (обновленная)
class StudentService:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger
    
    def create(self, student):
        self.logger.info(f"Creating: {student.name}")
        return self.repo.create(student)

# api/students.py (обновленная)
from utils.logger import get_logger

def get_service(repo = Depends(get_repository), logger = Depends(get_logger)):
    return StudentService(repo, logger)
```

---

## 📝 Задание 5: Basic Authentication

**Теория-шпаргалка:**
- **Basic Auth** = логин:пароль в base64 в заголовке `Authorization: Basic <encoded>`
- **Плюсы:** простота реализации
- **Минусы:** пароль передается в каждом запросе, нужен HTTPS
- **Формат:** `Authorization: Basic YWRtaW46c2VjcmV0` (admin:secret в base64)

**Задача:** Добавить базовую аутентификацию с использованием DI.

**Вариант 1: Фиксированные пользователи**
```python
# auth/basic_auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()
USERS = {"admin": "secret", "user": "pass"}

def verify_user(creds: HTTPBasicCredentials = Depends(security)):
    if creds.username not in USERS or USERS[creds.username] != creds.password:
        raise HTTPException(401, "Invalid credentials")
    return creds.username

# api/students.py (защищенные)
from auth.basic_auth import verify_user

@router.post("/")
def create(student: Student, user: str = Depends(verify_user)):
    return service.create(student)

@router.delete("/{name}")
def delete(name: str, user: str = Depends(verify_user)):
    if service.delete(name):
        return {"message": "Deleted"}
    raise HTTPException(404, "Not found")
```

**Вариант 2: Любые данные через Swagger**
```python
# auth/basic_auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_user(creds: HTTPBasicCredentials = Depends(security)):
    # Любые логин/пароль через Swagger UI
    if len(creds.username) < 3 or len(creds.password) < 3:
        raise HTTPException(401, "Username and password must be at least 3 characters")
    return creds.username

# api/students.py (защищенные)
from auth.basic_auth import verify_user

@router.post("/")
def create(student: Student, user: str = Depends(verify_user)):
    return service.create(student)

@router.delete("/{name}")
def delete(name: str, user: str = Depends(verify_user)):
    if service.delete(name):
        return {"message": "Deleted"}
    raise HTTPException(404, "Not found")
```

**Как использовать:**
1. Открыть Swagger UI: `http://localhost:8000/docs`
2. Нажать кнопку "Authorize" в правом верхнем углу
3. Ввести любой username и password (минимум 3 символа)
4. Нажать "Authorize"
5. Теперь можно вызывать защищенные эндпоинты

---

## 🎯 Самостоятельное задание: Роли пользователей

**Задача:** Добавить систему ролей в Basic Auth.

**Требования:**
1. Создать 3 роли: `admin`, `teacher`, `student`
2. Только `admin` может удалять студентов
3. `admin` и `teacher` могут создавать студентов
4. Все роли могут просматривать студентов
5. Роль определяется по username: `admin_*`, `teacher_*`, `student_*`

**Подсказка:**
```python
def get_role(username: str) -> str:
    if username.startswith("admin_"):
        return "admin"
    elif username.startswith("teacher_"):
        return "teacher"
    else:
        return "student"

def require_role(allowed_roles: list[str]):
    def role_checker(user: str = Depends(verify_user)):
        role = get_role(user)
        if role not in allowed_roles:
            raise HTTPException(403, f"Role {role} not allowed")
        return user
    return role_checker

# Использование:
@router.delete("/{name}")
def delete(name: str, user: str = Depends(require_role(["admin"]))):
    # только admin
```

**Тестирование:**
- `admin_john:pass` - может все
- `teacher_mary:pass` - может создавать, но не удалять
- `student_bob:pass` - только просмотр

**Решение:**
```python
# auth/basic_auth.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_user(creds: HTTPBasicCredentials = Depends(security)):
    if len(creds.username) < 3 or len(creds.password) < 3:
        raise HTTPException(401, "Invalid credentials")
    return creds.username

def get_role(username: str) -> str:
    if username.startswith("admin_"):
        return "admin"
    elif username.startswith("teacher_"):
        return "teacher"
    else:
        return "student"

def require_role(allowed_roles: list[str]):
    def role_checker(user: str = Depends(verify_user)):
        role = get_role(user)
        if role not in allowed_roles:
            raise HTTPException(403, f"Role {role} not allowed")
        return user
    return role_checker

# api/students.py (с ролями)
from auth.basic_auth import verify_user, require_role

@router.get("/")
def get_all(user: str = Depends(verify_user)):
    # Все могут просматривать
    return service.get_all()

@router.post("/")
def create(student: Student, user: str = Depends(require_role(["admin", "teacher"]))):
    # Только admin и teacher
    return service.create(student)

@router.delete("/{name}")
def delete(name: str, user: str = Depends(require_role(["admin"]))):
    # Только admin
    if service.delete(name):
        return {"message": "Deleted"}
    raise HTTPException(404, "Not found")
```

---

## 📝 Задание 6: JWT Authentication

**Теория-шпаргалка:**
- **JWT** = JSON Web Token, состоит из 3 частей: `header.payload.signature`
- **Header** - алгоритм подписи (HS256)
- **Payload** - данные пользователя (username, role, exp)
- **Signature** - подпись для проверки подлинности
- **Плюсы:** stateless, можно хранить данные в токене
- **Минусы:** нельзя отозвать до истечения
- **Формат:** `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Задача:** Исследовать и реализовать JWT аутентификацию.

### Шаг 1: Установка
```bash
pip install python-jose python-multipart
```

### Шаг 2: JWT утилиты
```python
# auth/jwt_auth.py
from datetime import datetime, timedelta
from jose import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

SECRET = "secret-key"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

USERS = {"admin": {"password": "secret", "role": "admin"}}

def create_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode({"sub": username, "exp": expire}, SECRET)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        return USERS[username]
    except:
        raise HTTPException(401, "Invalid token")

def require_admin(user = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin required")
    return user
```

### Шаг 3: Логин эндпоинт
```python
# api/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt_auth import USERS, create_token

router = APIRouter()

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_token(form.username), "token_type": "bearer"}
```

### Результат
```python
# api/students.py (финальная)
from auth.jwt_auth import get_current_user, require_admin

@router.post("/")
def create(student: Student, user = Depends(get_current_user)):
    return service.create(student)

@router.delete("/{name}")
def delete(name: str, user = Depends(require_admin)):
    if service.delete(name):
        return {"message": "Deleted"}
    raise HTTPException(404, "Not found")

# main.py
from fastapi import FastAPI
from api import students, auth

app = FastAPI()
app.include_router(auth.router)
app.include_router(students.router)
```

---

## 🎯 Самостоятельное задание: JWT с временем жизни

**Задача:** Создать систему с разными временами жизни токенов для разных ролей.

**Требования:**
1. `admin` - токен живет 60 минут
2. `teacher` - токен живет 30 минут  
3. `student` - токен живет 15 минут
4. Добавить эндпоинт `/auth/refresh` для обновления токена
5. Показывать время истечения токена в ответе

**Подсказка:**
```python
# auth/jwt_auth.py
def get_token_lifetime(role: str) -> int:
    lifetimes = {"admin": 60, "teacher": 30, "student": 15}
    return lifetimes.get(role, 15)

def create_token(username: str, role: str):
    minutes = get_token_lifetime(role)
    expire = datetime.utcnow() + timedelta(minutes=minutes)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET), expire

# api/auth.py
@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = USERS.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(401, "Invalid credentials")
    
    token, expire_time = create_token(form.username, user["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expire_time.isoformat(),
        "role": user["role"]
    }

@router.post("/refresh")
def refresh_token(current_user = Depends(get_current_user)):
    # Создать новый токен с тем же пользователем
    token, expire_time = create_token(current_user["username"], current_user["role"])
    return {"access_token": token, "expires_at": expire_time.isoformat()}
```

**Тестирование:**
1. Войти как `admin:secret` - получить токен на 60 мин
2. Войти как `student:pass` - получить токен на 15 мин
3. Использовать `/auth/refresh` для обновления токена
4. Проверить, что токен действительно истекает через указанное время

**Бонус:** Добавить middleware для автоматического логирования истекших токенов.

---

## 🎯 Критерии оценки

- **Задание 1 (2 балла):** Корректное разделение на модули с APIRouter
- **Задание 2 (3 балла):** Правильная реализация слоистой архитектуры
- **Задание 3 (2 балла):** Подключение PostgreSQL и Docker
- **Задание 4а (1 балл):** DI для сессии БД
- **Задание 4б (1 балл):** DI для дополнительного сервиса
- **Задание 5 (1 балл):** Basic Authentication
- **Задание 6 (2 балла):** JWT Authentication с ролями

**Максимум: 12 баллов**

## 📚 Полезные команды

```bash
# Запуск с Docker Compose
docker-compose up --build

# Тестирование API
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=secret123"

# Создание студента с JWT
curl -X POST "http://localhost:8000/api/v1/students/" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"name":"Иван Иванов","group":"ИС-21","specialty":"Информационные системы","year":3}'
```