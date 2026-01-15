# Текст для лектора: GraphQL - Современный подход к API
## 90 минут, неформальный стиль

---

## Вступление (5 минут)

Привет, ребята! Сегодня поговорим про GraphQL. Если вы до сих пор пишете REST API и думаете, что это круто - готовьтесь к прозрению. GraphQL - это как перейти с Nokia 3310 на iPhone. Да, старый телефон работал, но новый делает то же самое в 10 раз удобнее.

Представьте ситуацию: вы заходите в ресторан, а официант приносит вам ВСЁ меню целиком - и салаты, и супы, и десерты, и даже то, что вы не заказывали. Это REST. А GraphQL - это когда вы говорите: "Дай мне только борщ и компот", и получаете ровно это. Ни больше, ни меньше.

Facebook придумал GraphQL в 2012 году, потому что у них была реальная проблема: мобильное приложение Facebook делало кучу запросов к серверу, тратило батарею и интернет. Они подумали: "А что если клиент сам скажет, что ему нужно?" И родился GraphQL.

---

## Слайд 1: Введение в GraphQL (3 минуты)

Итак, GraphQL - это не база данных, не фреймворк, не библиотека. Это ЯЗЫК ЗАПРОСОВ. Как SQL, но для API. Представьте, что SQL - это язык для общения с базой данных, а GraphQL - это язык для общения между фронтендом и бэкендом.

Кстати, почему GraphQL так называется? Расшифровывается как **Graph Query Language** - язык запросов для графов. Дело в том, что данные в GraphQL организованы как граф: пользователи связаны с постами, посты с комментариями, комментарии с пользователями. Это не просто плоская таблица, а сеть связей. Представьте социальную сеть - вы дружите с кем-то, кто дружит с кем-то еще, и так далее. Это граф! GraphQL позволяет запрашивать данные, следуя этим связям. Отсюда и название - Graph (граф) + QL (Query Language, язык запросов). Facebook, создавая GraphQL, думал именно о графе социальных связей - отсюда и такое название.

Основная фишка GraphQL - один endpoint. В REST у вас куча URL: `/users`, `/posts`, `/comments`. В GraphQL - один `/graphql`. Это как универсальный пульт от всего в доме вместо кучи разных пультов.

Клиент запрашивает только то, что нужно. Если вам нужны только имя и email пользователя - вы получите только имя и email. Не будет лишних полей типа `createdAt`, `updatedAt`, `avatar`, `bio` и прочей фигни, которая вам не нужна.

Строгая типизация - это как TypeScript для API. Вы сразу видите, что можно запросить, что обязательно, что опционально. IDE подсказывает, автодополнение работает. Красота!

Интроспекция - это когда API сам рассказывает о себе. Вы можете спросить: "Эй, API, что ты умеешь?" И он ответит: "Я умею возвращать пользователей, посты, комментарии. Вот моя схема, изучай!"

---

## Слайд 2: Проблемы REST API (5 минут)

Давайте честно: REST - это старый добрый дедушка, который работает, но уже не торт. У него куча проблем, которые мы терпим годами.

**Over-fetching** - это когда вы просите яблоко, а получаете целый сад. Например, вам нужны только имя и email пользователя, а API возвращает всё: дату рождения, адрес, номер телефона, список друзей, посты за последние 5 лет. Зачем? Вы же не просили!

**Under-fetching** - обратная проблема. Вам нужен пользователь и его последние 3 поста. В REST вы делаете запрос `/users/123`, получаете пользователя, но без постов. Потом делаете `/users/123/posts?limit=3`. Два запроса вместо одного! Это как ходить в магазин два раза: сначала за хлебом, потом за маслом.

**Множественные endpoints** - это ад для фронтенда. Нужен пользователь? `/users/123`. Нужны его посты? `/users/123/posts`. Комментарии? `/posts/456/comments`. Это как иметь отдельный ключ для каждой двери в доме.

**Версионирование** - это когда вы меняете API и создаете `/api/v2`, а старый `/api/v1` висит мертвым грузом. Через год у вас `/api/v1`, `/api/v2`, `/api/v3`, и никто не помнит, что в какой версии работает. Это как старые версии Windows на компьютере - они занимают место, но удалить страшно.

**Слабая типизация** - в REST вы не знаете точно, что вернет API. Может быть `name`, может быть `fullName`, может быть `userName`. Документация устарела, примеры не работают. Это как играть в угадайку.

GraphQL решает все эти проблемы одним махом. Один endpoint, клиент сам решает, что ему нужно, строгая типизация, интроспекция. Это как перейти с Windows 95 на Windows 11 - та же идея, но в 100 раз лучше.

---

## Слайд 2.5: Проблема N+1 запросов (4 минуты)

Есть еще одна проблема, которая касается и REST, и GraphQL - это проблема N+1 запросов. Это классический баг, который убивает производительность.

Представьте ситуацию: вам нужно показать список из 10 постов, и для каждого поста показать автора. 

**Плохой подход (N+1 проблема):**
1. Делаете запрос: "Дай мне 10 постов" - это 1 запрос к БД
2. Для каждого поста делаете отдельный запрос: "Дай мне автора поста #1" - это еще 1 запрос
3. "Дай мне автора поста #2" - еще 1 запрос
4. И так далее для всех 10 постов

Итого: 1 запрос для постов + 10 запросов для авторов = **11 запросов к базе данных**. Это и есть N+1 проблема: N постов требуют N+1 запросов.

Это как если бы вы, читая книгу о 100 авторах, для каждого автора отдельно шли в библиотеку за его биографией. Вместо того чтобы один раз взять все биографии, вы делаете 100 походов. Безумие!

