html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Лабораторная: PostgreSQL Full-Text Search</title>
<style media="print">
body{font-family:Arial,sans-serif;font-size:12px}.container{box-shadow:none;background:white}.header{background:white!important;color:black!important}.save-btn{display:none!important}.section{page-break-inside:avoid}
</style>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;line-height:1.6;color:#333;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}.container{max-width:1200px;margin:20px auto;padding:20px;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.header{text-align:center;padding:30px;background:linear-gradient(135deg,#005EB8,#003D82);color:white;border-radius:10px;margin-bottom:30px}.header h1{font-size:2.5em;margin-bottom:10px}.student-info{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:30px;padding:20px;background:#f8f9fa;border-radius:10px}.form-group{margin-bottom:20px}.form-group label{display:block;margin-bottom:5px;font-weight:bold;color:#003D82}.form-group input,.form-group textarea{width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px;font-size:16px}.form-group input:focus,.form-group textarea:focus{outline:none;border-color:#005EB8}.section{margin-bottom:40px;padding:25px;background:#fff;border-left:5px solid #005EB8;border-radius:0 10px 10px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.section h2{color:#003D82;margin-bottom:20px;font-size:1.8em}.section h3{color:#005EB8;margin:20px 0 10px;font-size:1.3em}.code-block{background:#282c34;color:#e2e8f0;padding:20px;border-radius:8px;margin:15px 0;font-family:'Courier New',monospace;overflow-x:auto;white-space:pre;font-size:14px}ul{list-style:none;padding-left:0}ul li{padding:8px 0 8px 30px;position:relative}ul li::before{content:'▸';position:absolute;left:0;color:#005EB8;font-size:18px}.save-btn{background:linear-gradient(135deg,#005EB8,#003D82);color:white;border:none;padding:15px 30px;font-size:18px;border-radius:10px;cursor:pointer;display:block;margin:30px auto}.checkbox-item{margin:15px 0;padding:15px 20px;background:linear-gradient(135deg,#005EB8,#003D82);border-radius:10px;display:flex;align-items:center}.checkbox-item input[type="checkbox"]{appearance:none;width:24px;height:24px;border:3px solid white;border-radius:6px;margin-right:15px;cursor:pointer;background:transparent}.checkbox-item input[type="checkbox"]:checked{background:white}.checkbox-item input[type="checkbox"]:checked::after{content:'✓';position:absolute;font-size:18px;color:#005EB8;font-weight:bold}.checkbox-item label{color:white;font-weight:500;cursor:pointer}table{width:100%;border-collapse:collapse;margin:15px 0}table th,table td{border:1px solid #ddd;padding:12px;text-align:left}table th{background:#005EB8;color:white}table tr:nth-child(even){background:#f8f9fa}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
</head>
<body>
<div class="container">
<div class="header">
<h1>🔍 Лабораторная работа</h1>
<h2>Полнотекстовый поиск в PostgreSQL</h2>
<p>PostgreSQL Full-Text Search + FastAPI</p>
</div>
<div class="student-info">
<div class="form-group"><label for="student-name">ФИО:</label><input type="text" id="student-name"></div>
<div class="form-group"><label for="group">Группа:</label><input type="text" id="group"></div>
<div class="form-group"><label for="date">Дата:</label><input type="date" id="date"></div>
</div>
<div class="section">
<h2>🎯 Цель работы</h2>
<p>Изучить полнотекстовый поиск в PostgreSQL: базовый поиск, fuzzy search, синонимы, автодополнение.</p>
</div>
<div class="section">
<h2>📋 Шаг 1: Настройка PostgreSQL</h2>
<h3>1.1. Русский словарь</h3>
<div class="code-block"><code class="language-sql">SELECT cfgname FROM pg_ts_config;
SET default_text_search_config = 'pg_catalog.russian';
ALTER DATABASE shop SET default_text_search_config = 'pg_catalog.russian';</code></div>
<h3>1.2. Токенизация</h3>
<div class="code-block"><code class="language-sql">SELECT to_tsvector('russian', 'Съешь ещё этих мягких французских булок');
-- 'булок':6 'ещ':2 'мягк':4 'съеш':1 'французск':5 'эт':3</code></div>
<p><strong>Формат:</strong> 'основа':позиция</p>
<h3>1.3. Индекс</h3>
<div class="code-block"><code class="language-sql">CREATE INDEX idx_description ON products 
USING gin(to_tsvector('russian', description));</code></div>
<div class="checkbox-item"><input type="checkbox" id="t1"><label for="t1">Настройка выполнена</label></div>
</div>
<div class="section">
<h2>🔤 Шаг 2: Базовый поиск</h2>
<div class="code-block"><code class="language-sql">-- Простой поиск
SELECT * FROM products WHERE to_tsvector('russian', description) @@ to_tsquery('russian', 'умный');

