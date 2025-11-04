# SQL ORM SQLAlchemy

---

## Слайд 1: Учебные вопросы и структура занятия

### Учебные вопросы:
1. Основы работы с SQLAlchemy ORM
2. Синхронная и асинхронная работа с БД
3. CRUD операции
4. Отношения между таблицами
5. Продвинутые SQL операции

### Структура занятия:
- Введение в SQLAlchemy (плюсы и минусы)
- Подключение к БД (sync/async)
- Определение моделей и создание таблиц
- CRUD операции
- Отношения: один-ко-многим, многие-ко-многим
- Продвинутые операции: MERGE, UNION, JOIN, JSON

---

## Слайд 2: Плюсы и минусы SQLAlchemy

### ✅ Плюсы:
- Абстракция от конкретной СУБД
- Безопасность (защита от SQL-инъекций)
- Удобная работа с объектами Python
- Автоматическая генерация SQL
- Миграции и версионирование схемы
- Поддержка отношений между таблицами

### ❌ Минусы:
- Производительность ниже чистого SQL
- Сложность изучения
- Overhead при простых запросах
- Сложная отладка сгенерированных запросов
- Ограничения при специфичных операциях СУБД

---

## Слайд 3: Синхронное и асинхронное подключение

### Синхронное подключение:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Создаем движок для подключения к PostgreSQL
# Формат: postgresql://username:password@host:port/database
engine = create_engine('postgresql://user:pass@localhost/db')

# Создаем фабрику сессий, привязанную к движку
Session = sessionmaker(bind=engine)

# Создаем экземпляр сессии для работы с БД
session = Session()
```

### Асинхронное подключение:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Создаем асинхронный движок (требуется asyncpg драйвер)
# Обратите внимание на префикс postgresql+asyncpg://
engine = create_async_engine('postgresql+asyncpg://user:pass@localhost/db')

# Создаем фабрику асинхронных сессий
# expire_on_commit=False - объекты остаются доступными после commit
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Используем асинхронный контекстный менеджер
async with async_session() as session:
    # работа с БД через await
    pass
```

---

## Слайд 4: Плюсы и минусы синхронной и асинхронной работы

### Синхронная работа:
**✅ Плюсы:** Простота, понятность, легкая отладка, совместимость  
**❌ Минусы:** Блокировка потока, низкая производительность при I/O

### Асинхронная работа:
**✅ Плюсы:** Высокая производительность, масштабируемость, эффективное использование ресурсов  
**❌ Минусы:** Сложность кода, сложная отладка, требует async-драйверов

### Когда использовать:
- **Sync:** Скрипты, CLI, простые приложения
- **Async:** Веб-сервисы, высоконагруженные системы, микросервисы

---

## Слайд 5: Определение моделей и создание таблиц

### SQLAlchemy:
```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для всех моделей
Base = declarative_base()

# Определяем модель Пользователь
class User(Base):
    # Указываем имя таблицы в БД
    __tablename__ = 'users'
    
    # Определяем колонки таблицы
    id = Column(Integer, primary_key=True)  # Первичный ключ
    name = Column(String(50), nullable=False)  # Обязательное поле
    email = Column(String(100), unique=True)  # Уникальное поле

# Создаем движок для подключения
engine = create_engine('postgresql://user:pass@localhost/db')

# Создание всех таблиц, определенных в моделях
Base.metadata.create_all(engine)

# Удаление всех таблиц (осторожно!)
Base.metadata.drop_all(engine)
```

### SQL (PostgreSQL):
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE
);

-- Удаление таблицы
DROP TABLE users;
```

---

## Слайд 6: Создание сессии

### SQLAlchemy:
```python
from sqlalchemy.orm import sessionmaker, Session

# Создание фабрики сессий, привязанной к движку
SessionLocal = sessionmaker(bind=engine)

# Традиционный способ использования сессии
session = SessionLocal()
try:
    # работа с БД (add, query, update, delete)
    session.commit()  # Фиксируем изменения в БД
except:
    session.rollback()  # Откатываем изменения при ошибке
finally:
    session.close()  # Обязательно закрываем сессию

