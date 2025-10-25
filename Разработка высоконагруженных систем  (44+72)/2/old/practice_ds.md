# Подробное руководство по нагрузочному тестированию и мониторингу

## **Задание 2: Нагрузочное тестирование с мониторингом**

### **1. Подготовка окружения**

Сначала установим необходимые утилиты для мониторинга:

```bash
# Установка системных утилит мониторинга
sudo apt update
sudo apt install -y htop iotop nethogs python3-pip

# Установка Python библиотек для мониторинга
pip install psutil requests
```

### **2. Скрипт для комплексного мониторинга**

Создадим файл `monitor_system.py`:

```python
#!/usr/bin/env python3
import psutil
import time
import json
from datetime import datetime

def get_system_stats():
    """Сбор комплексной статистики системы"""
    
    # CPU статистика
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    cpu_times = psutil.cpu_times_percent()
    
    # Память
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Диск
    disk = psutil.disk_usage('/')
    disk_io = psutil.disk_io_counters()
    
    # Сеть
    network = psutil.net_io_counters()
    
    # Процессы
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except psutil.NoSuchProcess:
            pass
    
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu': {
            'total_percent': cpu_percent,
            'logical_cores': cpu_count,
            'user': cpu_times.user,
            'system': cpu_times.system,
            'idle': cpu_times.idle
        },
        'memory': {
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent': memory.percent
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': disk.percent,
            'read_mb': round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
            'write_mb': round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
        },
        'network': {
            'bytes_sent_mb': round(network.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(network.bytes_recv / (1024**2), 2),
            'packets_sent': network.packets_sent,
            'packets_recv': network.packets_recv
        }
    }

def monitor_loop(duration=60, interval=2):
    """Цикл мониторинга с заданной продолжительностью и интервалом"""
    print("🚀 Запуск мониторинга системы...")
    print("Время | CPU% | Память% | Сеть(МБ) | Диск IO")
    print("-" * 50)
    
    start_time = time.time()
    stats_history = []
    
    try:
        while time.time() - start_time < duration:
            stats = get_system_stats()
            stats_history.append(stats)
            
            # Краткий вывод в консоль
            print(f"{stats['timestamp'][11:19]} | "
                  f"{stats['cpu']['total_percent']:5.1f}% | "
                  f"{stats['memory']['percent']:7.1f}% | "
                  f"{stats['network']['bytes_recv_mb']:5.1f}/"
                  f"{stats['network']['bytes_sent_mb']:5.1f} | "
                  f"{stats['disk']['read_mb']:5.1f}/"
                  f"{stats['disk']['write_mb']:5.1f}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n⏹️  Мониторинг прерван пользователем")
    
    # Сохранение полной статистики в файл
    with open('system_stats.json', 'w') as f:
        json.dump(stats_history, f, indent=2)
    
    print(f"✅ Данные мониторинга сохранены в system_stats.json")
    return stats_history

if __name__ == "__main__":
    monitor_loop(duration=300)  # 5 минут мониторинга
```

### **3. Запуск нагрузочного теста с мониторингом**

Откройте **два терминала**:

#### **Терминал 1 - Мониторинг:**
```bash
# Запуск Python скрипта мониторинга
python3 monitor_system.py

# ИЛИ используем системные утилиты вручную:
# Мониторинг CPU и памяти
htop

# Мониторинг дисковых операций
sudo iotop

# Мониторинг сетевого трафика
sudo nethogs
```

#### **Терминал 2 - Нагрузочный тест:**
```bash
# Простой тест (аналогично вашему примеру)
ab -n 1000 -c 10 http://httpbin.org/get

# Более сложный тест с разными методами
ab -n 2000 -c 20 -k http://httpbin.org/get

# Тест с POST запросами
ab -n 1000 -c 10 -p post_data.txt -T application/json http://httpbin.org/post
```

Создайте файл `post_data.txt` для POST тестов:
```json
{"test": "data", "timestamp": "2024"}
```

### **4. Автоматизированный скрипт для одновременного запуска**

Создайте `run_load_test.sh`:
```bash
#!/bin/bash

echo "🎯 Запуск комплексного нагрузочного тестирования"

# Файлы для результатов
LOAD_RESULT="load_test_result.txt"
MONITOR_RESULT="system_stats.json"

# Запуск мониторинга в фоне
echo "📊 Запуск системы мониторинга..."
python3 monitor_system.py &
MONITOR_PID=$!

# Ждем старта мониторинга
sleep 5

echo "🔥 Запуск нагрузочного теста..."
# Запуск Apache Bench
ab -n 1000 -c 10 http://httpbin.org/get > $LOAD_RESULT

# Останавливаем мониторинг
kill $MONITOR_PID

echo "✅ Тестирование завершено"
echo "📊 Результаты:"
echo "   - Нагрузочный тест: $LOAD_RESULT"
echo "   - Мониторинг системы: $MONITOR_RESULT"

# Анализ результатов
echo "📈 Анализ производительности:"
grep -E "(Requests per second|Time per request|Failed requests)" $LOAD_RESULT
```

