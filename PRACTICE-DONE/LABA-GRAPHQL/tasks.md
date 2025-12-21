# Задания по созданию GraphQL резолверов

## Структура базы данных

- **users**: id, username, profile (JSONB)
- **messages**: id, author_id, title, content, metadata (JSONB), stats (JSONB), created_at, updated_at
- **comments**: id, message_id, author_id, content, parent_comment_id, reactions (JSONB), created_at, updated_at

---

## Задание 1: Простой резолвер для получения всех комментариев

**Сложность:** ⭐ (Очень простое)

**Описание:** Создайте резолвер `get_all_comments()` в файле `comment_resolvers.py`, который возвращает все комментарии из БД, отсортированные по дате создания (новые первыми).

**Пример GraphQL запроса:**

```graphql
query {
  comments {
    id
    messageId
    authorId
    content
    parentCommentId
    reactions
    createdAt
    updatedAt
  }
}
```

**Решение:**

```python
async def get_all_comments() -> list[CommentType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM comments ORDER BY created_at DESC")
        )
        rows = result.mappings().all()
        return [CommentType(**row) for row in rows]
```

---

## Задание 2: Резолвер для получения комментария по ID

**Сложность:** ⭐ (Очень простое)

**Описание:** Создайте резолвер `get_comment_by_id(comment_id: int)`, который возвращает комментарий по его ID или `None`, если комментарий не найден.

**Пример GraphQL запроса:**

```graphql
query {
  comment(id: 1) {
    id
    messageId
    authorId
    content
    parentCommentId
    reactions
    createdAt
    updatedAt
  }
}
```

**Решение:**

```python
async def get_comment_by_id(comment_id: int) -> CommentType | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM comments WHERE id = :id"),
            {"id": comment_id}
        )
        row = result.mappings().first()
        return CommentType(**row) if row else None
```

---

## Задание 3: Резолвер для получения комментариев к сообщению

**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `get_comments_by_message_id(message_id: int)`, который возвращает все комментарии к конкретному сообщению, отсортированные по дате создания.

**Пример GraphQL запроса:**

```graphql
query {
  commentsByMessageId(messageId: 1) {
    id
    authorId
    content
    parentCommentId
    reactions
    createdAt
  }
}
```

**Решение:**

```python
async def get_comments_by_message_id(message_id: int) -> list[CommentType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM comments WHERE message_id = :message_id ORDER BY created_at ASC"),
            {"message_id": message_id}
        )
        rows = result.mappings().all()
        return [CommentType(**row) for row in rows]
```

---

## Задание 4: Резолвер для получения сообщений пользователя

**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `get_messages_by_author_id(author_id: int)`, который возвращает все сообщения конкретного пользователя.

**Пример GraphQL запроса:**

```graphql
query {
  messagesByAuthorId(authorId: 1) {
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
```

**Решение:**

