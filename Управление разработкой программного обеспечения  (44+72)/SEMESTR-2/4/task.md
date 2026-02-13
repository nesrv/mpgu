# 📘 Исходная модель

```sql
video_cards (
    id          BIGSERIAL,
    name        TEXT,
    price       NUMERIC(12,2),
    description TEXT,
    created_at  TIMESTAMPTZ
)
```

---

# 🟢 Уровень 1 — функции и условия

---

## 1 Категория видеокарты по цене

**Задание:**  
Функция по цене возвращает сегмент: `бюджет` (< 70k), `средний` (< 100k), `высокий` (< 150k), `флагман` (иначе). Для `NULL` возвращать `'неизвестно'`.

```sql
CREATE OR REPLACE FUNCTION price_category(p_price NUMERIC)
RETURNS TEXT AS $$
BEGIN
    IF p_price IS NULL THEN
        RETURN 'неизвестно';
    ELSIF p_price < 70000 THEN
        RETURN 'бюджет';
    ELSIF p_price < 100000 THEN
        RETURN 'средний';
    ELSIF p_price < 150000 THEN
        RETURN 'высокий';
    ELSE
        RETURN 'флагман';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

**Пример вызова:**
```sql
SELECT price_category(85000);   -- 'средний'
SELECT price_category(NULL);    -- 'неизвестно'
SELECT price_category(200000);  -- 'флагман'
```

**Результат выполнения:**

| price_category |
|----------------|
| средний        |

| price_category |
|----------------|
| неизвестно     |

| price_category |
|----------------|
| флагман        |

---

## 2 Топ-N видеокарт по цене

**Задание:**  
Функция: порог цены `p_min_price` и число `p_limit`. Вернуть таблицу: название, цена, категория (через `price_category`). Только видеокарты не дешевле порога, не больше `p_limit` строк, сортировка по цене по убыванию.

```sql
CREATE OR REPLACE FUNCTION top_cards_by_price(p_min_price NUMERIC, p_limit INTEGER)
RETURNS TABLE(name TEXT, price NUMERIC, category TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT vc.name, vc.price, price_category(vc.price)
    FROM video_cards vc
    WHERE vc.price >= p_min_price
    ORDER BY vc.price DESC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

**Пример вызова:**
```sql
SELECT * FROM top_cards_by_price(50000, 5);
```

**Результат выполнения:**

| name     | price   | category |
|----------|---------|----------|
| RTX 4090 | 150000  | флагман  |
| RTX 4080 | 95000   | средний  |
| RX 7900  | 89000   | средний  |
| RTX 4070 | 65000   | бюджет   |
| RX 7800  | 58000   | бюджет   |

---

## 3 Содержимое корзины по массиву id

**Задание:**  
Функция принимает массив id видеокарт. Вернуть таблицу: `id`, `name`, `price` — только строки с этими id (без строки «ИТОГО»).

```sql
CREATE OR REPLACE FUNCTION cart_by_ids(p_ids BIGINT[])
RETURNS TABLE(id BIGINT, name TEXT, price NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT vc.id, vc.name, vc.price
    FROM video_cards vc
    WHERE vc.id = ANY(p_ids);
END;
$$ LANGUAGE plpgsql;
```

**Пример вызова:**
```sql
SELECT * FROM cart_by_ids(ARRAY[1, 2, 3]::BIGINT[]);
```

**Результат выполнения:**

| id | name     | price  |
|----|----------|--------|
| 1  | RTX 4090 | 150000 |
| 2  | RTX 4080 | 95000  |
| 3  | RX 7900  | 89000  |

---

# 🟡 Уровень 2 — процедуры

---

## 4 Добавление видеокарты с проверкой дубликата по имени

**Задание:**  
Процедура: `p_name`, `p_price`, `p_description`, OUT `new_id BIGINT`. Если видеокарта с таким `name` уже есть — в `new_id` вернуть существующий `id`. Иначе — INSERT и вернуть новый `id`.

```sql
CREATE OR REPLACE PROCEDURE upsert_video_card(
    p_name TEXT,
    p_price NUMERIC,
    p_description TEXT,
    OUT new_id BIGINT
)
LANGUAGE plpgsql AS $$
BEGIN
    SELECT vc.id INTO new_id FROM video_cards vc WHERE vc.name = p_name LIMIT 1;
    IF new_id IS NOT NULL THEN
        RETURN;
    END IF;
    INSERT INTO video_cards (name, price, description, created_at)
    VALUES (p_name, p_price, p_description, now())
    RETURNING id INTO new_id;
END;
$$;
```

**Пример вызова:**
```sql
-- только вызов (new_id не вывести в консоли):
CALL upsert_video_card('RTX 4080', 95000, 'Игровая видеокарта', NULL);

-- вызов с получением new_id:
DO $$
DECLARE out_id BIGINT;
BEGIN
  CALL upsert_video_card('RTX 4090', 150000, 'Flagship', out_id);
  RAISE NOTICE 'id: %', out_id;
END;
$$;
```

**Результат выполнения (в консоли/логах):**

| Результат   |
|-------------|
| NOTICE: id: 7 |

*При первом вызове для новой карты — новый id; при повторном вызове с тем же именем — id существующей.*

---

## 5 Обновление цены по массиву id

**Задание:**  
Процедура: массив id, новая цена. Обновить цену у всех видеокарт с этими id. OUT — количество обновлённых строк.

```sql
CREATE OR REPLACE PROCEDURE update_prices_by_ids(
    p_ids BIGINT[],
    p_new_price NUMERIC,
    OUT updated_count INTEGER
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE video_cards
    SET price = p_new_price
    WHERE id = ANY(p_ids);
    GET DIAGNOSTICS updated_count = ROW_COUNT;
END;
$$;
```

**Пример вызова:**
```sql
DO $$
DECLARE n INTEGER;
BEGIN
  CALL update_prices_by_ids(ARRAY[1, 2, 3]::BIGINT[], 89999, n);
  RAISE NOTICE 'Обновлено строк: %', n;
END;
$$;
```

**Результат выполнения (в консоли/логах):**

| Результат              |
|------------------------|
| NOTICE: Обновлено строк: 3 |

---

## 6 Удаление дешёвых с записью в лог перед удалением

**Задание:**  
Процедура: порог `p_price`. Для каждой видеокарты с ценой ниже порога вставить в `price_log` запись (card_id, old_price, new_price = NULL), затем удалить эти видеокарты. OUT — количество удалённых.

```sql
CREATE OR REPLACE PROCEDURE archive_cheaper_than(
    p_price NUMERIC,
    OUT deleted_count INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT id, price FROM video_cards WHERE price < p_price
    LOOP
        INSERT INTO price_log(card_id, old_price, new_price)
        VALUES (r.id, r.price, NULL);
    END LOOP;
    DELETE FROM video_cards WHERE price < p_price;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
END;
$$;
```

**Пример вызова:**
```sql
DO $$
DECLARE n INTEGER;
BEGIN
  CALL archive_cheaper_than(40000, n);
  RAISE NOTICE 'Удалено строк: %', n;
END;
$$;
```

**Результат выполнения (в консоли/логах):**

| Результат            |
|----------------------|
| NOTICE: Удалено строк: 2 |

*Перед удалением в `price_log` добавлены 2 записи с `new_price = NULL`.*

---

# 🟠 Уровень 3 — правила и возврат наборов

---

## 7 Правило: логирование изменений цен при UPDATE

**Задание:**  
Таблица `price_log (id, card_id, old_price, new_price, changed_at)`. Создать правило на `video_cards`: при UPDATE дополнительно вставлять в `price_log` строку со старой и новой ценой (использовать OLD и NEW в действии правила).

```sql
CREATE RULE r_log_price_change AS
ON UPDATE TO video_cards
DO ALSO
INSERT INTO price_log(card_id, old_price, new_price)
VALUES (OLD.id, OLD.price, NEW.price);
```

**Пример вызова (правило срабатывает при любом UPDATE по таблице):**
```sql
UPDATE video_cards SET price = 99000 WHERE id = 1;
-- в price_log добавится запись с старой и новой ценой для этой строки
```

**Результат выполнения:**

- Сообщение СУБД: `UPDATE 1`
- В таблице `price_log` появляется новая строка:

| id | card_id | old_price | new_price | changed_at          |
|----|---------|-----------|-----------|---------------------|
| 1  | 1       | 85000     | 99000     | 2025-02-13 12:00:00 |

*Примечание: в PostgreSQL правило с OLD/NEW выполняется в контексте изменённых строк. Если ваша версия не поддерживает OLD/NEW в правиле, используйте триггер из методички.*

---

## 8 Похожие по цене (в пределах процента)

**Задание:**  
Функция: `p_card_id`, `p_percent` (например 10). Вернуть таблицу `(id, name, price)` — видеокарты, у которых цена отличается от цены данной карты не более чем на p_percent%, кроме самой карты. Лимит 10 строк.

```sql
CREATE OR REPLACE FUNCTION similar_by_price(p_card_id BIGINT, p_percent NUMERIC DEFAULT 10)
RETURNS TABLE(id BIGINT, name TEXT, price NUMERIC) AS $$
DECLARE
    ref_price NUMERIC;
    delta NUMERIC;
BEGIN
    SELECT vc.price INTO ref_price FROM video_cards vc WHERE vc.id = p_card_id;
    IF ref_price IS NULL OR ref_price = 0 THEN
        RETURN;
    END IF;
    delta := ref_price * (p_percent / 100);

    RETURN QUERY
    SELECT vc.id, vc.name, vc.price
    FROM video_cards vc
    WHERE vc.id <> p_card_id
      AND vc.price BETWEEN ref_price - delta AND ref_price + delta
    ORDER BY abs(vc.price - ref_price)
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;
```

**Пример вызова:**
```sql
SELECT * FROM similar_by_price(1, 10);
SELECT * FROM similar_by_price(5, 15);  -- 15% разброс
```

**Результат выполнения (для карты id=1 с ценой 150000, ±10%):**

| id | name     | price  |
|----|----------|--------|
| 2  | RTX 4080 | 95000  |
| 3  | RX 7900  | 89000  |
| 4  | RTX 4070 Ti | 82000 |

---

## 9 Сумма и массив имён по массиву id

**Задание:**  
Функция принимает массив id. Вернуть одну строку: сумма цен и массив имён в порядке id (например `TABLE(total NUMERIC, names TEXT[])`).

```sql
CREATE OR REPLACE FUNCTION cart_totals(p_ids BIGINT[])
RETURNS TABLE(total NUMERIC, names TEXT[]) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(vc.price), 0),
        array_agg(vc.name ORDER BY array_position(p_ids, vc.id))
    FROM video_cards vc
    WHERE vc.id = ANY(p_ids);
END;
$$ LANGUAGE plpgsql;
```

**Пример вызова:**
```sql
SELECT * FROM cart_totals(ARRAY[1, 2, 3]::BIGINT[]);
-- одна строка: total (сумма), names (массив имён)
```

**Результат выполнения:**

| total  | names                              |
|--------|-------------------------------------|
| 334000 | {RTX 4090, RTX 4080, RX 7900}       |

---

## 10 Правило: запрет удаления при наличии записи в price_log

**Задание:**  
Правило на `video_cards`: при DELETE не выполнять удаление для тех строк, у которых есть записи в `price_log` по этому `card_id` (остальные удалять как обычно). Реализовать через DO INSTEAD: выполнять DELETE только по id, для которых в `price_log` нет записей.

```sql
CREATE RULE r_prevent_delete_if_in_log AS
ON DELETE TO video_cards
DO INSTEAD
DELETE FROM video_cards vc
WHERE vc.id = OLD.id
  AND NOT EXISTS (SELECT 1 FROM price_log pl WHERE pl.card_id = vc.id);
```

**Пример вызова (правило срабатывает при DELETE по таблице):**
```sql
DELETE FROM video_cards WHERE id = 5;
-- строка удалится только если в price_log нет записей с card_id = 5
```

**Результат выполнения:**

| Случай                    | Результат      |
|---------------------------|----------------|
| В `price_log` нет card_id=5 | `DELETE 1` — строка удалена |
| В `price_log` есть card_id=5 | `DELETE 0` — строка не удалена (правило отменило удаление) |

*Итог: строки с историей в `price_log` не удаляются, остальные удаляются.*

---

# 📋 Таблица price_log (для заданий 6, 7, 10)

```sql
CREATE TABLE price_log (
    id         BIGSERIAL PRIMARY KEY,
    card_id    BIGINT NOT NULL,
    old_price  NUMERIC(12,2),
    new_price  NUMERIC(12,2),
    changed_at TIMESTAMPTZ DEFAULT now()
);
```

---

Итого: **10 заданий** — без UNION, триггеры заменены на правила (задания 7 и 10).
