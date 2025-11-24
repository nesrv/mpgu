# Лабораторная работа: Продвинутая работа с PostgreSQL в среде FastAPI

**Дисциплина:** Проектирование и разработка высоконагруженных сервисов  
**Время выполнения:** 4 академических часа  
**МПГУ, 4 курс бакалавриата**

---

## 🎯 Цель работы

Изучить продвинутые возможности PostgreSQL (Views, Materialized Views, Cursors, Functions, Procedures) и интегрировать их с FastAPI через SQLAlchemy и raw SQL.

---

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


@app.post("/sql", summary="Execute SQL Query", description="Execute any SQL query and get results")
def execute_sql_query(sql: SQLQuery, db: Session = Depends(get_db)):
    try:
        # Выполняем запрос (может быть многострочным)
        result = db.execute(text(sql.query))
        db.commit()  
        return {"status": "success", "message": "Query executed successfully"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

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

**Способ 2: Через эндпоинт FastAPI**

```python
# main.py
@app.post("/admin/execute-sql")
def execute_sql(sql_command: str, db: Session = Depends(get_db)):
    """Выполнение произвольных SQL команд (только для разработки!)"""
    try:
        result = db.execute(text(sql_command))
        db.commit()
        
        # Пытаемся получить результат, если это SELECT
        try:
            rows = result.fetchall()
            return {
                "status": "success",
                "rows_affected": len(rows),
                "data": [dict(row._mapping) for row in rows]
            }
        except:
            return {"status": "success", "message": "Command executed"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.post("/admin/init-views")
def init_views(db: Session = Depends(get_db)):
    """Инициализация всех views"""
    try:
        db.execute(text("""
            CREATE OR REPLACE VIEW active_students_view AS
            SELECT id, name, email, created_at
            FROM students
            WHERE status = 'active';
        """))
        db.commit()
        return {"status": "success", "message": "Views created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
```

**Способ 3: Через psql или pgAdmin**

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

**Через Python-скрипт:**

```python
# init_materialized_views.py
from database import engine
from sqlalchemy import text

def create_materialized_views():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS course_statistics AS
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
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_course_stats_id 
            ON course_statistics(course_id);
        """))
        
        conn.commit()
        print("✅ Materialized view created")

if __name__ == "__main__":
    create_materialized_views()
```

**Через эндпоинт:**

```python
@app.post("/admin/init-materialized-views")
def init_materialized_views(db: Session = Depends(get_db)):
    """Создание materialized views"""
    try:
        db.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS course_statistics AS
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
        """))
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_course_stats_id 
            ON course_statistics(course_id);
        """))
        
        db.commit()
        return {"status": "success", "message": "Materialized views created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
```

**Через SQL:**

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

**Через Python-скрипт:**

```python
# init_procedures.py
from database import engine
from sqlalchemy import text

def create_procedures():
    with engine.connect() as conn:
        conn.execute(text("""
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
                SELECT EXISTS(SELECT 1 FROM students WHERE id = p_student_id) INTO v_student_exists;
                IF NOT v_student_exists THEN
                    RAISE EXCEPTION 'Student with id % does not exist', p_student_id;
                END IF;
                
                SELECT EXISTS(SELECT 1 FROM courses WHERE id = p_course_id) INTO v_course_exists;
                IF NOT v_course_exists THEN
                    RAISE EXCEPTION 'Course with id % does not exist', p_course_id;
                END IF;
                
                SELECT EXISTS(
                    SELECT 1 FROM grades 
                    WHERE student_id = p_student_id AND course_id = p_course_id
                ) INTO v_already_enrolled;
                
                IF v_already_enrolled THEN
                    RAISE EXCEPTION 'Student already enrolled in this course';
                END IF;
                
                INSERT INTO grades (student_id, course_id, grade)
                VALUES (p_student_id, p_course_id, 0);
                
                COMMIT;
                
                RAISE NOTICE 'Student % enrolled to course %', p_student_id, p_course_id;
            END;
            $$;
        """))
        conn.commit()
        print("✅ Procedure created")

if __name__ == "__main__":
    create_procedures()
```

**Через эндпоинт:**

```python
@app.post("/admin/init-procedures")
def init_procedures(db: Session = Depends(get_db)):
    """Создание хранимых процедур"""
    try:
        db.execute(text("""
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
                SELECT EXISTS(SELECT 1 FROM students WHERE id = p_student_id) INTO v_student_exists;
                IF NOT v_student_exists THEN
                    RAISE EXCEPTION 'Student with id % does not exist', p_student_id;
                END IF;
                
                SELECT EXISTS(SELECT 1 FROM courses WHERE id = p_course_id) INTO v_course_exists;
                IF NOT v_course_exists THEN
                    RAISE EXCEPTION 'Course with id % does not exist', p_course_id;
                END IF;
                
                SELECT EXISTS(
                    SELECT 1 FROM grades 
                    WHERE student_id = p_student_id AND course_id = p_course_id
                ) INTO v_already_enrolled;
                
                IF v_already_enrolled THEN
                    RAISE EXCEPTION 'Student already enrolled in this course';
                END IF;
                
                INSERT INTO grades (student_id, course_id, grade)
                VALUES (p_student_id, p_course_id, 0);
                
                COMMIT;
            END;
            $$;
        """))
        db.commit()
        return {"status": "success", "message": "Procedures created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
```

**Через SQL:**

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

**Через Python-скрипт:**

```python
# init_functions.py
from database import engine
from sqlalchemy import text

def create_functions():
    with engine.connect() as conn:
        # Функция расчета GPA
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION get_student_gpa(p_student_id INT)
            RETURNS NUMERIC
            LANGUAGE sql
            AS $$
                SELECT COALESCE(AVG(grade), 0)
                FROM grades
                WHERE student_id = p_student_id;
            $$;
        """))
        
        # Функция получения студентов по GPA
        conn.execute(text("""
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
        """))
        
        conn.commit()
        print("✅ Functions created")

if __name__ == "__main__":
    create_functions()
```

**Через эндпоинт:**

```python
@app.post("/admin/init-functions")
def init_functions(db: Session = Depends(get_db)):
    """Создание функций"""
    try:
        db.execute(text("""
            CREATE OR REPLACE FUNCTION get_student_gpa(p_student_id INT)
            RETURNS NUMERIC
            LANGUAGE sql
            AS $$
                SELECT COALESCE(AVG(grade), 0)
                FROM grades
                WHERE student_id = p_student_id;
            $$;
        """))
        
        db.execute(text("""
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
        """))
        
        db.commit()
        return {"status": "success", "message": "Functions created"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
```

**Через SQL:**

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

## 🎓 Контрольные вопросы

1. В чем разница между View и Materialized View?
2. Когда следует использовать курсоры?
3. Чем отличается процедура от функции в PostgreSQL?
4. Какие преимущества дает хранение логики в БД?
5. Как обновить Materialized View без блокировки чтения?

---

## 📊 Критерии оценки

| Задание | Баллы | Описание |
|---------|-------|----------|
| Задание 1 | 20 | Views через raw SQL и SQLAlchemy |
| Задание 2 | 20 | Materialized Views с обновлением |
| Задание 3 | 20 | Курсоры для больших данных |
| Задание 4 | 20 | Хранимые процедуры |
| Задание 5 | 20 | Хранимые функции |
| **Итого** | **100** | |

**Минимальный проходной балл:** 60

---

## 📦 Что сдавать

1. Исходный код проекта (все .py файлы)
2. SQL скрипты (init_db.sql с созданием всех объектов)
3. Скриншоты работы эндпоинтов в Swagger UI
4. Краткий отчет (README.md) с описанием выполненных заданий

**Удачи!** 🚀