-- AND
SELECT * FROM products WHERE to_tsvector('russian', description) @@ to_tsquery('russian', 'умн & дом');

-- OR
SELECT * FROM products WHERE to_tsvector('russian', description) @@ to_tsquery('russian', 'умн & (дом | телевизор)');

-- Фразовый поиск
SELECT * FROM products WHERE to_tsvector('russian', description) @@ to_tsquery('russian', 'умн <-> телевизор');</code></div>
<h3>Различия функций</h3>
<table>
<tr><th>Функция</th><th>Описание</th></tr>
<tr><td>plainto_tsquery</td><td>Безопасен для пользовательского ввода</td></tr>
<tr><td>to_tsquery</td><td>Поддерживает операторы (&, |, !)</td></tr>
<tr><td>websearch_to_tsquery</td><td>Поддерживает кавычки и минус</td></tr>
</table>
<div class="checkbox-item"><input type="checkbox" id="t2"><label for="t2">Базовый поиск реализован</label></div>
</div>
<div class="section">
<h2>🎯 Шаг 3: Хранимые функции</h2>
<div class="code-block"><code class="language-sql">CREATE OR REPLACE FUNCTION search_products(search_query TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, price NUMERIC, category VARCHAR)
BEGIN ATOMIC
    SELECT id, name, description, price, category FROM products
    WHERE to_tsvector('russian', name || ' ' || description) @@ plainto_tsquery('russian', search_query);
END;

-- С ранжированием
CREATE OR REPLACE FUNCTION search_ranked(search_query TEXT)
RETURNS TABLE(id INTEGER, name VARCHAR, description TEXT, rank REAL)
BEGIN ATOMIC
    SELECT p.id, p.name, p.description,
        ts_rank(to_tsvector('russian', p.name || ' ' || p.description), 
                plainto_tsquery('russian', search_query)) AS rank
    FROM products p
    WHERE to_tsvector('russian', p.name || ' ' || p.description) @@ plainto_tsquery('russian', search_query)
    ORDER BY rank DESC;
END;</code></div>
<div class="checkbox-item"><input type="checkbox" id="t3"><label for="t3">Функции созданы</label></div>
</div>
<div class="section">
<h2>🔧 Шаг 4: Fuzzy Search</h2>
<div class="code-block"><code class="language-sql">CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_name_trgm ON products USING gin (name gin_trgm_ops);

-- Поиск с опечатками
SELECT name, similarity(name, 'яблако') AS sim FROM products
WHERE name % 'яблако' ORDER BY sim DESC LIMIT 10;

-- Функция
CREATE OR REPLACE FUNCTION fuzzy_search(search_term TEXT, threshold REAL DEFAULT 0.3)
RETURNS TABLE(name VARCHAR, description TEXT, similarity REAL)
BEGIN ATOMIC
    SELECT p.name, p.description, word_similarity(search_term, p.name || ' ' || p.description) AS sim
    FROM products p
    WHERE word_similarity(search_term, p.name || ' ' || p.description) > threshold
    ORDER BY sim DESC LIMIT 20;
END;</code></div>
<div class="checkbox-item"><input type="checkbox" id="t4"><label for="t4">Fuzzy search реализован</label></div>
</div>
<div class="section">
<h2>📝 Шаг 5: Автодополнение</h2>
<div class="code-block"><code class="language-sql">CREATE OR REPLACE FUNCTION suggest_products(prefix TEXT)
RETURNS TABLE(name VARCHAR, similarity REAL)
BEGIN ATOMIC
    SELECT DISTINCT p.name, similarity(p.name, prefix) AS sim FROM products p
    WHERE p.name ILIKE prefix || '%' ORDER BY sim DESC, p.name LIMIT 10;
