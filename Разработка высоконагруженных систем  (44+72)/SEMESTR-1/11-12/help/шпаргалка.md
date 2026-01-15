# 📚 Шпаргалка по PostgreSQL

**Дисциплина:** Проектирование и разработка высоконагруженных сервисов  
**МПГУ, 4 курс бакалавриата**

---

## 📚 Часть 1: Диалект SQL PostgreSQL

### Основные типы данных

```sql
-- Числовые типы
SMALLINT              -- 2 байта, -32768 до +32767
INTEGER (INT)         -- 4 байта, -2147483648 до +2147483647
BIGINT                -- 8 байт, очень большие числа
NUMERIC(10,2)         -- точные десятичные (10 цифр, 2 после запятой)
DECIMAL(10,2)         -- аналог NUMERIC
REAL                  -- 4 байта, 6 знаков точности
DOUBLE PRECISION      -- 8 байт, 15 знаков точности
SERIAL                -- автоинкремент INTEGER
BIGSERIAL             -- автоинкремент BIGINT

-- Строковые типы
CHAR(10)              -- фиксированная длина, дополняется пробелами
VARCHAR(100)          -- переменная длина, до 100 символов
TEXT                  -- неограниченная длина

-- Дата и время
DATE                  -- только дата (2024-01-15)
TIME                  -- только время (14:30:00)
TIMESTAMP             -- дата + время
TIMESTAMPTZ           -- с часовым поясом
INTERVAL              -- временной интервал ('1 day', '2 hours')

-- JSON
JSON                  -- текстовое хранение, медленнее
JSONB                 -- бинарное хранение, быстрее, поддерживает индексы

-- Массивы
INTEGER[]             -- массив целых чисел
TEXT[]                -- массив строк
VARCHAR(50)[]         -- массив varchar

-- Специальные типы
UUID                  -- уникальный идентификатор
BOOLEAN               -- true/false
BYTEA                 -- бинарные данные
INET                  -- IP адрес
MACADDR               -- MAC адрес
POINT, LINE, POLYGON  -- геометрические типы
```

### Полезные функции

```sql
-- Агрегатные функции
COUNT(*)                     -- количество строк
COUNT(DISTINCT column)       -- количество уникальных значений
SUM(amount)                  -- сумма
AVG(grade)                   -- среднее значение
MAX(score), MIN(price)       -- максимум и минимум
STRING_AGG(name, ', ')       -- объединение строк
ARRAY_AGG(id)                -- создание массива

-- Строковые функции
CONCAT(first_name, ' ', last_name)  -- склеивание строк
first_name || ' ' || last_name      -- альтернативный способ
UPPER(name), LOWER(email)           -- верхний/нижний регистр
INITCAP(name)                       -- первая буква заглавная
LENGTH(text)                        -- длина строки
SUBSTRING(text, 1, 10)              -- подстрока
LEFT(text, 5), RIGHT(text, 5)      -- первые/последние N символов
TRIM(text), LTRIM(text), RTRIM(text) -- удаление пробелов
REPLACE(text, 'old', 'new')         -- замена подстроки
SPLIT_PART('a,b,c', ',', 2)         -- разбиение строки (вернет 'b')

-- Дата и время
NOW()                               -- текущие дата и время
CURRENT_DATE                        -- текущая дата
CURRENT_TIME                        -- текущее время
CURRENT_TIMESTAMP                   -- текущая метка времени
DATE_TRUNC('month', created_at)     -- округление до месяца
DATE_PART('year', created_at)       -- извлечение года
EXTRACT(YEAR FROM created_at)       -- альтернативный способ
AGE(birth_date)                     -- возраст
AGE('2024-01-01', '2020-01-01')     -- разница между датами
created_at + INTERVAL '1 day'       -- добавление интервала
created_at - INTERVAL '2 hours'     -- вычитание интервала

-- Работа с JSON/JSONB
jsonb_data->>'key'                  -- получить значение как текст
jsonb_data->'key'                   -- получить значение как JSONB
jsonb_data->'key'->'nested'         -- вложенный доступ
jsonb_data #> '{key,nested}'        -- альтернативный способ
jsonb_data @> '{"key": "value"}'    -- проверка содержимого
jsonb_data ? 'key'                  -- проверка наличия ключа
JSONB_BUILD_OBJECT('key', value)    -- создание JSON объекта
JSONB_AGG(column)                   -- агрегация в JSON массив

-- Математические
ABS(-5)                             -- модуль
ROUND(3.14159, 2)                   -- округление
CEIL(3.2), FLOOR(3.8)               -- округление вверх/вниз
POWER(2, 3)                         -- возведение в степень
SQRT(16)                            -- квадратный корень
RANDOM()                            -- случайное число 0-1

-- Условные выражения
COALESCE(value1, value2, 'default') -- первое не-NULL значение
NULLIF(value1, value2)              -- NULL если равны
CASE 
    WHEN grade >= 90 THEN 'A'
    WHEN grade >= 80 THEN 'B'
    ELSE 'C'
END
```