# Рекомендуемый способ - с контекстным менеджером
# Автоматически закрывает сессию при выходе из блока
with Session(engine) as session:
    # работа с БД
    session.commit()  # Фиксируем изменения
```

### SQL (PostgreSQL):
```sql
-- В PostgreSQL сессия создается автоматически
-- при подключении к БД

BEGIN; -- начало транзакции
-- SQL операции
COMMIT; -- или ROLLBACK;
```

---

## Слайд 7: CREATE - Создание записи

### SQLAlchemy:
```python
# Создание одного объекта
# Создаем экземпляр модели Пользователь
user = User(name='Иван Иванов', email='ivan@example.com')
# Добавляем объект в сессию (пока только в памяти)
session.add(user)
# Фиксируем изменения в БД (выполняется INSERT)
session.commit()

# Создание нескольких объектов
# Создаем список объектов
users = [
    User(name='Алиса', email='alice@example.com'),
    User(name='Борис', email='boris@example.com')
]
# Добавляем все объекты одной командой
session.add_all(users)
# Фиксируем все изменения
session.commit()
```

### SQL (PostgreSQL):
```sql
-- Вставка одной записи
INSERT INTO users (name, email) 
VALUES ('Иван Иванов', 'ivan@example.com');

-- Вставка нескольких записей
INSERT INTO users (name, email) 
VALUES 
    ('Алиса', 'alice@example.com'),
    ('Борис', 'boris@example.com');
```

---

## Слайд 8: READ - Чтение записей

### SQLAlchemy:
```python
# Получить все записи из таблицы
# all() возвращает список объектов
users = session.query(Пользователь).all()

# Получить первую запись или None
user = session.query(Пользователь).first()

# Получить запись по первичному ключу
user = session.query(Пользователь).get(1)

# Фильтрация по одному условию
# Используем оператор == для сравнения
users = session.query(Пользователь).filter(Пользователь.name == 'Иван').all()

# Фильтрация с несколькими условиями (AND)
# like() - поиск по шаблону, > - сравнение
users = session.query(Пользователь).filter(
    Пользователь.name.like('%Иван%'),  # Содержит 'Иван'
    Пользователь.id > 5  # ID больше 5
).all()
```

### SQL (PostgreSQL):
```sql
-- Все записи
SELECT * FROM users;

-- Первая запись
SELECT * FROM users LIMIT 1;

-- По ID
SELECT * FROM users WHERE id = 1;

-- С фильтрацией
SELECT * FROM users WHERE name = 'Иван';

-- Несколько условий
SELECT * FROM users 
WHERE name LIKE '%Иван%' AND id > 5;
```

---

## Слайд 9: UPDATE - Обновление записей

### SQLAlchemy:
```python
# Обновление одного объекта
# Сначала получаем объект из БД
user = session.query(Пользователь).filter(Пользователь.id == 1).first()
# Изменяем атрибут объекта
user.name = 'Мария Петрова'
# SQLAlchemy автоматически отслеживает изменения
session.commit()

# Массовое обновление без загрузки объектов
# Более эффективно для большого количества записей
session.query(Пользователь).filter(Пользователь.name == 'Иван').update({
    'email': 'newemail@example.com'
})
session.commit()
```

### SQL (PostgreSQL):
```sql
-- Обновление одной записи
UPDATE users 
SET name = 'Мария Петрова' 
WHERE id = 1;

-- Массовое обновление
UPDATE users 
SET email = 'newemail@example.com' 
WHERE name = 'Иван';
```

---

## Слайд 10: DELETE - Удаление записей

### SQLAlchemy:
```python
# Удаление одного объекта
# Сначала получаем объект
user = session.query(Пользователь).filter(Пользователь.id == 1).first()
# Помечаем объект на удаление
session.delete(user)
# Фиксируем удаление
session.commit()

# Массовое удаление без загрузки объектов
# Более эффективно для большого количества записей
session.query(Пользователь).filter(Пользователь.name == 'Иван').delete()
session.commit()
```

### SQL (PostgreSQL):
```sql
-- Удаление одной записи
DELETE FROM users WHERE id = 1;

-- Массовое удаление
DELETE FROM users WHERE name = 'Иван';

