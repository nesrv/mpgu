# Лабораторная работа: FastAPI - Архитектура и Безопасность (продолжение)

## 🎯 Цель работы

Изучить принципы построения масштабируемых API с использованием FastAPI, включая маршрутизацию, архитектурные паттерны и методы аутентификации.

# Задание 1. Оптимизация проекта и подключение его к СУБД

* Уменьшим структуру проекта для изучения методов аутентификации (всего будет 2 эндпоинта)


project-auth/
├── main.py     
├── api.py    
├── models.py    
├── schemas.py    
└── service.py  

```py
# main.py

# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Выполняется при запуске и остановке приложения"""
    # Код выполняется при запуске
    try:
        create_tables()  # Создаем таблицы в БД
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")    
    yield  # Приложение работает
    # Код выполняется при остановке (если нужно)
    # Здесь можно добавить очистку ресурсов


app = FastAPI(
    title="Student Management API",  # Название API
    version="1.0.0",  # Версия
    lifespan=lifespan  # Управление жизненным циклом
)

app.include_router(router)


# api.py
router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(db)

@router.post("/students/load-fixture")
def load_fixture(service: StudentService = Depends(get_service)):
    try:
        service.load_fixture()
        return {"message": "Loaded students from fixture"}
    except Exception as e:
        return {"error": f"Failed to load fixture: {str(e)}"}

@router.get("/students/")
def get_students(service: StudentService = Depends(get_service)):
    try:
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}


# models.py
DATABASE_URL = "postgresql://student:password@localhost:5435/students_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(JSON, default={})
    courses = relationship("CourseModel", back_populates="student")

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("StudentModel", back_populates="courses")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

# schemas.py
class StudentResponse(BaseModel):
    id: int
    name: str
    data: dict

# service.py
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models import StudentModel, CourseModel, Base, engine
from schemas import StudentResponse, StudentCreate
import json

class StudentService:
    def __init__(self, db: Session):
        self.db = db
    
    def load_fixture(self):
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Load students
        for student_data in data["students"]:
            student = StudentModel(**student_data)
            self.db.merge(student)
        
        # Load courses with enrollments
        for course_data in data["courses"]:
            course_id = course_data["id"]
            course_name = course_data["name"]
            
            # Find students enrolled in this course
            enrolled_students = [e["student_id"] for e in data["enrollments"] if e["course_id"] == course_id]
            
            for student_id in enrolled_students:
                course = CourseModel(
                    name=course_name,
                    student_id=student_id
                )
                self.db.merge(course)
        
        self.db.commit()        
       # Сбрасываем последовательность чтобы новые студенты получали правильные ID  
        max_id = self.db.query(func.max(StudentModel.id)).scalar() or 0
        self.db.execute(func.setval('students_id_seq', max_id))
    
    def get_all(self) -> List[StudentResponse]:
        students = self.db.query(StudentModel).all()
        return [StudentResponse(
            id=s.id,
            name=s.name,
            data=s.data or {}
        ) for s in students]



```

* Запустите postgresql в контейнере `docker run -d -p 5432:5432 postgres-students`

```sh
FROM postgres:17

ENV POSTGRES_DB=students_db
ENV POSTGRES_USER=student
ENV POSTGRES_PASSWORD=password

EXPOSE 5432
```

* Протестируйте API



# Задание 2. Изучение базовой аутентификации с помощью HTTP Basic Auth

* Сделайте для эндпоинта @router.get("/students/") аутентификацию HTTP Basic Auth
* Для этого в отдельном файле:

```py
# auth.py - Модуль аутентификации для FastAPI приложения

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Создаем объект для HTTP Basic Auth
security = HTTPBasic()


VALID_USERNAME = "admin"
VALID_PASSWORD = "secret123"


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
  
    # Проверяем username с защитой от timing attacks
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), VALID_USERNAME.encode("utf8")
    )
    # Проверяем password с защитой от timing attacks
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), VALID_PASSWORD.encode("utf8")
    )
    
    # Если учетные данные неверны, возвращаем ошибку 401
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},  # Указываем тип аутентификации
        )
    
    return credentials.username


# Добавьте аутентификацию с помощью Depency Injection

# api.py

from auth import authenticate_user 

@router.get("/students/")
def get_students(
    service: StudentService = Depends(get_service),
    current_user: str = Depends(authenticate_user)  # Требуем аутентификацию
):

    try:
        print(f"Пользователь {current_user} запросил список студентов")  # Логирование
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

```
* Проверяем

