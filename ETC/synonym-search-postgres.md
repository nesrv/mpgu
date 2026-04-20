# Synonym Analyzer в PostgreSQL

## 1. Простое решение через ARRAY

```sql
-- Прямой запрос с синонимами
SELECT * FROM products
WHERE name ILIKE ANY(ARRAY['%телефон%', '%смартфон%', '%мобильный%']);

-- Или через CASE в CTE
WITH synonyms AS (
    SELECT unnest(
        CASE 'телефон'
            WHEN 'телефон' THEN ARRAY['телефон', 'смартфон', 'мобильный']
            WHEN 'ноутбук' THEN ARRAY['ноутбук', 'лэптоп', 'laptop']
            ELSE ARRAY['телефон']
        END
    ) AS term
)
SELECT * FROM products
WHERE name ILIKE ANY(SELECT '%' || term || '%' FROM synonyms);
```

## 2. Через таблицу синонимов (гибкий вариант)

```sql
-- Таблица синонимов
CREATE TABLE synonyms (
    word TEXT,
    synonym TEXT
);

INSERT INTO synonyms VALUES
    ('телефон', 'смартфон'),
    ('телефон', 'мобильный'),
    ('ноутбук', 'лэптоп');

CREATE INDEX idx_synonyms ON synonyms(synonym);

-- Поиск с синонимами
WITH search_terms AS (
    SELECT 'смартфон' AS term
    UNION
    SELECT word FROM synonyms WHERE synonym = 'смартфон'
)
SELECT * FROM products
WHERE name ILIKE ANY(ARRAY(SELECT '%' || term || '%' FROM search_terms));
```

## 3. Через synonym dictionary

```sql
-- Создать файл: /usr/share/postgresql/tsearch_data/synonyms.syn
-- Формат: синоним базовое_слово
-- Пример содержимого:
-- смартфон телефон
-- лэптоп ноутбук
-- smart умный

CREATE TEXT SEARCH DICTIONARY syn_simple (
    TEMPLATE = synonym,
    SYNONYMS = synonyms
);

CREATE TEXT SEARCH CONFIGURATION syn_config (COPY = russian);
ALTER TEXT SEARCH CONFIGURATION syn_config
    ALTER MAPPING FOR asciiword, word WITH syn_simple, russian_stem;

-- Использование
SELECT to_tsvector('syn_config', 'смартфон');  -- вернет 'телефон'
SELECT * FROM products
WHERE to_tsvector('syn_config', name) @@ plainto_tsquery('syn_config', 'мобильный');
```

## 4. Через словарь синонимов (Thesaurus) - сложный вариант

```sql
-- Создать файл синонимов: /usr/share/postgresql/tsearch_data/synonyms.ths
-- Формат: синоним1 синоним2 : базовое_слово
-- Пример содержимого:
-- телефон смартфон мобильный : телефон
-- ноутбук лэптоп laptop : ноутбук
-- умный smart : умный

-- Создать словарь
CREATE TEXT SEARCH DICTIONARY syn_dict (
    TEMPLATE = thesaurus,
    DictFile = synonyms,
    Dictionary = russian_stem
);

-- Создать конфигурацию
CREATE TEXT SEARCH CONFIGURATION syn_ru (COPY = pg_catalog.russian);
ALTER TEXT SEARCH CONFIGURATION syn_ru
    ALTER MAPPING FOR asciiword, word WITH syn_dict, russian_stem;

-- Использование
SELECT to_tsvector('syn_ru', 'смартфон');  -- вернет 'телефон'
SELECT * FROM products
WHERE to_tsvector('syn_ru', name) @@ plainto_tsquery('syn_ru', 'мобильный');

-- С индексом для производительности
CREATE INDEX idx_name_syn ON products 
USING gin(to_tsvector('syn_ru', name));
```

**Рекомендация:** 
- Простые случаи (до 10 синонимов) → вариант 1 или 2
- Средние случаи (динамические синонимы) → вариант 2 (таблица)
- Сложные случаи (много синонимов, full-text search) → вариант 4 (thesaurus)