Сделайте скрипт исполняемым и запустите:
```bash
chmod +x run_load_test.sh
./run_load_test.sh
```

---

## **Задание 3: Анализ логов веб-сервера**

### **1. Генератор тестовых логов**

Создайте `log_generator.py` для генерации реалистичных логов:
```python
#!/usr/bin/env python3
import random
import time
from datetime import datetime, timedelta

def generate_apache_log():
    """Генерация одной строки лога в формате Apache"""
    
    # Случайные IP адреса
    ips = ['192.168.1.1', '10.0.0.1', '172.16.0.1', '203.0.113.1']
    
    # Endpoints
    endpoints = [
        '/api/users', '/api/orders', '/api/products', 
        '/home', '/about', '/contact',
        '/api/auth/login', '/api/auth/logout'
    ]
    
    # HTTP методы
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    # Статус коды
    status_codes = [200, 201, 400, 401, 404, 500]
    
    # Время ответа (секунды)
    response_times = [0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0, 2.0]
    
    ip = random.choice(ips)
    method = random.choice(methods)
    endpoint = random.choice(endpoints)
    status = random.choice(status_codes)
    response_size = random.randint(100, 5000)
    response_time = random.choice(response_times)
    
    # Текущее время с небольшим случайным смещением
    log_time = datetime.now() - timedelta(seconds=random.randint(0, 3600))
    timestamp = log_time.strftime('%d/%b/%Y:%H:%M:%S +0000')
    
    return f'{ip} - - [{timestamp}] "{method} {endpoint} HTTP/1.1" {status} {response_size} {response_time:.3f}\n'

# Генерация файла с логами
with open('access.log', 'w') as f:
    for _ in range(1000):  # 1000 записей
        f.write(generate_apache_log())

print("✅ Сгенерирован файл access.log с 1000 записями")
```

### **2. Скрипт для анализа логов**

