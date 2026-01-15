# Лабораторная работа "Проектирование RESTful API"

## Описание

В этой лабораторной работе вы создадите RESTful API для управления студентами и курсами.

**Предметная область:**
- **Student** (Студент) - информация о студентах
- **Course** (Курс) - информация о курсах

## Теория

Проектирование RESTful включает в себя следующие основные компоненты:

- **Ресурсы** - элементы данных, которыми управляет ваше приложение
- **Идентификаторы** - уникальные идентификаторы ресурсов
- **URL-адреса** - структурированные строки ресурсов и идентификаторов
- **Глагольные операторы** или действия:
  - **GET** - получение ресурса
  - **POST** - создание нового ресурса
  - **PUT** - полная замена ресурса
  - **PATCH** - частичная замена ресурса
  - **DELETE** - удаление ресурса

### Шаблоны RESTful

Общие правила RESTful, касающиеся сочетания глаголов и URL-адресов:

- `verb/resource/` - применение глагольного оператора ко всем ресурсам типа resource
- `verb/resource/id` - применение глагольного оператора к ресурсу с идентификатором id

### Параметры запросов

Параметры для сортировки, пагинации и других функций могут передаваться:
- Как параметры пути (после `/`)
- Как параметры запроса (`var=val` после `?`)
- В теле HTTP (для больших запросов)

---

## Структура проекта

### Макет каталогов

Создайте каталог `fastapi` со следующей структурой:

```
fastapi/
├── src/
│   ├── main.py
│   ├── web/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── course.py
│   ├── service/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── course.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── course.py
│   ├── model/
│   │   ├── __init__.py
│   │   ├── student.py
│   │   └── course.py
│   └── fake/
│       ├── __init__.py
│       ├── student.py
│       └── course.py
```

### Настройка PYTHONPATH

В Linux/macOS:
```bash
export PYTHONPATH=$PWD/src
```

---

## Примеры кода

### Пример 1. Основная программа main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def top():
    return "Главная страница"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
