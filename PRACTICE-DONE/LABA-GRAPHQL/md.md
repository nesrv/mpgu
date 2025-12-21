Отличный выбор темы! GraphQL и FastAPI — мощная комбинация для создания гибких API. Вот развернутый сценарий практического занятия на 2-3 часа, рассчитанный на разработчиков, уже знакомых с FastAPI и основами REST.

**Тема:** "Создание эффективного GraphQL API с использованием FastAPI и Strawberry"

**Цель занятия:** Научить участников проектировать и реализовывать GraphQL API поверх существующих сервисов на FastAPI, понимать отличия от REST и решать типичные задачи.

**Целевая аудитория:** Разработчики Python (уровень: Junior+/Middle), знакомые с FastAPI, Pydantic и SQLAlchemy/Tortoise-ORM.

**Длительность:** 2-2.5 часа.

---

### **Структура занятия**

#### **Часть 1: Теоретический ввод (20 минут)**
**Формат:** Презентация + живое обсуждение.

**Ключевые моменты:**
1.  **Проблемы REST:** N+1 запрос, over-fetching, under-fetching, множество эндпоинтов.
2.  **Идея GraphQL:** Единственная точка входа, язык запросов, клиент определяет структуру ответа.
3.  **Основные концепции:**
    *   Схема (Schema): Типы (Object Type, Scalar), `Query`, `Mutation`, `Subscription`.
    *   Резолверы (Resolvers): Функции, которые возвращают данные.
    *   Интроспекция и Playground.
4.  **Почему Strawberry?** Код-первый (code-first) подход, типобезопасность, отличная интеграция с Pydantic и современным Python (dataclasses, type hints).
5.  **Архитектура:** GraphQL как слой поверх бизнес-логики (сервисов) и моделей данных.

---

#### **Часть 2: Практическая работа (1 час 30 минут)**
**Задание:** Создать GraphQL API для мини-блога (Пользователи, Посты, Комментарии).

**Предварительные требования (выдаются участникам как готовый код или они пишут его быстро):**
*   FastAPI-приложение с SQLAlchemy/Tortoise ORM.
*   Модели: `User`, `Post`, `Comment`.
*   Несколько записей в БД (можно через фикстуры).

**Шаг 0: Настройка проекта (10 минут)**
```bash
# Установка зависимостей
pip install "fastapi[all]" strawberry-graphql "strawberry-graphql[fastapi]" sqlalchemy pydantic-settings
```

**Основной файл (`main.py`):**
```python
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter

# Импорт схемы (её мы создадим ниже)
from graphql_app.schema import schema

# Создаем GraphQL роутер
graphql_app = GraphQLRouter(schema)

# Создаем приложение FastAPI
app = FastAPI(title="Blog GraphQL API")

# Подключаем GraphQL эндпоинт
app.include_router(graphql_app, prefix="/graphql")

# Опционально: оставляем REST эндпоинт для сравнения
@app.get("/rest/posts")
async def get_posts():
    # ... обычная REST логика
    pass
```

**Шаг 1: Определение GraphQL-типов (20 минут)**
*Участники создают файл `graphql_app/schema.py`.*

**Задача:** Создать Strawberry-типы, соответствующие моделям БД.
**Объяснение:** Важно разделять модели БД (SQLAlchemy) и GraphQL-типы. GraphQL-типы определяют, что видят клиенты.

```python
import strawberry
from typing import List, Optional
from datetime import datetime

@strawberry.type
class UserType:
    id: strawberry.ID
    username: str
    email: str
    # Поле posts будет описано позднее (разрешение N+1)

@strawberry.type
class PostType:
    id: strawberry.ID
    title: str
    content: str
    created_at: datetime
    author: "UserType"  # Ссылка на другой тип
    comments: List["CommentType"]

@strawberry.type
class CommentType:
    id: strawberry.ID
    text: str
    author: UserType
    post: PostType
```

**Шаг 2: Создание Query (30 минут)**
**Задача:** Реализовать точку входа для чтения данных.
**Объяснение:** Пишем резолверы. Обсуждаем проблему N+1 и необходимость оптимизации (DataLoader).

