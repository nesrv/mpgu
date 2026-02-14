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
Привет из моего контейнера!
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


## Взаимодействие контейнеров. FastAPI и Redis

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

```bash
# 1. SET - установить значение
SET user:1:name "John"
# Ответ: OK

# 2. GET - получить значение
GET user:1:name
# Ответ: "John"

# 3. DEL - удалить ключ
DEL user:1:name
# Ответ: (integer) 1  (количество удалённых ключей)

# 4. EXISTS - проверить существование
EXISTS user:1:name
# Ответ: (integer) 1 (существует) или 0 (не существует)

# 5. KEYS - найти ключи по шаблону
KEYS user:*
# Ответ: 1) "user:1:name" 2) "user:2:name"

# 6. EXPIRE - установить время жизни (в секундах)
SET session:abc123 "user_data"
EXPIRE session:abc123 3600
# Ключ удалится через 1 час

# 7. TTL - проверить оставшееся время жизни
TTL session:abc123
# Ответ: (integer) 3599 (секунд осталось)

# 8. INCR - увеличить счётчик на 1
SET views:post:1 100
INCR views:post:1
# Ответ: (integer) 101

# 9. DECR - уменьшить счётчик на 1
DECR views:post:1
# Ответ: (integer) 100

# 10. MSET - установить несколько значений
MSET user:1:name "John" user:1:age "30" user:1:city "Moscow"
# Ответ: OK

# 11. MGET - получить несколько значений
MGET user:1:name user:1:age user:1:city
# Ответ: 1) "John" 2) "30" 3) "Moscow"
```


**Практические примеры использования:**

**Шаг 1: Подключитесь к Redis CLI и попробуйте команды**

```bash
# Скачать к Redis
docker pull redis:7-alpine

# Скачать и сразу запустить
docker run -d --name redis-server -p 6379:6379 redis:7-alpine

# Подключиться к Redis
docker exec -it redis-server redis-cli

# Создать данные (CREATE)
SET user:1 '{"name":"Anna","age":25}'
SET user:2 '{"name":"Ivan","age":30}'

# Прочитать данные (READ)
GET user:1

# Обновить данные (UPDATE)
SET user:1 '{"name":"Anna","age":26}'

# Удалить данные (DELETE)
DEL user:2

# Проверить все ключи
KEYS user:*
```

```bash
# Пример 1: Кеширование данных пользователя
SET user:123:profile '{"name":"Anna","email":"anna@mail.ru"}'
EXPIRE user:123:profile 300  # Кеш на 5 минут
GET user:123:profile

# Пример 2: Счётчик просмотров
SET post:456:views 0
INCR post:456:views  # +1 просмотр
INCR post:456:views  # +1 просмотр
GET post:456:views   # Результат: 2

# Пример 3: Сессия пользователя
SET session:xyz789 "user_id:123"
EXPIRE session:xyz789 1800  # Сессия на 30 минут
GET session:xyz789

# Пример 4: Поиск всех сессий
KEYS session:*

# Пример 5: Удаление всех ключей (ОСТОРОЖНО!)
FLUSHALL  # Удаляет ВСЕ данные из Redis
```



**Шаг 2: Попробуйте команды через Python**

Создайте файл `test_redis.py`:

```python
import redis
import json

# Подключение к Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# CREATE
user = {"name": "Anna", "age": 25}
r.set("user:1", json.dumps(user))
print("Created:", user)

# READ
data = r.get("user:1")
user = json.loads(data)
print("Read:", user)

# UPDATE
user["age"] = 26
r.set("user:1", json.dumps(user))
print("Updated:", user)

# DELETE
r.delete("user:1")
print("Deleted user:1")

# LIST ALL
keys = r.keys("user:*")
print("All users:", keys)
```

**Шаг 3: Запустите тест**

```bash
pip install redis
python test_redis.py
```

**Шаг 4: Coздайте FastAPI-сервер 'app.py' на основе test_redis.py **

```py
from fastapi import FastAPI, HTTPException
import redis
import json


app = FastAPI()

# r = redis.Redis(host='redis-server', port=6379, decode_responses=True)
r = redis.Redis(host='localhost', port=6381, decode_responses=True)

@app.get("/")
def root():
    return {"message": "FastAPI + Redis CRUD API"}

@app.get("/health/redis")
def test_redis():
    try:
        r.ping()
        return {"status": "connected", "message": "Redis is working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# uvicorn app:app --reload
```
Протестируйте через сваггер работу локального фастапи с Redis-контейнером 

