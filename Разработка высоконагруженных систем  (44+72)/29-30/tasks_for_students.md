# Задания по созданию GraphQL резолверов
## Практическая работа с базой данных мессенджера

> **Цель:** Создать GraphQL API для системы мессенджера с поддержкой сообщений, комментариев и пользователей.

---

## Задание 1: Резолвер для получения комментариев к сообщению
**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `get_comments_by_message_id(message_id: int)`, который возвращает все комментарии к конкретному сообщению, отсортированные по дате создания.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "commentsByMessageId": [
      {
        "id": 1,
        "authorId": 2,
        "content": "Отличный пост! Добавлю: не забывайте про networking. Многие находят работу через знакомых в IT.",
        "parentCommentId": null,
        "reactions": {"like": 12, "love": 2},
        "createdAt": "2026-01-20T14:00:00Z"
      },
      {
        "id": 2,
        "authorId": 3,
        "content": "Согласен! Я начал с бесплатных курсов на YouTube, потом сделал несколько проектов и через 6 месяцев нашел первую работу.",
        "parentCommentId": null,
        "reactions": {"like": 8},
        "createdAt": "2026-01-20T16:00:00Z"
      }
    ]
  }
}
```

---

## Задание 2: Резолвер для получения сообщений пользователя
**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `get_messages_by_author_id(author_id: int)`, который возвращает все сообщения конкретного пользователя.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "messagesByAuthorId": [
      {
        "id": 1,
        "title": "Как начать карьеру в IT без опыта",
        "content": "Привет! Многие спрашивают, как попасть в IT без опыта...",
        "authorId": 1,
        "metadata": {
          "tags": ["карьера", "IT", "советы"],
          "reading_time": 3,
          "is_pinned": true
        },
        "stats": {
          "views_count": 1247,
          "likes_count": 89,
          "comments_count": 23
        },
        "createdAt": "2026-01-20T10:00:00Z",
        "updatedAt": "2026-01-20T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 3: Создание комментария
**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `create_comment(message_id: int, author_id: int, content: str, parent_comment_id: int | None = None)`, который создает новый комментарий.

**GraphQL мутация:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "createComment": {
      "id": 20,
      "messageId": 1,
      "authorId": 2,
      "content": "Отличная статья!",
      "createdAt": "2026-01-25T15:30:00Z"
    }
  }
}
```

---

## Задание 4: Обновление комментария
**Сложность:** ⭐⭐ (Простое)

**Описание:** Создайте резолвер `update_comment(comment_id: int, content: str | None = None)`, который обновляет текст комментария.

**GraphQL мутация:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "updateComment": {
      "id": 1,
      "content": "Исправленный текст комментария",
      "updatedAt": "2026-01-25T15:35:00Z"
    }
  }
}
```

---

## Задание 5: Удаление комментария
**Сложность:** ⭐ (Очень простое)

**Описание:** Создайте резолвер `delete_comment(comment_id: int)`, который удаляет комментарий.

**GraphQL мутация:**
```graphql
mutation {
  deleteComment(commentId: 1)
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "deleteComment": true
  }
}
```

---

## Задание 6: Получение сообщений с пагинацией
**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_messages_paginated(limit: int = 10, offset: int = 0)`, который возвращает сообщения с пагинацией.

**GraphQL запрос:**
```graphql
query {
  messagesPaginated(limit: 3, offset: 0) {
    id
    title
    content
    authorId
    createdAt
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "messagesPaginated": [
      {
        "id": 6,
        "title": "ИИ в разработке: помощник или замена?",
        "content": "ChatGPT, Copilot, Claude - все используют...",
        "authorId": 6,
        "createdAt": "2026-01-25T12:00:00Z"
      },
      {
        "id": 4,
        "title": "Как правильно составить резюме для IT",
        "content": "Работаю в HR IT-компании и вижу много ошибок...",
        "authorId": 4,
        "createdAt": "2026-01-24T10:00:00Z"
      },
      {
        "id": 3,
        "title": "GraphQL vs REST: что выбрать?",
        "content": "Частый вопрос на собеседованиях...",
        "authorId": 3,
        "createdAt": "2026-01-23T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 7: Поиск сообщений по заголовку
**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `search_messages_by_title(search_term: str)`, который ищет сообщения по заголовку.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "searchMessagesByTitle": [
      {
        "id": 2,
        "title": "Топ-5 инструментов для разработчиков в 2026",
        "content": "Обновил список инструментов, которые реально экономят время...",
        "authorId": 2,
        "createdAt": "2026-01-22T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 8: Получение сообщений с фильтром по дате
**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_messages_by_date_range(start_date: datetime, end_date: datetime)`.

