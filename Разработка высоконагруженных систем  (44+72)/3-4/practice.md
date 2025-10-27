# Методичка и отчет по работе:

студент {фио} группа {группа} {дата}

## Изучение RESTful API на примере FastAPI

## 1. Настройка виртуального окружения на основе uv

### Что такое uv?

**uv** — менеджер пакетов Python на основе Rust, созданный для быстрой и надежной работы. Его основная цель — обеспечить максимально быструю установку, разрешение зависимостей и создание виртуальных окружений, значительно превосходя по скорости существующие альтернативы.

### Преимущества uv

**Производительность:**
- Создание виртуальных окружений в ~80 раз быстрее, чем `python -m venv`
- Установка пакетов в 4-12 раз быстрее без кэширования
- Установка пакетов в ~100 раз быстрее с кэшированием

**Причины высокой скорости:**
- **Rust под капотом** — компилируется в машинный код, минимальные накладные расходы
- **Параллельная обработка** — одновременная загрузка и установка пакетов
- **Оптимизированное разрешение зависимостей** — быстрый поиск совместимых версий
- **Эффективное кэширование** — минимизация повторных загрузок

### Почему uv лучше для обучения?

🚀 **Скорость**
- В 10-100 раз быстрее Poetry
- Мгновенная установка зависимостей
- Не теряем время на ожидание

🎯 **Простота**
- Один инструмент для всего: `uv init`, `uv add`, `uv run`
- Меньше команд для запоминания
- Автоматическое управление виртуальными окружениями

📦 **Современность**
- Написан на Rust (как ruff)
- Поддерживает все современные стандарты Python
- Активно развивается командой Astral

[] Выполнено  ✅ не получилось ❌

### Установка uv

**Windows (PowerShell):**
```powershell
# Способ 1: через winget
winget install astral-sh.uv

# Способ 2: через PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Способ 3: через pip
pip install uv
```

**Проверка установки:**
```powershell
uv --version
```

[] Выполнено  ✅ не получилось ❌

### Создание проекта с uv

```bash
# Создание проекта
uv init my-api
cd my-api

[] Выполнено  ✅ не получилось ❌

# Добавление зависимостей
uv add fastapi uvicorn strawberry-graphql

# Запуск
uv run uvicorn main:app --reload
```

### Структура проекта

После выполнения `uv init` создается следующая структура:

```
my-api/
├── .git/              # папка для работы с Git
├── main.py            # автосгенерированный файл приложения
├── pyproject.toml     # файл конфигурации проекта
├── README.md          # описание проекта
└── .python-version    # номер применяемой версии Python
```

[] Выполнено  ✅ не получилось ❌

### Основные команды uv

| Команда | Описание |
|---------|----------|
| `uv init <project-name>` | Создает и инициализирует проект Python |
| `uv venv` | Создает виртуальную среду в текущем проекте |
| `uv add <package-name>` | Добавляет пакет к зависимостям проекта |
| `uv pip install -r requirements.txt` | Устанавливает зависимости из requirements.txt |
| `uv remove <package-name>` | Удаляет пакет из зависимостей |
| `uv run script.py` | Запускает скрипт Python внутри проекта |
| `uv sync` | Устанавливает все зависимости из uv.lock |


[] Выполнено  ✅ не получилось ❌

### Работа с виртуальным окружением

```bash
# Создание виртуального окружения
python -m uv venv

# Активация (Windows)
.\.venv\Scripts\activate

# Добавление пакета
python -m uv add matplotlib
```

[] Выполнено  ✅ не получилось ❌

### Пример: График с matplotlib

```python
import matplotlib.pyplot as plt

def main():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    rates = [13.58, 15.33, 14.26, 13.92, 12.74, 12.2, 
             13.44, 15.63, 15.74, 17.08, 17.18, 16.66]
    
    plt.xlabel("month")
    plt.ylabel("rate")
    plt.plot(months, rates)
    plt.show()

if __name__ == "__main__":
    main()
```

[] Выполнено  ✅ не получилось ❌

## 2. Введение в FastAPI

# Введение в FastAPI

## 🚀 Обзор

