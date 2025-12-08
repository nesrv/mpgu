# Инструкция по запуску LAB-REDIS-MONGO

## 🚀 Быстрый старт

### 1. Перейти в папку проекта
```bash
cd LAB-REDIS-MONGO
```

### 2. Запустить все сервисы
```bash
docker-compose up --build -d
```

### 3. Проверить статус
```bash
docker-compose ps
```

Должно быть 3 контейнера: `app`, `db`, `mongodb`

## 🧪 Тестирование

### Проверить главную страницу
```bash
curl http://localhost:8000/
```

### Тестировать PostgreSQL счетчик
```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/postgresql_hit -Method POST

# Linux/WSL
curl -X POST http://localhost:8000/postgresql_hit
```

### Тестировать MongoDB счетчик
```bash
# Windows PowerShell
Invoke-WebRequest -Uri http://localhost:8000/mongodb_hit -Method POST

# Linux/WSL
curl -X POST http://localhost:8000/mongodb_hit
```

### Swagger UI
Открыть в браузере: http://localhost:8000/docs

## 📊 Нагрузочное тестирование

### PostgreSQL (через WSL/Linux)
```bash
echo '{}' > post_data.json
ab -n 1000 -c 50 -p post_data.json -T "application/json" http://localhost:8000/postgresql_hit
```

### MongoDB
```bash
ab -n 1000 -c 50 -p post_data.json -T "application/json" http://localhost:8000/mongodb_hit
```

## 🔧 Управление

### Остановить все
```bash
docker-compose down
```

### Посмотреть логи
```bash
docker-compose logs app
docker-compose logs db
docker-compose logs mongodb
```

### Перезапустить
```bash
docker-compose restart app
```

## 📋 Проверка данных

### PostgreSQL
```bash
docker-compose exec db psql -U student -d student_db -c "SELECT * FROM counter;"
```

### MongoDB
```bash
docker-compose exec mongodb mongosh --username student --password password --eval "db.counter.find()"
```

## ❗ Устранение проблем

### Если порты заняты
Изменить порты в `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # вместо 8000:8000
```

### Если контейнеры не запускаются
```bash
docker-compose down -v
docker-compose up --build
```