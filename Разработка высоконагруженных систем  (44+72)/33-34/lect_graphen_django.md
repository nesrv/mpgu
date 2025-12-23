# Презентация: Построение API на Django
## REST, GraphQL и новые возможности Django 6.0

---
## Слайд 1: Новые возможности Django 6.0

**Основные нововведения:**

| Возможность | Описание | Пример использования | Преимущества |
|-------------|----------|---------------------|--------------|
| **Template Partials** | Модуляризация шаблонов с помощью небольших именованных фрагментов | `{% partial "header" %}` | Более чистый и поддерживаемый код шаблонов |
| **Background Tasks** | Встроенный фреймворк для выполнения задач вне HTTP request-response цикла | `@background_task` | Гибкая система фоновых задач без внешних зависимостей |
| **Content Security Policy (CSP)** | Встроенная поддержка настройки и применения политик безопасности браузера | `CSP_MIDDLEWARE` | Защита от атак инъекции контента на уровне браузера |
| **Modernized Email API** | Использование Python `EmailMessage` для составления и отправки email | `EmailMessage()` | Более чистый, Unicode-friendly интерфейс |


## Слайд 2: Background Tasks

**Что это?**
Встроенный фреймворк для выполнения фоновых задач без внешних зависимостей (Celery, RQ).

**Пример использования:**
```python
from django.tasks import background_task

@background_task
def send_notification_email(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(
        subject='Notification',
        message=message,
        from_email='noreply@example.com',
        recipient_list=[user.email],
    )

# Вызов задачи
send_notification_email.delay(user.id, "Welcome!")
```

**Преимущества:**
- ✅ Не требует внешних зависимостей
- ✅ Простая настройка
- ✅ Интеграция с Django ORM
- ✅ Поддержка отложенных задач

**Настройка:**
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.tasks',  # Новое приложение
    # ...
]

