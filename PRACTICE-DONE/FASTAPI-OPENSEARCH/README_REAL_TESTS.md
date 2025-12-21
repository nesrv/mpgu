# Инструкция по запуску тестов на реальном API

## Подготовка окружения

### 1. Установка зависимостей
```bash
pip install -r requirements-test.txt
```

### 2. Запуск инфраструктуры
```bash
# Запустить PostgreSQL и OpenSearch
docker-compose up -d

# Проверить статус контейнеров
docker-compose ps
```

### 3. Инициализация данных
```bash
# Создать таблицы и загрузить тестовые данные
.\venv\Scripts\python.exe init_db.py
```

### 4. Запуск API сервера
```bash
# В отдельном терминале
uvicorn main:app --reload
```

## Запуск тестов

### Запустить все тесты
```bash
pytest test_api_real.py -v
```

### Запустить конкретную группу тестов
```bash
# Только тесты suggest
pytest test_api_real.py -k "suggest" -v

# Только тесты search
pytest test_api_real.py -k "search" -v

# Только тесты CRUD
pytest test_api_real.py -k "product" -v
```

### Запустить один тест
```bash
pytest test_api_real.py::test_suggest_iphone -v
```

### Запустить с выводом print
```bash
pytest test_api_real.py -v -s
```

## Проверка перед запуском

### Проверить доступность API
```bash
curl http://localhost:8000/docs
```

### Проверить данные в OpenSearch
```bash
curl http://localhost:9200/products/_search?size=1
```

### Проверить данные в PostgreSQL
```bash
.\venv\Scripts\python.exe -c "from database import SessionLocal, Product; db = SessionLocal(); print(f'Products: {db.query(Product).count()}')"
```

## Структура тестов

### Suggest endpoint (6 тестов)
- `test_suggest_iphone` - поиск iPhone
- `test_suggest_samsung` - поиск Samsung
- `test_suggest_macbook` - поиск MacBook
- `test_suggest_single_letter` - поиск по одной букве
- `test_suggest_empty` - пустой результат
- `test_suggest_cyrillic` - поиск кириллицей

### Search endpoint (5 тестов)
- `test_search_with_query` - текстовый поиск
- `test_search_by_category` - фильтр по категории
- `test_search_by_price` - фильтр по цене
- `test_search_combined_filters` - комбинированные фильтры
- `test_search_all` - поиск всех товаров

### Product CRUD (3 теста)
- `test_create_product` - создание товара
- `test_get_product` - получение товара
- `test_get_product_not_found` - несуществующий товар

## Устранение проблем

### API не отвечает
```bash
# Проверить, запущен ли сервер
curl http://localhost:8000/docs
```

### Пустые результаты поиска
```bash
# Переиндексировать данные
curl -X DELETE http://localhost:9200/products
.\venv\Scripts\python.exe init_db.py
```

### Ошибка подключения к БД
```bash
# Проверить порт PostgreSQL в docker-compose.yml и database.py
docker-compose ps
```

## Очистка после тестов

```bash
# Остановить контейнеры
docker-compose down

# Удалить данные
docker-compose down -v
```
