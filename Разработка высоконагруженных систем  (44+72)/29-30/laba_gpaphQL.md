# Лабораторная работа: Изучение GraphQL

## Цель работы:
Изучить основы GraphQL, создать API для системы мессенджера с поддержкой запросов, мутаций и работы с PostgreSQL. Освоить создание резолверов, типов данных и интеграцию с FastAPI.

## 1. Установка стенда

### 1.1 Docker Compose

```yaml
services:
  postgres:
    image: postgres:18
    container_name: postgres_graphql
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: messenger_channel
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql
      - ./sql.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 1.2 База данных (Информационный канал для мессенджера сообщений)

База данных представляет собой систему информационного канала мессенджера с тремя основными сущностями:
- **users** - пользователи системы с настройками профиля
- **messages** - сообщения канала с метаданными и статистикой
- **comments** - комментарии к сообщениям с поддержкой вложенности

[База данных](sql.sql)
[Скрипт](init_db.py)

┌─────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│     users       │
├─────────────────┤
│ PK id           │ INTEGER (GENERATED ALWAYS AS IDENTITY)
│ UQ username     │ VARCHAR(100) NOT NULL
│    profile      │ JSONB
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│    messages     │
├─────────────────┤
│ PK id           │ INTEGER (GENERATED ALWAYS AS IDENTITY)
│ FK author_id    │ INTEGER → users.id (ON DELETE CASCADE)
│    title        │ VARCHAR(200)
│    content      │ TEXT NOT NULL
│    metadata     │ JSONB
│    stats        │ JSONB
│    created_at   │ TIMESTAMP (DEFAULT CURRENT_TIMESTAMP)
│    updated_at   │ TIMESTAMP (DEFAULT CURRENT_TIMESTAMP)
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│    comments     │
├─────────────────┤
│ PK id           │ INTEGER (GENERATED ALWAYS AS IDENTITY)
│ FK message_id   │ INTEGER → messages.id (ON DELETE CASCADE)
│ FK author_id    │ INTEGER → users.id (ON DELETE CASCADE)
│ FK parent_comment_id│ INTEGER → comments.id (ON DELETE CASCADE)
│    content      │ TEXT NOT NULL
│    metadata     │ JSONB
│    reactions    │ JSONB
│    created_at   │ TIMESTAMP (DEFAULT CURRENT_TIMESTAMP)
│    updated_at   │ TIMESTAMP (DEFAULT CURRENT_TIMESTAMP)
└─────────────────┘


### 1.3 Установка зависимостей requirements.txt

```txt
fastapi[all]
strawberry-graphql[fastapi]
sqlalchemy[asyncio]
asyncpg
pydantic-settings
psycopg2-binary
uvicorn[standard]
```

### 1.4 Настройка виртуального окружения в WSL с помощью uv

**Важно:** Виртуальное окружение создается в Linux файловой системе (`~/.venv/`), а не в директории проекта, чтобы избежать проблем с правами доступа.

## Быстрый старт

```bash
wsl
# 1. Установка uv (если нужно)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# 2. Создание виртуального окружения
uv venv ~/.venv/laba-graphql

# 3. Активация и установка зависимостей
source ~/.venv/laba-graphql/bin/activate
cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL
uv pip install -r requirements.txt
```

## Ежедневная работа

```bash
# Активация окружения и переход в проект
cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL && source ~/.venv/laba-graphql/bin/activate
```

### Алиас для удобства

Добавьте в `~/.bashrc`:
```bash
alias activate-graphql='cd /mnt/c/W26/project/mpgu_practice/LABA-GRAPHQL && source ~/.venv/laba-graphql/bin/activate'
```

Затем: `source ~/.bashrc` и используйте `activate-graphql`

## Основные команды

```bash
# Активация
source ~/.venv/laba-graphql/bin/activate
# Деактивация
deactivate
# Установка пакета
uv pip install название-пакета
# Список пакетов
uv pip list
```

## 2. Развертывание FastAPI-GraphQL приложения

На этом этапе создаем базовую структуру GraphQL API с FastAPI. Настраиваем подключение к базе данных, создаем простейшую схему и проверяем работоспособность системы.

### 2.1 main.py

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from schema import schema

# Создаем GraphQL роутер
graphql_app = GraphQLRouter(schema)

# Создаем приложение FastAPI
app = FastAPI(title="Messenger Channel GraphQL API")

# Подключаем GraphQL эндпоинт
app.include_router(graphql_app, prefix="/graphql")

# Health check
@app.get("/")
async def root():
    return {"message": "GraphQL API доступен на /graphql"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.2 database.py

Файл содержит настройки подключения к PostgreSQL через SQLAlchemy с асинхронной поддержкой. Создает движок базы данных и фабрику сессий для выполнения запросов.

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/messenger_channel"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

### 2.3 schema.py

Определяет GraphQL схему с базовыми типами данных, Query и Mutation классами. Содержит скалярные типы для работы с JSONB полями PostgreSQL.

```python
from __future__ import annotations

