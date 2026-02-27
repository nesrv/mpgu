# e-shop

## Архитектура БД

Схема e-shop описывает интернет-магазин: пользователей, товары, корзину, заказы и состав заказов.

**Сущности:**
- **users** — пользователи (user_id, name, created_at)
- **products** — товары (product_id, name, price, description, created_at)
- **orders** — заказы (order_id, user_id, status, total, created_at, updated_at)
- **cart_items** — позиции корзины: хранит товары, добавленные пользователем до оформления заказа. Поля: `cart_item_id`, `user_id`, `product_id`, `quantity`, `price` (цена на момент добавления), `created_at`. Ограничение UNIQUE(user_id, product_id) — один товар один раз на пользователя, количество меняется в той же строке. Связь с users и products по `user_id`, `product_id` (NATURAL JOIN).

- **order_items** — позиции заказа (состав): фиксирует, какие товары и по какой цене вошли в заказ. Поля: `order_item_id`, `order_id`, `product_id`, `quantity`, `price`. Цену храним отдельно: цены в `products` могут меняться, а заказ должен сохранять историческую сумму. Одна строка — одна позиция в заказе; в одном заказе может быть несколько разных товаров.

**Связи:**
- `orders.user_id` → `users.user_id` (у заказа один пользователь)
- `cart_items.user_id` → `users.user_id`, `cart_items.product_id` → `products.product_id`
- `order_items.order_id` → `orders.order_id`, `order_items.product_id` → `products.product_id`

**Особенности:**
- Совпадающие имена колонок (`user_id`, `product_id`) позволяют использовать NATURAL JOIN
- Статусы заказа: ожидает, подтверждён, отправлен, доставлен, отменён, возвращён
- `price` в `cart_items` и `order_items` — снимок цены на момент добавления/оформления

```
users ──┬── orders ─── order_items ─── products
        └── cart_items ─────────────── products
```

## Исходные данные 