-- Удаление всех записей
DELETE FROM users;
```

---

## Слайд 11: Дополнительные операции READ

### SQLAlchemy:
```python
# Сортировка по возрастанию (для убывания: .desc())
users = session.query(Пользователь).order_by(Пользователь.name).all()

# Ограничение количества результатов (пагинация)
users = session.query(Пользователь).limit(10).all()

# Смещение + ограничение (пропускаем 5, берем 10)
users = session.query(Пользователь).offset(5).limit(10).all()
# Подсчет количества записей
count = session.query(Пользователь).count()

# Проверка существования записи (возвращает True/False)
exists = session.query(Пользователь).filter(Пользователь.id == 1).exists()
```

### SQL (PostgreSQL):
```sql
-- Сортировка
SELECT * FROM users ORDER BY name;

-- Ограничение
SELECT * FROM users LIMIT 10;

-- Смещение
SELECT * FROM users OFFSET 5 LIMIT 10;

-- Подсчет
SELECT COUNT(*) FROM users;

-- Проверка существования
SELECT EXISTS(SELECT 1 FROM users WHERE id = 1);
```

---

## Слайд 12: Отношение один-ко-многим

### SQLAlchemy:
```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    # Определяем отношение к Статья (один пользователь - много статей)
    posts = relationship('Post', back_populates='author')

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    # Внешний ключ на таблицу users
    user_id = Column(Integer, ForeignKey('users.id'))
    # Обратное отношение к Пользователь
    author = relationship('User', back_populates='posts')
```

### SQL (PostgreSQL):
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    user_id INTEGER REFERENCES users(id)
);
```

---

## Слайд 13: CRUD для один-ко-многим

### SQLAlchemy:
```python
# Создание с отношением
# Создаем пользователя
user = User(name='Иван')
# Создаем статьи, связывая их с пользователем
post1 = Post(title='Первая статья', author=user)
post2 = Post(title='Вторая статья', author=user)
# Достаточно добавить только пользователь, статьи добавятся автоматически
session.add(user)
session.commit()

# Чтение с отношением (от родителя к детям)
user = session.query(Пользователь).filter(Пользователь.id == 1).first()
# Получаем все статьи пользователя через relationship
posts = user.posts

# Обратное чтение (от ребенка к родителю)
post = session.query(Post).first()
# Получаем автора статьи
author = post.author
```

### SQL (PostgreSQL):
```sql
-- Создание
INSERT INTO users (name) VALUES ('Иван') RETURNING id;
INSERT INTO posts (title, user_id) VALUES 
    ('Первая статья', 1), ('Вторая статья', 1);

-- Чтение с JOIN
SELECT posts.* FROM posts 
JOIN users ON posts.user_id = users.id 
WHERE users.id = 1;

-- Обратное чтение
SELECT users.* FROM users 
JOIN posts ON users.id = posts.user_id 
WHERE posts.id = 1;
```

---

## Слайд 14: Отношение многие-ко-многим

### SQLAlchemy:
```python
from sqlalchemy import Table

# Промежуточная таблица для связи многие-ко-многим
# Создается через Table, а не через класс
student_course = Table('student_course', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    # secondary - указываем промежуточную таблицу
    courses = relationship('Course', secondary=student_course, back_populates='students')

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    # Обратное отношение через ту же промежуточную таблицу
    students = relationship('Student', secondary=student_course, back_populates='courses')
```

### SQL (PostgreSQL):
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100)
);

