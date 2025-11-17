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
    """
    Модель для частичного обновления данных студента.
    Все поля являются опциональными - можно обновлять только нужные поля.
    Используется в PATCH-запросах.
    Optional[str] = None - если поле не передано в запросе, его значение останется неизменным в БД
    """
    
    name: Optional[str] = None  # Имя студента (необязательное для обновления)
    group: Optional[str] = None  
    year: Optional[int] = None  

# Можно обновить только имя
update_data = {"name": "Новое имя"}
# Или только группу
update_data = {"group": "Новая группа"}
# Или все поля сразу
update_data = {"name": "Новое имя", "group": "Новая группа", "year": 2026}

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

проверьте 
```sh
uvicorn main:app --reload
```

## 📝 Задание 1: Маршрутизация с APIRouter и простыми слоями

**Задача:** Разделить монолитный код на модули с использованием APIRouter.

* Эта структура FastAPI проекта не является классическим MVC или MVT.
* Это слоистая архитектура (Layered Architecture) или трёхуровневая архитектура (3-tier architecture).

Вот как правильно назвать каждый слой:

* routers/ - Presentation Layer (слой представления) или API Layer
* services/ - Business Logic Layer (слой бизнес-логики) или Service Layer
* models/ - Data Access Layer (слой доступа к данным) или Model Layer

**Реализуем простую структура проекта:**

```
project-simple/
├── main.py      # FastAPI app + router подключение
├── models.py    # Student, StudentUpdate модели
└── students.py  # API endpoints + бизнес-логика

```


**Решение:**

```python
# students.py
from fastapi import APIRouter, HTTPException
from models import Student, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])

# In-memory storage
_students: list[Student] = []

@router.get("/")
def get_all() -> list[Student]:
    return _students

@router.get("/{name}")
def get_one(name: str) -> Student:
    student = next((s for s in _students if s.name == name), None)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/")
def create(student: Student) -> Student:
    _students.append(student)
    return student

@router.patch("/{name}")
def update(name: str, data: StudentUpdate) -> Student:
    for i, s in enumerate(_students):
        if s.name == name:
            updated = s.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _students[i] = Student(**updated)
            return _students[i]
    raise HTTPException(404, "Student not found")

@router.delete("/{name}")
def delete(name: str):
    for i, s in enumerate(_students):
        if s.name == name:
            _students.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Student not found")

# models.py
from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)

# main.py
from fastapi import FastAPI
from students import router

app = FastAPI()
app.include_router(router)
```


проверьте 
```sh
uvicorn main:app --reload
uvicorn main:app --reload --port 8001
```

## Особенности


* Один тип сущности (Student)
* Простая логика (CRUD)
* Нет базы данных
* Нет сложных бизнес-правил

# Задачи к первой части

1. добавь фикстуру на 20 студетов и эндпоинт для их загрузки 
* cоздай эндпоинт для поиска студентов: GET /students/search?query=Иван
* Добавить query параметры для фильтрации студентов:
GET /students?year=2&group=ИВТ-21

2. Модель "Курсы" (Courses)

* Создать модель Course с полями: id, name, credits, semester
* Добавить поле courses: list[int] в модель Student (ID курсов)
* Создать роутер courses.py с CRUD операциями

Добавить эндпоинты:

* GET /courses/{course_id}/students - студенты на курсе
* POST /students/{name}/enroll/{course_id} - записать на курс
* DELETE /students/{name}/unenroll/{course_id} - отчислить с курса


Решение 

