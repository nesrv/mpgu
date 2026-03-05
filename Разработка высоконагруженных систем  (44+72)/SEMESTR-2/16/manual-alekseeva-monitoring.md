# Методичка: Мониторинг FastAPI с Prometheus и Grafana

**Продолжение:** manual-alekseeva.md  
**Домен:** alekseeva.h1n.ru  
**Сервер:** 81.90.182.174

---

## Содержание

1. [Часть 5: Добавление метрик в FastAPI](#часть-5-добавление-метрик-в-fastapi)
2. [Часть 6: Установка Prometheus](#часть-6-установка-prometheus)
3. [Часть 7: Установка Grafana](#часть-7-установка-grafana)
4. [Часть 8: Настройка дашборда](#часть-8-настройка-дашборда)
5. [Удаление (откат лабы)](#удаление-как-откатить-всё-что-сделано-в-этой-лабе)

---

## Архитектура мониторинга

```
┌─────────────────────────────────────────────────────────────┐
│                        VDS сервер                           │
│                                                             │
│  ┌───────────┐    scrape    ┌────────────┐    query        │
│  │  FastAPI  │─────────────▶│ Prometheus │◀────────────┐   │
│  │  :8010    │   /metrics   │   :9090    │             │   │
│  └───────────┘              └────────────┘             │   │
│                                                        │   │
│                             ┌────────────┐             │   │
│                             │  Grafana   │─────────────┘   │
│                             │   :3000    │                 │
│                             └────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Внешний доступ:
  - alekseeva.h1n.ru/          → FastAPI
  - alekseeva.h1n.ru/grafana/  → Grafana
  - alekseeva.h1n.ru/prometheus/ → Prometheus (опционально)
```

---

## Часть 5: Добавление метрик в FastAPI

### 5.1. Установка библиотеки

```bash
ssh root@81.90.182.174

cd /opt/alekseeva-api
source venv/bin/activate

pip install prometheus-fastapi-instrumentator
```

---

### 5.2. Обновление main.py

```bash
cat > main.py << 'EOF'
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="API Алексеевой",
    description="Мой первый API на FastAPI с мониторингом",
    version="1.1.0"
)

# Инициализация Prometheus метрик
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

@app.get("/")
def home():
    """Главная страница"""
    return {"message": "Привет, мир!", "author": "Алексеева"}

@app.get("/health")
def health():
    """Проверка работоспособности"""
    return {"status": "ok"}

@app.get("/about")
def about():
    """Информация об авторе"""
    return {
        "name": "Алексеева",
        "project": "Учебный проект FastAPI",
        "monitoring": "Prometheus + Grafana"
    }
EOF
```

---

### 5.3. Обновление requirements.txt

```bash
cat > requirements.txt << 'EOF'
fastapi
uvicorn
prometheus-fastapi-instrumentator
EOF
```

---

### 5.4. Перезапуск приложения

```bash
systemctl restart alekseeva-api
systemctl status alekseeva-api
```

---

### 5.5. Проверка метрик

```bash
curl http://127.0.0.1:8010/metrics
```

Вы увидите метрики в формате Prometheus:

```
# HELP http_requests_total Total number of requests
# TYPE http_requests_total counter
http_requests_total{handler="/",method="GET",status="2xx"} 5.0
http_request_duration_seconds_bucket{handler="/",le="0.01",method="GET"} 5.0
...
```

---

## Часть 6: Установка Prometheus

### 6.1. Создание пользователя и директорий

```bash
# Пользователь для Prometheus
useradd --no-create-home --shell /bin/false prometheus

# Директории
mkdir -p /etc/prometheus
mkdir -p /var/lib/prometheus

chown prometheus:prometheus /etc/prometheus
chown prometheus:prometheus /var/lib/prometheus
```

---

### 6.2. Скачивание Prometheus

```bash
cd /tmp

# Скачиваем последнюю версию
wget https://github.com/prometheus/prometheus/releases/download/v2.48.0/prometheus-2.48.0.linux-amd64.tar.gz

# Распаковываем
tar xvfz prometheus-2.48.0.linux-amd64.tar.gz
cd prometheus-2.48.0.linux-amd64

# Копируем бинарники
cp prometheus /usr/local/bin/
cp promtool /usr/local/bin/

chown prometheus:prometheus /usr/local/bin/prometheus
chown prometheus:prometheus /usr/local/bin/promtool

# Копируем конфиги
cp -r consoles /etc/prometheus/
cp -r console_libraries /etc/prometheus/

chown -R prometheus:prometheus /etc/prometheus/consoles
chown -R prometheus:prometheus /etc/prometheus/console_libraries
```

---

### 6.3. Конфигурация Prometheus

```bash
cat > /etc/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers: []

rule_files: []

scrape_configs:
  # Мониторинг самого Prometheus
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Мониторинг FastAPI приложения
  - job_name: 'fastapi-alekseeva'
    static_configs:
      - targets: ['127.0.0.1:8010']
    metrics_path: /metrics
    scrape_interval: 10s
EOF

chown prometheus:prometheus /etc/prometheus/prometheus.yml
```

---

### 6.4. Systemd сервис для Prometheus

```bash
cat > /etc/systemd/system/prometheus.service << 'EOF'
[Unit]
Description=Prometheus Monitoring
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.path=/var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=127.0.0.1:9090 \
    --web.external-url=http://alekseeva.h1n.ru/prometheus/ \
    --web.route-prefix=/ \
    --storage.tsdb.retention.time=15d

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable prometheus
systemctl start prometheus
systemctl status prometheus
```

> **Примечание:** Параметры `--web.external-url` и `--web.route-prefix` нужны для корректной работы через subpath `/prometheus/`.

---

### 6.5. Проверка Prometheus

```bash
curl http://127.0.0.1:9090/api/v1/targets
```

Должен показать target `fastapi-alekseeva` в состоянии `up`.

---

## Часть 7: Установка Grafana

### 7.1. Установка Grafana из deb пакета

> **Примечание:** Репозиторий Grafana может быть недоступен в некоторых регионах. Используем прямую установку из deb пакета.

```bash
cd /tmp

# Скачиваем deb пакет
wget https://dl.grafana.com/oss/release/grafana_10.2.3_amd64.deb

# Устанавливаем
dpkg -i grafana_10.2.3_amd64.deb

# Если будут ошибки зависимостей — исправляем:
apt --fix-broken install -y
```

---

### 7.2. Настройка Grafana

```bash
# Редактируем конфиг для работы через subpath /grafana/
cat > /etc/grafana/grafana.ini << 'EOF'
[server]
http_addr = 127.0.0.1
http_port = 3000
domain = alekseeva.h1n.ru
root_url = %(protocol)s://%(domain)s/grafana/
serve_from_sub_path = true

[security]
admin_user = admin
admin_password = student123

[users]
allow_sign_up = false

[auth.anonymous]
enabled = false
EOF
```

---

### 7.3. Запуск Grafana

```bash
systemctl daemon-reload
systemctl enable grafana-server
systemctl start grafana-server
systemctl status grafana-server
```

---

### 7.4. Настройка Nginx

Обновляем конфиг Nginx для проксирования Grafana и Prometheus:

```bash
cat > /etc/nginx/sites-available/alekseeva << 'EOF'
server {
    listen 80;
    server_name alekseeva.h1n.ru;
    
    # FastAPI приложение
    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Grafana (без trailing slash в proxy_pass!)
    location /grafana/ {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Server $host;
    }
    
    # Prometheus
    location /prometheus/ {
        proxy_pass http://127.0.0.1:9090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

nginx -t && systemctl reload nginx
```

> **Важно:** Для Grafana `proxy_pass` указан БЕЗ trailing slash (`http://127.0.0.1:3000`), иначе будет redirect loop.

---

### 7.5. Проверка доступа

- **FastAPI:** http://alekseeva.h1n.ru/
- **Grafana:** http://alekseeva.h1n.ru/grafana/
- **Prometheus:** http://alekseeva.h1n.ru/prometheus/

Логин в Grafana:
- **Username:** admin
- **Password:** student123

---

## Часть 8: Настройка дашборда

### 8.1. Добавление Data Source в Grafana

1. Откройте http://alekseeva.h1n.ru/grafana/
2. Войдите (admin / student123)
3. Перейдите: **⚙️ Configuration** → **Data Sources**
4. Нажмите **Add data source**
5. Выберите **Prometheus**
6. Настройки:
   - **URL:** `http://127.0.0.1:9090`
   - Остальное по умолчанию
7. Нажмите **Save & Test** — должно показать "Data source is working"

---

### 8.2. Импорт готового дашборда

1. Перейдите: **➕** → **Import**
2. Введите ID дашборда: `11074` (FastAPI Dashboard)
3. Нажмите **Load**
4. Выберите Prometheus data source
5. Нажмите **Import**

Или создайте свой дашборд с панелями.

---

### 8.3. Создание простого дашборда вручную

1. **➕** → **Dashboard** → **Add new panel**

2. **Панель 1: Количество запросов**
   - Query: `sum(rate(http_requests_total[5m]))`
   - Title: "Requests per second"
   - Visualization: Graph

3. **Панель 2: Время ответа**
   - Query: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
   - Title: "Response time (p95)"
   - Visualization: Graph

4. **Панель 3: Статус приложения**
   - Query: `up{job="fastapi-alekseeva"}`
   - Title: "Application Status"
   - Visualization: Stat

5. Сохраните дашборд: **💾** → Name: "FastAPI Monitoring"

---

## Полезные команды

| Действие | Команда |
|----------|---------|
| Статус Prometheus | `systemctl status prometheus` |
| Логи Prometheus | `journalctl -u prometheus -f` |
| Статус Grafana | `systemctl status grafana-server` |
| Логи Grafana | `journalctl -u grafana-server -f` |
| Перезапуск всего | `systemctl restart alekseeva-api prometheus grafana-server` |
| Проверка метрик | `curl http://127.0.0.1:8010/metrics` |
| Проверка targets | `curl http://127.0.0.1:9090/api/v1/targets` |

---

## Полезные метрики FastAPI

| Метрика | Описание |
|---------|----------|
| `http_requests_total` | Общее количество запросов |
| `http_request_duration_seconds` | Время обработки запросов |
| `http_requests_in_progress` | Текущие активные запросы |
| `http_request_size_bytes` | Размер входящих запросов |
| `http_response_size_bytes` | Размер ответов |

---

## Примеры PromQL запросов

```promql
# Запросов в секунду
rate(http_requests_total[5m])

# Запросов в секунду по endpoint
sum by (handler) (rate(http_requests_total[5m]))

# 95-й перцентиль времени ответа
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Количество ошибок (5xx)
sum(rate(http_requests_total{status=~"5.."}[5m]))

# Процент успешных запросов
sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
```

---

## Итог

После выполнения всех шагов у вас будет:

1. ✅ FastAPI с метриками на http://alekseeva.h1n.ru/
2. ✅ Эндпоинт `/metrics` для Prometheus
3. ✅ Prometheus собирает метрики каждые 10 секунд
4. ✅ Grafana визуализирует данные
5. ✅ Дашборд с графиками запросов и времени ответа

---

## Требования к серверу

| Компонент | RAM | CPU |
|-----------|-----|-----|
| FastAPI | ~30 МБ | минимум |
| Prometheus | ~200-300 МБ | минимум |
| Grafana | ~200-300 МБ | минимум |
| **Итого** | ~500-700 МБ | 1 CPU |

> ⚠️ Если на VDS мало RAM (< 1 ГБ), можно использовать Grafana Cloud (бесплатный tier) вместо локальной Grafana.

---

---

## Удаление: как откатить всё, что сделано в этой лабе

Если нужно полностью убрать мониторинг с VPS:

### 1. Остановить и удалить сервисы Prometheus и Grafana

```bash
systemctl stop prometheus grafana-server
systemctl disable prometheus grafana-server
```

### 2. Удалить systemd-юниты

```bash
rm /etc/systemd/system/prometheus.service
systemctl daemon-reload
```

### 3. Удалить Grafana

Grafana ставили вручную через `dpkg -i`, поэтому удаляем через dpkg:

```bash
# Узнать точное имя пакета (если не уверены)
dpkg -l | grep grafana

# Удалить (имя может быть grafana или grafana-enterprise)
dpkg --purge grafana

# Если пакет не найден в dpkg — удалить файлы вручную
rm -rf /etc/grafana
rm -rf /var/lib/grafana
rm -f /etc/systemd/system/grafana-server.service
# (systemd-юнит Grafana обычно в /usr/lib/systemd/system/)
systemctl daemon-reload
```

### 4. Удалить Prometheus (установлен вручную)

```bash
# Удалить бинарники (если есть)
rm -f /usr/local/bin/prometheus /usr/local/bin/promtool

# Удалить конфиги и данные
rm -rf /etc/prometheus /var/lib/prometheus

# Удалить пользователя (если есть)
userdel prometheus 2>/dev/null || true
```

> Если файлов нет — Prometheus не устанавливался или уже удалён. Пропустите шаг.

### 5. Вернуть Nginx к конфигу без Grafana и Prometheus

```bash
cat > /etc/nginx/sites-available/alekseeva << 'EOF'
server {
    listen 80;
    server_name alekseeva.h1n.ru;
    
    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

nginx -t && systemctl reload nginx
```

### 6. Убрать prometheus-fastapi-instrumentator из FastAPI

```bash
cd /opt/alekseeva-api
source venv/bin/activate

pip uninstall -y prometheus-fastapi-instrumentator
```

Восстановите исходные `main.py` и `requirements.txt` (без Instrumentator и метрик). Пример минимального main.py:

```bash
cat > main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(
    title="API Алексеевой",
    description="Мой первый API на FastAPI",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Привет, мир!", "author": "Алексеева"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/about")
def about():
    return {"name": "Алексеева", "project": "Учебный проект FastAPI"}
EOF

cat > requirements.txt << 'EOF'
fastapi
uvicorn
EOF

systemctl restart alekseeva-api
```

### 7. Удалить временные файлы (по желанию)

```bash
rm -f /tmp/prometheus-2.48.0.linux-amd64.tar.gz
rm -rf /tmp/prometheus-2.48.0.linux-amd64
rm -f /tmp/grafana_10.2.3_amd64.deb
```

После этого на VPS останется только FastAPI без мониторинга.

---

**Вопросы?** Обращайтесь к преподавателю.