**FastAPI** — это современный веб-фреймворк для создания API на Python, который отличается:
- Высокой производительностью
- Простотой использования
- Современным подходом к разработке

## 📋 Основные характеристики

### **Стандарты и совместимость**
- Основан на стандартах **OpenAPI** и **JSON Schema**
- Автоматически генерирует документацию для вашего API
- Совместим со стандартами **OAuth 2.0** и **JWT**

### **Производительность**
- Поддерживает **асинхронное программирование** из коробки
- Позволяет обрабатывать множество запросов одновременно
- Имеет отличную производительность, сравнимую с **Node.js** и **Go**

## 💡 Технические особенности

### **Типизация и валидация**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

- Использует **аннотации типов Python** для валидации данных
- Код становится более **читаемым и надежным**
- Обеспечивает **автоматическую сериализацию** данных в JSON

### **Архитектура**
- Построен на основе **Starlette** и **Pydantic**
- Поддерживает интерактивную документацию **Swagger UI**
- Доступна альтернативная документация в **ReDoc**

## 🛠 Практическое применение

### **Интеграция**
- Легко интегрируется с базами данных через **ORM**
- Идеально подходит для создания **микросервисов**
- Значительно ускоряет процесс разработки API

### **Сообщество и поддержка**

### Первое приложение FastAPI

**Файл: hello.py**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi")
def greet():
    return "Hello? World?"
```

### Ключевые элементы:

- **`app`** — объект FastAPI верхнего уровня, представляющий веб-приложение

- **`@app.get("/hi")`** — декоратор пути.  Он сообщает FastAPI следующее:
  - Запрос к URL `/hi` на этом сервере должен быть направлен на следующую функцию;
  - Применяется только к HTTP-глаголу GET
  - Можно создать отдельные функции для других глаголов (PUT, POST, DELETE)
- **`def greet()`** — функция пути, основная точка контакта с HTTP-запросами

### Запуск приложения

**Способ 1: Через командную строку**
```bash
uvicorn hello:app --reload

```

[] Выполнено  ✅ не получилось ❌

**Способ 2: Внутри приложения**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi")
def greet():
    return "Hello? World?"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
```

В любом случае параметр reload указывает Uvicorn перезапустить веб-сервер, если содержимое файла main.py изменится.
По умолчанию будет задействоваться порт 8000 вашей машины localhost.

[] Выполнено  ✅ не получилось ❌

**Параметры:**
- `main:app` — файл `main.py`, переменная `app`
- `--reload` — автоматическая перезагрузка при изменении файла
- По умолчанию: `localhost:8000`

## 3. Тестирование API

### Способ 1: Браузер
```
http://localhost:8000/hi
```

### Способ 2: Requests
```python
import requests

r = requests.get("http://localhost:8000/hi")
print(r.json())  # 'Hello? World?'
```

### Способ 3: HTTPX
```python
import httpx

r = httpx.get("http://localhost:8000/hi")
print(r.json())  # 'Hello? World?'
```

### Способ 4: HTTPie

```bash
uv add httpie 
```

```bash
# Полный вывод
http localhost:8000/hi
```

Результат

```
HTTP/1.1 200 OK
content-length: 15
content-type: application/json     
date: Mon, 27 Oct 2025 14:13:56 GMT
server: uvicorn

"Hello? World?"
```



[] Выполнено  ✅ не получилось ❌

```bash
# Только тело ответа
http -b localhost:8000/hi
# Полные данные (запрос + ответ)
http -v localhost:8000/hi
```

Опишите результат

```
GET /hi HTTP/1.1 - это HTTP-запрос, состоящий из трех частей (тип операции, uri и версия протокола HTTP/1.1)
Accept: */*  - это ...
Accept-Encoding: gzip, deflate  - это ...
Connection: keep-alive  - это ...
Host: localhost:8000
User-Agent: HTTPie/3.2.4



HTTP/1.1 200 OK - это ...
content-length: 15 - это ...
content-type: application/json - это ...
date: Mon, 27 Oct 2025 14:15:59 GMT
server: uvicorn

"Hello? World?"
```

[] Выполнено  ✅ не получилось ❌



