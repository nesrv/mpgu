# Лекция: проектирование архитектуры потоковых приложений на основе RabbitMQ

**Аудитория:** студенты курса по высоконагруженным системам.  
**Опора:** устройство узла RabbitMQ и модель AMQP (exchange → binding → queue → consumer), лабораторный проект с WebSocket и воркером (`containers-architecture.mmd`).

**Дисклеймер:** примеры с продуктами рунета (**ВКонтакте**, **Рутуб**, **Озон**, **MAX** и т.д.) иллюстрируют **класс шаблонов**; внутренняя реализация у вендоров может опираться на Kafka, собственные брокеры и иные стеки. На лекции важны **роли компонентов**, а не маркетинг стека.

---

## Карта лекции

| Блок | Слайды (ориентир) | Содержание |
|------|-------------------|------------|
| Устройство RabbitMQ | 1–7 | Узел брокера, AMQP, vhost/connection/channel, путь сообщения, типы exchange, очереди и UI (**у каждого слайда — блок «На пальцах»**) |
| Ввод в тему лекции | 8–11 | Цели, потоковые приложения, зачем брокер, резюме модели маршрутизации |
| Паттерны | 12–26 | Буфер, воркеры, pub/sub, routing, topic, pipeline, **роль worker в лабе**, WebSocket, RPC |
| Надёжность и эксплуатация | 27–32 | Ack, DLX, идемпотентность, порядок, prefetch |
| Выводы | 33–34 | Чеклист, сравнение с Kafka, итог |

У **каждого** слайда ниже перед блоком **На экран** есть **На пальцах** — короткое устное объяснение «для человека», плюс на слайде 2 таблица «почта» и на слайде 3 деталь про vhost.

После **каждой** Mermaid-схемы добавлен блок **«Примерно в Docker Compose»** — не полный продакшен-файл, а **фрагмент** `services:` (образ `rabbitmq:3-management`, порты **5672** / **15672**). Полный compose смотрите в **методичке лабы** / `docker-compose` проекта; на слайдах **17–18** фрагмент максимально близок к учебному чату.

---

## Слайд 1. RabbitMQ как брокер: что это за узел

**На пальцах:**

- Это **посредник-почтальон** между программами: одна кладёт «письма» (сообщения), другая забирает, когда готова. Сам посредник **помнит** очередь, если получатель временно выключен.
- **Не база данных** и не замена Postgres: он для **очередей и маршрутов**, а не для сложных запросов к данным.
- Порт **5672** — «разговор программ»; **15672** — **сайт в браузере**, где смотрят очереди руками (если плагин включён).

**На экран:**

- **Брокер сообщений** принимает сообщения от **продьюсеров**, хранит их в **очередях** (по правилам) и отдаёт **консьюмерам** по протоколу **AMQP 0-9-1** (в типичном клиенте).
- Узел работает на **Erlang VM**; метаданные (очереди, exchange, bindings) и состояние — внутренняя подсистема брокера; сообщения — в **хранилище** (память и/или диск в зависимости от настроек и версии).
- Порты по умолчанию: **5672** — клиентский AMQP; **15672** — веб-интерфейс **Management** (если включён плагин).

**Схема: приложения и один брокер**

```mermaid
flowchart TB
  subgraph apps [Клиентские процессы]
    P1[Producer]
    P2[Producer]
    C1[Consumer]
    C2[Consumer]
  end
  subgraph node [Узел RabbitMQ]
    L[AMQP :5672]
    UI[Management :15672]
    R[Маршрутизация и очереди]
    S[(Хранилище сообщений)]
    L <--> R
    R <--> S
    UI -.->|метрики и конфиг| R
  end
  P1 -->|TCP| L
  P2 -->|TCP| L
  L -->|TCP| C1
  L -->|TCP| C2
```

**Примерно в Docker Compose** (один брокер; приложения-продьюсеры/консьюмеры — отдельные сервисы или один образ с разным `command`):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
  producer:
    build: .
    command: python producer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  consumer:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** что значит «говорить с брокером по AMQP» — на **слайде 2**; на лекции не углубляемся в **кластер** и **зеркалирование** классических очередей — акцент на **логической** модели, которую вы проектируете в приложении.

---

## Слайд 2. AMQP на «пальцах»: о чём договариваются клиент и брокер

**На пальцах:** программы не шлют друг другу файлы в чат — они говорят с **одним сервером (брокером)** строгим «языком» **AMQP**: «положи вот это сюда», «дай мне следующее из той очереди», «я обработал — убери». Это **не HTTP** и не обязательно JSON; библиотека сама упакует байты.

**На экран:**

- **AMQP** (в RabbitMQ — версия **0-9-1**) — это не «ещё один JSON поверх HTTP», а **бинарный протокол поверх TCP**: клиент и брокер обмениваются **кадрами** (frames) — строго оформленными порциями данных.
- Представьте **разговор по шагам**: сначала «здравствуйте, я такой-то пользователь и хочу работать в таком-то **vhost**», потом «открой мне **канал**», потом «вот **очередь** / **exchange** / **привязка**», потом «**кладу** сообщение» или «**забираю** и **подтверждаю**».
- Ваш код на **Python** вызывает `channel.basic_publish`, `basic_consume`, `queue_declare` — библиотека **переводит** это в те самые AMQP-кадры; вам не нужно писать байты вручную, но полезно понимать **логический** смысл команд.

**Аналогия «почта»:**

| AMQP-идея | На пальцах |
|-----------|------------|
| **Сообщение** | Письмо с конвертом: **тело** (payload) + **свойства** (доставка, тип контента, свои заголовки) |
| **Exchange** | **Сортировочный центр**: письмо сюда попало, дальше решают **правила** и **маршрут** |
| **Binding** | Правило «если ключ/тип такой-то — положить копию в **эту** ячейку (очередь)» |
| **Queue** | **Ящик** с письмами, которые **ждут** получателя; брокер **хранит**, пока не заберут и не подтвердят |
| **Consumer** | Тот, кто **забирает** из ящика; **ack** — «прочитал, можно выкинуть из очереди» |

**Схема: не «в очередь напрямую», а через логику маршрутизации**

```mermaid
flowchart LR
  APP[Ваш код] -->|AMQP-кадры по TCP| BR[Брокер]
  subgraph idea [Что вы заказываете словами]
    P[basic.publish в exchange]
    R[basic.consume из queue]
    A[basic.ack / nack]
  end
  APP -.-> idea
```

**Примерно в Docker Compose** (минимум: брокер + одно приложение, которое и публикует, и читает):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:**

- **Не путать** AMQP с **JMS** или с «просто положили JSON в Redis» — у AMQP своя модель **маршрутизации** (exchange + bindings), а не только «список в базе».
- В спецификации много деталей (**транзакции** канала, редко используемые режимы); на практике в курсе важны **publish**, **consume**, **ack**, **declare** для очередей/exchange/bindings.
- Следующие слайды разбирают **где** живут vhost, канал и очередь в этой картине.

