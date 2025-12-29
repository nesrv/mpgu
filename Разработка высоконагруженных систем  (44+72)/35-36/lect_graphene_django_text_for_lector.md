# Текст для лектора: Построение API на Django
## 90 минут, неформальный стиль для студентов-программистов

---

## Вступление (5 минут)

Сегодня поговорим про построение API на Django. Если вы до сих пор пишете только REST через DRF и думаете, что это всё, что нужно - готовьтесь расширить горизонты. Сегодня разберем GraphQL с Graphene, новые фишки Django 6.0, и как это всё работает вместе.

Представьте ситуацию: вы делаете мобильное приложение, и вам нужны данные с бэкенда. В REST вы делаете кучу запросов: `/users/123`, потом `/users/123/posts`, потом `/posts/456/comments`. Это как ходить в магазин три раза за одним обедом. GraphQL - это когда вы говорите: "Дай мне пользователя с его постами и комментариями", и получаете всё одним запросом. Красота!

Django 6.0 вышел недавно и принес кучу новых фишек. Background Tasks - это как встроенный Celery, но без лишних зависимостей. Template Partials - это как include, но лучше. CSP - это защита от XSS прямо из коробки. Всё это мы сегодня разберем.

---

## Слайд 1: Новые возможности Django 6.0 (3 минуты)

Итак, Django 6.0 - это не просто обновление версии, это реальные новые возможности. Давайте посмотрим, что там интересного.

**Template Partials** - это модуляризация шаблонов. Раньше вы использовали `{% include %}` или наследование. Теперь можно делать именованные фрагменты прямо в шаблоне. Это как функции в коде - определил один раз, используешь везде. `{% partial "header" %}` - и всё, готово. Более чистый код, легче поддерживать.

**Background Tasks** - это встроенный фреймворк для фоновых задач. Раньше нужно было ставить Celery или RQ, настраивать Redis или RabbitMQ, писать воркеры. Теперь всё из коробки! `@background_task` - и ваша функция выполняется в фоне. Это как встроенный асинхронный воркер без лишних зависимостей.

**Content Security Policy (CSP)** - это защита от XSS атак на уровне браузера. Раньше нужно было ставить отдельные библиотеки типа `django-csp`. Теперь всё встроено. Настроил политику - и браузер сам блокирует опасный контент. Это как встроенный антивирус для вашего сайта.

**Modernized Email API** - это обновленный API для работы с email. Теперь используется Python `EmailMessage` вместо старого `send_mail()`. Более Pythonic, лучше поддержка Unicode, гибче настройка. Это как перейти с Python 2 на Python 3 - та же идея, но лучше.

---

## Слайд 2: Background Tasks (4 минуты)

Background Tasks - это одна из самых крутых фишек Django 6.0. Давайте разберем подробнее.

**Что это?** Встроенный фреймворк для выполнения задач вне HTTP request-response цикла. Раньше для этого нужен был Celery или RQ. Теперь - просто декоратор `@background_task`.

Представьте ситуацию: пользователь регистрируется, и вам нужно отправить приветственное письмо. Если делать это в обычном view, пользователь будет ждать, пока письмо отправится. Это может занять секунду-две. Плохой UX! С Background Tasks вы просто говорите: "Отправь письмо в фоне", и пользователь сразу получает ответ.

```python
@background_task
def send_notification_email(user_id, message):
    user = User.objects.get(id=user_id)
    send_mail(...)

# Вызов
send_notification_email.delay(user.id, "Welcome!")
```

`.delay()` - это магия. Функция не выполняется сразу, а ставится в очередь. Воркер подхватывает задачу и выполняет её в фоне. Это как отправить письмо через почту - вы опустили в ящик, а почтальон доставит позже.

**Преимущества:**
- Не нужен Celery - всё из коробки
- Простая настройка - добавил в INSTALLED_APPS, настроил брокера, готово
- Интеграция с Django ORM - можете использовать все модели и запросы
- Поддержка отложенных задач - можете запланировать выполнение на определенное время

**Настройка:** Просто добавляете `django.contrib.tasks` в INSTALLED_APPS и настраиваете брокера (Redis, RabbitMQ). Всё! Никаких воркеров, никаких сложных конфигов. Django сам всё сделает.

Это как если бы в Python встроили asyncio, но для фоновых задач. Раньше нужны были внешние библиотеки, теперь - просто декоратор.

---

## Слайд 3: Другие улучшения Django 6.0 (3 минуты)

Кроме основных фишек, Django 6.0 принес кучу улучшений в разных областях.

**ORM** - улучшенные запросы. `select_related()` и `prefetch_related()` стали быстрее и умнее. Это как если бы ваш SQL запрос стал оптимизированнее сам по себе. Меньше запросов к БД - быстрее работает приложение.

