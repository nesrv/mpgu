# Практический кейс: Логическая репликация в PostgreSQL

## Введение

Этот кейс предназначен для студентов, изучающих логическую репликацию в PostgreSQL. Вы будете работать с Docker-контейнерами, настраивать мастер-сервер и реплики, создавать публикации и подписки, а также реализовывать каскадную репликацию. Кейс состоит из 10 заданий, каждое с подробным разбором решений и возможными ошибками.

**Предварительные требования:**
- Docker и Docker Compose установлены.
- Базовые знания SQL и PostgreSQL.
- Рабочая директория: `backup_logical`.

**Стенд:**
- Мастер (publisher): порт 5439, БД `source_db`.
- Реплика 1 (subscriber1): порт 5437, БД `target_db`.
- Реплика 2 (subscriber2): порт 5438, БД `replica_db` (добавим в docker-compose).

## Задание 1: Создание базового стенда с мастером и одной репликой

Создайте docker-compose.yml с сервисом publisher (мастер) и subscriber (реплика). Запустите контейнеры и проверьте их статус.

**Шаги:**
1. Создайте docker-compose.yml с publisher и subscriber.
2. Добавьте custom_postgresql.conf для мастера с `wal_level = logical`.
3. Запустите `docker compose up -d`.
4. Проверьте `docker ps`.

**Решение:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  publisher:
    image: postgres:17
    container_name: postgres_publisher
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: source_db
    ports:
      - "5439:5432"
    volumes:
      - ./custom_postgresql.conf:/etc/postgresql/postgresql.conf
    command: ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
    networks:
      - replication_net
  subscriber:
    image: postgres:17
    container_name: postgres_subscriber
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: target_db
    ports:
      - "5437:5432"
    networks:
      - replication_net
    depends_on:
      - publisher
networks:
  replication_net:
    driver: bridge
```
```bash
# custom_postgresql.conf
listen_addresses = '*'
wal_level = logical
max_replication_slots = 10
max_wal_senders = 10
```
```bash
docker compose up -d
docker ps
```

**Разбор:**
- Publisher слушает на порту 5439, subscriber на 5437.
- В custom_postgresql.conf обязательно `wal_level = logical` для логической репликации.
- Если контейнеры не запускаются, проверьте логи: `docker logs <container_name>`. Ошибка "database directory appears to contain a database" означает, что данные уже есть — удалите volumes или используйте `--force-recreate`.
- Подключитесь к мастеру: `psql -h localhost -p 5439 -U admin -d source_db`.

## Задание 2: Настройка второй реплики

Добавьте вторую реплику (subscriber2) в docker-compose.yml. Обновите конфигурацию и перезапустите стенд.

**Шаги:**
1. Добавьте сервис subscriber2 с портом 5438 и БД `replica_db`.
2. Убедитесь, что `max_replication_slots` и `max_wal_senders` увеличены в custom_postgresql.conf.
3. Перезапустите: `docker compose down && docker compose up -d`.
4. Проверьте все три контейнера.

**Решение:**
```yaml
# Добавьте в docker-compose.yml
  subscriber2:
    image: postgres:17
    container_name: postgres_subscriber2
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin123
      POSTGRES_DB: replica_db
    ports:
      - "5438:5432"
    networks:
      - replication_net
    depends_on:
      - publisher
```
```bash
docker compose down
docker compose up -d
docker ps
```

**Разбор:**
- Для нескольких реплик увеличьте `max_replication_slots = 10` и `max_wal_senders = 10`.
- Если порт конфликтует, измените маппинг (например, "5438:5432").
- Ошибка "port already in use" — остановите другие сервисы или измените порт.
- Все реплики должны быть в одной сети для связи.

## Задание 3: Создание тестовой таблицы на мастере

Подключитесь к мастеру и создайте таблицу `users` с данными. Проверьте, что она появилась на репликах.

**Шаги:**
1. Подключитесь: `psql -h localhost -p 5439 -U admin -d source_db`.
2. Выполните:
   ```sql
   CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(50), email VARCHAR(100));
   INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
   ```
3. Проверьте на subscriber: `psql -h localhost -p 5437 -U admin -d target_db -c "SELECT * FROM users;"`.

**Решение:**
```bash
psql -h localhost -p 5439 -U admin -d source_db -c "
CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(50), email VARCHAR(100));
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');
"
psql -h localhost -p 5437 -U admin -d target_db -c "SELECT * FROM users;"
```

**Разбор:**
- На репликах таблица должна появиться автоматически, если репликация работает (но для логической — нужно настроить публикации/подписки).
- Если таблица не появилась, значит репликация не настроена — это нормально на этом этапе.
- Ошибка "permission denied" — проверьте пользователя и права.

## Задание 4: Создание публикации на мастере

Создайте публикацию `users_pub` для таблицы `users` на мастере.

**Шаги:**
1. На мастере: `psql -h localhost -p 5439 -U admin -d source_db`.
2. Выполните: `CREATE PUBLICATION users_pub FOR TABLE users;`.
3. Проверьте: `SELECT * FROM pg_publication;`.

**Решение:**
```bash
psql -h localhost -p 5439 -U admin -d source_db -c "
CREATE PUBLICATION users_pub FOR TABLE users;
SELECT * FROM pg_publication;
"
```

**Разбор:**
- Публикация позволяет реплицировать изменения в указанных таблицах.
- Если ошибка "table does not exist", создайте таблицу сначала.
- Для нескольких таблиц: `FOR TABLE table1, table2`.
- Публикация активна сразу после создания.

## Задание 5: Создание подписки на первой реплике

Создайте подписку на первой реплике, указав соединение с мастером.

**Шаги:**
1. На subscriber: `psql -h localhost -p 5437 -U admin -d target_db`.
2. Выполните:
   ```sql
   CREATE SUBSCRIPTION users_sub
   CONNECTION 'host=publisher port=5432 dbname=source_db user=admin password=admin123'
   PUBLICATION users_pub;
   ```
3. Проверьте: `SELECT * FROM pg_subscription;`.

**Решение:**
```bash
psql -h localhost -p 5437 -U admin -d target_db -c "
CREATE SUBSCRIPTION users_sub
CONNECTION 'host=publisher port=5432 dbname=source_db user=admin password=admin123'
PUBLICATION users_pub;
SELECT * FROM pg_subscription;
"
```

**Разбор:**
- `host=publisher` — имя сервиса в Docker-сети.
- Пароль в строке соединения — используйте кавычки.
- Если ошибка "publication does not exist", проверьте имя публикации на мастере.
- После создания подписка начнёт синхронизацию — данные должны появиться.

## Задание 6: Проверка репликации данных

Вставьте данные на мастере и проверьте их на реплике.

**Шаги:**
1. На мастере вставьте: `INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');`.
2. На реплике проверьте: `SELECT * FROM users;`.
3. Убедитесь, что данные совпадают.

