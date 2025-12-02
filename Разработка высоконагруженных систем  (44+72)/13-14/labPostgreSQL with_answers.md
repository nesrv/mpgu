# Лабораторная работа: Продвинутая работа с PostgreSQL в среде FastAPI

**Дисциплина:** Проектирование и разработка высоконагруженных сервисов  
**Время выполнения:** 4 академических часа  
**МПГУ, 4 курс бакалавриата**

---

## 🎯 Цель работы

Изучить продвинутые возможности PostgreSQL (Views, Materialized Views, Cursors, Functions, Procedures) и интегрировать их с FastAPI через SQLAlchemy и raw SQL.
Оптмизация и ускорения работы бэкенда за счет перенос нагрузки на базу данны
---

## Серверная разработка

1. Запустите postgresql в контейнере
2. Создайте и заполните тестовыми данными бд из seed_data.sql

## Практические кейсы

## 3. Представления
3.1 Создать представление `active_students_view` для активных студентов

```sql
CREATE VIEW active_students_view AS
SELECT 
    id,
    name,
    email,
    created_at
FROM students
WHERE status = 'active';
```
Результат

| id | name             | email                          | created_at                  |
|----|------------------|--------------------------------|-----------------------------|
| 1  | Иван Иванов      | ivan.ivanov@example.com        | 2025-12-01 22:20:47.421411  |
| 2  | Мария Петрова    | maria.petrova@example.com      | 2025-12-01 22:20:47.421411  |
| 3  | Алексей Сидоров  | alexey.sidorov@example.com     | 2025-12-01 22:20:47.421411  |
| 5  | Дмитрий Волков   | dmitry.volkov@example.com      | 2025-12-01 22:20:47.421411  |
| 6  | Анна Смирнова    | anna.smirnova@example.com      | 2025-12-01 22:20:47.421411  |
| 7  | Сергей Лебедев   | sergey.lebedev@example.com     | 2025-12-01 22:20:47.421411  |


3.2 Создайте представление view `top_students_view` с топ-5 студентами по среднему баллу

```sql
CREATE VIEW top_students_view AS
SELECT 
   ...
FROM 
    ...
JOIN 
    ...
GROUP ...
ORDER ...
LIMIT 5;

-- Проверка:
SELECT * FROM top_students_view;

```

Результат:

| id | name             | email                          | avg_grade | courses_count |
|----|------------------|--------------------------------|-----------|---------------|
| 5  | Дмитрий Волков   | dmitry.volkov@example.com      | 4.83      | 6             |
| 2  | Мария Петрова    | maria.petrova@example.com      | 4.75      | 4             |
| 1  | Иван Иванов      | ivan.ivanov@example.com        | 4.63      | 4             |
| 6  | Анна Смирнова    | anna.smirnova@example.com      | 4.50      | 3             |
| 7  | Сергей Лебедев   | sergey.lebedev@example.com     | 4.17      | 3             |

3.3 Создайте materialized view `course_statistics_mv` со статистикой по каждому курсу:
название курса, количество студентов, средний балл, минимальный и максимальный балл



Результат:

| id | title                          | students_count | avg_grade | min_grade | max_grade |
|----|--------------------------------|----------------|-----------|-----------|-----------|
| 4  | Базы данных                    | 4              | 4.63      | 4         | 5         |
| 3  | Программирование               | 6              | 4.50      | 4         | 5         |
| 5  | Алгоритмы и структуры данных   | 3              | 4.50      | 4         | 5         |
| 6  | Веб-разработка                 | 4              | 4.25      | 3         | 5         |
| 1  | Математика                     | 6              | 4.17      | 3         | 5         |
| 2  | Физика                         | 4              | 4.13      | 3.5       | 5         |


```sql
--решение здесь

```

* Измени данные в таблице
* Выполни материализованный запрос
* Обнови материализованный запрос

## 4. Процедуры

4.1  Создайте процедуру add_student для добавления нового студента

