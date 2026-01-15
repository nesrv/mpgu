# Инструкция по установке и работе с Apollo Studio GraphQL

## Что такое Apollo Studio?

Apollo Studio — это мощный инструмент для работы с GraphQL API, который предоставляет:
- **Интерактивный редактор запросов** (Explorer)
- **Автодополнение** и валидацию запросов
- **Просмотр схемы** (Schema Reference)
- **Историю запросов** и сохранение операций
- **Профилирование производительности** (для Apollo Server)
- **Отслеживание изменений схемы**

---

## Способ 1: Apollo Studio (веб-версия) — Рекомендуется

### Шаг 1: Регистрация

1. Перейдите на [https://studio.apollographql.com](https://studio.apollographql.com)
2. Нажмите **"Sign Up"** или **"Sign In"** (можно через GitHub, Google)
3. Создайте аккаунт (бесплатный план доступен)

### Шаг 2: Создание графа (Graph)

1. После входа нажмите **"Create a new graph"**
2. Выберите **"Create a graph manually"** (для локальной разработки)
3. Введите название графа (например, `Messenger Channel API`)
4. Выберите **"Development"** в качестве варианта использования
5. Нажмите **"Create graph"**

### Шаг 3: Подключение к локальному GraphQL API

#### Вариант A: Через URL (если API доступен из интернета)

1. В Apollo Studio перейдите в раздел **"Settings"** → **"Graph Settings"**
2. Найдите раздел **"Graph Endpoint"**
3. Введите URL вашего GraphQL endpoint (например, `https://your-api.com/graphql`)

#### Вариант B: Через Apollo Router (для локальной разработки)

Если ваш API работает только локально (`localhost:8000`), используйте один из способов:

**Способ 1: Apollo Studio Sandbox (без регистрации)**
- См. раздел "Способ 2" ниже

**Способ 2: Туннелирование (ngrok, Cloudflare Tunnel)**

1. Установите ngrok:
   ```bash
   # Windows (через Chocolatey)
   choco install ngrok
   
   # Или скачайте с https://ngrok.com/download
   ```

2. Запустите ваш GraphQL сервер:
   ```bash
   cd LABA-GRAPHQL
   uvicorn main:app --reload
   ```

3. В другом терминале создайте туннель:
   ```bash
   ngrok http 8000
   ```

4. Скопируйте HTTPS URL (например, `https://abc123.ngrok.io`)

5. В Apollo Studio добавьте endpoint: `https://abc123.ngrok.io/graphql`

**Способ 3: Прямое подключение (если Apollo Studio поддерживает)**

1. В Apollo Studio откройте **"Explorer"**
2. В настройках подключения введите: `http://localhost:8000/graphql`
3. Убедитесь, что ваш сервер разрешает CORS запросы (см. настройки ниже)

### Шаг 4: Настройка CORS (если нужно)

Если Apollo Studio не может подключиться к вашему API, добавьте CORS в `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from models_graphql import schema

app = FastAPI(
    title="Messenger Channel API",
    description="GraphQL API для информационного канала мессенджера",
    version="1.0.0",
)

# Настройка CORS для Apollo Studio
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://studio.apollographql.com",
        "https://*.apollographql.com",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql",
)

app.include_router(graphql_app, prefix="/graphql")
```

---

## Способ 2: Apollo Studio Sandbox (локальная версия)

Apollo Studio Sandbox — это локальная версия Apollo Studio, которая работает без регистрации и подключения к облаку.

### Установка и запуск

1. **Через npm (если установлен Node.js):**
   ```bash
   npx @apollo/sandbox
   ```

2. **Или установите глобально:**
   ```bash
   npm install -g @apollo/sandbox
   apollo-sandbox
   ```

3. **Откроется браузер** с интерфейсом Apollo Studio Sandbox

4. **Введите URL вашего GraphQL endpoint:**
   - `http://localhost:8000/graphql`

5. **Нажмите "Connect"** — схема загрузится автоматически

### Преимущества Sandbox:
- ✅ Работает полностью локально
- ✅ Не требует регистрации
- ✅ Не требует туннелирования
- ✅ Все функции Apollo Studio доступны

---

## Способ 3: Apollo CLI (для продвинутых пользователей)

### Установка Apollo CLI

```bash
# Через npm
npm install -g apollo

# Или через npx (без установки)
npx apollo --version
```

### Использование

1. **Войдите в Apollo Studio:**
   ```bash
   apollo login
   ```

2. **Отправьте схему в Apollo Studio:**
   ```bash
   # Если у вас есть файл схемы
   apollo schema:push --endpoint=http://localhost:8000/graphql
   ```

3. **Или используйте для валидации:**
   ```bash
   apollo schema:check --endpoint=http://localhost:8000/graphql
   ```

---

## Работа с Apollo Studio

### 1. Explorer (Интерактивный редактор запросов)

**Основные возможности:**
- Автодополнение полей и аргументов
- Валидация запросов в реальном времени
- Подсветка синтаксиса
- История запросов

**Пример запроса:**
```graphql
query GetUsers {
  users {
    id
    username
    email
    posts {
      id
      title
    }
  }
}
```

**Как использовать:**
1. Откройте вкладку **"Explorer"** в Apollo Studio
2. Начните вводить запрос — появится автодополнение
3. Выберите нужные поля из схемы
4. Нажмите **"Run"** или `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

### 2. Schema Reference (Справочник схемы)

**Что можно делать:**
- Просматривать все типы, поля и аргументы
- Видеть описания (если они добавлены в схему)
- Понимать связи между типами
- Копировать примеры запросов

**Как открыть:**
- В боковом меню выберите **"Schema"** или **"Schema Reference"**

### 3. History (История запросов)

- Все выполненные запросы сохраняются
- Можно вернуться к предыдущим запросам
- Можно сохранить запросы как **"Operations"**

### 4. Variables (Переменные)

Используйте переменные для параметризованных запросов:

```graphql
query GetUser($userId: ID!) {
  user(id: $userId) {
    id
    username
    email
  }
}
```

**В разделе Variables:**
```json
{
  "userId": "1"
}
```

### 5. Headers (Заголовки)

Добавьте заголовки для аутентификации или других целей:

```json
{
  "Authorization": "Bearer your-token-here"
}
```

---

## Примеры работы с вашим API

### Пример 1: Получить всех пользователей

```graphql
query GetAllUsers {
  users {
    id
    username
    email
    createdAt
  }
}
```

### Пример 2: Получить пользователя по ID

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    username
    email
    posts {
      id
      title
      content
    }
  }
}
```

**Variables:**
```json
{
  "id": "1"
}
```

### Пример 3: Создать нового пользователя (Mutation)

```graphql
mutation CreateUser($input: UserCreateInput!) {
  createUser(input: $input) {
    id
    username
    email
  }
}
```

**Variables:**
```json
{
  "input": {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword"
  }
}
```

### Пример 4: Вложенные запросы

```graphql
query GetPostsWithDetails {
  posts {
    id
    title
    content
    author {
      id
      username
    }
    comments {
      id
      text
      author {
        username
      }
    }
  }
}
```

---

## Сравнение с GraphiQL

| Функция | GraphiQL | Apollo Studio |
|---------|----------|---------------|
| Локальная работа | ✅ Да | ✅ Да (Sandbox) |
| Автодополнение | ✅ Базовое | ✅ Продвинутое |
| История запросов | ❌ Нет | ✅ Да |
| Сохранение операций | ❌ Нет | ✅ Да |
| Профилирование | ❌ Нет | ✅ Да (для Apollo Server) |
| Отслеживание схемы | ❌ Нет | ✅ Да |
| Требует регистрацию | ❌ Нет | ⚠️ Только для облачной версии |

---

## Рекомендации

### Для локальной разработки:
- Используйте **Apollo Studio Sandbox** — не требует регистрации и работает локально

### Для командной работы:
- Используйте **Apollo Studio (веб)** — можно делиться запросами и отслеживать изменения схемы

### Для быстрого тестирования:
- Используйте встроенный **GraphiQL** в вашем FastAPI приложении (`http://localhost:8000/graphql`)

---

## Решение проблем

### Проблема: "Cannot connect to endpoint"

**Решение:**
1. Убедитесь, что сервер запущен: `uvicorn main:app --reload`
2. Проверьте URL: должен быть `http://localhost:8000/graphql`
3. Проверьте CORS настройки (см. выше)
4. Для Apollo Studio (веб) используйте туннелирование (ngrok)

### Проблема: "Schema introspection failed"

**Решение:**
1. Убедитесь, что интроспекция включена в Strawberry (по умолчанию включена)
2. Проверьте, что endpoint доступен
3. Проверьте логи сервера на наличие ошибок

### Проблема: "CORS error"

**Решение:**
Добавьте CORS middleware в `main.py` (см. раздел "Настройка CORS" выше)

---

## Полезные ссылки

- [Apollo Studio](https://studio.apollographql.com)
- [Apollo Studio Sandbox](https://www.apollographql.com/docs/studio/explorer/explorer/)
- [Strawberry GraphQL Documentation](https://strawberry.rocks)
- [GraphQL Specification](https://graphql.org/learn/)

---

## Быстрый старт (TL;DR)

1. **Для локальной работы:**
   ```bash
   npx @apollo/sandbox
   # Введите: http://localhost:8000/graphql
   ```

2. **Для облачной версии:**
   - Зарегистрируйтесь на [studio.apollographql.com](https://studio.apollographql.com)
   - Создайте граф
   - Используйте ngrok для туннелирования или настройте CORS

3. **Запустите сервер:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Начните писать запросы в Apollo Studio!**

---

*Последнее обновление: 2024*