**Admin** - новый UI компонент. Админка стала современнее, быстрее, удобнее. Это как если бы старый интерфейс Windows обновили до Windows 11 - та же функциональность, но выглядит лучше.

**Forms** - расширенные возможности валидации. Теперь можно валидировать формы более гибко, с лучшими сообщениями об ошибках. Это как если бы валидация стала умнее и понятнее.

**Security** - улучшенная защита по умолчанию. Django теперь более безопасен из коробки. Меньше нужно настраивать вручную, больше работает автоматически. Это как если бы ваш дом стал безопаснее сам по себе.

**Performance** - оптимизации производительности. Запросы стали быстрее, меньше нагрузка на БД, лучше кеширование. Это как если бы ваш код стал работать быстрее без изменений.

Всё это - мелкие улучшения, но вместе они делают Django 6.0 заметно лучше предыдущих версий. Это как обновление телефона - не революция, но приятно.

---

## Слайд 4: Сравнение API фреймворков для Django (5 минут)

Окей, теперь давайте поговорим про разные способы построения API в Django. Их много, и каждый для своих задач.

**Django REST Framework (DRF)** - это классика. Мощный, гибкий, много возможностей. Но может быть "тяжелым" для простых задач. Это как швейцарский нож - много функций, но иногда нужна только отвертка. DRF хорош для enterprise проектов, где нужна максимальная гибкость.

**Django Ninja** - это быстрый и простой REST API с типизацией. Похож на FastAPI, но для Django. Очень легкий, очень быстрый, очень простой. Это как велосипед - простой, быстрый, для коротких поездок. Django Ninja хорош для MVP, микросервисов, легких API.

**Tastypie** - это устаревший фреймворк. Не используйте его! Это как Windows XP - работал когда-то, но сейчас уже не актуален.

**Graphene-Django** - это GraphQL для Django. Автоматическая генерация типов из моделей, хорошая интеграция с ORM. Но синтаксис не самый современный, и поддержка медленная. Это как старый, но надежный автомобиль - работает, но не самый быстрый.

**Strawberry + Django** - это современный GraphQL с нативной типизацией. Очень быстрый, очень современный, очень гибкий. Но моложе, меньше примеров. Это как Tesla - современно, быстро, но нужно время, чтобы привыкнуть.

**Рекомендации:**
- Нужен классический REST? Django Ninja для простых задач, DRF для сложных.
- Нужен GraphQL? Strawberry для новых проектов, Graphene для существующих.
- Избегайте Tastypie - он мертв.

Выбор зависит от задачи. Нет универсального решения, есть правильный инструмент для конкретной ситуации.

---

## Слайд 5: Введение в Graphene (3 минуты)

Graphene - это библиотека для создания GraphQL API в Python. Разработана специально для Django, но может работать и с другими фреймворками.

**Почему Graphene?** Потому что это самый популярный выбор для Django проектов. Нативная интеграция с Django ORM - это значит, что ваши модели автоматически превращаются в GraphQL типы. Не нужно писать сериализаторы, не нужно маппить поля вручную. Просто модель - и готово!

Автоматическая генерация схемы из моделей - это магия. Вы создали модель Post, и Graphene автоматически создал тип PostType. Это как если бы Django Admin автоматически создавался для каждой модели - удобно!

Type-safe с помощью Python type hints - это значит, что IDE подсказывает, что можно запросить, что обязательно, что опционально. Меньше ошибок, быстрее разработка.

Поддержка всех возможностей GraphQL - queries, mutations, subscriptions. Всё из коробки, ничего дополнительно настраивать не нужно.

Активное сообщество и хорошая документация - это значит, что если что-то не понятно, можно найти ответ. Много примеров, много решений, много плагинов.

**Альтернативы:** Strawberry GraphQL (современная, с type hints), Ariadne (code-first подход), Tartiflette (async-first). Но Graphene - самый популярный, самый проверенный, самый надежный для Django.

---

## Слайд 6: Сравнение Strawberry и Graphene (5 минут)

Graphene vs Strawberry - это как выбор между проверенным решением и современным подходом.

**Graphene** - это зрелая библиотека с 2015 года. Это как Python 3.8 - проверено временем, много примеров, много решений. Отличная интеграция с Django ORM - `DjangoObjectType` автоматически создает типы из моделей. Это как магия - написал модель, получил GraphQL тип.

Но есть недостатки: менее современный синтаксис (много boilerplate кода), type hints не обязательны (меньше проверок), медленнее в разработке (больше кода нужно писать).

**Strawberry** - это современная библиотека с 2020 года. Это как Python 3.12 - современно, быстро, с новыми фишками. Современный синтаксис с декораторами - меньше кода, более читаемо. Обязательные type hints - IDE подсказывает всё, ошибки ловятся на этапе разработки.