```sql
CREATE OR REPLACE PROCEDURE add_student(
    p_name VARCHAR,
    p_email VARCHAR,
    p_status VARCHAR DEFAULT 'active'
)
LANGUAGE sql
AS $$
    INSERT INTO students (name, email, status)
    VALUES (p_name, p_email, p_status);
$$;

-- Вызов:
CALL add_student('Петр Петров', 'petr.petrov@example.com', 'active');
```

 4.2 Создайте процедуру add_grade для добавления оценки студенту по курсу

```sql
CREATE OR REPLACE PROCEDURE add_grade(
  ...
)
LANGUAGE sql
AS $$
    INSERT INTO grades ...
    VALUES ...
$$;

-- Вызов:
CALL add_grade(1, 1, 4.5);

```
4.3 Создайте процедуру delete_inactive_students для удаления неактивных студентов без оценок


```sql
CREATE OR REPLACE PROCEDURE delete_inactive_students()
LANGUAGE sql
AS $$
   ...
$$;

-- Вызов:
CALL delete_inactive_students();
```

## 5. Функции

5.1 Создайте функцию get_student_avg_grade, которая возвращает средний балл студента по его ID

```sql


-- РЕШЕНИЕ 1:
CREATE OR REPLACE FUNCTION get_student_avg_grade(p_student_id INT)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT COALESCE(ROUND(AVG(grade)::numeric, 2), 0)
    FROM grades
    WHERE student_id = p_student_id;
$$;

-- Использование:
SELECT name, get_student_avg_grade(id) as avg_grade
FROM students;

```

5.2 Создайте функцию count_student_courses, которая возвращает количество курсов студента

```sql

CREATE OR REPLACE FUNCTION count_student_courses(p_student_id INT)
RETURNS BIGINT
LANGUAGE sql
AS $$
   ...
$$;

-- Использование:
SELECT name, count_student_courses(id) as courses_count
FROM students;

```
5.3 Создайте функцию get_grade_status, которая возвращает статус оценки:
-- 'Отлично' (>=4.5), 'Хорошо' (>=3.5), 'Удовлетворительно' (<3.5)



| student_id | course_id | grade | status     |
|------------|-----------|-------|------------|
| 1          | 1         | 5     | Отлично    |
| 1          | 2         | 4.5   | Отлично    |
| 1          | 3         | 5     | Отлично    |
| 1          | 4         | 4     | Хорошо     |
| 2          | 1         | 4.5   | Отлично    |


```sql 

CREATE OR REPLACE FUNCTION get_grade_status(p_grade REAL)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT CASE
       ...
    END;
$$;


-- Использование:

-- Простой вызов функции
SELECT get_grade_status(4.8);  -- Результат: 'Отлично'
SELECT get_grade_status(4.0);  -- Результат: 'Хорошо'


-- Пример с таблицей оценок
SELECT 
    student_id,
    course_id,
    grade,
    get_grade_status(grade) AS status
FROM grades
LIMIT 5;

-- еще пример
SELECT 
    s.name, 
    c.title, 
    g.grade, 
    get_grade_status(g.grade) as status
FROM grades g
JOIN students s ON g.student_id = s.id
JOIN courses c ON g.course_id = c.id
LIMIT 5;
```



5.4 Создайте функцию calculate_course_discount, которая возвращает цену курса со скидкой
Скидка 10% если credits >= 4, иначе без скидки. Базовая цена: 1000 за credit



| Название курса                  | Длительность (мес) | Стоимость (руб) | Скидка 10% (руб) |
|-------------------------------|--------------------|------------------|------------------|
| Математика                    | 4                  | 4000             | 3600.0           |
| Физика                        | 3                  | 3000             | 3000             |
| Программирование              | 5                  | 5000             | 4500.0           |
| Базы данных                   | 4                  | 4000             | 3600.0           |
| Алгоритмы и структуры данных  | 4                  | 4000             | 3600.0           |
| Веб-разработка                | 3                  | 3000             | 3000             |

```sql

CREATE OR REPLACE FUNCTION calculate_course_discount(p_course_id INT)
RETURNS NUMERIC
LANGUAGE sql
STABLE
AS $$
   ...
$$;

-- Использование:
SELECT 
    title, 
    credits,
    credits * 1000 as original_price,
    calculate_course_discount(id) as discounted_price
FROM courses;

```