CREATE TABLE student_course (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
```

---

## Слайд 15: CRUD для многие-ко-многим

### SQLAlchemy:
```python
# Создание связи многие-ко-многим
student = Student(name='Алиса')
course1 = Course(title='Математика')
course2 = Course(title='Физика')
# Добавляем несколько курсов студенту
student.courses.extend([курс1, курс2])
# SQLAlchemy автоматически создаст записи в промежуточной таблице
session.add(student)
session.commit()

# Чтение связанных данных
student = session.query(Student).first()
# Получаем все курсы студента
курсы = student.courses

# Удаление связи (не удаляет сам курс!)
# Удаляется только запись из промежуточной таблицы
student.courses.remove(курс1)
session.commit()
```

### SQL (PostgreSQL):
```sql
-- Создание
INSERT INTO students (name) VALUES ('Алиса') RETURNING id;
INSERT INTO courses (title) VALUES ('Математика'), ('Физика');
INSERT INTO student_course (student_id, course_id) 
VALUES (1, 1), (1, 2);

-- Чтение
SELECT courses.* FROM courses
JOIN student_course ON courses.id = student_course.course_id
WHERE student_course.student_id = 1;

-- Удаление связи
DELETE FROM student_course 
WHERE student_id = 1 AND course_id = 1;
```

---

## Слайд 17: Операция MERGE (UPSERT)

### SQLAlchemy:
```python
from sqlalchemy.dialects.postgresql import insert

# UPSERT с использованием on_conflict_do_update
# Создаем INSERT запрос
stmt = insert(User).values(id=1, name='John', email='john@example.com')
# Добавляем логику: если конфликт по id - обновить
stmt = stmt.on_conflict_do_update(
    index_elements=['id'],  # По какому полю проверять конфликт
    set_=dict(name='John Updated', email='john@example.com')  # Что обновить
)
session.execute(stmt)
session.commit()

# Или через merge (устаревший способ)
# Если объект существует - обновит, иначе - создаст
user = User(id=1, name='John', email='john@example.com')
session.merge(user)
session.commit()
```

### SQL (PostgreSQL):
```sql
-- INSERT ... ON CONFLICT (UPSERT)
INSERT INTO users (id, name, email) 
VALUES (1, 'John', 'john@example.com')
ON CONFLICT (id) 
DO UPDATE SET 
    name = 'John Updated', 
    email = 'john@example.com';

-- Или с EXCLUDED
INSERT INTO users (id, name, email) 
VALUES (1, 'John', 'john@example.com')
ON CONFLICT (id) 
DO UPDATE SET 
    name = EXCLUDED.name, 
    email = EXCLUDED.email;
```

---

## Слайд 18: Операции UNION, INTERSECT, EXCEPT

### SQLAlchemy:
```python
from sqlalchemy import union, intersect, except_

# UNION - объединение результатов (без дубликатов)
# Создаем два запроса
query1 = session.query(User.name).filter(User.id < 5)
query2 = session.query(User.name).filter(User.id > 10)
# Объединяем результаты
result = union(query1, query2).all()

# INTERSECT - пересечение (только общие элементы)
result = intersect(query1, query2).all()

# EXCEPT - разность (элементы из query1, которых нет в query2)
# except_ с подчеркиванием, т.к. except - зарезервированное слово
result = except_(query1, query2).all()

# UNION ALL (с дубликатами, быстрее)
result = union(query1, query2).union_all().all()
```

### SQL (PostgreSQL):
```sql
-- UNION (без дубликатов)
SELECT name FROM users WHERE id < 5
UNION
SELECT name FROM users WHERE id > 10;

-- INTERSECT
SELECT name FROM users WHERE id < 5
INTERSECT
SELECT name FROM users WHERE id > 10;

-- EXCEPT
SELECT name FROM users WHERE id < 5
EXCEPT
SELECT name FROM users WHERE id > 10;

-- UNION ALL (с дубликатами)
SELECT name FROM users WHERE id < 5
UNION ALL
SELECT name FROM users WHERE id > 10;
```

---

## Слайд 19: Виды JOIN

### SQLAlchemy:
```python
from sqlalchemy.orm import joinedload

# INNER JOIN (по умолчанию) - только совпадающие записи
# SQLAlchemy автоматически определяет условие по relationship
result = session.query(User).join(Post).all()

# LEFT JOIN - все записи из левой таблицы + совпадения
result = session.query(User).outerjoin(Post).all()

# RIGHT JOIN (через переворот таблиц)
# В SQLAlchemy нет прямого RIGHT JOIN, меняем местами таблицы
result = session.query(Post).outerjoin(User).all()

# FULL OUTER JOIN - все записи из обеих таблиц
result = session.query(User).outerjoin(Post, full=True).all()

# Явное указание условия JOIN (если нет relationship)
result = session.query(User).join(Post, User.id == Post.user_id).all()
```

### SQL (PostgreSQL):
```sql
-- INNER JOIN
SELECT users.* FROM users 
INNER JOIN posts ON users.id = posts.user_id;

-- LEFT JOIN
SELECT users.* FROM users 
LEFT JOIN posts ON users.id = posts.user_id;

-- RIGHT JOIN
SELECT users.* FROM users 
RIGHT JOIN posts ON users.id = posts.user_id;

-- FULL OUTER JOIN
SELECT users.* FROM users 
FULL OUTER JOIN posts ON users.id = posts.user_id;

-- NATURAL JOIN (автоматическое соединение)
SELECT * FROM users NATURAL JOIN posts;
```

---

## Слайд 20: Работа с JSON полями

### SQLAlchemy:
```python
from sqlalchemy.dialects.postgresql import JSON, JSONB

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    # JSONB - бинарный JSON, быстрее для запросов, поддерживает индексы
    attributes = Column(JSONB)

# Создание записи с JSON данными
# Передаем обычный Python dict
product = Product(name='Laptop', attributes={'color': 'black', 'ram': 16})
session.add(product)
session.commit()

# Запрос по JSON полю
# ['color'] - доступ к ключу, astext - преобразование в текст
products = session.query(Product).filter(
    Product.attributes['color'].astext == 'black'
).all()

# Обновление JSON поля
# Можно работать как с обычным dict
product.attributes['ram'] = 32
session.commit()
```

### SQL (PostgreSQL):
```sql
-- Создание таблицы с JSONB
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes JSONB
);