---

## Слайд 3. Virtual host: изоляция «песочниц»

**На пальцах:**

- Представьте **один физический RabbitMQ** как **дом**. **Vhost** — это **отдельные квартиры** в этом доме: в каждой свои «вещи» с одинаковыми подписями.
- Очередь с именем `tasks` в vhost **`/shop`** и очередь `tasks` в vhost **`/billing`** — это **две разные очереди**. Они **не видят** друг друга и **не пересекаются**.
- Клиент при подключении указывает **в какую квартиру заходить** — в AMQP URI это кусок после хоста, например: `amqp://user:pass@rabbit:5672/` (vhost по умолчанию) или `amqp://user:pass@rabbit:5672/production` (vhost `production`). Без правильного vhost вы «стоите в подъезде не там» — не увидите свои очереди.
- **Зачем:** одна железка/контейнер брокера на всю компанию, а **изоляция** между командами, средами (**dev / prod**) и приложениями — без риска, что кто-то случайно **удалит или прочитает** чужие очереди (если выдать права только на свой vhost).

**На экран:**

- **Virtual host (vhost)** — логическое **пространство имён** внутри узла: свои exchange, очереди, bindings; отдельно настраиваются **права пользователей** «только на этот vhost».
- В учебной лабе обычно **один** vhost по умолчанию **`/`** — как одна квартира на весь курс; в проде часто **`/prod`**, **`/staging`** или vhost **на сервис** (`/shop`, `/billing`).
- **Не путать** с **Docker-контейнером**: vhost — это **не** отдельный процесс, а **логический** разделитель **внутри** одного брокера.

**Схема: один брокер, несколько vhost**

```mermaid
flowchart TB
  subgraph broker [Один узел RabbitMQ]
    subgraph v1 [/ vhost: /shop]
      X1[Exchange...]
      Q1[(Queues...)]
    end
    subgraph v2 [/ vhost: /billing]
      X2[Exchange...]
      Q2[(Queues...)]
    end
  end
  subgraph clients [Сервисы]
    A[Сервис витрины]
    B[Сервис оплат]
  end
  A -->|AMQP + vhost /shop| v1
  B -->|AMQP + vhost /billing| v2
```

**Примерно в Docker Compose** (один контейнер **rabbitmq**; разные vhost задаются в UI или при инициализации; приложения отличаются **URI**):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  shop-api:
    build: ./shop
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/shop
  billing-api:
    build: ./billing
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/billing
```

**Подробнее:** если vhost не трогали в Management UI, у вас почти наверняка есть только **`/`** — этого достаточно для лабы. Когда вырастете до общего брокера на несколько команд — заведите **отдельные vhost** и пользователей с узкими правами.

---

## Слайд 4. Соединение (connection) и канал (channel)

**На пальцах:**

- **Connection** — как **один долгий телефонный звонок** до брокера (реальный TCP). Открывать звонок каждый раз дорого, поэтому держат открытым.
- **Channel** — как **несколько тем в том же звонке**: «сейчас поговорим про очередь A», «теперь про B» — без нового TCP. Упрощённо: **один провод, много виртуальных линий**.
- Обрубили **звонок (TCP)** — рвутся **все темы (каналы)** сразу.

**На экран:**

- **Connection** — долгоживущее **TCP**-соединение до брокера; создание соединения дороже, чем операции поверх него.
- **Channel** — виртуальное **мультиплексированное** соединение внутри одного TCP: publish/consume объявляют через канал. Типичная практика: **одно TCP на процесс**, много каналов на потоки/задачи (с осторожностью к объёму).
- Разрыв **TCP** рвёт все каналы; при **ошибке на канале** в классической модели иногда «падает» весь connection — зависит от клиента и настроек.

**Схема: одно TCP, несколько каналов**

```mermaid
flowchart LR
  subgraph app [Процесс приложения]
    T1[Задача A]
    T2[Задача B]
    T3[Задача C]
  end
  subgraph tcp [Одно соединение TCP]
    CH1[Channel 1]
    CH2[Channel 2]
    CH3[Channel 3]
  end
  subgraph br [Брокер]
    CORE[AMQP endpoint]
  end
  T1 --> CH1
  T2 --> CH2
  T3 --> CH3
  CH1 --> CORE
  CH2 --> CORE
  CH3 --> CORE
```

**Примерно в Docker Compose** (каналы — **внутри** процесса; в Compose один сервис = один процесс с общим TCP к брокеру):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
    # Внутри app: одно Connection, несколько Channel (потоки/ asyncio tasks)
```

**Подробнее:** в коде на **pika/aio-pika** вы почти всегда работаете с **channel**, а connection создаёте один на старт приложения.

---

## Слайд 5. Путь сообщения: publish → exchange → binding → queue

**На пальцах:**

- Вы **не кидаете** сообщение «в очередь по имени» (в учебных примерах бывает исключение) — вы кидаете в **сортировочный центр (exchange)**, а брокер по **правилам привязок (bindings)** решает, в **какие ящики (очереди)** оно упадёт.
- **Exchange** сам по себе **не хранит** письма на полке: он **прогнал и разложил**; **ждать в очереди** будет уже в **queue**.
- **Consumer** забирает из **очереди**; **ack** — «забрал и обработал, **сотри** из очереди» (упрощённо).

**На экран:**

- Продьюсер вызывает **publish** в **exchange** с **routing key** (и опционально **headers**, **properties**).
- **Binding** связывает exchange с **очередью** и задаёт правило: при каком ключе (или без ключа у fanout) сообщение попадает в эту очередь.
- **Очередь** хранит сообщения до доставки консьюмеру; exchange **не является** долговременным складом сообщений (он **маршрутизирует** входящий кадр publish).
- Консьюмер получает **deliver** из очереди; после обработки отправляет **ack** (или **nack/reject**) — от этого зависит, удалится ли сообщение из очереди.

**Схема основного контура AMQP**

```mermaid
flowchart LR
  P[Producer] -->|basic.publish + routing key| X[Exchange]
  X -->|binding rules| Q[(Queue)]
  Q -->|basic.deliver| C[Consumer]
  C -->|basic.ack| Q
```

**Примерно в Docker Compose** (брокер + продьюсер + консьюмер; exchange/очередь/binding объявляются в коде при старте):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  producer:
    build: .
    command: python producer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  consumer:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Схема: несколько bindings от одного exchange**

```mermaid
flowchart TB
  P[Producer] --> X[Exchange]
  X -->|binding rk: order.paid| Q1[(billing.queue)]
  X -->|binding rk: order.shipped| Q2[(logistics.queue)]
  X -->|binding rk: order.#| Q3[(audit.queue)]
```