## 4. Параметры в FastAPI

**Компоненты:**
- Глагол-оператор (GET) и путь (/hi)
- Параметры запроса (после `?`)
- HTTP-заголовки
- Тело запроса

**Определения FastAPI:**
- **Header** — HTTP-заголовки
- **Path** — URL-адрес
- **Query** — параметры запроса (после `?`)
- **Body** — тело HTTP-сообщения

# Cпособы передачи параметров:

* в пути URL;
* в качестве параметра запроса после символа ? в URL;
* в теле НТТР-сообщения;
* в НТТР-заголовке.


### 4.1. Параметры пути (Path)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi/{who}")
def greet(who):
    return f"Hello? {who}?"
```

**Тестирование:**
```bash
# HTTPie
http localhost:8000/hi/Mom
# Ответ: "Hello? Mom?"
```

Результат 

```sh
HTTP/1.1 200 OK
content-length: 13
content-type: application/json
date: Mon, 27 Oct 2025 14:21:54 GMT
server: uvicorn

"Hello? mom?"

```


[] Выполнено  ✅ не получилось ❌


### 4.2. Параметры запроса (Query)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi")
def greet(who: str = "World"):
    return f"Hello? {who}?"
```

**Тестирование:**
```bash
http localhost:8000/hi?who=Mom
```

Результат 

```sh
HTTP/1.1 200 OK
content-length: 13
content-type: application/json
date: Mon, 27 Oct 2025 14:25:33 GMT
server: uvicorn

"Hello? mom?"
```

Чем, по-вашему, отличается `http localhost:8000/hi?who=Mom` от `http localhost:8000/hi/Mom`
Когда применяются эти способы?

```
напишите ответ здесь ...

```

[] Выполнено  ✅ не получилось ❌


### 4.3. Тело запроса (Body)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Greeting(BaseModel):
    who: str

@app.post("/hi")
def greet(greeting: Greeting):
    return f"Hello? {greeting.who}?"
```

### 4.4. Заголовки (Header)

```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.get("/hi")
def greet(who: str = Header()):
    return f"Hello? {who}?"
```

**Тестирование:**
```bash
http -v localhost:8000/hi who:Mo

```

Результат 

```
напишите ответ здесь ...
```


Добавьте эндпоинт
```py
@app.post("/agent")
def get_agent(user_agent:str = Header()):
    return user_agent

```

**Протестируйте**
```bash
http -v localhost:8000/agent

```

Результат 

```
напишите ответ здесь ...
сделайте выводы
```
[] Выполнено  ✅ не получилось ❌

## 4.4. Параметры запроса (Query Parameters)

Параметры запроса — это строки `name=value` после символа `?` в URL-адресе, разделенные символами `&`.

**Файл: hello.py**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi")
def greet(who):
    return f"Hello? {who}?"
```

**Особенность:** Слово `who` отсутствует в URL декоратора, поэтому FastAPI предполагает, что это параметр запроса.

**Тестирование:**

```bash
# Браузер
localhost:8000/hi?who=Mom

# HTTPie (способ 1)
http -b localhost:8000/hi?who=Mom

# HTTPie (способ 2 - с параметрами)
http -b localhost:8000/hi who==Mom
```

[] Выполнено  ✅ не получилось ❌

```python
# Requests (способ 1)
import requests
r = requests.get("http://localhost:8000/hi?who=Mom")
print(r.json())  # 'Hello? Mom?'

# Requests (способ 2 - с параметрами)
import requests
params = {"who": "Mom"}
r = requests.get("http://localhost:8000/hi", params=params)
print(r.json())  # 'Hello? Mom?'
```

[] Выполнено  ✅ не получилось ❌

## 5. Тело запроса (Request Body)

### Идемпотентность GET-запросов

**Важно:** GET-запросы должны быть идемпотентными (один и тот же вопрос — один и тот же ответ). GET должен только возвращать данные.

Тело запроса используется для:
- **POST** — создание данных
- **PUT** — полное обновление
- **PATCH** — частичное обновление

