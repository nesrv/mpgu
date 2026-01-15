# Лабораторная работа: Полнотекстовый поиск в PostgreSQL

## Введение

Изучение полнотекстового поиска в СУБД на примере PostgreSQL.

---

## Настройка словарей в PostgreSQL


```sql
-- Проверить доступные словари
SELECT cfgname FROM pg_ts_config;

-- Посмотреть текущую конфигурацию
SHOW default_text_search_config;

-- Установить русский словарь для сессии
SET default_text_search_config = 'pg_catalog.russian';

-- Установить русский словарь для базы данных
ALTER DATABASE shop SET default_text_search_config = 'pg_catalog.russian';

-- Пример токенизации и стемминга
SELECT to_tsvector('russian', 'Съешь ещё этих мягких французских булок');
```

### Результат токенизации

```
'булок':6 'ещ':2 'мягк':4 'съеш':1 'французск':5 'эт':3
```

### Объяснение формата

**Формат:** `'основа_слова':позиция_в_тексте`

- `'съеш':1` - слово "Съешь" → основа "съеш", позиция 1
- `'ещ':2` - слово "ещё" → основа "ещ", позиция 2
- `'эт':3` - слово "этих" → основа "эт", позиция 3
- `'мягк':4` - слово "мягких" → основа "мягк", позиция 4
- `'французск':5` - слово "французских" → основа "французск", позиция 5
- `'булок':6` - слово "булок" → основа "булок", позиция 6

### Зачем это нужно?

- **Стемминг**: Поиск работает по основам слов (найдет "булка", "булки", "булок")
- **Позиции**: Нужны для фразового поиска и ранжирования результатов
- **Стоп-слова**: Предлоги и союзы автоматически удаляются

### Создание индекса

```sql
CREATE INDEX idx_description ON products USING gin(to_tsvector('russian', description));
```

> **Важно:** Для полнотекстового поиска документ приводится к типу `tsvector`, а запрос — к типу `tsquery`.

---



## Часть 1. Простой полнотекстовый поиск

### Базовый поиск

```sql
-- Поиск по одному слову (найдет все формы слова)
SELECT * FROM products 
WHERE to_tsvector(description) @@ to_tsquery('булка');
-- Найдет: "булка", "булки", "булок", "булкой"

-- Поиск смартфонов
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('смартфон');

-- Поиск умных устройств
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умный');
```

### Логические операторы

```sql
-- AND: оба слова должны присутствовать
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умн & дом');

-- NOT: исключить слово
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умн & дом & !телевизор');

-- OR: либо умный дом, либо умный телевизор
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умн & (дом | телевизор)');
```

### Фразовый поиск

> Учитывает порядок и близость позиций слов в тексте.

```sql
-- Слова должны идти подряд: <->
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умн <-> телевизор');

-- Слова на расстоянии до 3 позиций: <3>
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ to_tsquery('умн <3> телевизор');
```

---

## Различия между plainto_tsquery и to_tsquery

### plainto_tsquery - простой поиск

- Преобразует текст в запрос автоматически
- Игнорирует спецсимволы (`&`, `|`, `!`, `()`)
- Слова соединяются через `&` (AND)
- Безопасен для пользовательского ввода

```sql
plainto_tsquery('кот собака') → 'кот' & 'собака'
plainto_tsquery('кот & собака') → 'кот' & 'собака' -- спецсимволы игнорируются
```

### to_tsquery - расширенный поиск

- Требует правильный синтаксис запроса
- Поддерживает операторы: `&` (AND), `|` (OR), `!` (NOT), `()` (группировка)
- Выдаст **ошибку** при неправильном синтаксисе
- Опасен для прямого пользовательского ввода

```sql
to_tsquery('кот & собака') → 'кот' & 'собака'
to_tsquery('кот | собака') → 'кот' | 'собака'
to_tsquery('кот & !собака') → 'кот' & !'собака'
to_tsquery('кот собака') → ОШИБКА (нет оператора)
```

