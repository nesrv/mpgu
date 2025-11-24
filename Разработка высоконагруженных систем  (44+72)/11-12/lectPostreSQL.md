# 🐘 PostgreSQL: Магия продвинутых возможностей

**Теория**  
Дисциплина: Проектирование и разработка высоконагруженных сервисов  
МПГУ, 4 курс бакалавриата

> "PostgreSQL — это не просто база данных, это швейцарский нож для данных" 🔪

---

## Слайд 1: 🚀 Современные возможности PostgreSQL

### Почему PostgreSQL — король среди СУБД?

**🎯 Топ-возможности:**
- ✅ **ACID-транзакции** — надежность как в банке
- ✅ **JSONB** — NoSQL внутри SQL
- ✅ **Full-Text Search** — свой поисковик без Elasticsearch
- ✅ **Расширения** — PostGIS, TimescaleDB, pg_stat_statements
- ✅ **Партиционирование** — делим таблицы на части
- ✅ **Параллельные запросы** — используем все ядра CPU

### 🔥 Что изучим сегодня:
1. **Views** — виртуальные таблицы для ленивых
2. **Materialized Views** — кэш на уровне БД
3. **Cursors** — читаем миллионы строк без паники
4. **Procedures & Functions** — логика прямо в базе
5. **Custom Types** — создаем свои типы данных
6. **Rules** — автоматизация на максималках

---

## Слайд 2: 👁️ Представления (Views) — Виртуальная реальность для данных

### Что такое View?
**View** — это сохраненный SQL-запрос, который выглядит как таблица, но не хранит данные.

### 💡 Зачем нужны?
- 🔒 **Безопасность**: скрываем чувствительные колонки
- 🎨 **Упрощение**: сложный запрос → простая таблица
- 🔄 **Переиспользование**: один раз написал — используй везде

### Пример: Создаем view для активных студентов

```sql
-- Создаем представление
CREATE VIEW active_students AS
SELECT 
    id,
    name,
    email,
    course_name
FROM students
WHERE status = 'active'
  AND graduation_year >= 2024;

-- Используем как обычную таблицу
SELECT * FROM active_students WHERE course_name = 'Python';
```

**🎭 Магия**: При каждом обращении к view выполняется исходный запрос!

---

## Слайд 3: 👁️ Views — Продвинутые фишки

### 🔄 Обновляемые представления

```sql
-- Простое представление можно обновлять
CREATE VIEW student_emails AS
SELECT id, name, email FROM students;

-- Это работает! 🎉
UPDATE student_emails SET email = 'new@example.com' WHERE id = 1;
```

### ⚠️ Когда view НЕ обновляемый?
- Есть JOIN с несколькими таблицами
- Используется GROUP BY, DISTINCT, UNION
- Есть агрегатные функции (COUNT, SUM, AVG)

### 🛡️ View для безопасности

```sql
-- Скрываем зарплаты от любопытных глаз
CREATE VIEW public_employees AS
SELECT 
    id,
    name,
    position,
    department
    -- salary НЕ включаем!
FROM employees;

-- Даем доступ только к view
GRANT SELECT ON public_employees TO intern_role;
```

---

## Слайд 4: 💎 Материализованные представления — Кэш на стероидах

### Проблема обычных Views
```sql
-- Этот запрос выполняется КАЖДЫЙ РАЗ 😱
CREATE VIEW sales_report AS
SELECT 
    product_id,
    SUM(amount) as total_sales,
    COUNT(*) as order_count
FROM orders
GROUP BY product_id;

-- 1 миллион строк → 5 секунд на каждый запрос 🐌
```

### Решение: Materialized View

```sql
-- Создаем материализованное представление
CREATE MATERIALIZED VIEW sales_report_cached AS
SELECT 
    product_id,
    SUM(amount) as total_sales,
    COUNT(*) as order_count,
    NOW() as last_updated
FROM orders
GROUP BY product_id;

-- Теперь запрос мгновенный! ⚡
SELECT * FROM sales_report_cached;
```

**🎯 Разница**: Данные физически хранятся на диске!

---

## Слайд 5: 💎 Materialized Views — Обновление данных

### 🔄 Как обновлять кэш?

```sql
-- Полное обновление (пересчитываем все)
REFRESH MATERIALIZED VIEW sales_report_cached;

-- Конкурентное обновление (без блокировки чтения)
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_report_cached;
```

### ⚡ Автоматическое обновление через cron

```sql
-- Создаем функцию для обновления
CREATE OR REPLACE FUNCTION refresh_sales_report()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY sales_report_cached;
END;
$$ LANGUAGE plpgsql;

-- Настраиваем обновление каждый час через pg_cron
SELECT cron.schedule('refresh-sales', '0 * * * *', 'SELECT refresh_sales_report()');
```

### 📊 Когда использовать?
✅ Тяжелые аналитические запросы  
✅ Отчеты, которые обновляются раз в час/день  
✅ Дашборды с метриками  
❌ Данные в реальном времени  

