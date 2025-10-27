# Практические задания: Комбинирование источников данных в FastAPI

## Задание 1: Приветствие пользователя

Создайте эндпоинт, который приветствует пользователя, используя данные из разных источников.

**Используйте:**
- **Path**: имя пользователя
- **Query**: язык приветствия (ru, en)
- **Body**: возраст пользователя
- **Header**: город пользователя

```python
from fastapi import FastAPI, Path, Query, Body, Header

app = FastAPI()

@app.post("/greet/{name}")
def greet_user(
    name: str = Path(...),
    lang: str = Query("ru"),
    age: int = Body(...),
    city: str = Header(...)
):
    if lang == "ru":
        greeting = f"Привет, {name}!"
    else:
        greeting = f"Hello, {name}!"
    
    return {
        "greeting": greeting,
        "age": age,
        "city": city,
        "language": lang
    }
```

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

```python
# Requests
import requests

response = requests.post(
    "http://localhost:8000/greet/Ivan",
    params={"lang": "ru"},
    json={"age": 25},
    headers={"city": "Moscow"}
)
print(response.json())
```

---

## Задание 2: Калькулятор с настройками

Создайте эндпоинт-калькулятор, который выполняет операции с числами.

**Используйте:**
- **Path**: операция (add, subtract, multiply, divide)
- **Query**: первое число
- **Body**: второе число
- **Header**: количество знаков после запятой

```python
@app.post("/calc/{operation}")
def calculate(
    operation: str = Path(...),
    num1: float = Query(...),
    num2: float = Body(...),
    precision: int = Header(2)
):
    if operation == "add":
        result = num1 + num2
    elif operation == "subtract":
        result = num1 - num2
    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        result = num1 / num2 if num2 != 0 else "Error: Division by zero"
    else:
        result = "Unknown operation"
    
    if isinstance(result, float):
        result = round(result, precision)
    
    return {
        "operation": operation,
        "num1": num1,
        "num2": num2,
        "result": result,
        "precision": precision
    }
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

```python
# Requests
import requests

response = requests.post(
    "http://localhost:8000/calc/divide",
    params={"num1": 10},
    json={"num2": 3},
    headers={"precision": "2"}
)
print(response.json())
# {"operation": "divide", "num1": 10.0, "num2": 3.0, "result": 3.33, "precision": 2}
```

---

## Проверка работы

1. Создайте файл `main.py` и скопируйте код обоих эндпоинтов
2. Запустите сервер: `uvicorn main:app --reload`
3. Протестируйте оба эндпоинта
4. Откройте документацию: `http://localhost:8000/docs`

## Что изучили

✅ **Path** - передача данных в URL  
✅ **Query** - параметры после `?`  
✅ **Body** - данные в теле запроса (JSON)  
✅ **Header** - данные в заголовках HTTP  
✅ Комбинирование всех источников в одной функции