**Примерно в Docker Compose** (тот же каркас, что у первой схемы на этом слайде; три очереди и ключи — в коде **order**-сервиса и трёх consumer’ов или одного сервиса с тремя задачами):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  orders:
    build: .
    command: python order_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  # billing_consumer, logistics_consumer, audit_consumer — по желанию отдельные services
```

**По стрелкам:** маршрутизация выполняется **на стороне брокера** при каждом publish; очередь — единственное место, где сообщение **ждёт** consumer’а (если не отброшено правилами).

---

## Слайд 6. Типы exchange: как брокер выбирает очереди

**На пальцах:**

- **direct** — «если на конверте написано **ровно** `order.paid` — в этот ящик».
- **fanout** — «размножить газету: **каждому** подписчику **своя** копия в **свой** ящик» (ключ не смотрим).
- **topic** — «если адрес подходит **шаблону** вроде `*.paid` или `order.#` — в этот ящик».
- **default (`""`)** — ленивый режим: «положи в очередь, **имя которой = routing key**» — для прототипов.

**На экран:**

| Тип | Как маршрутизирует | Типичное применение |
|-----|-------------------|---------------------|
| **direct** | Routing key **точно совпадает** с ключом binding | Именованные типы событий |
| **fanout** | Копия во **все** привязанные очереди (ключ игнорируется) | Широковещание подписчикам |
| **topic** | Совпадение ключа с **шаблоном** (`*`, `#`) | Иерархические доменные события |
| **headers** | Сопоставление по **заголовкам** сообщения | Редко на вводном курсе |
| **default** | Неявный exchange `""`: ключ = **имя очереди** | Простые сценарии, учебные прототипы |

**Сводная схема типов**

```mermaid
flowchart TB
  subgraph direct [direct]
    dX[Exchange] -->|rk = order.paid| dQ[(Q paid)]
  end
  subgraph fanout [fanout]
    fX{{Exchange}} --> fQ1[(Q1)]
    fX --> fQ2[(Q2)]
  end
  subgraph topic [topic]
    tX[Exchange] -->|binding: *.paid| tQ[(Q)]
  end
```

**Примерно в Docker Compose** (тип exchange задаётся в приложении; контейнеров по числу типов не требуется):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  app:
    build: .
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** **default exchange** удобен для «отправить в очередь с именем X», но в распределённых системах чаще явно создают **именованный** exchange и bindings — так проще сопровождать схему.

---

## Слайд 7. Очередь, устойчивость сообщений и Management UI

**На пальцах:**

- **Очередь** — **буфер**: сообщения лежат, пока воркер не заберёт. Если воркер медленный — буфер **растёт** (как пробка).
- **Durable очередь** — «после перезапуска брокера **название и настройки** очереди восстановятся». **Persistent сообщение** — ещё и «тело постарайся **не потерять** при падении» (не абсолютная гарантия без нормальной эксплуатации).
- **Management UI** — **панель приборов**: сколько сообщений ждёт, сколько «в руках у воркера» (unacked), не нужно гадать вслепую.

**На экран:**

- **Очередь** объявляется с флагами: **durable** — переживёт **перезапуск** брокера (метаданные очереди); сообщения дополнительно помечают **delivery_mode = persistent**, если нужна устойчивость **тела** на диске (всё равно не замена бэкапам и политике ретеншна).
- **Exclusive** — только одно соединение; **auto-delete** — удалится, когда отпадут консьюмеры: удобно для временных очередей, опасно для продакшена без понимания.
- **Management plugin**: очереди, скорость publish/consume, **ready / unacked**, привязки — основа **наблюдаемости** без написания своего UI.
- В RabbitMQ 3.8+ для критичных сценариев часто рассматривают **quorum queues**; на вводном курсе достаточно **classic** и понимания компромиссов.

**Схема: состояние сообщений у консьюмера**

```mermaid
flowchart LR
  subgraph broker [Брокер]
    Q[(Queue)]
  end
  subgraph cons [Consumer]
    BUF[Буфер prefetch]
    APP[Обработка]
  end
  Q -->|deliver до ack| BUF
  BUF --> APP
  APP -->|basic.ack| Q
```

**Примерно в Docker Compose** (prefetch настраивается в **коде** consumer’а):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  worker:
    build: .
    command: python consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**По стрелкам:** пока **ack** не отправлен, сообщение считается **unacked** и не отдано другому консьюмеру (в типичной настройке одной очереди).

---

## Слайд 8. Тема и результат занятия

**На пальцах:** после лекции вы не просто «знаете Rabbit», а умеете **нарисовать на доске**, куда идут события: кто шлёт, куда падает, кто читает, зачем **две очереди**, а не одна. Это язык общения с коллегами при разборе фич.

**На экран:**

- Как **разложить** потоковую систему (события, уведомления, чаты, обработка медиа) на **обменники, очереди и сервисы**.
- Как **назвать** и **нарисовать** типовые схемы, чтобы их узнавали коллеги и ревьюеры.
- Связка с **Python/FastAPI + RabbitMQ + worker + PostgreSQL** — как в учебном контуре.

**Подробнее:** после лекции студент должен уметь для задачи «много событий, много подписчиков» предложить **один основной паттерн** и обосновать, почему не смешали fanout с одной общей очередью.

---

## Слайд 9. Что считаем «потоковым приложением» здесь

**На пальцах:** «Потоковое» здесь — не обязательно видео по UDP. Это когда **события идут потоком** (много подряд), а сервер **не отвечает сразу на каждое** в одном HTTP-запросе, а **складывает в очередь** и обрабатывает **асинхронно**. Лента, чат, заказы, сторис — всё такое.

**На экран:**

- **Поток событий:** сообщения приходят **непрерывно или пачками**, обработка **асинхронна** от HTTP-запроса пользователя.
- **Примеры рунета:** лента и уведомления (**ВК**, **ОК**), чат стрима (**Рутуб**, **VK Live**), статусы заказа (**Озон**, **Яндекс Маркет**), фоновая обработка сторис (**ВК**, **ОК**).
- **Не обязательно** «бесконечный видеопоток»: достаточно **очереди задач и событий** между сервисами.

**Подробнее:** граница лекции — **сообщения в брокере** и **подписчики**; кодеки и RTP для WebRTC — отдельная тема.

---

## Слайд 10. Зачем между сервисами брокер, а не прямой HTTP

**На пальцах:**

- **HTTP «позвони соседу»**: если сосед занят или упал — вы **ждёте**, **падаете по таймауту**, давите каскадом. **Брокер** — **ящик у двери**: вы положили письмо и пошли дальше; сосед заберёт, когда проснётся.
- Минус: появился **ещё один сервис**, который надо **мониторить** и **настраивать** — не бесплатно.

**На экран:**

