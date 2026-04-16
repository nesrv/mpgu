Логическая репликация в PostgreSQL

Учебный стенд.

Логическая репликация работает по принципу "публикатор-подписчик" (publisher-subscriber) и позволяет реплицировать данные выборочно, в отличие от физической репликации, которая копирует всё на уровне диска.

Самый простой и воспроизводимый способ поднять такой стенд на Windows — использовать Docker Compose.

Всё, что вам нужно, — это файл `docker-compose.yml` и несколько простых SQL-скриптов для инициализации.

Вот пошаговое руководство.

### 🛠️ Шаг 1: Создаём структуру проекта

Создайте на диске `C:` папку для проекта, например, `postgres_logical_replication_lab`. Внутри неё создайте два файла:

* `docker-compose.yml` — главный файл оркестрации.
* `init-publisher.sql` — скрипт для настройки источника (мастера).

### 🐳 Шаг 2: Пишем `docker-compose.yml`

Этот файл опишет два сервиса: `publisher` и `subscriber`. Важно, чтобы они находились в одной Docker-сети.

```yaml
version: '3.8'

services:
  # 1. Публикующий сервер (Publisher / Master)
  publisher:
    image: postgres:17
    container_name: postgres_publisher
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: source_db
    ports:
      - "5435:5432"  # Маппинг на порт 5432 хоста
    volumes:
      - ./init-publisher.sql:/docker-entrypoint-initdb.d/init.sql
      # Монтируем конфиг с wal_level=logical
      - ./custom_postgresql.conf:/etc/postgresql/postgresql.conf
    command: ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
    networks:
      - replication_net

  # 2. Сервер-подписчик (Subscriber / Replica)
  subscriber:
    image: postgres:17
    container_name: postgres_subscriber
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: target_db
    ports:
      - "5436:5432"  # Другой порт, чтобы не конфликтовать с publisher на хосте
    networks:
      - replication_net
    # Подписчик будет ждать, пока запустится публикующий сервер
    depends_on:
      - publisher

networks:
  replication_net:
    driver: bridge
```

### ⚙️ Шаг 3: Настройка параметров PostgreSQL (`custom_postgresql.conf`)

Создайте в папке проекта файл `custom_postgresql.conf`. Для работы логической репликации критически важно изменить параметр `wal_level` на `logical`.

```properties
# Включаем логическую репликацию
listen_addresses = '*'
wal_level = logical

# Увеличиваем лимиты для слотов репликации и отправителей
max_replication_slots = 10
max_wal_senders = 10
```

### 📝 Шаг 4: Инициализация публикующего сервера (`init-publisher.sql`)

Этот скрипт выполнится автоматически при первом запуске контейнера `publisher`. Он создаст тестовую таблицу, наполнит её данными и настроит **публикацию (publication)**.

```sql
-- Создаём тестовую таблицу
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вставляем немного начальных данных
INSERT INTO users (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com');

-- Создаём ПУБЛИКАЦИЮ для таблицы users
-- ВАЖНО: Указываем FOR ALL TABLES или конкретные таблицы
CREATE PUBLICATION users_pub FOR TABLE users;

-- Сообщаем в логах, что всё готово
DO $$
BEGIN
    RAISE LOG '[Publisher] Table "users" and publication "users_pub" are ready.';
END $$;
```

### 🚀 Шаг 5: Запуск и настройка подписчика

1. **Запустите стенд.** Откройте терминал (PowerShell) в папке проекта и выполните:

   ```powershell
   docker-compose up -d
   ```
2. **Создайте схему на подписчике.**
   Логическая репликация **не копирует схему (DDL)**. Вам нужно вручную создать такую же таблицу на подписчике.
   Подключитесь к `subscriber` и выполните SQL:

   ```sql
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       name VARCHAR(50) NOT NULL,
       email VARCHAR(100) UNIQUE NOT NULL,
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```
3. **Создайте подписку (Subscription).**
   Теперь свяжите подписчика с публикацией:

   ```sql
   CREATE SUBSCRIPTION users_sub
   CONNECTION 'host=publisher port=5432 dbname=source_db user=admin password=admin123'
   PUBLICATION users_pub;
   ```

### ✅ Шаг 6: Проверка работы репликации

Всё готово! Теперь проверим, как данные синхронизируются.

1. **Вставьте данные в `publisher`**:
   Подключитесь к базе `source_db` на порту `5432` и выполните:

   ```sql
   INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com');
   ```
2. **Проверьте данные в `subscriber`**:
   Теперь подключитесь к базе `target_db` на порту `5433` и выполните запрос:

   ```sql
   SELECT * FROM users;
   ```

Вы должны увидеть там Charlie! 🎉

### 🔍 Где посмотреть статус репликации

* **На издателе (publisher)**: `SELECT * FROM pg_stat_replication;` — покажет активное соединение подписчика.
* **На подписчике (subscriber)**: `SELECT * FROM pg_stat_subscription;` — покажет статус получения данных.

### 🧹 Остановка и очистка

Когда закончите эксперименты, остановите контейнеры:

```powershell
docker-compose down -v
```

Ключ `-v` удалит тома с данными, чтобы при следующем запуске всё началось с чистого листа.

Этот стенд даёт вам полный контроль над процессом и идеально подходит для изучения всех нюансов логической репликации