```python
async def get_messages_by_author_id(author_id: int) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM messages WHERE author_id = :author_id ORDER BY created_at DESC"),
            {"author_id": author_id}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 5: Создание комментария

**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `create_comment(message_id: int, author_id: int, content: str, parent_comment_id: int | None = None)`, который создает новый комментарий.

**Пример GraphQL мутации:**

```graphql
mutation {
  createComment(
    messageId: 1
    authorId: 2
    content: "Отличная статья!"
    parentCommentId: null
  ) {
    id
    messageId
    authorId
    content
    createdAt
  }
}
```

**Решение:**

```python
async def create_comment(
    message_id: int,
    author_id: int,
    content: str,
    parent_comment_id: int | None = None
) -> CommentType:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO comments (message_id, author_id, content, parent_comment_id)
                VALUES (:message_id, :author_id, :content, :parent_comment_id)
                RETURNING *
            """),
            {
                "message_id": message_id,
                "author_id": author_id,
                "content": content,
                "parent_comment_id": parent_comment_id
            }
        )
        await session.commit()
        row = result.mappings().first()
        return CommentType(**row) if row else None
```

---

## Задание 6: Обновление комментария

**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `update_comment(comment_id: int, content: str | None = None)`, который обновляет текст комментария и автоматически обновляет `updated_at`.

**Пример GraphQL мутации:**

```graphql
mutation {
  updateComment(
    commentId: 1
    content: "Исправленный текст комментария"
  ) {
    id
    content
    updatedAt
  }
}
```

**Решение:**

```python
async def update_comment(
    comment_id: int,
    content: str | None = None
) -> CommentType | None:
    async with AsyncSessionLocal() as session:
        updates = []
        params = {"id": comment_id}
        
        if content is not None:
            updates.append("content = :content")
            params["content"] = content
        
        if not updates:
            return await get_comment_by_id(comment_id)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        result = await session.execute(
            text(f"""
                UPDATE comments
                SET {', '.join(updates)}
                WHERE id = :id
                RETURNING *
            """),
            params
        )
        await session.commit()
        row = result.mappings().first()
        return CommentType(**row) if row else None
```

---

## Задание 7: Удаление комментария

**Сложность:** ⭐ (Очень простое)

**Описание:** Создайте резолвер `delete_comment(comment_id: int)`, который удаляет комментарий и возвращает `True` при успехе, `False` если комментарий не найден.

**Пример GraphQL мутации:**

```graphql
mutation {
  deleteComment(commentId: 1)
}
```

**Решение:**

```python
async def delete_comment(comment_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM comments WHERE id = :id RETURNING id"),
            {"id": comment_id}
        )
        await session.commit()
        return result.rowcount > 0
```

---

## Задание 8: Получение сообщений с пагинацией

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_messages_paginated(limit: int = 10, offset: int = 0)`, который возвращает сообщения с пагинацией.

**Пример GraphQL запроса:**

```graphql
query {
  messagesPaginated(limit: 10, offset: 0) {
    id
    title
    content
    authorId
    createdAt
  }
}
```

**Решение:**

```python
async def get_messages_paginated(limit: int = 10, offset: int = 0) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM messages 
                ORDER BY created_at DESC 
                LIMIT :limit OFFSET :offset
            """),
            {"limit": limit, "offset": offset}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 9: Поиск сообщений по заголовку

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `search_messages_by_title(search_term: str)`, который ищет сообщения по заголовку (используйте `ILIKE` для регистронезависимого поиска).

**Пример GraphQL запроса:**

```graphql
query {
  searchMessagesByTitle(searchTerm: "инструменты") {
    id
    title
    content
    authorId
    createdAt
  }
}
```

**Решение:**

```python
async def search_messages_by_title(search_term: str) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM messages 
                WHERE title ILIKE :search_term 
                ORDER BY created_at DESC
            """),
            {"search_term": f"%{search_term}%"}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 10: Получение сообщений с фильтром по дате

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_messages_by_date_range(start_date: datetime, end_date: datetime)`, который возвращает сообщения, созданные в указанном диапазоне дат.

**Пример GraphQL запроса:**

```graphql
query {
  messagesByDateRange(
    startDate: "2026-01-01T00:00:00Z"
    endDate: "2026-01-31T23:59:59Z"
  ) {
    id
    title
    content
    authorId
    createdAt
  }
}
```

**Решение:**

```python
from datetime import datetime

async def get_messages_by_date_range(
    start_date: datetime,
    end_date: datetime
) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM messages 
                WHERE created_at BETWEEN :start_date AND :end_date
                ORDER BY created_at DESC
            """),
            {"start_date": start_date, "end_date": end_date}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 11: Получение топ сообщений по просмотрам

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_top_messages_by_views(limit: int = 10)`, который возвращает топ сообщений по количеству просмотров (поле `stats->>'views'` в JSONB).

**Пример GraphQL запроса:**

```graphql
query {
  topMessagesByViews(limit: 10) {
    id
    title
    content
    stats
    createdAt
  }
}
```

**Решение:**

```python
async def get_top_messages_by_views(limit: int = 10) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM messages 
                WHERE stats IS NOT NULL 
                ORDER BY (stats->>'views')::int DESC NULLS LAST
                LIMIT :limit
            """),
            {"limit": limit}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 12: Получение сообщений с тегами

**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_messages_by_tag(tag: str)`, который возвращает сообщения, содержащие указанный тег в поле `metadata->'tags'` (массив JSON).

