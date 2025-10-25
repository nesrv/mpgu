# Методичка для самостоятельго изучения GraphQL
(продожительность 4 ак.часа)


## 🎯 Цели 
- ✅ Понять основные концепции GraphQL
- ✅ Научиться писать запросы и мутации
- ✅ Попрактиковаться на реальном API
- ✅ Создать простой GraphQL сервер на Python

---

## 📖 Часть 1: Основы

### Что такое GraphQL?
**GraphQL** - это язык запросов для API, который позволяет:
- Запрашивать только нужные данные
- Получать много данных за один запрос
- Иметь строго типизированную схему

### 🔄 Сравнение с REST
```python
# REST - много endpoints
# GET /users/1
# GET /users/1/posts  
# GET /users/1/friends

# GraphQL - один endpoint
"""
query {
  user(id: 1) {
    name
    posts { title }
    friends { name }
  }
}
"""
```

### 📚 Ключевые понятия

- **Query** - получение данных (как GET в REST)
- **Mutation** - изменение данных (как POST/PUT/DELETE)  
- **Schema** - описание всех возможных данных
- **Resolver** - функции Python, которые возвращают данные

---

## 🛠️ Часть 2: Синтаксис (25 минут)

### Базовый запрос
```graphql
# Получить пользователя и его посты
query {
  user(id: "1") {
    name
    email
    posts {
      title
      createdAt
    }
  }
}
```

### Запрос с аргументами

```graphql
query GetUserPosts($userId: ID!, $limit: Int) {
  user(id: $userId) {
    name
    posts(limit: $limit) {
      title
      content
    }
  }
}
```

### Переменные для запроса
```json
{
  "userId": "1",
  "limit": 5
}
```

### Мутации (изменение данных)

```graphql
mutation CreatePost {
  createPost(input: {
    title: "Мой первый пост"
    content: "Hello GraphQL!"
    authorId: "1"
  }) {
    id
    title
    createdAt
  }
}
```

---

## 🎮 Часть 3: Практика с реальным API (30 минут)

### SpaceX API - отличный для обучения

**Открой в браузере:** https://studio.apollographql.com/sandbox/explorer

### Задание 1: Получить информацию о миссиях
```graphql
query GetLaunches {
  launches(limit: 3) {
    mission_name
    launch_date_utc
    rocket {
      rocket_name
    }
    launch_success
  }
}
```

curl -X POST https://api.spacex.land/graphql/  -H "Content-Type: application/json"  -d '{"query":"query{launches(limit:1){mission_name}}"}'


### Задание 2: Детальная информация о ракете
```graphql
query GetRocketDetails {
  rockets(limit: 2) {
    id
    name
    description
    height {
      meters
    }
    mass {
      kg
    }
  }
}
```

### Практика с Python-клиентом
```python
import requests
import json

# Выполнение GraphQL запроса из Python
def run_graphql_query(query, variables=None):
    url = "https://spacex-production.up.railway.app/"
    response = requests.post(
        url,
        json={
            'query': query,
            'variables': variables or {}
        }
    )
    return response.json()

# Пример запроса
query = """
{
  launches(limit: 2) {
    mission_name
    launch_date_utc
  }
}
"""

result = run_graphql_query(query)
print(json.dumps(result, indent=2))
```

### 🎯 Практические упражнения:
1. **Получи 5 последних запусков** с их датами и статусом
2. **Найди самую тяжелую ракету** в базе данных
3. **Создай Python-функцию** для выполнения запросов

---

## 💻 Часть 4: Создаем свой сервер на Python (30 минут)

### Быстрый старт с Strawberry (современная GraphQL библиотека)

**1. Установка зависимостей**
```bash
python -m venv graphql_env
source graphql_env/bin/activate  # Linux/Mac
# graphql_env\Scripts\activate  # Windows

pip install strawberry fastapi uvicorn
```

