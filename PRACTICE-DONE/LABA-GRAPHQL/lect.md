# Лекция: GraphQL - Современный подход к API

## Слайд 1: Введение в GraphQL
**Время: 3 минуты**

GraphQL - это язык запросов для API и среда выполнения для обработки этих запросов. Разработан Facebook в 2012 году, открыт в 2015. GraphQL решает проблемы традиционных REST API: over-fetching, under-fetching и множественные запросы.

Основные преимущества:
- Клиент запрашивает только нужные данные
- Один endpoint для всех операций
- Строгая типизация
- Интроспекция API
- Реальное время через подписки

GraphQL не привязан к конкретной базе данных или языку программирования - это спецификация, которая может быть реализована на любой платформе.

---

## Слайд 2: Проблемы REST API
**Время: 3 минуты**

REST API имеет несколько фундаментальных проблем:

**Over-fetching**: Получение избыточных данных. Например, запрос пользователя возвращает все поля, когда нужны только имя и email.

**Under-fetching**: Недостаток данных в одном запросе. Для получения пользователя и его постов нужно делать несколько запросов.

**Множественные endpoints**: Разные ресурсы требуют разных URL (/users, /posts, /comments).

**Версионирование**: Изменения API требуют новых версий (/api/v1, /api/v2).

**Слабая типизация**: Нет четкого контракта между клиентом и сервером.

GraphQL решает эти проблемы, предоставляя единый endpoint с гибкой системой запросов.

---

## Слайд 3: Основные концепции GraphQL
**Время: 3 минуты**

GraphQL построен на нескольких ключевых концепциях:

**Schema** - описание API, определяющее доступные типы данных и операции.

**Types** - строго типизированные объекты (User, Post, Comment).

**Fields** - свойства типов (name, email, createdAt).

**Queries** - операции чтения данных.

**Mutations** - операции изменения данных.

**Subscriptions** - операции для получения данных в реальном времени.

**Resolvers** - функции, которые получают данные для каждого поля.

Эти концепции работают вместе, создавая мощную и гибкую систему для работы с данными.

---

## Слайд 4: GraphQL Schema Definition Language (SDL)
**Время: 3 минуты**

SDL - это синтаксис для описания GraphQL схем. Основные элементы:

```graphql
# Скалярные типы
scalar Date

# Объектные типы
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  createdAt: Date!
}

# Корневые типы
type Query {
  users: [User!]!
  user(id: ID!): User
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}
```

Восклицательный знак (!) означает обязательное поле. Квадратные скобки [] обозначают массив.

---

## Слайд 5: Скалярные типы
**Время: 3 минуты**

GraphQL предоставляет встроенные скалярные типы:

**String** - UTF-8 строки
```graphql
name: String!
```

**Int** - 32-битные целые числа
```graphql
age: Int
```

**Float** - числа с плавающей точкой
```graphql
price: Float!
```

**Boolean** - true/false
```graphql
isActive: Boolean!
```

**ID** - уникальный идентификатор
```graphql
id: ID!
```

Можно создавать пользовательские скалярные типы:
```graphql
scalar Date
scalar Email
scalar URL
```

Пользовательские скаляры требуют реализации сериализации, парсинга и валидации.

---

## Слайд 6: Объектные типы
**Время: 3 минуты**

Объектные типы - основа GraphQL схемы. Они описывают структуру данных:

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  age: Int
  posts: [Post!]!
  profile: Profile
}

type Profile {
  bio: String
  avatar: String
  website: URL
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  tags: [String!]!
  publishedAt: Date
}
```

Поля могут быть:
- Скалярными значениями
- Другими объектными типами
- Массивами
- Nullable или Non-null

Связи между типами создают граф данных, отсюда название GraphQL.

---

## Слайд 7: Enum и Union типы
**Время: 3 минуты**

**Enum типы** ограничивают значения определенным набором:

```graphql
enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

enum UserRole {
  ADMIN
  MODERATOR
  USER
}

type Post {
  id: ID!
  title: String!
  status: PostStatus!
}
```

**Union типы** позволяют полю возвращать один из нескольких типов:

```graphql
union SearchResult = User | Post | Comment