**Пример GraphQL запроса:**

```graphql
query {
  messagesByTag(tag: "разработка") {
    id
    title
    content
    metadata
    createdAt
  }
}
```

**Решение:**

```python
async def get_messages_by_tag(tag: str) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM messages 
                WHERE metadata IS NOT NULL 
                AND metadata->'tags' @> :tag::jsonb
                ORDER BY created_at DESC
            """),
            {"tag": json.dumps([tag])}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 13: Получение автора сообщения (JOIN)

**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_message_with_author(message_id: int)`, который возвращает сообщение вместе с данными автора (используйте JOIN).

**Пример GraphQL запроса:**

```graphql
query {
  messageWithAuthor(messageId: 1) {
    id
    title
    content
    author {
      id
      username
      profile
    }
    createdAt
  }
}
```

**Решение:**

```python
async def get_message_with_author(message_id: int) -> MessageType | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT 
                    m.*,
                    u.id as author__id,
                    u.username as author__username,
                    u.profile as author__profile
                FROM messages m
                JOIN users u ON m.author_id = u.id
                WHERE m.id = :id
            """),
            {"id": message_id}
        )
        row = result.mappings().first()
        if row:
            # Преобразуем результат в MessageType
            message_data = {k: v for k, v in row.items() if not k.startswith('author__')}
            message = MessageType(**message_data)
            # Добавляем автора
            if row.get('author__id'):
                from models_graphql import UserType
                message.author = UserType(
                    id=row['author__id'],
                    username=row['author__username'],
                    profile=row['author__profile']
                )
            return message
        return None
```

---

## Задание 14: Получение комментариев с авторами

**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_comments_with_authors(message_id: int)`, который возвращает комментарии к сообщению вместе с данными авторов.

**Пример GraphQL запроса:**

```graphql
query {
  commentsWithAuthors(messageId: 1) {
    id
    content
    author {
      id
      username
      profile
    }
    createdAt
  }
}
```

**Решение:**

```python
async def get_comments_with_authors(message_id: int) -> list[CommentType]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT 
                    c.*,
                    u.id as author__id,
                    u.username as author__username,
                    u.profile as author__profile
                FROM comments c
                JOIN users u ON c.author_id = u.id
                WHERE c.message_id = :message_id
                ORDER BY c.created_at ASC
            """),
            {"message_id": message_id}
        )
        rows = result.mappings().all()
        comments = []
        for row in rows:
            comment_data = {k: v for k, v in row.items() if not k.startswith('author__')}
            comment = CommentType(**comment_data)
            if row.get('author__id'):
                from models_graphql import UserType
                comment.author = UserType(
                    id=row['author__id'],
                    username=row['author__username'],
                    profile=row['author__profile']
                )
            comments.append(comment)
        return comments
```

---

## Задание 15: Подсчет комментариев к сообщению

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_message_comment_count(message_id: int)`, который возвращает количество комментариев к сообщению.

**Пример GraphQL запроса:**

```graphql
query {
  messageCommentCount(messageId: 1)
}
```

**Решение:**

```python
async def get_message_comment_count(message_id: int) -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT COUNT(*) as count 
                FROM comments 
                WHERE message_id = :message_id
            """),
            {"message_id": message_id}
        )
        row = result.mappings().first()
        return row['count'] if row else 0