# Настройка брокера (Redis, RabbitMQ и т.д.)
TASK_BROKER = 'redis://localhost:6379/0'
```
## Слайд 3: Другие улучшения Django 6.0

| Область | Улучшение | Описание |
|---------|-----------|----------|
| **ORM** | Улучшенные запросы | Оптимизация `select_related()` и `prefetch_related()` |
| **Admin** | Новый UI компонент | Улучшенный интерфейс админ-панели |
| **Forms** | Валидация | Расширенные возможности валидации форм |
| **Security** | Улучшенная защита | Дополнительные меры безопасности по умолчанию |
| **Performance** | Оптимизации | Улучшения производительности запросов |

## Слайд 4: Сравнение API фреймворков для Django

Вот сравнительная таблица построения API в **Django** с использованием различных подходов и фреймворков: от «голого» Django до GraphQL и современных инструментов.

| Критерий / Подход                     | **Django REST Framework (DRF)**                     | **Django Ninja**                           | **Tastypie** (устаревший)               | **Graphene-Django** (GraphQL)          | **Strawberry + Django** (GraphQL)      |
|--------------------------------------|----------------------------------------------------|-------------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------|
| **Тип API**                          | REST                                               | REST                                      | REST                                   | GraphQL                                | GraphQL                                |
| **Основная цель**                    | Мощный, гибкий REST API                            | Быстрый, простой REST API с типизацией    | Устаревшая альтернатива DRF            | GraphQL поверх Django                   | Современный GraphQL с нативной типизацией |
| **Типизация (type hints)**          | Частичная (через сериализаторы)                    | ✅ Полная поддержка (`@api.get`, Pydantic-стиль) | ❌ Нет                                 | ❌ Собственные классы (`ObjectType`)    | ✅ Нативные Python-типы (`@strawberry.type`) |
| **Производительность**              | Хорошая, но может быть «тяжёлой» для простых задач | ⚡ Очень высокая (лёгкий фреймворк)       | Низкая / устаревшая                    | Средняя                                | Высокая (особенно с async)             |
| **Асинхронность**                   | Ограниченная (DRF + async views — экспериментально) | ✅ Полная поддержка `async/await`         | ❌ Нет                                 | ❌ Минимальная                         | ✅ Полная поддержка (включая subscriptions) |
| **Автоматическая документация**     | ✅ Swagger/OpenAPI через `drf-spectacular`         | ✅ Встроенная OpenAPI UI                  | ❌ Нет                                 | ✅ GraphiQL                            | ✅ GraphiQL                            |
| **Интеграция с моделями Django**    | ✅ Через `ModelSerializer`                         | ✅ Через Pydantic-модели или вручную      | ✅ Через `ModelResource`               | ✅ Автоматическая генерация из моделей | ✅ Вручную или через `@strawberry.django.type` |
| **Сложность освоения**              | Средняя (много концепций: ViewSets, Serializers…) | Низкая (похоже на FastAPI)                | Высокая (устаревший синтаксис)        | Средняя                                | Низкая–средняя (если знаете GraphQL)   |
| **Поддержка и развитие**            | ✅ Активно поддерживается                          | ✅ Активно (автор — создатель Django)     | ❌ Не поддерживается                   | ⚠️ Поддерживается, но медленно         | ✅ Активно развивается                  |
| **Лучше подходит для**              | Сложных REST API, enterprise-проектов             | Быстрых MVP, микросервисов, легких API    | Поддержка старых проектов              | Гибких запросов, клиентских приложений | Современных GraphQL-сервисов с типизацией |

---

### Краткие рекомендации:

- **Нужен классический REST API?**
  - ✅ **Django Ninja** — если хотите быстро, просто и с типизацией (как FastAPI, но в Django).
  - ✅ **DRF** — если нужна максимальная гибкость, авторизация, пагинация «из коробки», интеграции.

- **Нужен GraphQL?**
  - ✅ **Strawberry + Django** — для новых проектов, особенно если важна типизация и async.
  - ⚠️ **Graphene-Django** — если уже используете его или нужна автоматическая генерация из моделей.

- **Избегайте** `Tastypie` — он устарел и не поддерживается.

---



## Слайд 5: Введение в Graphene

**Graphene** - это библиотека для создания GraphQL API в Python. Разработана специально для Django, но может работать и с другими фреймворками.

**Почему Graphene?**
- Нативная интеграция с Django ORM
- Автоматическая генерация схемы из моделей
- Type-safe с помощью Python type hints
- Поддержка всех возможностей GraphQL (Queries, Mutations, Subscriptions)
- Активное сообщество и хорошая документация

**Альтернативы:**
- Strawberry GraphQL (современная, с type hints)
- Ariadne (code-first подход)
- Tartiflette (async-first)

Graphene - самый популярный выбор для Django проектов.

---

## Слайд 6: Сравнение Strawberry и Graphene

**Graphene vs Strawberry GraphQL** - два основных выбора для GraphQL в Python.

### Graphene

**Преимущества:**
- ✅ Зрелая библиотека (с 2015 года)
- ✅ Отличная интеграция с Django ORM
- ✅ Большое сообщество и много примеров
- ✅ `DjangoObjectType` автоматически создает типы из моделей
- ✅ Много готовых решений и плагинов
- ✅ Хорошая документация

**Недостатки:**
- ❌ Менее современный синтаксис
- ❌ Type hints не обязательны (меньше проверок)
- ❌ Больше boilerplate кода
- ❌ Медленнее в разработке (больше кода)

**Пример кода:**
```python
import graphene
from graphene_django import DjangoObjectType
from .models import Post

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = '__all__'

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    
    def resolve_posts(self, info):
        return Post.objects.all()
```

### Strawberry GraphQL

**Преимущества:**
- ✅ Современный синтаксис с декораторами
- ✅ Обязательные type hints (лучше IDE поддержка)
- ✅ Меньше кода, более читаемо
- ✅ Лучшая производительность
- ✅ Async/await из коробки
- ✅ Автоматическая валидация типов

**Недостатки:**
- ❌ Моложе (с 2020 года)
- ❌ Меньше примеров и документации
- ❌ Меньше готовых решений
- ❌ Интеграция с Django требует больше настройки

**Пример кода:**
```python
import strawberry
from typing import List
from .models import Post

@strawberry.django.type(Post)
class PostType:
    id: strawberry.ID
    title: str
    content: str

@strawberry.type
class Query:
    @strawberry.field
    def posts(self) -> List[PostType]:
        return Post.objects.all()