**Правильный подход:**
1. Делаете запрос: "Дай мне 10 постов" - это 1 запрос
2. Собираете все ID авторов: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
3. Делаете один запрос: "Дай мне всех авторов с ID [1,2,3,4,5,6,7,8,9,10]" - это еще 1 запрос

Итого: **2 запроса к базе данных** вместо 11. В 5.5 раз быстрее!

В REST эта проблема тоже есть, но в GraphQL она особенно опасна. Почему? Потому что GraphQL позволяет делать гибкие запросы. Клиент может запросить посты с авторами, авторов с их постами, посты с комментариями и авторами комментариев - и всё это одним запросом. Если не оптимизировать, вы получите ад из запросов к БД.

Например, запрос:
```graphql
query {
  posts {
    title
    author {
      name
      posts {
        title
        author {
          name
        }
      }
    }
  }
}
```

Если у вас 10 постов, у каждого поста есть автор, и у каждого автора есть еще 5 постов - это может превратиться в сотни запросов к БД! Сервер просто упадет.

**Решение проблемы N+1:**
- **DataLoader** - библиотека, которая группирует запросы и кеширует результаты
- **Batch loading** - загрузка связанных данных одним запросом
- **Join'ы в SQL** - правильное использование JOIN в запросах к БД

Мы еще вернемся к этому, когда будем говорить про DataLoader и оптимизацию. Но запомните: N+1 проблема - это убийца производительности. Всегда думайте, сколько запросов к БД вы делаете!

---

## Слайд 3: Основные концепции GraphQL (4 минуты)

GraphQL построен на простых, но мощных концепциях. Давайте разберем их, как конструктор LEGO.

**Schema** - это чертеж вашего API. Как план дома: здесь кухня (User), здесь гостиная (Post), здесь спальня (Comment). Schema описывает, что можно запросить, что можно изменить, какие типы данных есть.

**Types** - это строго типизированные объекты. `User`, `Post`, `Comment`. Это как классы в ООП, но для API. Каждый тип знает, какие у него поля, какие обязательные, какие опциональные.

**Fields** - это свойства типов. У `User` есть поля `name`, `email`, `age`. Это как атрибуты класса. Просто и понятно.

**Queries** - операции чтения. "Дай мне пользователя с id=123". Это как SELECT в SQL, но для API.

**Mutations** - операции изменения. "Создай пользователя", "Обнови пост", "Удали комментарий". Это как INSERT, UPDATE, DELETE в SQL.

**Subscriptions** - это реальное время. "Уведомляй меня, когда появится новый пост". Это как WebSocket, но через GraphQL. Представьте мессенджер - когда кто-то пишет, вы сразу видите сообщение. Это subscriptions.

**Resolvers** - это функции, которые получают данные. Когда клиент запрашивает `user { name }`, resolver говорит: "Окей, нужно получить пользователя и вернуть его имя". Это как методы класса, которые знают, где взять данные.

Все эти концепции работают вместе, создавая мощную систему. Это как оркестр: каждый инструмент играет свою партию, но вместе получается симфония.

---

## Слайд 4: GraphQL Schema Definition Language (SDL) (5 минут)

SDL - это синтаксис для описания схемы. Выглядит как TypeScript, но для API. Давайте разберем на примерах.

Скалярные типы - это базовые типы: `String`, `Int`, `Float`, `Boolean`, `ID`. Это как примитивы в языках программирования. Можно создавать свои: `Date`, `Email`, `URL`. Это как создать свой тип в TypeScript.

Объектные типы - это структуры данных. `type User { ... }` - это как интерфейс в TypeScript или класс. Восклицательный знак `!` означает "обязательно". Без `!` - опционально. Это как `name: string` vs `name?: string` в TypeScript.

Квадратные скобки `[]` - это массивы. `[Post!]!` означает "массив постов, каждый пост обязателен, и сам массив обязателен". Это как `posts: Post[]` в TypeScript.

Корневые типы - это точки входа. `Query` - для чтения, `Mutation` - для изменения, `Subscription` - для реального времени. Это как публичные методы класса - через них клиент общается с API.

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!  # Массив постов, обязательный
}
```

Это читается так: "У пользователя есть обязательный id, обязательное имя, обязательный email и обязательный массив постов, где каждый пост обязателен".

---

## Слайд 5: Скалярные типы (3 минуты)

GraphQL дает вам базовые типы из коробки. Это как стандартная библиотека языка.

**String** - обычные строки. UTF-8, поддерживает эмодзи, кириллицу, всё что угодно. Это как `string` в TypeScript.

**Int** - целые числа, 32 бита. Для возраста, количества, ID. Это как `number` в TypeScript, но только целые.

**Float** - числа с плавающей точкой. Для цен, рейтингов, координат. Это как `number` в TypeScript для дробных.

**Boolean** - true/false. Для флагов: `isActive`, `isPublished`, `isDeleted`. Просто и понятно.

**ID** - уникальный идентификатор. Может быть строкой или числом, но семантически это ID. GraphQL знает, что это идентификатор, и может оптимизировать под это.

Можно создавать свои скаляры. Например, `scalar Date` - для дат. Или `scalar Email` - для email с валидацией. Это как создать свой тип в TypeScript с проверками.

```graphql
scalar Date
scalar Email

type User {
  email: Email!  # Автоматическая валидация email
  createdAt: Date!
}
```

Круто, правда? Вместо того чтобы валидировать email на клиенте и сервере отдельно, вы определяете тип `Email`, и GraphQL сам проверяет.

---

## Слайд 6: Объектные типы (4 минуты)

Объектные типы - это основа GraphQL. Это как классы в ООП, но для API.

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  age: Int  # Опционально
  posts: [Post!]!  # Обязательный массив постов
  profile: Profile  # Опциональный профиль
}
```

Поля могут быть:
- Скалярными значениями (`name: String!`)
- Другими объектными типами (`profile: Profile`)
- Массивами (`posts: [Post!]!`)
- Nullable или Non-null (с `!` или без)

