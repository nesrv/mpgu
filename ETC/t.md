
Отлично! Вот пошаговое решение с использованием Python для вывода сообщения.

## Решение: Создание Hello World контейнера с Python

### Шаг 1: Создаем Python скрипт

Создайте файл `app.py` со следующим содержимым:

```python
#!/usr/bin/env python3

def main():
    message = "Привет из моего контейнера!"
    print(message)

if __name__ == "__main__":
    main()
```

### Шаг 3: Создаем Dockerfile

**Упрощенный вариант Dockerfile:**

```dockerfile
FROM FROM python:3.13-rc-alpine

COPY app.py .

CMD ["python", "app.py"]
```


**Типовой вариант Dockerfile:**
```dockerfile
FROM FROM python:3.13-rc-alpine

# Устанавливаем метаинформацию
LABEL maintainer="your-name@example.com"
LABEL description="My custom hello world container with Python"

# Копируем Python скрипт в контейнер
COPY app.py /app/app.py

# Устанавливаем рабочую директорию
WORKDIR /app

# Запускаем Python скрипт при старте контейнера
CMD ["python", "app.py"]
```

### Шаг 4: Собираем Docker образ

```bash
docker build -t my-hello .
```

### Шаг 5: Запускаем контейнер

```bash
docker run my-hello
```

**Ожидаемый результат:**
```
Hello from my custom container!
```

## Дополнительные варианты реализации

### Вариант 1: С использованием ENTRYPOINT

```dockerfile
FROM python:3.9-alpine

COPY app.py /app/app.py
WORKDIR /app

ENTRYPOINT ["python", "app.py"]
```
