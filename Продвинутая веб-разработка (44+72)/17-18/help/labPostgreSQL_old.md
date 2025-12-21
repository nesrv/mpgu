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


4.1  Генерация большого количества студентов (например, 10000)

```sql

INSERT INTO students (name, email, status)
SELECT 
    'Student ' || i,
    'student' || i || '@test.com',
    CASE WHEN i % 2 = 0 THEN 'active' ELSE 'inactive' END
FROM generate_series(1, 10000) AS i;
```

## 📋 Подготовка к работе

## 



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

-

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

---

## 📝 Задание 1: Работа с Views (Представлениями)

### Цель
Создать представление для активных студентов и работать с ним через FastAPI.

### Шаг 1: Создание представления в БД

**Способ 1: Через Python-скрипт**

```python
# init_views.py
from database import engine
from sqlalchemy import text

def create_views():
    with engine.connect() as conn:
        # Создаем view для активных студентов
        conn.execute(text("""
            CREATE OR REPLACE VIEW active_students_view AS
            SELECT 
                id,
                name,
                email,
                created_at
            FROM students
            WHERE status = 'active';
        """))
        conn.commit()
        print("✅ View 'active_students_view' created successfully")

if __name__ == "__main__":
    create_views()
```


**Способ 2: Через dbeaver или pgAdmin**

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

### Шаг 2: Работа через Raw SQL

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db

app = FastAPI()

@app.get("/students/active/raw")
def get_active_students_raw(db: Session = Depends(get_db)):
    """Получение активных студентов через raw SQL"""
    result = db.execute(text("SELECT * FROM active_students_view"))
    students = [dict(row._mapping) for row in result]
    return {"method": "raw_sql", "count": len(students), "data": students}
```

### Шаг 3: Работа через SQLAlchemy

```python
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

### Задание для выполнения

1. Создайте view `top_students_view` с топ-10 студентами по среднему баллу
2. Реализуйте эндпоинт `/students/top` двумя способами (raw SQL и SQLAlchemy)
3. Добавьте параметр `limit` для управления количеством результатов

---

## 📝 Задание 2: Материализованные представления

### Цель
Создать материализованное представление для статистики по курсам.

### Шаг 1: Создание materialized view


```sql
CREATE MATERIALIZED VIEW course_statistics AS
SELECT 
    c.id as course_id,
    c.title,
    COUNT(g.id) as student_count,
    AVG(g.grade) as avg_grade,
    MAX(g.grade) as max_grade,
    MIN(g.grade) as min_grade,
    NOW() as last_updated
FROM courses c
LEFT JOIN grades g ON c.id = g.course_id
GROUP BY c.id, c.title;

-- Создаем индекс для быстрого доступа
CREATE INDEX idx_course_stats_id ON course_statistics(course_id);
```

### Шаг 2: Чтение данных

```python
@app.get("/courses/statistics")
def get_course_statistics(db: Session = Depends(get_db)):
    """Получение статистики по курсам из materialized view"""
    result = db.execute(text("SELECT * FROM course_statistics"))
    stats = [dict(row._mapping) for row in result]
    return {"data": stats}
```

### Шаг 3: Обновление materialized view

```python
@app.post("/courses/statistics/refresh")
def refresh_course_statistics(db: Session = Depends(get_db)):
    """Обновление материализованного представления"""
    db.execute(text("REFRESH MATERIALIZED VIEW course_statistics"))
    db.commit()
    return {"message": "Statistics refreshed successfully"}

@app.post("/courses/statistics/refresh-concurrent")
def refresh_course_statistics_concurrent(db: Session = Depends(get_db)):
    """Обновление без блокировки чтения"""
    db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY course_statistics"))
    db.commit()
    return {"message": "Statistics refreshed concurrently"}
```

### Задание для выполнения

1. Создайте materialized view `student_performance` с информацией о каждом студенте
2. Добавьте эндпоинт для получения данных из этого view
3. Реализуйте автоматическое обновление через фоновую задачу (используйте `BackgroundTasks`)

---

## 📝 Задание 3: Работа с курсорами

### Цель
Обработать большой объем данных порциями с помощью курсоров.

### Шаг 1: Создание тестовых данных

```python
@app.post("/students/generate")
def generate_test_students(count: int = 10000, db: Session = Depends(get_db)):
    """Генерация тестовых данных"""
    for i in range(count):
        student = Student(
            name=f"Student {i}",
            email=f"student{i}@test.com",
            status='active' if i % 2 == 0 else 'inactive'
        )
        db.add(student)
        if i % 1000 == 0:
            db.commit()
    db.commit()
    return {"message": f"Generated {count} students"}
```

### Шаг 2: Использование серверного курсора

```python
import psycopg2
from typing import List

@app.get("/students/export")
def export_students_with_cursor(batch_size: int = 1000):
    """Экспорт студентов порциями через курсор"""
    conn = psycopg2.connect(DATABASE_URL)
    
    # Создаем серверный курсор
    cursor = conn.cursor(name='student_cursor')
    cursor.execute("SELECT id, name, email FROM students")
    
    all_students = []
    batch_count = 0
    
    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break
        
        batch_count += 1
        all_students.extend([{"id": r[0], "name": r[1], "email": r[2]} for r in rows])
    
    cursor.close()
    conn.close()
    
    return {
        "total": len(all_students),
        "batches": batch_count,
        "batch_size": batch_size,
        "sample": all_students[:10]  # Первые 10 для примера
    }
```