Связи между типами создают граф - отсюда и название GraphQL (Graph Query Language). Это как социальная сеть: пользователи связаны с постами, посты с комментариями, комментарии с пользователями. Вы можете запросить пользователя, его посты, комментарии к постам, авторов комментариев - и всё это одним запросом, следуя по связям графа. Это не просто таблицы в БД, это сеть взаимосвязанных данных!

Представьте дерево: корень - это `Query`, ветки - это типы, листья - это поля. Клиент может пройти по любому пути в этом дереве и получить нужные данные. Или представьте карту города: узлы (вершины) - это типы данных (User, Post, Comment), дороги (рёбра) - это связи между ними. GraphQL позволяет "путешествовать" по этой карте, запрашивая нужные данные.

---

## Слайд 7: Enum и Union типы (5 минут)

**Enum** - это ограниченный набор значений. Как константы в TypeScript.

```graphql
enum PostStatus {
  DRAFT      # Черновик
  PUBLISHED  # Опубликован
  ARCHIVED   # В архиве
}
```

Это как `type PostStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED'` в TypeScript. Только эти три значения, больше никаких. Если кто-то попытается передать `DELETED` - GraphQL скажет "нет, так нельзя".

**Union** - это "один из нескольких типов". Как `type Result = User | Post | Comment` в TypeScript.

```graphql
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}
```

Когда вы делаете поиск, результат может быть пользователем, постом или комментарием. GraphQL не знает заранее, что вернется. Поэтому нужны inline fragments:

```graphql
query {
  search(query: "GraphQL") {
    ... on User { name email }
    ... on Post { title content }
    ... on Comment { text }
  }
}
```

Это как `if (result instanceof User) { ... }` в TypeScript. Вы проверяете тип и обрабатываете соответственно.

Union полезны для поиска, уведомлений, лент активности. Когда результат может быть разным типом.

---

## Слайд 8: Interface типы (4 минуты)

Interface - это как интерфейс в TypeScript. Определяет общие поля для группы типов.

```graphql
interface Node {
  id: ID!
  createdAt: Date!
}

type User implements Node {
  id: ID!
  createdAt: Date!
  name: String!
  email: String!
}

type Post implements Node {
  id: ID!
  createdAt: Date!
  title: String!
  content: String!
}
```

Все, что реализует `Node`, имеет `id` и `createdAt`. Это полезно для:
- Общих операций (получение по ID)
- Полиморфных связей
- Переиспользования логики

```graphql
type Query {
  node(id: ID!): Node  # Может вернуть User или Post
}
```

Когда запрашиваете интерфейс, используйте inline fragments для доступа к специфичным полям:

```graphql
query {
  node(id: "123") {
    id
    createdAt
    ... on User { name email }
    ... on Post { title content }
  }
}
```

Это как полиморфизм в ООП. Базовый тип `Node`, конкретные реализации `User` и `Post`.

---

## Слайд 9: Input типы (4 минуты)

Input типы - это для передачи сложных данных в мутации. Как DTO (Data Transfer Object) в бэкенде.

```graphql
input CreateUserInput {
  name: String!
  email: String!
  age: Int
  profileInput: ProfileInput
}
```

Input типы:
- Не могут содержать поля объектных типов (только скаляры, enum, другие input типы, массивы)
- Обеспечивают валидацию входных данных
- Делают API более читаемым

Это как форма на сайте: вы заполняете поля, отправляете, и сервер создает объект. Input тип - это описание этой формы.

```graphql
mutation {
  createUser(input: {
    name: "John"
    email: "john@example.com"
    age: 25
  }) {
    id
    name
  }
}
```

Чисто, понятно, типизировано. GraphQL проверит, что все обязательные поля заполнены, типы правильные.

---

## Слайд 10: Директивы (5 минут)

Директивы - это как аннотации в Java или декораторы в Python. Они изменяют выполнение запросов.

**@include** - включает поле при условии. Это как `if` в коде.

```graphql
query GetUser($withPosts: Boolean!) {
  user(id: "1") {
    name
    posts @include(if: $withPosts) {
      title
    }
  }
}
```

Если `$withPosts = true`, вернутся посты. Если `false` - не вернутся. Это условная логика в запросе.

**@skip** - пропускает поле при условии. Обратная логика `@include`.

```graphql
query GetUser($skipEmail: Boolean!) {
  user(id: "1") {
    name
    email @skip(if: $skipEmail)
  }
}
```

**@deprecated** - помечает поле как устаревшее. Это как `@deprecated` в Java или `#deprecated` в Python.

```graphql
type User {
  name: String!
  fullName: String! @deprecated(reason: "Use name instead")
}
```

IDE покажет предупреждение, если кто-то использует устаревшее поле. Это помогает мигрировать API без breaking changes.

Можно создавать свои директивы для валидации, авторизации, кеширования. Это мощный механизм расширения GraphQL.

---

## Слайд 11: Queries - Основы запросов (5 минут)

Query - это операция чтения. Как SELECT в SQL, но для API.

Базовый синтаксис простой:

```graphql
query {
  users {
    id
    name
    email
  }
}
```

Читается как: "Дай мне всех пользователей, и для каждого верни id, name и email". Просто и понятно.

С аргументами:

```graphql
query {
  user(id: "123") {
    name
    email
    posts(limit: 5) {
      title
      createdAt
    }
  }
}
```

"Дай мне пользователя с id=123, его имя, email и первые 5 постов с заголовком и датой создания".

Именованные запросы с переменными:

```graphql
query GetUserWithPosts($userId: ID!, $postsLimit: Int = 10) {
  user(id: $userId) {
    name
    posts(limit: $postsLimit) {
      title
    }
  }
}
```