**Файл: hello.py**
```python
from fastapi import FastAPI, Body

app = FastAPI()

@app.post("/hi")
def greet(who: str = Body(embed=True)):
    return f"Hello? {who}?"
```

**Параметры:**
- `Body(embed=True)` — значение `who` берется из тела запроса в формате JSON
- `embed=True` — ответ должен быть `{"who": "Mom"}`, а не просто `"Mom"`

**Тестирование:**

```bash
# HTTPie (= для JSON body)
http -v localhost:8000/hi who=Mom
```
[] Выполнено  ✅ не получилось ❌

**Запрос:**
```
POST /hi HTTP/1.1
Content-Type: application/json

{
    "who": "Mom"
}
```

**Ответ:**
```
HTTP/1.1 200 OK
"Hello? Mom?"
```

[] Выполнено  ✅ не получилось ❌

```python
# Requests
import requests
data = {"who": "Mom"}
r = requests.post("http://localhost:8000/hi", json=data)
print(r.json())  # 'Hello? Mom?'
```
[] Выполнено  ✅ не получилось ❌

## 6. HTTP-заголовки (Headers)

**Файл: hello.py**
```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.post("/hi")
def greet(who: str = Header()):
    return f"Hello? {who}?"
```

**Тестирование:**

```bash
# HTTPie (: для заголовков)
http -v localhost:8000/hi who:Mom
```

**Запрос:**
```
GET /hi HTTP/1.1
who: Mom
```

**Ответ:**
```
HTTP/1.1 200 OK
"Hello? Mom?"
```

[] Выполнено  ✅ не получилось ❌

### Преобразование заголовков

FastAPI автоматически:
- Переводит ключи заголовков в нижний регистр
- Преобразует дефис (`-`) в нижнее подчеркивание (`_`)

**Пример с User-Agent:**

```python
from fastapi import FastAPI, Header

app = FastAPI()

@app.get("/agent")
def get_agent(user_agent: str = Header()):
    return user_agent
```

**Тестирование:**
```bash
http -v localhost:8000/agent
# Ответ: "HTTPie/3.2.1"
```

[] Выполнено  ✅ не получилось ❌

## 7. Комбинирование источников данных

В одной функции пути можно использовать несколько методов одновременно:
- URL-параметры (Path)
- Параметры запроса (Query)
- Тело запроса (Body)
- HTTP-заголовки (Header)
- Cookie-файлы

### Рекомендации по выбору метода:

| Метод | Когда использовать |
|-------|-------------------|
| **Path** | Идентификация ресурса (RESTful) |
| **Query** | Дополнительные аргументы (пагинация, фильтры) |
| **Body** | Большие объемы данных, модели |
| **Header** | Метаданные, аутентификация |

**Важно:** При использовании подсказок типов, аргументы автоматически проверяются библиотекой Pydantic.

[] Выполнено  ✅ не получилось ❌

## 8. Коды состояния HTTP

По умолчанию FastAPI возвращает код `200`. Можно указать другой код в декораторе:

```python
@app.get("/happy", status_code=200)
def happy():
    return ":)"
```

**Тестирование:**
```bash
http localhost:8000/happy
# HTTP/1.1 200 OK
# ":)"
```
[] Выполнено  ✅ не получилось ❌

## 9. Установка заголовков ответа

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/header/{name}/{value}")
def header(name: str, value: str, response: Response):
    response.headers[name] = value
    return "normal body"
```

**Тестирование:**
```bash
http localhost:8000/header/marco/polo
```

**Ответ:**
```
# HTTP-ответы в FastAPI

## Пример HTTP-ответа

```http
HTTP/1.1 200 OK
marco: polo

"normal body"
```
[] Выполнено  ✅ не получилось ❌

## 📋 Типы ответов

Импортируйте эти классы из модуля `fastapi.responses`:

### 🔹 Основные типы ответов
- **`JSONResponse`** (используется по умолчанию)
- **`HTMLResponse`**
- **`PlainTextResponse`**
- **`RedirectResponse`**
- **`FileResponse`**
- **`StreamingResponse`**

> **Примечание:** `FileResponse` и `StreamingResponse` подробно рассматрим позже 

## 🛠 Универсальный класс Response

