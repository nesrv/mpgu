from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any

# ============================================================================
# User Models для REST API
# ============================================================================

class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str = Field(..., min_length=1, max_length=100)

class UserCreate(UserBase):
    """Модель для создания пользователя"""
    profile: dict[str, Any] | None = Field(None, description="Настройки профиля")

class UserUpdate(BaseModel):
    """Модель для обновления пользователя"""
    username: str | None = Field(None, min_length=1, max_length=100)
    profile: dict[str, Any] | None = None

class UserResponse(UserBase):
    """Модель ответа для пользователя"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "alex_dev",
                "profile": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "ru"
                }
            }
        }
    )
    
    id: int
    profile: dict[str, Any] | None = None

# ============================================================================
# Message Models для REST API
# ============================================================================

class MessageBase(BaseModel):
    """Базовая модель сообщения"""
    title: str | None = Field(None, max_length=200, description="Заголовок сообщения")
    content: str = Field(..., min_length=1, description="Содержимое сообщения")
    metadata: dict[str, Any] | None = Field(None, description="Дополнительные данные")

class MessageCreate(MessageBase):
    """Модель для создания сообщения"""
    author_id: int = Field(..., gt=0, description="ID автора сообщения")

class MessageUpdate(BaseModel):
    """Модель для обновления сообщения"""
    title: str | None = Field(None, max_length=200)
    content: str | None = Field(None, min_length=1)
    metadata: dict[str, Any] | None = None

class MessageResponse(MessageBase):
    """Модель ответа для сообщения"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "author_id": 1,
                "title": "Как начать карьеру в IT",
                "content": "Привет! Многие спрашивают...",
                "metadata": {
                    "tags": ["карьера", "IT"],
                    "reading_time": 3,
                    "is_pinned": True
                },
                "stats": {
                    "views_count": 1247,
                    "likes_count": 89,
                    "comments_count": 23
                },
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )
    
    id: int
    author_id: int
    stats: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

# ============================================================================
# Comment Models для REST API
# ============================================================================

class CommentBase(BaseModel):
    """Базовая модель комментария"""
    content: str = Field(..., min_length=1, description="Текст комментария")
    metadata: dict[str, Any] | None = Field(None, description="Дополнительные данные")

class CommentCreate(CommentBase):
    """Модель для создания комментария"""
    message_id: int = Field(..., gt=0, description="ID сообщения")
    author_id: int = Field(..., gt=0, description="ID автора комментария")
    parent_comment_id: int | None = Field(None, gt=0, description="ID родительского комментария")

class CommentUpdate(BaseModel):
    """Модель для обновления комментария"""
    content: str | None = Field(None, min_length=1)
    metadata: dict[str, Any] | None = None
    reactions: dict[str, Any] | None = None

class CommentResponse(CommentBase):
    """Модель ответа для комментария"""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "message_id": 1,
                "author_id": 2,
                "parent_comment_id": None,
                "content": "Отличный пост!",
                "metadata": {
                    "is_edited": False,
                    "mentions": []
                },
                "reactions": {
                    "like": 12,
                    "love": 2
                },
                "created_at": "2024-01-01T12:00:00",
                "updated_at": "2024-01-01T12:00:00"
            }
        }
    )
    
    id: int
    message_id: int
    author_id: int
    parent_comment_id: int | None = None
    reactions: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
