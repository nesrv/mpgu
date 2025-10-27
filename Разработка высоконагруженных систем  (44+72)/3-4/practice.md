# Методичка: Изучение высоконагруженных систем и API с FastAPI

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
- **`@app.get("/hi")`** — декоратор пути:
  - Запрос к URL `/hi` направляется на следующую функцию
  - Применяется только к HTTP-глаголу GET
  - Можно создать отдельные функции для других глаголов (PUT, POST, DELETE)
- **`def greet()`** — функция пути, основная точка контакта с HTTP-запросами

### Запуск приложения

**Способ 1: Через командную строку**
```bash
uvicorn main:app --reload

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

[] Выполнено  ✅ не получилось ❌

**Параметры:**
- `main:app` — файл `hello.py`, переменная `app`
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
```


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
# Ответ: "Hello? Mom?"
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

Чем по вашему отличается `http localhost:8000/hi?who=Mom` от `http localhost:8000/hi/Mom`
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

## 5. HTTP-запрос и его части

### Структура HTTP-запроса:

```
GET /hi HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/3.2.1
```

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

## 6. Автоматическая документация

FastAPI автоматически генерирует интерактивную документацию:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`




## 7. Параметры запроса (Query Parameters)

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


## 8. Тело запроса (Request Body)

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

```python
# Requests
import requests
data = {"who": "Mom"}
r = requests.post("http://localhost:8000/hi", json=data)
print(r.json())  # 'Hello? Mom?'
```

## 9. HTTP-заголовки (Headers)

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
## 10. Комбинирование источников данных

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


## 11. Коды состояния HTTP

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

## 12. Установка заголовков ответа

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
HTTP/1.1 200 OK
marco: polo

"normal body"
```
Типы ответов
Типы ответов (импортируйте эти классы из модуля fastapi. responses) бывают
следующие:
• JSONResponse (по умолчанию);
• HTMLResponse;

• PlainTextResponse;
• RedirectResponse;
• FileResponse;
• StreamingResponse.
О двух последних я расскажу подробнее в главе 15.
Для других форматов вывода, известных также как MIME-munъt или медиатuпъt,
можно использовать общий класс Response, требующий следующие сущности:
• content - строка или байт;
• media_type - строка МIМЕ-типа;
• status_code - целочисленный код состояния НТТР;
• headers - словарь (dict) строк


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

## Заключение

В этой методичке мы рассмотрели:
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