Но есть недостатки: моложе (меньше примеров и документации), меньше готовых решений, интеграция с Django требует больше настройки.

**Когда выбирать Graphene?** Если работаете с Django проектом, нужна максимальная совместимость, важна зрелость библиотеки, нужно много примеров, команда уже знакома с Graphene. Это безопасный выбор.

**Когда выбирать Strawberry?** Если нужен современный синтаксис, важна производительность, нужна полная async поддержка, хотите меньше boilerplate кода, готовы к меньшей документации. Это современная альтернатива для новых проектов.

**Вывод:** Graphene - это как проверенный друг, на которого можно положиться. Strawberry - это как новый друг, который может быть интереснее, но нужно время, чтобы узнать его лучше.

---

## Слайд 7: Установка и настройка (3 минуты)

Окей, давайте установим Graphene и настроим его. Это просто!

**Установка:** `pip install graphene-django django-filter`. Всё! Два пакета, и готово. `django-filter` нужен для фильтрации запросов.

**Настройка в settings.py:** Добавляете `graphene_django` в INSTALLED_APPS. Потом настраиваете GRAPHENE словарь - указываете путь к схеме и middleware. Middleware нужен для JWT токенов, если используете авторизацию.

**URL конфигурация:** Просто добавляете путь к GraphQLView. `graphiql=True` включает интерактивную IDE для тестирования запросов. Это как Swagger для REST, но для GraphQL. Открываете браузер, идете на `/graphql/`, и видите интерактивный редактор запросов. Красота!

Всё это занимает 5 минут. Установили, настроили, готово. Никаких сложных конфигов, никаких магических настроек. Всё просто и понятно.

---

## Слайд 8: Структура проекта (2 минуты)

Рекомендуемая структура проекта простая:

```
myproject/
├── myapp/
│   ├── models.py          # Django модели
│   ├── schema.py          # GraphQL схема
│   ├── types.py           # GraphQL типы
│   ├── queries.py         # Query классы
│   ├── mutations.py       # Mutation классы
│   └── subscriptions.py   # Subscription классы
```

**Types** - соответствуют Django моделям. Это как сериализаторы в DRF, но для GraphQL.

**Queries** - операции чтения данных. Это как GET запросы в REST.

**Mutations** - операции изменения данных. Это как POST, PUT, DELETE в REST.

**Schema** - объединяет всё вместе. Это как главный файл, который собирает все типы, queries и mutations в одну схему.

Всё логично, всё понятно. Каждый файл отвечает за свою часть. Это как разделение ответственности в коде - каждый модуль делает своё дело.

---

## Слайд 9: Django модель (2 минуты)

Начнем с Django модели. Это стандартная модель - ничего особенного.

```python
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
```

Это обычная модель. Ничего нового. Graphene автоматически может создать GraphQL тип из модели, но лучше делать это вручную для контроля. Автоматическая генерация - это хорошо, но ручной контроль - это лучше. Вы сами решаете, какие поля показывать, какие скрывать, какие добавлять.

---

## Слайд 10: Создание GraphQL типа (3 минуты)

Теперь создаем GraphQL тип из модели. Это просто!

```python
class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'created_at', 'published')
```

**DjangoObjectType** - это магия. Он автоматически:
- Создает GraphQL тип из Django модели
- Маппит поля модели на GraphQL поля
- Поддерживает связи (ForeignKey, ManyToMany)

Это как если бы Django Admin автоматически создавался для каждой модели - удобно! Вы просто указали модель и поля, и Graphene сам создал тип.

**Доступные опции Meta:**
- `model` - Django модель
- `fields` - какие поля включить
- `exclude` - какие поля исключить
- `filter_fields` - поля для фильтрации
- `interfaces` - GraphQL интерфейсы

Всё просто и понятно. Никакой магии, всё явно и контролируемо.

---

## Слайд 11: Кастомизация типов (3 минуты)

Но что если нужно добавить вычисляемые поля? Например, количество слов в посте или краткое описание?

```python
class PostType(DjangoObjectType):
    word_count = graphene.Int()
    excerpt = graphene.String()
    
    def resolve_word_count(self, info):
        return len(self.content.split())
    
    def resolve_excerpt(self, info):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content
```

**Resolvers** - это функции, которые вычисляют значения полей. Это как свойства в Python классах - вы определяете, как получить значение. Graphene вызывает resolver, когда клиент запрашивает это поле.

**Добавление связей:** Можно добавить связи к другим типам. Например, комментарии к посту:

```python
class PostType(DjangoObjectType):
    comments = graphene.List('myapp.types.CommentType')
    
    def resolve_comments(self, info):
        return self.comments.all()
```

Resolvers позволяют добавлять любую логику для получения данных. Это как методы в классах - можете делать что угодно. Хотите фильтровать комментарии? Пожалуйста! Хотите добавить проверку прав? Легко! Хотите кешировать результат? Без проблем!

