### Задание 2: Улучшение поиска

**Задача:** Добавить поиск по синонимам и fuzzy search

```python
# opensearch_client.py

# Создание индекса с синонимами
INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "synonym_filter": {
                    "type": "synonym",
                    "synonyms": [
                        "телефон, смартфон, phone",
                        "ноутбук, лэптоп, laptop",
                        "наушники, гарнитура, headphones"
                    ]
                }
            },
            "analyzer": {
                "synonym_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "synonym_filter"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "name": {
                "type": "text",
                "analyzer": "synonym_analyzer",  # Используем анализатор с синонимами
                "fields": {
                    "keyword": {"type": "keyword"},
                    "suggest": {"type": "completion"}
                }
            },
            # ... остальные поля
        }
    }
}

# Fuzzy search
def fuzzy_search(query):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "fuzziness": "AUTO"  # Автоматическая коррекция опечаток
            }
        }
    }
    return client.search(index=INDEX_NAME, body=body)
```

```python
# main.py

@app.get("/fuzzy-search")
def fuzzy_search_endpoint(q: str):
    results = os_client.fuzzy_search(q)
    return {"hits": [hit["_source"] for hit in results["hits"]["hits"]]}
```

---

### Задание 3: Расширенная аналитика

**Задача:** Добавить агрегацию по брендам и статистику по ценам

```python
# database.py - добавить поле brand

class Product(Base):
    __tablename__ = "products"
    # ... существующие поля
    brand = Column(String(100))  # Новое поле
```

```python
# opensearch_client.py

def get_analytics(category=None):
    filters = []
    if category:
        filters.append({"term": {"category": category}})
    
    body = {
        "size": 0,  # Не возвращаем документы, только агрегации
        "query": {
            "bool": {"filter": filters} if filters else {"match_all": {}}
        },
        "aggs": {
            "brands": {
                "terms": {"field": "brand.keyword"}  # Топ брендов
            },
            "price_stats": {
                "stats": {"field": "price"}  # Мин, макс, средняя цена
            },
            "avg_price_by_category": {
                "terms": {"field": "category"},
                "aggs": {
                    "avg_price": {"avg": {"field": "price"}}
                }
            }
        }
    }
    return client.search(index=INDEX_NAME, body=body)
```

```python
# main.py

@app.get("/analytics")
def analytics(category: Optional[str] = None):
    results = os_client.get_analytics(category)
    aggs = results["aggregations"]
    return {
        "brands": aggs["brands"]["buckets"],
        "price_stats": aggs["price_stats"],
        "avg_by_category": aggs["avg_price_by_category"]["buckets"]
    }
```

---

### Задание 4: Производительность

**Задача:** Измерить время поиска и добавить кэширование

```python
# main.py

import time
from functools import lru_cache

@app.get("/benchmark")
def benchmark(q: str, db: Session = Depends(get_db)):
    # Поиск в PostgreSQL
    start = time.time()
    pg_results = db.query(Product).filter(
        Product.name.ilike(f"%{q}%")
    ).all()
    pg_time = time.time() - start
    
    # Поиск в OpenSearch
    start = time.time()
    os_results = os_client.search_products(q)
    os_time = time.time() - start
    
    return {
        "postgresql": {"time_ms": pg_time * 1000, "count": len(pg_results)},
        "opensearch": {"time_ms": os_time * 1000, "count": os_results["hits"]["total"]["value"]}
    }

# Кэширование популярных запросов
@lru_cache(maxsize=100)
def cached_search(q: str, category: str = None):
    return os_client.search_products(q, category)

@app.get("/cached-search")
def search_cached(q: str, category: Optional[str] = None):
    results = cached_search(q, category)
    return {
        "hits": [hit["_source"] for hit in results["hits"]["hits"]],
        "total": results["hits"]["total"]["value"]
    }
```

**Альтернатива: Redis для кэширования**

```python
# requirements.txt - добавить
redis==5.0.1

# cache.py
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_cached(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None

def set_cached(key, value, ttl=300):
    redis_client.setex(key, ttl, json.dumps(value))

# main.py
from cache import get_cached, set_cached

@app.get("/redis-search")
def redis_search(q: str):
    cache_key = f"search:{q}"
    cached = get_cached(cache_key)
    
    if cached:
        return {**cached, "from_cache": True}
    
    results = os_client.search_products(q)
    response = {
        "hits": [hit["_source"] for hit in results["hits"]["hits"]],
        "total": results["hits"]["total"]["value"]
    }
    
    set_cached(cache_key, response, ttl=300)  # Кэш на 5 минут
    return {**response, "from_cache": False}
```

```yaml
# docker-compose.yml - добавить Redis
services:
  # ... существующие сервисы
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## Структура проекта

```
lab1_product_search/
├── docker-compose.yml      # Конфигурация Docker
├── requirements.txt        # Зависимости Python
├── database.py            # Модель PostgreSQL
├── opensearch_client.py   # Клиент OpenSearch
├── schemas.py             # Pydantic схемы
├── main.py                # FastAPI приложение
├── init_db.py             # Инициализация БД
└── test_api.http          # Тесты API
```

---
