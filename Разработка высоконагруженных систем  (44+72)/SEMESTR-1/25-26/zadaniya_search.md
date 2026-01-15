# Самостоятельные задания по поиску в PostgreSQL

## Задание 1: Автодополнение (Suggest)

Реализуйте поиск с автодополнением для названий товаров.

**SQL:**
```sql
-- Создать индекс
CREATE INDEX idx_name_suggest ON products USING gin(name gin_trgm_ops);

-- Функция автодополнения
CREATE OR REPLACE FUNCTION suggest_products(prefix TEXT)
RETURNS TABLE(name VARCHAR, similarity REAL)
BEGIN ATOMIC
    SELECT DISTINCT p.name, similarity(p.name, prefix) AS sim
    FROM products p
    WHERE p.name ILIKE prefix || '%'
    ORDER BY sim DESC, p.name
    LIMIT 10;
END;

-- Использование
SELECT * FROM suggest_products('умн');
```

**SQLAlchemy:**
```python
from sqlalchemy import func

@app.get("/suggest")
def suggest(q: str, db: Session = Depends(get_db)):
    results = db.query(
        Product.name,
        func.similarity(Product.name, q).label('sim')
    ).filter(
        Product.name.ilike(f'{q}%')
    ).order_by(
        func.similarity(Product.name, q).desc(),
        Product.name
    ).limit(10).all()
    
    return {"suggestions": [r.name for r in results]}
```

---

## Задание 2: Ранжирование результатов

Добавьте ранжирование по релевантности с помощью `ts_rank()`.

**SQL:**
```sql
-- Функция поиска с ранжированием
CREATE OR REPLACE FUNCTION search_ranked(search_query TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, rank REAL)
BEGIN ATOMIC
    SELECT 
        p.id, 
        p.name, 
        p.description,
        ts_rank(to_tsvector('russian', p.name || ' ' || p.description), 
                to_tsquery('russian', search_query)) AS rank
    FROM products p
    WHERE to_tsvector('russian', p.name || ' ' || p.description) 
          @@ to_tsquery('russian', search_query)
    ORDER BY rank DESC;
END;

-- Использование
SELECT * FROM search_ranked('умный & дом');
```

**SQLAlchemy:**
```python
from sqlalchemy import text

@app.get("/search-ranked")
def search_ranked(q: str, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    
    results = db.query(
        Product.id,
        Product.name,
        Product.description,
        func.ts_rank(
            func.to_tsvector('russian', query_text),
            func.to_tsquery('russian', q)
        ).label('rank')
    ).filter(
        func.to_tsvector('russian', query_text).op('@@')(
            func.to_tsquery('russian', q)
        )
    ).order_by(text('rank DESC')).all()
    
    return {"results": [{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "rank": float(r.rank)
    } for r in results]}
```

---

## Задание 3: Поиск с подсветкой

Реализуйте подсветку найденных слов в результатах.

**SQL:**
```sql
-- Функция с подсветкой
CREATE OR REPLACE FUNCTION search_highlight(search_query TEXT)
RETURNS TABLE(name VARCHAR, snippet TEXT)
BEGIN ATOMIC
    SELECT 
        p.name,
        ts_headline('russian', p.description, 
                    to_tsquery('russian', search_query),
                    'MaxWords=20, MinWords=10') AS snippet
    FROM products p
    WHERE to_tsvector('russian', p.description) 
          @@ to_tsquery('russian', search_query);
END;

-- Использование
SELECT * FROM search_highlight('умный');
```

**SQLAlchemy:**
```python
@app.get("/search-highlight")
def search_highlight(q: str, db: Session = Depends(get_db)):
    results = db.query(
        Product.name,
        func.ts_headline(
            'russian',
            Product.description,
            func.to_tsquery('russian', q),
            'MaxWords=20, MinWords=10'
        ).label('snippet')
    ).filter(
        func.to_tsvector('russian', Product.description).op('@@')(
            func.to_tsquery('russian', q)
        )
    ).all()
    
    return {"results": [{
        "name": r.name,
        "snippet": r.snippet
    } for r in results]}
```

