# База данных для отслеживания вклада разработчиков в open-source проекты

## Назначение

База данных предназначена для:
- Учета участников open-source проектов
- Отслеживания активности разработчиков
- Анализа популярности репозиториев
- Статистики по языкам программирования и технологиям
- Мониторинга вклада каждого участника в проекты

## Структура базы данных

### Таблицы

#### contributors
Участники проектов
- `user_id` (PK) - уникальный идентификатор
- `username` - никнейм пользователя
- `full_name` - полное имя

#### repositories  
Репозитории проектов
- `repo_id` (PK) - уникальный идентификатор
- `name` - название репозитория
- `description` - описание проекта
- `stars` - количество звезд
- `repo_metadata` (JSON) - метаданные проекта

#### contributions
Вклады участников в проекты (связующая таблица)
- `user_id` (PK, FK) - ссылка на участника
- `repo_id` (PK, FK) - ссылка на репозиторий
- `commits_count` - количество коммитов
- `last_activity` - дата последней активности

## Связи

### Диаграмма связей
```
contributors (1) ----< contributions >---- (1) repositories
    user_id              user_id, repo_id              repo_id
```

### Описание связей
- **contributors → contributions**: один участник может иметь много вкладов (1:N)
- **repositories → contributions**: один репозиторий может иметь много вкладов (1:N)  
- **contributors ↔ repositories**: участники и репозитории связаны через contributions (M:N)

### Ключи
- `contributions.user_id` → `contributors.user_id` (FK)
- `contributions.repo_id` → `repositories.repo_id` (FK)
- Составной первичный ключ: `(user_id, repo_id)` в таблице contributions

## JSON поле repo_metadata

Содержит дополнительную информацию о проекте:

```json
{
  "language": "Python",
  "framework": "FastAPI", 
  "tags": ["web", "api"],
  "libraries": ["pandas", "sklearn"],
  "difficulty": "beginner",
  "type": "library",
  "platforms": ["linux", "windows"]
}
```

### Поля JSON:
- `language` - язык программирования
- `framework` - используемый фреймворк
- `tags` - массив тегов
- `libraries` - массив библиотек
- `difficulty` - уровень сложности
- `type` - тип проекта
- `platforms` - поддерживаемые платформы

## Примеры данных

### Участники
- alice_dev (Алиса Смирнова)
- bob_code (Борис Иванов)  
- clara_python (Клара Петрова)

### Проекты
- веб-шаблон (Python/FastAPI, 1200 звезд)
- мл-инструменты (Python/ML, 870 звезд)
- консоль-логгер (Go/library, 340 звезд)

### Активность
- Алиса: 57 коммитов в 2 проекта
- Борис: 28 коммитов в 1 проект
- Клара: 65 коммитов в 2 проекта