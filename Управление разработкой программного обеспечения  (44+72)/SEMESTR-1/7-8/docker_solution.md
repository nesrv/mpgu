# Управление проектами
# Лабораторная работа: Контейнеризация с помощью Docker

## Задание 1. "Hello, World!" от Docker
```bash
docker run hello-world
```
**Объяснение:** Команда `docker run` делает сразу три вещи:
1. Ищет образ `hello-world` локально
2. Не находит и качает его из Docker Hub
3. Создает и запускает из него контейнер

### Вопросы для самопроверки:

1. Найдите ID образа hello-world с помощью `docker images`
2. Изучите его историю и слои с помощью `docker history <image_id>`
3. Что вы можете сказать о размере и структуре этого образа?
4. С помощью команды `docker inspect <image_id>` найдите информацию о том, какая команда выполняется внутри контейнера по умолчанию (поле Cmd)
5. Какой образ был использован для создания контейнера?

---

## Задание 2

Создайте свой собственный Dockerfile, который будет выводить сообщение "Привет из моего контейнера!".
Соберите образ (docker build -t my-hello .) и запустите его (docker run my-hello).

## Решение: Создание кастомного Hello World контейнера

### Шаг 1: Создаем рабочую директорию

```bash
# Создаем и переходим в новую директорию
mkdir my-docker-hello
cd my-docker-hello
```

### Шаг 2: Создаем Dockerfile

Создайте файл с именем `Dockerfile` (без расширения) со следующим содержимым:

```dockerfile
FROM alpine:latest
CMD echo "Привет из моего контейнера!"
```

### Шаг 3: Собираем Docker образ

Выполните команду сборки в той же директории, где находится Dockerfile:

```bash
docker build -t my-hello .
```

**Пояснение параметров:**
- `docker build` - команда сборки образа
- `-t my-hello` - тег (имя) для нашего образа
- `.` - путь к контексту сборки (текущая директория)

**Ожидаемый вывод во время сборки:**
```
[+] Building 2.1s (6/6) FINISHED
 => [internal] load build definition from Dockerfile
 => [internal] load .dockerignore
 => [internal] load metadata for docker.io/library/alpine:latest
 => [internal] load build context
 => [1/2] FROM docker.io/library/alpine:latest
 => [2/2] CMD ["echo", "Hello from my custom container!"]
 => exporting to image
 => => writing image sha256:abc123...
 => => naming to docker.io/library/my-hello:latest
```

### Шаг 4: Запускаем контейнер

```bash
docker run my-hello
```

**Ожидаемый результат:**
```
Привет из моего контейнера!
```

### Шаг 5: Проверяем созданный образ

Убедимся, что наш образ создан успешно:

```bash
docker images
```

Вы должны увидеть что-то подобное:
```
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
my-hello      latest    abc123def456   2 minutes ago   7.05MB
```

#### Вариант с ENTRYPOINT

Более продвинутая версия Dockerfile:

```dockerfile
FROM alpine:latest

# Устанавливаем точку входа
ENTRYPOINT ["echo"]

# Устанавливаем команду по умолчанию
CMD ["Привет из моего контейнера!"]
```

С этим вариантом вы можете переопределять сообщение при запуске:

```bash
docker run my-hello "Другое сообщение!"
```


---

## Задание 3. Создание Hello World контейнера с Python

### Шаг 1: Создаем Python скрипт

Создайте файл `app.py` со следующим содержимым:

```python
#!/usr/bin/env python3

def main():
    message = "Привет из моего контейнера!"
    print(message)

if __name__ == "__main__":
    main()
```

### Шаг 3: Создаем Dockerfile

**Упрощенный вариант Dockerfile:**

```dockerfile
FROM python:3.13-rc-alpine

COPY app.py .

CMD ["python", "app.py"]
```

### Шаг 4: Собираем Docker образ

```bash
docker build -t my-hello .
```

### Шаг 5: Запускаем контейнер

```bash
docker run my-hello
```

**Ожидаемый результат:**
```
Hello from my custom container!
```


## Дополнительные варианты реализации

### Вариант 1: С использованием ENTRYPOINT

```dockerfile
FROM python:3.9-alpine

COPY app.py /app/app.py
WORKDIR /app

ENTRYPOINT ["python", "app.py"]
```


**Типовой вариант Dockerfile:**