```

### Пример 2. Запуск основной программы

```bash
$ python main.py &
INFO: Will watch for changes in these directories: [.../fastapi']
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: Started reloader process [92543] using StatReload
INFO: Started server process [92551]
INFO: Waiting for application startup.
INFO: Application startup complete.
```

### Пример 3. Тестирование основной программы

```bash
$ http localhost:8000
HTTP/1.1 200 OK
content-length: 8
content-type: application/json
date: Sun, 05 Feb 2023 03:54:29 GMT
server: uvicorn

"Главная страница"
```

### Пример 4. Добавление конечной точки в main.py

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def top():
    return "Главная страница"

@app.get("/echo/{thing}")
def echo(thing):
    return f"Эхо: {thing}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
```

### Пример 5. Тестирование новой конечной точки

```bash
$ http -b localhost:8000/echo/argh
"Эхо: argh"
```

### Пример 6. Заголовки HTTP-запросов и ответов

```bash
$ http -p HBh http://example.com/

# ЗАПРОС (Request)
GET / HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: example.com
User-Agent: HTTPie/3.2.1

# ОТВЕТ (Response)
HTTP/1.1 200 OK
Age: 374045
Cache-Control: max-age=604800
Content-Type: text/html; charset=UTF-8
Date: Sat, 04 Feb 2023 01:00:21 GMT
Etag: "3147526947+gzip"
Expires: Sat, 11 Feb 2023 01:00:21 GMT
Last-Modified: Thu, 17 Oct 2019 07:18:26 GMT
Server: ECS (cha/80E2)
Vary: Accept-Encoding
X-Cache: HIT
```

### Пример 7. Использование APIRouter в файле web/student.py

```python
from fastapi import APIRouter

router = APIRouter(prefix="/student")

@router.get("/")
def top():
    return "Корневой эндпоинт студентов"
```

### Пример 8. Подключение основного приложения к субмаршруту

```python
from fastapi import FastAPI
from web import student

app = FastAPI()

app.include_router(student.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)
```

### Пример 9. Тестирование нового субмаршрута

```bash
$ http -b localhost:8000/student/
"Корневой эндпоинт студентов"
```

---

## Определение моделей данных

### Пример 10. Определение модели в файле model/student.py

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    group: str
    specialty: str
    year: int
```

### Пример 11. Определение модели в файле model/course.py

```python
from pydantic import BaseModel

class Course(BaseModel):
    name: str
    credits: int
    semester: int
    description: str
    instructor: str
```

---

## Создание фиктивных данных

### Пример 12. Новый модуль в файле fake/student.py

```python
from model.student import Student

# фиктивные данные
_students = [
    Student(
        name="Иван Иванов",
        group="ИСТ-401", 
        specialty="Информационные системы",
        year=4
    ),
    Student(
        name="Мария Петрова",
        group="ИСТ-402",
        specialty="Информационные технологии",
        year=4
    ),
]

def get_all() -> list[Student]:
    """Возврат всех студентов"""
    return _students

def get_one(name: str) -> Student | None:
    """Получить одного студента по имени"""
    for _student in _students:
        if _student.name == name:
            return _student
    return None

def create(student: Student) -> Student:
    """Добавление студента"""
    return student

def modify(student: Student) -> Student:
    """Частичное изменение записи студента"""
    return student

def replace(student: Student) -> Student:
    """Полная замена записи студента"""
    return student

def delete(name: str) -> bool:
    """Удаление записи студента"""
    return None
```

### Пример 13. Новый модуль в файле fake/course.py

```python
from model.course import Course

# фиктивные данные
_courses = [
    Course(
        name="Разработка высоконагруженных систем",
        credits=6,
        semester=7, 
        description="Проектирование и разработка масштабируемых систем",
        instructor="Иванов И.И."
    ),
    Course(
        name="Продвинутая веб-разработка",
        credits=5,
        semester=7,
        description="Современные фреймворки и технологии веб-разработки",
        instructor="Петров П.П."
    ),
]

def get_all() -> list[Course]:
    """Возврат всех курсов"""
    return _courses

def get_one(name: str) -> Course | None:
    """Возврат одного курса"""
    for _course in _courses:
        if _course.name == name:
            return _course
    return None

def create(course: Course) -> Course:
    """Добавление курса"""
    return course

def modify(course: Course) -> Course:
    """Частичное изменение записи курса"""
    return course

def replace(course: Course) -> Course:
    """Полная замена записи курса"""
    return course

def delete(name: str) -> bool:
    """Удаление записи курса"""
    return None
```

---

## Создание веб-уровня

### Пример 14. Новые конечные точки в файле web/student.py

```python
from fastapi import APIRouter
from model.student import Student
import fake.student as service

router = APIRouter(prefix="/student")

@router.get("/")
def get_all() -> list[Student]:
    return service.get_all()

@router.get("/{name}")
def get_one(name) -> Student | None:
    return service.get_one(name)

@router.post("/")
def create(student: Student) -> Student:
    return service.create(student)

@router.patch("/")
def modify(student: Student) -> Student:
    return service.modify(student)

@router.put("/")
def replace(student: Student) -> Student:
    return service.replace(student)

@router.delete("/{name}")
def delete(name: str):
    return None
```

### Пример 15. Новые конечные точки в файле web/course.py

```python
from fastapi import APIRouter
from model.course import Course
import fake.course as service

router = APIRouter(prefix="/course")

@router.get("/")
def get_all() -> list[Course]:
    return service.get_all()

@router.get("/{name}")
def get_one(name) -> Course:
    return service.get_one(name)

@router.post("/")
def create(course: Course) -> Course:
    return service.create(course)

@router.patch("/")
def modify(course: Course) -> Course:
    return service.modify(course)

@router.put("/")
def replace(course: Course) -> Course:
    return service.replace(course)

@router.delete("/{name}")
def delete(name: str):
    return service.delete(name)
```

### Пример 16. Добавление субмаршрутов в файл main.py

```python
import uvicorn
from fastapi import FastAPI
from web import student, course

app = FastAPI()

app.include_router(student.router)
app.include_router(course.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
```

---

## Тестирование

### Пример 17. Тестирование конечной точки Get All

```bash
$ http -b localhost:8000/student/
[
    {
        "name": "Иван Иванов",
        "group": "ИСТ-401",
        "specialty": "Информационные системы",
        "year": 4
    },
    {
        "name": "Мария Петрова",
        "group": "ИСТ-402",
        "specialty": "Информационные технологии",
        "year": 4
    }
]
```

### Пример 18. Тестирование конечной точки Get One

```bash
$ http -b localhost:8000/student/"Иван Иванов"
{
    "name": "Иван Иванов",
    "group": "ИСТ-401",
    "specialty": "Информационные системы",
    "year": 4
}
```

### Пример 19. Тестирование конечной точки Replace

```bash
$ http -b PUT localhost:8000/student/ name="Иван Иванов" group="ИСТ-401" specialty="Информационные системы" year=4
{
    "name": "Иван Иванов",
    "group": "ИСТ-401",
    "specialty": "Информационные системы",
    "year": 4
}
```

### Пример 20. Тестирование конечной точки Modify

```bash
$ http -b PATCH localhost:8000/student/ name="Иван Иванов" year=5
{
    "name": "Иван Иванов",
    "group": "ИСТ-401",
    "specialty": "Информационные системы",
    "year": 5
}
```

### Пример 21. Тестирование конечной точки Delete

```bash
$ http -b DELETE localhost:8000/student/Иван%20Иванов
true

$ http -b DELETE localhost:8000/student/Петр%20Сидоров
false
```

---

## Источники данных в HTTP-запросах

FastAPI позволяет получать данные из разных частей HTTP-сообщения:

- **Header** - в HTTP-заголовке
- **Path** - в пути URL
- **Query** - после символа `?` в URL (параметры запроса)
- **Body** - в теле HTTP-сообщения

Другие источники:
- Переменные окружения
- Настройки конфигурации




## Использование форм автоматизированного тестирования FastAPI

Помимо выполняемых вручную тестов, FastAPI предоставляет автоматизированные формы тестирования в конечных точках `/docs` и `/redoc`. Это два разных стиля для одних и тех же сведений.

FastAPI автоматически генерирует интерактивную документацию Swagger UI по адресу `/docs`, где можно:

1. **Нажать стрелку вниз** под разделом GET `/student/` - откроется форма для тестирования
2. **Нажать синюю кнопку "Execute"** для выполнения запроса
3. **Просмотреть результаты** - код ответа, заголовки и тело ответа в формате JSON

### Пример ответа для студентов

В разделе Response body выводится текст в формате JSON, возвращаемый для фиктивных данных студентов:

```json
[
    {
        "name": "Иван Иванов",
        "group": "ИСТ-401",
        "specialty": "Информационные системы",
        "year": 4
    },
    {
        "name": "Мария Петрова",
        "group": "ИСТ-402",
        "specialty": "Информационные технологии",
        "year": 4
    }
]
```

### Пример ответа для курсов

```json
[
    {
        "name": "Разработка высоконагруженных систем",
        "credits": 6,
        "semester": 7,
        "description": "Проектирование и разработка масштабируемых систем",
        "instructor": "Иванов И.И."
    },
    {
        "name": "Продвинутая веб-разработка",
        "credits": 5,
        "semester": 7,
        "description": "Современные фреймворки и технологии веб-разработки",
        "instructor": "Петров П.П."
    }
]
```

## Общение с уровнями сервисов и данных

Когда функциям на веб-уровне нужны данные, находящиеся под управлением уровня данных, она должна попросить уровень сервисов стать посредником. Это требует больше кода, но это хорошая практика:

### Преимущества трехуровневой архитектуры

- **Безопасность**: Веб-уровень работает с Интернетом, а уровень данных - с внешними хранилищами
- **Тестируемость**: Уровни можно тестировать независимо друг от друга
- **Изоляция**: Сервисный уровень определяет бизнес-логику и скрывает детали реализации от других уровней

### Пример взаимодействия уровней

```python
# web/student.py
from model.student import Student
import service.student as service

@router.get("/")
def get_all() -> list[Student]:
    return service.get_all()  # Веб → Сервис

# service/student.py
import data.student as data

def get_all() -> list[Student]:
    return data.get_all()  # Сервис → Данные

# data/student.py
def get_all() -> list[Student]:
    # Работа с БД
    return _students
```

## Пагинация и сортировка

В веб-интерфейсах часто требуется:
- **Сортировка** - упорядочение результатов
- **Пагинация** - возвращение части результатов за раз

### Примеры параметров запроса для студентов

```bash
# Сортировка по группе
GET /student?sort=group

# Пагинация (позиции 10-19)
GET /student?offset=10&size=10

# Комбинированный запрос
GET /student?sort=group&offset=10&size=10
```

### Примеры параметров запроса для курсов

```bash
# Сортировка по семестру
GET /course?sort=semester

# Фильтрация по семестру
GET /course?semester=7

# Поиск по названию
GET /course?name=веб
```

### Реализация пагинации

```python
from fastapi import Query

@router.get("/")
def get_all(
    offset: int = Query(0, ge=0),
    size: int = Query(10, ge=1, le=100)
) -> list[Student]:
    return service.get_all(offset=offset, size=size)
```



## Задания для самостоятельной работы

1. **Добавьте фильтрацию студентов по курсу обучения**
   ```python
   GET /student?year=4
   ```

2. **Реализуйте поиск курсов по преподавателю**
   ```python
   GET /course?instructor=Иванов
   ```

3. **Добавьте сортировку студентов по имени**
   ```python
   GET /student?sort=name&order=asc
   ```

4. **Реализуйте подсчет количества студентов в группе**
   ```python
   GET /student/count?group=ИСТ-401
   ```

5. **Добавьте валидацию для года обучения (1-6)**
   ```python
   from pydantic import Field
   
   class Student(BaseModel):
       year: int = Field(ge=1, le=6)
   ```

## Заключение

В этой лабораторной работе вы изучили:

1. **Автоматическое тестирование** через Swagger UI (`/docs`)
2. **Трехуровневую архитектуру** (web → service → data)
3. **Пагинацию и сортировку** для работы с большими объемами данных
4. **Фильтрацию данных** через параметры запроса

На веб-уровне определяются конечные точки с помощью декораторов путей FastAPI, которые:

- Автоматически проверяют и подтверждают данные с помощью Pydantic
- Собирают данные запроса из различных частей HTTP-сообщения
- Передают аргументы соответствующим сервисным функциям

Это основа для построения масштабируемого и поддерживаемого веб-приложения с четким разделением ответственности между уровнями.



---

## Задания для самостоятельной работы

1. Добавьте валидацию для полей моделей (например, year должен быть от 1 до 6)
2. Реализуйте поиск студентов по группе
3. Добавьте эндпоинт для получения всех курсов определенного семестра
4. Реализуйте связь многие-ко-многим между студентами и курсами
5. Добавьте пагинацию для списка студентов

## Выводы

В этой лабораторной работе вы:
1. Создали структуру RESTful API с использованием FastAPI
2. Определили модели данных Student и Course с помощью Pydantic
3. Реализовали CRUD операции для обеих сущностей
4. Использовали маршрутизаторы для организации кода
5. Протестировали API с помощью HTTPie
6. Познакомились с трехуровневой архитектурой (web, service, data)