import strawberry
from typing import Any
from datetime import datetime

# Скалярный тип для JSONB полей
JSON = strawberry.scalar(
    Any,
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

@strawberry.type
class UserType:
    id: int
    username: str
    profile: JSON | None = None
    

@strawberry.type
class MessageType:
    id: int
    author_id: int
    title: str | None = None
    content: str
    metadata: JSON | None = None
    stats: JSON | None = None
    created_at: datetime
    updated_at: datetime
    # Связи (будут разрешены в резолверах)
    author: UserType | None = None
    comments: list[CommentType] = strawberry.field(default_factory=list)
    

@strawberry.type
class CommentType:
    id: int
    message_id: int
    author_id: int
    parent_comment_id: int | None = None
    content: str
    metadata: JSON | None = None
    reactions: JSON | None = None
    created_at: datetime
    updated_at: datetime
    # Связи (будут разрешены в резолверах)
    author: UserType | None = None
    message: MessageType | None = None
    parent_comment: CommentType | None = None
    replies: list[CommentType] = strawberry.field(default_factory=list)
    

# Input типы для мутаций (можно использовать Pydantic)
@strawberry.input
class MessageCreateInput:
    author_id: int
    title: str | None = None
    content: str
    metadata: JSON | None = None


# Query для чтения данных
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """Простой тестовый запрос"""
        return "Hello, GraphQL!"

# Mutation для изменения данных
@strawberry.type
class Mutation:
    @strawberry.mutation
    def test_mutation(self) -> str:
        """Простая тестовая мутация"""
        return "Mutation works!"

# Создание схемы
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### 2.4 Запуск FastAPI сервера
```bash
python main.py
```

## 3. Погружение в CRUD-GraphQL

Расширяем базовую схему, добавляем полноценные типы данных для всех сущностей БД. Создаем резолверы для чтения данных из PostgreSQL и настраиваем GraphQL Playground для тестирования.

### 3.1 main.py

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from models_graphql import schema

# Создаем GraphQL роутер с включенным GraphQL IDE (Playground)
graphql_app = GraphQLRouter(
    schema,
    graphql_ide="graphiql",  # Включает GraphQL Playground для тестирования
)

# Создаем приложение FastAPI
app = FastAPI(
    title="Messenger Channel API",
    description="GraphQL API для информационного канала мессенджера",
    version="1.0.0",
)

# Подключаем GraphQL эндпоинт
app.include_router(graphql_app, prefix="/graphql")

# Health check
@app.get("/")
async def root():
    return {
        "message": "API доступен",
        "graphql": "/graphql",
        "graphql_playground": "/graphql (откройте в браузере)",
        "swagger": "/docs",
        "redoc": "/redoc",
    }

# Информация об API
@app.get("/info")
async def info():
    return {
        "graphql_endpoint": "/graphql",
        "graphql_playground": "Откройте /graphql в браузере для интерактивного тестирования",
        "swagger_ui": "/docs - только для REST эндпоинтов",
        "note": "GraphQL запросы тестируются через GraphQL Playground, а не Swagger",
    }

if __name__ == "__main__":
    import uvicorn
    # Для разработки с reload используйте: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.2 models_graphql.py

Основной файл с GraphQL схемой. Содержит все типы данных (UserType, MessageType, CommentType), Input типы для мутаций, Query и Mutation классы с резолверами.

```python
"""
GraphQL схема для информационного канала мессенджера

Этот файл содержит:
- GraphQL типы (UserType, MessageType, CommentType)
- Input типы для мутаций
- Query и Mutation классы с резолверами
- Схему GraphQL API
"""

from __future__ import annotations  # Отложенные аннотации типов для Python 3.13+

import strawberry
from typing import Any
from datetime import datetime
from database import AsyncSessionLocal  # Асинхронная сессия для работы с БД
from sqlalchemy import text  # Для выполнения SQL запросов

# ============================================================================
# Скалярные типы
# ============================================================================

# JSON скалярный тип для работы с JSONB полями из PostgreSQL
# Позволяет GraphQL работать с произвольными JSON структурами
# serialize - функция сериализации (преобразование в JSON для ответа)
# parse_value - функция парсинга (преобразование из JSON при получении)
JSON = strawberry.scalar(Any, serialize=lambda v: v, parse_value=lambda v: v)

# ============================================================================
# GraphQL Output Types (типы для возврата данных)
# ============================================================================

@strawberry.type
class UserType:
    """
    GraphQL тип пользователя
    
    Соответствует таблице users в БД.
    Используется для возврата данных о пользователях в GraphQL запросах.
    """
    id: int  # Уникальный идентификатор пользователя
    username: str  # Уникальное имя пользователя
    profile: JSON | None = None  # Настройки профиля в формате JSON (тема, уведомления, язык)

@strawberry.type
class MessageType:
    """
    GraphQL тип сообщения канала
    
    Соответствует таблице messages в БД.
    Представляет сообщение, опубликованное в информационном канале.
    """
    id: int  # Уникальный идентификатор сообщения
    author_id: int  # ID автора сообщения (ссылка на users.id)
    title: str | None = None  # Заголовок сообщения (опционально)
    content: str  # Текст сообщения (обязательное поле)
    metadata: JSON | None = None  # Дополнительные данные: теги, время чтения, закрепление
    stats: JSON | None = None  # Статистика: просмотры, лайки, количество комментариев
    created_at: datetime  # Дата и время создания сообщения
    updated_at: datetime  # Дата и время последнего обновления
    
    # Связи с другими типами (разрешаются в резолверах)
    author: UserType | None = None  # Объект автора сообщения (загружается отдельным запросом)
    comments: list[CommentType] = strawberry.field(
        default_factory=list  # Список комментариев к сообщению (по умолчанию пустой)
    )

@strawberry.type
class CommentType:
    """
    GraphQL тип комментария
    
    Соответствует таблице comments в БД.
    Представляет комментарий пользователя к сообщению канала.
    Поддерживает вложенные комментарии (ответы на комментарии).
    """
    id: int  # Уникальный идентификатор комментария
    message_id: int  # ID сообщения, к которому относится комментарий
    author_id: int  # ID автора комментария (ссылка на users.id)
    parent_comment_id: int | None = None  # ID родительского комментария (для вложенных комментариев)
    content: str  # Текст комментария
    metadata: JSON | None = None  # Дополнительные данные: редактирование, упоминания
    reactions: JSON | None = None  # Реакции на комментарий: {"like": 5, "love": 2}
    created_at: datetime  # Дата и время создания комментария
    updated_at: datetime  # Дата и время последнего обновления
    
    # Связи с другими типами (разрешаются в резолверах)
    author: UserType | None = None  # Объект автора комментария
    message: MessageType | None = None  # Объект сообщения, к которому относится комментарий
    parent_comment: CommentType | None = None  # Родительский комментарий (если это ответ)
    replies: list[CommentType] = strawberry.field(
        default_factory=list  # Список ответов на этот комментарий
    )

# ============================================================================
# GraphQL Input Types (типы для входных данных в мутациях)
# ============================================================================

@strawberry.input
class MessageCreateInput:
    """
    Input тип для создания нового сообщения
    
    Используется в мутациях для создания сообщений.
    Не содержит id, created_at, updated_at - они генерируются автоматически.
    """
    author_id: int  # ID автора сообщения (обязательное поле)
    title: str | None = None  # Заголовок сообщения (опционально)
    content: str  # Текст сообщения (обязательное поле)
    metadata: JSON | None = None  # Дополнительные данные в формате JSON

@strawberry.input
class CommentCreateInput:
    """
    Input тип для создания нового комментария
    
    Используется в мутациях для создания комментариев.
    Не содержит id, created_at, updated_at - они генерируются автоматически.
    """
    message_id: int  # ID сообщения, к которому относится комментарий
    author_id: int  # ID автора комментария
    content: str  # Текст комментария (обязательное поле)
    parent_comment_id: int | None = None  # ID родительского комментария (если это ответ)

# ============================================================================
# Query (запросы для чтения данных)
# ============================================================================

@strawberry.type
class Query:
    """
    Класс Query содержит все резолверы для чтения данных
    
    Каждый метод с декоратором @strawberry.field становится доступным
    в GraphQL схеме как поле для запросов.
    """
    
    @strawberry.field
    def hello(self) -> str:
        """
        Простой тестовый запрос для проверки работы GraphQL API
        
        Пример запроса:
        query {
          hello
        }
        
        Возвращает: "Hello, GraphQL!"
        """
        return "Hello, GraphQL!"
    
    @strawberry.field
    async def messages(self) -> list[MessageType]:
        """
        Резолвер для получения всех сообщений канала
        
        Выполняет SQL запрос к БД и возвращает список всех сообщений,
        отсортированных по дате создания (новые первыми).
        
        Пример запроса:
        query {
          messages {
            id
            title
            content
            authorId
            createdAt
          }
        }
        
        Возвращает: список объектов MessageType
        
        Примечание:
        - Использует асинхронную сессию SQLAlchemy для работы с БД
        - RowMapping автоматически преобразуется в словарь для создания MessageType
        - Связи (author, comments) пока не загружаются (можно добавить отдельные резолверы)
        """
        # Создаем асинхронную сессию для работы с БД
        async with AsyncSessionLocal() as session:
            # Выполняем SQL запрос для получения всех сообщений
            # ORDER BY created_at DESC - сортировка по дате создания (новые первыми)
            result = await session.execute(
                text("SELECT * FROM messages ORDER BY created_at DESC")
            )
            # Получаем все строки результата как RowMapping объекты
            # RowMapping ведет себя как словарь, что позволяет использовать **row
            rows = result.mappings().all()
            
            # Преобразуем каждую строку из БД в GraphQL тип MessageType
            # **row распаковывает словарь и передает все поля как именованные аргументы
            return [MessageType(**row) for row in rows]

# ============================================================================
# Mutation (мутации для изменения данных)
# ============================================================================

@strawberry.type
class Mutation:
    """
    Класс Mutation содержит все резолверы для изменения данных
    
    Каждый метод с декоратором @strawberry.mutation становится доступным
    в GraphQL схеме как мутация.
    """
    
    @strawberry.mutation
    def test_mutation(self) -> str:
        """
        Простая тестовая мутация для проверки работы GraphQL API
        
        Пример запроса:
        mutation {
          testMutation
        }
        
        Возвращает: "Mutation works!"
        
        Примечание: Это заглушка, реальные мутации будут создавать/обновлять данные в БД
        """
        return "Mutation works!"

# ============================================================================
# Создание GraphQL схемы
# ============================================================================

# Создаем финальную GraphQL схему, объединяя Query и Mutation
# query=Query - все запросы для чтения данных
# mutation=Mutation - все мутации для изменения данных
# Схема используется в main.py для создания GraphQL роутера
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

## 4. Реализуем CRUD операции. Пробуем самостоятельно

### 4.1 models_graphql.py

```python
@strawberry.type
class Query:
       
    @strawberry.field
    async def message(self, id: int) -> MessageType | None:
        """
        Резолвер для получения одного сообщения по ID
        
        Выполняет SQL запрос к БД для поиска сообщения с указанным ID.
        Если сообщение не найдено, возвращает None.
        
        Параметры:
        - id: int - уникальный идентификатор сообщения
        
        Пример запроса:
        query {
          message(id: 1) {
            id
            title
            content
            authorId
            metadata
            stats
            createdAt
            updatedAt
          }
        }
        
        Возвращает:
        - MessageType если сообщение найдено
        - None если сообщение с указанным ID не существует
        
        Примечание:
        - Использует параметризованный SQL запрос для безопасности (защита от SQL инъекций)
        - Связи (author, comments) пока не загружаются (можно добавить отдельные резолверы)
        """
        # Создаем асинхронную сессию для работы с БД
        async with AsyncSessionLocal() as session:
            # Выполняем параметризованный SQL запрос для поиска сообщения по ID
            # :id - именованный параметр, который безопасно подставляется SQLAlchemy
            result = await session.execute(
                text("SELECT * FROM messages WHERE id = :id"),
                {"id": id}
            )
            # Получаем первую строку результата (если есть)
            row = result.mappings().first()
            
            # Если сообщение найдено, преобразуем в MessageType, иначе возвращаем None
            return MessageType(**row) if row else None
    
    @strawberry.field
    async def users(self) -> list[UserType]:
        """
        Резолвер для получения всех пользователей       
       
        """
        async with AsyncSessionLocal() as session:
            result = ...
            rows = ...
            return ...
    
    @strawberry.field
    async def user(self, id: int) -> UserType | None:
        """
        Резолвер для получения одного пользователя по ID
        """
        async with AsyncSessionLocal() as session:
          ...

# ============================================================================
# Mutation (мутации для изменения данных)
# ============================================================================

@strawberry.type
class Mutation:
    """
    Класс Mutation содержит все резолверы для изменения данных
    
    Каждый метод с декоратором @strawberry.mutation становится доступным
    в GraphQL схеме как мутация.
    """
    
    @strawberry.mutation
    def test_mutation(self) -> str:
        """
        Простая тестовая мутация для проверки работы GraphQL API
        
        Пример запроса:
        mutation {
          testMutation
        }
        
        Возвращает: "Mutation works!"
        
        Примечание: Это заглушка, реальные мутации будут создавать/обновлять данные в БД
        """
        return "Mutation works!"

# ============================================================================
# Создание GraphQL схемы
# ============================================================================

# Создаем финальную GraphQL схему, объединяя Query и Mutation
# query=Query - все запросы для чтения данных
# mutation=Mutation - все мутации для изменения данных
# Схема используется в main.py для создания GraphQL роутера
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

## 5. Погружение в мутации

Создаем полноценные CRUD операции для пользователей. Выносим логику в отдельные файлы резолверов для лучшей организации кода. Изучаем Input типы и обработку ошибок.

### 5.1 schema.py

```python
# Input типы для мутаций (можно использовать Pydantic)
@strawberry.input
class MessageCreateInput:
    author_id: int
    title: str | None = None
    content: str
    metadata: JSON | None = None

@strawberry.input
class CommentCreateInput:
    message_id: int
    author_id: int
    content: str
    parent_comment_id: int | None = None

# Query для чтения данных
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """Простой тестовый запрос"""
        return "Hello, GraphQL!"

# Mutation для изменения данных
@strawberry.type
class Mutation:
    @strawberry.mutation
    def test_mutation(self) -> str:
        """Простая тестовая мутация"""
        return "Mutation works!"

# Создание схемы
```

### 5.2 user_resolvers.py

```python
"""
Резолверы для CRUD операций с пользователями

Этот файл содержит резолверы для:
- Create: создание нового пользователя
- Read: получение пользователей (список и по ID)
- Update: обновление данных пользователя
- Delete: удаление пользователя
"""

import json
from database import AsyncSessionLocal
from sqlalchemy import text
from models_graphql import UserType

# ============================================================================
# Read (чтение данных)
# ============================================================================

async def get_all_users() -> list[UserType]:
   
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users ORDER BY id")
        )
        rows = result.mappings().all()
        return [UserType(**row) for row in rows]


async def get_user_by_id(user_id: int) -> UserType | None:   
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": user_id}
        )
        row = result.mappings().first()
        return UserType(**row) if row else None

async def create_user(username: str, profile: dict | None = None) -> UserType:
    """
    Создать нового пользователя
    
    Параметры:
    - username: str - уникальное имя пользователя
    - profile: dict | None - настройки профиля в формате JSON
    
    Возвращает:
    - UserType: созданный пользователь с присвоенным ID
    
    Примечание:
    - Автоматически генерирует ID через GENERATED ALWAYS AS IDENTITY
    - Возвращает созданного пользователя с полными данными
    
    Пример GraphQL мутации:
    graphql
    mutation {
      createUser(
        username: "new_user"
        profile: {
          theme: "light"
          notifications: true
          language: "ru"
        }
      ) {
        id
        username
        profile
      }
    }
  """  
    async with AsyncSessionLocal() as session:
        # Подготавливаем profile как JSON строку для PostgreSQL
        # Если profile не передан, используем пустой JSON объект
        profile_json = json.dumps(profile) if profile else '{}'
        
        # Вставляем нового пользователя и возвращаем созданную запись
        # Используем CAST вместо ::jsonb для совместимости с asyncpg
        result = await session.execute(
            text("""
                INSERT INTO users (username, profile)
                VALUES (:username, CAST(:profile AS jsonb))
                RETURNING *
            """),
            {"username": username, "profile": profile_json}
        )
        await session.commit()
        
        row = result.mappings().first()
        return UserType(**row) if row else None

# ============================================================================
# Update (обновление данных)
# ============================================================================

async def update_user(
    user_id: int,
    username: str | None = None,
    profile: dict | None = None
) -> UserType | None:
    """
    Обновить данные пользователя    
   
    Пример GraphQL мутации (обновление username):
    graphql
    mutation {
      updateUser(
        userId: 1
        username: "updated_username"
      ) {
        id
        username
        profile
      }
    }
    """    
    async with AsyncSessionLocal() as session:
        # Формируем динамический SQL запрос в зависимости от переданных полей
        updates = []
        params = {"id": user_id}
        
        if username is not None:
            updates.append("username = :username")
            params["username"] = username
        
        if profile is not None:
            updates.append("profile = :profile::jsonb")
            params["profile"] = json.dumps(profile)
        
        if not updates:
            # Если ничего не передано для обновления, просто возвращаем пользователя
            return await get_user_by_id(user_id)
        
        # Выполняем обновление и возвращаем обновленную запись
        result = await session.execute(
            text(f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE id = :id
                RETURNING *
            """),
            params
        )
        await session.commit()
        
        row = result.mappings().first()
        return UserType(**row) if row else None

# ============================================================================
# Delete (удаление данных)
# ============================================================================

async def delete_user(user_id: int) -> bool:
    """
    Удалить пользователя по ID
   
    
    Пример GraphQL мутации:
   graphql
    mutation {
      deleteUser(userId: 1)
    }
    """    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"),
            {"id": user_id}
        )
        await session.commit()
        
        # Проверяем, была ли удалена хотя бы одна запись
        return result.rowcount > 0
```

### 5.3 models_graphql.py

```python
@strawberry.field
    async def users(self) -> list[UserType]:
        """
        Резолвер для получения всех пользователей       
        """
        from user_resolvers import get_all_users
        return await get_all_users()
    
    @strawberry.field
    async def user(self, id: int) -> UserType | None:
        """
        Резолвер для получения одного пользователя по ID        
        """
        from user_resolvers import get_user_by_id
        return await get_user_by_id(id)

# ============================================================================
# Mutation (мутации для изменения данных)
# ============================================================================

@strawberry.type
class Mutation:
    """
    Класс Mutation содержит все резолверы для изменения данных    
    Каждый метод с декоратором @strawberry.mutation становится доступным
    в GraphQL схеме как мутация.
    """
    
    
    
    @strawberry.mutation
    async def create_user(
        self,
        username: str,
        profile: JSON | None = None
    ) -> UserType:
        """
        Создать нового пользователя       
        """
        from user_resolvers import create_user
        profile_dict = profile if isinstance(profile, dict) else None
        return await create_user(username, profile_dict)
    
    @strawberry.mutation
    async def update_user(
        self,
        user_id: int,
        username: str | None = None,
        profile: JSON | None = None
    ) -> UserType | None:
        """
        Обновить данные пользователя
       
        """
        from user_resolvers import update_user
        profile_dict = profile if isinstance(profile, dict) else None
        return await update_user(user_id, username, profile_dict)
    
    @strawberry.mutation
    async def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя по ID        
      
        """
        from user_resolvers import delete_user
        return await delete_user(user_id)
```

## 6. Задачи для самостоятельной работы

Выполните задания из файла [tasks_for_students.md](tasks_for_students.md) используя заготовки из [student_resolvers.py](student_resolvers.py)


📊 Выводы по работе
Что изучили:
Перечислите основные технологии...
Какие сложности возникли:
Опишите проблемы...
Практическое применение: