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

---

### Задача 1. Функция pl/pgSQL

Напишите функцию `get_user_orders_count(user_id BIGINT)`, возвращающую `(user_name TEXT, orders_count BIGINT)`. Используйте **NATURAL LEFT JOIN** `orders` и `users` (общая колонка `user_id`).

**Ожидаемый результат** (`get_user_orders_count(1)`):

| user_name    | orders_count |
|--------------|--------------|
| Иван Петров  | 2            |

**Решение**

```sql
CREATE OR REPLACE FUNCTION get_user_orders_count(...)
...
```

---

### Задача 2. Процедура

Напишите процедуру `change_order_status(order_id BIGINT, new_status TEXT)`, которая обновляет статус заказа.

**Ожидаемый результат** (`CALL change_order_status(2, 'подтверждён')`):

Статус заказа 2 изменится с «ожидает» на «подтверждён». Процедура не возвращает данных.

**Решение**

```sql
CREATE OR REPLACE PROCEDURE change_order_status(...)
...
```

---

### Задача 3. RETURNING

Напишите функцию `add_product(name TEXT, price NUMERIC, descr TEXT)`, которая вставляет товар и возвращает вставленную строку через RETURNING.

**Ожидаемый результат** (`add_product('Веб-камера', 3990.00, '1080p')`):

| product_id | name       | price   | description | created_at |
|------------|------------|---------|-------------|------------|
| 6          | Веб-камера | 3990.00 | 1080p       | 2026-01-21 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION add_product(...)
...
```

---

### Задача 4. RETURN QUERY

Напишите функцию `orders_by_status(st TEXT)`, возвращающую заказы с заданным статусом и именем пользователя. Используйте RETURN QUERY и **NATURAL JOIN** `orders` с `users` (по `user_id`).

**Ожидаемый результат** (`orders_by_status('ожидает')`):

| order_id | user_name        | status  | total    | created_at |
|----------|------------------|---------|----------|------------|
| 2        | Мария Сидорова   | ожидает | 1290.00  | 2026-01-18 |
| 5        | Дмитрий Новиков  | ожидает | 17880.00 | 2026-01-20 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION orders_by_status(...)
...
```

---

### Задача 5. RETURNS SETOF

Напишите функцию `expensive_products(threshold NUMERIC)` RETURNS TABLE, возвращающую товары дороже порога с дополнительной колонкой `total_in_carts BIGINT` — суммарное количество единиц этого товара во всех корзинах. Используйте RETURNS TABLE, **NATURAL LEFT JOIN** с `cart_items` и `GROUP BY`.

**Ожидаемый результат** (`expensive_products(10000)`):

| product_id | name        | price    | description     | created_at | total_in_carts |
|------------|-------------|----------|-----------------|------------|----------------|
| 1          | Ноутбук     | 89990.00 | 15.6", 16 GB RAM | 2026-01-21 | 2              |
| 4          | Монитор 27" | 34990.00 | 4K UHD, IPS     | 2026-01-21 | 1              |

**Решение**

```sql
CREATE OR REPLACE FUNCTION expensive_products(...)
...
```

---

### Задача 6. RETURNS TABLE

Напишите функцию `user_order_summary(user_id BIGINT)`, возвращающую `order_id`, `user_name`, `status`, `total`. Используйте RETURNS TABLE и **NATURAL JOIN** `orders` с `users`.

**Ожидаемый результат** (`user_order_summary(1)`):

| order_id | user_name   | status      | total    |
|----------|-------------|-------------|----------|
| 1        | Иван Петров | подтверждён | 95490.00 |
| 7        | Иван Петров | возвращён   | 5990.00  |

**Решение**

```sql
CREATE OR REPLACE FUNCTION user_order_summary(...)
...
```

---

### Задача 7. REFCURSOR

Напишите функцию `open_user_orders(p_user_id BIGINT)` RETURNS refcursor, открывающую курсор по заказам пользователя с именем. Используйте **NATURAL JOIN** `orders` и `users`.

**Ожидаемый результат** (`open_user_orders(4)`, затем `FETCH ALL FROM user_orders_cur`):