- **Декуплинг по времени:** продьюсер не ждёт, пока потребитель освободится.
- **Декуплинг по доступности:** потребитель упал — сообщения **буферизуются** (с ограничениями по политике и диску).
- **Масштабирование чтения:** несколько воркеров читают **одну очередь** или разные очереди с одного exchange.
- **Цена:** новая инфраструктура, **операционка**, семантика доставки (**at-least-once** по умолчанию у потребителя с ack).

**Подробнее:** «позвонить соседу по HTTP» ломается при всплесках и каскадных таймаутах; брокер — **шина с буфером**.

---

## Слайд 11. Модель маршрутизации: резюме перед паттернами

**На пальцах:** запомните цепочку из **четырёх слов**: **пишем в exchange → правила (bindings) → лежит в queue → читает consumer**. Всё остальное — вариации этой схемы.

**На экран:**

- **Producer** публикует в **exchange** (не в очередь напрямую, кроме default exchange).
- **Binding:** связь exchange ↔ queue (+ **routing key** или fanout).
- **Consumer** читает из **queue**; подтверждение **ack** снимает сообщение с очереди.
- Типы exchange: **direct**, **topic**, **fanout**, **headers** (реже на вводном курсе).

**Схема (обобщённо):**

```mermaid
flowchart LR
  subgraph prod [Продьюсеры]
    P1[Svc A]
    P2[Svc B]
  end
  subgraph rabbit [RabbitMQ]
    X[Exchange]
    Q1[(Queue 1)]
    Q2[(Queue 2)]
    X -->|binding| Q1
    X -->|binding| Q2
  end
  subgraph cons [Потребители]
    C1[Worker 1]
    C2[Worker 2]
  end
  P1 --> X
  P2 --> X
  Q1 --> C1
  Q2 --> C2
```

**Примерно в Docker Compose** (несколько сервисов публикуют / читают; маршрутизация в коде):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  svc_a:
    build: ./svc_a
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  svc_b:
    build: ./svc_b
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  worker_1:
    build: ./worker
    command: python worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  worker_2:
    build: ./worker
    command: python worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**По стрелкам:** публикация всегда в exchange; дальше маршрутизация по правилам binding; consumer привязан к **очереди**.

**Подробнее:** детальный разбор узла брокера, **AMQP**, **vhost**, **channel**, пути сообщения, типов **exchange** и флагов очереди — **слайды 1–7**.

---

## Слайд 12. Паттерн: буфер — одна очередь, сглаживание пиков

**Привязка к рунету:** **ВКонтакте / Одноклассники** — загрузка сторис, генерация превью и постобработка; **Дзен** — тяжёлая подготовка карточки после быстрого приёма контента.

**На пальцах:** пользователь нажал «загрузить» — API **быстро** ответил «ок, приняли», а тяжёлая работа **встала в хвост**. Как **тикет в жёлоб**: кассир (воркер) обслуживает не всех сразу, но никто не висит на линии HTTP.

**На экран:**

- Быстрый **API** кладёт **задание** в очередь и отвечает клиенту «принято».
- Медленный **воркер** забирает задачи, когда успевает.
- Риск: **рост очереди** при длительном перекосе скоростей — нужны метрики и масштабирование consumer’ов.

**Схема:**

```mermaid
flowchart LR
  subgraph client [Клиент]
    U[Пользователь]
  end
  subgraph api [Сервис API]
    A[Приём загрузки]
  end
  subgraph rabbit [RabbitMQ]
    X[direct exchange]
    Q[(encode.jobs)]
  end
  subgraph worker [Воркеры]
    W[Encoder]
  end
  U -->|upload| A
  A -->|publish job| X
  X --> Q
  Q --> W
```

**Примерно в Docker Compose** (API кладёт задачи, воркер забирает; часто **два** сервиса из одного образа):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  api:
    build: .
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000
    ports: ["8000:8000"]
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  encoder:
    build: .
    command: python encoder_worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** это базовый **producer–consumer**; основа для всех остальных паттернов.

---

## Слайд 13. Паттерн: work queue — несколько воркеров, одна очередь

**Привязка к рунету:** **Рутуб**, **Okko**, **Кинопоиск** — транскодинг видео: много **однотипных** задач, пул машин забирает из **одной** очереди.

**На пальцах:** одна **общая куча задач**, много **рабочих рук**. Кто освободился — взял **следующий** тикет. Так **увеличивают скорость**, запуская второй и третий воркер, а не ускоряя один.

**На экран:**

- RabbitMQ распределяет сообщения между консьюмерами (**конкурирующие подписчики** на одну очередь).
- Настройка **prefetch (QoS)** — сколько неподтверждённых сообщений держит у себя воркер; влияет на **честность** нагрузки.
- **Идемпотентность:** одно и то же сообщение теоретически могут обработать дважды при сбоях — проектировать обработчик устойчивым к повтору.

**Схема:**

```mermaid
flowchart LR
  subgraph upload [Сервис загрузки]
    UPL[Upload API]
  end
  subgraph rabbit [RabbitMQ]
    X[direct]
    Q[(transcode.tasks)]
  end
  subgraph pool [Пул воркеров]
    W1[Worker 1]
    W2[Worker 2]
    W3[Worker 3]
  end
  UPL -->|publish| X
  X --> Q
  Q --> W1
  Q --> W2
  Q --> W3
```

**Примерно в Docker Compose** (несколько одинаковых воркеров — **три** сервиса с одним образом и одной командой; в Swarm/K8s чаще **replicas**):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  uploader:
    build: .
    command: python upload_api.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  worker_1:
    build: .
    command: python transcode_worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  worker_2:
    build: .
    command: python transcode_worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  worker_3:
    build: .
    command: python transcode_worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** глобальный **порядок** между разными воркерами не гарантирован; если нужен строгий порядок по сущности — смотреть **partition key** или одного consumer’а на ключ (или другой брокер).

---

## Слайд 14. Паттерн: pub/sub через fanout — своя очередь на каждый сервис

**Привязка к рунету:** **ВКонтакте** — новый пост: нужно обновить **ленту**, **поиск**, **рекомендации**, **счётчики**; **Одноклассники** — аналогично для ленты и смежных подсистем.

**На пальцах:** произошло **одно** событие — но **трём отделам** нужна **каждому своя копия** новости. Если все трое сядут читать **одну** очередь, каждый получит **разные** сообщения из потока (как три человека делят одну газету по страницам). Правильно: **три отдельные очереди**, в каждую — **полная копия** события.

**На экран:**

- **Fanout exchange** игнорирует routing key: копия (логически) уходит во **все** привязанные очереди.
- У каждого подписчика **своя очередь** — один медленный сервис **не блокирует** остальных.
- Не путать с **одной очередью на всех** — там конкурируют за сообщения и теряется широковещание.

**Схема:**

