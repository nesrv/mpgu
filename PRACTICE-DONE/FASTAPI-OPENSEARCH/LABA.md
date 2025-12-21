# Лабораторная работа: Поисковая система для каталога товаров

## Цель
Создать API для интернет-магазина с полнотекстовым поиском на базе PostgreSQL, OpenSearch и FastAPI.

## Архитектура
```
FastAPI (REST API)
    ↓
PostgreSQL (основное хранилище)
    ↓
OpenSearch (поисковый индекс)
```

---

## Последовательность выполнения работы

### Шаг 1: Подготовка окружения

**1.1. Создать директорию проекта**
**1.2. Создать виртуальное окружение Python**


### Шаг 2: Настройка инфраструктуры

**2.1. Создать файл `docker-compose.yml`**

Этот файл описывает два сервиса:
- **PostgreSQL** - реляционная БД для хранения товаров
- **OpenSearch** - поисковый движок для быстрого полнотекстового поиска

```yaml
services:
  postgres:
    image: postgres:18
    env_file: .env
    ports:
      - "5437:5432"
    volumes:
      - postgres_data:/var/lib/postgresql

  opensearch:
    image: opensearchproject/opensearch:2.11.0
    env_file: .env
    ports:
      - "9200:9200"
    volumes:
      - opensearch_data:/usr/share/opensearch/data

volumes:
  postgres_data:
  opensearch_data:
```

```sh
# .env
POSTGRES_DB=shop
POSTGRES_USER=user
POSTGRES_PASSWORD=password

discovery.type=single-node
# OpenSearch работает в режиме одного узла (без кластера). 
# Для разработки, не требует настройки сети между узлами.

OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
# Ограничивает память Java для OpenSearch: минимум и максимум по 512 МБ. 
# Без этого может съесть всю доступную RAM.
DISABLE_SECURITY_PLUGIN=true
# Отключает аутентификацию и HTTPS в OpenSearch. 
# Для локальной разработки - не нужно вводить логин/пароль при каждом запросе.

```

**2.2. Запустить контейнеры**
```bash
docker-compose up -d

# docker-compose down -v && docker-compose up -d
```

**2.3. Проверить работу сервисов**
```bash
# PostgreSQL
docker ps | grep postgres

# OpenSearch
curl http://localhost:9200
```

---

### Шаг 3: Установка зависимостей Python

**3.1. Создать файл `requirements.txt`**
```
fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
opensearch-py==2.4.2
pydantic==2.10.5

```

**3.2. Установить зависимости**
```bash
pip install -r requirements.txt
```

---

### Шаг 4: Создание модели данных PostgreSQL

**4.1. Создать файл `database.py`**

Здесь определяем:
- Подключение к PostgreSQL через SQLAlchemy
- Модель таблицы `products` с полями: id, name, description, price, category, popularity

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost:5432/shop"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    popularity = Column(Integer, default=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Пояснение:**
- `engine` - движок для подключения к БД
- `SessionLocal` - фабрика сессий для работы с БД
- `Product` - ORM модель таблицы товаров
- `get_db()` - dependency для FastAPI, создает и закрывает сессию

---

### Шаг 5: Настройка OpenSearch

**5.1. Создать файл `opensearch_client.py`**

Здесь реализуем:
- Подключение к OpenSearch
- Создание индекса с маппингом полей
- Функции для индексации, поиска и автодополнения

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_auth=None,
    use_ssl=False,
    verify_certs=False
)

INDEX_NAME = "products"

INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "id": {"type": "integer"},
            "name": {
                "type": "text",  # Полнотекстовый поиск по названию
                "fields": {
                    "keyword": {"type": "keyword"},  # Точное совпадение и сортировка
                    "suggest": {"type": "completion"}  # Автодополнение
                }
            },
            "description": {"type": "text"},  # Полнотекстовый поиск по описанию
            "price": {"type": "float"},  # Числовое поле для фильтрации и сортировки
            "category": {"type": "keyword"},  # Точное совпадение для фильтров
            "popularity": {"type": "integer"}  # Числовое поле для ранжирования
        }
    }
}

def create_index():
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(index=INDEX_NAME, body=INDEX_MAPPING)

def index_product(product):
    doc = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "category": product.category,
        "popularity": product.popularity
    }
    client.index(index=INDEX_NAME, id=product.id, body=doc)

