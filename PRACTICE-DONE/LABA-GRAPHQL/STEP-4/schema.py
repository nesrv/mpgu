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
schema = strawberry.Schema(query=Query, mutation=Mutation)