```py
# models.py
from pydantic import BaseModel, Field
from typing import Optional

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)
    courses: list[int] = []

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    courses: Optional[list[int]] = None

class Course(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None

# fixtures.json
[
  {"name": "Иван Петров", "group": "ИВТ-21", "year": 2, "courses": [1, 2]},
  {"name": "Мария Сидорова", "group": "ИВТ-21", "year": 2, "courses": [1]},
  {"name": "Алексей Иванов", "group": "ИВТ-22", "year": 1, "courses": [2, 3]},
  {"name": "Елена Козлова", "group": "ИВТ-21", "year": 2, "courses": [1, 3]},
  {"name": "Дмитрий Смирнов", "group": "ИВТ-23", "year": 3, "courses": [2]},
  {"name": "Анна Волкова", "group": "ИВТ-22", "year": 1, "courses": [1, 2, 3]},
  {"name": "Сергей Морозов", "group": "ИВТ-21", "year": 2, "courses": [3]},
  {"name": "Ольга Новикова", "group": "ИВТ-23", "year": 3, "courses": [1]},
  {"name": "Павел Лебедев", "group": "ИВТ-22", "year": 1, "courses": [2, 3]},
  {"name": "Татьяна Соколова", "group": "ИВТ-21", "year": 2, "courses": [1, 2]},
  {"name": "Николай Попов", "group": "ИВТ-23", "year": 3, "courses": [3]},
  {"name": "Виктория Орлова", "group": "ИВТ-22", "year": 1, "courses": [1, 3]},
  {"name": "Андрей Михайлов", "group": "ИВТ-21", "year": 2, "courses": [2]},
  {"name": "Светлана Федорова", "group": "ИВТ-23", "year": 3, "courses": [1, 2]},
  {"name": "Максим Романов", "group": "ИВТ-22", "year": 1, "courses": [3]},
  {"name": "Екатерина Жукова", "group": "ИВТ-21", "year": 2, "courses": [1]},
  {"name": "Владимир Кузнецов", "group": "ИВТ-23", "year": 3, "courses": [2, 3]},
  {"name": "Наталья Васильева", "group": "ИВТ-22", "year": 1, "courses": [1, 2]},
  {"name": "Артем Петров", "group": "ИВТ-21", "year": 2, "courses": [3]},
  {"name": "Юлия Александрова", "group": "ИВТ-23", "year": 3, "courses": [1, 2, 3]}
]

# students.py
from fastapi import APIRouter, HTTPException, Query
from models import Student, StudentUpdate
from typing import Optional
import json

router = APIRouter(prefix="/students", tags=["students"])

_students: list[Student] = []

@router.post("/load-fixture")
def load_fixture():
    global _students
    with open("fixtures.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    _students = [Student(**item) for item in data]
    return {"message": f"Loaded {len(_students)} students"}

@router.get("/")
def get_all(year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
    result = _students
    if year:
        result = [s for s in result if s.year == year]
    if group:
        result = [s for s in result if s.group == group]
    return result

@router.get("/search")
def search(query: str = Query(...)) -> list[Student]:
    return [s for s in _students if query.lower() in s.name.lower()]

@router.get("/{name}")
def get_one(name: str) -> Student:
    student = next((s for s in _students if s.name == name), None)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/")
def create(student: Student) -> Student:
    _students.append(student)
    return student

@router.patch("/{name}")
def update(name: str, data: StudentUpdate) -> Student:
    for i, s in enumerate(_students):
        if s.name == name:
            updated = s.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _students[i] = Student(**updated)
            return _students[i]
    raise HTTPException(404, "Student not found")

@router.delete("/{name}")
def delete(name: str):
    for i, s in enumerate(_students):
        if s.name == name:
            _students.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Student not found")

@router.post("/{name}/enroll/{course_id}")
def enroll(name: str, course_id: int):
    for student in _students:
        if student.name == name:
            if course_id not in student.courses:
                student.courses.append(course_id)
            return {"message": "Enrolled"}
    raise HTTPException(404, "Student not found")

@router.delete("/{name}/unenroll/{course_id}")
def unenroll(name: str, course_id: int):
    for student in _students:
        if student.name == name:
            if course_id in student.courses:
                student.courses.remove(course_id)
            return {"message": "Unenrolled"}
    raise HTTPException(404, "Student not found")

# courses.py
from fastapi import APIRouter, HTTPException
from models import Course, CourseUpdate, Student
import students

router = APIRouter(prefix="/courses", tags=["courses"])

_courses: list[Course] = [
    Course(id=1, name="Программирование", credits=4, semester=1),
    Course(id=2, name="Математика", credits=3, semester=1),
    Course(id=3, name="Базы данных", credits=3, semester=2)
]

@router.get("/")
def get_all() -> list[Course]:
    return _courses

@router.get("/{course_id}")
def get_one(course_id: int) -> Course:
    course = next((c for c in _courses if c.id == course_id), None)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@router.post("/")
def create(course: Course) -> Course:
    _courses.append(course)
    return course

@router.patch("/{course_id}")
def update(course_id: int, data: CourseUpdate) -> Course:
    for i, c in enumerate(_courses):
        if c.id == course_id:
            updated = c.model_dump()
            updated.update(data.model_dump(exclude_unset=True))
            _courses[i] = Course(**updated)
            return _courses[i]
    raise HTTPException(404, "Course not found")

@router.delete("/{course_id}")
def delete(course_id: int):
    for i, c in enumerate(_courses):
        if c.id == course_id:
            _courses.pop(i)
            return {"message": "Deleted"}
    raise HTTPException(404, "Course not found")

@router.get("/{course_id}/students")
def get_students(course_id: int) -> list[Student]:
    return [s for s in students._students if course_id in s.courses]

# main.py
from fastapi import FastAPI
from students import router as students_router
from courses import router as courses_router

app = FastAPI()
app.include_router(students_router)
app.include_router(courses_router)


```