Переменные передаются отдельно:

```json
{
  "query": "query GetUserWithPosts($userId: ID!) { ... }",
  "variables": {
    "userId": "123",
    "postsLimit": 5
  }
}
```

Это безопасно (нет SQL-инъекций), переиспользуемо, кешируемо. Клиент получает ровно то, что запросил, в том же формате.

---

## Слайд 12: Aliases и Fragments (5 минут)

**Aliases** - это переименование полей в результате. Как `AS` в SQL.

```graphql
query {
  currentUser: user(id: "123") {
    name
  }
  otherUser: user(id: "456") {
    name
  }
}
```

Результат будет:
```json
{
  "currentUser": { "name": "John" },
  "otherUser": { "name": "Jane" }
}
```

Без aliases оба поля назывались бы `user`, и одно перезаписало бы другое. С aliases - два разных поля.

**Fragments** - это переиспользование наборов полей. Как функции в коде.

```graphql
fragment UserInfo on User {
  id
  name
  email
}

query {
  user(id: "123") {
    ...UserInfo
    posts { title }
  }
  
  users {
    ...UserInfo
  }
}
```

Вместо того чтобы повторять `id name email` везде, вы определяете fragment один раз и используете его. DRY принцип - Don't Repeat Yourself.

**Inline fragments** - для условной выборки. Полезны с Union и Interface.

```graphql
query {
  search(query: "test") {
    ... on User { name email }
    ... on Post { title content }
  }
}
```

Если результат - User, вернутся name и email. Если Post - title и content. Условная логика прямо в запросе.

---

## Слайд 13: Переменные в запросах (4 минуты)

Переменные делают запросы динамическими и безопасными. Это как параметры функции.

```graphql
query GetUser($id: ID!, $includeEmail: Boolean = false) {
  user(id: $id) {
    name
    email @include(if: $includeEmail)
    posts(first: 10) {
      title
    }
  }
}
```

Типы переменных:
- Обязательные: `$id: ID!` - без них запрос не выполнится
- Опциональные: `$limit: Int` - могут быть null
- С значением по умолчанию: `$limit: Int = 10` - если не передали, используется 10

Переменные передаются отдельно:

```json
{
  "query": "query GetUser($id: ID!) { ... }",
  "variables": {
    "id": "123",
    "includeEmail": true
  }
}
```

Это безопасно - нет SQL-инъекций. GraphQL валидирует типы переменных перед выполнением. Это переиспользуемо - один запрос, разные переменные. Это кешируемо - запросы с одинаковыми переменными можно кешировать.

---

## Слайд 14: Mutations - Изменение данных (5 минут)

Mutations - это операции изменения. Как INSERT, UPDATE, DELETE в SQL.

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
  }
}
```

Мутации должны возвращать измененные данные. Это хорошая практика - клиент сразу получает результат, не нужно делать отдельный запрос.

Множественные мутации выполняются последовательно (не параллельно!):

```graphql
mutation {
  createPost(input: {title: "Post 1"}) { id }
  createPost(input: {title: "Post 2"}) { id }
}
```

Сначала создастся первый пост, потом второй. Это гарантирует порядок выполнения и целостность данных.

Хорошая практика - возвращать объект с полезной нагрузкой и ошибками:

```graphql
type Mutation {
  createUser(input: CreateUserInput!): UserPayload!
}

type UserPayload {
  user: User
  errors: [Error!]!
}
```

Это позволяет обрабатывать частичные ошибки. Например, пользователь создан, но email не отправлен - это не критично, но нужно сообщить клиенту.

---

## Слайд 15: Subscriptions - Реальное время (5 минут)

Subscriptions - это реальное время. Как WebSocket, но через GraphQL.

```graphql
subscription {
  messageAdded(chatId: "123") {
    id
    content
    author {
      name
    }
    createdAt
  }
}
```

Клиент подписывается на события, сервер отправляет данные при изменениях. Это как подписка на YouTube канал - когда выходит новое видео, вы получаете уведомление.

Подписка на изменения пользователя:

```graphql
subscription UserUpdated($userId: ID!) {
  userUpdated(id: $userId) {
    id
    name
    email
    lastSeen
  }
}
```

Subscriptions работают через WebSocket или Server-Sent Events. Сервер отправляет данные при изменениях:

```graphql
type Subscription {
  messageAdded(chatId: ID!): Message!
  userOnline: User!
  postPublished: Post!
}
```

Подписки идеальны для:
- Чатов (новые сообщения)
- Уведомлений (новые события)
- Live-обновлений (изменения в реальном времени)
- Collaborative editing (совместное редактирование)

Представьте Google Docs - когда кто-то печатает, вы видите курсор в реальном времени. Это subscriptions.

---

## Слайд 16: Resolvers - Получение данных (6 минут)

Resolvers - это функции, которые получают данные для каждого поля. Это сердце GraphQL.

```javascript
const resolvers = {
  Query: {
    user: (parent, args, context) => {
      return getUserById(args.id);
    },
    users: () => {
      return getAllUsers();
    }
  },
  
  User: {
    posts: (user, args, context) => {
      return getPostsByUserId(user.id);
    },
    email: (user, args, context) => {
      // Проверка авторизации
      if (context.user.id !== user.id) {
        throw new Error('Unauthorized');
      }
      return user.email;
    }
  }
};
```

Resolver получает 4 аргумента:
- **parent** - результат родительского resolver. Для `User.posts` parent - это объект User
- **args** - аргументы поля. Для `user(id: "123")` args = `{ id: "123" }`
- **context** - общий контекст (пользователь, база данных, сервисы). Это как глобальные переменные, но безопасные
- **info** - метаинформация о запросе. Редко используется, но мощный инструмент

Context - это как рюкзак путешественника. В нем всё необходимое: данные пользователя, подключения к БД, сервисы. Доступен в любом resolver.

Resolvers могут быть асинхронными:

```javascript
User: {
  posts: async (user, args, context) => {
    return await getPostsByUserId(user.id);
  }
}
```

GraphQL автоматически ждет Promise. Это как async/await в JavaScript - просто и удобно.

---

## Слайд 17: Context и DataLoader (7 минут)

**Context** передает общие данные между resolvers. Это как dependency injection в бэкенде.

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => ({
    user: getUser(req.headers.authorization),
    db: database,
    dataSources: {
      userAPI: new UserAPI(),
      postAPI: new PostAPI()
    }
  })
});
```