### Рекомендация

- **Для поиска от пользователей** → `plainto_tsquery` (безопасно)
- **Для сложных запросов с логикой** → `to_tsquery` (валидируйте ввод!)
- **Для веб-поиска** → `websearch_to_tsquery` (PostgreSQL 11+) - поддерживает кавычки и `-`

**Пример websearch_to_tsquery:**
```sql
SELECT id, name, description FROM products
WHERE to_tsvector(description) @@ websearch_to_tsquery('"умный дом" -телевизор');
-- Найдет фразу "умный дом", но исключит результаты с "телевизор"
```

---

## Хранимые функции для поиска

```sql
-- Создание функции поиска
CREATE OR REPLACE FUNCTION search_products(search_query TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, price NUMERIC, category VARCHAR)
BEGIN ATOMIC
    SELECT id, name, description, price, category
    FROM products
    WHERE to_tsvector(name || ' ' || description) @@ to_tsquery(search_query);
END;

-- Использование функции
SELECT * FROM search_products('умный');
```

---

## Интеграция с FastAPI



### Вариант 1: Через SQL функцию

```python
@app.get("/direct-search")
def direct_search(q: str, db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM search_products(:query)"), {"query": q})
    hits = []
    for row in rows:
        hits.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "category": row[4]
        })
    return {"hits": hits}
```

### Вариант 2: Через SQLAlchemy ORM

```python
@app.get("/direct-search-orm")
def direct_search_orm(q: str, db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    products = db.query(Product).filter(
        func.to_tsvector(Product.name + ' ' + Product.description).op('@@')(func.to_tsquery(q))
    ).all()
    
    hits = []
    for p in products:
        hits.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "category": p.category
        })
    return {"hits": hits}
```

### Измерение производительности

```python
import time

start = time.time()
# ваш код поиска
elapsed = time.time() - start

return {
    "hits": hits, 
    "time_ms": round(elapsed * 1000, 2), 
    "count": len(hits)
}
```

---

## Нагрузочное тестирование с Apache Bench

### Команды для тестирования

```bash
# Тест SQL функции
ab -n 100 -c 10 "http://localhost:8000/direct-search?q=apple"

# Тест SQLAlchemy ORM
ab -n 100 -c 10 "http://localhost:8000/direct-search-orm?q=apple"

# Тест OpenSearch
ab -n 100 -c 10 "http://localhost:8000/search?q=apple"
```

**Параметры:**
- `-n 100` - общее количество запросов
- `-c 10` - количество одновременных соединений




### Сравнительная таблица результатов

| Параметр | `/search?q=apple` | `/direct-search?q=apple` | `/direct-search-orm?q=apple` |
|----------|-------------------|--------------------------|-----------------------------|
| **Успешность запросов** | ✅ 100% (0 failed) | ⚠️ 34% (66 failed) | ⚠️ 63% (37 failed) |
| **Скорость (запросов/сек)** | 111.16 | 159.14 | 168.65 |
| **Общее время теста (сек)** | 0.900 | 0.628 | 0.593 |
| **Среднее время запроса (мс)** | 89.963 | 62.838 | 59.296 |
| **Медиана времени (50%, мс)** | 71 | 46 | 53 |
| **90-й перцентиль (мс)** | 157 | 116 | 78 |
| **Максимальное время (мс)** | 239 | 168 | 101 |
| **Размер ответа (байт)** | 1146 | 635 | 642 |
| **Стабильность (разброс σ)** | Высокая (±47.5 мс) | Средняя (±31.8 мс) | Низкая (±15.0 мс) |
| **Тип ошибок** | Нет | Length mismatch | Length mismatch |

### Ключевые выводы

