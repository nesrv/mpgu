# Методичка

## PostgreSQL High Availability

### Docker Compose + Patroni + etcd + HAProxy

---

## 0. Цель методички

Студент **должен понять**, а не просто запустить:

* как работает **репликация PostgreSQL**
* почему **PostgreSQL сам не умеет HA**
* что делает **Patroni**
* зачем нужен **etcd**
* как **HAProxy** узнаёт, кто primary
* что происходит при **падении primary**

---

## 1. Архитектура стенда

```text
Client / psql / app
        |
     HAProxy (5432)
        |
   ┌───────────────┐
   │   Patroni     │  ← HTTP API :8008
   │ PostgreSQL-1  │  ← PRIMARY / REPLICA
   └───────────────┘
            │
         streaming
            │
   ┌───────────────┐
   │   Patroni     │
   │ PostgreSQL-2  │
   └───────────────┘
            │
         distributed lock
            │
        ┌─────────┐
        │  etcd   │
        └─────────┘
```

---

## 2. Компоненты и их роли

| Компонент      | Роль                                |
| -------------- | ----------------------------------- |
| PostgreSQL     | Хранение данных                     |
| Patroni        | Управление ролями (primary/replica) |
| etcd           | Distributed lock / leader election  |
| HAProxy        | Проксирование к current primary     |
| Docker Compose | Среда запуска                       |

---

## 3. Требования

* Linux VPS (2 CPU / 4 GB RAM достаточно)
* Docker
* Docker Compose v2
* Открытые порты:

  * `5432` — PostgreSQL (через HAProxy)
  * `8008` — Patroni API (внутренняя сеть)

---

## 4. Структура проекта

```text
postgres-ha/
├── docker-compose.yml
├── haproxy/
│   └── haproxy.cfg
└── patroni/
    └── patroni.yml
```

---

## 5. docker-compose.yml

```yaml
version: "3.8"

services:

  etcd:
    image: quay.io/coreos/etcd:v3.5.9
    command: >
      etcd
      --name etcd1
      --initial-advertise-peer-urls http://etcd:2380
      --listen-peer-urls http://0.0.0.0:2380
      --listen-client-urls http://0.0.0.0:2379
      --advertise-client-urls http://etcd:2379
      --initial-cluster etcd1=http://etcd:2380
    networks: [pgnet]

  postgres1:
    image: patroni
    container_name: pg1
    hostname: pg1
    volumes:
      - pg1_data:/data
    environment:
      PATRONI_NAME: pg1
      PATRONI_ETCD_HOSTS: etcd:2379
    networks: [pgnet]
    depends_on: [etcd]

  postgres2:
    image: patroni
    container_name: pg2
    hostname: pg2
    volumes:
      - pg2_data:/data
    environment:
      PATRONI_NAME: pg2
      PATRONI_ETCD_HOSTS: etcd:2379
    networks: [pgnet]
    depends_on: [etcd]

  haproxy:
    image: haproxy:2.9
    ports:
      - "5432:5432"
    volumes:
      - ./haproxy/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
    networks: [pgnet]
    depends_on: [postgres1, postgres2]

networks:
  pgnet:

volumes:
  pg1_data:
  pg2_data:
```

⚠️ Образ `patroni` можно взять:

* `zalando/patroni`
* или собрать кастомный (лучше для обучения)

---

## 6. Конфигурация Patroni (`patroni.yml`)

```yaml
scope: postgres-ha
namespace: /db/

restapi:
  listen: 0.0.0.0:8008
  connect_address: {{ hostname }}:8008

etcd:
  hosts: etcd:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    postgresql:
      use_pg_rewind: true
      parameters:
        wal_level: replica
        hot_standby: "on"
        max_wal_senders: 10
        max_replication_slots: 10

  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: {{ hostname }}:5432
  data_dir: /data
  authentication:
    replication:
      username: replicator
      password: replicator
    superuser:
      username: postgres
      password: postgres
```

---

## 7. HAProxy (`haproxy.cfg`)

```conf
defaults
  mode tcp
  timeout connect 5s
  timeout client  1m
  timeout server  1m

frontend postgres
  bind *:5432
  default_backend postgres_nodes

backend postgres_nodes
  option httpchk GET /primary
  http-check expect status 200

  server pg1 pg1:5432 check port 8008
  server pg2 pg2:5432 check port 8008
```

---

## 8. Запуск стенда

```bash
docker compose up -d
```

Проверка:

```bash
docker ps
```

---

## 9. Проверка ролей

```bash
docker exec -it pg1 patronictl list
```

Пример вывода:

```text
+ Cluster: postgres-ha -----+
| Member | Role    | State  |
+--------+---------+--------+
| pg1    | Leader  | running|
| pg2    | Replica | running|
+--------+---------+--------+
```

---

## 10. Подключение к PostgreSQL

```bash
psql -h localhost -p 5432 -U postgres
```

❗ Всегда подключение идёт **к primary**, даже после failover.

---

## 11. Лабораторные работы (ОБЯЗАТЕЛЬНО)

### Лаба 1 — Убийство primary

```bash
docker stop pg1
```

Наблюдаем:

```bash
docker exec -it pg2 patronictl list
```

👉 pg2 стал Leader
👉 HAProxy переключился автоматически

---

### Лаба 2 — Возвращение старого primary

```bash
docker start pg1
```

👉 pg1 возвращается как **Replica**
👉 split-brain НЕ происходит

---

### Лаба 3 — Падение etcd

```bash
docker stop etcd
```

Обсуждение:

* почему нельзя promote
* почему Patroni «замер»

---

### Лаба 4 — Запросы на реплике

```sql
SELECT pg_is_in_recovery();
```

---

## 12. Вопросы для студентов (контроль понимания)

1. Почему PostgreSQL не может сам выбрать primary?
2. Что хранится в etcd?
3. Почему нельзя сделать HA без distributed lock?
4. Что будет, если HAProxy подключить напрямую к postgres1?
5. Чем отличается failover от restart?

---

## 13. Что считается «продом»

✅ Patroni
✅ Distributed lock
✅ Proxy
❌ docker-compose (условно)

---

## 14. Итог

> **Docker Compose + Patroni + etcd + HAProxy**
> — идеальный учебный стенд:

* прозрачно
* воспроизводимо
* ломаемо
* приближено к реальному продакшену

---

## Хочешь продолжение?

Могу:

* сделать **вариант для Kubernetes**
* добавить **наблюдение (Prometheus)**
* оформить это в **PDF / markdown**
* добавить **чек-лист для экзамена**

Просто скажи 👌
