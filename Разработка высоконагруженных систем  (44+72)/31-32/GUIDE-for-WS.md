# Методичка: Добавление GraphQL Subscriptions (WebSocket) в STEP-5

## 📋 Содержание

1. [Введение](#введение)
2. [Подготовка](#подготовка)
3. [Шаг 1: Создание Pub/Sub менеджера](#шаг-1-создание-pubsub-менеджера)
4. [Шаг 2: Добавление Subscription класса](#шаг-2-добавление-subscription-класса)
5. [Шаг 3: Обновление схемы](#шаг-3-обновление-схемы)
6. [Шаг 4: Публикация событий в мутациях](#шаг-4-публикация-событий-в-мутациях)
7. [Шаг 5: Тестирование](#шаг-5-тестирование)
8. [Проверочный список](#проверочный-список)
9. [Решение проблем](#решение-проблем)

---

## Введение

### Что мы делаем?

На предыдущем занятии мы создали GraphQL API с **Query** (чтение данных) и **Mutation** (изменение данных). 
Теперь  мы добавим **Subscriptions** — возможность получать обновления в реальном времени через WebSocket.

### Зачем это нужно?

**Без Subscriptions:**
- Клиент должен постоянно опрашивать сервер: "Есть ли новые сообщения?"
- Лишняя нагрузка на сервер
- Задержка в получении данных

**С Subscriptions:**
- Сервер сам отправляет данные клиенту, когда они появляются
- Мгновенное обновление
- Эффективное использование ресурсов

### Что мы реализуем?

1. ✅ Подписка на новые сообщения канала
2. ✅ Подписка на комментарии к конкретному сообщению
3. ✅ Подписка на обновления сообщений

---

## Подготовка

### Проверьте текущее состояние

```bash

# Запустите сервер
uvicorn main:app --reload

# Откройте в браузере
# http://localhost:8000/graphql
```

**Проверка:** Выполните простой запрос:
```graphql
query {
  hello
}
```

Должен вернуться ответ: `"Hello, GraphQL!"`

### Создайте копию для приложение в отдельной папке


После подготовки у вас должна быть такая структура:

```
APP/
├── main.py              # FastAPI приложение
├── schema.py            # GraphQL схема (Query, Mutation)
├── models_graphql.py    # GraphQL типы (UserType, MessageType, CommentType)
├── user_resolvers.py    # Резолверы для пользователей
├── message_resolvers.py # Резолверы для сообщений (если есть)
├── database.py          # Настройка БД
└── requirements.txt     # Зависимости
```

---

## Шаг 1: Создание Pub/Sub менеджера

### Что такое Pub/Sub?

**Pub/Sub (Publish/Subscribe)** — паттерн, где:
- **Publisher** (издатель) публикует события в каналы
- **Subscriber** (подписчик) подписывается на каналы и получает события

**Пример:** Когда создается новое сообщение, мы публикуем событие в канал "messages". Все подписчики этого канала получат это событие.

### Создайте файл `pubsub.py`

Создайте новый файл `pubsub.py` в директории `STEP-5`:

```python
"""
Pub/Sub менеджер для GraphQL Subscriptions

Этот модуль реализует простой in-memory pub/sub механизм
для передачи событий между мутациями и подписками.
"""

from typing import AsyncIterator, Dict, List
import asyncio
from collections import defaultdict


class PubSubManager:
    """
    Менеджер публикации и подписки на события
    
    Использует in-memory хранилище для разработки.
    В production можно заменить на Redis или PostgreSQL LISTEN/NOTIFY.
    
    Пример использования:
    
    # Подписка
    async for event in pubsub.subscribe("messages"):
        print(f"Получено событие: {event}")
    
    # Публикация
    await pubsub.publish("messages", {"id": 1, "content": "Hello"})
    """
    
    def __init__(self):
        """
        Инициализация менеджера
        
        subscribers - словарь, где ключ - название канала,
        значение - список очередей (queues) для подписчиков
        """
        self.subscribers: Dict[str, List[asyncio.Queue]] = defaultdict(list)
        self._lock = asyncio.Lock()  # Блокировка для потокобезопасности
    
    async def subscribe(self, channel: str) -> AsyncIterator[dict]:
        """
        Подписаться на канал событий
        
        Параметры:
        - channel: str - название канала (например, "messages", "comments:1")
        
        Возвращает:
        - AsyncIterator[dict]: асинхронный итератор событий
        
        Использование:
        ```python
        async for event in pubsub.subscribe("messages"):
            # Обработка события
            yield event
        ```
        """
        # Создаем очередь для этого подписчика
        queue = asyncio.Queue()
        
        # Добавляем очередь в список подписчиков канала
        async with self._lock:
            self.subscribers[channel].append(queue)
        
        try:
            # Бесконечный цикл: ждем события и возвращаем их
            while True:
                message = await queue.get()
                yield message
        finally:
            # Когда подписка завершается, удаляем очередь
            async with self._lock:
                if queue in self.subscribers[channel]:
                    self.subscribers[channel].remove(queue)
    
    async def publish(self, channel: str, message: dict):
        """
        Опубликовать событие в канал
        
        Параметры:
        - channel: str - название канала
        - message: dict - данные события (будет отправлено всем подписчикам)
        
        Использование:
        ```python
        await pubsub.publish("messages", {
            "id": 1,
            "title": "Новое сообщение",
            "content": "Текст сообщения"
        })
        ```
        """
        async with self._lock:
            # Отправляем сообщение всем подписчикам канала
            disconnected = []
            for queue in self.subscribers[channel]:
                try:
                    await queue.put(message)
                except Exception:
                    # Если очередь недоступна, помечаем для удаления
                    disconnected.append(queue)
            
            # Удаляем отключенные очереди
            for queue in disconnected:
                if queue in self.subscribers[channel]:
                    self.subscribers[channel].remove(queue)


# Глобальный экземпляр менеджера
# Импортируйте его в других файлах: from pubsub import pubsub
pubsub = PubSubManager()
```

### Проверка шага 1

Создайте тестовый файл `test_pubsub.py`:

```python
import asyncio
from pubsub import pubsub

async def test_pubsub():
    """Тест pub/sub механизма"""
    
    async def subscriber():
        """Подписчик - получает события"""
        print("Подписчик: жду события...")
        async for event in pubsub.subscribe("test_channel"):
            print(f"Подписчик: получил {event}")
            break  # Получили одно событие и выходим
    
    async def publisher():
        """Издатель - отправляет события"""
        await asyncio.sleep(1)  # Ждем, пока подписчик подключится
        print("Издатель: отправляю событие...")
        await pubsub.publish("test_channel", {"message": "Hello, Pub/Sub!"})
    
    # Запускаем подписчика и издателя параллельно
    await asyncio.gather(subscriber(), publisher())

if __name__ == "__main__":
    asyncio.run(test_pubsub())
```

Запустите тест:
```bash
python test_pubsub.py
```

**Ожидаемый результат:**
```
Подписчик: жду события...
Издатель: отправляю событие...
Подписчик: получил {'message': 'Hello, Pub/Sub!'}
```

✅ **Если тест прошел успешно, переходите к шагу 2.**

---

## Шаг 2: Добавление Subscription класса

### Что такое Subscription в GraphQL?

**Subscription** — это третий тип операций в GraphQL (после Query и Mutation), который позволяет получать данные в реальном времени через WebSocket.

### Откройте файл `schema.py`

Найдите конец файла, где создается схема:

```python
# Создание схемы
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### Добавьте Subscription класс

**Перед строкой создания схемы** добавьте новый класс `Subscription`:

```python
# ============================================================================
# Subscription (подписки для real-time обновлений)
# ============================================================================

@strawberry.type
class Subscription:
    """
    Класс Subscription содержит все подписки для получения данных в реальном времени
    
    Каждый метод с декоратором @strawberry.subscription становится доступным
    в GraphQL схеме как подписка.
    
    Подписки работают через WebSocket и позволяют получать обновления
    без постоянного опроса сервера.
    """
    
    @strawberry.subscription
    async def message_added(self) -> AsyncIterator[MessageType]:
        """
        Подписка на новые сообщения канала
        
        Возвращает новые сообщения сразу после их создания.
        
        Пример GraphQL подписки:
        ```graphql
        subscription {
          messageAdded {
            id
            title
            content
            authorId
            createdAt
          }
        }
        ```
        
        Как это работает:
        1. Клиент подписывается через WebSocket
        2. Когда создается новое сообщение (через мутацию createMessage),
           оно публикуется в канал "messages"
        3. Все подписчики получают это сообщение автоматически
        """
        from pubsub import pubsub
        
        # Подписываемся на канал "messages"
        async for message_data in pubsub.subscribe("messages"):
            # Преобразуем данные в MessageType
            # message_data - это словарь с полями сообщения
            yield MessageType(**message_data)
    
    @strawberry.subscription
    async def comment_added(
        self, 
        message_id: int
    ) -> AsyncIterator[CommentType]:
        """
        Подписка на комментарии к конкретному сообщению
        
        Параметры:
        - message_id: int - ID сообщения, комментарии к которому нас интересуют
        
        Возвращает новые комментарии для указанного сообщения.
        
        Пример GraphQL подписки:
        ```graphql
        subscription {
          commentAdded(messageId: 1) {
            id
            content
            authorId
            createdAt
          }
        }
        ```
        
        Как это работает:
        1. Клиент указывает message_id при подписке
        2. Создается канал "comments:{message_id}" (например, "comments:1")
        3. Когда создается комментарий к этому сообщению,
           он публикуется в соответствующий канал
        4. Только подписчики этого канала получают событие
        """
        from pubsub import pubsub
        
        # Формируем название канала на основе message_id
        channel = f"comments:{message_id}"
        
        # Подписываемся на канал комментариев для этого сообщения
        async for comment_data in pubsub.subscribe(channel):
            # Преобразуем данные в CommentType
            yield CommentType(**comment_data)
    
    @strawberry.subscription
    async def message_updated(
        self,
        message_id: int | None = None
    ) -> AsyncIterator[MessageType]:
        """
        Подписка на обновления сообщений
        
        Параметры:
        - message_id: int | None - ID конкретного сообщения (опционально)
          Если не указан, подписка на все сообщения
        
        Возвращает обновленные сообщения.
        
        Пример GraphQL подписки (все сообщения):
        ```graphql
        subscription {
          messageUpdated {
            id
            title
            content
            updatedAt
          }
        }
        ```
        
        Пример GraphQL подписки (конкретное сообщение):
        ```graphql
        subscription {
          messageUpdated(messageId: 1) {
            id
            title
            content
            updatedAt
          }
        }
        ```
        """
        from pubsub import pubsub
        
        # Формируем название канала
        if message_id:
            channel = f"message_updates:{message_id}"
        else:
            channel = "message_updates:all"
        
        # Подписываемся на канал обновлений
        async for message_data in pubsub.subscribe(channel):
            yield MessageType(**message_data)
```

### Добавьте импорт AsyncIterator

В начале файла `schema.py` добавьте импорт:

```python
from typing import AsyncIterator  # Добавьте это
```

Теперь в начале файла должно быть:

```python
from __future__ import annotations

import strawberry
from typing import Any, AsyncIterator  # Добавлен AsyncIterator
from datetime import datetime
# ... остальные импорты
```

### Проверка шага 2

Убедитесь, что код компилируется без ошибок:

```bash
python -m py_compile schema.py
```

✅ **Если ошибок нет, переходите к шагу 3.**

---

## Шаг 3: Обновление схемы

### Обновите создание схемы

В конце файла `schema.py` найдите строку:

```python
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

Замените на:

```python
# Создаем финальную GraphQL схему, объединяя Query, Mutation и Subscription
schema = strawberry.Schema(
    query=Query,           # Запросы для чтения данных
    mutation=Mutation,     # Мутации для изменения данных
    subscription=Subscription  # Подписки для real-time обновлений
)
```

### Проверка шага 3

Запустите сервер:

```bash
uvicorn main:app --reload
```

Откройте GraphQL Playground: `http://localhost:8000/graphql`

В левой панели (Schema) вы должны увидеть новый тип `Subscription` с полями:
- `messageAdded`
- `commentAdded(messageId: Int!)`
- `messageUpdated(messageId: Int)`

✅ **Если Subscription виден в схеме, переходите к шагу 4.**

---

## Шаг 4: Публикация событий в мутациях

### Где публиковать события?

События нужно публиковать в тех местах, где происходят изменения:
- При создании сообщения → публикуем в "messages"
- При создании комментария → публикуем в "comments:{message_id}"
- При обновлении сообщения → публикуем в "message_updates:all" и "message_updates:{message_id}"

### Обновление мутации create_message

**Найдите файл с мутациями для сообщений.** Это может быть:
- `message_resolvers.py` (если есть)
- Или прямо в `schema.py` в классе `Mutation`

**Если мутации в `schema.py`:**

Найдите метод `create_message` в классе `Mutation`:

```python
@strawberry.mutation
async def create_message(...) -> MessageType:
    # ... существующий код создания сообщения ...
    return new_message
```

**Добавьте публикацию события после создания:**

```python
@strawberry.mutation
async def create_message(
    self,
    author_id: int,
    content: str,
    title: str | None = None,
    metadata: JSON | None = None,
    stats: JSON | None = None
) -> MessageType:
    """
    Создать новое сообщение
    """
    from message_resolvers import create_message as create_message_resolver
    from pubsub import pubsub
    
    # Создаем сообщение (существующий код)
    new_message = await create_message_resolver(
        author_id, content, title, metadata, stats
    )
    
    # Публикуем событие для подписчиков
    await pubsub.publish("messages", {
        "id": new_message.id,
        "author_id": new_message.author_id,
        "title": new_message.title,
        "content": new_message.content,
        "metadata": new_message.metadata,
        "stats": new_message.stats,
        "created_at": new_message.created_at,
        "updated_at": new_message.updated_at,
    })
    
    return new_message
```

**Если мутации в `message_resolvers.py`:**

Откройте файл `message_resolvers.py` и найдите функцию `create_message`:

```python
async def create_message(...) -> MessageType:
    # ... код создания ...
    return new_message
```

**Добавьте публикацию в конце функции:**

```python
async def create_message(...) -> MessageType:
    # ... существующий код создания сообщения ...
    
    # Публикуем событие для подписчиков
    from pubsub import pubsub
    await pubsub.publish("messages", {
        "id": new_message.id,
        "author_id": new_message.author_id,
        "title": new_message.title,
        "content": new_message.content,
        "metadata": new_message.metadata,
        "stats": new_message.stats,
        "created_at": new_message.created_at,
        "updated_at": new_message.updated_at,
    })
    
    return new_message
```

### Обновление мутации create_comment

**Найдите функцию создания комментария** и добавьте публикацию:

```python
async def create_comment(...) -> CommentType:
    # ... код создания комментария ...
    
    # Публикуем событие для подписчиков этого сообщения
    from pubsub import pubsub
    channel = f"comments:{new_comment.message_id}"
    await pubsub.publish(channel, {
        "id": new_comment.id,
        "message_id": new_comment.message_id,
        "author_id": new_comment.author_id,
        "parent_comment_id": new_comment.parent_comment_id,
        "content": new_comment.content,
        "metadata": new_comment.metadata,
        "reactions": new_comment.reactions,
        "created_at": new_comment.created_at,
        "updated_at": new_comment.updated_at,
    })
    
    return new_comment
```

### Обновление мутации update_message

**Найдите функцию обновления сообщения:**

```python
async def update_message(...) -> MessageType | None:
    # ... код обновления ...
    
    if updated_message:
        from pubsub import pubsub
        
        # Публикуем в канал для всех сообщений
        await pubsub.publish("message_updates:all", {
            "id": updated_message.id,
            "author_id": updated_message.author_id,
            "title": updated_message.title,
            "content": updated_message.content,
            "metadata": updated_message.metadata,
            "stats": updated_message.stats,
            "created_at": updated_message.created_at,
            "updated_at": updated_message.updated_at,
        })
        
        # Публикуем в канал для конкретного сообщения
        await pubsub.publish(f"message_updates:{updated_message.id}", {
            "id": updated_message.id,
            "author_id": updated_message.author_id,
            "title": updated_message.title,
            "content": updated_message.content,
            "metadata": updated_message.metadata,
            "stats": updated_message.stats,
            "created_at": updated_message.created_at,
            "updated_at": updated_message.updated_at,
        })
    
    return updated_message
```

### Важно: Преобразование datetime

Если у вас возникают ошибки с `datetime`, преобразуйте его в строку:

```python
# Вместо:
"created_at": new_message.created_at,

# Используйте:
"created_at": new_message.created_at.isoformat() if hasattr(new_message.created_at, 'isoformat') else new_message.created_at,
```

Или создайте вспомогательную функцию:

```python
# В pubsub.py или в начале файла с резолверами
def message_to_dict(message: MessageType) -> dict:
    """Преобразует MessageType в словарь для публикации"""
    return {
        "id": message.id,
        "author_id": message.author_id,
        "title": message.title,
        "content": message.content,
        "metadata": message.metadata,
        "stats": message.stats,
        "created_at": message.created_at.isoformat() if hasattr(message.created_at, 'isoformat') else message.created_at,
        "updated_at": message.updated_at.isoformat() if hasattr(message.updated_at, 'isoformat') else message.updated_at,
    }
```

И в Subscription преобразуйте обратно:

```python
@strawberry.subscription
async def message_added(self) -> AsyncIterator[MessageType]:
    from pubsub import pubsub
    from datetime import datetime
    
    async for message_data in pubsub.subscribe("messages"):
        # Преобразуем строки обратно в datetime
        if isinstance(message_data.get("created_at"), str):
            message_data["created_at"] = datetime.fromisoformat(message_data["created_at"])
        if isinstance(message_data.get("updated_at"), str):
            message_data["updated_at"] = datetime.fromisoformat(message_data["updated_at"])
        
        yield MessageType(**message_data)
```

### Проверка шага 4

Убедитесь, что код компилируется:

```bash
python -m py_compile schema.py
python -m py_compile message_resolvers.py  # если есть
```

✅ **Если ошибок нет, переходите к шагу 5.**

---

## Шаг 5: Тестирование

### Тест 1: Проверка схемы

1. Запустите сервер:
   ```bash
   uvicorn main:app --reload
   ```

2. Откройте GraphQL Playground: `http://localhost:8000/graphql`

3. В левой панели нажмите на "Schema" и проверьте наличие:
   - `Subscription` типа
   - Поля `messageAdded`
   - Поля `commentAdded(messageId: Int!)`
   - Поля `messageUpdated(messageId: Int)`

### Тест 2: Подписка на новые сообщения

**В GraphQL Playground:**

1. Откройте вкладку "Subscriptions" (если доступна) или используйте обычный редактор

2. Введите подписку:
   ```graphql
   subscription {
     messageAdded {
       id
       title
       content
       authorId
       createdAt
     }
   }
   ```

3. Нажмите "Play" (▶️)

4. **В другом окне браузера или вкладке** откройте тот же Playground

5. Выполните мутацию создания сообщения:
   ```graphql
   mutation {
     createMessage(
       authorId: 1
       title: "Тестовое сообщение"
       content: "Это сообщение должно появиться в подписке!"
     ) {
       id
       title
     }
   }
   ```

6. **Проверьте:** В первом окне (с подпиской) должно появиться новое сообщение автоматически!

### Тест 3: Подписка на комментарии

1. В первом окне создайте подписку:
   ```graphql
   subscription {
     commentAdded(messageId: 1) {
       id
       content
       authorId
       createdAt
     }
   }
   ```

2. Во втором окне создайте комментарий:
   ```graphql
   mutation {
     createComment(
       messageId: 1
       authorId: 1
       content: "Новый комментарий!"
     ) {
       id
       content
     }
   }
   ```

3. **Проверьте:** Комментарий должен появиться в подписке!

### Тест 4: Использование Apollo Studio Sandbox

Если GraphQL Playground не поддерживает subscriptions, используйте Apollo Studio Sandbox:

1. Установите (или используйте через npx):
   ```bash
   npx @apollo/sandbox
   ```

2. Введите endpoint: `http://localhost:8000/graphql`

3. Создайте подписку и протестируйте так же, как выше

### Ожидаемый результат

✅ Подписки работают и получают события в реальном времени  
✅ Новые сообщения появляются автоматически у всех подписчиков  
✅ Комментарии приходят только подписчикам соответствующего сообщения  

---

## Проверочный список

Пройдитесь по этому списку и убедитесь, что все выполнено:

### Файлы
- [ ] Создан файл `pubsub.py` с классом `PubSubManager`
- [ ] В `schema.py` добавлен класс `Subscription`
- [ ] В `schema.py` обновлена строка создания схемы (добавлен `subscription=Subscription`)
- [ ] В мутациях добавлена публикация событий

### Код
- [ ] Импортирован `AsyncIterator` в `schema.py`
- [ ] Импортирован `pubsub` в нужных местах
- [ ] События публикуются при создании сообщений
- [ ] События публикуются при создании комментариев
- [ ] События публикуются при обновлении сообщений

### Тестирование
- [ ] Сервер запускается без ошибок
- [ ] Subscription виден в GraphQL схеме
- [ ] Подписка на новые сообщения работает
- [ ] Подписка на комментарии работает
- [ ] События приходят в реальном времени

---

## Решение проблем

### Проблема 1: "ModuleNotFoundError: No module named 'pubsub'"

**Решение:**
- Убедитесь, что файл `pubsub.py` находится в той же директории, что и `schema.py`
- Проверьте, что вы импортируете правильно: `from pubsub import pubsub`

### Проблема 2: "TypeError: Object of type datetime is not JSON serializable"

**Решение:**
- Преобразуйте `datetime` в строку перед публикацией:
  ```python
  "created_at": message.created_at.isoformat()
  ```
- И преобразуйте обратно в Subscription:
  ```python
  from datetime import datetime
  message_data["created_at"] = datetime.fromisoformat(message_data["created_at"])
  ```

### Проблема 3: "Subscription не виден в схеме"

**Решение:**
- Проверьте, что вы добавили `subscription=Subscription` в `strawberry.Schema()`
- Перезапустите сервер
- Очистите кеш браузера

### Проблема 4: "Подписка не получает события"

**Решение:**
- Убедитесь, что вы публикуете события в правильный канал
- Проверьте, что публикация происходит **после** успешного создания/обновления
- Добавьте логирование для отладки:
  ```python
  print(f"Публикую событие в канал: {channel}")
  await pubsub.publish(channel, message_data)
  print(f"Событие опубликовано: {message_data}")
  ```

### Проблема 5: "GraphQL Playground не поддерживает subscriptions"

**Решение:**
- Используйте Apollo Studio Sandbox: `npx @apollo/sandbox`
- Или используйте клиент на JavaScript (см. пример ниже)

### Проблема 6: "Ошибка при преобразовании данных в MessageType"

**Решение:**
- Убедитесь, что все поля из БД присутствуют в словаре
- Проверьте типы данных (особенно datetime)
- Добавьте обработку None значений:
  ```python
  yield MessageType(
      id=message_data.get("id"),
      author_id=message_data.get("author_id"),
      title=message_data.get("title"),
      content=message_data.get("content"),
      # ... остальные поля
  )
  ```

---

## Дополнительные материалы

### Пример клиента на JavaScript

Если хотите протестировать подписки из веб-приложения:

```javascript
// Установите: npm install @apollo/client graphql ws

import { ApolloClient, InMemoryCache, split, HttpLink } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';

// HTTP ссылка для Query и Mutation
const httpLink = new HttpLink({
  uri: 'http://localhost:8000/graphql',
});

// WebSocket ссылка для Subscriptions
const wsLink = new GraphQLWsLink(createClient({
  url: 'ws://localhost:8000/graphql',
}));

// Разделяем ссылки: HTTP для запросов, WebSocket для подписок
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink,
);

// Создаем клиент
const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});

// Использование подписки
import { gql } from '@apollo/client';

const MESSAGE_ADDED = gql`
  subscription {
    messageAdded {
      id
      title
      content
      authorId
      createdAt
    }
  }
`;

client.subscribe({ query: MESSAGE_ADDED }).subscribe({
  next: (data) => {
    console.log('Новое сообщение:', data.data.messageAdded);
  },
  error: (err) => {
    console.error('Ошибка подписки:', err);
  },
});
```

---

## Итоги

После выполнения всех шагов вы должны иметь:

✅ **Работающий Pub/Sub механизм** для передачи событий  
✅ **GraphQL Subscriptions** для real-time обновлений  
✅ **Интеграцию** между мутациями и подписками  
✅ **Работающие подписки** на новые сообщения и комментарии  

### Что дальше?

1. **Добавьте больше подписок:**
   - Подписка на удаление сообщений
   - Подписка на обновления пользователей
   - Подписка на реакции к комментариям

2. **Улучшите производительность:**
   - Замените in-memory pub/sub на Redis
   - Добавьте фильтрацию событий
   - Реализуйте rate limiting для подписок

3. **Добавьте авторизацию:**
   - Проверяйте права доступа при подписке
   - Фильтруйте события по правам пользователя

---

**Удачи в реализации! 🚀**

*Если возникли вопросы, можно посмотреть документацию Strawberry: https://strawberry.rocks/docs/guides/subscriptions*