Context создается для каждого запроса. В нем можно хранить:
- Данные пользователя (из токена)
- Подключения к БД
- Сервисы (API клиенты)
- Кеши
- Логгеры

**DataLoader** решает проблему N+1 запросов. Это классическая проблема GraphQL.

Проблема: у вас есть 10 постов, каждый с автором. Без DataLoader вы делаете:
1. Запрос постов (1 запрос)
2. Для каждого поста запрос автора (10 запросов)
Итого: 11 запросов к БД. Это N+1 проблема.

DataLoader группирует запросы:

```javascript
const userLoader = new DataLoader(async (userIds) => {
  const users = await getUsersByIds(userIds);
  return userIds.map(id => users.find(user => user.id === id));
});

const resolvers = {
  Post: {
    author: (post, args, { userLoader }) => {
      return userLoader.load(post.authorId);
    }
  }
};
```

DataLoader собирает все `load()` вызовы в рамках одного запроса, группирует их и делает один запрос к БД. Вместо 11 запросов - 2 запроса (посты + авторы).

DataLoader также кеширует результаты в рамках одного запроса. Если один и тот же пользователь запрашивается дважды, DataLoader вернет кешированный результат.

Это как умный помощник: "Стоп! Дайте мне список всех авторов, я схожу один раз и принесу все биографии сразу".

---

## Слайд 18: Валидация и ошибки (5 минут)

GraphQL выполняет валидацию на нескольких уровнях. Это как многоуровневая защита.

**Синтаксическая валидация** - проверка корректности запроса:

```graphql
# Ошибка: отсутствует закрывающая скобка
query {
  user(id: "123" {
    name
  }
}
```

GraphQL скажет: "Синтаксическая ошибка на строке 2". Четко и понятно.

**Валидация схемы** - проверка соответствия типам:

```graphql
# Ошибка: поле age не существует в типе User
query {
  user(id: "123") {
    name
    age  # Нет такого поля!
  }
}
```

GraphQL скажет: "Поле 'age' не существует в типе 'User'". IDE покажет ошибку еще до отправки запроса.

**Обработка ошибок в resolvers**:

```javascript
const resolvers = {
  Query: {
    user: async (parent, { id }) => {
      const user = await getUserById(id);
      if (!user) {
        throw new UserInputError('User not found', {
          argumentName: 'id'
        });
      }
      return user;
    }
  }
};
```

Ошибки возвращаются в поле `errors` ответа:

```json
{
  "data": null,
  "errors": [
    {
      "message": "User not found",
      "extensions": {
        "argumentName": "id"
      }
    }
  ]
}
```

GraphQL не падает при ошибке - он возвращает частичные данные и ошибки. Это как try-catch, но на уровне API.

---

## Слайд 19: Авторизация и аутентификация (6 минут)

Авторизация в GraphQL реализуется на уровне resolvers. Это как middleware в Express, но для каждого поля.

```javascript
const resolvers = {
  Query: {
    users: (parent, args, context) => {
      if (!context.user || context.user.role !== 'ADMIN') {
        throw new ForbiddenError('Access denied');
      }
      return getAllUsers();
    }
  },
  
  User: {
    email: (user, args, context) => {
      // Пользователь может видеть только свой email
      if (context.user.id !== user.id) {
        return null;  // Или throw new Error
      }
      return user.email;
    }
  }
};
```

Авторизация на уровне полей - это мощно. Вы можете скрыть чувствительные данные от неавторизованных пользователей. Это как банк: кассир видит баланс, но не видит пин-код.

Директивы для авторизации:

```graphql
type User {
  id: ID!
  name: String!
  email: String! @auth(requires: USER)
  adminNotes: String @auth(requires: ADMIN)
}

type Query {
  users: [User!]! @auth(requires: ADMIN)
}
```

Директива `@auth` проверяет права доступа перед выполнением resolver. Это декларативный подход - вы описываете, кто может что делать, а не пишете if'ы везде.

Middleware для проверки токенов:

```javascript
context: ({ req }) => {
  const token = req.headers.authorization;
  const user = verifyToken(token);
  return { user, db: database };
}
```

Context создается для каждого запроса, поэтому вы можете проверить токен один раз и использовать `context.user` везде.

---

## Слайд 20: Пагинация (6 минут)

GraphQL поддерживает несколько подходов к пагинации. Это важно для больших списков.

**Offset-based пагинация** - классический подход:

```graphql
type Query {
  posts(offset: Int, limit: Int): [Post!]!
}

query {
  posts(offset: 20, limit: 10) {
    id
    title
  }
}
```

Проблема: если данные изменяются (добавляются/удаляются записи), offset может сбиться. Представьте, что вы читаете книгу и кто-то постоянно добавляет новые страницы в начало. Если вы запомнили номер страницы (offset), то потеряетесь.

**Cursor-based пагинация (Relay Connection)** - более надежный подход:

```graphql
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
}

type PostEdge {
  node: Post!
  cursor: String!  # Уникальный идентификатор позиции
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  posts(first: Int, after: String): PostConnection!
}
```

Cursor - это уникальный идентификатор позиции. Как закладка в книге с уникальным текстом - даже если страницы добавляются, вы всегда найдете место.