---

## Слайд 12: Типы для User (2 минуты)

Создание типа для Django User - это важно. Нужно быть осторожным!

```python
class UserType(DjangoObjectType):
    posts = graphene.List('myapp.types.PostType')
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        # Исключаем чувствительные поля
```

**Важно:** Не включайте `password` и другие чувствительные поля в GraphQL тип! Это как не показывать пин-код от карты - очевидно, но многие забывают. GraphQL позволяет клиенту запросить любые поля, которые вы определили. Если вы включили `password`, клиент может его запросить, и вы его вернете. Плохо!

Всегда исключайте чувствительные поля. `password`, `is_superuser`, `is_staff` - всё это не должно быть в GraphQL типе. Это как не давать ключи от дома незнакомым людям - очевидно, но важно помнить.

---

## Слайд 13: Базовый Query (3 минуты)

Теперь создаем Query класс. Это операции чтения данных.

```python
class Query(graphene.ObjectType):
    posts = graphene.List(PostType)
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    
    def resolve_posts(self, info):
        return Post.objects.all()
    
    def resolve_post(self, info, id):
        return Post.objects.get(id=id)
```

**Query** - это как GET запросы в REST. Вы определяете, какие данные можно запросить, и как их получить.

**Resolvers** - это функции, которые получают данные. Когда клиент запрашивает `posts`, Graphene вызывает `resolve_posts()`. Когда клиент запрашивает `post(id: 1)`, Graphene вызывает `resolve_post()` с аргументом `id=1`.

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

Клиент запрашивает только нужные поля. Хочет только `id` и `title`? Получит только `id` и `title`. Хочет `author` с `username`? Получит `author` с `username`. Это гибкость GraphQL - клиент решает, что ему нужно.

---

## Слайд 14: Фильтрация и пагинация (4 минуты)

Фильтрация и пагинация - это важно для больших списков.

**Фильтрация с django-filter:**
```python
class PostType(DjangoObjectType):
    class Meta:
        model = Post
        filter_fields = {
            'title': ['exact', 'icontains'],
            'published': ['exact'],
            'created_at': ['gte', 'lte'],
        }
```

`filter_fields` - это словарь, который определяет, как можно фильтровать. `'title': ['exact', 'icontains']` означает, что можно фильтровать по точному совпадению или по вхождению подстроки (без учета регистра).

**Использование:**
```graphql
query {
  posts(title_Icontains: "Django", published: true) {
    edges {
      node {
        title
      }
    }
  }
}
```

`title_Icontains` - это автоматически сгенерированное поле для фильтрации. Graphene сам создает эти поля на основе `filter_fields`. Это как магия - вы определили, как можно фильтровать, и Graphene сам создал поля для фильтрации.

**Relay Connection** - это стандартный подход для пагинации в GraphQL. Вместо простого списка возвращается объект с `edges` и `pageInfo`. Это как Instagram - вы листаете ленту, и получаете следующую порцию постов по cursor, а не по offset.

---

## Слайд 15: Пагинация (Relay Connection) (3 минуты)

Relay Connection - это стандартный подход для пагинации в GraphQL. Это не просто список, а структурированный объект.

```python
class Query(graphene.ObjectType):
    posts = relay.ConnectionField(PostType)
    
    def resolve_posts(self, info, **kwargs):
        return Post.objects.all()
```

**Использование:**
```graphql
query {
  posts(first: 10, after: "cursor123") {
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

**Cursor-based пагинация** - это более надежный подход, чем offset-based. Представьте ситуацию: вы запросили посты с offset=20, но пока вы их читали, кто-то добавил новый пост в начало. Ваш offset сбился! С cursor этого не происходит - cursor - это уникальный идентификатор позиции, который не зависит от изменений данных.

Это как закладка в книге с уникальным текстом - даже если страницы добавляются, вы всегда найдете место. Offset - это номер страницы, cursor - это уникальный текст на странице.

---

## Слайд 16: Авторизация в Query (3 минуты)

Авторизация в GraphQL реализуется на уровне resolvers. Это как middleware в Express, но для каждого поля.

```python
def resolve_me(self, info):
    user = info.context.user
    if not user.is_authenticated:
        raise Exception('Authentication required')
    return user
