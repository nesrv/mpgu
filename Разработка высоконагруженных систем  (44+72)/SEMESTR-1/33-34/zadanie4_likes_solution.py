"""
Решение задания 4: Подписка на лайки к сообщению
Дисциплина: Разработка высоконагруженных систем
"""

from __future__ import annotations
import strawberry
from typing import AsyncIterator, Optional
from datetime import datetime
from pubsub import pubsub  # Импорт из основной лабораторной

# ============================================================================
# ТИПЫ ДАННЫХ
# ============================================================================

@strawberry.type
class Like:
    """Лайк к сообщению"""
    id: int
    message_id: int
    user_id: int
    user_name: str
    created_at: datetime


@strawberry.type
class LikeStats:
    """Статистика лайков сообщения"""
    message_id: int
    total_likes: int
    recent_likes: list[Like]
    user_liked: bool = False


@strawberry.type
class LikeResult:
    """Результат операции лайка"""
    success: bool
    total_likes: int
    message: str = ""


# ============================================================================
# ХРАНИЛИЩЕ ДАННЫХ
# ============================================================================

# In-memory хранилище лайков: {message_id: {user_id: Like}}
likes_storage: dict[int, dict[int, Like]] = {}

# Счетчик для генерации ID
like_id_counter = 1


def generate_like_id() -> int:
    """Генерация уникального ID для лайка"""
    global like_id_counter
    current_id = like_id_counter
    like_id_counter += 1
    return current_id


# ============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================================

def get_like_stats(message_id: int, user_id: Optional[int] = None) -> LikeStats:
    """
    Получить статистику лайков для сообщения
    
    Args:
        message_id: ID сообщения
        user_id: ID текущего пользователя (для проверки user_liked)
    
    Returns:
        LikeStats: статистика лайков
    """
    if message_id not in likes_storage:
        likes_storage[message_id] = {}
    
    likes = list(likes_storage[message_id].values())
    total = len(likes)
    recent = sorted(likes, key=lambda x: x.created_at, reverse=True)[:5]
    user_liked = user_id in likes_storage[message_id] if user_id else False
    
    return LikeStats(
        message_id=message_id,
        total_likes=total,
        recent_likes=recent,
        user_liked=user_liked
    )


async def publish_like_update(message_id: int):
    """
    Опубликовать обновление лайков в канал подписки
    
    Args:
        message_id: ID сообщения
    """
    stats = get_like_stats(message_id)
    await pubsub.publish(
        f"message_likes:{message_id}",
        {
            "message_id": stats.message_id,
            "total_likes": stats.total_likes,
            "recent_likes": stats.recent_likes
        }
    )


# ============================================================================
# QUERY
# ============================================================================

@strawberry.type
class Query:
    
    @strawberry.field
    def like_stats(
        self,
        message_id: int,
        info: strawberry.Info
    ) -> LikeStats:
        """
        Получить статистику лайков для сообщения
        
        Пример запроса:
        ```graphql
        query {
          likeStats(messageId: 1) {
            messageId
            totalLikes
            recentLikes {
              userId
              userName
              createdAt
            }
            userLiked
          }
        }
        ```
        """
        user_id = info.context.get("user_id")
        return get_like_stats(message_id, user_id)


# ============================================================================
# MUTATION
# ============================================================================

@strawberry.type
class Mutation:
    
    @strawberry.mutation
    async def like_message(
        self,
        message_id: int,
        info: strawberry.Info
    ) -> LikeResult:
        """
        Поставить лайк сообщению (или убрать, если уже лайкнуто)
        
        Пример запроса:
        ```graphql
        mutation {
          likeMessage(messageId: 1) {
            success
            totalLikes
            message
          }
        }
        ```
        """
        # Получаем данные пользователя из контекста
        user_id = info.context.get("user_id", 1)
        user_name = info.context.get("user_name", f"User{user_id}")
        
        # Инициализируем хранилище для сообщения, если его нет
        if message_id not in likes_storage:
            likes_storage[message_id] = {}
        
        # Toggle логика: если лайк есть - удаляем, если нет - добавляем
        if user_id in likes_storage[message_id]:
            # Удаляем лайк
            del likes_storage[message_id][user_id]
            message = "Лайк удален"
        else:
            # Добавляем лайк
            like = Like(
                id=generate_like_id(),
                message_id=message_id,
                user_id=user_id,
                user_name=user_name,
                created_at=datetime.now()
            )
            likes_storage[message_id][user_id] = like
            message = "Лайк добавлен"
        
        # Публикуем обновление для всех подписчиков
        await publish_like_update(message_id)
        
        total_likes = len(likes_storage[message_id])
        
        return LikeResult(
            success=True,
            total_likes=total_likes,
            message=message
        )
    
    @strawberry.mutation
    async def unlike_message(
        self,
        message_id: int,
        info: strawberry.Info
    ) -> LikeResult:
        """
        Убрать лайк с сообщения
        
        Пример запроса:
        ```graphql
        mutation {
          unlikeMessage(messageId: 1) {
            success
            totalLikes
            message
          }
        }
        ```
        """
        user_id = info.context.get("user_id", 1)
        
        # Проверяем существование лайка
        if message_id not in likes_storage or user_id not in likes_storage[message_id]:
            return LikeResult(
                success=False,
                total_likes=len(likes_storage.get(message_id, {})),
                message="Лайк не найден"
            )
        
        # Удаляем лайк
        del likes_storage[message_id][user_id]
        
        # Публикуем обновление
        await publish_like_update(message_id)
        
        total_likes = len(likes_storage[message_id])
        
        return LikeResult(
            success=True,
            total_likes=total_likes,
            message="Лайк удален"
        )