def search_products(query, category=None, min_price=None, max_price=None):
    must = []
    filters = []
    
    if query:
        must.append({
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "type": "best_fields"
            }
        })
    
    if category:
        filters.append({"term": {"category": category}})
    
    if min_price or max_price:
        range_filter = {"range": {"price": {}}}
        if min_price:
            range_filter["range"]["price"]["gte"] = min_price
        if max_price:
            range_filter["range"]["price"]["lte"] = max_price
        filters.append(range_filter)
    
    body = {
        "query": {
            "bool": {
                "must": must if must else [{"match_all": {}}],
                "filter": filters
            }
        },
        "aggs": {
            "categories": {"terms": {"field": "category"}},
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"to": 1000},
                        {"from": 1000, "to": 5000},
                        {"from": 5000}
                    ]
                }
            }
        }
    }
    
    return client.search(index=INDEX_NAME, body=body)

def suggest_products(prefix):
    body = {
        "query": {
            "match_phrase_prefix": {
                "name": prefix
            }
        },
        "_source": ["name"],
        "size": 5
    }
    return client.search(index=INDEX_NAME, body=body)

```


**Пояснение ключевых моментов:**

1. **Маппинг полей:**
   - `name` имеет 3 типа: `text` (для поиска), `keyword` (для фильтров), `suggest` (для автодополнения)
   - `category` - `keyword` для точного совпадения
   - `price` - `float` для диапазонов

2. **Функция `search_products`:**
   - `multi_match` - поиск по нескольким полям
   - `name^3` - boost (утроенный вес) для названия
   - `bool query` - комбинирует условия поиска и фильтры
   - `aggregations` - подсчет товаров по категориям и ценовым диапазонам

3. **Функция `suggest_products`:**
   - Использует `completion suggester` для быстрого автодополнения

---

### Шаг 6: Создание Pydantic схем

**6.1. Создать файл `schemas.py`**

```python
from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    popularity: int = 0

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    category: str
    popularity: int

    class Config:
        from_attributes = True
```

**Пояснение:**
- `ProductCreate` - схема для создания товара (без id)
- `ProductResponse` - схема для ответа API (с id)
- `from_attributes = True` - позволяет создавать Pydantic модели из ORM объектов

---

### Шаг 7: Создание FastAPI приложения

**7.1. Создать файл `main.py`**

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db, Product
from schemas import ProductCreate, ProductResponse
import opensearch_client as os_client

app = FastAPI(title="Product Search API")

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Создаем товар в PostgreSQL
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    # Синхронизируем с OpenSearch для поиска
    os_client.index_product(db_product)
    return db_product

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/search")
def search(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    # Выполняем поиск в OpenSearch
    results = os_client.search_products(q, category, min_price, max_price)
    return {
        "hits": [hit["_source"] for hit in results["hits"]["hits"]],  # Список найденных товаров
        "total": results["hits"]["total"]["value"],  # Общее количество результатов
        "aggregations": results.get("aggregations", {})  # Фасеты (категории, ценовые диапазоны)
    }

@app.get("/suggest")
def suggest(q: str):
    # Получаем подсказки из OpenSearch
    results = os_client.suggest_products(q)
    suggestions = results["suggest"]["product-suggest"][0]["options"]
    # Возвращаем только текст подсказок
    return {"suggestions": [s["text"] for s in suggestions]}
```

**Пояснение эндпоинтов:**

1. **POST /products** - создание товара:
   - Сохраняет в PostgreSQL
   - Индексирует в OpenSearch
   - Возвращает созданный товар

2. **GET /products/{id}** - получение товара по ID из PostgreSQL

3. **GET /search** - поиск товаров:
   - Принимает параметры: текст запроса, категория, диапазон цен
   - Возвращает найденные товары и агрегации

4. **GET /suggest** - автодополнение:
   - Принимает префикс
   - Возвращает список подсказок

---

### Шаг 8: Инициализация базы данных

**8.1. Создать файл `init_db.py`**