**GraphQL запрос:**
```graphql
query {
  messagesByDateRange(
    startDate: "2026-01-23T00:00:00Z"
    endDate: "2026-01-25T23:59:59Z"
  ) {
    id
    title
    authorId
    createdAt
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "messagesByDateRange": [
      {
        "id": 6,
        "title": "ИИ в разработке: помощник или замена?",
        "authorId": 6,
        "createdAt": "2026-01-25T12:00:00Z"
      },
      {
        "id": 4,
        "title": "Как правильно составить резюме для IT",
        "authorId": 4,
        "createdAt": "2026-01-24T10:00:00Z"
      },
      {
        "id": 3,
        "title": "GraphQL vs REST: что выбрать?",
        "authorId": 3,
        "createdAt": "2026-01-23T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 9: Получение топ сообщений по просмотрам
**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_top_messages_by_views(limit: int = 10)`.

**GraphQL запрос:**
```graphql
query {
  topMessagesByViews(limit: 3) {
    id
    title
    stats
    createdAt
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "topMessagesByViews": [
      {
        "id": 4,
        "title": "Как правильно составить резюме для IT",
        "stats": {
          "views_count": 2105,
          "likes_count": 145,
          "comments_count": 41
        },
        "createdAt": "2026-01-24T10:00:00Z"
      },
      {
        "id": 6,
        "title": "ИИ в разработке: помощник или замена?",
        "stats": {
          "views_count": 1876,
          "likes_count": 134,
          "comments_count": 52
        },
        "createdAt": "2026-01-25T12:00:00Z"
      },
      {
        "id": 3,
        "title": "GraphQL vs REST: что выбрать?",
        "stats": {
          "views_count": 1563,
          "likes_count": 112,
          "comments_count": 34
        },
        "createdAt": "2026-01-23T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 10: Получение сообщений с тегами
**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_messages_by_tag(tag: str)`, который возвращает сообщения с указанным тегом.

**GraphQL запрос:**
```graphql
query {
  messagesByTag(tag: "разработка") {
    id
    title
    metadata
    createdAt
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "messagesByTag": [
      {
        "id": 6,
        "title": "ИИ в разработке: помощник или замена?",
        "metadata": {
          "tags": ["AI", "разработка", "будущее"],
          "reading_time": 4,
          "is_pinned": true
        },
        "createdAt": "2026-01-25T12:00:00Z"
      },
      {
        "id": 2,
        "title": "Топ-5 инструментов для разработчиков в 2026",
        "metadata": {
          "tags": ["инструменты", "разработка", "продуктивность"],
          "reading_time": 2,
          "is_pinned": false
        },
        "createdAt": "2026-01-22T10:00:00Z"
      }
    ]
  }
}
```

---

## Задание 11: Получение автора сообщения (JOIN)
**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_message_with_author(message_id: int)`, который возвращает сообщение с данными автора.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "messageWithAuthor": {
      "id": 1,
      "title": "Как начать карьеру в IT без опыта",
      "content": "Привет! Многие спрашивают, как попасть в IT без опыта...",
      "author": {
        "id": 1,
        "username": "alex_dev",
        "profile": {
          "theme": "dark",
          "notifications": true,
          "language": "ru"
        }
      },
      "createdAt": "2026-01-20T10:00:00Z"
    }
  }
}
```

---

## Задание 12: Получение комментариев с авторами
**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_comments_with_authors(message_id: int)`.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "commentsWithAuthors": [
      {
        "id": 1,
        "content": "Отличный пост! Добавлю: не забывайте про networking...",
        "author": {
          "id": 2,
          "username": "maria_tech",
          "profile": {
            "theme": "light",
            "notifications": true,
            "language": "ru"
          }
        },
        "createdAt": "2026-01-20T14:00:00Z"
      },
      {
        "id": 2,
        "content": "Согласен! Я начал с бесплатных курсов на YouTube...",
        "author": {
          "id": 3,
          "username": "dmitry_coder",
          "profile": {
            "theme": "dark",
            "notifications": false,
            "language": "ru"
          }
        },
        "createdAt": "2026-01-20T16:00:00Z"
      }
    ]
  }
}
```

---

## Задание 13: Подсчет комментариев к сообщению
**Сложность:** ⭐⭐⭐ (Среднее)