# ============================================================================
# SUBSCRIPTION
# ============================================================================

@strawberry.type
class Subscription:
    
    @strawberry.subscription
    async def on_message_likes(
        self,
        message_id: int
    ) -> AsyncIterator[LikeStats]:
        """
        Подписка на изменения лайков сообщения
        
        Пример подписки:
        ```graphql
        subscription {
          onMessageLikes(messageId: 1) {
            messageId
            totalLikes
            recentLikes {
              id
              userId
              userName
              createdAt
            }
          }
        }
        ```
        """
        # Отправляем текущее состояние при подключении
        yield get_like_stats(message_id)
        
        # Подписываемся на обновления
        async for event in pubsub.subscribe(f"message_likes:{message_id}"):
            yield LikeStats(
                message_id=event["message_id"],
                total_likes=event["total_likes"],
                recent_likes=event["recent_likes"],
                user_liked=False
            )


# ============================================================================
# СХЕМА
# ============================================================================

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)


# ============================================================================
# ИНТЕГРАЦИЯ С FASTAPI
# ============================================================================

"""
Добавьте в main.py:

from fastapi import FastAPI, Request
from strawberry.fastapi import GraphQLRouter
from zadanie4_likes_solution import schema

app = FastAPI()

# Контекст для передачи данных пользователя
async def get_context(request: Request):
    return {
        "user_id": request.headers.get("X-User-Id", 1),
        "user_name": request.headers.get("X-User-Name", "Anonymous")
    }

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

app.include_router(graphql_app, prefix="/graphql")
"""


# ============================================================================
# ПРИМЕРЫ ЗАПРОСОВ ДЛЯ ТЕСТИРОВАНИЯ
# ============================================================================

"""
=== ТЕСТ 1: Базовая функциональность ===

Вкладка 1 - Подписка:
subscription {
  onMessageLikes(messageId: 1) {
    messageId
    totalLikes
    recentLikes {
      userId
      userName
      createdAt
    }
  }
}

Вкладка 2 - Лайк (добавьте заголовок X-User-Id: 10, X-User-Name: Alice):
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
    message
  }
}

Ожидаемый результат: Вкладка 1 получит обновление с totalLikes: 1


=== ТЕСТ 2: Множественные лайки ===

Вкладка 1-3 - Подписки на сообщение 1

Вкладка 4 (User 10):
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
  }
}

Вкладка 5 (User 20):
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
  }
}

Вкладка 6 (User 30):
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
  }
}

Ожидаемый результат: Все подписчики получат обновления, totalLikes = 3


=== ТЕСТ 3: Удаление лайка ===

Вкладка 1 - Подписка на сообщение 1

Вкладка 2 (User 10) - Лайк:
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
  }
}

Вкладка 2 (User 10) - Повторный лайк (удаление):
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
    message
  }
}

Ожидаемый результат: totalLikes уменьшится, message: "Лайк удален"


=== ТЕСТ 4: Получение статистики ===

query {
  likeStats(messageId: 1) {
    messageId
    totalLikes
    recentLikes {
      userId
      userName
      createdAt
    }
    userLiked
  }
}


=== ТЕСТ 5: Проверка последних 5 лайков ===

1. Добавьте 10 лайков от разных пользователей
2. Проверьте, что в recentLikes только последние 5
3. Проверьте, что они отсортированы по времени (новые первые)
"""


# ============================================================================
# ДОПОЛНИТЕЛЬНЫЕ УЛУЧШЕНИЯ (БОНУС)
# ============================================================================

"""
1. Добавить разные типы реакций (👍, ❤️, 😂, 😮, 😢):

@strawberry.enum
class ReactionType:
    LIKE = "like"
    LOVE = "love"
    LAUGH = "laugh"
    WOW = "wow"
    SAD = "sad"

@strawberry.type
class Reaction:
    id: int
    message_id: int
    user_id: int
    user_name: str
    type: ReactionType
    created_at: datetime


2. Добавить группировку по типам реакций:

@strawberry.type
class ReactionStats:
    message_id: int
    reactions_by_type: dict[ReactionType, int]
    total_reactions: int
    recent_reactions: list[Reaction]


3. Добавить уведомления автору сообщения:

subscription OnMyMessageLikes($userId: Int!) {
  onMyMessageLikes(userId: $userId) {
    messageId
    messageTitle
    totalLikes
    lastLikedBy {
      userName
    }
  }
}
"""