1. **По надёжности**: `/search` — абсолютный лидер (100% успешных запросов)
2. **По скорости**: `direct-search-orm` самый быстрый (168.65 запр/сек), но с ошибками
3. **По стабильности**: `direct-search-orm` имеет наименьший разброс времени ответа
4. **По качеству ответов**: `/search` возвращает почти в 2 раза больше данных (1146 vs ~640 байт)

### Рекомендации

- **Для продакшена**: Использовать `/search` (надёжность важнее скорости)
- **Для оптимизации**: Исследовать причины ошибок в direct-методах (ошибки Length означают разную длину ответов)
- **direct-search-orm** показывает лучший баланс скорости и стабильности, если исправить ошибки

---



## Часть 2. Продвинутый поиск (Fuzzy Search)

> **Важно:** Оператор `%` ищет похожие **целые строки**, а не слова внутри текста.

### Поиск слов внутри текста

#### Решение 1: word_similarity

```sql

SELECT description, word_similarity('умный', description) AS sim
FROM products
WHERE 'умный' <% description  -- оператор word_similarity
ORDER BY sim DESC;


```

#### Решение 2: ILIKE с trigram индексом

```sql
-- Поиск с опечатками и похожими словами
SELECT description, similarity(description, 'умный') AS sim
FROM products
WHERE description ILIKE '%умны%'
ORDER BY sim DESC;


-- Поиск по похожести всей строки
SELECT description, similarity(description, 'умный') AS sim
FROM products
WHERE description % 'умный'
ORDER BY sim DESC;
```

**Результат:**

| description | similarity |
|-------------|------------|
| Умный дом | 0.6 |
| Ночник Умник | 0.21428572 |
| Швабра Умница | 0.1764706 |
| Умные часы на Wear OS | 0.16666667 |
| Умная колонка с Алисой | 0.115384616 |
| Умные часы с датчиком температуры | 0.11111111 |

#### Решение 3: word_similarity с префиксным поиском (рекомендуется)

```sql
SELECT description, 
       word_similarity('умный', description) AS sim
FROM products
WHERE description ILIKE '%умн%'  -- префиксный поиск
ORDER BY sim DESC;
```

**Результат:**

| description | similarity |
|-------------|------------|
| Умный дом | 1.0 |
| Умные часы с датчиком температуры | 0.6666667 |
| Умные часы на Wear OS | 0.6666667 |
| Умная колонка с Алисой | 0.5 |
| Ночник Умник | 0.5 |
| Швабра Умница | 0.5 |

---





## Fuzzy Search (поиск с опечатками)

### 1. pg_trgm (рекомендуется)

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

### 2. Levenshtein (расстояние редактирования)

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

### 3. Комбинированный подход

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

### 4. Для слов внутри текста

```sql
SELECT description,
       word_similarity('умнае', description) AS sim
FROM products
WHERE 'умнае' <% description  -- найдет "умные"
ORDER BY sim DESC
LIMIT 10;
```

**Рекомендация:** `pg_trgm` с `similarity()` - быстро, с индексом, находит опечатки.

---



## Synonym Analyzer (поиск с синонимами)

### 1. Простое решение через ARRAY

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

### 2. Через таблицу синонимов (гибкий вариант)

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

### 3. Через synonym dictionary

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

### 4. Через Thesaurus (сложный вариант)

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

- **Простые случаи** (до 10 синонимов) → вариант 1 или 2
- **Средние случаи** (динамические синонимы) → вариант 2 (таблица)
- **Сложные случаи** (много синонимов, full-text search) → вариант 4 (thesaurus)

---



1. **Автодополнение (Suggest)** - поиск с автодополнением для названий товаров
2. **Ранжирование результатов** - сортировка по релевантности с `ts_rank()`
3. **Поиск с подсветкой** - выделение найденных слов с `ts_headline()`
4. **Поиск по категориям** - полнотекстовый поиск с фильтрацией
5. **Fuzzy поиск** - нечеткий поиск с настраиваемым порогом
6. **Комбинированный поиск** - объединение полнотекстового и fuzzy поиска