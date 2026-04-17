# Лабораторная работа
## Изучение каскадной репликации PostgreSQL

### Цель работы
Изучить каскадную репликацию в PostgreSQL и проверить, как изменения проходят по цепочке `publisher -> subscriber -> subscriber2`.

### Используемая схема
1. `publisher` - первичный сервер.
2. `subscriber` - первая реплика, которая одновременно выступает источником для следующего узла.
3. `subscriber2` - вторая реплика, получающая изменения через `subscriber`.

### Стенд

```yml
services:
  publisher:
    image: postgres:17
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: source_db
    ports:
      - "5433:5432"
    volumes:
      - publisher_data:/var/lib/postgresql/data

  subscriber:
    image: postgres:17
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: target_db
    ports:
      - "5434:5432"
    volumes:
      - subscriber_data:/var/lib/postgresql/data
    depends_on:
      - publisher

  subscriber2:
    image: postgres:17
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: replica_db
    ports:
      - "5435:5432"
    volumes:
      - subscriber2_data:/var/lib/postgresql/data
    depends_on:
      - subscriber

volumes:
  publisher_data:
  subscriber_data:
  subscriber2_data:
```

### Подготовка окружения
Перед началом работы нужно:

1. Убедиться, что установлен Docker и Docker Compose.
2. Запустить контейнеры командой:

```bash
docker compose up -d
```

3. Проверить, что все три контейнера запущены:

```bash
docker ps
```

### Настройка каскадной репликации

#### 1. Настроить `publisher`
На первичном сервере нужно включить параметры репликации. Это можно сделать несколькими способами:

1. Через `psql` с командой `ALTER SYSTEM`.
   - Удобно, если настройки нужно изменить уже внутри работающего контейнера.
   - После изменения требуется перезапуск PostgreSQL.
2. Через `postgresql.conf`.
   - Подходит, если ты хочешь хранить настройки в отдельном конфигурационном файле.
   - Это самый наглядный вариант для ручной настройки.
3. Через параметры запуска `postgres -c`.
   - Удобно для Docker и временных учебных стендов.
   - Все параметры видны прямо в команде запуска контейнера.

В этом примере используется вариант через `psql`, потому что он позволяет показать изменение параметров прямо в базе:

```sh
docker exec -it physic_replica-publisher-1 psql -U admin -d source_db
```



```sql
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET listen_addresses = '*';
```

После этого перезапустить `publisher`.

```bash
docker compose restart publisher
# или
docker restart physic_replica-publisher-1
```

Проверь 

```sql
SELECT name, setting FROM pg_settings
WHERE name in ('wal_level','max_wal_senders');

```


#### 2. Создать пользователя для репликации
На `publisher` создать пользователя `replicator`, который нужен только для репликации. Это безопаснее, чем использовать администратора базы данных:

```sql
CREATE ROLE replicator WITH LOGIN PASSWORD 'replicator';
ALTER ROLE replicator WITH REPLICATION;
```

#### 3. Создать публикацию на `publisher`

```sql
CREATE PUBLICATION pub_all FOR ALL TABLES;
```

#### 4. Настроить `subscriber`
На `subscriber` создать подписку на `publisher`:

```sql
CREATE SUBSCRIPTION sub_from_publisher
CONNECTION 'host=publisher port=5432 dbname=source_db user=replicator password=replicator'
PUBLICATION pub_all;
```

#### 5. Настроить `subscriber2`
На `subscriber2` создать публикацию и подписку от `subscriber`:

```sql
CREATE PUBLICATION pub_from_subscriber FOR ALL TABLES;
```

Затем подключить `subscriber2` к `subscriber`:

```sql
CREATE SUBSCRIPTION sub_from_subscriber
CONNECTION 'host=subscriber port=5432 dbname=target_db user=replicator password=replicator'
PUBLICATION pub_from_subscriber;
```

#### 6. Подготовить `subscriber` для каскадной репликации
Так как `subscriber` сам становится источником для `subscriber2`, на нём тоже нужно включить параметры репликации и создать пользователя `replicator`:

```sql
CREATE ROLE replicator WITH LOGIN PASSWORD 'replicator';
ALTER ROLE replicator WITH REPLICATION;

ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_wal_senders = 10;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET listen_addresses = '*';
```

После этого перезапустить `subscriber`:

```bash
docker compose restart subscriber
```

Или:

```bash
docker restart physic_replica-subscriber-1
```

После перезапуска проверить:

```sql
SHOW wal_level;
```

Должно быть:

```text
logical
```

### Проверка работы

1. Создать таблицу на `publisher`:

```sql
CREATE TABLE test_replica (
    id serial PRIMARY KEY,
    name text
);
```

2. Вставить данные на `publisher`:

```sql
INSERT INTO test_replica(name) VALUES ('row 30'), ('row 40');
```