### Window Functions (Оконные функции)

```sql
-- Ранжирование
ROW_NUMBER() OVER (ORDER BY score DESC)              -- порядковый номер (1,2,3,4...)
RANK() OVER (ORDER BY score DESC)                   -- ранг с пропусками (1,2,2,4...)
DENSE_RANK() OVER (ORDER BY score DESC)             -- ранг без пропусков (1,2,2,3...)
NTILE(4) OVER (ORDER BY score DESC)                 -- разбиение на 4 группы

-- Ранжирование с разбиением на группы
ROW_NUMBER() OVER (PARTITION BY course_id ORDER BY grade DESC)
RANK() OVER (PARTITION BY course_id ORDER BY grade DESC)

-- Агрегация с окном
SUM(amount) OVER (PARTITION BY user_id ORDER BY date)           -- накопительная сумма
AVG(grade) OVER (PARTITION BY student_id ORDER BY date)         -- скользящее среднее
COUNT(*) OVER (PARTITION BY course_id)                          -- количество в группе

-- Скользящее окно
AVG(grade) OVER (
    ORDER BY date 
    ROWS BETWEEN 3 PRECEDING AND CURRENT ROW        -- последние 4 строки
)

SUM(amount) OVER (
    ORDER BY date
    RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW  -- последние 7 дней
)

-- Доступ к соседним строкам
LAG(grade, 1) OVER (ORDER BY date)                  -- предыдущее значение
LEAD(grade, 1) OVER (ORDER BY date)                 -- следующее значение
FIRST_VALUE(grade) OVER (ORDER BY date)             -- первое значение в окне
LAST_VALUE(grade) OVER (ORDER BY date)              -- последнее значение в окне

-- Пример: расчет разницы с предыдущим значением
SELECT 
    date,
    amount,
    amount - LAG(amount) OVER (ORDER BY date) as difference
FROM sales;
```

### Продвинутые JOIN

```sql
-- INNER JOIN - только совпадающие записи
SELECT * FROM students s
INNER JOIN grades g ON s.id = g.student_id;

-- LEFT JOIN - все из левой таблицы
SELECT * FROM students s
LEFT JOIN grades g ON s.id = g.student_id;

-- RIGHT JOIN - все из правой таблицы
SELECT * FROM students s
RIGHT JOIN grades g ON s.id = g.student_id;

-- FULL OUTER JOIN - все из обеих таблиц
SELECT * FROM students s
FULL OUTER JOIN grades g ON s.id = g.student_id;

-- CROSS JOIN - декартово произведение
SELECT * FROM students CROSS JOIN courses;

-- SELF JOIN - соединение таблицы с самой собой
SELECT s1.name as student, s2.name as mentor
FROM students s1
JOIN students s2 ON s1.mentor_id = s2.id;
```

### CTE (Common Table Expressions)