```dockerfile
FROM python:3.13-rc-alpine

# Устанавливаем метаинформацию
LABEL maintainer="your-name@example.com"
LABEL description="My custom hello world container with Python"

# Копируем Python скрипт в контейнер
COPY app.py /app/app.py

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем Python скрипт при старте контейнера
CMD ["python", "app.py"]
```


### Управление контейнерами

После запуска проверьте статусы контейнеров:

```bash
# Показать все контейнеры (включая остановленные)
docker ps -a
# Удалить контейнеры (если нужно очистить систему)
docker container prune
# Удалить образ
docker rmi my-hello
```

---

## Задание 4. Эксперимент с запуском веб-сервера Nginx
```bash
docker run -d -p 8080:80 --name my-webserver nginx
```
**Объяснение флагов:**
- `-d` (detach) — запустить в фоновом режиме
- `-p 8080:80` (publish) — пробросить порт (порт 80 внутри контейнера доступен снаружи на порту 8080)
- `--name` — дать контейнеру понятное имя

**Действие:** Откройте браузер и перейдите на `http://localhost:8080`. Вы увидите приветственную страницу Nginx!

### Основные команды для управления


```bash
docker ps # показать работающие контейнеры
docker ps -a # показать все контейнеры (включая остановленные)
docker stop my-webserver # остановить контейнер
docker start my-webserver # запустить остановленный контейнер
docker rm my-webserver # удалить контейнер (только после остановки)
docker images # посмотреть список образов
docker rmi nginx # удалить образ
```



---

## Задание 5. Создаем свой FastAPI-контейнер


**Подготовка:**
1. Создайте папку `my_python_app`
2. Внутри создайте два файла: `app.py` и `Dockerfile`

### Содержимое `app.py`:
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get('/')
def hello():
    return {'message': 'Привет от моего первого Docker-приложения!'}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
```

### Содержимое `Dockerfile`:
```dockerfile
# Используем официальный легковесный Python образ как базовый
FROM python:3.13-rc-alpine

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app
# Копируем файл с зависимостями (если бы он был)
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Копируем наш код в контейнер
COPY . .

# Устанавливаем FastAPI и uvicorn
RUN pip install fastapi uvicorn

# Говорим Docker, какой порт будет прослушивать контейнер
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "app.py"]
```
**Запоминаем:**
- `FROM` — основа
- `WORKDIR` — рабочая папка
- `COPY` — копируем файлы
- `RUN` — выполняем команду при сборке
- `EXPOSE` — документация о порте
- `CMD` — команда для запуска

### Сборка образа и запуск контейнера:
```bash
# Переходим в папку с Dockerfile
cd my_python_app

# Собираем образ с тегом 'my-python-app'
docker build -t my-python-app .

# Запускаем контейнер из нашего образа
docker run -d -p 5000:5000 my-python-app
```
Перейдите в браузере на `http://localhost:5000`. Вы увидите сообщение от вашего приложения!


## Дополнительные задания

**Redis - что это и зачем нужно**

Redis (Remote Dictionary Server) - это высокопроизводительная база данных типа "ключ-значение" в памяти.

**Основные особенности:**
- Хранит данные в оперативной памяти (очень быстро)
- Поддерживает различные структуры данных: строки, списки, множества, хеши
- Может использоваться как кеш, брокер сообщений, база данных
- Поддерживает персистентность данных на диск

**Когда используется Redis - практические примеры:**

**1. Кеширование данных**
- Сохранение результатов сложных SQL-запросов
- Кеш API-ответов от внешних сервисов
- Пример: сохранить список товаров на 5 минут вместо запроса к базе

**2. Сессии пользователей**
- Хранение JWT-токенов и данных авторизации
- Корзина покупок в интернет-магазине
- Пример: `user:123:cart` → `[{"id": 1, "qty": 2}, {"id": 5, "qty": 1}]`

**3. Счетчики и статистика**
- Количество просмотров статьи/видео
- Лайки и дизлайки в соцсетях
- Пример: `INCR post:456:views` - увеличить счетчик на 1

**4. Очереди задач**
- Обработка загрузки файлов
- Отправка email-уведомлений
- Пример: `LPUSH email_queue '{"to": "user@mail.com", "subject": "Welcome!"}'`