---

## Задание 4: Поиск по категориям с фильтрацией

Реализуйте полнотекстовый поиск с фильтром по категории.

**SQL:**
```sql
-- Функция поиска с фильтром
CREATE OR REPLACE FUNCTION search_by_category(
    search_query TEXT, 
    category_filter VARCHAR
)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, category VARCHAR)
BEGIN ATOMIC
    SELECT p.id, p.name, p.description, p.category
    FROM products p
    WHERE to_tsvector('russian', p.name || ' ' || p.description) 
          @@ to_tsquery('russian', search_query)
      AND p.category = category_filter;
END;

-- Использование
SELECT * FROM search_by_category('умный', 'Электроника');
```

**SQLAlchemy:**
```python
@app.get("/search-category")
def search_category(q: str, category: str, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    
    results = db.query(Product).filter(
        func.to_tsvector('russian', query_text).op('@@')(
            func.to_tsquery('russian', q)
        ),
        Product.category == category
    ).all()
    
    return {"results": [{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "category": r.category
    } for r in results]}
```

---

## Задание 5: Fuzzy поиск с порогом похожести

Реализуйте нечеткий поиск с настраиваемым порогом.

**SQL:**
```sql
-- Функция fuzzy поиска
CREATE OR REPLACE FUNCTION fuzzy_search(
    search_term TEXT, 
    threshold REAL DEFAULT 0.3
)
RETURNS TABLE(name VARCHAR, description TEXT, similarity REAL)
BEGIN ATOMIC
    SELECT 
        p.name, 
        p.description,
        word_similarity(search_term, p.name || ' ' || p.description) AS sim
    FROM products p
    WHERE word_similarity(search_term, p.name || ' ' || p.description) > threshold
    ORDER BY sim DESC
    LIMIT 20;
END;

-- Использование
SELECT * FROM fuzzy_search('умнае часы', 0.2);
```

**SQLAlchemy:**
```python
@app.get("/fuzzy-search")
def fuzzy_search(q: str, threshold: float = 0.3, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    
    results = db.query(
        Product.name,
        Product.description,
        func.word_similarity(q, query_text).label('sim')
    ).filter(
        func.word_similarity(q, query_text) > threshold
    ).order_by(text('sim DESC')).limit(20).all()
    
    return {"results": [{
        "name": r.name,
        "description": r.description,
        "similarity": float(r.sim)
    } for r in results]}
```

---

## Задание 6: Комбинированный поиск

Реализуйте поиск, объединяющий полнотекстовый и fuzzy поиск.

**SQL:**
```sql
CREATE OR REPLACE FUNCTION combined_search(search_query TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, score REAL)
BEGIN ATOMIC
    SELECT 
        p.id,
        p.name,
        p.description,
        GREATEST(
            ts_rank(to_tsvector('russian', p.name || ' ' || p.description), 
                    plainto_tsquery('russian', search_query)),
            word_similarity(search_query, p.name || ' ' || p.description)
        ) AS score
    FROM products p
    WHERE to_tsvector('russian', p.name || ' ' || p.description) 
          @@ plainto_tsquery('russian', search_query)
       OR word_similarity(search_query, p.name || ' ' || p.description) > 0.3
    ORDER BY score DESC
    LIMIT 20;
END;

SELECT * FROM combined_search('умнае часы');
```

**SQLAlchemy:**
```python
from sqlalchemy import or_

@app.get("/combined-search")
def combined_search(q: str, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    
    results = db.query(
        Product.id,
        Product.name,
        Product.description,
        func.greatest(
            func.ts_rank(
                func.to_tsvector('russian', query_text),
                func.plainto_tsquery('russian', q)
            ),
            func.word_similarity(q, query_text)
        ).label('score')
    ).filter(
        or_(
            func.to_tsvector('russian', query_text).op('@@')(
                func.plainto_tsquery('russian', q)
            ),
            func.word_similarity(q, query_text) > 0.3
        )
    ).order_by(text('score DESC')).limit(20).all()
    
    return {"results": [{
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "score": float(r.score)
    } for r in results]}
```
