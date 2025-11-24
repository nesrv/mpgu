# Практика: SQLAlchemy ORM с json

## Описание базы данных

## Назначение

База данных предназначена для:
- Учета участников open-source проектов
- Отслеживания активности разработчиков
- Анализа популярности репозиториев
- Статистики по языкам программирования и технологиям
- Мониторинга вклада каждого участника в проекты

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

## Инициализация и наполнения таблиц в бд

```py

from datetime import date
from sqlalchemy import create_engine, select, func, text, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

# Базовый класс
class Base(DeclarativeBase):
    pass

# Модели — теперь с более чистыми аннотациями
class Contributor(Base):
    __tablename__ = "contributors"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    full_name: Mapped[str]


class Repository(Base):
    __tablename__ = "repositories"

    repo_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    stars: Mapped[int]
    repo_metadata: Mapped[dict] = mapped_column(JSON)


class Contribution(Base):
    __tablename__ = "contributions"

    # Составной PK: два внешних ключа
    user_id: Mapped[int] = mapped_column(
        ForeignKey("contributors.user_id"), primary_key=True
    )
    repo_id: Mapped[int] = mapped_column(
        ForeignKey("repositories.repo_id"), primary_key=True
    )

    commits_count: Mapped[int]
    last_activity: Mapped[date]


# Создание и заполнение БД

engine = create_engine("postgresql://student:password@localhost:5435/students_db")
try:
    Base.metadata.drop_all(engine)
except:
    pass
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.execute(text("DELETE FROM contributions"))
    session.execute(text("DELETE FROM contributors"))
    session.execute(text("DELETE FROM repositories"))
    session.commit()

    # Данные
    contributors = [
        Contributor(user_id=1, username="alice_dev", full_name="Алиса Смирнова"),
        Contributor(user_id=2, username="bob_code", full_name="Борис Иванов"),
        Contributor(user_id=3, username="clara_python", full_name="Клара Петрова"),
    ]

    repos = [
        Repository(repo_id=101, name="веб-шаблон", description="Современный стартер для веб-приложений", stars=1200, repo_metadata={"language": "Python", "framework": "FastAPI", "tags": ["web", "api"]}),
        Repository(repo_id=102, name="мл-инструменты", description="Утилиты машинного обучения для студентов", stars=870, repo_metadata={"language": "Python", "libraries": ["pandas", "sklearn"], "difficulty": "beginner"}),
        Repository(repo_id=103, name="консоль-логгер", description="Простая библиотека для логирования", stars=340, repo_metadata={"language": "Go", "type": "library", "platforms": ["linux", "windows"]}),
    ]

    contributions = [
        Contribution(user_id=1, repo_id=101, commits_count=42, last_activity=date(2025, 10, 15)),
        Contribution(user_id=1, repo_id=102, commits_count=15, last_activity=date(2025, 9, 20)),
        Contribution(user_id=2, repo_id=101, commits_count=28, last_activity=date(2025, 11, 1)),
        Contribution(user_id=3, repo_id=102, commits_count=60, last_activity=date(2025, 11, 20)),
        Contribution(user_id=3, repo_id=103, commits_count=5, last_activity=date(2025, 8, 5)),
    ]

    session.add_all(contributors)
    session.add_all(repos)
    session.commit()
    
    session.add_all(contributions)
    session.commit()
```



## Паактические задачи