Пример из Instagram: когда вы листаете ленту и кто-то публикует новый пост, вы не теряете место просмотра, потому что используете cursor, а не offset.

```graphql
query {
  posts(first: 10, after: "cursor123") {
    edges {
      node {
        id
        title
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

Cursor-based пагинация более надежна для изменяющихся данных. Это стандарт в Relay (Facebook's GraphQL клиент).

---

## Слайд 21: Кеширование (5 минут)

Кеширование в GraphQL имеет особенности из-за гибкости запросов. Каждый запрос может быть уникальным, поэтому кеширование сложнее, чем в REST.

**Query-level кеширование** - кеширование целых запросов:

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    responseCachePlugin({
      sessionId: (requestContext) => 
        requestContext.request.http.headers.get('session-id'),
      shouldReadFromCache: (requestContext) => 
        requestContext.request.operationName !== 'GetCurrentUser'
    })
  ]
});
```

Запросы с одинаковыми переменными и session-id кешируются. Это как кеш в браузере - если запрос тот же, возвращается кешированный результат.

**Field-level кеширование** - кеширование отдельных полей:

```javascript
const resolvers = {
  User: {
    posts: async (user, args, { cache }) => {
      const cacheKey = `user:${user.id}:posts`;
      let posts = await cache.get(cacheKey);
      
      if (!posts) {
        posts = await getPostsByUserId(user.id);
        await cache.set(cacheKey, posts, { ttl: 300 });  // 5 минут
      }
      
      return posts;
    }
  }
};
```

Это как кеш в Redis - вы кешируете результаты запросов к БД, чтобы не делать их каждый раз.

**Client-side кеширование** с Apollo Client, Relay. Клиент кеширует результаты запросов и обновляет их при мутациях. Это как state management в React, но автоматический.

Кеширование в GraphQL сложнее, чем в REST, потому что запросы гибкие. Но инструменты помогают - Apollo Server, Apollo Client, Relay имеют встроенное кеширование.

---

## Слайд 22: Инструменты разработки (5 минут)

GraphQL имеет отличные инструменты разработки. Это как IDE для API.

**GraphQL Playground** - интерактивная IDE для GraphQL:
- Автодополнение запросов (как в IDE)
- Документация схемы (автоматически генерируется)
- История запросов (как в Postman)
- Переменные и заголовки

Это как швейцарский нож для разработчика. Представьте ресторан с интерактивным меню: вы можете не только посмотреть все блюда, но и сразу попробовать их, узнать состав, аллергены, и даже посмотреть, как готовит повар!

**GraphiQL** - браузерная IDE:
- Исследование схемы
- Выполнение запросов
- Валидация в реальном времени

Это как DevTools в браузере, но для GraphQL API.

**Apollo Studio** - платформа для мониторинга:
- Метрики производительности (сколько времени занимают запросы)
- Трассировка запросов (какие resolvers вызываются)
- Управление схемой (версионирование, изменения)
- Федерация сервисов (объединение нескольких GraphQL API)

Это как диспетчерская вышка в аэропорту: видите все самолеты (запросы), их маршруты, задержки и можете управлять трафиком.

**Инструменты командной строки**:
- `graphql-codegen` - генерация типов TypeScript из схемы
- `apollo-tooling` - CLI для Apollo
- `graphql-inspector` - анализ изменений схемы (breaking changes)

Эти инструменты значительно упрощают разработку и отладку. GraphQL без инструментов - это как программирование без IDE. Работает, но неудобно.

---

## Слайд 23: Apollo Server (5 минут)

Apollo Server - популярная реализация GraphQL сервера. Это как Express для REST, но для GraphQL.

```javascript
const { ApolloServer, gql } = require('apollo-server');

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
  }
  
  type Query {
    users: [User!]!
    user(id: ID!): User
  }
`;

const resolvers = {
  Query: {
    users: () => users,
    user: (parent, { id }) => users.find(user => user.id === id)
  }
};

const server = new ApolloServer({ 
  typeDefs, 
  resolvers,
  context: ({ req }) => ({
    user: getUser(req.headers.authorization)
  })
});

server.listen().then(({ url }) => {
  console.log(`Server ready at ${url}`);
});
```

Apollo Server предоставляет:
- Middleware (авторизация, логирование)
- Плагины (кеширование, метрики)
- Интеграции с различными фреймворками (Express, Koa, Fastify)
- GraphQL Playground из коробки

Это как конструктор LEGO для GraphQL. У вас есть базовые блоки (типы, резолверы), и вы можете легко добавлять новые детали (плагины, middleware). Это как собирать космический корабль - основа одна, но можете добавить лазеры, щиты, турбодвигатели.

Context в Apollo - это как рюкзак путешественника: в нем всё необходимое (данные пользователя, подключения к БД), и он доступен в любой точке маршрута.

---

## Слайд 24: GraphQL с Express.js (4 минуты)

Интеграция GraphQL с Express.js - простой способ добавить GraphQL в существующий проект.

```javascript
const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');

const schema = buildSchema(`
  type User {
    id: ID!
    name: String!
    email: String!
  }
  
  type Query {
    user(id: ID!): User
    users: [User!]!
  }
`);

const root = {
  user: ({ id }) => getUserById(id),
  users: () => getAllUsers()
};

const app = express();

app.use('/graphql', graphqlHTTP({
  schema: schema,
  rootValue: root,
  graphiql: true,  // Включает GraphiQL IDE
  context: (req) => ({
    user: getUser(req.headers.authorization)
  })
}));