**5. Ограничение частоты запросов (Rate Limiting)**
- Максимум 100 запросов в минуту от одного IP
- Пример: `INCR ip:192.168.1.1:requests EXPIRE ip:192.168.1.1:requests 60`

**6. Реальное время (Pub/Sub)**
- Чаты и мессенджеры
- Уведомления о новых заказах
- Пример: `PUBLISH notifications '{"user_id": 123, "message": "New order!"}'`

**Основные команды Redis:**
```
SET key value    # установить значение
GET key          # получить значение
DEL key          # удалить ключ
EXISTS key       # проверить существование
KEYS pattern     # найти ключи по шаблону
EXPIRE key sec   # установить время жизни
```

### Задание 6: Взаимодействие FastAPI и Redis (без docker-compose)
Создайте два контейнера, которые взаимодействуют через сеть:

**Шаг 1: Создайте FastAPI приложение с Redis (`app.py`):**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='redis-server', port=6379, decode_responses=True)

class Item(BaseModel):
    name: str
    value: str

@app.get("/")
def root():
    return {"message": "FastAPI + Redis CRUD API"}

```

**Шаг 2: Создайте `requirements.txt`:**
```
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
```

**Шаг 3: Запустите Redis:**
```bash
docker run -d -p 6379:6379 redis:latest
```



**Шаг 4: 

```py
@app.post("/items/{item_id}")
def create_item(item_id: str, item: Item):
    r.set(item_id, json.dumps(item.dict()))
    return {"item_id": item_id, "status": "created"}

@app.get("/items/{item_id}")
def read_item(item_id: str):
    data = r.get(item_id)
    if not data:
        raise HTTPException(status_code=404, detail="Item not found")
    return json.loads(data)

@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item):
    if not r.exists(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    r.set(item_id, json.dumps(item.dict()))
    return {"item_id": item_id, "status": "updated"}

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    if not r.delete(item_id):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "status": "deleted"}

@app.get("/items")
def list_items():
    keys = r.keys("*")
    items = {}
    for key in keys:
        items[key] = json.loads(r.get(key))
    return items

```



Создайте `Dockerfile`:**

**Почему нужен Dockerfile, если есть готовые образы?**
- `docker run redis:latest` - запускает готовый образ без изменений
- Dockerfile - создает кастомный образ с вашим кодом и зависимостями
- Нам нужно упаковать FastAPI приложение + Python зависимости в один образ
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Шаг 5: Запустите контейнеры:**
```bash
# Создать сеть (чтобы контейнеры могли обращаться друг к другу по имени)
docker network create app-network

# Запустить Redis
docker run -d --name redis-server --network app-network redis:7-alpine

# Собрать и запустить FastAPI
docker build -t fastapi-redis .
docker run -d --name fastapi-app --network app-network -p 8000:8000 fastapi-redis
```

**Шаг 6: Тестирование CRUD операций через Swagger UI:**
1. Откройте браузер и перейдите на `http://localhost:8000/docs`
2. Вы увидите автоматически сгенерированную документацию API
3. Протестируйте операции в следующем порядке:

   - **POST /items/{item_id}** - создать элемент:
     - item_id: `1`
     - Request body: `{"name": "test", "value": "data"}`
   
   - **GET /items/{item_id}** - получить элемент:
     - item_id: `1`
   
   - **GET /items** - получить все элементы
   
   - **PUT /items/{item_id}** - обновить элемент:
     - item_id: `1`
     - Request body: `{"name": "updated", "value": "new_data"}`
   
   - **DELETE /items/{item_id}** - удалить элемент:
     - item_id: `1`

4. Альтернативно используйте ReDoc: `http://localhost:8000/redoc`


```bash
# CREATE
curl -X POST "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "value": "data"}'

# READ
curl "http://localhost:8000/items/1"

# UPDATE
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "updated", "value": "new_data"}'

# LIST ALL
curl "http://localhost:8000/items"

# DELETE
curl -X DELETE "http://localhost:8000/items/1"
```

**Практические задачи для студентов:**
1. Создайте FastAPI приложение с эндпоинтом `/health`
2. Соберите образ размером менее 100MB
3. Настройте автоперезапуск контейнера при падении
4. Создайте docker-compose для микросервисной архитектуры
5. Реализуйте hot-reload для разработки
6. Добавьте валидацию данных и обработку ошибок подключения к Redis

---