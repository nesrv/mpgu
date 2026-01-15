# Методичка: CAP-теорема на практике (10 минут)
## Быстрый эксперимент с Redis

### Цель
За 10 минут понять CAP-теорему на практике, используя Redis в режиме standalone vs cluster.

### Что понадобится
- Redis (установлен локально или через Docker)
- Python с библиотекой redis: `pip install redis`

---

## Шаг 1: Простой Redis (2 мин)

### Запуск одного узла Redis:
```bash
redis-server --port 6379
```

### Тест в Python:
```python
import redis

# Подключение к одному узлу
r = redis.Redis(host='127.0.0.1', port=6379)

# Записываем данные
r.set('user:1', 'Alice')
print(f"Записали: {r.get('user:1').decode()}")

# Что происходит при отказе узла?
# Остановите redis-server (Ctrl+C) и попробуйте:
try:
    print(r.get('user:1'))
except Exception as e:
    print(f"Ошибка: {e}")
```

**Вывод:** Одиночный Redis = CA система (Consistency + Availability, но не Partition Tolerance)

---

## Шаг 2: Redis Cluster эмуляция (3 мин)

### Запуск "кластера" из 2 узлов:
```bash
# Терминал 1
redis-server --port 7000

# Терминал 2  
redis-server --port 7001
```

### Тест распределения данных:
```python
import redis

# Подключение к двум узлам
r1 = redis.Redis(host='127.0.0.1', port=7000)
r2 = redis.Redis(host='127.0.0.1', port=7001)

# Записываем данные на разные узлы
r1.set('user:1', 'Alice')
r2.set('user:2', 'Bob')

print(f"Узел 1 знает про user:1: {r1.get('user:1')}")
print(f"Узел 1 знает про user:2: {r1.get('user:2')}")  # None!

print(f"Узел 2 знает про user:1: {r2.get('user:1')}")  # None!
print(f"Узел 2 знает про user:2: {r2.get('user:2')}")
```

**Вывод:** Без синхронизации = AP система (Availability + Partition Tolerance, но не Consistency)

---

## Шаг 3: Эмуляция сетевого разделения (3 мин)

### Тест "падения" узла:
```python
import redis
import time

r1 = redis.Redis(host='127.0.0.1', port=7000)
r2 = redis.Redis(host='127.0.0.1', port=7001)

# Записываем на оба узла
r1.set('counter', '10')
r2.set('counter', '20')

print("До 'падения':")
print(f"Узел 1: {r1.get('counter')}")
print(f"Узел 2: {r2.get('counter')}")

# Теперь остановите один из redis-server (Ctrl+C в терминале)
# И попробуйте:

try:
    print(f"Узел 1 после падения: {r1.get('counter')}")
except:
    print("Узел 1 недоступен")

try:
    print(f"Узел 2 после падения: {r2.get('counter')}")
except:
    print("Узел 2 недоступен")
```

---

## Шаг 4: Выводы (2 мин)

### Что мы увидели:

| Сценарий | C (Consistency) | A (Availability) | P (Partition Tolerance) |
|----------|----------------|------------------|------------------------|
| **Один Redis** | ✅ Да | ✅ Да | ❌ Нет |
| **Два Redis без синхронизации** | ❌ Нет | ✅ Да | ✅ Да |
| **Настоящий Redis Cluster** | ⚖️ Eventual | ✅ Да | ✅ Да |

### Практические выводы:
1. **Банк** выберет CA (один мощный сервер) - лучше недоступность, чем неправильный баланс
2. **Соцсеть** выберет AP (много серверов) - лучше показать старые посты, чем ничего
3. **Нельзя получить все три свойства одновременно!**

### Домашнее задание:
Подумайте, какой компромиссы CAP делают:
- YouTube (видео могут не сразу появляться везде)
- Сбербанк Онлайн (иногда недоступен для обслуживания)
- WhatsApp (сообщения могут дублироваться при сбоях)

---

**Время выполнения:** 10 минут  
**Результат:** Понимание CAP-теоремы на практике через простые эксперименты