Добавьте в `app.py` следующие функции:

```python
# сохраняет в Redis: ключ = name, значение = value
@app.post("/items")
def test_post(name: str, value: str):
    ...
    return {"status": "saved", "name": name, "value": value}

# эндпоинт для установления времени жизни
@app.post("/items/expire")
def test_post_with_ttl(name: str, value: str, ttl: int = 60):
   ...
    return {"status": "saved", "name": name, "value": value, "ttl": ttl}

# эндпоинт для установки TTL существующему ключу
@app.post("/items/{name}/expire")
def set_ttl(name: str, seconds: int):
    if not r.exists(name):
        raise HTTPException(404, "Key not found")
    ...
    return {"name": name, "ttl": seconds}


 Получить количество всех элементов
@app.get("/items/stats/count")
def count_items():
    ...
    return {"total_items": count}

# Очистить все данные
@app.delete("/items/clear")
def clear_all():
    ...
    return {"status": "cleared", "deleted": len(keys)}


# Проверить время жизни элемента
@app.get("/items/{item_id}/ttl")
def get_ttl(item_id: str):
    ...
    if ...:
        raise HTTPException(404, "Item not found")
    return {"item_id": item_id, "ttl": ttl}

# 5. Поиск по паттерну
# Pattern - это шаблон для поиска ключей:
#   * - любое количество символов (пример: user:* найдёт user:1, user:2, user:abc)
#   ? - один любой символ (пример: user:? найдёт user:1, user:a)
#   [abc] - один из указанных символов (пример: user:[123] найдёт user:1, user:2, user:3)
 # Примеры использования:
    # /items/search/* - найти все ключи
    # /items/search/user:* - найти все ключи, начинающиеся с user:
    # /items/search/user:1* - найти user:1, user:10, user:123

@app.get("/items/search/{pattern}")
def search_items(pattern: str):
    keys = r.keys(pattern)
    if not keys:
        return {}
    return ...

```

### Задание 6: Взаимодействие FastAPI и Redis (без docker-compose)
Создайте два контейнера, которые взаимодействуют через сеть:

**Шаг : Создайте `requirements.txt`:**
```
fastapi==0.104.1
uvicorn==0.24.0
redis==5.0.1
```

**Шаг : Запустите Redis:**
```bash
docker run -d -p 6379:6379 redis:latest
```


Создайте `Dockerfile`:**

**Почему нужен Dockerfile, если есть готовые образы?**
- `docker run redis:latest` - запускает готовый образ без изменений
- Dockerfile - создает кастомный образ с вашим кодом и зависимостями
- Нам нужно упаковать FastAPI приложение + Python зависимости в один образ

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```


# Собрать образ
docker build -t fastapi-app .

# Запустить контейнер

docker run -it -p 8000:8000 fastapi-app

# Тестирование CRUD операций через Swagger UI:**
 Откройте браузер и перейдите на `http://localhost:8000/docs`


Если нужно подключиться к Redis контейнеру, создайте сеть:
```bash
# Создать сеть (если не существует)
docker network create app-network 2>/dev/null || true

# Остановить и удалить старые контейнеры
docker stop redis-server fastapi-app 2>/dev/null || true
docker rm redis-server fastapi-app 2>/dev/null || true

# Запустить Redis
docker run -d --name redis-server --network app-network redis:7-alpine

# Собрать и запустить FastAPI
docker build -t fastapi-redis .
docker run -d --name fastapi-app --network app-network -p 8000:8000 fastapi-redis
```


** Тестирование CRUD операций через Swagger UI: **

Результаты работы студента:

Исходники
```py
# фастапи-сервер + CRUD для редис


```



Всю сеть можно поднять одной командой через docker-compose (создайте docker-compose.yml):

```bash
services:
  redis:
    image: redis:7-alpine
    container_name: redis-server
  
  app:
    build: .
    container_name: fastapi-app
    ports:
      - "8000:8000"
    depends_on:
      - redis

```
Запуск:

`docker-compose up -d --build`