```python
from database import Base, engine, SessionLocal, Product
import opensearch_client as os_client

def init():
    Base.metadata.create_all(bind=engine)
    os_client.create_index()
    
    db = SessionLocal()
    
    # Индексируем все товары в OpenSearch
    for product in db.query(Product).all():
        os_client.index_product(product)
    
    if db.query(Product).count() == 0:
        products = [
            Product(name="iPhone 15 Pro", description="Смартфон Apple с чипом A17 Pro, 256 ГБ", price=119990, category="Смартфоны", popularity=100),
            Product(name="Samsung Galaxy S24 Ultra", description="Флагманский смартфон Samsung с S Pen", price=109990, category="Смартфоны", popularity=95),
           
            # ... остальные товары
        ]
        
        for product in products:
            db.add(product)
            db.commit()
            db.refresh(product)
            os_client.index_product(product)
    
    db.close()
    print("База данных инициализирована!")

if __name__ == "__main__":
    init()
```

**Пояснение:**
- Создает таблицы в PostgreSQL
- Создает индекс в OpenSearch
- Заполняет тестовыми данными
- Синхронизирует данные между PostgreSQL и OpenSearch

**8.2. Запустить инициализацию**
```bash
python init_db.py
```

---

### Шаг 9: Запуск и тестирование

**9.1. Запустить FastAPI сервер**
```bash
uvicorn main:app --reload
```

**9.2. Открыть документацию API и протестировать эндпоинты
```
http://localhost:8000/docs
```


**9.3. Создать файл `test_api.http` для тестирования**

```http
### Автодополнение - поиск iPhone
GET http://localhost:8000/suggest?q=iph

### Автодополнение - поиск Samsung
GET http://localhost:8000/suggest?q=sam

### Автодополнение - поиск MacBook
GET http://localhost:8000/suggest?q=mac

### Автодополнение - поиск по одной букве
GET http://localhost:8000/suggest?q=a

### Автодополнение - пустой результат
GET http://localhost:8000/suggest?q=xyz

### Автодополнение - кириллица
GET http://localhost:8000/suggest?q=яндекс

### Поиск товаров - текстовый запрос
GET http://localhost:8000/search?q=phone

### Поиск товаров - фильтр по категории
GET http://localhost:8000/search?category=Смартфоны

### Поиск товаров - фильтр по цене
GET http://localhost:8000/search?min_price=50000&max_price=100000

### Поиск товаров - комбинированные фильтры
GET http://localhost:8000/search?q=samsung&category=Смартфоны&min_price=80000

### Поиск всех товаров
GET http://localhost:8000/search

### Создание товара
POST http://localhost:8000/products
Content-Type: application/json

{
  "name": "Test Product",
  "description": "Test Description",
  "price": 9999.99,
  "category": "Test Category",
  "popularity": 50
}

### Получение товара по ID
GET http://localhost:8000/products/1

### Получение несуществующего товара
GET http://localhost:8000/products/999

```

VS Code - установи расширение "REST Client", открой файл и нажимай "Send Request" над каждым запросом




**9.4. Тестирование через curl**

```bash
# Поиск
curl "http://localhost:8000/search?q=iPhone"

# Автодополнение
curl "http://localhost:8000/suggest?q=sam"

# Фильтры
curl "http://localhost:8000/search?category=Смартфоны&min_price=80000"
```

---

## Задания для самостоятельной работы

### Задание 1: Синхронизация данных

**Задача:** Реализовать обновление и удаление товара с синхронизацией в OpenSearch

```python
# main.py

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    os_client.index_product(db_product)  # Обновляем в OpenSearch
    return db_product

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    client.delete(index=INDEX_NAME, id=product_id)  # Удаляем из OpenSearch
    return {"message": "Product deleted"}
```

---

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

## Полезные команды

```bash
# Остановить контейнеры
docker-compose down

# Удалить данные
docker-compose down -v

# Посмотреть логи
docker-compose logs -f

# Подключиться к PostgreSQL
docker exec -it lab1_product_search-postgres-1 psql -U user -d shop

# Проверить индексы OpenSearch
curl http://localhost:9200/_cat/indices
```

---

## Критерии оценки

- ✅ Запущены PostgreSQL и OpenSearch
- ✅ Создана таблица и индекс
- ✅ Реализована синхронизация данных
- ✅ Работает полнотекстовый поиск
- ✅ Работает автодополнение
- ✅ Работают фильтры по категориям и ценам
- ✅ Возвращаются агрегации
- ✅ API документирован в Swagger
