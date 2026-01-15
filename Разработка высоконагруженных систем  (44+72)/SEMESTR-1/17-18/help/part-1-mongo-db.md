# Подключение к графическому интерфейсу MongoDB

## 🖥️ MongoDB Compass (Рекомендуется)

### Установка
1. Скачать с https://www.mongodb.com/products/compass
https://github.com/mongodb-js/compass/releases/download/v1.48.2/mongodb-compass-1.48.2-win32-x64.msi

2. Установить MongoDB Compass

### Подключение
**Connection String:**
```
mongodb://student:password@localhost:27017/
```

**Или заполнить поля:**
- **Host**: `localhost`
- **Port**: `27017`
- **Username**: `student`
- **Password**: `password`
- **Authentication Database**: `admin`



## 🌐 MongoDB Express (Web интерфейс)

### Добавить в docker-compose.yml
```yaml
  mongo-express:
    image: mongo-express
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: student
      ME_CONFIG_MONGODB_ADMINPASSWORD: password
      ME_CONFIG_MONGODB_URL: mongodb://student:password@mongodb:27017/
      ME_CONFIG_BASICAUTH_USERNAME: admin
      ME_CONFIG_BASICAUTH_PASSWORD: admin
    depends_on:
      - mongodb
```

### Запуск
```bash
docker-compose up mongo-express -d
```

### Доступ
Открыть: http://localhost:8081
- **Логин**: `admin`
- **Пароль**: `admin`