```

---

## Задание 16: Обновление статистики сообщения

**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `increment_message_views(message_id: int)`, который увеличивает счетчик просмотров в поле `stats->>'views'` на 1.

**Пример GraphQL мутации:**

```graphql
mutation {
  incrementMessageViews(messageId: 1) {
    id
    stats
    updatedAt
  }
}
```

**Решение:**

```python
async def increment_message_views(message_id: int) -> MessageType | None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                UPDATE messages
                SET stats = jsonb_set(
                    COALESCE(stats, '{}'::jsonb),
                    '{views}',
                    COALESCE(((COALESCE(stats->>'views', '0'))::int + 1)::text, '1'),
                    true
                ),
                updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
                RETURNING *
            """),
            {"id": message_id}
        )
        await session.commit()
        row = result.mappings().first()
        return MessageType(**row) if row else None
```

---

## Задание 17: Получение вложенных комментариев (дерево)

**Сложность:** ⭐⭐⭐⭐⭐ (Очень сложное)

**Описание:** Создайте резолвер `get_comment_thread(parent_comment_id: int)`, который возвращает комментарий и все его дочерние комментарии (рекурсивно) в виде дерева.

**Пример GraphQL запроса:**

```graphql
query {
  commentThread(parentCommentId: 1) {
    id
    content
    authorId
    replies {
      id
      content
      authorId
      replies {
        id
        content
      }
    }
    createdAt
  }
}
```

**Решение:**

```python
async def get_comment_thread(parent_comment_id: int) -> CommentType | None:
    async with AsyncSessionLocal() as session:
        # Получаем родительский комментарий
        parent = await get_comment_by_id(parent_comment_id)
        if not parent:
            return None
        
        # Получаем все дочерние комментарии рекурсивно
        result = await session.execute(
            text("""
                WITH RECURSIVE comment_tree AS (
                    SELECT * FROM comments WHERE id = :parent_id
                    UNION ALL
                    SELECT c.* FROM comments c
                    INNER JOIN comment_tree ct ON c.parent_comment_id = ct.id
                )
                SELECT * FROM comment_tree WHERE id != :parent_id
                ORDER BY created_at ASC
            """),
            {"parent_id": parent_comment_id}
        )
        rows = result.mappings().all()
        children = [CommentType(**row) for row in rows]
        
        # Рекурсивно получаем дочерние комментарии для каждого ребенка
        for child in children:
            child.children = await get_comment_thread(child.id)
        
        parent.children = children
        return parent
```

---

## Задание 18: Получение статистики пользователя

**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_user_statistics(user_id: int)`, который возвращает словарь со статистикой пользователя: количество сообщений, комментариев, общее количество просмотров его сообщений.

**Пример GraphQL запроса:**

```graphql
query {
  userStatistics(userId: 1) {
    messagesCount
    commentsCount
    totalViews
  }
}
```

**Примечание:** Для этого запроса нужно создать специальный GraphQL тип `UserStatisticsType`:

```python
@strawberry.type
class UserStatisticsType:
    messages_count: int
    comments_count: int
    total_views: int
```

**Решение:**

```python
async def get_user_statistics(user_id: int) -> dict:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT 
                    (SELECT COUNT(*) FROM messages WHERE author_id = :user_id) as messages_count,
                    (SELECT COUNT(*) FROM comments WHERE author_id = :user_id) as comments_count,
                    (SELECT COALESCE(SUM((stats->>'views')::int), 0) 
                     FROM messages 
                     WHERE author_id = :user_id AND stats IS NOT NULL) as total_views
            """),
            {"user_id": user_id}
        )
        row = result.mappings().first()
        return {
            "messages_count": row['messages_count'] if row else 0,
            "comments_count": row['comments_count'] if row else 0,
            "total_views": row['total_views'] if row else 0
        }