END;</code></div>
<div class="checkbox-item"><input type="checkbox" id="t5"><label for="t5">Автодополнение реализовано</label></div>
</div>
<div class="section">
<h2>🔄 Шаг 6: Синонимы</h2>
<div class="code-block"><code class="language-sql">CREATE TABLE synonyms (word TEXT, synonym TEXT);
INSERT INTO synonyms VALUES ('телефон', 'смартфон'), ('телефон', 'мобильный');
CREATE INDEX idx_synonyms ON synonyms(synonym);

WITH search_terms AS (
    SELECT 'смартфон' AS term UNION SELECT word FROM synonyms WHERE synonym = 'смартфон'
)
SELECT * FROM products WHERE name ILIKE ANY(ARRAY(SELECT '%' || term || '%' FROM search_terms));</code></div>
<div class="checkbox-item"><input type="checkbox" id="t6"><label for="t6">Синонимы реализованы</label></div>
</div>
<div class="section">
<h2>🚀 Шаг 7: FastAPI</h2>
<div class="code-block"><code class="language-python">from fastapi import FastAPI, Depends
from sqlalchemy import text, func
from sqlalchemy.orm import Session

@app.get("/direct-search")
def direct_search(q: str, db: Session = Depends(get_db)):
    rows = db.execute(text("SELECT * FROM search_products(:query)"), {"query": q})
    return {"hits": [dict(row._mapping) for row in rows]}

