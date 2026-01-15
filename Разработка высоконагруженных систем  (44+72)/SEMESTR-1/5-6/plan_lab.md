# Лабораторная работа: Проектирование API для информационной системы

**Цель:** Спроектировать и исследовать API для информационной системы. Изучить Pydantic.

---

## Справочные данные по Pydantic

### Базовые модели
```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None  # Необязательное поле

# Использование
user = User(
    id=1, 
    name="Anna", 
    email="anna@mail.ru"
)
print(user.name)  # "Anna"
```

### Валидация данных
```python
from pydantic import Field, field_validator

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: float = Field(gt=0)  # Больше 0
    quantity: int = Field(ge=0)  # Больше или равно 0
    
    @field_validator('name')
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError('Name cannot be empty')
        return value

# При ошибке валидации
try:
    product = Product(name="", price=-100, quantity=5)
except Exception as e:
    print(e)  # Увидим ошибки валидации
```

### Работа с JSON
```python
# Модель → JSON
user_json = user.model_dump_json()
print(user_json)  
# '{"id":1,"name":"Anna","email":"anna@mail.ru","age":null}'

# JSON → Модель
user_data = '{"id":2,"name":"Ivan","email":"ivan@test.ru"}'
user2 = User.model_validate_json(user_data)

# Конвертация в словарь
user_dict = user.model_dump()
```

### Работа с Headers в FastAPI
```python
from fastapi import Header

@app.get("/info")
def get_info(
    user_agent: str = Header(None, alias="User-Agent"),
    authorization: str = Header(None)
):
    return {
        "user_agent": user_agent,
        "auth": authorization
    }
```

---

## Исходные данные для лабораторной работы 

```python
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

```

---

## Выполнение

### Задание 1. Создание FastAPI сервера

Создайте файл `main.py` для запуска FastAPI-сервера и добавьте тестовый эндпоинт:

```python
from fastapi import FastAPI

app = FastAPI()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

```

Запустите сервер командой:
```bash
python main.py
```

### Задание 2. Определение моделей данных

Определите модели данных с использованием Pydantic:

```python
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    ...


class Course(BaseModel):
    name: str
    ...

```

### Задание 3. Эндпоинт для получения всех студентов

Добавьте эндпоинт для возврата всех студентов:

```python
@app.get("/student")
def get_all() -> ...:
    """Возврат всех студентов"""
    return _students

```

### Задание 4. CRUD операции для студентов

Добавьте следующие эндпоинты:

- **GET** `/student/{name}` - Получение одного студента по имени
- **POST** `/student` - Добавление студента
- **PATCH** `/student/{name}` - Частичное изменение записи студента
- **PUT** `/student/{name}` - Полная замена записи студента
- **DELETE** `/student/{name}` - Удаление записи студента

**Требования:**
- Протестируйте все эндпоинты через Swagger UI (http://localhost:8000/docs)
- Разделите приложение на слои (уровни):
  - `model.py` - модели данных (Pydantic)
  - `service.py` - бизнес-логика (CRUD операции)
  - `web.py` или `main.py` - веб-слой (эндпоинты FastAPI)

**Место для решения:**
```python
# Ваш код здесь
# model.py
...

# service.py
...

# main.py
...

```


### Задание 5. Тестовые данные

1. Создайте JSON-фикстуру на 10 студентов (`fixtures/students.json`)
2. Создайте эндпоинт для загрузки тестовых данных:
   ```python
   @app.post("/student/load-fixtures")
   def load_fixtures():       
       # Загрузка данных
       ...
       return {"loaded": len(data)}
   ```


---

## Задания для самостоятельной работы


1. **Фильтрация студентов по курсу обучения**
   
   **Что нужно сделать:**
   - Добавьте необязательный Query параметр year в эндпоинт GET /student
   - Если year указан - отфильтруйте список студентов по этому курсу
   - Если year не указан - верните всех студентов
   - Протестируйте: GET /student?year=4
   
   ```python
   @app.get("/student")
   def get_students(year: int | None = Query(None, ge=1, le=6)):
       ...
       return _students
   ```

2. **Поиск курсов по преподавателю**
   
   **Что нужно сделать:**
   - Создайте список _courses с тестовыми данными курсов
   - Добавьте Query параметр instructor в эндпоинт GET /course
   - Отфильтруйте курсы по имени преподавателя (используйте частичное совпадение)
   - Протестируйте: GET /course?instructor=Иванов
   
   ```python
   @app.get("/course")
   def get_courses(...):
       if instructor:
           return ...
       return _courses
   ```

3. **Сортировка студентов по имени**
   
   **Что нужно сделать:**
   - Добавьте Query параметры sort и order в эндпоинт GET /student
   - Параметр sort может быть: "name", "year", "group"
   - Параметр order может быть: "asc" или "desc"
   - Отсортируйте список студентов согласно параметрам
   - Протестируйте: GET /student?sort=name&order=asc
   
   ```python
   @app.get("/student")
   def get_students(
       sort: str | None = Query(None, pattern="^(name|year|group)$"),
       order: str = Query("asc", pattern="^(asc|desc)$")
   ):
       result = _students.copy()
       ...
       return result
   ```

4. **Подсчет количества студентов в группе**
   
   **Что нужно сделать:**
   - Создайте эндпоинт GET /student/count
   - Добавьте обязательный Query параметр group
   - Подсчитайте количество студентов в указанной группе
   - Верните JSON с полями: group, count
   - Протестируйте: GET /student/count?group=ИСТ-401
   
   ```python
   @app.get("/student/count")
   def count_students(group: str = Query(...)):
       ...
       return {"group": group, "count": count}
   ```



**Место для решения:**
textbox
```python
# Ваш код здесь


```


## Выводы


В этой лабораторной работе вы:

textbox
```
1. Создали структуру RESTful API с использованием FastAPI



```