## 📝 Задание 3: Траснформация с сложную архитектуру
### Repository + Service Pattern с разделением ответственности

Далее нужно разделить слои по зонам ответственности

* Routers - обработка HTTP запросов
* Services - бизнес-логика
* Repositories - работа с данными
* Models - доменные сущности
* Schemas - валидация API

**Структура проекта:**

```py
project-pattern/
├── main.py                    # Точка входа
├── api/                   # API Уровень (Представление)
│   ├── __init__.py
│   ├── students.py           # REST эндпоинты студентов
│   └── courses.py            # REST эндпоинты курсов
│  
├── services/                  # Уровень бизнес-логики
│   ├── student_service.py    # Бизнес-логика студентов
│   └── course_service.py     # Бизнес-логика курсов
│  
├── repositories/              # Уровень доступа к данным
│   ├── student_repository.py # Операции с данными студентов
│   └── course_repository.py  # Операции с данными курсов
│  
├── models/                    # Доменные модели
│   ├── student.py            # Модель Student
│   └── course.py             # Модель Course
│  
├── schemas/                   # Схемы API
│   ├── student.py            # DTO студентов
│   └── course.py             # DTO курсов
│  
├── database/                  # Конфигурация БД
│   └── __init__.py           # Настройка БД (заглушка)
└── fixtures.json             # Тестовые данные


```

**Решение:**