Важно: таблицы на `subscriber` и `subscriber2` нужно создать **до** создания подписок. Если таблица появилась уже после подписки, старые строки могут не примениться. В этом случае достаточно:

1. создать таблицу на всех репликах;
2. выполнить новую вставку на `publisher`;
3. либо пересоздать подписку, если нужно заново подтянуть данные.

3. Проверить данные на `subscriber`:

```sql
SELECT * FROM test_replica;
```

4. Проверить данные на `subscriber2`:

```sql
SELECT * FROM test_replica;
```

Если каскадная репликация настроена правильно, данные должны появиться на обоих узлах-репликах.

### Мониторинг

Для проверки состояния репликации использовать:

```sql
-- На publisher
SELECT * FROM pg_stat_replication;

-- На subscriber и subscriber2
SELECT * FROM pg_stat_subscription;
```

Для просмотра логов:

```bash
docker logs postgres_publisher
docker logs postgres_subscriber
docker logs postgres_subscriber2
```

### Переключение на реплику
Переключение на реплику нужно, когда требуется временно или постоянно перенести работу на другой узел. В этой лабораторной сценарий выполняется вручную.

#### Плановое переключение
Плановое переключение выполняют заранее, когда основной сервер нужно остановить для технических работ без прерывания обслуживания.

##### 1. Сымитировать выход из строя мастера
Остановить основной сервер `publisher`:

```bash
docker stop physic_replica-publisher-1
```

После этого приложение временно работает через реплику.

##### 2. Перевести реплику из режима восстановления в обычный режим
Если `subscriber` должен стать новым основным сервером, отключить его от репликации и поднять как обычный сервер. В рамках лабораторной это можно сделать вручную через остановку подписки и повторный запуск контейнера:

```sql
DROP SUBSCRIPTION sub_from_publisher;
```

После этого перезапустить `subscriber`:

```bash
docker restart physic_replica-subscriber-1
```

Теперь `subscriber` работает как самостоятельный сервер.

#### Аварийное переключение
Аварийное переключение используют, если основной сервер вышел из строя и продолжать работу на нём невозможно.

##### 3. Восстановить основной сервер и подключить его обратно в кластер
После восстановления `publisher` его можно вернуть в исходную схему:

```bash
docker start physic_replica-publisher-1
```

Затем заново настроить репликацию:

1. вернуть `wal_level = logical` и параметры репликации, если они были сброшены;
2. создать подписку на `publisher` заново;
3. проверить, что репликация снова работает через `pg_stat_replication` и `pg_stat_subscription`.

На практике такие сценарии часто автоматизируют с помощью дополнительного кластерного ПО, чтобы сократить время простоя и избежать ручных ошибок.

### Конфликтующие записи в логической репликации
Этот раздел описывает поведение системы при возникновении конфликтов данных. В логической репликации, в отличие от физической, реплика доступна на запись, что может привести к расхождениям.

**Важно:** При возникновении конфликта (например, дублирование Primary Key) процесс репликации (apply worker) на реплике **останавливается** с ошибкой до ручного вмешательства.

#### Подготовка
1. Убедиться, что логическая репликация активна.
2. Создать таблицу `conflict_test` на всех узлах (`publisher`, `subscriber`, `subscriber2`).

Пример таблицы:

```sql
CREATE TABLE conflict_test (
    id integer PRIMARY KEY,
    name text
);
```

#### Задание 1. Конфликтующая вставка
1. На реплике (`subscriber`) вставить строку вручную:

```sql
INSERT INTO conflict_test VALUES (1, 'replica row');
```

2. На основном сервере (`publisher`) вставить строку с тем же `id`:

```sql
INSERT INTO conflict_test VALUES (1, 'master row');
```

3. Ожидаемый результат:
   - Данные на реплику не придут.
   - В логах реплики (`docker logs physic_replica-subscriber-1`) появится ошибка: `ERROR: duplicate key value violates unique constraint "conflict_test_pkey"`.
   - Репликация для этой таблицы (или всей подписки) остановится.

4. Решение конфликта:
   - Удалить конфликтующую строку на реплике или изменить её ID, чтобы worker смог продолжить работу.

5. Вывод: Логическая репликация требует строгого контроля уникальности данных на всех узлах.

#### Задание 2. Конфликтующее обновление
1. На основном сервере (`publisher`) изменить строку, которая уже есть на всех узлах:

```sql
UPDATE conflict_test SET name = 'updated on master' WHERE id = 1;
```

2. На реплике (`subscriber`) одновременно или заранее изменить ту же строку:

```sql
UPDATE conflict_test SET name = 'updated on replica' WHERE id = 1;
```

3. Ожидаемый результат:
   - В логической репликации побеждает "последнее пришедшее изменение" (Last Update Wins), если нет конфликта по ключам. 
   - Однако, если строка на реплике была удалена или её ID изменен, репликация остановится с ошибкой `tuple to be updated was already modified` или `relation not found`.