```

**info.context.user** - это текущий пользователь из Django сессии или JWT токена. Это как `request.user` в Django views, но для GraphQL.

Проверка авторизации простая: если пользователь не авторизован, выбрасываете исключение. GraphQL вернет ошибку клиенту. Это как проверка прав в Django views - если нет прав, возвращаете 403.

**Важно:** Проверяйте авторизацию в каждом resolver, который требует авторизации. Не полагайтесь на то, что middleware всё проверит - лучше перестраховаться. Это как проверка двери - даже если вы думаете, что она закрыта, лучше проверить.

---

## Слайд 17: Базовый Mutation (4 минуты)

Mutations - это операции изменения данных. Это как POST, PUT, DELETE в REST.

```python
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
```

**Arguments** - это входные параметры мутации. Это как параметры функции - вы определяете, что нужно передать.

**mutate()** - это метод, который выполняет мутацию. Это как метод `create()` в DRF serializer - вы получаете данные, создаете объект, возвращаете результат.

**Возвращаемое значение** - это поля мутации. Вы возвращаете объект с полями, которые определены в классе. Это как возвращаемое значение функции - вы определяете, что вернуть.

Мутации должны возвращать измененные данные. Это хорошая практика - клиент сразу получает результат, не нужно делать отдельный запрос. Это как REST API, который возвращает созданный объект - удобно!

---

## Слайд 18: Input типы для Mutations (3 минуты)

Input типы делают мутации более читаемыми и переиспользуемыми.

```python
class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    published = graphene.Boolean()

class CreatePost(graphene.Mutation):
    class Arguments:
        input = PostInput(required=True)
    
    def mutate(self, info, input):
        post = Post.objects.create(
            title=input.title,
            content=input.content,
            published=input.get('published', False)
        )
```

**Input типы** - это как DTO (Data Transfer Object) в бэкенде. Вы определяете структуру входных данных один раз и используете её везде. Это как класс в Python - определили один раз, используете много раз.

Вместо того чтобы передавать кучу параметров:
```python
createPost(title="...", content="...", published=True)
```

Вы передаете один объект:
```python
createPost(input: {title: "...", content: "...", published: true})
```

Это более читаемо, более структурировано, более переиспользуемо. Это как перейти от позиционных аргументов к именованным - удобнее!

---

## Слайд 19: Update и Delete Mutations (4 минуты)

Update и Delete мутации - это стандартные операции.

**Update Mutation:**
```python
class UpdatePost(graphene.Mutation):
    def mutate(self, info, id, input):
        user = info.context.user
        post = Post.objects.get(id=id)
        
        if post.author != user:
            raise Exception('Permission denied')
        
        for key, value in input.items():
            setattr(post, key, value)
        post.save()
```

**Проверка прав** - это важно! Не позволяйте пользователям обновлять чужие посты. Это как не давать ключи от чужой квартиры - очевидно, но важно проверять.

**Обновление полей** - можно использовать `setattr()` для обновления всех полей из input. Это как `**kwargs` в Python - вы передаете словарь, и все поля обновляются.

**Delete Mutation:**
```python
class DeletePost(graphene.Mutation):
    def mutate(self, info, id):
        user = info.context.user
        post = Post.objects.get(id=id)
        
        if post.author != user:
            raise Exception('Permission denied')
        
        post.delete()
        return DeletePost(success=True)
```

Удаление - это просто. Проверили права, удалили объект, вернули успех. Это как удаление файла - проверили права, удалили, готово.

---

## Слайд 20: Обработка ошибок в Mutations (3 минуты)

Обработка ошибок - это важно. Нужно валидировать данные и возвращать понятные ошибки.

```python
class CreatePost(graphene.Mutation):
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
        
        post = Post.objects.create(...)
        return CreatePost(post=post, errors=[])
```

**Валидация** - это проверка данных перед созданием объекта. Это как проверка формы перед отправкой - лучше проверить заранее, чем получить ошибку от БД.

**Возврат ошибок** - вместо того чтобы выбрасывать исключение, можно вернуть ошибки в поле `errors`. Это более гибко - клиент может обработать ошибки и показать их пользователю. Это как валидация формы - показываете ошибки, но не блокируете форму.

**Кастомные исключения** - можно создать свои классы исключений для разных типов ошибок. Это как разные типы ошибок в Python - `ValueError`, `TypeError`, `KeyError`. Каждый тип ошибки для своей ситуации.

---

## Слайд 21: Объединение Schema (2 минуты)

Schema - это главный файл, который объединяет всё вместе.

```python
# schema.py
import graphene
from .queries import Query
from .mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
```

**Schema** - это как главный роутер в Django. Вы собираете все queries, mutations и subscriptions в одну схему, и Graphene использует её для обработки запросов.

**Если есть Subscriptions:**
```python
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

Всё просто! Создали схему, указали путь в settings, готово. Это как настройка URL в Django - указали путь, всё работает.

---

## Слайд 22: Subscriptions (WebSocket) (4 минуты)

Subscriptions - это реальное время. Это как WebSocket, но через GraphQL.

**Настройка:** Нужно установить `channels` и `channels-redis`. Это библиотеки для WebSocket в Django.