-- Вставка
INSERT INTO products (name, attributes) 
VALUES ('Laptop', '{"color": "black", "ram": 16}');

-- Запрос по JSON
SELECT * FROM products 
WHERE attributes->>'color' = 'black';

-- Обновление JSON
UPDATE products 
SET attributes = jsonb_set(attributes, '{ram}', '32')
WHERE id = 1;
```

---

## Слайд 21: Продвинутые JSON операции

### SQLAlchemy:
```python
from sqlalchemy.dialects.postgresql import JSONB

# Проверка существования ключа в JSON
# has_key() - проверяет наличие ключа на верхнем уровне
products = session.query(Product).filter(
    Product.attributes.has_key('color')
).all()

# Проверка, что JSON содержит указанные ключ-значение
# contains() - оператор @> в PostgreSQL
products = session.query(Product).filter(
    Product.attributes.contains({'color': 'black'})
).all()

# Извлечение вложенных значений (nested JSON)
# Используем цепочку ['key1']['key2']
products = session.query(Product).filter(
    Product.attributes['specs']['cpu'].astext == 'Intel'
).all()
```

### SQL (PostgreSQL):
```sql
-- Проверка существования ключа
SELECT * FROM products 
WHERE attributes ? 'color';

-- Содержит значение
SELECT * FROM products 
WHERE attributes @> '{"color": "black"}';

-- Вложенные значения
SELECT * FROM products 
WHERE attributes->'specs'->>'cpu' = 'Intel';

-- Массив ключей
SELECT * FROM products 
WHERE attributes ?| array['color', 'size'];
```

---

## Слайд 22: Агрегатные функции

### SQLAlchemy:
```python
from sqlalchemy import func

# COUNT - подсчет количества записей
# scalar() - возвращает одно значение
count = session.query(func.count(User.id)).scalar()

# Агрегатные функции
# SUM - сумма, AVG - среднее, MIN - минимум, MAX - максимум
total = session.query(func.sum(Product.price)).scalar()
avg_price = session.query(func.avg(Product.price)).scalar()
min_price = session.query(func.min(Product.price)).scalar()
max_price = session.query(func.max(Product.price)).scalar()

# GROUP BY - группировка результатов
# Подсчитываем количество постов для каждого пользователя
result = session.query(
    User.name, 
    func.count(Post.id)
).join(Post).group_by(User.name).all()

# HAVING - фильтрация после группировки
# Оставляем только пользователей с более чем 5 постами
result = session.query(User.name, func.count(Post.id))\
    .join(Post).group_by(User.name)\
    .having(func.count(Post.id) > 5).all()
```

### SQL (PostgreSQL):
```sql
-- COUNT
SELECT COUNT(id) FROM users;

-- Агрегатные функции
SELECT SUM(price), AVG(price), MIN(price), MAX(price) 
FROM products;