4. Вывод: Логическая репликация чувствительна к состоянию данных на подписчике.

#### Задание 3. Конфликтующее удаление
1. На реплике (`subscriber`) удалить строку:

```sql
DELETE FROM conflict_test WHERE id = 1;
```

2. На мастере (`publisher`) попытаться обновить или удалить ту же строку:

```sql
UPDATE conflict_test SET name = 'master update' WHERE id = 1;
```

3. Ожидаемый результат:
   - Репликация на подписчике упадет с ошибкой, так как worker не найдет строку для обновления (`tuple to be updated could not be found`).

4. Вывод: Для стабильной работы логической репликации данные на репликах не должны изменяться вручную.

#### Что наблюдать
1. Остановку apply worker в `pg_stat_subscription`.
2. Сообщения об ошибках в логах контейнера реплики.
3. Расхождение данных (Data Drift) между узлами.

### Возможные ошибки

1. Неверный `host`, `port` или пароль в строке подключения.
2. Не включён `wal_level`.
3. Не созданы публикация или подписка.
4. Реплика не может подключиться к предыдущему узлу из-за сетевой ошибки или неправильного имени сервиса.

### Вывод
В ходе работы была изучена каскадная репликация PostgreSQL. Было показано, как изменения переходят от `publisher` к `subscriber`, а затем к `subscriber2` через промежуточную реплику.

### Обоснование перехода к `docker-compose-prod.yml`
В процессе работы был сохранён отдельный вариант стенда в файле `docker-compose copy.yml`. Он нужен как промежуточная и более наглядная версия конфигурации перед упрощением.

Причины использовать именно этот файл:

1. В нём явно показаны все служебные элементы стенда: `container_name`, ручная сеть `replication_net`, отдельные конфиги и папка `data`.
2. Такой вариант удобен для изучения базовой схемы и понимания, какие файлы и параметры участвуют в запуске каждого узла.
3. На его основе проще объяснять, что именно было убрано при переходе к минимальному `docker-compose.yml`.

Ниже приведено содержимое `docker-compose-prod.yml` с комментариями:

```yml
version: '3.8'

services:
  # Первичный сервер, с которого начинается репликация
  publisher:
    image: postgres:17
    container_name: postgres_publisher
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: source_db
    ports:
      - "5439:5432"
    volumes:
      # Инициализация данных при первом запуске
      - ./init-publisher.sql:/docker-entrypoint-initdb.d/init.sql
      # Отдельный конфигурационный файл для publisher
      - ./custom_postgresql.conf:/etc/postgresql/postgresql.conf
      # Хранение данных на диске в папке проекта
      - ./data/publisher:/var/lib/postgresql/data
    command: ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
    networks:
      - replication_net

  # Первая реплика, которая получает данные от publisher
  subscriber:
    image: postgres:17
    container_name: postgres_subscriber
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: target_db
    ports:
      - "5437:5432"
    volumes:
      # Хранилище данных для первой реплики
      - ./data/subscriber:/var/lib/postgresql/data
      # Конфигурация режима standby
      - ./standby.conf:/etc/postgresql/standby.conf
    command: ["postgres", "-c", "config_file=/etc/postgresql/standby.conf"]
    depends_on:
      - publisher
    networks:
      - replication_net

  # Вторая реплика, которая подключается уже к subscriber
  subscriber2:
    image: postgres:17
    container_name: postgres_subscriber2
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: replica_db
    ports:
      - "5438:5432"
    volumes:
      # Хранилище данных для второй реплики
      - ./data/subscriber2:/var/lib/postgresql/data
      # Конфигурация каскадной репликации
      - ./subscriber2.conf:/etc/postgresql/standby2.conf
      # Файл сигнала для запуска standby-режима
      - ./subscriber2.signal:/var/lib/postgresql/data/standby.signal
    command: ["postgres", "-c", "config_file=/etc/postgresql/standby2.conf"]
    depends_on:
      - subscriber
    networks:
      - replication_net

networks:
  replication_net:
    driver: bridge
```

Этот вариант удобен как исходная точка для разбора ручной настройки, потому что в нём видны все зависимости и можно поэтапно упростить стенд до минимальной версии.

### Заключение
В работе использовался исходный вариант стенда из `docker-compose copy.yml`, где данные хранились в папке `data`, а настройки задавались через отдельные конфигурационные файлы.

После упрощения стенд был переведён на минимальный вариант `docker-compose.yml` с именованными томами и тремя узлами: `publisher`, `subscriber` и `subscriber2`. Это позволило сосредоточиться на ручной настройке каскадной репликации, проверке передачи данных, переключении на реплику и разборе конфликтующих записей.

Таким образом, были изучены основные этапы работы с репликацией: подготовка стенда, создание публикаций и подписок, проверка синхронизации, сценарии переключения и поведение системы при ошибках и конфликтах.

