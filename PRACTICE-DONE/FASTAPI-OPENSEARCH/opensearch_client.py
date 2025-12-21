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

def fuzzy_search(query):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "description"],
                "fuzziness": "AUTO"
            }
        }
    }
    return client.search(index=INDEX_NAME, body=body)