-- GROUP BY
SELECT users.name, COUNT(posts.id) 
FROM users 
JOIN posts ON users.id = posts.user_id 
GROUP BY users.name;

-- HAVING
SELECT users.name, COUNT(posts.id) 
FROM users 
JOIN posts ON users.id = posts.user_id 
GROUP BY users.name 
HAVING COUNT(posts.id) > 5;
```

---

## Слайд 23: Подзапросы и CTE

### SQLAlchemy:
```python
from sqlalchemy import select

# Подзапрос (subquery) - запрос внутри запроса
# Находим среднюю цену и ищем товары дороже
subq = session.query(func.avg(Product.price)).scalar_subquery()
products = session.query(Product).filter(Product.price > subq).all()

# CTE (Common Table Expression) - временная именованная таблица
# Создаем CTE с пользователями
cte = session.query(User.id, User.name).filter(User.id < 10).cte()
# Используем CTE в основном запросе, cte.c - доступ к колонкам
result = session.query(cte, Post).join(Post, cte.c.id == Post.user_id).all()

# Рекурсивный CTE - для иерархических данных (деревья)
# Базовый случай - корневая категория
cte = select([Category.id, Category.parent_id]).where(Category.id == 1).cte(recursive=True)
# Рекурсивная часть - потомки
cte = cte.union_all(
    select([Category.id, Category.parent_id]).where(Category.parent_id == cte.c.id)
)
```

### SQL (PostgreSQL):
```sql
-- Подзапрос
SELECT * FROM products 
WHERE price > (SELECT AVG(price) FROM products);

-- CTE
WITH user_cte AS (
    SELECT id, name FROM users WHERE id < 10
)
SELECT * FROM user_cte 
JOIN posts ON user_cte.id = posts.user_id;

-- Рекурсивный CTE
WITH RECURSIVE category_tree AS (
    SELECT id, parent_id FROM categories WHERE id = 1
    UNION ALL
    SELECT c.id, c.parent_id FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

---

## Слайд 24: Транзакции и блокировки

### SQLAlchemy:
```python
# Явная транзакция с автоматическим управлением
# При успехе - commit, при ошибке - rollback
with session.begin():
    user = User(name='John')
    session.add(user)
    # автоматический commit или rollback

# Вложенные транзакции (savepoints)
# Позволяют откатить часть изменений, не трогая остальные
with session.begin_nested():
    session.add(user)
    # можно откатить только эту часть

# Блокировка FOR UPDATE - эксклюзивная блокировка
# Другие транзакции не смогут читать/изменять запись
user = session.query(User).filter(User.id == 1)\
    .with_for_update().first()

# Блоировка FOR SHARE - разделяемая блокировка
# Другие могут читать, но не изменять
user = session.query(User).filter(User.id == 1)\
    .with_for_update(read=True).first()
```

### SQL (PostgreSQL):
```sql
-- Транзакция
BEGIN;
INSERT INTO users (name) VALUES ('John');
COMMIT; -- или ROLLBACK;

-- Savepoint
BEGIN;
SAVEPOINT sp1;
INSERT INTO users (name) VALUES ('John');
ROLLBACK TO sp1;
COMMIT;

-- Блокировка FOR UPDATE
SELECT * FROM users WHERE id = 1 FOR UPDATE;

-- Блокировка FOR SHARE
SELECT * FROM users WHERE id = 1 FOR SHARE;
```

---

## Слайд 25: Best Practices и заключение

### Рекомендации:
1. **Используйте connection pooling** для оптимизации подключений
2. **Eager loading** (joinedload, selectinload) для избежания N+1 проблемы
3. **Индексы** на часто используемые поля для фильтрации
4. **Batch операции** для массовых вставок/обновлений
5. **Async** для высоконагруженных приложений
6. **Миграции** (Alembic) для управления схемой БД

### Типичные ошибки:
- Забывать commit() после изменений
- N+1 проблема при загрузке связанных объектов
- Не закрывать сессии
- Использовать sync в async контексте

### Полезные ресурсы:
- Документация: https://docs.sqlalchemy.org
- Alembic (миграции): https://alembic.sqlalchemy.org
- PostgreSQL документация: https://www.postgresql.org/docs/
