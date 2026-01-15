"""
Задание 4: Подписка на лайки к сообщению (ПРОСТОЕ РЕШЕНИЕ)
"""

from __future__ import annotations
import strawberry
from typing import AsyncIterator
from datetime import datetime
from pubsub import pubsub

# ============================================================================
# ШАГ 1: ТИПЫ ДАННЫХ
# ============================================================================

@strawberry.type
class Like:
    id: int
    message_id: int
    user_id: int
    user_name: str
    created_at: datetime


@strawberry.type
class LikeStats:
    message_id: int
    total_likes: int
    recent_likes: list[Like]


@strawberry.type
class LikeResult:
    success: bool
    total_likes: int


# ============================================================================
# ШАГ 2: ХРАНИЛИЩЕ (простой словарь)
# ============================================================================

# Хранилище: {message_id: {user_id: Like}}
likes = {}
like_id = 1


# ============================================================================
# ШАГ 3: QUERY
# ============================================================================

@strawberry.type
class Query:
    
    @strawberry.field
    def like_stats(self, message_id: int) -> LikeStats:
        """Получить статистику лайков"""
        if message_id not in likes:
            likes[message_id] = {}
        
        all_likes = list(likes[message_id].values())
        recent = sorted(all_likes, key=lambda x: x.created_at, reverse=True)[:5]
        
        return LikeStats(
            message_id=message_id,
            total_likes=len(all_likes),
            recent_likes=recent
        )


# ============================================================================
# ШАГ 4: MUTATION
# ============================================================================

@strawberry.type
class Mutation:
    
    @strawberry.mutation
    async def like_message(self, message_id: int, info: strawberry.Info) -> LikeResult:
        """Поставить/убрать лайк"""
        global like_id
        
        user_id = info.context.get("user_id", 1)
        user_name = info.context.get("user_name", f"User{user_id}")
        
        # Создаем хранилище для сообщения
        if message_id not in likes:
            likes[message_id] = {}
        
        # Toggle: если лайк есть - удаляем, если нет - добавляем
        if user_id in likes[message_id]:
            del likes[message_id][user_id]
        else:
            likes[message_id][user_id] = Like(
                id=like_id,
                message_id=message_id,
                user_id=user_id,
                user_name=user_name,
                created_at=datetime.now()
            )
            like_id += 1
        
        # Отправляем обновление подписчикам
        all_likes = list(likes[message_id].values())
        recent = sorted(all_likes, key=lambda x: x.created_at, reverse=True)[:5]
        
        await pubsub.publish(f"likes:{message_id}", {
            "message_id": message_id,
            "total_likes": len(all_likes),
            "recent_likes": recent
        })
        
        return LikeResult(success=True, total_likes=len(all_likes))


# ============================================================================
# ШАГ 5: SUBSCRIPTION
# ============================================================================

@strawberry.type
class Subscription:
    
    @strawberry.subscription
    async def on_message_likes(self, message_id: int) -> AsyncIterator[LikeStats]:
        """Подписка на лайки"""
        # Отправляем текущее состояние
        if message_id not in likes:
            likes[message_id] = {}
        
        all_likes = list(likes[message_id].values())
        recent = sorted(all_likes, key=lambda x: x.created_at, reverse=True)[:5]
        
        yield LikeStats(
            message_id=message_id,
            total_likes=len(all_likes),
            recent_likes=recent
        )
        
        # Слушаем обновления
        async for event in pubsub.subscribe(f"likes:{message_id}"):
            yield LikeStats(
                message_id=event["message_id"],
                total_likes=event["total_likes"],
                recent_likes=event["recent_likes"]
            )


# ============================================================================
# ШАГ 6: СХЕМА
# ============================================================================

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)


# ============================================================================
# ПРИМЕРЫ ЗАПРОСОВ
# ============================================================================

"""
=== ПОДПИСКА (Вкладка 1) ===
subscription {
  onMessageLikes(messageId: 1) {
    totalLikes
    recentLikes {
      userName
      createdAt
    }
  }
}


=== ЛАЙК (Вкладка 2) ===
mutation {
  likeMessage(messageId: 1) {
    success
    totalLikes
  }
}

Добавьте заголовки:
X-User-Id: 10
X-User-Name: Alice


=== СТАТИСТИКА ===
query {
  likeStats(messageId: 1) {
    totalLikes
    recentLikes {
      userName
    }
  }
}
"""