```mermaid
flowchart LR
  subgraph origin [Источник события]
    P[Сервис постов]
  end
  subgraph rabbit [RabbitMQ]
    X{{fanout post.created}}
    QF[(feed.queue)]
    QS[(search.queue)]
    QR[(recs.queue)]
    X --> QF
    X --> QS
    X --> QR
  end
  subgraph subs [Подписчики]
    F[Лента]
    S[Поиск]
    R[Рекомендации]
  end
  P --> X
  QF --> F
  QS --> S
  QR --> R
```

**Примерно в Docker Compose** (fanout + три **независимых** consumer’а — три сервиса):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  posts:
    build: .
    command: python post_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  feed_worker:
    build: .
    command: python feed_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  search_worker:
    build: .
    command: python search_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  recs_worker:
    build: .
    command: python recs_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** на лекции подчеркнуть: **одно доменное событие — много независимых конвейеров**.

---

## Слайд 15. Паттерн: direct exchange — маршрутизация по точному ключу

**Привязка к рунету:** **Озон / Яндекс Маркет** — разные типы событий заказа: оплачен, отгружен, возврат; разные команды потребляют **разные** потоки.

**На пальцах:** как **переключатель по этикетке**: наклейка **точно** «оплата» — в ящик бухгалтерии; «отгрузка» — в ящик склада. Без звёздочек и «похожих» слов — только **точное совпадение** ключа.

**На экран:**

- Очередь привязана к exchange с **конкретным** routing key.
- Подходит, когда множество **именованных** типов сообщений без иерархии `*` и `#`.
- Продьюсер явно задаёт ключ при publish.

**Схема:**

```mermaid
flowchart LR
  subgraph orders [Сервис заказов]
    O[Order service]
  end
  subgraph rabbit [RabbitMQ]
    X[direct orders.events]
    Q1[(queue paid)]
    Q2[(queue shipped)]
    Q3[(queue refunded)]
    X -->|order.paid| Q1
    X -->|order.shipped| Q2
    X -->|order.refunded| Q3
  end
  subgraph cs [Потребители]
    A[Биллинг]
    B[Логистика]
    C[Поддержка]
  end
  O --> X
  Q1 --> A
  Q2 --> B
  Q3 --> C
```

**Примерно в Docker Compose** (один **orders** + три consumer-сервиса под разные ключи):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  orders:
    build: .
    command: python order_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  billing:
    build: .
    command: python billing_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  logistics:
    build: .
    command: python logistics_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  support:
    build: .
    command: python support_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** при росте числа ключей смотреть на **topic** или конвенцию имён + мониторинг «мёртвых» ключей.

---

## Слайд 16. Паттерн: topic exchange — иерархия и шаблоны

**Привязка к рунету:** **MAX**, корпоративные мессенджеры, **VK** — много видов событий с «путями»: комната, тип сущности, действие.

**На пальцах:** ключи как **путь в папках**: `chat.room5.message`. Подписчик говорит: «мне всё, что **начинается с chat.**» или «**любой** сегмент `.paid`» — для этого есть шаблоны **`*`** (одно слово) и **`#`** (хвост любой длины). Удобно, когда типов событий **много**, а не три штуки.

**На экран:**

- Ключи вида `chat.room.message`, `user.profile.updated`.
- Binding с `*` (одно слово) и `#` (ноль или больше слов).
- Гибче, чем direct, но нужна **дисциплина именования** и ревью схемы ключей.

**Схема:**

```mermaid
flowchart LR
  subgraph api [Backend API]
    B[Публикация событий]
  end
  subgraph rabbit [RabbitMQ]
    X[topic events.bus]
    Q1[(audit.*)]
    Q2[(chat.#)]
    Q3[(user.*.updated)]
    X --> Q1
    X --> Q2
    X --> Q3
  end
  subgraph w [Обработчики]
    W1[Аудит]
    W2[Чат-сервис]
    W3[Профили]
  end
  B -->|chat.room123.message| X
  Q1 --> W1
  Q2 --> W2
  Q3 --> W3
```

**Примерно в Docker Compose** (один backend публикует; несколько подписчиков на шаблоны ключей):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  backend:
    build: .
    command: python backend.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  audit:
    build: .
    command: python audit_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  chat_svc:
    build: .
    command: python chat_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  profiles:
    build: .
    command: python profiles_consumer.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** совпадает с учебным **topic** в лабе (`chat.message.created` / `persisted`).

---

## Слайд 17. Паттерн: конвейер (pipeline) — стадии и новые события

**Привязка к рунету:** **мессенджеры** (MAX, VK Мессенджер): принято → сохранено → доставлено подписчикам; **чат стрима** (**Рутуб**): модерация/фильтр → запись → рассылка в веб-клиенты.

**На пальцах:** не один воркер «сделал всё», а **цепочка**: «приняли» → отдельная очередь → «сохранили в БД» → **новое** событие «сохранено» → следующий этап (например, пуш в браузер). Как конвейер: каждая станция **заканчивает работу** и передаёт **дальше по ленте**.

**На экран:**

- Каждая стадия **заканчивается** осмысленным событием для следующей очереди.
- Веб-слой не обязан писать в БД сам: **разгрузка** и **чёткие границы** ответственности.
- Учебный эталон — схема из `containers-architecture.mmd`.

**Схема (как в лабе):**

```mermaid
flowchart LR
  subgraph client [Браузер]
    U[Пользователь]
  end
  subgraph web [Контейнер web]
    W[FastAPI и WebSocket]
    C[consume_persisted_events]
  end
  subgraph rabbit [Контейнер rabbitmq]
    X[Exchange topic]
    Q1[incoming queue]
    Q2[persisted queue]
  end
  subgraph worker [Контейнер worker]
    WK[worker.py]
  end
  subgraph db [Контейнер postgres]
    PG[(PostgreSQL)]
  end
  U -->|HTTP / WS| W
  W -->|WebSocket| U
  W -->|publish chat.message.created| X
  X --> Q1
  Q1 --> WK
  WK --> PG
  WK -->|publish chat.message.persisted| X
  X --> Q2
  Q2 --> C
  C -->|broadcast HTML| W
```

**Примерно в Docker Compose** (учебный чат: те же **роли**, что на схеме и в `containers-architecture.mmd`; команды и переменные — как в вашей методичке):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: chat
      POSTGRES_PASSWORD: chat
      POSTGRES_DB: chat
  web:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8100:8000"
    depends_on: [rabbitmq, postgres]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
      DATABASE_URL: postgresql+asyncpg://chat:chat@postgres:5432/chat
  worker:
    build: .
    command: python worker.py
    depends_on: [rabbitmq, postgres]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
      DATABASE_URL: postgresql+asyncpg://chat:chat@postgres:5432/chat