**Описание:** Создайте резолвер `get_message_comment_count(message_id: int)`.

**GraphQL запрос:**
```graphql
query {
  messageCommentCount(messageId: 1)
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "messageCommentCount": 4
  }
}
```

---

## Задание 14: Обновление статистики сообщения
**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `increment_message_views(message_id: int)`, который увеличивает счетчик просмотров.

**GraphQL мутация:**
```graphql
mutation {
  incrementMessageViews(messageId: 1) {
    id
    stats
    updatedAt
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "incrementMessageViews": {
      "id": 1,
      "stats": {
        "views_count": 1248,
        "likes_count": 89,
        "comments_count": 23
      },
      "updatedAt": "2026-01-25T15:45:00Z"
    }
  }
}
```

---

## Задание 15: Получение статистики пользователя
**Сложность:** ⭐⭐⭐⭐ (Сложное)

**Описание:** Создайте резолвер `get_user_statistics(user_id: int)`.

**GraphQL запрос:**
```graphql
query {
  userStatistics(userId: 1) {
    messagesCount
    commentsCount
    totalViews
  }
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "userStatistics": {
      "messagesCount": 1,
      "commentsCount": 3,
      "totalViews": 1247
    }
  }
}
```

---

## Задание 16: Комплексный запрос с переменными
**Сложность:** ⭐⭐⭐⭐⭐ (Очень сложное)

**Описание:** Создайте резолвер `get_messages_advanced` с множественными фильтрами.

**GraphQL запрос:**
```graphql
query GetMessagesAdvanced(
  $authorId: Int
  $tag: String
  $minViews: Int
  $limit: Int = 10
  $offset: Int = 0
) {
  messagesAdvanced(
    authorId: $authorId
    tag: $tag
    minViews: $minViews
    limit: $limit
    offset: $offset
  ) {
    id
    title
    authorId
    metadata
    stats
    createdAt
  }
}
```

**Переменные:**
```json
{
  "authorId": null,
  "tag": "разработка",
  "minViews": 1000,
  "limit": 5,
  "offset": 0
}
```

**Ожидаемый результат:**
```json
{
  "data": {
    "messagesAdvanced": [
      {
        "id": 6,
        "title": "ИИ в разработке: помощник или замена?",
        "authorId": 6,
        "metadata": {
          "tags": ["AI", "разработка", "будущее"],
          "reading_time": 4,
          "is_pinned": true
        },
        "stats": {
          "views_count": 1876,
          "likes_count": 134,
          "comments_count": 52
        },
        "createdAt": "2026-01-25T12:00:00Z"
      }
    ]
  }
}
```

---

## Задание 17: Полнотекстовый поиск
**Сложность:** ⭐⭐⭐⭐⭐ (Очень сложное)

**Описание:** Создайте резолвер `search_messages_fulltext(search_query: str)` с PostgreSQL FTS.

**GraphQL запрос:**
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

**Ожидаемый результат:**
```json
{
  "data": {
    "searchMessagesFulltext": [
      {
        "id": 2,
        "title": "Топ-5 инструментов для разработчиков в 2026",
        "content": "Обновил список инструментов, которые реально экономят время в 2026...",
        "authorId": 2,
        "createdAt": "2026-01-22T10:00:00Z"
      }
    ]
  }
}
```

---

## Критерии оценки

### Отлично (5):
- Выполнены все задания 1-17
- Код оптимизирован и использует лучшие практики
- Правильная обработка ошибок
- Документация и комментарии

### Хорошо (4):
- Выполнены задания 1-14
- Код работает корректно
- Базовая обработка ошибок

### Удовлетворительно (3):
- Выполнены задания 1-10
- Код работает с основными случаями
- Минимальная обработка ошибок

### Неудовлетворительно (2):
- Выполнено менее 10 заданий
- Код содержит критические ошибки

---

## Дополнительные требования

1. **Безопасность**: Используйте параметризованные запросы
2. **Производительность**: Оптимизируйте SQL запросы
3. **Обработка ошибок**: Возвращайте корректные HTTP статусы
4. **Документация**: Добавьте docstrings к функциям
5. **Тестирование**: Проверьте граничные случаи

---

## Полезные ссылки

- [GraphQL Playground](http://localhost:8000/graphql) - для тестирования запросов
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Strawberry GraphQL](https://strawberry.rocks/) - документация библиотеки
- [SQLAlchemy Core](https://docs.sqlalchemy.org/en/20/core/) - работа с базой данных