```python

# main.py
from fastapi import FastAPI
from api import students, courses

app = FastAPI()
app.include_router(students.router)
app.include_router(courses.router)

# models/student.py
from pydantic import BaseModel, Field

class Student(BaseModel):
    name: str
    group: str
    year: int = Field(ge=1, le=5)
    courses: list[int] = []

# models/course.py
from pydantic import BaseModel

class Course(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

# schemas/student.py
from pydantic import BaseModel, Field
from typing import Optional

class StudentCreate(BaseModel):
    name: str
    group: str
    year: int
    courses: list[int] = []

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    group: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=5)
    courses: Optional[list[int]] = None

class StudentResponse(BaseModel):
    name: str
    group: str
    year: int
    courses: list[int]

# schemas/course.py
from pydantic import BaseModel
from typing import Optional

class CourseCreate(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[int] = None

class CourseResponse(BaseModel):
    id: int
    name: str
    credits: int
    semester: int

# repositories/student_repository.py
from models.student import Student
from typing import Optional
import json

class StudentRepository:
    def __init__(self):
        self._students: list[Student] = []
    
    def load_fixture(self):
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        self._students = [Student(**item) for item in data]
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> list[Student]:
        result = self._students
        if year:
            result = [s for s in result if s.year == year]
        if group:
            result = [s for s in result if s.group == group]
        return result
    
    def search(self, query: str) -> list[Student]:
        return [s for s in self._students if query.lower() in s.name.lower()]
    
    def get_by_name(self, name: str) -> Optional[Student]:
        return next((s for s in self._students if s.name == name), None)
    
    def create(self, student: Student) -> Student:
        self._students.append(student)
        return student
    
    def update(self, name: str, data: dict) -> Optional[Student]:
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
    
    def enroll(self, name: str, course_id: int) -> bool:
        student = self.get_by_name(name)
        if student and course_id not in student.courses:
            student.courses.append(course_id)
            return True
        return False
    
    def unenroll(self, name: str, course_id: int) -> bool:
        student = self.get_by_name(name)
        if student and course_id in student.courses:
            student.courses.remove(course_id)
            return True
        return False
    
    def get_students_by_course(self, course_id: int) -> list[Student]:
        return [s for s in self._students if course_id in s.courses]

# repositories/course_repository.py
from models.course import Course
from typing import Optional

class CourseRepository:
    def __init__(self):
        self._courses: list[Course] = [
            Course(id=1, name="Программирование", credits=4, semester=1),
            Course(id=2, name="Математика", credits=3, semester=1),
            Course(id=3, name="Базы данных", credits=3, semester=2)
        ]
    
    def get_all(self) -> list[Course]:
        return self._courses
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return next((c for c in self._courses if c.id == course_id), None)

# services/student_service.py
from models.student import Student
from schemas.student import StudentCreate, StudentUpdate
from repositories.student_repository import StudentRepository
from typing import List, Optional

class StudentService:
    def __init__(self):
        self.repository = StudentRepository()
    
    def load_fixture(self):
        return self.repository.load_fixture()
    
    def get_all(self, year: Optional[int] = None, group: Optional[str] = None) -> List[Student]:
        return self.repository.get_all(year, group)
    
    def search(self, query: str) -> List[Student]:
        return self.repository.search(query)
    
    def get_by_name(self, name: str) -> Optional[Student]:
        return self.repository.get_by_name(name)
    
    def create(self, student_data: StudentCreate) -> Student:
        student = Student(**student_data.model_dump())
        return self.repository.create(student)
    
    def update(self, name: str, student_data: StudentUpdate) -> Optional[Student]:
        return self.repository.update(name, student_data.model_dump(exclude_unset=True))
    
    def delete(self, name: str) -> bool:
        return self.repository.delete(name)
    
    def enroll(self, name: str, course_id: int) -> bool:
        return self.repository.enroll(name, course_id)
    
    def unenroll(self, name: str, course_id: int) -> bool:
        return self.repository.unenroll(name, course_id)

# services/course_service.py
from models.course import Course
from repositories.course_repository import CourseRepository
from repositories.student_repository import StudentRepository
from typing import List, Optional

class CourseService:
    def __init__(self):
        self.course_repository = CourseRepository()
        self.student_repository = StudentRepository()
    
    def get_all(self) -> List[Course]:
        return self.course_repository.get_all()
    
    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.course_repository.get_by_id(course_id)
    
    def get_students_by_course(self, course_id: int):
        return self.student_repository.get_students_by_course(course_id)

# api/students.py
from fastapi import APIRouter, HTTPException, Query
from schemas.student import StudentCreate, StudentUpdate, StudentResponse
from services.student_service import StudentService
from typing import List, Optional

router = APIRouter(prefix="/students", tags=["students"])
service = StudentService()

@router.post("/load-fixture")
def load_fixture():
    service.load_fixture()
    return {"message": "Loaded students from fixture"}

@router.get("/", response_model=List[StudentResponse])
def get_all(year: Optional[int] = None, group: Optional[str] = None):
    return service.get_all(year, group)

@router.get("/search", response_model=List[StudentResponse])
def search(query: str = Query(...)):
    return service.search(query)

@router.get("/{name}", response_model=StudentResponse)
def get_one(name: str):
    student = service.get_by_name(name)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.post("/", response_model=StudentResponse)
def create(student: StudentCreate):
    return service.create(student)

@router.patch("/{name}", response_model=StudentResponse)
def update(name: str, data: StudentUpdate):
    student = service.update(name, data)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.delete("/{name}")
def delete(name: str):
    if not service.delete(name):
        raise HTTPException(404, "Student not found")
    return {"message": "Deleted"}

@router.post("/{name}/enroll/{course_id}")
def enroll(name: str, course_id: int):
    if not service.enroll(name, course_id):
        raise HTTPException(404, "Student not found")
    return {"message": "Enrolled"}

@router.delete("/{name}/unenroll/{course_id}")
def unenroll(name: str, course_id: int):
    if not service.unenroll(name, course_id):
        raise HTTPException(404, "Student not found")
    return {"message": "Unenrolled"}

# api/courses.py
from fastapi import APIRouter, HTTPException
from schemas.course import CourseResponse
from schemas.student import StudentResponse
from services.course_service import CourseService
from typing import List

router = APIRouter(prefix="/courses", tags=["courses"])
service = CourseService()

@router.get("/", response_model=List[CourseResponse])
def get_all_courses():
    return service.get_all()

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int):
    course = service.get_by_id(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return course

@router.get("/{course_id}/students", response_model=List[StudentResponse])
def get_students_by_course(course_id: int):
    return service.get_students_by_course(course_id)

```


## Когда нужна сложная структура:

* Много сущностей (User, Course, Grade, etc.)
* Реальная БД (PostgreSQL, MongoDB)
* Сложная бизнес-логика
* Аутентификация/авторизация

## 📝 Задание 3: Подключение PostgreSQL

**Задача:** Заменить in-memory хранилище на PostgreSQL в Docker контейнере.

1. Поднять бд в докер контейнере

```dockerfile
# Dockerfile
FROM postgres:18

ENV POSTGRES_DB=students_db
ENV POSTGRES_USER=student
ENV POSTGRES_PASSWORD=password

EXPOSE 5432
```

```bash
# Команды для запуска

docker build -t postgres-students .
docker run -d -p 5432:5432 postgres-students
```


```txt
# requirements.txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
```




**Файлы конфигурации:**

```python
# database.py
from sqlalchemy import Column, Integer, String, create_engine, JSON
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
    courses = Column(JSON, default=[])

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    credits = Column(Integer)
    semester = Column(Integer)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
```


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