```sql
-- Простой CTE
WITH active_students AS (
    SELECT * FROM students WHERE status = 'active'
)
SELECT * FROM active_students WHERE grade > 80;

-- Несколько CTE
WITH 
    active_students AS (
        SELECT * FROM students WHERE status = 'active'
    ),
    top_grades AS (
        SELECT student_id, AVG(grade) as gpa
        FROM grades
        GROUP BY student_id
        HAVING AVG(grade) > 85
    )
SELECT s.*, t.gpa
FROM active_students s
JOIN top_grades t ON s.id = t.student_id;

-- Рекурсивный CTE (дерево категорий)
WITH RECURSIVE category_tree AS (
    -- Базовый случай
    SELECT id, name, parent_id, 1 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Рекурсивный случай
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;
```

---

## 📚 Часть 2: Продвинутый PostgreSQL

### Views (Представления)

```sql
-- Создание
CREATE VIEW active_students AS
SELECT id, name, email FROM students WHERE status = 'active';

-- Использование
SELECT * FROM active_students;

-- Удаление
DROP VIEW active_students;

-- Обновляемое представление
CREATE VIEW student_info AS
SELECT id, name, email FROM students;

UPDATE student_info SET email = 'new@mail.com' WHERE id = 1;

-- Замена существующего view
CREATE OR REPLACE VIEW active_students AS
SELECT id, name, email, created_at FROM students WHERE status = 'active';
```

### Materialized Views (Материализованные представления)

```sql
-- Создание
CREATE MATERIALIZED VIEW sales_summary AS
SELECT product_id, SUM(amount) as total
FROM orders
GROUP BY product_id;

-- Обновление
REFRESH MATERIALIZED VIEW sales_summary;
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;  -- Без блокировки

-- Удаление
DROP MATERIALIZED VIEW sales_summary;

-- Создание с индексом
CREATE MATERIALIZED VIEW course_stats AS
SELECT course_id, COUNT(*) as student_count
FROM enrollments
GROUP BY course_id;

CREATE INDEX idx_course_stats ON course_stats(course_id);
```

### Cursors (Курсоры)

```sql
-- Объявление и использование
BEGIN;
DECLARE my_cursor CURSOR FOR SELECT * FROM large_table;
FETCH 100 FROM my_cursor;
FETCH 100 FROM my_cursor;
CLOSE my_cursor;
COMMIT;

-- Курсор с прокруткой
BEGIN;
DECLARE my_cursor SCROLL CURSOR FOR SELECT * FROM students;
FETCH NEXT FROM my_cursor;
FETCH PRIOR FROM my_cursor;
FETCH FIRST FROM my_cursor;
FETCH LAST FROM my_cursor;
CLOSE my_cursor;
COMMIT;
```

### Functions (Функции)

```sql
-- Простая SQL функция
CREATE OR REPLACE FUNCTION get_student_count()
RETURNS INTEGER
LANGUAGE sql
AS $$
    SELECT COUNT(*)::INTEGER FROM students;
$$;

-- Функция с параметрами
CREATE OR REPLACE FUNCTION calculate_gpa(p_student_id INT)
RETURNS NUMERIC
LANGUAGE sql
AS $$
    SELECT COALESCE(AVG(grade), 0) FROM grades WHERE student_id = p_student_id;
$$;

-- Функция, возвращающая таблицу
CREATE OR REPLACE FUNCTION get_top_students(p_limit INT)
RETURNS TABLE(student_id INT, student_name TEXT, gpa NUMERIC)
LANGUAGE sql
AS $$
    SELECT s.id, s.name, AVG(g.grade) as avg_grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    GROUP BY s.id, s.name
    ORDER BY avg_grade DESC
    LIMIT p_limit;
$$;

-- Использование
SELECT * FROM get_top_students(10);
SELECT get_student_count();
SELECT calculate_gpa(1);

-- Immutable функция (для оптимизации)
CREATE OR REPLACE FUNCTION calculate_discount(price NUMERIC)
RETURNS NUMERIC
IMMUTABLE
LANGUAGE sql
AS $$
    SELECT price * 0.9;
$$;
```

### Procedures (Процедуры)

