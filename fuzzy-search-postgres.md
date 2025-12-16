# Fuzzy Search в PostgreSQL

## 1. pg_trgm (лучший вариант)

```sql
-- Установка
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Индекс
CREATE INDEX idx_name_trgm ON products USING gin (name gin_trgm_ops);

-- Поиск с опечатками
SELECT name, similarity(name, 'яблако') AS sim  -- опечатка в "яблоко"
FROM products
WHERE name % 'яблако'
ORDER BY sim DESC
LIMIT 10;

-- Или через ILIKE с индексом (быстрее)
SELECT name, similarity(name, 'яблако') AS sim
FROM products
WHERE name ILIKE '%яблак%'
ORDER BY sim DESC
LIMIT 10;
```

## 2. Levenshtein (расстояние редактирования)

```sql
-- Установка
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

-- Поиск (без индекса, медленно)
SELECT name, levenshtein(name, 'яблоко') AS dist
FROM products
WHERE levenshtein(name, 'яблоко') <= 3  -- макс 3 изменения
ORDER BY dist
LIMIT 10;
```

## 3. Комбинированный (рекомендуется)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_name_trgm ON products USING gin (name gin_trgm_ops);

-- Настройка порога
SET pg_trgm.similarity_threshold = 0.3;  -- 0.0-1.0

-- Fuzzy search
SELECT name, 
       similarity(name, 'умнае часы') AS sim  -- опечатки
FROM products
WHERE name % 'умнае часы'
   OR name ILIKE '%умн%'
   OR name ILIKE '%час%'
ORDER BY sim DESC
LIMIT 10;
```

## 4. Для слов внутри текста

```sql
SELECT description,
       word_similarity('умнае', description) AS sim
FROM products
WHERE 'умнае' <% description  -- найдет "умные"
ORDER BY sim DESC
LIMIT 10;
```

**Рекомендация:** `pg_trgm` с `similarity()` - быстро, с индексом, находит опечатки.