type Query {
  search(query: String!): [SearchResult!]!
}
```

При использовании Union нужны inline fragments для обработки разных типов:

```graphql
query {
  search(query: "GraphQL") {
    ... on User { name }
    ... on Post { title }
  }
}
```

---

## Слайд 8: Interface типы
**Время: 3 минуты**

Interface определяет общие поля для группы типов:

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

type Query {
  node(id: ID!): Node
}
```

Типы, реализующие интерфейс, должны включать все его поля. Interface полезны для:
- Общих операций (получение по ID)
- Полиморфных связей
- Переиспользования логики

При запросе интерфейса используются inline fragments для доступа к специфичным полям типов.

---

## Слайд 9: Input типы
**Время: 3 минуты**

Input типы используются для передачи сложных данных в мутации и запросы:

```graphql
input CreateUserInput {
  name: String!
  email: String!
  age: Int
  profileInput: ProfileInput
}

input ProfileInput {
  bio: String
  avatar: String
  website: String
}

input UpdateUserInput {
  name: String
  email: String
  age: Int
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
}
```

Input типы:
- Не могут содержать поля объектных типов
- Могут содержать только скаляры, enum, другие input типы и массивы
- Обеспечивают валидацию входных данных
- Делают API более читаемым

---

## Слайд 10: Директивы
**Время: 3 минуты**

Директивы изменяют выполнение запросов. Встроенные директивы:

**@include** - включает поле при условии:
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

**@skip** - пропускает поле при условии:
```graphql
query GetUser($skipEmail: Boolean!) {
  user(id: "1") {
    name
    email @skip(if: $skipEmail)
  }
}
```

**@deprecated** - помечает поле как устаревшее:
```graphql
type User {
  name: String!
  fullName: String! @deprecated(reason: "Use name instead")
}
```

Можно создавать пользовательские директивы для валидации, авторизации, кеширования.

---

## Слайд 11: Queries - Основы запросов
**Время: 3 минуты**

Query - операция чтения данных. Базовый синтаксис:

```graphql
query {
  users {
    id
    name
    email
  }
}
```

Запросы с аргументами:
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

Клиент получает точно те данные, которые запросил, в том же формате.

---

## Слайд 12: Aliases и Fragments
**Время: 3 минуты**

**Aliases** позволяют переименовывать поля в результате:

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

**Fragments** переиспользуют наборы полей:

```graphql
fragment UserInfo on User {
  id
  name
  email
}

query {
  user(id: "123") {
    ...UserInfo
    posts {
      title
    }
  }
  
  users {
    ...UserInfo
  }
}
```

**Inline fragments** для условной выборки:
```graphql
query {
  search(query: "test") {
    ... on User {
      name
    }
    ... on Post {
      title
    }
  }
}
```

---

## Слайд 13: Переменные в запросах
**Время: 3 минуты**

Переменные делают запросы динамическими и безопасными:

```graphql
query GetUser($id: ID!, $includeEmail: Boolean = false) {
  user(id: $id) {
    name
    email @include(if: $includeEmail)
    posts(first: 10) {
      title
      content
    }
  }
}
```

Переменные передаются отдельно от запроса:
```json
{
  "query": "query GetUser($id: ID!) { ... }",
  "variables": {
    "id": "123",
    "includeEmail": true
  }
}
```

Типы переменных:
- Обязательные: `$id: ID!`
- Опциональные: `$limit: Int`
- С значением по умолчанию: `$limit: Int = 10`

Переменные предотвращают SQL-инъекции и позволяют кешировать запросы.

---

## Слайд 14: Mutations - Изменение данных
**Время: 3 минуты**