**2. Создаем server.py**
```python
import strawberry
from typing import List, Optional
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# 1. Определяем типы данных
@strawberry.type
class User:
    id: str
    name: str
    email: str
    age: Optional[int] = None

@strawberry.input
class UserInput:
    name: str
    email: str
    age: Optional[int] = None

# 2. Mock данные
users_db = [
    User(id="1", name="Анна", email="anna@example.com", age=25),
    User(id="2", name="Иван", email="ivan@example.com", age=30),
]

# 3. Определяем запросы и мутации
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Привет, GraphQL из Python!"
    
    @strawberry.field
    def users(self) -> List[User]:
        return users_db
    
    @strawberry.field
    def user(self, id: str) -> Optional[User]:
        return next((user for user in users_db if user.id == id), None)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: UserInput) -> User:
        new_user = User(
            id=str(len(users_db) + 1),
            name=input.name,
            email=input.email,
            age=input.age
        )
        users_db.append(new_user)
        return new_user
    
    @strawberry.mutation
    def update_user_age(self, id: str, age: int) -> Optional[User]:
        for user in users_db:
            if user.id == id:
                user.age = age
                return user
        return None

# 4. Создаем схему
schema = strawberry.Schema(query=Query, mutation=Mutation)

# 5. Настраиваем FastAPI приложение
app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**3. Запускаем сервер**
```bash
python server.py
```

**4. Тестируем в браузере**
Открой: http://localhost:8000/graphql

### Альтернатива: Ariadne (другая популярная библиотека)
```python
from ariadne import QueryType, MutationType, make_executable_schema
from ariadne.asgi import GraphQL
from graphql import graphql_sync
import json

type_defs = """
    type User {
        id: ID!
        name: String!
        email: String!
        age: Int
    }

    type Query {
        hello: String!
        users: [User!]!
    }
"""

query = QueryType()
mutation = MutationType()

@query.field("hello")
def resolve_hello(_, info):
    return "Hello from Ariadne!"

schema = make_executable_schema(type_defs, query, mutation)
app = GraphQL(schema, debug=True)
```

### 🎯 Практика с нашим сервером:

**Запрос 1: Получить всех пользователей**
```graphql
query {
  users {
    id
    name
    email
  }
}
```

**Запрос 2: Получить конкретного пользователя**
```graphql
query {
  user(id: "1") {
    name
    email
    age
  }
}
```

**Запрос 3: Создать нового пользователя**
```graphql
mutation {
  createUser(input: {
    name: "Мария", 
    email: "maria@test.com", 
    age: 28
  }) {
    id
    name
    email
  }
}
```

**Запрос 4: Обновить возраст пользователя**
```graphql
mutation {
  updateUserAge(id: "1", age: 26) {
    id
    name
    age
  }
}
```

---

## 📋 Часть 5: Итоги и что дальше (15 минут)

### ✅ Что мы узнали за 2 часа:
- **Основы GraphQL** и отличия от REST
- **Синтаксис запросов** и мутаций
- **Практику** на реальном SpaceX API
- **Создали свой сервер на Python** с пользователями

### 🎯 Ключевые преимущества GraphQL:
- ✅ **Точно получаешь что нужно** - нет over-fetching
- ✅ **Один запрос для сложных данных** - нет under-fetching  
- ✅ **Строгая типизация** - меньше ошибок
- ✅ **Интеграция с Python** - отличные библиотеки

### 📚 Python GraphQL библиотеки:
- **Strawberry** - современная, с типами Python
- **Graphene** - популярная, зрелая
- **Ariadne** - schema-first подход

### 🚀 Что изучать дальше:
1. **Базы данных** - подключение SQLAlchemy, Django ORM
2. **Аутентификация** - JWT в GraphQL
3. **Django Integration** - Graphene-Django
4. **FastAPI Integration** - как мы сделали сегодня
5. **Тестирование** - pytest для GraphQL

### 🔗 Полезные ресурсы:
- **Strawberry документация**: https://strawberry.rocks
- **Graphene документация**: https://docs.graphene-python.org
- **Практика**: https://studio.apollographql.com/sandbox

### 📝 Домашнее задание:
1. **Добавь тип "Post"** с полями id, title, content, authorId
2. **Создай мутацию** createPost для добавления постов
3. **Добавь запрос** posts который возвращает все посты
4. **Создай связь** между пользователями и их постами

---

## 💡 Советы для новичков в Python:
- **Начни с Strawberry** - она наиболее pythonic
- **Используй type hints** - это обязательно для Strawberry
- **Тестируй в GraphQL IDE** - http://localhost:8000/graphql
- **Экспериментируй с данными** - добавь больше полей и типов

```python
# Пример расширения с постами
@strawberry.type
class Post:
    id: str
    title: str
    content: str
    author_id: str

# Добавь это в свою схему!
```

**Ты освоил основы GraphQL в Python! 🎉 Теперь практикуйся и создавай крутые API!**