```sql
-- Простая SQL процедура
CREATE OR REPLACE PROCEDURE enroll_student(
    p_student_id INT,
    p_course_id INT
)
LANGUAGE sql
AS $$
    INSERT INTO enrollments (student_id, course_id, enrolled_at)
    VALUES (p_student_id, p_course_id, NOW());
$$;

-- Вызов процедуры
CALL enroll_student(1, 101);

-- Процедура с несколькими командами
CREATE OR REPLACE PROCEDURE update_student_status(
    p_student_id INT,
    p_new_status TEXT
)
LANGUAGE sql
AS $$
    UPDATE students 
    SET status = p_new_status, updated_at = NOW()
    WHERE id = p_student_id;
    
    INSERT INTO status_log (student_id, new_status, changed_at)
    VALUES (p_student_id, p_new_status, NOW());
$$;

-- Процедура с транзакцией
CREATE OR REPLACE PROCEDURE transfer_student(
    p_student_id INT,
    p_old_course_id INT,
    p_new_course_id INT
)
LANGUAGE sql
BEGIN ATOMIC
    DELETE FROM enrollments 
    WHERE student_id = p_student_id AND course_id = p_old_course_id;
    
    INSERT INTO enrollments (student_id, course_id, enrolled_at)
    VALUES (p_student_id, p_new_course_id, NOW());
END;
```

### Triggers (Триггеры)

```sql
-- Функция для триггера
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера
CREATE TRIGGER student_update_trigger
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();

-- Триггер для логирования
CREATE OR REPLACE FUNCTION log_student_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO students_log (operation, student_id, changed_at)
    VALUES (TG_OP, NEW.id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER student_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON students
FOR EACH ROW
EXECUTE FUNCTION log_student_changes();
```

### Индексы

```sql
-- B-tree индекс (по умолчанию)
CREATE INDEX idx_students_email ON students(email);

-- Уникальный индекс
CREATE UNIQUE INDEX idx_students_email_unique ON students(email);

-- Составной индекс
CREATE INDEX idx_grades_student_course ON grades(student_id, course_id);

-- Частичный индекс
CREATE INDEX idx_active_students ON students(name) WHERE status = 'active';

-- GIN индекс для JSONB
CREATE INDEX idx_students_data ON students USING GIN(data);

-- Полнотекстовый поиск
CREATE INDEX idx_students_name_fts ON students USING GIN(to_tsvector('russian', name));

-- Удаление индекса
DROP INDEX idx_students_email;
```

### Транзакции

```sql
-- Базовая транзакция
BEGIN;
INSERT INTO students (name, email) VALUES ('John', 'john@test.com');
UPDATE courses SET credits = 4 WHERE id = 1;
COMMIT;

-- Откат транзакции
BEGIN;
DELETE FROM students WHERE id = 1;
ROLLBACK;

-- Точки сохранения
BEGIN;
INSERT INTO students (name) VALUES ('Alice');
SAVEPOINT sp1;
INSERT INTO students (name) VALUES ('Bob');
ROLLBACK TO sp1;  -- Откатываем только Bob
COMMIT;

-- Уровни изоляции
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

---

## 🔍 Оптимизация запросов

### EXPLAIN и ANALYZE

```sql
-- Просмотр плана выполнения
EXPLAIN SELECT * FROM students WHERE email = 'test@test.com';

-- С реальным выполнением
EXPLAIN ANALYZE SELECT * FROM students WHERE email = 'test@test.com';

-- Подробный вывод
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) 
SELECT * FROM students s
JOIN grades g ON s.id = g.student_id;
```

### Полезные команды

```sql
-- Статистика по таблице
SELECT * FROM pg_stat_user_tables WHERE relname = 'students';

-- Размер таблицы
SELECT pg_size_pretty(pg_total_relation_size('students'));

-- Обновление статистики
ANALYZE students;
VACUUM ANALYZE students;

-- Список активных запросов
SELECT pid, query, state, query_start 
FROM pg_stat_activity 
WHERE state = 'active';

-- Убить долгий запрос
SELECT pg_terminate_backend(pid);
```

---

**Удачи в изучении PostgreSQL!** 🚀
