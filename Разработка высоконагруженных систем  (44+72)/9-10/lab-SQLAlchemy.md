# Лабораторная работа: FastAPI - Работа с бд

## 🎯 Цель работы

Изучить работу FastAPI с СУБД PostgreSQL c помощью SQLAlchemy

# SQLAlchemy ШПАРГАЛКА для студентов

```py


# ============= ОСНОВНЫЕ ОПЕРАЦИИ =============

# CREATE - Создать студента
student = StudentModel(name="Иван", group="ИВТ-21", year=2, courses=[1,2])
db.add(student)
db.commit()

# READ - Получить студентов
db.query(StudentModel).all()                           # Все студенты
db.query(StudentModel).first()                         # Первый студент
db.query(StudentModel).filter(StudentModel.name == "Иван").first()  # По имени

# UPDATE - Обновить студента
student = db.query(StudentModel).filter(StudentModel.name == "Иван").first()
student.year = 3
db.commit()

# DELETE - Удалить студента
student = db.query(StudentModel).filter(StudentModel.name == "Иван").first()
db.delete(student)
db.commit()

# ============= ФИЛЬТРАЦИЯ =============

# По году
db.query(StudentModel).filter(StudentModel.year == 2)

# По группе
db.query(StudentModel).filter(StudentModel.group == "ИВТ-21")

# Несколько условий
db.query(StudentModel).filter(StudentModel.year == 2, StudentModel.group == "ИВТ-21")

# Поиск по имени (без учета регистра)
db.query(StudentModel).filter(StudentModel.name.ilike("%иван%"))

# Студенты на курсе (JSON поле)
db.query(StudentModel).filter(StudentModel.courses.contains([1]))

# ============= ПОЛЕЗНЫЕ КОМАНДЫ =============

# Подсчет
db.query(StudentModel).count()

# Сортировка
db.query(StudentModel).order_by(StudentModel.name)

# Лимит
db.query(StudentModel).limit(10)

# Обновить после изменений
db.refresh(student)

# ============= РАБОТА С JSON (курсы) =============

# Добавить курс
courses = student.courses or []
courses.append(course_id)
student.courses = courses
db.commit()

# Удалить курс
courses = student.courses or []
courses.remove(course_id)
student.courses = courses
db.commit()


```


## 📝 Задание 4а: Dependency Injection для БД

**Теория:** Dependency Injection (DI) - паттерн, позволяющий передавать зависимости в объект извне, а не создавать их внутри объекта.

**Практика:**

```python
# СРАВНЕНИЕ: project-pattern (in-memory) vs project-pattern-db (SQLAlchemy)

# ============= REPOSITORIES COMPARISON =============

# project-pattern: repositories/student_repository.py (IN-MEMORY)
class StudentRepository_InMemory:
    def __init__(self):
        self._students: list[Student] = []
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
        result = self._students
        if year:
            result = [s for s in result if s.year == year]
        if group:
            result = [s for s in result if s.group == group]
        return result
    
    def create(self, student_data: dict) -> Student:
        student = Student(**student_data)
        self._students.append(student)
        return student

# project-pattern-db: repositories/student_repository.py (SQLALCHEMY)
class StudentRepository_DB:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
        query = self.db.query(StudentModel)
        if year:
            query = query.filter(StudentModel.year == year)
        if group:
            query = query.filter(StudentModel.group == group)
        
        db_students = query.all()
        return [Student(name=s.name, group=s.group, year=s.year, courses=s.courses or []) for s in db_students]
    
    def create(self, student_data: dict) -> Student:
        db_student = StudentModel(**student_data)
        self.db.add(db_student)
        self.db.commit()
        self.db.refresh(db_student)
        return Student(name=db_student.name, group=db_student.group, year=db_student.year, courses=db_student.courses or [])

# ============= SERVICES COMPARISON =============

# project-pattern: services/student_service.py (IN-MEMORY)
class StudentService_InMemory:
    def __init__(self):
        self.repository = StudentRepository()  # Без БД сессии

# project-pattern-db: services/student_service.py (SQLALCHEMY)
class StudentService_DB:
    def __init__(self, db: Session):
        self.repository = StudentRepository(db)  # С БД сессией

# ============= API COMPARISON =============

# project-pattern: api/students.py (IN-MEMORY)
router = APIRouter(prefix="/students", tags=["students"])
service = StudentService()  # Глобальный сервис

@router.get("/")
def get_all(year: Optional[int] = None, group: Optional[str] = None):
    return service.get_all(year, group)  # Прямой вызов

# project-pattern-db: api/students.py (SQLALCHEMY)
router = APIRouter(prefix="/students", tags=["students"])

def get_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(db)  # Инъекция БД сессии

@router.get("/")
def get_all(year: Optional[int] = None, group: Optional[str] = None, service: StudentService = Depends(get_service)):
    return service.get_all(year, group)  # Через зависимость

# ============= MAIN APPLICATION COMPARISON =============

# project-pattern: main.py (IN-MEMORY)
from fastapi import FastAPI
from api import students, courses

app = FastAPI()
app.include_router(students.router)
app.include_router(courses.router)

# project-pattern-db: main.py (SQLALCHEMY)
from fastapi import FastAPI
from api import students, courses
from database.database import create_tables

app = FastAPI()

@app.on_event("startup")
def startup_event():
    create_tables()  # Создание таблиц при запуске

app.include_router(students.router)
app.include_router(courses.router)

# ============= КЛЮЧЕВЫЕ ОТЛИЧИЯ =============

"""
1. ХРАНЕНИЕ ДАННЫХ:
   - project-pattern: В памяти (списки Python)
   - project-pattern-db: PostgreSQL база данных

2. ЗАВИСИМОСТИ:
   - project-pattern: Нет внешних зависимостей
   - project-pattern-db: SQLAlchemy, PostgreSQL

3. ИНЪЕКЦИЯ ЗАВИСИМОСТЕЙ:
   - project-pattern: Глобальные сервисы
   - project-pattern-db: FastAPI Depends для БД сессий

4. ПЕРСИСТЕНТНОСТЬ:
   - project-pattern: Данные теряются при перезапуске
   - project-pattern-db: Данные сохраняются в БД

5. МАСШТАБИРУЕМОСТЬ:
   - project-pattern: Ограничена памятью сервера
   - project-pattern-db: Масштабируется с БД

6. КОНКУРЕНТНОСТЬ:
   - project-pattern: Проблемы с многопользовательским доступом
   - project-pattern-db: БД обеспечивает ACID транзакции

7. ЗАПРОСЫ:
   - project-pattern: Фильтрация в Python коде
   - project-pattern-db: SQL запросы в БД
"""



# остальные эндпоинты самостоятельно обновить

```



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