# Задание 3. Добавьте аутентификацию с помощью OAuth 


### Сначала создадим эндпоинт @router.post("/") и логику для него

```py
#api.py

@router.post("/students/", response_model=StudentResponse)
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_user)  # Требуем аутентификацию
):
   
    try:
        print(f"Пользователь {current_user} создает студента: {student_data.name}")  # Логирование
        return service.create(student_data)
    except Exception as e:
        return {"error": f"Failed to create student: {str(e)}"}

# schemas.py

class StudentCreate(BaseModel):
    name: str
    data: dict = {}


# service.py
class StudentService:
    ...

     def create(self, student_data):
        student = StudentModel(name=student_data.name, data=student_data.data or {})
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return StudentResponse(id=student.id, name=student.name, data=student.data or {})


```

## Настроим OAuth для этого эндпоинта @router.post("/students/")

```py

# oauth.py - OAuth2 аутентификация для FastAPI приложения

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets


# ========== НАСТРОЙКА OAUTH2 ==========
# Создаем объект для Bearer Token (проще для Swagger)
oauth2_scheme = HTTPBearer()

# OAuth2 токен (в реальном проекте хранить в переменных окружения)
VALID_TOKEN = "secret-oauth-token"

# ========== ФУНКЦИЯ OAUTH2 АУТЕНТИФИКАЦИИ ==========
def authenticate_oauth(credentials = Depends(oauth2_scheme)):
    # Проверяем токен с защитой от timing attacks
    is_valid_token = secrets.compare_digest(
        credentials.credentials.encode("utf8"), VALID_TOKEN.encode("utf8")
    )
    
    if not is_valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return "oauth_user"


# api.py

from oauth import authenticate_oauth  # OAuth2 Bearer Token

# Добавляем  аутентификацию с помощью Depency Injection
@router.post("/students/")
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 аутентификацию
):
   
 ...

```


## Тестирование

### В Swagger UI для OAuth2 нужно ввести токен напрямую:

#### Вариант 1 - Простой (используйте токен напрямую):

* В Swagger UI нажмите "Authorize" и введите:
* Token : secret-oauth-token
* Остальные поля оставьте пустыми


#### Вариант 2 Создадим собственный сервер авторизации:

```py

# ========== OAUTH СЕРВЕР АВТОРИЗАЦИИ ==========

def authenticate_user_for_token(username: str, password: str):
    """Проверка пользователя для выдачи токена"""
    # Заглушка - в реальности проверка в БД
    if username == "admin" and password == "password":
        return {"id": 1, "username": username}
    return None


@router.post("/oauth/token")
def get_token(credentials: OAuth2PasswordRequestForm = Depends()):
    # Проверка логина/пароля
    user = authenticate_user_for_token(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Выдача токена
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}



# oauth.py

# ========== ФУНКЦИЯ OAUTH2 АУТЕНТИФИКАЦИИ ==========
def authenticate_oauth(credentials = Depends(oauth2_scheme)):
    if VALID_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не создан",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем токен с защитой от timing attacks
    is_valid_token = secrets.compare_digest(
        credentials.credentials.encode("utf8"), VALID_TOKEN.encode("utf8")
    )
    
    if not is_valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return "oauth_user"

# ========== ФУНКЦИЯ СОЗДАНИЯ ПРОСТОГО ТОКЕНА ==========
def create_access_token(data: dict):
    """Создает простой UUID токен"""
    global VALID_TOKEN
    token = str(uuid.uuid4())
    VALID_TOKEN = token  # Сохраняем токен для проверки
    return token

```

## Тестирование

### Шаг 1 - Получить токен:

* Найдите эндпоинт POST /token
* Нажмите "Try it out"
* Введите:
```
username: admin
password: password
```
* Нажмите "Execute"
* Скопируйте access_token из ответа

### Шаг 2 - Авторизоваться:
* Нажмите кнопку "Authorize" вверху страницы
* В разделе OAuth2PasswordBearer введите:
```
username: admin
password: password
```
* Нажмите "Authorize"
* Или просто введите токен


Теперь эндпоинт POST /students/ будет работать с OAuth2 аутентификацией через Swagger


# Листинг измененного кода