```

---

## Задание 19: Поиск по содержимому сообщений (full-text search)

**Сложность:** ⭐⭐⭐⭐⭐ (Очень сложное)

**Описание:** Создайте резолвер `search_messages_fulltext(search_query: str)`, который выполняет полнотекстовый поиск по содержимому сообщений используя PostgreSQL `tsvector` и `tsquery`.

**Пример GraphQL запроса:**

```graphql
query {
  searchMessagesFulltext(searchQuery: "инструменты разработки") {
    id
    title
    content
    authorId
    createdAt
  }
}
```

**Решение:**

```python
async def search_messages_fulltext(search_query: str) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        # Создаем индекс для полнотекстового поиска (если еще не создан)
        # CREATE INDEX IF NOT EXISTS messages_content_fts ON messages 
        # USING gin(to_tsvector('russian', COALESCE(title, '') || ' ' || content));
        
        result = await session.execute(
            text("""
                SELECT * FROM messages
                WHERE to_tsvector('russian', COALESCE(title, '') || ' ' || content) 
                      @@ plainto_tsquery('russian', :search_query)
                ORDER BY ts_rank(
                    to_tsvector('russian', COALESCE(title, '') || ' ' || content),
                    plainto_tsquery('russian', :search_query)
                ) DESC
            """),
            {"search_query": search_query}
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 20: Комплексный резолвер с агрегацией и фильтрацией

**Сложность:** ⭐⭐⭐⭐⭐ (Очень сложное)

**Описание:** Создайте резолвер `get_messages_advanced(filters: dict)`, который поддерживает множественные фильтры: по автору, дате, тегам, минимальному количеству просмотров, и возвращает результаты с пагинацией и сортировкой.

**Пример GraphQL запроса:**

```graphql
query {
  messagesAdvanced(
    authorId: 1
    startDate: "2026-01-01T00:00:00Z"
    endDate: "2026-01-31T23:59:59Z"
    tag: "разработка"
    minViews: 100
    limit: 20
    offset: 0
    orderBy: "created_at"
    orderDirection: "DESC"
  ) {
    id
    title
    content
    authorId
    metadata
    stats
    createdAt
  }
}
```

**Решение:**

```python
async def get_messages_advanced(
    author_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    tag: str | None = None,
    min_views: int | None = None,
    limit: int = 10,
    offset: int = 0,
    order_by: str = "created_at",
    order_direction: str = "DESC"
) -> list[MessageType]:
    async with AsyncSessionLocal() as session:
        conditions = []
        params = {"limit": limit, "offset": offset}
        
        if author_id is not None:
            conditions.append("author_id = :author_id")
            params["author_id"] = author_id
        
        if start_date is not None:
            conditions.append("created_at >= :start_date")
            params["start_date"] = start_date
        
        if end_date is not None:
            conditions.append("created_at <= :end_date")
            params["end_date"] = end_date
        
        if tag is not None:
            conditions.append("metadata->'tags' @> :tag::jsonb")
            params["tag"] = json.dumps([tag])
        
        if min_views is not None:
            conditions.append("(stats->>'views')::int >= :min_views")
            params["min_views"] = min_views
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Валидация order_by для безопасности
        valid_order_by = ["created_at", "updated_at", "id"]
        if order_by not in valid_order_by:
            order_by = "created_at"
        
        order_direction = "DESC" if order_direction.upper() == "DESC" else "ASC"
        
        query = f"""
            SELECT * FROM messages
            {where_clause}
            ORDER BY {order_by} {order_direction}
            LIMIT :limit OFFSET :offset
        """
        
        result = await session.execute(text(query), params)
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]
```

---

## Задание 21: Именованные GraphQL запросы с переменными

**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолверы, которые поддерживают именованные GraphQL запросы с переменными. Это позволяет переиспользовать запросы, передавать параметры динамически и улучшает читаемость кода.

**Пример GraphQL запроса с переменными:**

```graphql
query GetUserWithMessages($userId: Int!, $messagesLimit: Int = 10) {
  user(id: $userId) {
    id
    username
    profile
    messages(limit: $messagesLimit) {
      id
      title
      content
      createdAt
    }
  }
}
```

**Переменные (Variables):**

```json
{
  "userId": 1,
  "messagesLimit": 5
}
```

**Пример GraphQL запроса для сообщения с комментариями:**

```graphql
query GetMessageWithComments(
  $messageId: Int!
  $commentsLimit: Int = 20
  $includeReplies: Boolean = false
) {
  message(id: $messageId) {
    id
    title
    content
    authorId
    comments(limit: $commentsLimit) {
      id
      content
      authorId
      createdAt
      replies @include(if: $includeReplies) {
        id
        content
        authorId
      }
    }
    stats
    createdAt
  }
}
```

**Переменные (Variables):**

```json
{
  "messageId": 1,
  "commentsLimit": 10,
  "includeReplies": true
}
```

**Пример GraphQL мутации с переменными:**

```graphql
mutation CreateMessageWithMetadata(
  $authorId: Int!
  $title: String
  $content: String!
  $tags: [String!]
  $pinned: Boolean = false
) {
  createMessage(
    authorId: $authorId
    title: $title
    content: $content
    metadata: {
      tags: $tags
      pinned: $pinned
    }
  ) {
    id
    title
    content
    metadata
    createdAt
  }
}
```

**Переменные (Variables):**

```json
{
  "authorId": 1,
  "title": "Новое сообщение",
  "content": "Текст сообщения",
  "tags": ["разработка", "graphql"],
  "pinned": true
}
```

**Пример GraphQL запроса с множественными переменными:**

```graphql
query SearchMessagesAdvanced(
  $searchTerm: String!
  $authorId: Int
  $startDate: DateTime
  $endDate: DateTime
  $tag: String
  $minViews: Int
  $limit: Int = 10
  $offset: Int = 0
) {
  messagesAdvanced(
    searchTerm: $searchTerm
    authorId: $authorId
    startDate: $startDate
    endDate: $endDate
    tag: $tag
    minViews: $minViews
    limit: $limit
    offset: $offset
  ) {
    id
    title
    content
    authorId
    metadata
    stats
    createdAt
  }
}
```

**Переменные (Variables):**

```json
{
  "searchTerm": "инструменты",
  "authorId": 1,
  "startDate": "2026-01-01T00:00:00Z",
  "endDate": "2026-01-31T23:59:59Z",
  "tag": "разработка",
  "minViews": 100,
  "limit": 20,
  "offset": 0
}
```

**Решение:**

Резолверы уже поддерживают переменные через параметры функций. В GraphQL Playground или клиенте просто используйте именованные запросы с переменными:

1. **В GraphQL Playground:**
   - В левой панели введите именованный запрос с переменными
   - В нижней панели "Query Variables" добавьте JSON с переменными

2. **В коде клиента (JavaScript/TypeScript):**

```javascript
const GET_USER_WITH_MESSAGES = gql`
  query GetUserWithMessages($userId: Int!, $messagesLimit: Int = 10) {
    user(id: $userId) {
      id
      username
      messages(limit: $messagesLimit) {
        id
        title
        content
      }
    }
  }
`;

// Использование
const { data } = useQuery(GET_USER_WITH_MESSAGES, {
  variables: {
    userId: 1,
    messagesLimit: 5
  }
});
```

3. **В Python клиенте:**

```python
from gql import gql, Client

query = gql("""
  query GetUserWithMessages($userId: Int!, $messagesLimit: Int = 10) {
    user(id: $userId) {
      id
      username
      messages(limit: $messagesLimit) {
        id
        title
        content
      }
    }
  }
""")

result = client.execute(query, variable_values={
    "userId": 1,
    "messagesLimit": 5
})
```

**Преимущества именованных запросов с переменными:**

1. **Переиспользование** - один запрос можно использовать с разными переменными
2. **Читаемость** - понятно, что делает запрос из его имени
3. **Кэширование** - клиенты могут кэшировать запросы по имени
4. **Отладка** - легче отслеживать запросы в логах
5. **Типизация** - переменные имеют типы, что предотвращает ошибки

**Примечание:** Резолверы на сервере не требуют изменений - они уже принимают параметры. Именованные запросы с переменными - это синтаксис GraphQL на стороне клиента.

---

## Дополнительные рекомендации

1. **Всегда используйте параметризованные запросы** для защиты от SQL-инъекций
2. **Обрабатывайте ошибки** - возвращайте `None` или пустые списки при отсутствии данных
3. **Используйте транзакции** для операций, изменяющих данные
4. **Добавляйте индексы** для часто используемых полей (author_id, message_id, created_at)
5. **Оптимизируйте запросы** - используйте JOIN вместо множественных запросов
6. **Документируйте код** - добавляйте docstrings с примерами GraphQL запросов
7. **Тестируйте резолверы** - проверяйте граничные случаи (пустые данные, несуществующие ID)

---

## Структура файлов для решений

```
LABA-GRAPHQL/
├── comment_resolvers.py    # Резолверы для комментариев
├── message_resolvers.py    # Резолверы для сообщений (уже создан)
├── user_resolvers.py       # Резолверы для пользователей (уже создан)
└── models_graphql.py      # GraphQL типы и схема
```