```sql
-- PostgreSQL 17+ совместимый синтаксис
-- GENERATED ALWAYS AS IDENTITY, DATE, NUMERIC, TEXT, CHECK, REFERENCES

-- Пользователи (user_id — для NATURAL JOIN с orders, cart_items)
CREATE TABLE users (
    user_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    created_at  DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Товары (product_id — для NATURAL JOIN с cart_items)
CREATE TABLE products (
    product_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    price       NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    description TEXT,
    created_at  DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Заказы 
CREATE TABLE orders (
    order_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users (user_id),
    status      TEXT NOT NULL DEFAULT 'ожидает'
        CHECK (status IN ('ожидает', 'подтверждён', 'отправлен', 'доставлен', 'отменён', 'возвращён')),
    total       NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    created_at  DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at  DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Позиции корзины 
CREATE TABLE cart_items (
    cart_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users (user_id),
    product_id  BIGINT NOT NULL REFERENCES products (product_id),
    quantity    INT NOT NULL CHECK (quantity > 0),
    price       NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    created_at  DATE NOT NULL DEFAULT CURRENT_DATE,
    UNIQUE (user_id, product_id)
);

-- Позиции заказа 
CREATE TABLE order_items (
    order_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id      BIGINT NOT NULL REFERENCES orders (order_id),
    product_id    BIGINT NOT NULL REFERENCES products (product_id),
    quantity      INT NOT NULL CHECK (quantity > 0),
    price         NUMERIC(12, 2) NOT NULL CHECK (price >= 0)
);

CREATE INDEX idx_orders_user_id ON orders (user_id);
CREATE INDEX idx_orders_status ON orders (status);
CREATE INDEX idx_cart_items_product_id ON cart_items (product_id);

-- Фейковые данные (users: 7, products: 5, orders: 9, cart_items: 7; заказы: отменён, возвращён)
INSERT INTO products (name, price, description) VALUES
    ('Ноутбук', 89990.00, '15.6", 16 GB RAM'),
    ('Мышь беспроводная', 1290.00, 'Bluetooth 5.0'),
    ('Клавиатура', 4500.00, 'Механическая RGB'),
    ('Монитор 27"', 34990.00, '4K UHD, IPS'),
    ('Наушники', 5990.00, 'Беспроводные, ANC');

INSERT INTO users (name) VALUES
    ('Иван Петров'),
    ('Мария Сидорова'),
    ('Алексей Козлов'),
    ('Елена Волкова'),
    ('Дмитрий Новиков'),
    ('Ольга Смирнова'),
    ('Сергей Кузнецов');

INSERT INTO orders (user_id, status, total, created_at, updated_at) VALUES
    (1, 'подтверждён', 95490.00, '2026-01-16', '2026-01-16'),
    (2, 'ожидает', 1290.00,    '2026-01-18', '2026-01-18'),
    (3, 'доставлен', 94490.00, '2026-01-11', '2026-01-14'),
    (4, 'отправлен', 40990.00, '2026-01-19', '2026-01-20'),
    (5, 'ожидает', 17880.00,   '2026-01-20', '2026-01-20'),
    (6, 'отменён', 4500.00,    '2026-01-17', '2026-01-18'),
    (1, 'возвращён', 5990.00,  '2026-01-10', '2026-01-20'),
    (5, 'отменён', 89990.00,   '2026-01-19', '2026-01-19'),
    (4, 'возвращён', 34990.00, '2026-01-12', '2026-01-25');

INSERT INTO cart_items (user_id, product_id, quantity, price, created_at) VALUES
    (1, 1, 1, 89990.00, '2026-01-15'),
    (2, 2, 2, 1290.00,  '2026-01-18'),
    (3, 3, 1, 4500.00,  '2026-01-10'),
    (4, 4, 1, 34990.00, '2026-01-19'),
    (5, 5, 3, 5990.00,  '2026-01-20'),
    (6, 3, 1, 4500.00,  '2026-01-17'),
    (7, 1, 1, 89990.00, '2026-01-21');

INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
    (1, 1, 1, 89990.00), (1, 3, 1, 5500.00),
    (2, 2, 2, 1290.00),
    (3, 1, 1, 89990.00), (3, 3, 1, 4500.00),
    (4, 4, 1, 34990.00), (4, 5, 1, 5990.00),
    (5, 5, 3, 5990.00),
    (6, 3, 1, 4500.00),
    (7, 5, 1, 5990.00),
    (8, 1, 1, 89990.00),
    (9, 4, 1, 34990.00), (9, 5, 1, 5990.00);
-- Заказы 7, 9 — возвращён: товары 4 (монитор), 5 (наушники) в возвратах
```

### Описание сценариев (соответствие данным в таблицах)

**Иван Петров** — положил в корзину Ноутбук (15.01.2026), оформил и подтвердил заказ (16.01.2026). Заказ в статусе «подтверждён».

**Мария Сидорова** — положила в корзину 2 шт. Мыши беспроводной (18.01.2026), оформила заказ (18.01.2026), но пока не подтвердила его.

**Алексей Козлов** — положил в корзину Клавиатуру (10.01.2026), подтвердил заказ (11.01.2026), товар доставлен и получен (14.01.2026).

**Елена Волкова** — положила в корзину Монитор 27" (19.01.2026), подтвердила заказ (19.01.2026), товар отправлен (20.01.2026), ожидает доставку.

**Дмитрий Новиков** — положил в корзину 3 шт. Наушников (20.01.2026), оформил заказ (20.01.2026), пока не подтвердил его.

**Ольга Смирнова** — положила в корзину Клавиатуру (17.01.2026), оформила заказ (17.01.2026), затем отменила его (18.01.2026).

**Сергей Кузнецов** — положил в корзину Ноутбук (21.01.2026), заказ не оформлял.

**Иван Петров** — ещё один заказ: Наушники оформлены (10.01.2026), доставлены, возвращены (20.01.2026).

**Дмитрий Новиков** — оформил заказ на Ноутбук (19.01.2026), в тот же день отменил его.

**Елена Волкова** — заказ на Монитор 27" оформлен (12.01.2026), доставлен, возвращён (25.01.2026).

## Задания по углубленному изучению SQL и pl/pgSQL


### Задача 9. EXECUTE (динамический SQL)