Для других форматов вывода (MIME-типов или медиатипов) используйте общий класс **`Response`**:

### 📝 Параметры класса Response:

| Параметр | Тип | Описание |
|----------|-----|----------|
| **`content`** | `str` или `bytes` | Содержимое ответа |
| **`media_type`** | `str` | Строка MIME-типа |
| **`status_code`** | `int` | Целочисленный код состояния HTTP |
| **`headers`** | `dict` | Словарь строковых заголовков |

### 💻 Пример использования:

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/custom")
async def custom_response():
    return Response(
        content="Custom content",
        media_type="text/plain",
        status_code=200,
        headers={"Custom-Header": "value"}
    )
```

[] Выполнено  ✅ не получилось ❌

## 13. Типы ответов (Response Types)

FastAPI поддерживает различные типы ответов (импорт из `fastapi.responses`):

| Тип | Описание |
|-----|----------|
| `JSONResponse` | По умолчанию, JSON-данные |
| `HTMLResponse` | HTML-страницы |
| `PlainTextResponse` | Простой текст |
| `RedirectResponse` | Перенаправление |
| `FileResponse` | Отправка файлов |
| `StreamingResponse` | Потоковая передача данных |

### Пользовательский Response

Для других форматов используйте класс `Response`:

```python
from fastapi import Response

@app.get("/custom")
def custom():
    return Response(
        content="Custom content",
        media_type="text/plain",
        status_code=200,
        headers={"X-Custom": "Header"}
    )
```

**Параметры:**
- `content` — строка или байты
- `media_type` — строка MIME-типа
- `status_code` — целочисленный код состояния HTTP
- `headers` — словарь строк

[] Выполнено  ✅ не получилось ❌


### Самостоятельные задания:

## Задание 1: Приветствие пользователя

Создайте эндпоинт, который приветствует пользователя, используя данные из разных источников.

**Используйте:**
- **Path**: имя пользователя
- **Query**: язык приветствия (ru, en)
- **Body**: возраст пользователя
- **Header**: город пользователя

**Как тестировать:**

```bash
# HTTPie
http POST localhost:8000/greet/Ivan lang==ru age:=25 city:Moscow

# Ожидаемый ответ:
{
    "greeting": "Привет, Ivan!",
    "age": 25,
    "city": "Moscow",
    "language": "ru"
}
```

## Решение 

```py
from fastapi import FastAPI, Path, Query, Body, Header

app = FastAPI()

@app.post("/.../{...}")
def greet_user(
    name: ...,
    lang: ...,
    age: ...,
    city: ...
):
    ...

```

**Как тестировать:**

```bash
# HTTPie - сложение
http POST localhost:8000/calc/add num1==10.5 num2:=5.3 precision:3

# HTTPie - умножение
http POST localhost:8000/calc/multiply num1==7 num2:=8 precision:0

# Ожидаемый ответ:
{
    "operation": "multiply",
    "num1": 7.0,
    "num2": 8.0,
    "result": 56.0,
    "precision": 0
}
```
[] Выполнено  ✅ не получилось ❌

## Задание 2: Калькулятор с настройками

Создайте эндпоинт-калькулятор, который выполняет операции с числами.

**Используйте:**
- **Path**: операция (add, subtract, multiply, divide)
- **Query**: первое число
- **Body**: второе число
- **Header**: количество знаков после запятой


## Решение 

```py
@app.post("/.../{...}")
def calculate(
    ...
    
    return {
        ...
    }
```

[] Выполнено  ✅ не получилось ❌

Выводы по занятию:


```
На данном занятия мы изучили ...
Что нового узнал(а)
Что было трудно для понимания ....

```


## Заключение

В этом занятии мы рассмотрели:
- Установку и настройку uv
- Создание первого приложения FastAPI
- Различные способы тестирования API
- Работу с параметрами (Path, Query, Body, Header)
- Структуру HTTP-запросов
- Коды состояния и заголовки
- Типы ответов

**Следующие шаги:**
- Изучение моделей Pydantic
- Работа с базами данных
- Аутентификация и авторизация
- Тестирование приложений


{кнопка сохранить в pdf}