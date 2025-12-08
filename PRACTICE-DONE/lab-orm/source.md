# Практика: SQLAlchemy ORM с json

## Описание базы данных

```py
# oss_tracking_py313.py
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

# 1. Простые задания на sqlalchemy

1.1
1.2
1.3
1.4
1.5

# 2. Средние задания на sqlalchemy
2.1
2.2
2.3
2.4
2.5

# 3. Сложные задания на sqlalchemy
3.1
3.2
3.3
3.4
3.5