```

### Сравнительная таблица

| Критерий | Graphene | Strawberry |
|----------|----------|------------|
| **Возраст** | 2015 (зрелая) | 2020 (молодая) |
| **Синтаксис** | Классический | Современный (декораторы) |
| **Type hints** | Опциональные | Обязательные |
| **Django интеграция** | Отличная | Хорошая |
| **Производительность** | Хорошая | Лучше |
| **Async поддержка** | Частичная | Полная |
| **Сообщество** | Большое | Растущее |
| **Документация** | Отличная | Хорошая |
| **Boilerplate** | Больше | Меньше |

### Когда выбирать?

**Выбирайте Graphene, если:**
- Работаете с Django проектом
- Нужна максимальная совместимость
- Важна зрелость библиотеки
- Нужно много примеров и решений
- Команда уже знакома с Graphene

**Выбирайте Strawberry, если:**
- Нужен современный синтаксис
- Важна производительность
- Нужна полная async поддержка
- Хотите меньше boilerplate кода
- Готовы к меньшей документации

**Вывод:** Graphene - безопасный выбор для Django, Strawberry - современная альтернатива для новых проектов.

---

## Слайд 7: Установка и настройка

**Установка:**
```bash
pip install graphene-django django-filter
```

**Настройка в settings.py:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'graphene_django',  # Добавляем Graphene
    'myapp',
]

# Настройка GraphQL
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema',
    'MIDDLEWARE': [
        'graphene_django.ext.django_jwt.middleware.JSONWebTokenMiddleware',
    ],
}
```

**URL конфигурация:**
```python
# urls.py
from django.urls import path
from graphene_django.views import GraphQLView

urlpatterns = [
    path('graphql/', GraphQLView.as_view(graphiql=True)),
]
```

`graphiql=True` включает интерактивную IDE для тестирования запросов.

---

## Слайд 8: Структура проекта

**Рекомендуемая структура:**
```
myproject/
├── myapp/
│   ├── models.py          # Django модели
│   ├── schema.py          # GraphQL схема
│   ├── types.py           # GraphQL типы
│   ├── queries.py         # Query классы
│   ├── mutations.py       # Mutation классы
│   └── subscriptions.py   # Subscription классы
├── settings.py
└── urls.py
```

**Основные компоненты:**
- **Types** - соответствуют Django моделям
- **Queries** - операции чтения данных
- **Mutations** - операции изменения данных
- **Schema** - объединяет всё вместе

---

## Слайд 9: Django модель

**Пример модели:**
```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
```

Это стандартная Django модель. Graphene автоматически может создать GraphQL тип из модели, но лучше делать это вручную для контроля.

---

## Слайд 10: Создание GraphQL типа

**Базовый тип из модели:**
```python
# types.py
import graphene
from graphene_django import DjangoObjectType
from .models import Post

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'created_at', 'published')
```

**DjangoObjectType** автоматически:
- Создает GraphQL тип из Django модели
- Маппит поля модели на GraphQL поля
- Поддерживает связи (ForeignKey, ManyToMany)

**Доступные опции Meta:**
- `model` - Django модель
- `fields` - какие поля включить
- `exclude` - какие поля исключить
- `filter_fields` - поля для фильтрации
- `interfaces` - GraphQL интерфейсы

---

## Слайд 11: Кастомизация типов

**Добавление вычисляемых полей:**
```python
class PostType(DjangoObjectType):
    word_count = graphene.Int()
    excerpt = graphene.String()
    
    class Meta:
        model = Post
        fields = '__all__'
    
    def resolve_word_count(self, info):
        return len(self.content.split())
    
    def resolve_excerpt(self, info):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content
```

**Добавление связей:**
```python
class PostType(DjangoObjectType):
    comments = graphene.List('myapp.types.CommentType')
    
    class Meta:
        model = Post
    
    def resolve_comments(self, info):
        return self.comments.all()
```

Resolvers позволяют добавлять любую логику для получения данных.

---

## Слайд 12: Типы для User

**Создание типа для Django User:**
```python
# types.py
from django.contrib.auth.models import User
import graphene
from graphene_django import DjangoObjectType

class UserType(DjangoObjectType):
    posts = graphene.List('myapp.types.PostType')
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        # Исключаем чувствительные поля
    
    def resolve_posts(self, info):
        return self.post_set.all()
```

**Важно:** Не включайте `password` и другие чувствительные поля в GraphQL тип!

---

## Слайд 13: Базовый Query

**Создание Query класса:**
```python
# queries.py
import graphene
from graphene_django import DjangoObjectType
from .models import Post
from .types import PostType

class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    
    def resolve_posts(self, info):
        return Post.objects.all()
    
    def resolve_post(self, info, id):
        return Post.objects.get(id=id)
```