**settings.py:**
```python
INSTALLED_APPS = [
    'channels',
    'graphene_django',
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

**Channels** - это библиотека для WebSocket в Django. Это как встроенный WebSocket сервер. Раньше нужно было использовать отдельные библиотеки, теперь всё встроено.

**Redis** - это брокер сообщений для Channels. Это как очередь задач - Channels использует Redis для передачи сообщений между клиентами и сервером.

Всё это нужно для real-time обновлений. Хотите чат? Subscriptions! Хотите live-обновления? Subscriptions! Хотите уведомления? Subscriptions!

---

## Слайд 23: Создание Subscription (3 минуты)

Создание Subscription - это просто.

```python
class PostSubscription(graphene.ObjectType):
    post_created = graphene.Field(PostType)
    post_updated = graphene.Field(PostType)
    
    def resolve_post_created(root, info):
        return root.filter(
            lambda event: event.operation == CREATED and
            isinstance(event.instance, Post)
        ).map(lambda event: event.instance)
```

**Subscription** - это как Query, но для real-time данных. Клиент подписывается на события, и сервер отправляет данные при изменениях.

**События** - это CREATED, UPDATED, DELETED. Когда создается пост, отправляется событие CREATED. Когда обновляется, отправляется UPDATED. Когда удаляется, отправляется DELETED.

**Resolvers** - это функции, которые фильтруют события. Вы определяете, какие события отправлять клиенту. Это как фильтр в SQL - вы выбираете, какие данные показать.

Подписки идеальны для чатов, уведомлений, live-обновлений. Это как подписка на YouTube канал - когда выходит новое видео, вы получаете уведомление.

---

## Слайд 24: Отправка событий в Mutations (3 минуты)

Чтобы подписки работали, нужно отправлять события в мутациях.

```python
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

**Отправка события** - это как отправка сообщения в очередь. Вы создали пост, отправили событие, и все подписчики получили уведомление.

**Channel Layer** - это брокер сообщений. Это как Redis pub/sub - вы отправляете сообщение в канал, и все подписчики получают его.

**async_to_sync** - это обертка для синхронного кода. Channels работает асинхронно, но мутации синхронные. Нужно обернуть асинхронный вызов в синхронный. Это как `asyncio.run()` в Python - вы запускаете асинхронный код из синхронного.

Всё это нужно для real-time обновлений. Без отправки событий подписки не работают. Это как радио без передатчика - не работает!

---

## Слайд 25: Middleware (3 минуты)

Middleware - это промежуточное ПО, которое выполняется перед каждым resolver.

```python
class AuthMiddleware:
    def resolve(self, next, root, info, **args):
        if not info.context.user.is_authenticated:
            raise Exception('Authentication required')
        return next(root, info, **args)
```

**Middleware** - это как декораторы в Python. Вы определяете логику, которая выполняется перед каждым resolver. Это как `@login_required` в Django - проверяете авторизацию перед выполнением функции.

**next()** - это следующий middleware или resolver. Это как цепочка вызовов - каждый middleware вызывает следующий, последний вызывает resolver.

**Встроенные middleware:**
- `JSONWebTokenMiddleware` - для JWT токенов
- `DjangoDebugMiddleware` - для отладки

Middleware полезен для авторизации, логирования, кеширования. Это как middleware в Express - можете добавить любую логику перед выполнением запроса.

---

## Слайд 26: Оптимизация запросов (N+1) (5 минут)

Проблема N+1 - это классическая проблема GraphQL. Давайте разберем.

**Проблема:**
```python
# Плохо - N+1 запросов
def resolve_posts(self, info):
    return Post.objects.all()  # Для каждого поста отдельный запрос автора
```

Если у вас 10 постов, вы делаете 11 запросов: 1 для постов + 10 для авторов. Это как если бы вы, читая книгу о 100 авторах, для каждого автора отдельно шли в библиотеку за его биографией. Безумие!

**Решение:**
```python
# Хорошо - 2 запроса
def resolve_posts(self, info):
    return Post.objects.select_related('author').prefetch_related('comments').all()
```

`select_related()` - это JOIN для ForeignKey. Один запрос вместо N. Это как если бы вы один раз пошли в библиотеку и взяли все биографии сразу.

`prefetch_related()` - это отдельный запрос для ManyToMany. Два запроса вместо N+1. Это как если бы вы один раз пошли в библиотеку и взяли все книги, потом один раз взяли все авторы.

**DataLoader для сложных случаев:**
```python
class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        users = User.objects.in_bulk(keys)
        return [users.get(key) for key in keys]
```

DataLoader группирует запросы и кеширует результаты. Это как умный помощник - вы просите авторов, он собирает все запросы, делает один запрос к БД, возвращает результаты.

Всегда оптимизируйте запросы! N+1 проблема убивает производительность. Это как если бы вы делали 100 запросов вместо 2 - медленно и неэффективно.

---

## Слайд 27: Тестирование GraphQL (3 минуты)