app.listen(4000);
```

Простая интеграция для быстрого старта проектов. Express + GraphQL - это как добавить GPS-навигатор в обычную машину. Express - надежный автомобиль, который везет ваши данные, а GraphQL - умный навигатор, который знает, какой именно маршрут нужен каждому пассажиру.

GraphiQL: true - это как включить голосовые подсказки: "Через 200 метров поверните направо к полю 'email'".

---

## Слайд 25: Клиентские библиотеки (5 минут)

Клиентские библиотеки - это как разные виды транспорта. Каждая для своих задач.

**Apollo Client** - полнофункциональный GraphQL клиент:

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache()
});

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

client.query({ query: GET_USERS })
  .then(result => console.log(result.data));
```

Apollo Client - это Tesla Model S: много функций, автопилот (кеширование), но сложнее в управлении. Имеет встроенное кеширование, оптимистичные обновления, подписки.

**Relay** - Facebook's GraphQL клиент:
- Автоматическая пагинация
- Оптимистичные обновления
- Нормализованный кеш

Relay - это Formula 1: максимальная производительность, но нужен опытный пилот. Сложнее в настройке, но мощнее для больших приложений.

**urql** - легковесная альтернатива:
- Меньший размер bundle
- Простая настройка
- Хорошая производительность

urql - это Toyota Prius: надежно, экономично, просто. Для небольших проектов идеально.

**graphql-request** - минималистичный клиент для простых случаев:

```javascript
import { request } from 'graphql-request';

const query = `{ users { id name } }`;
const data = await request('http://localhost:4000/graphql', query);
```

graphql-request - это велосипед: легкий, быстрый старт, но только для коротких поездок. Для простых случаев, когда не нужен кеш и подписки.

Выбор зависит от проекта. Для React приложений - Apollo Client или Relay. Для простых случаев - urql или graphql-request.

---

## Слайд 26: React и GraphQL (5 минут)

Использование GraphQL в React с Apollo Client - это как peanut butter и jelly. Идеально сочетаются.

```jsx
import { useQuery, useMutation, gql } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
      email
    }
  }
`;