Создайте `log_analyzer.py`:
```python
#!/usr/bin/env python3
import re
from datetime import datetime
import statistics
from collections import Counter

class ApacheLogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.requests = []
        
        # Регулярное выражение для парсинга Apache логов
        self.pattern = r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) ([\d.]+)'
    
    def parse_logs(self):
        """Парсинг лог файла"""
        print("📖 Чтение и анализ логов...")
        
        with open(self.log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                match = re.match(self.pattern, line.strip())
                if match:
                    ip, timestamp, request, status, size, response_time = match.groups()
                    
                    # Парсинг HTTP запроса
                    method, endpoint, _ = self.parse_request(request)
                    
                    self.requests.append({
                        'ip': ip,
                        'timestamp': timestamp,
                        'method': method,
                        'endpoint': endpoint,
                        'status': int(status),
                        'size': int(size),
                        'response_time': float(response_time),
                        'line_number': line_num
                    })
        
        print(f"✅ Обработано записей: {len(self.requests)}")
    
    def parse_request(self, request_str):
        """Парсинг строки HTTP запроса"""
        parts = request_str.split()
        if len(parts) >= 2:
            return parts[0], parts[1], ' '.join(parts[2:])
        return 'UNKNOWN', 'UNKNOWN', 'UNKNOWN'
    
    def calculate_metrics(self):
        """Расчет основных метрик"""
        if not self.requests:
            print("❌ Нет данных для анализа")
            return
        
        # Среднее время ответа
        response_times = [r['response_time'] for r in self.requests]
        avg_response_time = statistics.mean(response_times)
        
        # Количество запросов по статус-кодам
        status_counts = Counter(r['status'] for r in self.requests)
        
        # Топ самых медленных запросов
        slow_requests = sorted(self.requests, 
                             key=lambda x: x['response_time'], 
                             reverse=True)[:10]
        
        # Распределение по методам
        method_counts = Counter(r['method'] for r in self.requests)
        
        # Популярные endpoints
        endpoint_counts = Counter(r['endpoint'] for r in self.requests)
        
        return {
            'total_requests': len(self.requests),
            'avg_response_time': avg_response_time,
            'status_counts': dict(status_counts),
            'method_counts': dict(method_counts),
            'endpoint_counts': dict(endpoint_counts.most_common(10)),
            'slow_requests': slow_requests,
            'response_time_stats': {
                'min': min(response_times),
                'max': max(response_times),
                'median': statistics.median(response_times),
                'p95': sorted(response_times)[int(len(response_times) * 0.95)]
            }
        }
    
    def generate_report(self, metrics):
        """Генерация отчета"""
        print("\n" + "="*60)
        print("📊 ОТЧЕТ АНАЛИЗА ЛОГОВ ВЕБ-СЕРВЕРА")
        print("="*60)
        
        print(f"\n📈 ОСНОВНЫЕ МЕТРИКИ:")
        print(f"   Всего запросов: {metrics['total_requests']}")
        print(f"   Среднее время ответа: {metrics['avg_response_time']:.3f} сек")
        
        print(f"\n⏱️  СТАТИСТИКА ВРЕМЕНИ ОТВЕТА:")
        stats = metrics['response_time_stats']
        print(f"   Минимальное: {stats['min']:.3f} сек")
        print(f"   Максимальное: {stats['max']:.3f} сек")
        print(f"   Медиана: {stats['median']:.3f} сек")
        print(f"   95-й перцентиль: {stats['p95']:.3f} сек")
        
        print(f"\n🔢 СТАТУС-КОДЫ:")
        for status, count in sorted(metrics['status_counts'].items()):
            print(f"   {status}: {count} запросов")
        
        print(f"\n🛠️  HTTP МЕТОДЫ:")
        for method, count in metrics['method_counts'].items():
            print(f"   {method}: {count} запросов")
        
        print(f"\n🌐 ПОПУЛЯРНЫЕ ENDPOINTS:")
        for endpoint, count in metrics['endpoint_counts'].items():
            print(f"   {endpoint}: {count} запросов")
        
        print(f"\n🐢 ТОП-10 САМЫХ МЕДЛЕННЫХ ЗАПРОСОВ:")
        for i, req in enumerate(metrics['slow_requests'], 1):
            print(f"   {i:2d}. {req['method']} {req['endpoint']} - "
                  f"{req['response_time']:.3f} сек (Status: {req['status']})")
    
    def analyze(self):
        """Основной метод анализа"""
        self.parse_logs()
        metrics = self.calculate_metrics()
        self.generate_report(metrics)

# Запуск анализа
if __name__ == "__main__":
    analyzer = ApacheLogAnalyzer('access.log')
    analyzer.analyze()
```

### **3. Дополнительные утилиты анализа**

Создайте `advanced_log_analysis.py` для расширенного анализа:
```python
#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def advanced_analysis():
    """Расширенный анализ с визуализацией"""
    
    # Чтение логов в DataFrame
    data = []
    with open('access.log', 'r') as f:
        for line in f:
            # Простой парсинг для демонстрации
            if 'GET' in line or 'POST' in line:
                parts = line.split()
                if len(parts) >= 10:
                    data.append({
                        'ip': parts[0],
                        'method': parts[5][1:],  # Убираем кавычку
                        'endpoint': parts[6],
                        'status': int(parts[8]),
                        'response_time': float(parts[9])
                    })
    
    df = pd.DataFrame(data)
    
    print("📊 РАСШИРЕННЫЙ АНАЛИЗ:")
    print(f"\nСтатистика по времени ответа:")
    print(df['response_time'].describe())
    
    # Группировка по статус-кодам
    status_groups = df.groupby('status').size()
    print(f"\nРаспределение по статус-кодам:")
    print(status_groups)
    
    # Топ IP адресов
    top_ips = df['ip'].value_counts().head(5)
    print(f"\nТоп-5 IP адресов:")
    print(top_ips)

if __name__ == "__main__":
    advanced_analysis()
```

### **4. Запуск полного анализа**

```bash
# 1. Генерация тестовых логов
python3 log_generator.py

# 2. Основной анализ
python3 log_analyzer.py

# 3. Расширенный анализ (если установлен pandas)
python3 advanced_log_analysis.py
```

## **Ключевые выводы по каждому заданию:**

### **Задание 2 - Мониторинг:**
- ✅ Отслеживание CPU, памяти, диска, сети в реальном времени
- ✅ Корреляция нагрузки системы с нагрузочным тестом
- ✅ Выявление "узких мест" производительности

### **Задание 3 - Анализ логов:**
- ✅ Парсинг сложного формата Apache логов
- ✅ Расчет ключевых метрик производительности
- ✅ Выявление медленных запросов и ошибок
- ✅ Статистика по методам и endpoint'ам

Этот комплексный подход дает полное понимание работы системы под нагрузкой!