Тестирование GraphQL - это важно. Нужно проверять, что запросы работают правильно.

```python
from graphene.test import Client
from .schema import schema

class PostQueryTest(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.post = Post.objects.create(...)
    
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
```

**Client** - это тестовый клиент для GraphQL. Это как `Client()` в Django - вы делаете запросы и проверяете результаты.

**Тестирование** - это как тестирование views в Django. Вы создаете данные, делаете запрос, проверяете результат. Просто и понятно.

Тестирование GraphQL проще, чем REST, потому что один endpoint. Не нужно тестировать разные URL, достаточно тестировать разные запросы. Это как тестирование одной функции вместо нескольких - проще!

---

## Слайд 28: Тестирование Mutations (3 минуты)

Тестирование мутаций - это как тестирование POST запросов в REST.

```python
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
    context = {'user': self.user}
    result = self.client.execute(mutation, context_value=context)
    
    self.assertTrue(result['data']['createPost']['post'])
```

**Context** - это контекст запроса. Вы передаете пользователя, и GraphQL использует его для авторизации. Это как `client.force_login()` в Django - вы авторизуете пользователя для теста.

**Проверка результата** - вы проверяете, что мутация вернула правильные данные. Это как проверка создания объекта в Django - вы создали, проверили, готово.

Тестирование мутаций важно, потому что они изменяют данные. Нужно проверять, что данные создаются правильно, права проверяются, ошибки обрабатываются. Это как тестирование форм в Django - нужно проверить всё!

---

## Слайд 29: JWT аутентификация (4 минуты)

JWT аутентификация - это стандартный способ авторизации в GraphQL.

**Установка:** `pip install django-graphql-jwt`. Всё!

**Настройка:**
```python
GRAPHENE = {
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
class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
```

**JWT** - это JSON Web Token. Это как пропуск - вы получили токен, предъявляете его при каждом запросе, получаете доступ. Это как ключ от дома - есть ключ, можете войти.

**Получение токена:**
```graphql
mutation {
  tokenAuth(username: "user", password: "pass") {
    token
  }
}
```

Вы отправляете логин и пароль, получаете токен. Потом используете токен в заголовках запросов. Это как авторизация в REST API - получили токен, используете его.

JWT лучше, чем сессии, потому что stateless. Не нужно хранить сессии на сервере, всё в токене. Это как пропуск вместо списка гостей - не нужно проверять список, достаточно проверить пропуск.

---

## Слайд 30: Использование JWT (3 минуты)

Использование JWT токена простое.

**В заголовках запроса:**
```javascript
headers: {
  'Authorization': 'JWT <token>'
}
```

**В Python клиенте:**
```python
response = requests.post(
    'http://localhost:8000/graphql/',
    json={'query': query},
    headers={'Authorization': 'JWT <token>'}
)
```

**Middleware** автоматически извлекает токен из заголовков и авторизует пользователя. Это как автоматическая проверка пропуска - вы предъявили токен, вас пропустили.

**info.context.user** содержит авторизованного пользователя. Это как `request.user` в Django views - вы получаете пользователя из токена.

JWT удобен для мобильных приложений и SPA. Не нужны куки, не нужны сессии, всё в токене. Это как пропуск вместо билета - не нужно хранить билет, достаточно показать пропуск.

---

## Слайд 31: Файловые загрузки (3 минуты)

Файловые загрузки в GraphQL - это не так просто, как в REST.

**Установка:** `pip install graphene-file-upload`. Всё!

**Настройка:**
```python
from graphene_file_upload.django import FileUploadGraphQLView

urlpatterns = [
    path('graphql/', FileUploadGraphQLView.as_view(graphiql=True)),
]
```

**Mutation для загрузки:**
```python
from graphene_file_upload.scalars import Upload

class UploadFile(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)
    
    def mutate(self, info, file):
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        url = fs.url(filename)
        return UploadFile(success=True, url=url)
```

**Upload** - это специальный скалярный тип для файлов. Это как `FileField` в Django forms - вы получаете файл, сохраняете его, возвращаете URL.

Файловые загрузки в GraphQL работают через multipart/form-data. Это как загрузка файлов в HTML формах - вы отправляете файл, сервер его сохраняет.

Важно использовать `FileUploadGraphQLView` вместо обычного `GraphQLView`. Это специальный view, который умеет обрабатывать файлы. Это как специальный обработчик для файлов - обычный не справится.

---

## Слайд 32: Кастомные скалярные типы (3 минуты)

Кастомные скалярные типы - это когда встроенных типов недостаточно.

```python
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
```

**Скалярные типы** - это базовые типы (String, Int, Float, Boolean, ID). Если нужен свой тип, создаете кастомный скаляр.

**serialize()** - это как `__str__()` в Python. Вы определяете, как преобразовать значение в строку для GraphQL.