**Использование:**
```graphql
query {
  posts {
    id
    title
    content
  }
  
  post(id: 1) {
    title
    author {
      username
    }
  }
}
```

---

## Слайд 14: Фильтрация и пагинация

**Фильтрация с django-filter:**
```python
# types.py
import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from .models import Post

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = {
            'title': ['exact', 'icontains'],
            'published': ['exact'],
            'created_at': ['gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)

# queries.py
class Query(graphene.ObjectType):
    posts = DjangoFilterConnectionField(PostType)
```

**Использование:**
```graphql
query {
  posts(title_Icontains: "Django", published: true) {
    edges {
      node {
        title
        content
      }
    }
  }
}
```

---

## Слайд 15: Пагинация (Relay Connection)

**Relay Connection для пагинации:**
```python
# queries.py
import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from .types import PostType

class Query(graphene.ObjectType):
    posts = relay.ConnectionField(PostType)
    
    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()
```

**Использование:**
```graphql
query {
  posts(first: 10, after: "YXJyYXljb25uZWN0aW9uOjk=") {
    edges {
      node {
        title
        content
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

Это стандартный подход для пагинации в GraphQL.

---

## Слайд 16: Авторизация в Query

**Проверка авторизации:**
```python
# queries.py
import graphene
from django.contrib.auth.models import User
from .types import UserType, PostType

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    my_posts = graphene.List(PostType)
    
    def resolve_me(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication required')
        return user
    
    def resolve_my_posts(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication required')
        return Post.objects.filter(author=user)
```

**info.context.user** содержит текущего пользователя из Django сессии или JWT токена.

---

## Слайд 17: Базовый Mutation

**Создание Mutation:**
```python
# mutations.py
import graphene
from graphene_django import DjangoObjectType
from .models import Post
from .types import PostType

class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        published = graphene.Boolean()
    
    post = graphene.Field(PostType)
    success = graphene.Boolean()
    
    def mutate(self, info, title, content, published=False):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication required')
        
        post = Post.objects.create(
            title=title,
            content=content,
            author=user,
            published=published
        )
        
        return CreatePost(post=post, success=True)

class Mutation(graphene.ObjectType):
    create_post = CreatePost.Field()
```

---

## Слайд 18: Input типы для Mutations

**Использование Input типов:**
```python
# mutations.py
import graphene
from graphene_django import DjangoObjectType
from .models import Post
from .types import PostType

class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    published = graphene.Boolean()

class CreatePost(graphene.Mutation):
    class Arguments:
        input = PostInput(required=True)
    
    post = graphene.Field(PostType)
    
    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception('Authentication required')
        
        post = Post.objects.create(
            title=input.title,
            content=input.content,
            author=user,
            published=input.get('published', False)
        )
        
        return CreatePost(post=post)
```

Input типы делают мутации более читаемыми и переиспользуемыми.

---

## Слайд 19: Update и Delete Mutations

**Update Mutation:**
```python
class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        input = PostInput()
    
    post = graphene.Field(PostType)
    
    def mutate(self, info, id, input):
        user = info.context.user
        post = Post.objects.get(id=id)
        
        # Проверка прав
        if post.author != user:
            raise Exception('Permission denied')
        
        # Обновление полей
        for key, value in input.items():
            setattr(post, key, value)
        post.save()
        
        return UpdatePost(post=post)
```

**Delete Mutation:**
```python
class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, id):
        user = info.context.user
        post = Post.objects.get(id=id)
        
        if post.author != user:
            raise Exception('Permission denied')
        
        post.delete()
        return DeletePost(success=True)
```

---

## Слайд 20: Обработка ошибок в Mutations

**Кастомные исключения:**
```python
# exceptions.py
class GraphQLError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

# mutations.py
from .exceptions import GraphQLError

class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
    
    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, title, content):
        errors = []
        
        if not title or len(title) < 3:
            errors.append('Title must be at least 3 characters')
        
        if not content or len(content) < 10:
            errors.append('Content must be at least 10 characters')
        
        if errors:
            return CreatePost(errors=errors)
        
        user = info.context.user
        post = Post.objects.create(
            title=title,
            content=content,
            author=user
        )
        
        return CreatePost(post=post, errors=[])