5.5* Создайте функцию get_course_students, которая возвращает всех студентов курса


| id | Имя                 | Email                          | Оценка |
|----|---------------------|--------------------------------|--------|
| 1  | Иван Иванов         | ivan.ivanov@example.com        | 5      |
| 5  | Дмитрий Волков      | dmitry.volkov@example.com      | 5      |
| 2  | Мария Петрова       | maria.petrova@example.com      | 4.5    |
| 7  | Сергей Лебедев      | sergey.lebedev@example.com     | 4      |
| 8  | Ольга Новикова      | olga.novikova@example.com      | 3.5    |
| 4  | Елена Козлова       | elena.kozlova@example.com      | 3      |


```sql

CREATE OR REPLACE FUNCTION get_course_students(p_course_id INT)
RETURNS TABLE(
    student_id INT,
    student_name VARCHAR,
    student_email VARCHAR,
    grade REAL
)
LANGUAGE sql
AS $$
  ...
$$;

-- Использование:
SELECT * FROM get_course_students(1);


```

Работа с хранимыми в бд объектами через fastapi

## 📋 Подготовка к работе



### Структура проекта

```
lab-postgres/
├── main.py              # FastAPI приложение
├── database.py          # Подключение к БД
├── models.py            # SQLAlchemy модели
├── schemas.py           # Pydantic схемы
├── init_db.sql          # SQL для инициализации
└── requirements.txt     # Зависимости
```

### Установка зависимостей

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```


## 🔧 Настройка проекта

### database.py

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "postgresql://user:password@localhost/lab_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### models.py

```python
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import datetime

class Student(Base):
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    grades: Mapped[list["Grade"]] = relationship(back_populates="student")

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    credits: Mapped[int] = mapped_column(default=3)
    
    grades: Mapped[list["Grade"]] = relationship(back_populates="course")

class Grade(Base):
    __tablename__ = "grades"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    grade: Mapped[float] = mapped_column(Float)
    
    student: Mapped["Student"] = relationship(back_populates="grades")
    course: Mapped["Course"] = relationship(back_populates="grades")
```

### schemas.py

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class StudentBase(BaseModel):
    name: str
    email: str
    status: str = 'active'

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class GradeResponse(BaseModel):
    student_id: int
    course_id: int
    grade: float
    
    model_config = ConfigDict(from_attributes=True)

class SQLQuery(BaseModel):
    query: str

# main.py
# 
from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text, MetaData, Table, select
from database import get_db, engine
from pydantic import BaseModel
from schemas import SQLQuery

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Lab PostgreSQL API is running"}

def get_active_students_table():
    metadata = MetaData()
    return Table('active_students_view', metadata, autoload_with=engine)


@app.post("/sql/file", summary="Execute SQL from file", description="Upload and execute SQL file")
async def execute_sql_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        sql_query = content.decode('utf-8')
        
        # Выполняем все запросы из файла
        result = db.execute(text(sql_query))
        db.commit()       
       
        return {"status": "success", "message": "SQL file executed successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


```

Реализовать вызов представлений, процедур и функций через эндпоинты


### Пример получения активных студентов

```python
# main.py

@app.get("/students/active/raw")
def get_active_students_raw(db: Session = Depends(get_db)):
    """Получение активных студентов через raw SQL"""
    result = db.execute(text("SELECT * FROM active_students_view"))
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "count": len(students), "data": students}


# через SQLAlchemy

from sqlalchemy import Table, MetaData, select
from database import engine

# Отражаем view как таблицу
metadata = MetaData()
active_students_table = Table('active_students_view', metadata, autoload_with=engine)

@app.get("/students/active/sqlalchemy")
def get_active_students_sqlalchemy(db: Session = Depends(get_db)):
    """Получение активных студентов через SQLAlchemy"""
    stmt = select(active_students_table)
    result = db.execute(stmt)
    students = [dict(row._mapping) for row in result]
    return {"method": "sqlalchemy", "count": len(students), "data": students}
```

