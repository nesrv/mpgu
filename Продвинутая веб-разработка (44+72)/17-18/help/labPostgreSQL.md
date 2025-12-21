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
    s.id,
    s.name,
    s.email,
    ROUND(AVG(g.grade)::numeric, 2) as avg_grade,
    COUNT(g.course_id) as courses_count
FROM 
    students s
JOIN 
    grades g ON s.id = g.student_id
GROUP BY s.id, s.name, s.email
ORDER BY avg_grade DESC
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

```sql
CREATE MATERIALIZED VIEW course_statistics_mv AS
SELECT 
    c.id,
    c.title,
    COUNT(g.student_id) as students_count,
    ROUND(AVG(g.grade)::numeric, 2) as avg_grade,
    MIN(g.grade) as min_grade,
    MAX(g.grade) as max_grade
FROM 
    courses c
JOIN 
    grades g ON c.id = g.course_id
GROUP BY c.id, c.title
ORDER BY avg_grade DESC;

-- Проверка:
SELECT * FROM course_statistics_mv;

-- Обновление:
REFRESH MATERIALIZED VIEW course_statistics_mv;
```

Результат:

| id | title                          | students_count | avg_grade | min_grade | max_grade |
|----|--------------------------------|----------------|-----------|-----------|-----------|
| 4  | Базы данных                    | 4              | 4.63      | 4         | 5         |
| 3  | Программирование               | 6              | 4.50      | 4         | 5         |
| 5  | Алгоритмы и структуры данных   | 3              | 4.50      | 4         | 5         |
| 6  | Веб-разработка                 | 4              | 4.25      | 3         | 5         |
| 1  | Математика                     | 6              | 4.17      | 3         | 5         |
| 2  | Физика                         | 4              | 4.13      | 3.5       | 5         |




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
    p_student_id INT,
    p_course_id INT,
    p_grade REAL
)
LANGUAGE sql
AS $$
    INSERT INTO grades (student_id, course_id, grade)
    VALUES (p_student_id, p_course_id, p_grade);
$$;

-- Вызов:
CALL add_grade(1, 1, 4.5);

```
4.3 Создайте процедуру delete_inactive_students для удаления неактивных студентов без оценок


```sql
CREATE OR REPLACE PROCEDURE delete_inactive_students()
LANGUAGE sql
AS $$
    DELETE FROM students
    WHERE status = 'inactive'
    AND id NOT IN (SELECT DISTINCT student_id FROM grades);
$$;

-- Вызов:
CALL delete_inactive_students();
```

## 5. Функции

5.1 Создайте функцию get_student_avg_grade, которая возвращает средний балл студента по его ID

```sql

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
    SELECT COUNT(DISTINCT course_id)
    FROM grades
    WHERE student_id = p_student_id;
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
        WHEN p_grade >= 4.5 THEN 'Отлично'
        WHEN p_grade >= 3.5 THEN 'Хорошо'
        ELSE 'Удовлетворительно'
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
    SELECT CASE
        WHEN credits >= 4 THEN credits * 1000 * 0.9
        ELSE credits * 1000
    END
    FROM courses
    WHERE id = p_course_id;
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
    SELECT s.id, s.name, s.email, g.grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    WHERE g.course_id = p_course_id
    ORDER BY g.grade DESC;
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

# Самостоятельная работа
Сделать решения через raw sql и sqlalchemy 

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
def add_student_raw(name: str, email: str, status: str = 'active', db: Session = Depends(get_db)):
    db.execute(text("CALL add_student(:name, :email, :status)"), 
               {"name": name, "email": email, "status": status})
    db.commit()
    return {"message": "Student added successfully"}


# эндпоинт для delete_inactive_students
@app.delete("/students/inactive/raw")
def delete_inactive_students_raw(db: Session = Depends(get_db)):
    db.execute(text("CALL delete_inactive_students()"))
    db.commit()
    return {"message": "Inactive students deleted"}


# эндпоинт для get_student_avg_grade
@app.get("/students/{student_id}/avg-grade/raw")
def get_student_avg_grade_raw(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT get_student_avg_grade(:id) as avg_grade"), 
                        {"id": student_id})
    avg_grade = result.scalar()
    return {"student_id": student_id, "avg_grade": float(avg_grade)}


# эндпоинт для count_student_courses
@app.get("/students/{student_id}/courses-count/raw")
def count_student_courses_raw(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT count_student_courses(:id) as courses_count"), 
                        {"id": student_id})
    count = result.scalar()
    return {"student_id": student_id, "courses_count": int(count)}


# эндпоинт для get_grade_status
@app.get("/grades/status/raw")
def get_grade_status_raw(grade: float, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT get_grade_status(:grade) as status"), 
                        {"grade": grade})
    status = result.scalar()
    return {"grade": grade, "status": status}


# эндпоинт для calculate_course_discount
@app.get("/courses/{course_id}/discount/raw")
def calculate_course_discount_raw(course_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT calculate_course_discount(:id) as discounted_price"), 
                        {"id": course_id})
    price = result.scalar()
    return {"course_id": course_id, "discounted_price": float(price)}


# эндпоинт для get_course_students
@app.get("/courses/{course_id}/students/raw")
def get_course_students_raw(course_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM get_course_students(:id)"), 
                        {"id": course_id})
    students = [dict(row._mapping) for row in result]
    return {"course_id": course_id, "students": students}

```

## Примеры использования

```bash
# Запуск сервера
uvicorn main:app --reload

# Тестирование эндпоинтов
curl http://localhost:8000/students/top/raw
curl http://localhost:8000/courses/statistics/sqlalchemy
curl -X POST "http://localhost:8000/students/add/raw?name=Test&email=test@test.com"
curl http://localhost:8000/students/1/avg-grade/raw
curl http://localhost:8000/courses/1/students/raw
```