**parse_literal()** - это парсинг из GraphQL запроса. Вы получаете строку, преобразуете в нужный тип.

**parse_value()** - это парсинг из переменных. Вы получаете значение, преобразуете в нужный тип.

Кастомные скаляры полезны для дат, email, URL. Это как создание своего типа в Python - вы определяете, как работать с данными.

---

## Слайд 33: Best Practices (4 минуты)

Best Practices - это рекомендации, как делать правильно.

**1. Разделение на модули:**
- `types.py` - GraphQL типы
- `queries.py` - Query классы
- `mutations.py` - Mutation классы
- `schema.py` - главная схема

Это как разделение кода на модули в Python - каждый файл отвечает за свою часть. Легче поддерживать, легче тестировать, легче понимать.

**2. Используйте Input типы для мутаций:**
```python
class PostInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
```

Это более читаемо и переиспользуемо. Это как использование классов вместо словарей - структурированнее.

**3. Оптимизируйте запросы:**
```python
Post.objects.select_related('author').prefetch_related('comments')
```

Всегда используйте `select_related()` и `prefetch_related()`. Это как использование индексов в БД - быстрее работает.

**4. Валидация на уровне мутаций:**
```python
if not title or len(title) < 3:
    raise Exception('Title too short')
```

Проверяйте данные перед сохранением. Это как валидация форм - лучше проверить заранее.

**5. Используйте permissions:**
```python
if post.author != user:
    raise Exception('Permission denied')
```

Всегда проверяйте права доступа. Это как проверка двери - лучше перестраховаться.

---

## Слайд 34: Отладка и мониторинг (3 минуты)

Отладка и мониторинг - это важно для продакшена.

**Django Debug Toolbar для GraphQL:**
```python
if DEBUG:
    GRAPHENE = {
        'MIDDLEWARE': [
            'graphene_django.debug.DjangoDebugMiddleware',
        ],
    }
```

Это показывает все запросы к БД, время выполнения, использованные resolvers. Это как DevTools в браузере - видите, что происходит под капотом.

**Логирование запросов:**
```python
class LoggingMiddleware:
    def resolve(self, next, root, info, **args):
        logger.info(f"GraphQL query: {info.field_name}")
        return next(root, info, **args)
```

Логируйте все запросы. Это как логирование в Django - видите, что происходит, когда что-то ломается.

**Apollo Studio** - это платформа для мониторинга GraphQL API. Метрики производительности, трассировка запросов, анализ использования. Это как Google Analytics для API - видите, как используется ваш API.

Отладка важна, потому что GraphQL запросы могут быть сложными. Нужно видеть, какие resolvers вызываются, сколько времени занимают, какие запросы к БД делаются. Это как профилирование кода - видите узкие места.

---

## Слайд 35: Заключение (5 минут)

Итак, что мы узнали?

**Graphene + Django = мощное сочетание:**
- ✅ Нативная интеграция с Django ORM - модели автоматически превращаются в GraphQL типы
- ✅ Автоматическая генерация типов из моделей - не нужно писать сериализаторы
- ✅ Поддержка всех возможностей GraphQL - queries, mutations, subscriptions
- ✅ Легкая авторизация и permissions - просто проверяете права в resolvers
- ✅ Отличная документация и сообщество - много примеров, много решений

**Когда использовать:**
- Существующие Django проекты - легко интегрировать
- Нужна интеграция с Django Admin - всё работает вместе
- Команда знает Django - не нужно изучать новый фреймворк

**Альтернативы:**
- Strawberry GraphQL - современный, с type hints, но моложе
- Ariadne - code-first подход, но менее популярный
- FastAPI + Strawberry - async-first, но не Django

**Следующие шаги:**
1. Изучите документацию Graphene - там много полезного
2. Попробуйте создать простой API - практика важнее теории
3. Изучите оптимизацию запросов - N+1 проблема реальна
4. Настройте авторизацию - JWT или сессии, на ваш выбор

GraphQL - это не замена REST, это другой подход. REST - это отвертка, GraphQL - это шуруповерт. Иногда нужна отвертка, иногда - шуруповерт. Выбирайте инструмент под задачу!

Django 6.0 принес много новых возможностей. Background Tasks - это встроенный Celery. Template Partials - это лучшие include. CSP - это защита из коробки. Всё это делает Django лучше и удобнее.

**Вопросы?** Давайте обсудим!

---

## Время для вопросов (5 минут)

Отлично, мы прошли весь материал. GraphQL с Graphene - это мощный инструмент для построения API. Django 6.0 - это новые возможности, которые делают разработку удобнее.

Вопросы? Давайте обсудим!

---

**Итого: 90 минут**
- Вступление: 5 мин
- Слайды 1-35: 80 мин (примерно 2.3 мин на слайд)
- Вопросы: 5 мин
