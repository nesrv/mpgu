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
    """
    Получить всех пользователей из БД
    
    Возвращает:
    - list[UserType]: список всех пользователей, отсортированных по ID
    
    Пример GraphQL запроса:
    ```graphql
    query {
      users {
        id
        username
        profile
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "users": [
          {
            "id": 1,
            "username": "alex_dev",
            "profile": {
              "theme": "dark",
              "notifications": true,
              "language": "ru"
            }
          }
        ]
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users ORDER BY id")
        )
        rows = result.mappings().all()
        return [UserType(**row) for row in rows]


async def get_user_by_id(user_id: int) -> UserType | None:
    """
    Получить пользователя по ID
    
    Параметры:
    - user_id: int - уникальный идентификатор пользователя
    
    Возвращает:
    - UserType если пользователь найден
    - None если пользователь с указанным ID не существует
    
    Пример GraphQL запроса:
    ```graphql
    query {
      user(id: 1) {
        id
        username
        profile
      }
    }
    ```
    
    Пример ответа (пользователь найден):
    ```json
    {
      "data": {
        "user": {
          "id": 1,
          "username": "alex_dev",
          "profile": {
            "theme": "dark",
            "notifications": true,
            "language": "ru"
          }
        }
      }
    }
    ```
    
    Пример ответа (пользователь не найден):
    ```json
    {
      "data": {
        "user": null
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": user_id}
        )
        row = result.mappings().first()
        return UserType(**row) if row else None

# ============================================================================
# Create (создание данных)
# ============================================================================

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
    ```graphql
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
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "createUser": {
          "id": 9,
          "username": "new_user",
          "profile": {
            "theme": "light",
            "notifications": true,
            "language": "ru"
          }
        }
      }
    }
    ```
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
    
    Параметры:
    - user_id: int - ID пользователя для обновления
    - username: str | None - новое имя пользователя (опционально)
    - profile: dict | None - новые настройки профиля (опционально)
    
    Возвращает:
    - UserType если пользователь найден и обновлен
    - None если пользователь с указанным ID не существует
    
    Примечание:
    - Обновляет только переданные поля
    - Если поле не передано, оно остается без изменений
    
    Пример GraphQL мутации (обновление username):
    ```graphql
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
    ```
    
    Пример GraphQL мутации (обновление profile):
    ```graphql
    mutation {
      updateUser(
        userId: 1
        profile: {
          theme: "dark"
          notifications: false
          language: "en"
        }
      ) {
        id
        username
        profile
      }
    }
    ```
    
    Пример ответа:
    ```json
    {
      "data": {
        "updateUser": {
          "id": 1,
          "username": "updated_username",
          "profile": {
            "theme": "dark",
            "notifications": false,
            "language": "en"
          }
        }
      }
    }
    ```
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
    
    Параметры:
    - user_id: int - уникальный идентификатор пользователя для удаления
    
    Возвращает:
    - bool: True если пользователь был удален, False если не найден
    
    Примечание:
    - Использует CASCADE для автоматического удаления связанных данных
    - Удаляет все сообщения и комментарии пользователя (ON DELETE CASCADE)
    
    Пример GraphQL мутации:
    ```graphql
    mutation {
      deleteUser(userId: 1)
    }
    ```
    
    Пример ответа (пользователь удален):
    ```json
    {
      "data": {
        "deleteUser": true
      }
    }
    ```
    
    Пример ответа (пользователь не найден):
    ```json
    {
      "data": {
        "deleteUser": false
      }
    }
    ```
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("DELETE FROM users WHERE id = :id RETURNING id"),
            {"id": user_id}
        )
        await session.commit()
        
        # Проверяем, была ли удалена хотя бы одна запись
        return result.rowcount > 0