@app.get("/search-ranked")
def search_ranked(q: str, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    results = db.query(Product.id, Product.name, Product.description,
        func.ts_rank(func.to_tsvector('russian', query_text), func.plainto_tsquery('russian', q)).label('rank')
    ).filter(func.to_tsvector('russian', query_text).op('@@')(func.plainto_tsquery('russian', q))
    ).order_by(text('rank DESC')).all()
    return {"results": [{"id": r.id, "name": r.name, "rank": float(r.rank)} for r in results]}

@app.get("/fuzzy-search")
def fuzzy_search(q: str, threshold: float = 0.3, db: Session = Depends(get_db)):
    query_text = Product.name + ' ' + Product.description
    results = db.query(Product.name, Product.description, func.word_similarity(q, query_text).label('sim')
    ).filter(func.word_similarity(q, query_text) > threshold).order_by(text('sim DESC')).limit(20).all()
    return {"results": [{"name": r.name, "similarity": float(r.sim)} for r in results]}</code></div>
<div class="checkbox-item"><input type="checkbox" id="t7"><label for="t7">FastAPI интеграция выполнена</label></div>
</div>
<div class="section">
<h2>🧪 Шаг 8: Тестирование</h2>
<div class="code-block"><code class="language-bash">uvicorn main:app --reload

### Тесты
GET http://localhost:8000/direct-search?q=умный
GET http://localhost:8000/search-ranked?q=умный дом
GET http://localhost:8000/fuzzy-search?q=умнае часы&threshold=0.2</code></div>
<h3>Нагрузочное тестирование</h3>
<div class="code-block"><code class="language-bash">ab -n 100 -c 10 "http://localhost:8000/direct-search?q=apple"
ab -n 100 -c 10 "http://localhost:8000/search-ranked?q=apple"</code></div>
<h3>Результаты тестирования</h3>
<table>
<tr><th>Параметр</th><th>/search</th><th>/direct-search</th><th>/direct-search-orm</th></tr>
<tr><td>Успешность</td><td>✅ 100%</td><td>⚠️ 34%</td><td>⚠️ 63%</td></tr>
<tr><td>Скорость (запр/сек)</td><td>111.16</td><td>159.14</td><td>168.65</td></tr>
<tr><td>Среднее время (мс)</td><td>89.963</td><td>62.838</td><td>59.296</td></tr>
</table>
<div class="checkbox-item"><input type="checkbox" id="t8"><label for="t8">Тестирование выполнено</label></div>
</div>
<div class="section">
<h2>🔍 Часть 2: Продвинутый поиск</h2>
<h3>Поиск слов внутри текста</h3>
<h4>Решение 1: word_similarity</h4>
<div class="code-block"><code class="language-sql">SELECT description, word_similarity('умный', description) AS sim
FROM products
WHERE 'умный' <% description
ORDER BY sim DESC;</code></div>
<h4>Решение 2: ILIKE с trigram индексом</h4>
<div class="code-block"><code class="language-sql">SELECT description, similarity(description, 'умный') AS sim
FROM products
WHERE description ILIKE '%умны%'
ORDER BY sim DESC;

-- Поиск по похожести всей строки
SELECT description, similarity(description, 'умный') AS sim
FROM products
WHERE description % 'умный'
ORDER BY sim DESC;</code></div>
<table>
<tr><th>description</th><th>similarity</th></tr>
<tr><td>Умный дом</td><td>0.6</td></tr>
<tr><td>Ночник Умник</td><td>0.21428572</td></tr>
<tr><td>Швабра Умница</td><td>0.1764706</td></tr>
<tr><td>Умные часы на Wear OS</td><td>0.16666667</td></tr>
</table>
<h4>Решение 3: word_similarity с префиксным поиском (рекомендуется)</h4>
<div class="code-block"><code class="language-sql">SELECT description, word_similarity('умный', description) AS sim
FROM products
WHERE description ILIKE '%умн%'
ORDER BY sim DESC;</code></div>
<table>
<tr><th>description</th><th>similarity</th></tr>
<tr><td>Умный дом</td><td>1.0</td></tr>
<tr><td>Умные часы с датчиком температуры</td><td>0.6666667</td></tr>
<tr><td>Умные часы на Wear OS</td><td>0.6666667</td></tr>
<tr><td>Умная колонка с Алисой</td><td>0.5</td></tr>
</table>
<div class="checkbox-item"><input type="checkbox" id="t9"><label for="t9">Продвинутый поиск реализован</label></div>
</div>
<div class="section">
<h2>🔧 Расширенный Fuzzy Search</h2>
<h3>1. pg_trgm (рекомендуется)</h3>
<div class="code-block"><code class="language-sql">CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_name_trgm ON products USING gin (name gin_trgm_ops);

-- Поиск с опечатками
SELECT name, similarity(name, 'яблако') AS sim
FROM products
WHERE name % 'яблако'
ORDER BY sim DESC LIMIT 10;

-- Через ILIKE (быстрее)
SELECT name, similarity(name, 'яблако') AS sim
FROM products
WHERE name ILIKE '%яблак%'
ORDER BY sim DESC LIMIT 10;</code></div>
<h3>2. Levenshtein (расстояние редактирования)</h3>
<div class="code-block"><code class="language-sql">CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;

SELECT name, levenshtein(name, 'яблоко') AS dist
FROM products
WHERE levenshtein(name, 'яблоко') <= 3
ORDER BY dist LIMIT 10;</code></div>
<h3>3. Комбинированный подход</h3>
<div class="code-block"><code class="language-sql">SET pg_trgm.similarity_threshold = 0.3;

SELECT name, similarity(name, 'умнае часы') AS sim
FROM products
WHERE name % 'умнае часы'
   OR name ILIKE '%умн%'
   OR name ILIKE '%час%'
ORDER BY sim DESC LIMIT 10;</code></div>
<h3>4. Для слов внутри текста</h3>
<div class="code-block"><code class="language-sql">SELECT description, word_similarity('умнае', description) AS sim
FROM products
WHERE 'умнае' <% description
ORDER BY sim DESC LIMIT 10;</code></div>
<div class="checkbox-item"><input type="checkbox" id="t10"><label for="t10">Расширенный fuzzy search реализован</label></div>
</div>
<div class="section">
<h2>🔄 Synonym Analyzer</h2>
<h3>1. Простое решение через ARRAY</h3>
<div class="code-block"><code class="language-sql">SELECT * FROM products
WHERE name ILIKE ANY(ARRAY['%телефон%', '%смартфон%', '%мобильный%']);

-- Через CASE в CTE
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
WHERE name ILIKE ANY(SELECT '%' || term || '%' FROM synonyms);</code></div>
<h3>2. Через таблицу синонимов</h3>
<div class="code-block"><code class="language-sql">CREATE TABLE synonyms (word TEXT, synonym TEXT);
INSERT INTO synonyms VALUES
    ('телефон', 'смартфон'),
    ('телефон', 'мобильный'),
    ('ноутбук', 'лэптоп');
CREATE INDEX idx_synonyms ON synonyms(synonym);

WITH search_terms AS (
    SELECT 'смартфон' AS term
    UNION
    SELECT word FROM synonyms WHERE synonym = 'смартфон'
)
SELECT * FROM products
WHERE name ILIKE ANY(ARRAY(SELECT '%' || term || '%' FROM search_terms));</code></div>
<h3>3. Через synonym dictionary</h3>
<div class="code-block"><code class="language-sql">-- Создать файл: /usr/share/postgresql/tsearch_data/synonyms.syn
-- Формат: синоним базовое_слово
-- смартфон телефон
-- лэптоп ноутбук

CREATE TEXT SEARCH DICTIONARY syn_simple (
    TEMPLATE = synonym,
    SYNONYMS = synonyms
);

CREATE TEXT SEARCH CONFIGURATION syn_config (COPY = russian);
ALTER TEXT SEARCH CONFIGURATION syn_config
    ALTER MAPPING FOR asciiword, word WITH syn_simple, russian_stem;

SELECT to_tsvector('syn_config', 'смартфон');
SELECT * FROM products
WHERE to_tsvector('syn_config', name) @@ plainto_tsquery('syn_config', 'мобильный');</code></div>
<h3>4. Через Thesaurus (сложный вариант)</h3>
<div class="code-block"><code class="language-sql">-- Создать файл: /usr/share/postgresql/tsearch_data/synonyms.ths
-- Формат: синоним1 синоним2 : базовое_слово
-- телефон смартфон мобильный : телефон

CREATE TEXT SEARCH DICTIONARY syn_dict (
    TEMPLATE = thesaurus,
    DictFile = synonyms,
    Dictionary = russian_stem
);

CREATE TEXT SEARCH CONFIGURATION syn_ru (COPY = pg_catalog.russian);
ALTER TEXT SEARCH CONFIGURATION syn_ru
    ALTER MAPPING FOR asciiword, word WITH syn_dict, russian_stem;

SELECT to_tsvector('syn_ru', 'смартфон');
SELECT * FROM products
WHERE to_tsvector('syn_ru', name) @@ plainto_tsquery('syn_ru', 'мобильный');

CREATE INDEX idx_name_syn ON products 
USING gin(to_tsvector('syn_ru', name));</code></div>
<p><strong>Рекомендация:</strong></p>
<ul>
<li>Простые случаи (до 10 синонимов) → вариант 1 или 2</li>
<li>Средние случаи (динамические синонимы) → вариант 2 (таблица)</li>
<li>Сложные случаи (много синонимов) → вариант 4 (thesaurus)</li>
</ul>
<div class="checkbox-item"><input type="checkbox" id="t11"><label for="t11">Synonym analyzer реализован</label></div>
</div>
<div class="section">
<h2>📚 Самостоятельные задания</h2>
<ol style="padding-left:30px">
<li>Автодополнение - suggest_products(prefix)</li>
<li>Ранжирование - search_ranked(query)</li>
<li>Подсветка - search_highlight(query)</li>
<li>Фильтр по категориям - search_by_category(query, category)</li>
<li>Fuzzy поиск - fuzzy_search(term, threshold)</li>
<li>Комбинированный - combined_search(query)</li>
</ol>
</div>
<div class="section">
<h2>📊 Выводы</h2>
<div class="form-group"><label>Что изучили:</label><textarea rows="4"></textarea></div>
<div class="form-group"><label>Сложности:</label><textarea rows="4"></textarea></div>
<div class="form-group"><label>Применение:</label><textarea rows="4"></textarea></div>
</div>
<button class="save-btn" onclick="window.print()">💾 Сохранить в PDF</button>
</div>
<script>
if(!sessionStorage.getItem('pg-loaded')){localStorage.clear();sessionStorage.setItem('pg-loaded','true')}
['student-name','group','date'].forEach(id=>{const el=document.getElementById(id);el.value=localStorage.getItem(id)||'';el.addEventListener('input',()=>localStorage.setItem(id,el.value))});
document.getElementById('date').value=document.getElementById('date').value||new Date().toISOString().split('T')[0];
document.querySelectorAll('input[type="checkbox"]').forEach(cb=>{if(localStorage.getItem(cb.id)==='true')cb.checked=true;cb.addEventListener('change',()=>localStorage.setItem(cb.id,cb.checked))});
document.querySelectorAll('textarea').forEach((ta,i)=>{const saved=localStorage.getItem('ta-'+i);if(saved)ta.value=saved;ta.addEventListener('input',()=>localStorage.setItem('ta-'+i,ta.value))});
document.addEventListener('DOMContentLoaded',()=>document.querySelectorAll('code').forEach(el=>hljs.highlightElement(el)));
</script>
</body>
</html>"""

with open('laba_postgresql_search.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
print("HTML методичка создана!")