```

**По стрелкам:**

- Клиент ↔ web: **WebSocket** / HTTP.
- Web публикует **создано** → очередь входящих → **worker** пишет в **Postgres** → публикует **сохранено** → web **рассылает** в комнату.

**Подробнее:** UI обновляется после **факта персистенции** — меньше рассинхрона «показали, а в БД нет». Отдельно про **зачем выделен worker-контейнер** — **слайд 18**.

---

## Слайд 18. Роль отдельного worker в лабе (`worker.py`, `containers-architecture.mmd`)

**На пальцах:** на общей схеме **не один герой**. **Worker** — это **отдельный процесс** (у вас — контейнер): он **сидит на входящей очереди**, **пишет в Postgres**, после коммита шлёт событие **«сохранено»**. **Web** в этой модели **не обязан** в том же потоке крутить тяжёлую работу с БД на каждое сообщение чата — он **положил задачу в Rabbit** и отделался; дальше трудится worker.

**На экран:**

- Воркер **не обязателен** для «чата в принципе» — в методичке он **учебно-архитектурный**: показать **очередь между приёмом и записью** и отдельного consumer’а, как в реальных сервисах.
- **По факту в лабе:** обычно **единственный** читатель `chat.messages.incoming` и **единственный**, кто на этом пути **вставляет строку** в PostgreSQL; затем публикует **`chat.message.persisted`**, и уже **web** рассылает HTML/WebSocket в комнату.
- **Зачем так делают:** **разгрузка web** при всплесках; **масштаб** (несколько worker, один web); **устойчивость** — сообщения в durable-очереди переживают рестарт web, воркер доработает; **явная модель** «создано» vs «сохранено» — UI трогают после `persisted`.
- **Честное упрощение:** писать в БД сразу из `main.py` после приёма сообщения **можно** — тогда для этой задачи отдельный `worker.py` не нужен; в репозитории воркер нужен, чтобы **увидеть паттерн** на диаграмме и в коде.

**Схема — только «хвост» с worker (остальное как на слайде 17):**

```mermaid
flowchart LR
  Q1[(incoming queue)]
  WK[worker.py]
  PG[(PostgreSQL)]
  X[topic exchange]
  Q1 -->|consume| WK
  WK -->|INSERT commit| PG
  WK -->|publish chat.message.persisted| X
```

**Примерно в Docker Compose** (тот же стек, что на **слайде 17**; здесь на схеме только «хвост» **worker** — в YAML он по-прежнему сервис **`worker`**, рядом с **`web`** и **`rabbitmq`**):

```yaml
# См. полный фрагмент на слайде 17. Минимально для обсуждения роли worker:
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  postgres:
    image: postgres:16
  worker:
    build: .
    command: python worker.py
    depends_on: [rabbitmq, postgres]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** раздел **«Зачем нужен worker.py»** в **`about.md`**.

---

## Слайд 19. Слой доставки в браузер: WebSocket и брокер

**На пальцах:** **RabbitMQ не лезет в браузер** — с ним говорят **серверы**. Браузер держит **WebSocket** с **вашим** backend; backend **читает очередь** и решает, кому из открытых сокетов **отправить** обновление. Если серверов **несколько**, без доп. трюков сложно: событие может прийти на **другой** инстанс, где сокета пользователя **нет**.

**На экран:**

- Брокер **не заменяет** WebSocket: он связывает **серверные** процессы.
- Типичная схема: событие из очереди → процесс с **активными WS** (или Redis pub/sub между инстансами) → клиент.
- Проблема **нескольких инстансов** web: нужна **общая шина** или **sticky sessions** + осторожность.

**Схема (упрощённо):**

```mermaid
flowchart LR
  subgraph r [RabbitMQ]
    Q[(persisted)]
  end
  subgraph web1 [Web инстанс 1]
    WS1[WebSocket hub]
  end
  subgraph web2 [Web инстанс 2]
    WS2[WebSocket hub]
  end
  subgraph clients [Клиенты]
    C1[Браузер A]
    C2[Браузер B]
  end
  Q -->|consume| WS1
  Q -->|consume| WS2
  WS1 <-->|WS| C1
  WS2 <-->|WS| C2
```

**Примерно в Docker Compose** (два инстанса **web** за балансировщиком — в учебном виде два сервиса с разными портами; **одна** очередь `persisted` — в проде обычно один тип consumer или отдельная шина между инстансами):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  web1:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports: ["8101:8000"]
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  web2:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    ports: ["8102:8000"]
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  # В проде: nginx + sticky sessions или Redis pub/sub между web
```

**Подробнее:** в проде часто **один** тип consumer’а на очередь; для fan-out по инстансам — отдельный дизайн (общий pub/sub, распределение по room id). На лекции достаточно назвать проблему.

---

## Слайд 20. Паттерн: RPC поверх очередей (request–reply)

**Привязка к рунету:** редко «лицо» продукта, чаще **внутренние** вызовы: тяжёлый скоринг (**антиспам ВК**), внешний **ML**-сервис с очередью задач.

**На пальцах:** вместо «вызови функцию и **сразу** получи ответ» — «положи **заявку** в очередь, в заявке напиши **куда ответить** и **номер заказа** (correlation_id); исполнитель положит ответ в **очередь ответов», ты сопоставишь по номеру». Медленнее и сложнее, чем HTTP, зато **очередь** гасит пики.

**На экран:**

- Отдельная **очередь запросов**, в сообщении **reply_to** и **correlation_id**.
- Ответ публикуется в **очередь ответов**; клиент сопоставляет по `correlation_id`.
- Минусы: **задержка**, сложность таймаутов; для публичного API чаще **HTTP/gRPC**.

**Схема:**

```mermaid
flowchart LR
  subgraph caller [Клиент RPC]
    A[Сервис A]
  end
  subgraph rabbit [RabbitMQ]
    X[direct]
    QR[(rpc.requests)]
    QP[(rpc.replies A)]
  end
  subgraph worker [Исполнитель]
    B[Сервис B]
  end
  A -->|publish + reply_to| X
  X --> QR
  QR --> B
  B -->|reply + correlation_id| X
  X --> QP
  QP --> A
```

**Примерно в Docker Compose** (клиент RPC и исполнитель — два сервиса + брокер; очереди `rpc.requests` / `rpc.replies` создаются в коде):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  rpc_client:
    build: .
    command: python rpc_client_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  rpc_server:
    build: .
    command: python rpc_server_service.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
```

**Подробнее:** в RabbitMQ есть **встроенный** RPC tutorial; в потоковых продуктах паттерн **точечный**.

---

## Слайд 21. Семантика доставки и подтверждения (ack)

**На пальцах:**

- **Auto ack** — «как только воркер **получил** сообщение в память — считаем готово». Воркер **упал** через секунду — сообщение **потерялось**. Для учёбы иногда ок, для денег — нет.
- **Manual ack** — «обработал **и только тогда** сказал брокеру: убери». Упал до ack — брокер **отдаст снова** другому воркеру. Значит одно и то же **могут попробовать дважды** — обработчик должен быть к этому готов.