```

---

## Слайд 21: Объединение Schema

**Создание главной схемы:**
```python
# schema.py
import graphene
from .queries import Query
from .mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
```

**Если есть Subscriptions:**
```python
# schema.py
import graphene
from .queries import Query
from .mutations import Mutation
from .subscriptions import Subscription

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
```

**В settings.py:**
```python
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema',
}
```

---

## Слайд 22: Subscriptions (WebSocket)

**Настройка для Subscriptions:**
```bash
pip install channels channels-redis
```

**settings.py:**
```python
INSTALLED_APPS = [
    'channels',
    'graphene_django',
    # ...
]

ASGI_APPLICATION = 'myproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

**asgi.py:**
```python
from channels.routing import ProtocolTypeRouter, URLRouter
from graphene_subscriptions.consumers import GraphqlSubscriptionConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        path("graphql/", GraphqlSubscriptionConsumer),
    ]),
})
```

---

## Слайд 23: Создание Subscription

**Пример Subscription:**
```python
# subscriptions.py
import graphene
from graphene_subscriptions.events import CREATED, UPDATED, DELETED
from .types import PostType

class PostSubscription(graphene.ObjectType):
    post_created = graphene.Field(PostType)
    post_updated = graphene.Field(PostType)
    post_deleted = graphene.Int()
    
    def resolve_post_created(root, info):
        return root.filter(
            lambda event: event.operation == CREATED and
            isinstance(event.instance, Post)
        ).map(lambda event: event.instance)
    
    def resolve_post_updated(root, info):
        return root.filter(
            lambda event: event.operation == UPDATED and
            isinstance(event.instance, Post)
        ).map(lambda event: event.instance)
```

---

## Слайд 24: Отправка событий в Mutations

**Отправка событий:**
```python
# mutations.py
from graphene_subscriptions.events import CREATED, UPDATED
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CreatePost(graphene.Mutation):
    # ... код создания поста ...
    
    def mutate(self, info, title, content):
        post = Post.objects.create(...)
        
        # Отправка события
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "posts",
            {
                "type": "post.created",
                "event": {
                    "operation": CREATED,
                    "instance": post,
                }
            }
        )
        
        return CreatePost(post=post)
```

---

## Слайд 25: Middleware

**Создание кастомного middleware:**
```python
# middleware.py
class AuthMiddleware:
    def resolve(self, next, root, info, **args):
        # Проверка авторизации перед каждым resolver
        if not info.context.user.is_authenticated:
            raise Exception('Authentication required')
        return next(root, info, **args)

# settings.py
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema',
    'MIDDLEWARE': [
        'myapp.middleware.AuthMiddleware',
    ],
}
```

**Встроенные middleware:**
- `JSONWebTokenMiddleware` - для JWT токенов
- `DjangoDebugMiddleware` - для отладки

---

## Слайд 26: Оптимизация запросов (N+1)

**Проблема N+1:**
```python
# Плохо - N+1 запросов
class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    
    def resolve_posts(self, info):
        return Post.objects.all()  # Для каждого поста отдельный запрос автора
```

**Решение - select_related и prefetch_related:**
```python
# Хорошо - 2 запроса
class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    
    def resolve_posts(self, info):
        return Post.objects.select_related('author').prefetch_related('comments').all()
```

**DataLoader для сложных случаев:**
```python
from promise import Promise
from promise.dataloader import DataLoader

class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        users = User.objects.in_bulk(keys)
        return [users.get(key) for key in keys]
```

---

## Слайд 27: Тестирование GraphQL

**Тестирование с Django TestCase:**
```python
# tests.py
from django.test import TestCase
from graphene.test import Client
from .schema import schema
from .models import Post

class PostQueryTest(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content'
        )
    
    def test_posts_query(self):
        query = '''
        query {
            posts {
                id
                title
            }
        }
        '''
        result = self.client.execute(query)
        self.assertEqual(len(result['data']['posts']), 1)
        self.assertEqual(result['data']['posts'][0]['title'], 'Test Post')
```

---

## Слайд 28: Тестирование Mutations

**Тестирование мутаций:**
```python
class PostMutationTest(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_create_post(self):
        mutation = '''
        mutation {
            createPost(input: {
                title: "New Post"
                content: "Post Content"
            }) {
                post {
                    id
                    title
                }
            }
        }
        '''
        # Авторизация
        context = {'user': self.user}
        result = self.client.execute(mutation, context_value=context)
        
        self.assertTrue(result['data']['createPost']['post'])
        self.assertEqual(result['data']['createPost']['post']['title'], 'New Post')
```

