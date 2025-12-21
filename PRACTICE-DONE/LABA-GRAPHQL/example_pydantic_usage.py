"""
Пример использования Pydantic со Strawberry GraphQL

Этот файл показывает различные способы интеграции Pydantic и Strawberry
"""

from models import UserModel, MessageModel, CommentModel
from schema import UserType, MessageType, CommentType

# Пример 1: Конвертация из Pydantic модели в Strawberry тип
def example_conversion():
    # Предположим, у вас есть данные из БД (например, через SQLAlchemy)
    user_data = {
        "id": 1,
        "username": "alex_dev",
        "profile": {"theme": "dark", "notifications": True}
    }
    
    # Создаем Pydantic модель (валидация данных)
    user_model = UserModel(**user_data)
    
    # Конвертируем в Strawberry тип для GraphQL
    user_type = UserType.from_pydantic(user_model)
    
    return user_type


# Пример 2: Использование Pydantic для валидации в резолверах
async def example_resolver_with_validation():
    # Получаем данные из БД (например, через SQLAlchemy)
    # db_user = await db.get_user(user_id=1)
    
    # Валидируем через Pydantic (автоматическая валидация)
    # user_model = UserModel.model_validate(db_user)
    
    # Конвертируем в GraphQL тип
    # return UserType.from_pydantic(user_model)
    pass


# Пример 3: Использование Pydantic для валидации входных данных
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    """Pydantic модель для валидации создания сообщения"""
    author_id: int = Field(gt=0, description="ID автора должен быть положительным")
    title: str | None = Field(None, max_length=200)
    content: str = Field(..., min_length=1, description="Содержимое обязательно")
    metadata: dict | None = None
    
    def to_strawberry_input(self) -> dict:
        """Конвертация в формат для Strawberry input"""
        return {
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
        }


# Пример 4: Использование Pydantic Settings для конфигурации
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Настройки БД через Pydantic"""
    database_url: str
    pool_size: int = 5
    echo: bool = False
    
    model_config = {
        "env_prefix": "DB_",
        "case_sensitive": False,
    }

# Использование:
# settings = DatabaseSettings()  # Автоматически загрузит из переменных окружения DB_DATABASE_URL и т.д.

