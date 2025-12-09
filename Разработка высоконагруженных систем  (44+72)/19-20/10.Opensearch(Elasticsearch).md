# Работа с датасетом книг в OpenSearch/Elasticsearch

## 📚 Описание датасета

20 классических русских книг с полями:
- `title` - название
- `author` - автор
- `year` - год публикации
- `genre` - жанр
- `annotation` - аннотация

## 🚀 Быстрый старт

### 1. Запуск OpenSearch через Docker

```bash
docker run -d \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  --name opensearch \
  opensearchproject/opensearch:latest
```

### 2. Проверка подключения

```bash
curl http://localhost:9200
```

### 3. Импорт данных

**Создать индекс:**
```bash
curl -X PUT "http://localhost:9200/books" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "author": {"type": "keyword"},
      "year": {"type": "integer"},
      "genre": {"type": "keyword"},
      "annotation": {"type": "text"}
    }
  }
}'
```

**Импортировать книги (по одной):**
```bash
curl -X POST "http://localhost:9200/books/_doc" -H 'Content-Type: application/json' -d'
{
  "title": "Война и мир",
  "author": "Лев Толстой",
  "year": 1869,
  "genre": "роман",
  "annotation": "Эпический роман о русском обществе в эпоху войн против Наполеона."
}'
```

## 🔍 Основные запросы

### Поиск всех документов
```bash
curl -X GET "http://localhost:9200/books/_search?pretty"
```

### Поиск по названию
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "title": "война"
    }
  }
}'
```

### Поиск по автору
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "author": "Лев Толстой"
    }
  }
}'
```

### Поиск по диапазону лет
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "year": {
        "gte": 1860,
        "lte": 1880
      }
    }
  }
}'
```

### Полнотекстовый поиск по аннотации
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "annotation": "любовь революция"
    }
  }
}'
```

## 📊 Агрегации

### Группировка по жанрам
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "genres": {
      "terms": {
        "field": "genre"
      }
    }
  }
}'
```

### Группировка по авторам
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "authors": {
      "terms": {
        "field": "author"
      }
    }
  }
}'
```

### Статистика по годам
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "year_stats": {
      "stats": {
        "field": "year"
      }
    }
  }
}'
```

## 🎯 Сложные запросы

### Булевый поиск (AND)
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        {"match": {"annotation": "война"}},
        {"term": {"genre": "роман"}}
      ]
    }
  }
}'
```

### Поиск с сортировкой
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {"match_all": {}},
  "sort": [
    {"year": {"order": "desc"}}
  ]
}'
```

### Поиск с пагинацией
```bash
curl -X GET "http://localhost:9200/books/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {"match_all": {}},
  "from": 0,
  "size": 5
}'
```

## 📝 Практические задания

1. Найти все книги Достоевского
2. Найти книги, опубликованные после 1900 года
3. Найти все романы
4. Полнотекстовый поиск слова "любовь" в аннотациях
5. Подсчитать количество книг каждого автора
6. Найти самую старую и самую новую книгу

## 📊 OpenSearch Dashboards

### Запуск Dashboards

```bash
docker run -d \
  -p 5601:5601 \
  -e "OPENSEARCH_HOSTS=http://opensearch:9200" \
  -e "DISABLE_SECURITY_DASHBOARDS_PLUGIN=true" \
  --link opensearch \
  --name opensearch-dashboards \
  opensearchproject/opensearch-dashboards:latest
```

Открыть: http://localhost:5601

### Работа в Dev Tools

1. Открыть **Dev Tools** в меню слева
2. В консоли вводить запросы

**Пример 1: Поиск всех книг**
```json
GET /books/_search
{
  "query": {
    "match_all": {}
  }
}
```

**Пример 2: Поиск по названию**
```json
GET /books/_search
{
  "query": {
    "match": {
      "title": "война"
    }
  }
}
```

**Пример 3: Фильтрация по автору**
```json
GET /books/_search
{
  "query": {
    "term": {
      "author": "Лев Толстой"
    }
  }
}
```

### Выполнение заданий в Dashboards

**Задание 1: Найти все книги Достоевского**
```json
GET /books/_search
{
  "query": {
    "term": {
      "author": "Фёдор Достоевский"
    }
  }
}
```

**Задание 2: Книги после 1900 года**
```json
GET /books/_search
{
  "query": {
    "range": {
      "year": {
        "gt": 1900
      }
    }
  }
}
```

**Задание 3: Все романы**
```json
GET /books/_search
{
  "query": {
    "term": {
      "genre": "роман"
    }
  }
}
```

**Задание 4: Поиск "любовь" в аннотациях**
```json
GET /books/_search
{
  "query": {
    "match": {
      "annotation": "любовь"
    }
  }
}
```

**Задание 5: Количество книг каждого автора**
```json
GET /books/_search
{
  "size": 0,
  "aggs": {
    "authors_count": {
      "terms": {
        "field": "author",
        "size": 20
      }
    }
  }
}
```

**Задание 6: Самая старая и новая книга**
```json
GET /books/_search
{
  "size": 0,
  "aggs": {
    "oldest": {
      "min": {
        "field": "year"
      }
    },
    "newest": {
      "max": {
        "field": "year"
      }
    }
  }
}
```

### Создание визуализаций

1. **Visualize** → **Create visualization**
2. Выбрать тип: Pie, Bar, Line
3. Выбрать индекс: `books`

**Пример: Круговая диаграмма по жанрам**
- Metrics: Count
- Buckets: Terms → Field: `genre`

**Пример: Гистограмма по годам**
- Metrics: Count
- Buckets: Histogram → Field: `year`, Interval: 10

### Discover (Просмотр данных)

1. **Discover** в меню
2. Выбрать индекс `books`
3. Использовать фильтры:
   - Add filter → `author` is `Лев Толстой`
   - Add filter → `year` is between 1860 and 1880

## 🐍 Python клиент

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    use_ssl=False
)

# Поиск
response = client.search(
    index="books",
    body={
        "query": {
            "match": {"title": "война"}
        }
    }
)

for hit in response['hits']['hits']:
    print(hit['_source'])
```