---

## Слайд 6: 🎯 Курсоры (Cursors) — Читаем Big Data порциями

### Проблема: Миллион строк в памяти

```sql
-- Это убьет вашу память! 💀
SELECT * FROM huge_table; -- 10 миллионов строк
```

### Решение: Курсоры

**Курсор** — это указатель на результат запроса, который читает данные порциями.

```sql
-- Начинаем транзакцию
BEGIN;

-- Объявляем курсор
DECLARE student_cursor CURSOR FOR 
    SELECT id, name, email FROM students;

-- Читаем первые 100 строк
FETCH 100 FROM student_cursor;

-- Читаем следующие 100
FETCH 100 FROM student_cursor;

-- Закрываем курсор
CLOSE student_cursor;
COMMIT;
```

**🎯 Преимущество**: Память не взрывается!

---

## Слайд 7: 🎯 Курсоры — Продвинутое использование

### 🔄 Навигация по курсору

```sql
BEGIN;
DECLARE my_cursor SCROLL CURSOR FOR SELECT * FROM students;

-- Вперед
FETCH NEXT FROM my_cursor;

-- Назад
FETCH PRIOR FROM my_cursor;

-- К первой записи
FETCH FIRST FROM my_cursor;

-- К последней
FETCH LAST FROM my_cursor;

-- Пропустить 10 записей
FETCH ABSOLUTE 10 FROM my_cursor;

CLOSE my_cursor;
COMMIT;
```

### 🐍 Использование в Python

```python
import psycopg2

conn = psycopg2.connect("dbname=mydb")
cur = conn.cursor(name='my_cursor')  # Серверный курсор

cur.execute("SELECT * FROM huge_table")

# Читаем по 1000 строк
while True:
    rows = cur.fetchmany(1000)
    if not rows:
        break
    process_batch(rows)  # Обрабатываем порцию

cur.close()
conn.close()
```

---

## Слайд 8: ⚙️ Хранимые процедуры — Логика в базе данных

### Процедура vs Функция

| Процедура (PROCEDURE) | Функция (FUNCTION) |
|----------------------|--------------------|
| Не возвращает значение | Возвращает значение |
| Может делать COMMIT | Не может делать COMMIT |
| Вызов: `CALL proc()` | Вызов: `SELECT func()` |

### 🎯 Создаем процедуру для зачисления студента

```sql
CREATE OR REPLACE PROCEDURE enroll_student(
    p_student_id INT,
    p_course_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Проверяем, есть ли места
    IF (SELECT count(*) FROM enrollments WHERE course_id = p_course_id) >= 30 THEN
        RAISE EXCEPTION 'Курс переполнен!';
    END IF;
    
    -- Зачисляем студента
    INSERT INTO enrollments (student_id, course_id, enrolled_at)
    VALUES (p_student_id, p_course_id, NOW());
    
    -- Отправляем уведомление
    INSERT INTO notifications (student_id, message)
    VALUES (p_student_id, 'Вы зачислены на курс!');
    
    COMMIT;  -- Процедура может делать commit!
END;
$$;

-- Вызов
CALL enroll_student(123, 456);
```

---

## Слайд 9: 🔧 Функции — Возвращаем результаты

### Простая функция

```sql
CREATE OR REPLACE FUNCTION get_student_gpa(p_student_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_gpa NUMERIC;
BEGIN
    SELECT AVG(grade) INTO v_gpa
    FROM grades
    WHERE student_id = p_student_id;
    
    RETURN COALESCE(v_gpa, 0);
END;
$$;

-- Использование
SELECT name, get_student_gpa(id) as gpa
FROM students;
```

### 📊 Функция, возвращающая таблицу

```sql
CREATE OR REPLACE FUNCTION get_top_students(p_limit INT)
RETURNS TABLE(
    student_id INT,
    student_name TEXT,
    gpa NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        AVG(g.grade) as avg_grade
    FROM students s
    JOIN grades g ON s.id = g.student_id
    GROUP BY s.id, s.name
    ORDER BY avg_grade DESC
    LIMIT p_limit;
END;
$$;

-- Использование
SELECT * FROM get_top_students(10);
```

---

## Слайд 10: 🔧 Функции — SQL vs PL/pgSQL

### SQL функции (быстрее!)

```sql
-- Простая SQL функция
CREATE OR REPLACE FUNCTION get_active_count()
RETURNS BIGINT
LANGUAGE sql
AS $$
    SELECT COUNT(*) FROM students WHERE status = 'active';
$$;

-- Inline в запросе!
SELECT get_active_count();
```

### 🚀 Иммутабельные функции (для оптимизации)

```sql
CREATE OR REPLACE FUNCTION calculate_discount(price NUMERIC)
RETURNS NUMERIC
IMMUTABLE  -- Результат всегда одинаковый для одних входных данных
LANGUAGE sql
AS $$
    SELECT price * 0.9;
$$;

-- PostgreSQL может кэшировать результат!
SELECT product_name, calculate_discount(price)
FROM products;
```

