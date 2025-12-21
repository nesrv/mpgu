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