Mutations изменяют данные на сервере:

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
  }
}
```

Множественные мутации выполняются последовательно:
```graphql
mutation {
  createPost(input: {title: "Post 1", content: "..."}) {
    id
  }
  createPost(input: {title: "Post 2", content: "..."}) {
    id
  }
}
```

Мутации должны возвращать измененные данные:
```graphql
type Mutation {
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
  createPost(input: CreatePostInput!): Post!
}
```

Хорошая практика - возвращать объект с полезной нагрузкой и ошибками.

---

## Слайд 15: Subscriptions - Реальное время
**Время: 3 минуты**

Subscriptions обеспечивают получение данных в реальном времени:

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

Подписки идеальны для чатов, уведомлений, live-обновлений, collaborative editing.

---

## Слайд 16: Resolvers - Получение данных
**Время: 3 минуты**

Resolvers - функции, которые получают данные для каждого поля:

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
- **parent** - результат родительского resolver
- **args** - аргументы поля
- **context** - общий контекст (пользователь, база данных)
- **info** - метаинформация о запросе

---

## Слайд 17: Context и DataLoader
**Время: 3 минуты**

**Context** передает общие данные между resolvers:

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

**DataLoader** решает проблему N+1 запросов:

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

DataLoader группирует запросы и кеширует результаты в рамках одного запроса.

---

## Слайд 18: Валидация и ошибки
**Время: 3 минуты**

GraphQL выполняет валидацию на нескольких уровнях:

**Синтаксическая валидация** - проверка корректности запроса:
```graphql
# Ошибка: отсутствует закрывающая скобка
query {
  user(id: "123" {
    name
  }
```

**Валидация схемы** - проверка соответствия типам:
```graphql
# Ошибка: поле age не существует в типе User
query {
  user(id: "123") {
    name
    age
  }
}
```

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

Ошибки возвращаются в поле `errors` ответа.

---

## Слайд 19: Авторизация и аутентификация
**Время: 3 минуты**

Авторизация в GraphQL реализуется на уровне resolvers:

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
        return null;
      }
      return user.email;
    }
  }
};
```

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

Middleware для проверки токенов, ролей, разрешений.

---

## Слайд 20: Пагинация
**Время: 3 минуты**

GraphQL поддерживает несколько подходов к пагинации:

**Offset-based пагинация**:
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

**Cursor-based пагинация (Relay Connection)**:
```graphql
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
}

type PostEdge {
  node: Post!
  cursor: String!
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

Cursor-based пагинация более надежна для изменяющихся данных.

**Для лектора**: Представьте, что вы читаете книгу и кто-то постоянно добавляет новые страницы в начало. Если вы запомнили номер страницы (offset), то потеряетесь. А если запомнили закладку с уникальным текстом (cursor) - всегда найдете место! Как в Instagram - когда вы листаете ленту и кто-то публикует новый пост, вы не теряете место просмотра.

---

## Слайд 21: Кеширование
**Время: 3 минуты**

Кеширование в GraphQL имеет особенности из-за гибкости запросов:

**Query-level кеширование**:
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

**Field-level кеширование**:
```javascript
const resolvers = {
  User: {
    posts: async (user, args, { cache }) => {
      const cacheKey = `user:${user.id}:posts`;
      let posts = await cache.get(cacheKey);
      
      if (!posts) {
        posts = await getPostsByUserId(user.id);
        await cache.set(cacheKey, posts, { ttl: 300 });
      }
      
      return posts;
    }
  }
};
```

**Client-side кеширование** с Apollo Client, Relay.

---

## Слайд 22: Инструменты разработки
**Время: 3 минуты**

**GraphQL Playground** - интерактивная IDE для GraphQL:
- Автодополнение запросов
- Документация схемы
- История запросов
- Переменные и заголовки

**GraphiQL** - браузерная IDE:
- Исследование схемы
- Выполнение запросов
- Валидация в реальном времени

**Apollo Studio** - платформа для мониторинга:
- Метрики производительности
- Трассировка запросов
- Управление схемой
- Федерация сервисов

**Инструменты командной строки**:
- `graphql-codegen` - генерация типов
- `apollo-tooling` - CLI для Apollo
- `graphql-inspector` - анализ изменений схемы

Эти инструменты значительно упрощают разработку и отладку.

**Для лектора**: GraphQL Playground - это как швейцарский нож для разработчика. Представьте, что вы пришли в ресторан, где меню интерактивное: вы можете не только посмотреть все блюда, но и сразу попробовать их, узнать состав, аллергены, и даже посмотреть, как готовит повар! Apollo Studio - это как диспетчерская вышка в аэропорту: видите все самолеты (запросы), их маршруты, задержки и можете управлять трафиком.

---

## Слайд 23: Apollo Server
**Время: 3 минуты**

Apollo Server - популярная реализация GraphQL сервера:

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

Apollo Server предоставляет middleware, плагины, интеграции с различными фреймворками.

**Для лектора**: Apollo Server - это как конструктор LEGO для GraphQL. У вас есть базовые блоки (типы, резолверы), и вы можете легко добавлять новые детали (плагины, middleware). Это как собирать космический корабль - основа одна, но можете добавить лазеры, щиты, турбодвигатели. Context в Apollo - это как рюкзак путешественника: в нем всё необходимое (данные пользователя, подключения к БД), и он доступен в любой точке маршрута.

---

## Слайд 24: GraphQL с Express.js
**Время: 3 минуты**

Интеграция GraphQL с Express.js:

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
  graphiql: true, // Включает GraphiQL IDE
  context: (req) => ({
    user: getUser(req.headers.authorization)
  })
}));

app.listen(4000);
```

Простая интеграция для быстрого старта проектов.

**Для лектора**: Express + GraphQL - это как добавить GPS-навигатор в обычную машину. Express - надежный автомобиль, который везет ваши данные, а GraphQL - умный навигатор, который знает, какой именно маршрут нужен каждому пассажиру. GraphiQL: true - это как включить голосовые подсказки: "Через 200 метров поверните направо к полю 'email'".

---

## Слайд 25: Клиентские библиотеки
**Время: 3 минуты**

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

**Relay** - Facebook's GraphQL клиент:
- Автоматическая пагинация
- Оптимистичные обновления
- Нормализованный кеш

**urql** - легковесная альтернатива:
- Меньший размер bundle
- Простая настройка
- Хорошая производительность

**graphql-request** - минималистичный клиент для простых случаев.

**Для лектора**: Клиентские библиотеки - это как разные виды транспорта. Apollo Client - это Tesla Model S: много функций, автопилот (кеширование), но сложнее в управлении. Relay - это Formula 1: максимальная производительность, но нужен опытный пилот. urql - это Toyota Prius: надежно, экономично, просто. graphql-request - это велосипед: легкий, быстрый старт, но только для коротких поездок.

---

## Слайд 26: React и GraphQL
**Время: 3 минуты**

Использование GraphQL в React с Apollo Client:

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

Hooks упрощают работу с GraphQL в функциональных компонентах.

**Для лектора**: React Hooks с GraphQL - это как умный холодильник. useQuery - это датчик, который автоматически проверяет, есть ли еда (данные), и сообщает, когда нужно сходить в магазин (загрузка). useMutation - это кнопка заказа продуктов на дом: нажал и обновил содержимое. Loading состояние - это как мигающий индикатор "идет загрузка" на микроволновке. А refetchQueries - это как автоматическое обновление списка продуктов после доставки.

---

## Слайд 27: Тестирование GraphQL
**Время: 3 минуты**

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

**Для лектора**: Тестирование GraphQL - это как проверка качества в ресторане. Unit тесты резолверов - проверяете каждое блюдо отдельно: "А правильно ли повар готовит борщ?". Integration тесты - проверяете весь обед целиком: "А получается ли полноценный обед из салата, супа и десерта?". Mock'и - это как муляжи еды в витрине: выглядят как настоящие, но есть нельзя, зато можно показать клиенту, что будет.

---

## Слайд 28: Производительность и оптимизация
**Время: 3 минуты**

**Проблема N+1 запросов**:
```javascript
// Плохо: N+1 запросов к базе данных
const resolvers = {
  Post: {
    author: (post) => getUserById(post.authorId) // Запрос для каждого поста
  }
};

// Хорошо: DataLoader группирует запросы
const resolvers = {
  Post: {
    author: (post, args, { userLoader }) => userLoader.load(post.authorId)
  }
};
```

**Query complexity analysis**:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    require('graphql-query-complexity').createComplexityLimitRule(1000)
  ]
});
```

**Query depth limiting**:
```javascript
const depthLimit = require('graphql-depth-limit');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(7)]
});
```

**Persistent queries** для уменьшения размера запросов.

**Для лектора**: N+1 проблема - это как если бы вы, читая книгу о 100 авторах, для каждого автора отдельно шли в библиотеку за его биографией. DataLoader - это как умный помощник, который говорит: "Стоп! Дайте мне список всех авторов, я схожу один раз и принесу все биографии сразу". Query complexity - это как ограничение на количество блюд в ресторане: нельзя заказать 50 салатов и 30 супов одновременно, иначе кухня встанет.

---

## Слайд 29: Безопасность GraphQL
**Время: 3 минуты**

**Query depth limiting** предотвращает глубокие вложенные запросы:
```javascript
const depthLimit = require('graphql-depth-limit');
app.use('/graphql', graphqlHTTP({
  schema,
  validationRules: [depthLimit(10)]
}));
```

**Query complexity analysis** ограничивает сложность запросов:
```javascript
const costAnalysis = require('graphql-cost-analysis');
app.use('/graphql', graphqlHTTP({
  schema,
  validationRules: [costAnalysis.maximumCostRule(1000)]
}));
```

**Rate limiting** ограничивает количество запросов:
```javascript
const rateLimit = require('express-rate-limit');
app.use('/graphql', rateLimit({
  windowMs: 15 * 60 * 1000, // 15 минут
  max: 100 // максимум 100 запросов
}));
```

**Whitelist queries** в продакшене:
- Только предварительно одобренные запросы
- Предотвращает произвольные запросы
- Улучшает кеширование

**Авторизация на уровне полей** для защиты чувствительных данных.

**Для лектора**: Безопасность GraphQL - это как охрана в многоэтажном офисном здании. Query depth limiting - это как ограничение "не выше 10 этажа без специального пропуска", иначе злоумышленник может построить башню до небес. Rate limiting - это турникет: "не больше 100 человек в час". Whitelist queries - это как VIP-список на вечеринке: "только те запросы, которые мы заранее одобрили". А авторизация на уровне полей - это как в банке: кассир видит баланс, но не видит пин-код.

---

## Слайд 30: Будущее GraphQL и заключение
**Время: 3 минуты**

**Текущие тренды**:
- **GraphQL Federation** - объединение нескольких GraphQL сервисов
- **Real-time subscriptions** - WebSocket, Server-Sent Events
- **GraphQL over HTTP/2** - улучшенная производительность
- **Automatic persisted queries** - кеширование запросов

**Новые возможности**:
- **@defer и @stream директивы** - потоковая передача данных
- **GraphQL Modules** - модульная архитектура
- **Code-first подход** - генерация схемы из кода

**Заключение**:
GraphQL революционизирует разработку API, предоставляя:
- Гибкость запросов данных
- Строгую типизацию
- Отличный developer experience
- Мощную экосистему инструментов

GraphQL не заменяет REST полностью, но решает многие его проблемы. Выбор между GraphQL и REST зависит от требований проекта, команды и архитектуры системы.

**Рекомендации для изучения**:
1. Практикуйтесь с GraphQL Playground
2. Изучите Apollo Server и Client
3. Попробуйте интеграцию с React/Vue
4. Изучите паттерны проектирования схем
5. Рассмотрите GraphQL Federation для микросервисов

**Для лектора**: Будущее GraphQL - это как эволюция от телефона к смартфону. Federation - это как объединение разных приложений в одном устройстве: камера, плеер, навигатор работают вместе, но каждое - отдельный сервис. @defer и @stream - это как прогрессивная загрузка видео: сначала показываем картинку, потом звук, потом HD качество. 

GraphQL vs REST - это не война мечей против пистолетов, это выбор инструмента под задачу. REST - это отвертка: простая, надежная, везде работает. GraphQL - это шуруповерт: мощнее, быстрее, но нужно зарядить батарею и изучить инструкцию. Иногда нужна отвертка, иногда - шуруповерт, а иногда - оба сразу!