## Слайд 2

**Starlette** - это легкий ASGI-фреймворк/инструментарий, он идеально подходит для создания асинхронных веб-сервисов на Python.

Большая часть веб-кода FastAPI основана на созданном Томом Кристи пакете Starlette (https://www.starlette.io). 

Его можно применять в качестве самостоятельного веб-фреймворка или как библиотеку для других фреймворков, например FastAPI. Как и любой другой веб-фреймворк, Starlette выполняет все обычные операции синтаксического анализа HTTP-запросов и генерации ответов.

Он аналогичен лежащему в основе Flask пакету Werkzeug (https://werkzeug.palletsprojects.com).

## Слайд 3

Самая важная его особенность заключается в поддержке современного асинхронного веб-стандарта Python - ASGI (https://asgi.readthedocs.io). 

До сих пор большинство веб-фреймворков Python, например Flask и Django, основывались на традиционном синхронном стандарте WSGI (https://wsgi.readthedocs.io).

ASGI позволяет избежать характерных для приложений на базе WSGI блокировок и напряженного ожидания. Проблемы такого типа связаны с частым подключением веб-приложений к гораздо более медленному коду, например, для доступа к базам данных, файлам и сетям. 

В результате Starlette и использующие его фреймворки стали самыми быстрыми веб-пакетами Python и составили конкуренцию даже приложениям на Go и Node.js.

## Слайд 4

### Типы конкурентности

При **параллельных вычислениях** задача распределяется между несколькими выделенными центральными процессорами (ЦП). Этот метод часто используется в приложениях для выполнения расчетов, таких как задачи обработки графики и машинное обучение.

При **конкурентных вычислениях** каждый ЦП переключается между несколькими задачами. Некоторые задачи из потока занимают больше времени, и необходимо сократить общее время выполнения. 

Считывание файла или доступ к удаленному сетевому сервису буквально в тысячи и миллионы раз медленнее, чем выполнение вычислений в ЦП.

Веб-приложения выполняют большую часть этой медленной работы. Как заставить их или любые другие серверы работать быстрее?

## Слайд 5

### Распределенные и параллельные вычисления

## Слайд 6

### Сравнение синхронного и асинхронного кода

**Синхронный код:**

```py
import time

def q():
    print("Why can't programmers tell jokes?")
    time.sleep(3)

def a():
    print("Timing!")

def main():
    q()
    a()

main()
```

Вывод:
```
Why can't programmers tell jokes?
Timing!
```

Между вопросом и ответом будет трехсекундный промежуток. Скукота.

**Асинхронный код:**

```py
import asyncio

async def q():
    print("Why can't programmers tell jokes?")
    await asyncio.sleep(3)

async def a():
    print("Timing!")

async def main():
    await asyncio.gather(q(), a())

asyncio.run(main())
```

## Слайд 7

### Асинхронный эндпоинт

```py
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/hi")
async def greet():
    await asyncio.sleep(1)
    return "Hello? World?"
```

Запуск:
```bash
uvicorn greet_async:app
```

Или с uvicorn в коде:

```py
from fastapi import FastAPI
import asyncio
import uvicorn

app = FastAPI()

@app.get("/hi")
async def greet():
    await asyncio.sleep(1)
    return "Hello? World?"

if __name__ == "__main__":
    uvicorn.run("greet_async_uvicorn:app")
```

## Слайд 8

### Pydantic, подсказки типов и обзор моделей

Подсказки типа переменной могут включать только тип:
```
name: type
```

или также инициализировать переменную значением:
```
name: type = value
```

**Пример:**

```py
thing: str = "yeti"
physics_magic_number: float = 1.0/137.03599913
hp_lovecraft_noun: str = "ichor"
exploding_sheep: tuple = ("sis", "boom", "bah!")
responses: dict = {"Marco": "Polo", "answer": 42}
```

Можно также включать подтипы коллекций:

```py
name: dict[keytype, valtype] = {key1: val1, key2: val2}
```

## Слайд 9

При использовании Python до версии 3.9 необходимо импортировать прописные версии стандартных имен типов из модуля typing:

```py
from typing import Str
thing: Str = "yeti"
```

Модуль typing содержит полезные дополнения для подтипов. Наиболее распространенные из них следующие:
- **Any** - любой тип
- **Union** - любой из указанных типов, например `Union[str, int]`

## Слайд 10

Примеры определений Pydantic для словарей (dict) в Python включают следующее:

```py
from typing import Any
responses: dict[str, Any] = {"Marco": "Polo", "answer": 42}
```

Или, если быть более точными:

```py
from typing import Union
responses: dict[str, Union[str, int]] = {"Marco": "Polo", "answer": 42}
```

либо (в Python 3.10 и более поздних версиях):

```py
responses: dict[str, str | int] = {"Marco": "Polo", "answer": 42}
```

## Слайд 11

Обратите внимание на то, что в Python строка переменной с подсказкой типа является верной, а простая строка переменной - нет:

```py
>>> thing0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'thing0' is not defined

>>> thing0: str
>>> thing1: str = "yeti"
>>> thing1 = 47
```

Но такие ошибки будут обнаружены mypy.

Если у вас еще не установлен этот статический анализатор, наберите команду:
```bash
pip install mypy
```

Сохраните две предыдущие строки в файле `stuff.py`, а затем попробуйте выполнить следующие команды:

```bash
mypy stuff.py
```

## Слайд 12

В подсказке типа возврата функции вместо двоеточия применяется стрелка:

```
function(args) -> type:
```

Вот пример возврата функции при использовании Pydantic:

```py
def get_thing() -> str:
    return "yeti"
```

Можно задействовать любой тип, включая определенные классы или их комбинации.



## Слайд 13

Методы FastAPI
Одним из преимуществ FastAPI является то, что фреймворк позволяет быстро и легко построить веб-сервис в стиле REST. Архитектура REST предполагает применение следующих методов или типов запросов HTTP для взаимодействия с сервером, где каждый тип запроса отвечает за определенное действие:

GET (получение данных)

POST (добавление данных)

PUT (изменение данных)

DELETE (удаление данных)

Кроме этих типов запросов HTTP поддерживает еще ряд, в частности:

OPTIONS

HEAD

PATCH

TRACE

## Слайд 14

В классе FastAPI для каждого из этих типов запросов определены одноименные методы:

get() - получение данных (чтение)
post() - создание новых данных
put() - полное обновление данных (замена)
delete() - удаление данных
options() - получение информации о поддерживаемых методах (CORS)
head() - получение только заголовков ответа
patch() - частичное обновление данных
trace() - диагностика, возвращает полученные данные (редко используется)

Все эти методы имеют множество параметров, но все они в качестве обязательного параметра принимают путь, запрос по которому должен обрабатываться.

## Слайд 14

 методы сам запрос не обрабатывают - они применяются в качестве декоратора к функциям, которые непосредственно обрабатывают запрос. 
 Например:

 from fastapi import FastAPI
 
app = FastAPI()
 
@app.get("/")
def root():
    return {"message": "Hello Пушкин.COM"}

В данном случае метод app.get() применяется в качестве декоратора к функции root() (символ @ указывает на определение декоратора). Этот декоратор определяет путь, запросы по которому будет обрабатывать функция root(). 
В данном случае путь представляет строку "/", то есть функция будет обрабатывать запросы к корню веб-приложения (например, по адресу http://127.0.0.:8000/).

Функция возвращает некоторые результат. Обычно это словарь (объект dict). Здесь словарь содержит один элемент "message". При отправке эти данные автоматически сериализуются в формат JSON - популярный формат для взаимодействия между клиентом и сервером. А у ответа для заголовка content-type устанавливается значение application/json. Вообще функция может возвращать различные данные - словари (dict), списки (list), одиночные значения типа строк, чисел и т.д., которые затем сериализуются в json.


## Слайд 15

Подобным образом можно определять и другие функции, которые будут обрабатывать запросы по другим путям. Например:

from fastapi import FastAPI
 
app = FastAPI()
 
@app.get("/")
def root():
    return {"message": ""Hello Пушкин.COM"}
 
@app.get("/about")
def about():
    return {"message": "О сайте"}

## Слайд 16
Response
Класс fastapi.Response является базовым для остальных классов ответа. Его преимуществом является то, что он позволяется также отправить ответ, который не покрывается встроенными классами, например, в каком-то нестандартном формате. Для отпределения ответа конструктор класса принимает следующие параметры:

content: задает отправляемое содержимое

status_code: задает статусный код ответа

media_type: задает MIME-тип ответа

headers: задает заголовки ответа

from fastapi import FastAPI, Response
 
app = FastAPI()
 
 
@app.get("/")
def root():
    data = "Hello METANIT.COM"
    return Response(content=data, media_type="text/plain")

В данном случае клиенту отправляет обычная строка "Hello METANIT.COM". А MIME-тип "text/plain" указывает, что тип ответа - простой текст.

## Слайд 17

PlainTextResponse
Для отправки простого текста также можно использовать класс-наследник PlainTextResponse
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
 
app = FastAPI()
 
@app.get("/")
def root():
    data = "Hello METANIT.COM"
    return PlainTextResponse(content=data)

## Слайд 18
HTMLResponse
Для упрощения отправки кода html предназначен класс HTMLResponse. Он устанавливает для заголовока Content-Type значение text/html:
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
 
app = FastAPI()
 
@app.get("/")
def root():
    data = "<h2>Hello METANIT.COM</h2>"
    return HTMLResponse(content=data)

## Слайд 19

Установка типа ответа через методы FastAPI
Методы FastAPI такие как get(), post() и т.д. позволяют задать тип ответа с помощью параметра response_class:
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, JSONResponse, HTMLResponse
 
app = FastAPI()
 
@app.get("/text", response_class = PlainTextResponse)
def root_text():
    return "Hello METANIT.COM"
 
@app.get("/html", response_class = HTMLResponse)
def root_html():
    return "<h2>Hello METANIT.COM</h2>"


## Слайд 20


## Слайд 14

## Слайд 14