| order_id | user_id | user_name     | status    | total    | created_at |
|----------|---------|---------------|-----------|----------|------------|
| 4        | 4       | Елена Волкова | отправлен | 40990.00 | 2026-01-19 |
| 9        | 4       | Елена Волкова | возвращён | 34990.00 | 2026-01-12 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION open_user_orders(...)
...
```

---

### Задача 8. CURSOR

Напишите функцию, использующую объявленный CURSOR для обхода товаров и возврата их имён через RETURNS SETOF TEXT.

**Ожидаемый результат** (`product_names()`):

| product_names     |
|-------------------|
| Ноутбук           |
| Мышь беспроводная |
| Клавиатура        |
| Монитор 27"       |
| Наушники          |

**Решение**

```sql
CREATE OR REPLACE FUNCTION product_names(...)
...
```

---

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

### Задача 10. OPEN cur FOR EXECUTE

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

### Задача 11. format('%I') и quote_ident

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

### Задача 12. format('%L') и quote_literal

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

### Задача 13. quote_nullable

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

### Задача 14. Процедура с OUT

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

### Задача 15. Комбинированная: EXECUTE + format + RETURNS TABLE

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

### Задача 16. Пользователи с неоформленными корзинами

Напишите функцию `users_with_unordered_carts()` RETURNS SETOF users — пользователи, у которых есть позиции в `cart_items`, но нет ни одного заказа (NATURAL LEFT JOIN `orders`, фильтр `WHERE order_id IS NULL`).

**Ожидаемый результат** (`users_with_unordered_carts()`):

| user_id | name             | created_at |
|---------|------------------|------------|
| 7       | Сергей Кузнецов  | 2026-01-21 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION users_with_unordered_carts(...)
...
```

---

### Задача 17. Заказы с доставкой более n дней

Напишите функцию `orders_delivered_longer_than(n_days INT)` RETURNS SETOF orders — заказы со статусом «доставлен», у которых разница `updated_at - created_at` больше `n_days`.

**Ожидаемый результат** (`orders_delivered_longer_than(2)`):

| order_id | user_id | status    | total    | created_at | updated_at |
|----------|---------|-----------|----------|------------|------------|
| 3        | 3       | доставлен | 94490.00 | 2026-01-11 | 2026-01-14 |

(заказ 3: 14-11 = 3 дня > 2)

**Решение**

```sql
CREATE OR REPLACE FUNCTION orders_delivered_longer_than(...)
...
```

---

### Задача 18. Заказы не получены более n дней

Напишите функцию `orders_pending_longer_than(n_days INT)` RETURNS TABLE — заказы со статусом «ожидает» или «отправлен», для которых `CURRENT_DATE - created_at` больше `n_days`.

**Ожидаемый результат** (`orders_pending_longer_than(30)`, CURRENT_DATE = '2026-02-20'):

| order_id | user_name        | status    | days_pending |
|----------|------------------|-----------|--------------|
| 2        | Мария Сидорова   | ожидает   | 33           |
| 4        | Елена Волкова    | отправлен | 32           |
| 5        | Дмитрий Новиков  | ожидает   | 31           |

**Решение**

```sql
CREATE OR REPLACE FUNCTION orders_pending_longer_than(...)
...
```

---

### Задача 19. Отменённые заказы

Напишите функцию `cancelled_orders()` RETURNS TABLE — заказы со статусом «отменён» с именем пользователя (NATURAL JOIN `users`).

**Ожидаемый результат** (`cancelled_orders()`):

| order_id | user_name       | total    | created_at | updated_at |
|----------|-----------------|----------|------------|------------|
| 6        | Ольга Смирнова  | 4500.00  | 2026-01-17 | 2026-01-18 |
| 8        | Дмитрий Новиков | 89990.00 | 2026-01-19 | 2026-01-19 |

**Решение**

```sql
CREATE OR REPLACE FUNCTION cancelled_orders(...)
...
```

---

### Задача 20. Наиболее часто возвращаемые товары

Напишите функцию `most_returned_products(limit_n INT DEFAULT 5)` RETURNS TABLE (product_id BIGINT, product_name TEXT, return_count BIGINT) — товары из заказов со статусом «возвращён» (`order_items` JOIN `orders` JOIN `products`), отсортированные по количеству возвратов по убыванию.

**Ожидаемый результат** (`most_returned_products(5)`):

| product_id | product_name | return_count |
|------------|--------------|--------------|
| 5          | Наушники     | 2            |
| 4          | Монитор 27"  | 1            |

(заказы 7, 9 — статус «возвращён»; товары: Наушники в обоих, Монитор в заказе 9)

**Решение**

```sql
CREATE OR REPLACE FUNCTION most_returned_products(...)
...
```




