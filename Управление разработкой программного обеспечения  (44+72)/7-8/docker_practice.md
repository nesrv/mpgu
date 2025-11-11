
#### **Часть 3: Практика! Работа с Docker CLI (30 минут)**

**(Преподаватель)**
"Теперь давайте перейдем к самому интересному — практике. Откройте свои терминалы."

*Ведите демонстрацию в реальном времени, комментируя каждую команду.*

**1. "Hello, World!" от Docker**
```bash
docker run hello-world
```
*   **Объяснение:** "Команда `docker run` делает сразу три вещи:
    1.  Ищет образ `hello-world` локально.
    2.  Не находит и качает его из Docker Hub.
    3.  Создает и запускает из него контейнер.
    Вы только что запустили свой первый контейнер!"

**2. Запуск чего-то полезного: веб-сервер Nginx**
```bash
docker run -d -p 8080:80 --name my-webserver nginx
```
*   **Объяснение флагов:**
    *   `-d` (detach) — запустить в фоновом режиме.
    *   `-p 8080:80` (publish) — пробросить порт. "Порт 80 внутри контейнера (где работает nginx) теперь доступен снаружи на порту 8080 вашей машины."
    *   `--name` — дать контейнеру понятное имя.
*   **Действие:** "Откройте браузер и перейдите на `http://localhost:8080`. Вы увидите приветственную страницу Nginx, работающую внутри контейнера!"

**3. Основные команды для управления**
```bash
docker ps # показать работающие контейнеры
docker ps -a # показать все контейнеры (включая остановленные)
docker stop my-webserver # остановить контейнер
docker start my-webserver # запустить остановленный контейнер
docker rm my-webserver # удалить контейнер (только после остановки)
docker images # посмотреть список образов
docker rmi nginx # удалить образ
```
*   **Объяснение:** "Эти команды — ваш основной инструмент для управления жизненным циклом контейнеров."

---

#### **Часть 4: Создаем свой образ (25 минут)**

**(Преподаватель)**
"Запускать готовые образы — это здорово. Но настоящая магия начинается, когда вы создаете свои. Давайте упакуем простое Python-приложение."

**1. Подготовка:**
*   Создайте папку `my_python_app`.
*   Внутри создайте два файла: `app.py` и `Dockerfile`.

**2. Содержимое `app.py`:**
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

**3. Содержимое `Dockerfile`:**
```dockerfile
# Используем официальный легковесный Python образ как базовый
FROM python:3.9-slim

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
*   **Построчно разберите Dockerfile:** "`FROM` — основа, `WORKDIR` — рабочая папка, `COPY` — копируем файлы, `RUN` — выполняем команду при сборке, `EXPOSE` — документация о порте, `CMD` — команда для запуска."

**4. Сборка образа и запуск контейнера:**
```bash
# Переходим в папку с Dockerfile
cd my_python_app

# Собираем образ с тегом 'my-python-app'
docker build -t my-python-app .

# Запускаем контейнер из нашего образа
docker run -d -p 5000:5000 my-python-app
```
*   **Действие:** "Перейдите в браузере на `http://localhost:5000`. Вы увидите сообщение от вашего собственного приложения, работающего в изолированном контейнере!"

---

#### **Часть 5: Дополнительные задания**

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

**Задание 6: Взаимодействие FastAPI и Redis (без docker-compose)**
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

**Шаг 4: Создайте `Dockerfile`:**

*Почему нужен Dockerfile, если есть готовые образы?*
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