**На экран:**

- **Auto ack** — сообщение «сгорело» при доставке в клиента; при падении воркера **потеря**.
- **Manual ack** после успешной обработки — при падении до ack сообщение **вернётся** в очередь (**at-least-once** с точки зрения попыток доставки).
- **Нет волшебного exactly-once** без **идемпотентности** на стороне обработчика и/или дедупликации.

**Подробнее:** проектировать обработчик так, чтобы **повтор** не ломал данные (уникальные ключи, upsert, outbox).

---

## Слайд 22. Паттерн: Dead Letter Exchange (DLX) и очередь «ядовитых» сообщений

**Привязка к рунету:** **Рутуб**, **ВК**, **Дзен** — модерация и обработка UGC: битый payload, таймаут внешнего API, версия схемы не поддержана.

**На пальцах:** сообщение **битое** или обработчик **сдался** — не крутить его вечно в круг, а **сложить на полку «проблемные»** (DLQ). Туда потом зайдёт человек или скрипт: починить данные, переотправить, выкинуть.

**На экран:**

- Очередь настраивается с **x-dead-letter-exchange** (и при необходимости routing key).
- Сообщение уходит в DLQ после **отказа**, **истечения TTL** в очереди или **превышения** лимита повторов (в зависимости от политики).
- Операторы разбирают DLQ вручную или отдельным **replayer**.

**Схема:**

```mermaid
flowchart LR
  subgraph rabbit [RabbitMQ]
    X[main exchange]
    Q[(main.queue)]
    DLX[DLX]
    DLQ[(dead letters)]
  end
  subgraph ok [Успех]
    W[Worker]
  end
  subgraph bad [Сбой / отказ]
    M[Manual review]
  end
  X --> Q
  Q -->|consume| W
  Q -.->|nack / reject / TTL| DLX
  DLX --> DLQ
  DLQ --> M
```

**Примерно в Docker Compose** (DLX/DLQ задаются **аргументами очереди** в коде или политикой брокера; в YAML только процессы):

```yaml
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  worker:
    build: .
    command: python worker.py
    depends_on: [rabbitmq]
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
  # При declare очереди: x-dead-letter-exchange, при необходимости отдельный consumer для DLQ
```

**Подробнее:** без DLQ «битые» сообщения крутятся вечно или теряются молча — оба варианта хуже для эксплуатации.

---

## Слайд 23. Повторные попытки (retry) — осторожно с нагрузкой

**На пальцах:** «упало — попробуй ещё раз» звучит просто. Если **упало всё сразу** (база лежит), retry превращается в **шквал** повторов и может **положить** и брокер. Нужны **лимиты**, **задержки**, **метрики**: видно ли, что retry-очередь раздулась.

**На экран:**

- Простая схема: **retry-очередь** с **TTL** и возвратом в основную — возможен **шторм** при массовых сбоях.
- Альтернатива: **exponential backoff** на уровне приложения или отдельного планировщика.
- Метрики: глубина retry и DLQ — **обязательны** в дашборде.

**Подробнее:** согласовать с **идемпотентностью**: повтор — это норма, а не авария.

---

## Слайд 24. Идемпотентность и дедупликация в потоке

**На пальцах:** одно событие **дважды** доставили — это **нормальная** ситуация при ack/restart. Обработчик должен вести себя как кнопка лифта: нажали **два раза** — едете **один раз**. Техники: **уникальный id** события в БД, «уже обработано — пропускаю».

**На экран:**

- Повторная доставка возможна при **requeue**, **сетевых сбоях**, **перезапуске** consumer’а.
- Практики: **idempotency key** в сообщении, уникальный индекс в БД, **лог обработанных** event_id.
- Связка **запись в БД + публикация в Rabbit** — классическая ловушка; на продвинутом уровне **transactional outbox**.

**Подробнее:** без этого «exactly-once обещание брокера» не спасёт бизнес-логику.

---

## Слайд 25. Порядок сообщений: иллюзии и реальность

**На пальцах:** **один** воркер, **одна** очередь — обычно порядок «как клали». **Три** воркера из **одной** очереди — кто быстрее, тот и взял: порядок **обработки** уже не как в очереди. Если порядок критичен (например, по пользователю) — либо **один** consumer на этого пользователя, либо **своя** очередь/ключ.

**На экран:**

- В **одной очереди** у **одного** consumer’а порядок обычно сохраняется.
- **Несколько воркеров** на одну очередь — порядок **глобально** не гарантирован.
- Если нужен порядок по **user_id** — partition: отдельная очередь на ключ или один consumer на ключ (компромисс по масштабу).

**Подробнее:** для чатов часто достаточно порядка **внутри комнаты** при одном writer’е в БД или одном partition’е.

---

## Слайд 26. Prefetch (QoS) и обратное давление

**На пальцах:** **Prefetch** — «брокер, не шли мне **сразу сто** сообщений; держи у себя, пока я **не ack’ну** первые N». Иначе один жадный воркер заберёт пачку, а два других **простоят**. **Backpressure** — идея «не накапливай бесконечно в памяти у воркера»: лимит prefetch как предохранитель.

**На экран:**

- `prefetch_count` ограничивает, сколько неack’нутых сообщений получит воркер.
- Слишком большой prefetch — один толстый воркер забирает пачку, остальные простаивают.
- Слишком маленький — рост **латентности** на round-trip.
- Связь с **backpressure**: брокер держит хвост, consumer не должен **бесконечно** буферизовать в памяти.

**Подробнее:** настраивать prefetch после **профилирования** времени обработки.

---

## Слайд 27. Наблюдаемость: что логировать и метрить

**На пальцах:** без цифр вы **слепые**: очередь **растёт** — значит воркеры не успевают или упали; **unacked** растёт — воркеры зависли или не шлют ack. В сообщение кладут **id** для поиска в логах «где потерялось». Management UI — первый **бесплатный** датчик.

**На экран:**

- Глубина очереди (**ready**, **unacked**), rate publish/consume, **возраст** head-of-line.
- **Корреляция**: trace_id / event_id в заголовках или теле сообщения.
- RabbitMQ Management UI и экспорт метрик (**Prometheus** plugin и т.д.).

**Подробнее:** архитектура «с очередью» без метрик — слепая при первом всплеске.

---

## Слайд 28. RabbitMQ и Kafka — когда о чём думают

**На пальцах:** **Rabbit** — «**очередь задач** и **хитрая раздача** по правилам»; удобно, когда важны **маршруты** и **очереди**. **Kafka** — «**длинная лента** записей на диске, все читают **смещение**»; удобно, когда **огромный поток** и нужна **история/переигрывание». На курсе учим **идеи** на Rabbit; часть переносится на Kafka мысленно.