---

## Слайд 29: JWT аутентификация

**Установка:**
```bash
pip install django-graphql-jwt
```

**Настройка:**
```python
# settings.py
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

**Добавление мутаций:**
```python
# mutations.py
import graphene
import graphql_jwt

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    # ... другие мутации
```

---

## Слайд 30: Использование JWT

**Получение токена:**
```graphql
mutation {
  tokenAuth(username: "user", password: "pass") {
    token
  }
}
```

**Использование токена:**
```javascript
// В заголовках запроса
headers: {
  'Authorization': 'JWT <token>'
}
```

**В Python клиенте:**
```python
import requests

query = '''
query {
  me {
    username
    email
  }
}
'''

response = requests.post(
    'http://localhost:8000/graphql/',
    json={'query': query},
    headers={'Authorization': 'JWT <token>'}
)
```

---

## Слайд 31: Файловые загрузки

**Установка:**
```bash
pip install graphene-file-upload
```

**Настройка:**
```python
# urls.py
from graphene_file_upload.django import FileUploadGraphQLView

urlpatterns = [
    path('graphql/', FileUploadGraphQLView.as_view(graphiql=True)),
]
```

**Mutation для загрузки:**
```python
import graphene
from graphene_file_upload.scalars import Upload

class UploadFile(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)
    
    success = graphene.Boolean()
    url = graphene.String()
    
    def mutate(self, info, file):
        # Сохранение файла
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        url = fs.url(filename)
        
        return UploadFile(success=True, url=url)
```

---

## Слайд 32: Кастомные скалярные типы

**Создание кастомного типа:**
```python
# scalars.py
import graphene
from datetime import datetime

class DateTime(graphene.Scalar):
    @staticmethod
    def serialize(dt):
        return dt.isoformat()
    
    @staticmethod
    def parse_literal(node):
        if isinstance(node, str):
            return datetime.fromisoformat(node)
    
    @staticmethod
    def parse_value(value):
        return datetime.fromisoformat(value)

# types.py
class PostType(DjangoObjectType):
    created_at = DateTime()
    
    class Meta:
        model = Post
```

---

## Слайд 33: Best Practices

**1. Разделение на модули:**
- `types.py` - GraphQL типы
- `queries.py` - Query классы
- `mutations.py` - Mutation классы
- `schema.py` - главная схема

**2. Используйте Input типы для мутаций:**
```python
class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
```

**3. Оптимизируйте запросы:**
```python
Post.objects.select_related('author').prefetch_related('comments')
```

**4. Валидация на уровне мутаций:**
```python
if not title or len(title) < 3:
    raise Exception('Title too short')
```

**5. Используйте permissions:**
```python
if post.author != user:
    raise Exception('Permission denied')
```

---

## Слайд 34: Отладка и мониторинг

**Django Debug Toolbar для GraphQL:**
```python
# settings.py
if DEBUG:
    GRAPHENE = {
        'SCHEMA': 'myapp.schema.schema',
        'MIDDLEWARE': [
            'graphene_django.debug.DjangoDebugMiddleware',
        ],
    }
```

**Логирование запросов:**
```python
# middleware.py
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def resolve(self, next, root, info, **args):
        logger.info(f"GraphQL query: {info.field_name}")
        return next(root, info, **args)
```

**Apollo Studio для мониторинга:**
- Метрики производительности
- Трассировка запросов
- Анализ использования API

---

## Слайд 35: Заключение

**Graphene + Django = мощное сочетание:**
- ✅ Нативная интеграция с Django ORM
- ✅ Автоматическая генерация типов из моделей
- ✅ Поддержка всех возможностей GraphQL
- ✅ Легкая авторизация и permissions
- ✅ Отличная документация и сообщество

**Когда использовать:**
- Существующие Django проекты
- Нужна интеграция с Django Admin
- Команда знает Django

**Альтернативы:**
- Strawberry GraphQL (современный, type hints)
- Ariadne (code-first)
- FastAPI + Strawberry (async)

**Следующие шаги:**
1. Изучите документацию Graphene
2. Попробуйте создать простой API
3. Изучите оптимизацию запросов
4. Настройте авторизацию

---