Напишите функцию `count_rows(tbl TEXT)` RETURNS BIGINT, возвращающую количество строк в таблице по имени. Используйте EXECUTE.

**Ожидаемый результат** (`count_rows('users')`):

| count_rows |
|------------|
| 7          |

**Решение**

```sql
CREATE OR REPLACE FUNCTION count_rows(...)
...
```

---

### Задача 1. OPEN cur FOR EXECUTE

Напишите функцию `query_by_column(tbl TEXT, col TEXT, val TEXT)` RETURNS SETOF record, выполняющую динамический SELECT по таблице, колонке и значению. Используйте OPEN cur FOR EXECUTE.

**Ожидаемый результат** (`query_by_column('users', 'name', 'Иван Петров')`):

| user_id | name        | created_at |
|---------|-------------|------------|
| 1       | Иван Петров | 2026-01-21 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION query_by_column(...)
...
```

---

### Задача 2. format('%I') и quote_ident

Напишите функцию, которая формирует SQL для `SELECT * FROM <table> LIMIT 1` с использованием `format('%I')` для имени таблицы. Сравните с `quote_ident()`.

**Ожидаемый результат**:

| Вызов | Результат |
|-------|-----------|
| `format('...%I...', 'orders')` | `SELECT * FROM orders LIMIT 1` |
| `format('...%I...', 'my table')` | `SELECT * FROM "my table" LIMIT 1` |
| `quote_ident('orders')` | `orders` |

**Решение**

```sql
SELECT format(...)
...
```

---

### Задача 3. format('%L') и quote_literal

Напишите динамический запрос `SELECT * FROM users WHERE name = '<name>'`, экранируя значение через `format('%L')` и `quote_literal()`.

**Ожидаемый результат**:

| Вызов | Результат |
|-------|-----------|
| `format('...%L', 'Иван Петров')` | `SELECT * FROM users WHERE name = 'Иван Петров'` |
| `format('...%L', '''; DROP TABLE users; --')` | `SELECT * FROM users WHERE name = '''; DROP TABLE users; --'` (экранировано) |
| `quote_literal('safe')` | `'safe'` |

**Решение**

```sql
SELECT format(...)
...
```

---

### Задача 4. quote_nullable

Напишите функцию `find_user_by_name(nm TEXT)`, строящую динамический запрос. Если `nm` = NULL, условие не добавлять. Используйте `quote_nullable()`.

**Ожидаемый результат** (`find_user_by_name('Мария Сидорова')`):

| user_id | name            | created_at |
|---------|-----------------|------------|
| 2       | Мария Сидорова  | 2026-01-21 |

При вызове `find_user_by_name(NULL)` — вернёт всех пользователей (7 строк).

**Решение**

```sql
CREATE OR REPLACE FUNCTION find_user_by_name(...)
...
```

---

### Задача 5. Процедура с OUT

Напишите процедуру `get_order_info(order_id BIGINT, OUT o_user_id BIGINT, OUT o_user_name TEXT, OUT o_total NUMERIC, OUT o_status TEXT)`. Используйте **NATURAL JOIN** `orders` и `users`.

**Ожидаемый результат** (`CALL get_order_info(3, ...)`):

| o_user_id | o_user_name    | o_total  | o_status  |
|-----------|----------------|----------|-----------|
| 3         | Алексей Козлов | 94490.00 | доставлен |

**Решение**

```sql
CREATE OR REPLACE PROCEDURE get_order_info(...)
...
```

---

### Задача 6. Комбинированная: EXECUTE + format + RETURNS TABLE

Напишите функцию `dynamic_select(tbl TEXT, limit_n INT DEFAULT 10)` RETURNS TABLE (id BIGINT, name TEXT). Для `users` — `SELECT user_id, name`. Для `orders` — **NATURAL JOIN** с `users`: `SELECT o.order_id, u.name`. Используйте условную сборку SQL через format.

**Ожидаемый результат** (`dynamic_select('orders', 3)`):

| id | name            |
|----|-----------------|
| 1  | Иван Петров     |
| 2  | Мария Сидорова  |
| 3  | Алексей Козлов  |

**Решение**

```sql
CREATE OR REPLACE FUNCTION dynamic_select(...)
...
```

---


### Задача 7. Реализуйте функцию map, принимающую два параметра:
массив вещественных чисел и название вспомогательной функции, принимающей один параметр вещественного типа.
 
Функция должна возвращать исходный массив, в котором к каждому элементу применена вспомогательная функция.

 Например:
map(ARRAY[4.0,9.0],'sqrt') → ARRAY[2.0,3.0]


**Решение**
```sql
CREATE FUNCTION map(a INOUT float[], func text)
...

```


## Полиморфный вариант функций


```sql

=> CREATE FUNCTION map(...)


-- Требуется фиктивный параметр типа anyelement, чтобы внутри функции объявить переменную такого же типа.

=> SELECT map(ARRAY[4.0,9.0,16.0],'sqrt');
```

---

### Задача 8. Реализуйте функцию apply_discount, принимающую три параметра:
массив идентификаторов товаров (product_id[]), название функции расчёта скидки и процент скидки.

Функция должна возвращать таблицу с product_id, исходной ценой и новой ценой после применения функции скидки.

Например:
```sql
-- Вспомогательная функция для расчёта скидки
CREATE OR REPLACE FUNCTION calc_percent_discount(price NUMERIC, percent NUMERIC)
RETURNS NUMERIC AS $$
    SELECT ROUND(price * (1 - percent / 100), 2);
$$ LANGUAGE sql IMMUTABLE;

-- Вызов
SELECT * FROM apply_discount(ARRAY[1,2,3], 'calc_percent_discount', 10);
```

**Ожидаемый результат**:

| product_id | name              | old_price | new_price |
|------------|-------------------|-----------|-----------|
| 1          | Ноутбук           | 89990.00  | 80991.00  |
| 2          | Мышь беспроводная | 1290.00   | 1161.00   |
| 3          | Клавиатура        | 4500.00   | 4050.00   |

**Решение**

```sql
CREATE OR REPLACE FUNCTION apply_discount(
    product_ids BIGINT[],
    discount_func TEXT,
    discount_percent NUMERIC
)
...
```

---

### Задача 9. Реализуйте функцию transform_orders, принимающую три параметра:
идентификатор пользователя (user_id), текущий статус заказа и название функции-трансформера статуса.

Функция должна возвращать таблицу заказов пользователя с применённым новым статусом (без изменения данных в БД).

Например:
```sql
-- Вспомогательная функция для перехода статуса
CREATE OR REPLACE FUNCTION next_status(current_status TEXT)
RETURNS TEXT AS $$
    SELECT CASE current_status
        WHEN 'ожидает' THEN 'подтверждён'
        WHEN 'подтверждён' THEN 'отправлен'
        WHEN 'отправлен' THEN 'доставлен'
        ELSE current_status
    END;
$$ LANGUAGE sql IMMUTABLE;

-- Вызов: показать, какой статус будет у заказов пользователя 1 после перехода
SELECT * FROM transform_orders(1, 'next_status');
```

**Ожидаемый результат**:

| order_id | user_name   | current_status | next_status |
|----------|-------------|----------------|-------------|
| 1        | Иван Петров | подтверждён    | отправлен   |
| 7        | Иван Петров | возвращён      | возвращён   |

**Решение**

```sql
CREATE OR REPLACE FUNCTION transform_orders(
    uid BIGINT,
    status_func TEXT
)
...
```

---

### Задача 10. Реализуйте функцию aggregate_by_user, принимающую два параметра:
название агрегатной функции (SUM, AVG, MAX, MIN, COUNT) и название числовой колонки из таблицы orders.

Функция должна возвращать таблицу с user_id, именем пользователя и результатом применения агрегатной функции к указанной колонке.

Например:
```sql
-- Вызов: средняя сумма заказов по пользователям
SELECT * FROM aggregate_by_user('AVG', 'total');

-- Вызов: количество заказов по пользователям  
SELECT * FROM aggregate_by_user('COUNT', 'order_id');
```

**Ожидаемый результат** (`aggregate_by_user('SUM', 'total')`):

| user_id | user_name        | agg_result |
|---------|------------------|------------|
| 1       | Иван Петров      | 101480.00  |
| 2       | Мария Сидорова   | 1290.00    |
| 3       | Алексей Козлов   | 94490.00   |
| 4       | Елена Волкова    | 75980.00   |
| 5       | Дмитрий Новиков  | 107870.00  |
| 6       | Ольга Смирнова   | 4500.00    |

**Решение**

```sql
CREATE OR REPLACE FUNCTION aggregate_by_user(
    agg_func TEXT,
    col_name TEXT
)
...
```

---

## Обработка ошибок в PL/pgSQL

### Задача 11. Безопасное добавление товара в корзину с обработкой UNIQUE_VIOLATION

Напишите процедуру `safe_add_to_cart(p_user_id BIGINT, p_product_id BIGINT, p_quantity INT)`, которая добавляет товар в корзину. Если товар уже есть у пользователя (нарушение UNIQUE), увеличить quantity. Используйте блок EXCEPTION для перехвата ошибки.

**Ожидаемый результат**:
```sql
-- Первый вызов: добавляет новую запись
CALL safe_add_to_cart(7, 2, 3);
-- cart_items: user_id=7, product_id=2, quantity=3

-- Второй вызов: увеличивает quantity (UNIQUE_VIOLATION перехвачен)
CALL safe_add_to_cart(7, 2, 2);
-- cart_items: user_id=7, product_id=2, quantity=5
```

| Действие | Результат |
|----------|-----------|
| Первый вызов | INSERT выполнен, quantity=3 |
| Второй вызов | UNIQUE_VIOLATION → UPDATE, quantity=5 |

**Решение**

```sql
CREATE OR REPLACE PROCEDURE safe_add_to_cart(
    p_user_id BIGINT,
    p_product_id BIGINT,
    p_quantity INT
)
...
```

---

### Задача 12. Функция оформления заказа с GET STACKED DIAGNOSTICS

Напишите функцию `create_order_from_cart(p_user_id BIGINT)` RETURNS BIGINT, которая:
1. Создаёт заказ из корзины пользователя
2. Переносит позиции из cart_items в order_items
3. Очищает корзину
4. При любой ошибке логирует детали через GET STACKED DIAGNOSTICS и пробрасывает исключение

**Ожидаемый результат** (`create_order_from_cart(7)`):

| Результат | order_id |
|-----------|----------|
| Успех     | 10       |

При пустой корзине:
```
ERROR: Корзина пользователя 999 пуста
CONTEXT: ...
```

**Решение**

```sql
CREATE OR REPLACE FUNCTION create_order_from_cart(p_user_id BIGINT)
...
```

---

### Задача 13. Процедура изменения статуса заказа с валидацией переходов

Напишите процедуру `change_order_status(p_order_id BIGINT, p_new_status TEXT)`, которая:
1. Проверяет существование заказа (иначе — NO_DATA_FOUND)
2. Проверяет допустимость перехода статуса (иначе — пользовательское исключение)
3. Использует RAISE с разными уровнями: NOTICE, WARNING, EXCEPTION

Допустимые переходы:
- ожидает → подтверждён, отменён
- подтверждён → отправлен, отменён
- отправлен → доставлен
- доставлен → возвращён

**Ожидаемый результат**:
```sql
-- Успешный переход
CALL change_order_status(2, 'подтверждён');
-- NOTICE: Статус заказа 2 изменён: ожидает → подтверждён

-- Недопустимый переход
CALL change_order_status(3, 'ожидает');
-- ERROR: Недопустимый переход статуса: доставлен → ожидает
```

| order_id | old_status | new_status  | Результат |
|----------|------------|-------------|-----------|
| 2        | ожидает    | подтверждён | OK        |
| 3        | доставлен  | ожидает     | ERROR     |
| 6        | отменён    | подтверждён | ERROR     |

**Решение**

```sql
CREATE OR REPLACE PROCEDURE change_order_status(
    p_order_id BIGINT,
    p_new_status TEXT
)
...
```