```py

from datetime import date
from sqlalchemy import select, func, update, cast, String
from sqlalchemy.orm import Session
from source import *

# 1. Простые задания на sqlalchemy 2.x

# 1.1 Найти всех участников
# SQL: SELECT username, full_name FROM contributors;
def task_1_1():
    with Session(engine) as session:
        stmt = select(Contributor)
        for contributor in session.execute(stmt).scalars():
            print(f"{contributor.username}: {contributor.full_name}")

# 1.2 Найти все репозитории с количеством звезд больше 500
# SQL: SELECT name, stars FROM repositories WHERE stars > 500;
def task_1_2():
    with Session(engine) as session:
        ....

# 1.3 Найти все вклады конкретного участника
# SQL: SELECT user_id, commits_count FROM contributions WHERE user_id = 1;
def task_1_3():
    with Session(engine) as session:
        ...

# 1.4 Подсчитать общее количество участников
# SQL: SELECT COUNT(*) FROM contributors;
def task_1_4():
    with Session(engine) as session:
       ...

# 1.5 Найти репозиторий с максимальным количеством звезд
# SQL: SELECT name, stars FROM repositories ORDER BY stars DESC LIMIT 1;
def task_1_5():
    with Session(engine) as session:
        ...

# 2. Средние задания на sqlalchemy

# 2.1 Найти участников и их общее количество коммитов
# SQL: SELECT c.username, SUM(co.commits_count) as total FROM contributors c NATURAL JOIN contributions co GROUP BY c.user_id;
def task_2_1():
    with Session(engine) as session:
       ...

# 2.2 Найти все Python проекты через JSON
# SQL: SELECT name FROM repositories WHERE repo_metadata->>'language' = 'Python';
def task_2_2():
    with Session(engine) as session:
       ...

# 2.3 Найти участников, работающих с FastAPI
# SQL: SELECT c.full_name, r.name FROM contributions co NATURAL JOIN contributors c NATURAL JOIN repositories r WHERE r.repo_metadata->>'framework' = 'FastAPI';
def task_2_3():
    with Session(engine) as session:
       ...

# 2.4 Подсчитать проекты по языкам программирования
# SQL: SELECT repo_metadata->>'language' as language, COUNT(*) as count FROM repositories GROUP BY repo_metadata->>'language';
def task_2_4():
    with Session(engine) as session:
       ...

# 2.5 Найти участников с активностью в последние 3 месяца
# SQL: SELECT DISTINCT c.full_name FROM contributors c NATURAL JOIN contributions co WHERE co.last_activity >= '2025-09-01';
def task_2_5():
    with Session(engine) as session:
       ...

# 3. Сложные задания на sqlalchemy

# 3.1 Найти самого активного участника через подзапрос
# SQL: SELECT c.full_name, s.total FROM contributors c NATURAL JOIN (SELECT user_id, SUM(commits_count) as total FROM contributions GROUP BY user_id) s ORDER BY s.total DESC LIMIT 1;

def task_3_1():
    with Session(engine) as session:
        subq = (
            select(
                Contribution.user_id,
                func.sum(Contribution.commits_count).label('total')
            )
            .group_by(Contribution.user_id)
            .subquery()
        )
        
        stmt = (
            select(Contributor.full_name, subq.c.total)
            .join(subq)
            .order_by(subq.c.total.desc())
            .limit(1)
        )
        result = session.execute(stmt).first()
        print(f"Самый активный: {result.full_name} ({result.total} коммитов)")

# 3.2 Ранжировать участников по активности с window функциями
# SQL: SELECT c.full_name, SUM(co.commits_count) as total, RANK() OVER (ORDER BY SUM(co.commits_count) DESC) as rank FROM contributors c NATURAL JOIN contributions co GROUP BY c.user_id, c.full_name;
def task_3_2():
    with Session(engine) as session:
       ...

# 3.3 Найти проекты с активностью выше средней через CTE
# SQL: WITH avg_commits AS (SELECT AVG(commits_count) as avg_commits FROM contributions) SELECT r.name, c.commits_count FROM repositories r NATURAL JOIN contributions c WHERE c.commits_count > (SELECT avg_commits FROM avg_commits);
def task_3_3():
    with Session(engine) as session:
       ...

# 3.4 Обновить JSON метаданные - добавить новый тег
# SQL: UPDATE repositories SET repo_metadata = '{"language": "Python", "framework": "FastAPI", "tags": ["web", "api", "обновлено"]}' WHERE name = 'веб-шаблон';
def task_3_4():
    with Session(engine) as session:
      ...



if __name__ == "__main__":
    print("=== 1. Простые задания ===")
    task_1_1()
    task_1_2()
    task_1_3()
    task_1_4()
    task_1_5()
    
    print("\n=== 2. Средние задания ===")
    task_2_1()
    task_2_2()
    task_2_3()
    task_2_4()
    task_2_5()
    
    print("\n=== 3. Сложные задания ===")
    task_3_1()
    task_3_2()
    task_3_3()
    task_3_4()
    task_3_5()

```