### Шаг 3: Курсор с SQLAlchemy

```python
from sqlalchemy import select
from models import Student

@app.get("/students/stream")
def stream_students(limit: int = 100, db: Session = Depends(get_db)):
    """Потоковое чтение через SQLAlchemy"""
    stmt = select(Student).execution_options(yield_per=limit)
    result = db.execute(stmt)
    
    students = []
    for row in result.scalars():
        students.append({
            "id": row.id,
            "name": row.name,
            "email": row.email
        })
    
    return {"count": len(students), "data": students[:10]}
```

### Задание для выполнения

1. Создайте эндпоинт `/grades/export` для экспорта всех оценок порциями по 500
2. Добавьте подсчет статистики во время обработки (средний балл, количество)
3. Реализуйте прогресс-бар через WebSocket или Server-Sent Events

---

## 📝 Задание 4: Хранимые процедуры

### Цель
Создать процедуру для зачисления студента на курс с проверками.

### Шаг 1: Создание процедуры


```sql
CREATE OR REPLACE PROCEDURE enroll_student_to_course(
    p_student_id INT,
    p_course_id INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_student_exists BOOLEAN;
    v_course_exists BOOLEAN;
    v_already_enrolled BOOLEAN;
BEGIN
    -- Проверяем существование студента
    SELECT EXISTS(SELECT 1 FROM students WHERE id = p_student_id) INTO v_student_exists;
    IF NOT v_student_exists THEN
        RAISE EXCEPTION 'Student with id % does not exist', p_student_id;
    END IF;
    
    -- Проверяем существование курса
    SELECT EXISTS(SELECT 1 FROM courses WHERE id = p_course_id) INTO v_course_exists;
    IF NOT v_course_exists THEN
        RAISE EXCEPTION 'Course with id % does not exist', p_course_id;
    END IF;
    
    -- Проверяем, не зачислен ли уже
    SELECT EXISTS(
        SELECT 1 FROM grades 
        WHERE student_id = p_student_id AND course_id = p_course_id
    ) INTO v_already_enrolled;
    
    IF v_already_enrolled THEN
        RAISE EXCEPTION 'Student already enrolled in this course';
    END IF;
    
    -- Зачисляем студента (добавляем запись с оценкой 0)
    INSERT INTO grades (student_id, course_id, grade)
    VALUES (p_student_id, p_course_id, 0);
    
    COMMIT;
    
    RAISE NOTICE 'Student % enrolled to course %', p_student_id, p_course_id;
END;
$$;
```

### Шаг 2: Вызов процедуры из FastAPI

```python
from pydantic import BaseModel

class EnrollRequest(BaseModel):
    student_id: int
    course_id: int

@app.post("/enrollments/")
def enroll_student(request: EnrollRequest, db: Session = Depends(get_db)):
    """Зачисление студента на курс через процедуру"""
    try:
        db.execute(
            text("CALL enroll_student_to_course(:student_id, :course_id)"),
            {"student_id": request.student_id, "course_id": request.course_id}
        )
        db.commit()
        return {"message": "Student enrolled successfully"}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
```

### Задание для выполнения

1. Создайте процедуру `update_student_grade(p_student_id, p_course_id, p_grade)` с валидацией
2. Добавьте процедуру `archive_old_students(p_year)` для архивации выпускников
3. Реализуйте эндпоинты для вызова этих процедур

---

## 📝 Задание 5: Хранимые функции

### Цель
Создать функции для расчета статистики и использовать их в запросах.

### Шаг 1: Простая функция

```sql
CREATE OR REPLACE FUNCTION get_student_gpa(p_student_id INT)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT COALESCE(AVG(grade), 0)
    FROM grades
    WHERE student_id = p_student_id;
$$;
```

### Шаг 2: Использование в FastAPI

```python
@app.get("/students/{student_id}/gpa")
def get_student_gpa(student_id: int, db: Session = Depends(get_db)):
    """Получение GPA студента через функцию"""
    result = db.execute(
        text("SELECT get_student_gpa(:student_id) as gpa"),
        {"student_id": student_id}
    )
    gpa = result.scalar()
    return {"student_id": student_id, "gpa": float(gpa)}
```

### Шаг 3: Функция, возвращающая таблицу

```sql
CREATE OR REPLACE FUNCTION get_students_by_gpa(p_min_gpa NUMERIC)
RETURNS TABLE(
    student_id INT,
    student_name TEXT,
    gpa NUMERIC
)
LANGUAGE sql
AS $$
    SELECT 
        s.id,
        s.name,
        AVG(g.grade) as avg_grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    GROUP BY s.id, s.name
    HAVING AVG(g.grade) >= p_min_gpa
    ORDER BY avg_grade DESC;
$$;
```

```python
@app.get("/students/by-gpa/{min_gpa}")
def get_students_by_gpa(min_gpa: float, db: Session = Depends(get_db)):
    """Получение студентов с GPA выше указанного"""
    result = db.execute(
        text("SELECT * FROM get_students_by_gpa(:min_gpa)"),
        {"min_gpa": min_gpa}
    )
    students = [dict(row._mapping) for row in result]
    return {"min_gpa": min_gpa, "count": len(students), "data": students}
```

### Задание для выполнения

1. Создайте функцию `calculate_course_difficulty(p_course_id)` - возвращает сложность курса (0-10)
2. Создайте функцию `get_student_ranking()` - возвращает рейтинг всех студентов
3. Реализуйте эндпоинты для использования этих функций

---