**На экран:**

- **RabbitMQ:** очереди, гибкая маршрутизация, **потребитель тянет** сообщения (push-модель с точки зрения брокера к клиенту), удобен для **задач** и **интеграции** сервисов.
- **Kafka:** **лог** с партициями, высокий throughput, **ретеншн** по времени/размеру, типичный выбор для **центральной шины событий** при очень большом объёме.
- На курсе RabbitMQ — **компактная** модель для обучения **паттернам**, переносимым на другие брокеры.

**Подробнее:** не религиозная война, а **требования** к задержке, объёму, хранению истории, операционке.

---

## Слайд 29. Анти-паттерн: одна «универсальная» очередь на всё

**На пальцах:** смешали в одну кучу **лёгкие** уведомления и **тяжёлые** видео-джобы. Очередь забита тяжестью — **лёгкие стоят** и ждут. Как одна касса на магазин и опт: все в одной змейке — раздражение гарантировано.

**На экран:**

- Разные SLA и скорости обработки в **одной** очереди: тяжёлые задачи блокируют лёгкие.
- Сложно масштабировать **избирательно** один тип нагрузки.
- Решение: **разнести** по очередям или ключам, мониторить каждую очередь отдельно.

**Подробнее:** «всё в default exchange в одну очередь» годится только на прототипе.

---

## Слайд 30. Анти-паттерн: fanout в одну общую очередь «для всех подписчиков»

**На пальцах:** хотели «всем разослать», а сделали **одну** очередь на троих — получилось **конкуренция**: сообщение **одно**, заберёт **кто-то один**. Остальные два **не увидят** эту копию. Для «всем по копии» нужны **три очереди** (слайд 14).

**На экран:**

- Подписчики **конкурируют** за сообщения — каждый получит **другую** подвыборку, а не копию события.
- Для широковещания нужны **отдельные очереди** на каждого потребителя (слайд 14).

**Подробнее:** типичная ошибка студенческих схем на экзамене.

---

## Слайд 31. Безопасность и границы доверия

**На пальцах:** брокер — **общий** для сервисов: отдельные **логины**, **vhost**, в проде **шифрование** канала. В сообщениях не гоняйте **пароли и токены** открытым текстом «потому что внутри сети». Персональные данные — по политике компании и закону (в РФ обычно вспоминают **152-ФЗ**).

**На экран:**

- Доступ к брокеру: **учётки** по сервисам, **виртуальные хосты**, TLS в проде.
- **Содержимое сообщений** — не место для секретов без шифрования; PII — политика хранения и логирования.
- Для РФ: соответствие **152-ФЗ**, локализация данных — на уровне **развёртывания**, не только кода.

**Подробнее:** кратко, без юридических деталей — акцент на инженерной гигиене.

---

## Слайд 32. Чеклист проектирования потока на RabbitMQ

**На пальцах:** перед кодом ответьте на **семь вопросов** ниже — как чеклист перед полётом. Если на какой-то пункт «не знаю» — там часто всплывает баг в проде.

**На экран:**

1. Кто **продьюсер**, кто **консьюмер**, какой **SLA** по задержке?
2. Нужен **fanout** (копии всем) или **маршрутизация** (direct/topic)?
3. Сколько **воркеров**, нужен ли **порядок** по ключу?
4. **Ack** ручной? **DLQ**? **Идемпотентность**?
5. **Prefetch**, лимиты очереди, **алерты** по глубине.
6. Как событие попадёт в **UI** (WS, SSE, polling)?
7. Кто **пишет в БД** на критичном пути — **web** или **отдельный worker** (как в лабе)?

**Подробнее:** использовать как **шаблон ревью** курсового и лабы.

---

## Слайд 33. Итог: опорные паттерны + роль worker в лабе

**На пальцах:** таблица — **шпаргалка на жизнь**: какой приём для какой боли (пик, масштаб, рассылка всем, точный ключ, шаблоны, конвейер, мусор в DLQ). Строка про **worker** напоминает: в вашей лабе это не «ещё один случайный сервис», а **учебный якорь** на схеме `containers-architecture.mmd`. На экзамене достаточно **объяснить словами** два–три паттерна и нарисовать стрелки.

**На экран:**

| Паттерн / приём | Зачем | Пример рунета (иллюстрация) |
|--------|--------|------------------------------|
| Буфер / одна очередь | Сгладить пик | Сторис ВК/ОК |
| Work queue | Масштаб обработки | Транскодинг Рутуб/Okko |
| Fanout + очереди | Независимые подписчики | Пост в ВК → лента, поиск, реки |
| Direct | Точный тип события | Статусы заказа Озон/Маркет |
| Topic | Иерархия ключей | Мессенджеры, доменные шины |
| Pipeline | Стадии и события | Чат, стрим-чат |
| **Отдельный worker** | Запись в БД не на горячем пути web; масштаб; «создано» vs «сохранено» | Лаба, `worker.py`, см. **слайд 18** |
| DLX / DLQ | Сбои и ручной разбор | Модерация UGC |

**Подробнее:** студенты должны **нарисовать** хотя бы **три** строки из таблицы (включая по желанию цепочку с worker) без шпаргалки.

---

## Слайд 34. Вопросы и связка с практикой

**На пальцах:** закрепление — **связать** то, что на слайдах, с **лабой**: тот же pipeline «создано → worker → сохранено → сокет». Вопросы в конце — проверка, что **картинка в голове сложилась**, а не только «я копировал из туториала».

**На экран:**

- Повторить схему **pipeline** из лабы (`chat.message.created` → worker → `persisted` → WebSocket).
- Вопросы: чем **topic** отличается от **direct**? Почему **fanout** не в одну очередь? Что такое **at-least-once**? Чем **AMQP** отличается от «положили JSON в Redis» с точки зрения **маршрутизации**? Зачем в лабе **отдельный** `worker.py`, если теоретически можно писать в БД из **web**?
- Домашнее чтение: официальные **RabbitMQ tutorials** (Work queues, Pub/Sub, Routing, Topics, RPC), раздел **Reliability** в документации.

**Подробнее:** привязать к файлам **`containers-architecture.mmd`**, **`about.md`**, методичке лабораторной.

---

## Приложение. Имена файлов со схемами

- Полная схема конвейера чата: `containers-architecture.mmd` (использовать в презентации как есть или экспорт в PNG).
- Фрагменты **Docker Compose** после Mermaid в этом файле — **учебные**; эталонный `docker-compose` для сдачи лабы — в методичке / репозитории проекта.

---

*Конец конспекта слайдов (34 штуки). При необходимости слайды 19–20 (WebSocket + RPC) или 27–28 (метрики + Kafka) можно сократить; блок устройства RabbitMQ и AMQP (слайды 1–7) можно сжать. Слайды 17–18 (pipeline + worker) логично показывать подряд.*