**Решение:**
```bash
psql -h localhost -p 5439 -U admin -d source_db -c "INSERT INTO users (name, email) VALUES ('Bob', 'bob@example.com');"
psql -h localhost -p 5437 -U admin -d target_db -c "SELECT * FROM users;"
```

**Разбор:**
- Репликация логическая — копирует изменения, не всю БД.
- Если данные не появились, проверьте статус подписки: `SELECT * FROM pg_stat_subscription;`.
- Ошибка "replication slot active" — слот занят, подождите или удалите старую подписку.

## Задание 7: Настройка подписки на второй реплике

Повторите создание подписки для второй реплики.

**Шаги:**
1. На subscriber2: `psql -h localhost -p 5438 -U admin -d replica_db`.
2. Создайте подписку аналогично заданию 5.
3. Проверьте данные.

**Решение:**
```bash
psql -h localhost -p 5438 -U admin -d replica_db -c "
CREATE SUBSCRIPTION users_sub2
CONNECTION 'host=publisher port=5432 dbname=source_db user=admin password=admin123'
PUBLICATION users_pub;
SELECT * FROM pg_subscription;
"
psql -h localhost -p 5438 -U admin -d replica_db -c "SELECT * FROM users;"
```

**Разбор:**
- Каждая реплика нуждается в своей подписке.
- Если слоты исчерпаны, увеличьте `max_replication_slots`.
- Для нагрузки — используйте разные публикации или фильтры.

## Задание 8: Каскадная репликация — настройка реплики как мастера

Сделайте первую реплику каскадным мастером для второй реплики.

**Шаги:**
1. На subscriber (реплика 1) создайте публикацию: `CREATE PUBLICATION cascade_pub FOR TABLE users;`.
2. На subscriber2 измените подписку: `ALTER SUBSCRIPTION users_sub CONNECTION 'host=subscriber port=5432 ...';`.
3. Пересоздайте подписку.

**Решение:**
```bash
# На subscriber1
psql -h localhost -p 5437 -U admin -d target_db -c "CREATE PUBLICATION cascade_pub FOR TABLE users;"

# На subscriber2
psql -h localhost -p 5438 -U admin -d replica_db -c "
DROP SUBSCRIPTION users_sub2;
CREATE SUBSCRIPTION cascade_sub
CONNECTION 'host=subscriber port=5432 dbname=target_db user=admin password=admin123'
PUBLICATION cascade_pub;
"
```

**Разбор:**
- Каскадная репликация: реплика реплицирует данные дальше.
- Нужно `wal_level = logical` на всех уровнях.
- Если не работает, проверьте логи на ошибки репликации.

## Задание 9: Тестирование каскадной репликации

Вставьте данные на мастере и проверьте на второй реплике через каскад.

**Шаги:**
1. На мастере вставьте данные.
2. Проверьте на subscriber (должно быть).
3. Проверьте на subscriber2 (через каскад).

**Решение:**
```bash
psql -h localhost -p 5439 -U admin -d source_db -c "INSERT INTO users (name, email) VALUES ('Charlie', 'charlie@example.com');"
psql -h localhost -p 5437 -U admin -d target_db -c "SELECT * FROM users;"
psql -h localhost -p 5438 -U admin -d replica_db -c "SELECT * FROM users;"
```

**Разбор:**
- Задержка может быть, проверьте статус.
- Ошибки: "upstream connection failed" — проверьте сеть.

## Задание 10: Мониторинг и устранение проблем

Проверьте статус репликации и исправьте возможные ошибки.

**Шаги:**
1. На мастере: `SELECT * FROM pg_stat_replication;`.
2. На репликах: `SELECT * FROM pg_stat_subscription;`.
3. Если проблемы, перезапустите подписки или проверьте логи.

**Решение:**
```bash
# На мастере
psql -h localhost -p 5439 -U admin -d source_db -c "SELECT * FROM pg_stat_replication;"

# На репликах
psql -h localhost -p 5437 -U admin -d target_db -c "SELECT * FROM pg_stat_subscription;"
psql -h localhost -p 5438 -U admin -d replica_db -c "SELECT * FROM pg_stat_subscription;"

# Логи
docker logs postgres_publisher
docker logs postgres_subscriber
```

**Разбор:**
- Мониторьте задержку и состояние.
- Распространённые ошибки: сетевые проблемы, недостаток слотов, конфликты.
- Для продакшена добавьте мониторинг (Prometheus, etc.).

Этот кейс покрывает основы логической репликации. Для углубления изучите документацию PostgreSQL.