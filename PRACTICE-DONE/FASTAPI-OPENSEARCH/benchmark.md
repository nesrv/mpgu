# Сравнение производительности поиска

## Тестирование с Apache Bench

### 1. SQL функция (direct-search)
```bash
ab -n 1000 -c 50 "http://localhost:8000/direct-search?q=laptop"
```

### 2. SQLAlchemy ORM (direct-search-orm)
```bash
ab -n 1000 -c 50 "http://localhost:8000/direct-search-orm?q=laptop"
```

### 3. OpenSearch (search)
```bash
ab -n 1000 -c 50 "http://localhost:8000/search?q=laptop"
```

## Параметры теста
- `-n 1000` - общее количество запросов
- `-c 50` - количество конкурентных соединений

## Метрики для сравнения
- **Requests per second** - запросов в секунду
- **Time per request** - среднее время ответа
- **Failed requests** - количество ошибок