Решения через raw sql и sqlalchemy 

```python

# эндпоинт для top_students_view
@app.get("/students/top/raw")
def get_top_students_raw(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM top_students_view"))
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "data": students}

top_students_table = Table('top_students_view', metadata, autoload_with=engine)

@app.get("/students/top/sqlalchemy")
def get_top_students_sqlalchemy(db: Session = Depends(get_db)):
    stmt = select(top_students_table)
    result = db.execute(stmt)
    students = [dict(row._mapping) for row in result]
    return {"method": "sqlalchemy", "data": students}


# эндпоинт для course_statistics_mv
@app.get("/courses/statistics/raw")
def get_course_statistics_raw(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM course_statistics_mv"))
    stats = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "data": stats}

course_stats_table = Table('course_statistics_mv', metadata, autoload_with=engine)

@app.get("/courses/statistics/sqlalchemy")
def get_course_statistics_sqlalchemy(db: Session = Depends(get_db)):
    stmt = select(course_stats_table)
    result = db.execute(stmt)
    stats = [dict(row._mapping) for row in result]
    return {"method": "sqlalchemy", "data": stats}


# эндпоинт для add_student
@app.post("/students/add/raw")
def add_student_raw(name: str, email: str, status: str = "active", db: Session = Depends(get_db)):
    db.execute(text("CALL add_student(:name, :email, :status)"), 
               {"name": name, "email": email, "status": status})
    db.commit()
    return {"method": "raw_sql", "message": "Student added"}


# эндпоинт для delete_inactive_students
@app.delete("/students/inactive/raw")
def delete_inactive_students_raw(db: Session = Depends(get_db)):
    db.execute(text("CALL delete_inactive_students()"))
    db.commit()
    return {"method": "raw_sql", "message": "Inactive students deleted"}


# эндпоинт для get_student_avg_grade
@app.get("/students/{student_id}/avg-grade/raw")
def get_student_avg_grade_raw(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT get_student_avg_grade(:id) as avg_grade"), 
                        {"id": student_id})
    avg_grade = result.scalar()
    return {"method": "raw_sql", "student_id": student_id, "avg_grade": float(avg_grade)}


# эндпоинт для count_student_courses
@app.get("/students/{student_id}/courses-count/raw")
def count_student_courses_raw(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT count_student_courses(:id) as count"), 
                        {"id": student_id})
    count = result.scalar()
    return {"method": "raw_sql", "student_id": student_id, "courses_count": count}


# эндпоинт для get_grade_status
@app.get("/grades/status/raw")
def get_grade_status_raw(grade: float, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT get_grade_status(:grade) as status"), 
                        {"grade": grade})
    status = result.scalar()
    return {"method": "raw_sql", "grade": grade, "status": status}


# эндпоинт для calculate_course_discount
@app.get("/courses/{course_id}/discount/raw")
def calculate_course_discount_raw(course_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT calculate_course_discount(:id) as price"), 
                        {"id": course_id})
    price = result.scalar()
    return {"method": "raw_sql", "course_id": course_id, "discounted_price": float(price)}


# эндпоинт для get_course_students
@app.get("/courses/{course_id}/students/raw")
def get_course_students_raw(course_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM get_course_students(:id)"), 
                        {"id": course_id})
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "course_id": course_id, "data": students}


# ============================================
# ПРИМЕРЫ ДАЛЬНЕЙШЕЙ ОБРАБОТКИ ДАННЫХ
# ============================================

# Пример 1: Агрегация и фильтрация данных из view
@app.get("/students/top/filtered")
def get_top_students_filtered(min_courses: int = 3, db: Session = Depends(get_db)):
    """""" Получаем топ студентов с фильтрацией по количеству курсов """
    result = db.execute(text("""
        SELECT * FROM top_students_view 
        WHERE courses_count >= :min_courses
    """), {"min_courses": min_courses})
    
    students = [dict(row._mapping) for row in result]
    
    # Дополнительная обработка в Python
    for student in students:
        student['grade_category'] = (
            'Отличник' if student['avg_grade'] >= 4.5 
            else 'Хорошист' if student['avg_grade'] >= 4.0 
            else 'Удовлетворительно'
        )
        student['email_domain'] = student['email'].split('@')[1]
    
    return {
        "total": len(students),
        "filter": {"min_courses": min_courses},
        "data": students
    }


# Пример 2: Комбинирование нескольких функций
@app.get("/students/{student_id}/profile")
def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    """Полный профиль студента с использованием нескольких функций"""
    # Получаем базовую информацию
    student = db.execute(text("""
        SELECT id, name, email, status FROM students WHERE id = :id
    """), {"id": student_id}).fetchone()
    
    if not student:
        return {"error": "Student not found"}
    
    # Используем функции для дополнительных данных
    avg_grade = db.execute(text(
        "SELECT get_student_avg_grade(:id)"
    ), {"id": student_id}).scalar()
    
    courses_count = db.execute(text(
        "SELECT count_student_courses(:id)"
    ), {"id": student_id}).scalar()
    
    # Собираем все в один объект
    profile = {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "status": student.status,
        "avg_grade": float(avg_grade),
        "courses_count": courses_count,
        "performance": "Excellent" if avg_grade >= 4.5 else "Good" if avg_grade >= 4.0 else "Average"
    }
    
    return profile


# Пример 3: Статистика и аналитика
@app.get("/analytics/courses")
def get_courses_analytics(db: Session = Depends(get_db)):
    """Аналитика по курсам с дополнительными расчетами"""
    result = db.execute(text("SELECT * FROM course_statistics_mv"))
    courses = [dict(row._mapping) for row in result]
    
    # Расчет дополнительных метрик
    total_students = sum(c['students_count'] for c in courses)
    avg_grade_all = sum(c['avg_grade'] * c['students_count'] for c in courses) / total_students if total_students > 0 else 0
    
    # Добавляем дополнительные поля
    for course in courses:
        course['difficulty'] = (
            'Сложный' if course['avg_grade'] < 4.0 
            else 'Средний' if course['avg_grade'] < 4.5 
            else 'Легкий'
        )
        course['popularity_percent'] = round((course['students_count'] / total_students * 100), 2) if total_students > 0 else 0
    
    return {
        "summary": {
            "total_courses": len(courses),
            "total_students": total_students,
            "avg_grade_overall": round(avg_grade_all, 2)
        },
        "courses": courses
    }


# Пример 4: Использование процедур с валидацией
from pydantic import BaseModel, EmailStr

class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    status: str = "active"

@app.post("/students/create")
def create_student_validated(student: StudentCreate, db: Session = Depends(get_db)):
    """Создание студента с валидацией и проверкой"""
    # Проверяем, существует ли email
    existing = db.execute(text(
        "SELECT id FROM students WHERE email = :email"
    ), {"email": student.email}).fetchone()
    
    if existing:
        return {"error": "Student with this email already exists", "existing_id": existing.id}
    
    # Вызываем процедуру
    db.execute(text(
        "CALL add_student(:name, :email, :status)"
    ), {"name": student.name, "email": student.email, "status": student.status})
    db.commit()
    
    # Получаем созданного студента
    new_student = db.execute(text(
        "SELECT * FROM students WHERE email = :email"
    ), {"email": student.email}).fetchone()
    
    return {
        "message": "Student created successfully",
        "student": dict(new_student._mapping)
    }


# Пример 5: Пагинация результатов функции
@app.get("/courses/{course_id}/students/paginated")
def get_course_students_paginated(
    course_id: int, 
    page: int = 1, 
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Получение студентов курса с пагинацией"""
    offset = (page - 1) * page_size
    
    # Получаем все данные
    result = db.execute(text("""
        SELECT * FROM get_course_students(:id)
        LIMIT :limit OFFSET :offset
    """), {"id": course_id, "limit": page_size, "offset": offset})
    
    students = [dict(row._mapping) for row in result]
    
    # Подсчитываем общее количество
    total = db.execute(text("""
        SELECT COUNT(*) FROM get_course_students(:id)
    """), {"id": course_id}).scalar()
    
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "data": students
    }

```