```python
# В schema.py, продолжаем
from .services import get_all_posts, get_user_by_id, get_post_by_id  # Предполагаемые сервисы
import asyncio

# Ключевой момент 1: Объявляем Query-тип
@strawberry.type
class Query:
    # Резолвер для получения всех постов
    @strawberry.field
    async def posts(self) -> List[PostType]:
        # Используем бизнес-логику (сервисный слой)
        post_models = await get_all_posts()
        # Преобразуем модели БД в GraphQL-типы
        return [
            PostType(
                id=post.id,
                title=post.title,
                content=post.content,
                created_at=post.created_at,
                author=UserType(id=post.author.id, username=post.author.username, email=post.author.email),  # Проблема N+1!
                comments=[]  # Пока пропустим
            )
            for post in post_models
        ]

    # Резолвер для получения одного поста по ID
    @strawberry.field
    async def post(self, post_id: strawberry.ID) -> Optional[PostType]:
        post_model = await get_post_by_id(post_id)
        if not post_model:
            return None
        return PostType(...)  # Аналогичное преобразование

    # Резолвер для получения пользователей (новый)
    @strawberry.field
    async def users(self) -> List[UserType]:
        user_models = await get_all_users()
        return [UserType(id=u.id, username=u.username, email=u.email) for u in user_models]
```

**Шаг 3: Создание Mutation (20 минут)**
**Задача:** Реализовать операции для изменения данных (создание поста).

```python
# В schema.py, после Query
@strawberry.input
class PostCreateInput:
    title: str
    content: str
    author_id: strawberry.ID

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_post(self, post_data: PostCreateInput) -> PostType:
        # Логика создания поста через сервис
        new_post_model = await create_new_post(
            title=post_data.title,
            content=post.data.content,
            author_id=post_data.author_id
        )
        # Возвращаем новый пост как GraphQL-объект
        return PostType(
            id=new_post_model.id,
            title=new_post_model.title,
            # ... и т.д.
        )
```

**Шаг 4: Сборка схемы и тестирование (10 минут)**
```python
# В конце schema.py
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

**Запуск и тестирование:**
1.  Запустите сервер: `uvicorn main:app --reload`
2.  Перейдите в Playground: `http://localhost:8000/graphql`
3.  **Упражнение 1:** Напишите запрос на получение всех постов с их названиями и именами авторов.
4.  **Упражнение 2:** Напишите запрос на получение одного поста с комментариями и именами авторов комментариев.
5.  **Упражнение 3:** Напишите мутацию для создания нового поста и верните его `id` и `title`.

---

#### **Часть 3: Решение продвинутых задач и обсуждение (30 минут)**

1.  **Проблема N+1 и DataLoader (15 минут):**
    *   **Демонстрация проблемы:** Покажите, как в текущем коде запрос на 10 постов генерирует 11 SQL-запросов (1 на посты + 10 на авторов).
    *   **Решение:** Внедрите `strawberry.dataloader`.
    *   **Задание:** Участники создают DataLoader для загрузки пользователей по списку ID и переписывают резолвер `author` в `PostType`.

2.  **Сравнение с REST (10 минут):**
    *   Попросите участников выполнить одинаковые задачи через REST (`/rest/posts`) и GraphQL.
    *   **Обсудите:**
        *   Объем передаваемых данных.
        *   Количество запросов.
        *   Гибкость и сложность на стороне клиента и сервера.

3.  **Резюме и лучшие практики (5 минут):**
    *   **Когда использовать GraphQL?** Сложные клиенты (мобильные приложения, SPA), публичные API для разных клиентов, объединение нескольких источников данных (Apollo Federation).
    *   **Когда осторожнее?** Простые CRUD-приложения, кэширование на уровне HTTP, файловая upload-загрузка (используйте REST рядом).
    *   **Безопасность:** Сложность запросов (Depth Limit, Query Cost Analysis), авторизация на уровне полей (можно в резолверах).
    *   **Документация и версионирование:** Схема само-документирована. Версионирование через добавление новых полей/типов, а не через URL.

---

### **Материалы для участников:**

1.  **Стартовый репозиторий** с настроенным FastAPI и моделями.
2.  **Шпаргалка по GraphQL-запросам:**
    ```graphql
    # Запрос (Query)
    query {
      posts {
        id
        title
        author {
          username
        }
      }
    }

    # Мутация (Mutation)
    mutation {
      createPost(postData: {title: "Новый пост", content: "Привет!", authorId: 1}) {
        id
        title
      }
    }
    ```
3.  **Ссылки для дальнейшего изучения:**
    *   Официальная документация Strawberry: [https://strawberry.rocks](https://strawberry.rocks)
    *   GraphQL Spec: [https://graphql.org](https://graphql.org)
    *   Как проектировать GraphQL API: [https://graphql.org/learn/thinking-in-graphs/](https://graphql.org/learn/thinking-in-graphs/)

### **Критерии успеха занятия:**
*   Участники самостоятельно пишут и выполняют GraphQL-запросы в Playground.
*   Понимают разницу между REST и GraphQL на практическом примере.
*   Осознают проблему N+1 и знают инструменты для её решения (DataLoader).
*   Могут добавить новое поле или мутацию в схему.

Такой сценарий обеспечивает баланс между теорией, практикой и решением реальных проблем, с которыми разработчики сталкиваются при внедрении GraphQL. Удачи в проведении занятия