# Инструкция по запуску автотестов

## Установка зависимостей

```bash
pip install -r requirements-test.txt
```

## Запуск тестов

### Запустить все тесты
```bash
pytest
```

### Запустить с подробным выводом
```bash
pytest -v
```

### Запустить конкретный тест
```bash
pytest test_api.py::test_suggest_success
```

### Запустить с покрытием кода
```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## Структура тестов

### test_api.py (с моками)
- `test_suggest_success` - проверка автодополнения с результатами
- `test_suggest_empty` - проверка автодополнения без результатов
- `test_search_with_query` - поиск с текстовым запросом
- `test_search_with_filters` - поиск с фильтрами (категория, цена)
- `test_create_product` - создание товара
- `test_get_product_not_found` - получение несуществующего товара

**Особенности:**
- Используют моки для OpenSearch и БД
- Не требуют запущенных контейнеров
- Быстрые (выполняются за секунды)
- Изолированные (не влияют на реальные данные)

### test_api_real.py (реальное API)
- 6 тестов для `/suggest` (iPhone, Samsung, MacBook, кириллица, пустой результат)
- 5 тестов для `/search` (запрос, категория, цена, комбинированные фильтры)
- 3 теста для CRUD операций с товарами

**Особенности:**
- Тестируют реальное API через httpx
- Требуют запущенные контейнеры (`docker-compose up -d`)
- Требуют запущенный сервер (`uvicorn main:app --reload`)
- Требуют загруженные данные (`py init_db.py`)

### Запуск реальных тестов
```bash
# Запустить только реальные тесты
pytest test_api_real.py -v

# Запустить только тесты suggest
pytest test_api_real.py::test_suggest -v
```
