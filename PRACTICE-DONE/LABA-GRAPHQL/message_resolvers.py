"""
Резолверы для CRUD операций с сообщениями

Этот файл содержит резолверы для:
- Create: создание нового сообщения
- Read: получение сообщений (список и по ID)
- Update: обновление данных сообщения
- Delete: удаление сообщения
"""

import json
from database import AsyncSessionLocal
from sqlalchemy import text
from models_graphql import MessageType

# ============================================================================
# Read (чтение данных)
# ============================================================================

async def get_all_messages() -> list[MessageType]:
    """
    Получить все сообщения из БД
    
    Возвращает:
    - list[MessageType]: список всех сообщений, отсортированных по дате создания (новые первыми)
    
    Пример GraphQL запроса:
    ```graphql
    query {
      messages {
        id
        authorId
        title
        content
        metadata
        stats
        createdAt
        updatedAt
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "messages": [
          {
            "id": 1,
            "authorId": 1,
            "title": "Топ-5 инструментов для разработчиков в 2026",
            "content": "Содержание сообщения...",
            "metadata": {
              "tags": ["разработка", "инструменты"],
              "pinned": false
            },
            "stats": {
              "views": 150,
              "likes": 25,
              "comments_count": 5
            },
            "createdAt": "2026-01-15T10:00:00",
            "updatedAt": "2026-01-15T10:00:00"
          }
        ]
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM messages ORDER BY created_at DESC")
        )
        rows = result.mappings().all()
        return [MessageType(**row) for row in rows]


async def get_message_by_id(message_id: int) -> MessageType | None:
    """
    Получить сообщение по ID
    
    Параметры:
    - message_id: int - уникальный идентификатор сообщения
    
    Возвращает:
    - MessageType если сообщение найдено
    - None если сообщение с указанным ID не существует
    
    Пример GraphQL запроса:
    ```graphql
    query {
      message(id: 1) {
        id
        authorId
        title
        content
        metadata
        stats
        createdAt
        updatedAt
      }
    }
    ```
    
    Пример ответа (сообщение найдено):
    ```json
    {
      "data": {
        "message": {
          "id": 1,
          "authorId": 1,
          "title": "Топ-5 инструментов для разработчиков в 2026",
          "content": "Содержание сообщения...",
          "metadata": {
            "tags": ["разработка", "инструменты"]
          },
          "stats": {
            "views": 150,
            "likes": 25
          },
          "createdAt": "2026-01-15T10:00:00",
          "updatedAt": "2026-01-15T10:00:00"
        }
      }
    }
    ```
    
    Пример ответа (сообщение не найдено):
    ```json
    {
      "data": {
        "message": null
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM messages WHERE id = :id"),
            {"id": message_id}
        )
        row = result.mappings().first()
        return MessageType(**row) if row else None

# ============================================================================
# Create (создание данных)
# ============================================================================

async def create_message(
    author_id: int,
    content: str,
    title: str | None = None,
    metadata: dict | None = None,
    stats: dict | None = None
) -> MessageType:
    """
    Создать новое сообщение
    
    Параметры:
    - author_id: int - ID автора сообщения (ссылка на users.id)
    - content: str - текст сообщения (обязательное поле)
    - title: str | None - заголовок сообщения (опционально)
    - metadata: dict | None - дополнительные данные в формате JSON (опционально)
    - stats: dict | None - статистика в формате JSON (опционально)
    
    Возвращает:
    - MessageType: созданное сообщение с присвоенным ID
    
    Примечание:
    - Автоматически генерирует ID через GENERATED ALWAYS AS IDENTITY
    - Автоматически устанавливает created_at и updated_at
    - Возвращает созданное сообщение с полными данными
    
    Пример GraphQL мутации:
    ```graphql
    mutation {
      createMessage(
        authorId: 1
        title: "Новое сообщение"
        content: "Текст нового сообщения"
        metadata: {
          tags: ["новости", "технологии"]
          pinned: false
        }
        stats: {
          views: 0
          likes: 0
          comments_count: 0
        }
      ) {
        id
        authorId
        title
        content
        metadata
        stats
        createdAt
        updatedAt
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "createMessage": {
          "id": 10,
          "authorId": 1,
          "title": "Новое сообщение",
          "content": "Текст нового сообщения",
          "metadata": {
            "tags": ["новости", "технологии"],
            "pinned": false
          },
          "stats": {
            "views": 0,
            "likes": 0,
            "comments_count": 0
          },
          "createdAt": "2026-01-20T12:00:00",
          "updatedAt": "2026-01-20T12:00:00"
        }
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        # Подготавливаем JSON поля для PostgreSQL
        metadata_json = json.dumps(metadata) if metadata else '{}'
        stats_json = json.dumps(stats) if stats else '{}'
        
        # Вставляем новое сообщение и возвращаем созданную запись
        result = await session.execute(
            text("""
                INSERT INTO messages (author_id, title, content, metadata, stats)
                VALUES (:author_id, :title, :content, CAST(:metadata AS jsonb), CAST(:stats AS jsonb))
                RETURNING *
            """),
            {
                "author_id": author_id,
                "title": title,
                "content": content,
                "metadata": metadata_json,
                "stats": stats_json
            }
        )
        await session.commit()
        
        row = result.mappings().first()
        return MessageType(**row) if row else None

# ============================================================================
# Update (обновление данных)
# ============================================================================

async def update_message(
    message_id: int,
    title: str | None = None,
    content: str | None = None,
    metadata: dict | None = None,
    stats: dict | None = None
) -> MessageType | None:
    """
    Обновить данные сообщения
    
    Параметры:
    - message_id: int - ID сообщения для обновления
    - title: str | None - новый заголовок сообщения (опционально)
    - content: str | None - новый текст сообщения (опционально)
    - metadata: dict | None - новые дополнительные данные (опционально)
    - stats: dict | None - новая статистика (опционально)
    
    Возвращает:
    - MessageType если сообщение найдено и обновлено
    - None если сообщение с указанным ID не существует
    
    Примечание:
    - Обновляет только переданные поля
    - Если поле не передано, оно остается без изменений
    - Автоматически обновляет updated_at
    
    Пример GraphQL мутации (обновление title и content):
    ```graphql
    mutation {
      updateMessage(
        messageId: 1
        title: "Обновленный заголовок"
        content: "Обновленное содержание"
      ) {
        id
        title
        content
        updatedAt
      }
    }
    ```
    
    Пример GraphQL мутации (обновление stats):
    ```graphql
    mutation {
      updateMessage(
        messageId: 1
        stats: {
          views: 200
          likes: 30
          comments_count: 8
        }
      ) {
        id
        stats
        updatedAt
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "updateMessage": {
          "id": 1,
          "title": "Обновленный заголовок",
          "content": "Обновленное содержание",
          "updatedAt": "2026-01-20T13:00:00"
        }
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        # Формируем динамический SQL запрос в зависимости от переданных полей
        updates = []
        params = {"id": message_id}
        
        if title is not None:
            updates.append("title = :title")
            params["title"] = title
        
        if content is not None:
            updates.append("content = :content")
            params["content"] = content
        
        if metadata is not None:
            updates.append("metadata = CAST(:metadata AS jsonb)")
            params["metadata"] = json.dumps(metadata)
        
        if stats is not None:
            updates.append("stats = CAST(:stats AS jsonb)")
            params["stats"] = json.dumps(stats)
        
        if not updates:
            # Если ничего не передано для обновления, просто возвращаем сообщение
            return await get_message_by_id(message_id)
        
        # Добавляем обновление updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        # Выполняем обновление и возвращаем обновленную запись
        result = await session.execute(
            text(f"""
                UPDATE messages
                SET {', '.join(updates)}
                WHERE id = :id
                RETURNING *
            """),
            params
        )
        await session.commit()
        
        row = result.mappings().first()
        return MessageType(**row) if row else None

# ============================================================================
# Delete (удаление данных)
# ============================================================================

async def delete_message(message_id: int) -> bool:
    """
    Удалить сообщение по ID
    
    Параметры:
    - message_id: int - уникальный идентификатор сообщения для удаления
    
    Возвращает:
    - bool: True если сообщение было удалено, False если не найдено
    
    Примечание:
    - Использует CASCADE для автоматического удаления связанных данных
    - Удаляет все комментарии к сообщению (ON DELETE CASCADE)
    
    Пример GraphQL мутации:
    ```graphql
    mutation {
      deleteMessage(messageId: 1)
    }
    ```
    
    Пример ответа (сообщение удалено):
    ```json
    {
      "data": {
        "deleteMessage": true
      }
    }
    ```
    
    Пример ответа (сообщение не найдено):
    ```json
    {
      "data": {
        "deleteMessage": false
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM messages WHERE id = :id RETURNING id"),
            {"id": message_id}
        )
        await session.commit()
        
        # Проверяем, была ли удалена хотя бы одна запись
        return result.rowcount > 0