### ⚡ Типы стабильности функций

| Тип | Описание | Пример |
|-----|----------|--------|
| **IMMUTABLE** | Всегда одинаковый результат | `calculate_discount(100)` |
| **STABLE** | Одинаковый в рамках запроса | `get_current_user()` |
| **VOLATILE** | Может меняться (по умолчанию) | `NOW()`, `random()` |

---

## Слайд 11: 🎨 Составные типы данных — Создаем свои типы

### Зачем нужны кастомные типы?

```sql
-- Было: много параметров 😵
CREATE FUNCTION create_order(
    p_customer_name TEXT,
    p_customer_email TEXT,
    p_customer_phone TEXT,
    p_product_id INT,
    p_quantity INT
) ...

-- Стало: один параметр 😎
CREATE TYPE customer_info AS (
    name TEXT,
    email TEXT,
    phone TEXT
);

CREATE FUNCTION create_order(
    p_customer customer_info,
    p_product_id INT,
    p_quantity INT
) ...
```

### 🏗️ Создание составного типа

```sql
-- Определяем тип "Адрес"
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT
);

-- Используем в таблице
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    home_address address,
    work_address address
);

-- Вставка данных
INSERT INTO customers (name, home_address, work_address)
VALUES (
    'Иван Иванов',
    ROW('Ленина 1', 'Москва', '101000', 'Россия')::address,
    ROW('Пушкина 2', 'Москва', '102000', 'Россия')::address
);

-- Доступ к полям
SELECT name, (home_address).city FROM customers;
```

---

## Слайд 12: 📜 Правила (Rules) — Автоматизация запросов

### Что такое Rules?

**Rule** — это механизм перезаписи запросов на лету.

> ⚠️ **Внимание**: Rules считаются устаревшими! Используйте триггеры вместо них.

### 🔄 Пример: Перенаправление INSERT

```sql
-- Создаем архивную таблицу
CREATE TABLE students_archive (
    LIKE students INCLUDING ALL
);

-- Создаем правило: старые студенты → в архив
CREATE RULE archive_old_students AS
    ON INSERT TO students
    WHERE NEW.graduation_year < 2020
    DO INSTEAD
        INSERT INTO students_archive VALUES (NEW.*);

-- Теперь старые студенты автоматически попадают в архив
INSERT INTO students (name, graduation_year)
VALUES ('Петр', 2019);  -- Попадет в students_archive!
```

### 🎭 Правило для логирования

```sql
CREATE TABLE students_log (
    operation TEXT,
    student_id INT,
    changed_at TIMESTAMP
);

CREATE RULE log_student_updates AS
    ON UPDATE TO students
    DO ALSO
        INSERT INTO students_log (operation, student_id, changed_at)
        VALUES ('UPDATE', NEW.id, NOW());
```

---

## Слайд 13: 📜 Rules vs Triggers — Что выбрать?

### Сравнение

| Аспект | Rules | Triggers |
|--------|-------|----------|
| **Когда выполняется** | До выполнения запроса | После/вместо запроса |
| **Производительность** | Быстрее для массовых операций | Медленнее, но гибче |
| **Гибкость** | Ограниченная | Полная (можно писать код) |
| **Рекомендация** | ❌ Устарели | ✅ Используйте их! |

### ✅ Современный подход: Триггеры

```sql
-- Создаем функцию для триггера
CREATE OR REPLACE FUNCTION log_student_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO students_log (operation, student_id, changed_at)
    VALUES (TG_OP, NEW.id, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создаем триггер
CREATE TRIGGER student_changes_trigger
AFTER INSERT OR UPDATE OR DELETE ON students
FOR EACH ROW
EXECUTE FUNCTION log_student_changes();
```

**🎯 Вывод**: Забудьте про Rules, используйте Triggers!

---

## Слайд 14: 🎓 Выводы и best practices

### 📚 Что мы изучили:

✅ **Views** — для упрощения сложных запросов  
✅ **Materialized Views** — для кэширования тяжелых отчетов  
✅ **Cursors** — для обработки больших объемов данных  
✅ **Procedures & Functions** — для бизнес-логики в БД  
✅ **Custom Types** — для структурирования данных  
✅ **Rules** — устарели, используйте Triggers  

### 🎯 Best Practices:

1. **Views**: используйте для безопасности и переиспользования
2. **Materialized Views**: обновляйте регулярно через cron
3. **Cursors**: только для больших данных (>100k строк)
4. **Functions**: помечайте IMMUTABLE/STABLE для оптимизации
5. **Procedures**: для транзакционной логики
6. **Custom Types**: для читаемости кода
7. **Rules**: НЕ используйте, только Triggers!

### 🚀 Следующий шаг:
Практика! Создайте свою БД с views, functions и triggers.

**Вопросы?** 🙋‍♂️