function UserList() {
  const { loading, error, data } = useQuery(GET_USERS);
  const [createUser] = useMutation(CREATE_USER, {
    refetchQueries: [{ query: GET_USERS }]
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      {data.users.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}
```

React Hooks с GraphQL - это как умный холодильник. `useQuery` - это датчик, который автоматически проверяет, есть ли еда (данные), и сообщает, когда нужно сходить в магазин (загрузка). `useMutation` - это кнопка заказа продуктов на дом: нажал и обновил содержимое.

Loading состояние - это как мигающий индикатор "идет загрузка" на микроволновке. А `refetchQueries` - это как автоматическое обновление списка продуктов после доставки.

Hooks упрощают работу с GraphQL в функциональных компонентах. Нет need в class components, нет need в HOCs. Просто hooks и всё работает.

---

## Слайд 27: Тестирование GraphQL (5 минут)

Тестирование GraphQL - это как проверка качества в ресторане. Нужно проверить каждое блюдо.

**Unit тестирование resolvers**:

```javascript
const { user } = require('./resolvers');

describe('User resolver', () => {
  test('should return user by id', async () => {
    const mockContext = {
      db: {
        getUserById: jest.fn().mockResolvedValue({
          id: '1',
          name: 'John Doe'
        })
      }
    };

    const result = await user(null, { id: '1' }, mockContext);
    
    expect(result).toEqual({
      id: '1',
      name: 'John Doe'
    });
  });
});
```

Unit тесты резолверов - проверяете каждое блюдо отдельно: "А правильно ли повар готовит борщ?". Mock'и - это как муляжи еды в витрине: выглядят как настоящие, но есть нельзя, зато можно показать клиенту, что будет.

**Integration тестирование**:

```javascript
const { createTestClient } = require('apollo-server-testing');
const { server } = require('./server');

const { query } = createTestClient(server);

test('should fetch users', async () => {
  const GET_USERS = gql`
    query {
      users {
        id
        name
      }
    }
  `;

  const res = await query({ query: GET_USERS });
  expect(res.data.users).toHaveLength(2);
});
```

Integration тесты - проверяете весь обед целиком: "А получается ли полноценный обед из салата, супа и десерта?". Тестируете весь запрос от начала до конца, включая валидацию, resolvers, БД.

Тестирование GraphQL проще, чем REST, потому что:
- Один endpoint (легче тестировать)
- Строгая типизация (меньше edge cases)
- Интроспекция (можно генерировать тесты из схемы)

---

## Слайд 28: Производительность и оптимизация (6 минут)

Производительность в GraphQL - это важно. Гибкость запросов может привести к проблемам, если не оптимизировать.

**Проблема N+1 запросов** - классическая проблема:

```javascript
// Плохо: N+1 запросов к базе данных
const resolvers = {
  Post: {
    author: (post) => getUserById(post.authorId)  // Запрос для каждого поста
  }
};
```

Если у вас 10 постов, вы делаете 11 запросов (1 для постов + 10 для авторов). Это как если бы вы, читая книгу о 100 авторах, для каждого автора отдельно шли в библиотеку за его биографией.

```javascript
// Хорошо: DataLoader группирует запросы
const resolvers = {
  Post: {
    author: (post, args, { userLoader }) => userLoader.load(post.authorId)
  }
};
```

DataLoader - это как умный помощник, который говорит: "Стоп! Дайте мне список всех авторов, я схожу один раз и принесу все биографии сразу". Вместо 11 запросов - 2 запроса.

**Query complexity analysis** - ограничение сложности запросов:

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    require('graphql-query-complexity').createComplexityLimitRule(1000)
  ]
});
```

Query complexity - это как ограничение на количество блюд в ресторане: нельзя заказать 50 салатов и 30 супов одновременно, иначе кухня встанет. Каждое поле имеет "стоимость", и сумма не должна превышать лимит.

**Query depth limiting** - ограничение глубины вложенности:

```javascript
const depthLimit = require('graphql-depth-limit');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(7)]
});
```

Это предотвращает глубокие вложенные запросы типа `user { posts { author { posts { author { ... } } } } }`. Как ограничение на этажность здания - не выше 7 этажей без специального пропуска.

**Persistent queries** - кеширование запросов на сервере. Клиент отправляет hash запроса, сервер знает, что это за запрос. Уменьшает размер запросов и улучшает безопасность.

---

## Слайд 29: Безопасность GraphQL (6 минут)

Безопасность GraphQL - это важно. Гибкость запросов может быть использована злоумышленниками.

**Query depth limiting** - предотвращает глубокие вложенные запросы:

```javascript
const depthLimit = require('graphql-depth-limit');
app.use('/graphql', graphqlHTTP({
  schema,
  validationRules: [depthLimit(10)]
}));
```

Это как ограничение "не выше 10 этажа без специального пропуска", иначе злоумышленник может построить башню до небес и уронить сервер.

**Query complexity analysis** - ограничивает сложность запросов:

```javascript
const costAnalysis = require('graphql-cost-analysis');
app.use('/graphql', graphqlHTTP({
  schema,
  validationRules: [costAnalysis.maximumCostRule(1000)]
}));
```

Каждое поле имеет "стоимость". Запрос не должен превышать лимит. Это как лимит на кредитной карте - нельзя потратить больше, чем разрешено.

**Rate limiting** - ограничивает количество запросов:

```javascript
const rateLimit = require('express-rate-limit');
app.use('/graphql', rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 минут
  max: 100  // максимум 100 запросов
}));
```

Это турникет: "не больше 100 человек в час". Предотвращает DDoS атаки и злоупотребления.

**Whitelist queries** в продакшене:
- Только предварительно одобренные запросы
- Предотвращает произвольные запросы
- Улучшает кеширование

Whitelist queries - это как VIP-список на вечеринке: "только те запросы, которые мы заранее одобрили". В продакшене можно разрешить только известные запросы, а произвольные блокировать.

**Авторизация на уровне полей** для защиты чувствительных данных:

```javascript
User: {
  email: (user, args, context) => {
    if (context.user.id !== user.id) {
      return null;  // Скрыть email от других пользователей
    }
    return user.email;
  }
}
```

Это как в банке: кассир видит баланс, но не видит пин-код. Авторизация на уровне полей позволяет скрыть чувствительные данные от неавторизованных пользователей.

Безопасность GraphQL требует внимания, но инструменты помогают. Главное - не забывать про эти меры защиты.

---

## Слайд 30: Будущее GraphQL и заключение (7 минут)

GraphQL активно развивается. Давайте посмотрим на тренды.

**Текущие тренды**:
- **GraphQL Federation** - объединение нескольких GraphQL сервисов в один. Это как микросервисы, но с единым API. Каждый сервис управляет своей частью схемы, но клиент видит единый GraphQL API.
- **Real-time subscriptions** - WebSocket, Server-Sent Events. Подписки становятся стандартом для real-time приложений.
- **GraphQL over HTTP/2** - улучшенная производительность. HTTP/2 позволяет мультиплексировать запросы.
- **Automatic persisted queries** - кеширование запросов на сервере. Клиент отправляет hash, сервер знает запрос.

**Новые возможности**:
- **@defer и @stream директивы** - потоковая передача данных. Можно отправить часть данных сразу, остальное - позже. Это как прогрессивная загрузка видео: сначала показываем картинку, потом звук, потом HD качество.
- **GraphQL Modules** - модульная архитектура. Разделение схемы на модули для лучшей организации кода.
- **Code-first подход** - генерация схемы из кода. Вместо SDL вы пишете код, схема генерируется автоматически.

Federation - это как объединение разных приложений в одном устройстве: камера, плеер, навигатор работают вместе, но каждое - отдельный сервис. Это позволяет масштабировать GraphQL API на множество сервисов.

**Заключение**:
GraphQL революционизирует разработку API, предоставляя:
- Гибкость запросов данных (клиент решает, что нужно)
- Строгую типизацию (меньше ошибок, лучше IDE)
- Отличный developer experience (инструменты, автодополнение)
- Мощную экосистему инструментов (Apollo, Relay, GraphiQL)

GraphQL не заменяет REST полностью, но решает многие его проблемы. Выбор между GraphQL и REST зависит от требований проекта, команды и архитектуры системы.

GraphQL vs REST - это не война мечей против пистолетов, это выбор инструмента под задачу. REST - это отвертка: простая, надежная, везде работает. GraphQL - это шуруповерт: мощнее, быстрее, но нужно зарядить батарею и изучить инструкцию. Иногда нужна отвертка, иногда - шуруповерт, а иногда - оба сразу!

**Рекомендации для изучения**:
1. Практикуйтесь с GraphQL Playground - это лучший способ изучить GraphQL
2. Изучите Apollo Server и Client - это стандарт индустрии
3. Попробуйте интеграцию с React/Vue - увидите, как это работает на практике
4. Изучите паттерны проектирования схем - это поможет создавать хорошие API
5. Рассмотрите GraphQL Federation для микросервисов - это будущее больших систем

GraphQL - это не просто технология, это новый способ думать об API. Вместо "что может сервер?" думайте "что нужно клиенту?". Это смена парадигмы, и она здесь, чтобы остаться.

---

## Время для вопросов (5 минут)

Отлично, мы прошли весь материал. GraphQL - это мощный инструмент, который решает реальные проблемы REST API. Гибкость, типизация, инструменты - всё это делает разработку приятнее.

Вопросы? Давайте обсудим!

---

**Итого: 90 минут**
- Вступление: 5 мин
- Слайды 1-30: 75 мин (примерно 2.5 мин на слайд)
- Вопросы: 5 мин
- Резерв: 5 мин