```py
# ========== OAUTH СЕРВЕР АВТОРИЗАЦИИ ==========

class TokenRequest(BaseModel):
    username: str
    password: str

def authenticate_user_for_token(username: str, password: str):    
    # Заглушка - в реальности проверка в БД
    if username == "admin" and password == "password":
        return {"id": 1, "username": username}
    return None

@router.post("/oauth/token")
def get_token(credentials: TokenRequest):  
    user = authenticate_user_for_token(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Выдача токена
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/students/load-fixture")
def load_fixture(service = Depends(get_service)):
    ...

@router.post("/students/")
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 аутентификацию
):
   
   ...

@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_user)  # Требуем Basic Auth
):
   ...

# oauth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import secrets
import uuid

# ========== НАСТРОЙКА OAUTH2 ==========
# Создаем объект для Bearer Token (проще для Swagger)
oauth2_scheme = HTTPBearer()

# OAuth2 токен (в реальном проекте хранить в переменных окружения)
VALID_TOKEN = None  # Будет установлен при создании токена

# ========== ФУНКЦИЯ OAUTH2 АУТЕНТИФИКАЦИИ ==========
def authenticate_oauth(credentials = Depends(oauth2_scheme)):
    if VALID_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не создан",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем токен с защитой от timing attacks
    is_valid_token = secrets.compare_digest(
        credentials.credentials.encode("utf8"), VALID_TOKEN.encode("utf8")
    )
    
    if not is_valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return "oauth_user"

# ========== ФУНКЦИЯ СОЗДАНИЯ ПРОСТОГО ТОКЕНА ==========
def create_access_token(data: dict):
    """Создает простой UUID токен"""
    global VALID_TOKEN
    token = str(uuid.uuid4())
    VALID_TOKEN = token  # Сохраняем токен для проверки
    return token
```



Изучить создание и управления ролями




## 🎯  Задание 4. Роли пользователей

**Задача:** Добавить систему ролей в Basic Auth.

**Требования:**

1. Создать 3 роли: `admin`, `teacher`, `student`
2. Только `admin` может удалять студентов
3. `admin` и `teacher` могут создавать студентов
4. Все роли могут просматривать студентов
5. Роль определяется по username: `admin_*`, `teacher_*`, `student_*`


## Замени HTTP Basic Auth на OAuth2.
Оба эндпоинта используют Bearer токены:

* GET /students/ 
* POST /students/




```py
# api.py
@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 Auth
):

```

# Создадим роли и внесем изменения в сервисный слой

```py
# roles.py
from fastapi import HTTPException, status
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

# Пользователи с ролями
USERS = {
    "admin": {"password": "admin123", "role": Role.ADMIN},
    "teacher": {"password": "teacher123", "role": Role.TEACHER},
    "student": {"password": "student123", "role": Role.STUDENT}
}

def get_user_role(username: str) -> Role:
    """Получить роль пользователя"""
    user = USERS.get(username)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user["role"]

def check_permission(user_role: Role, required_roles: list[Role]):
    """Проверить права доступа"""
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {[r.value for r in required_roles]}"
        )

# api.py

def authenticate_user_for_token(username: str, password: str):
    """Проверка пользователя для выдачи токена"""
    from roles import USERS
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"id": 1, "username": username, "role": user["role"]}
    return None


@router.post("/students/")
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 аутентификацию
):
    # Проверяем права доступа
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN, Role.TEACHER])
    
    try:
        print(f"Пользователь {current_user} ({user_role}) создает студента: {student_data.name}")
        return service.create(student_data)
    except Exception as e:
        return {"error": f"Failed to create student: {str(e)}"}

@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_user_with_role)  # Требуем Basic Auth
):
    # Проверяем права доступа (все роли могут просматривать)
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN, Role.TEACHER, Role.STUDENT])
    
    try:
        print(f"Пользователь {current_user} ({user_role}) запросил список студентов")
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

```


# Задание 5. Добавьте эндпоинт для удаления студентов:

`DELETE /students/{student_id} - только admin может удалять`


```py
# app.py
@router.delete("/students/{student_id}")
def delete_student(
    ...
):
   ...

# service.py

def delete(self, student_id: int):
    student = ...
    ...
    return {"message": f"Student {student.name} deleted"}
```



📊 Выводы по занятию

На данном занятии мы изучили:
Перечислите основные темы...

Что нового узнал(а):
Опишите новые знания...

Что было трудно для понимания:
