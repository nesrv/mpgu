# oss_tracking_py313.py
from datetime import date
from sqlalchemy import create_engine, select, func, text, ForeignKey
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
engine = create_engine("postgresql://student:password@localhost:5435/students_db?client_encoding=utf8", echo=False)
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
        Repository(repo_id=101, name="веб-шаблон", description="Современный стартер для веб-приложений", stars=1200),
        Repository(repo_id=102, name="мл-инструменты", description="Утилиты машинного обучения для студентов", stars=870),
        Repository(repo_id=103, name="консоль-логгер", description="Простая библиотека для логирования", stars=340),
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


# Запросы
with Session(engine) as session:
    print("=== Участники и их вклад ===")
    stmt = (
        select(Contributor.username, Repository.name, Contribution.commits_count)
        .select_from(Contribution)
        .join(Contributor)
        .join(Repository)
    )
    # В SQLAlchemy 2.0+ join по FK работает автоматически, если связи объявлены.
    # Но у нас нет relationship — поэтому лучше явно:
    stmt = (
        select(Contributor.username, Repository.name, Contribution.commits_count)
        .select_from(Contribution)
        .join(Contributor, Contribution.user_id == Contributor.user_id)
        .join(Repository, Contribution.repo_id == Repository.repo_id)
    )
    for row in session.execute(stmt):
        print(f"{row.username} → {row.name}: {row.commits_count} коммитов")

    print("\n=== Топ-2 по коммитам ===")
    stmt = (
        select(Contributor.username, func.sum(Contribution.commits_count).label("total"))
        .join(Contributor, Contribution.user_id == Contributor.user_id)
        .group_by(Contributor.user_id)
        .order_by(func.sum(Contribution.commits_count).desc())
        .limit(2)
    )
    for row in session.execute(stmt):
        print(f"{row.username}: {row.total}")

    print("\n=== NATURAL JOIN через raw SQL ===")
    for row in session.execute(text("""
        SELECT username, name, commits_count
        FROM contributions
        NATURAL JOIN contributors
        NATURAL JOIN repositories
    """)):
        print(row)