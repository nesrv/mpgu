# Задания для lab-orm\source.py
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
        stmt = select(Repository).where(Repository.stars > 500)
        for repo in session.execute(stmt).scalars():
            print(f"{repo.name}: {repo.stars} звезд")

# 1.3 Найти все вклады конкретного участника
# SQL: SELECT user_id, commits_count FROM contributions WHERE user_id = 1;
def task_1_3():
    with Session(engine) as session:
        stmt = select(Contribution).where(Contribution.user_id == 1)
        for contrib in session.execute(stmt).scalars():
            print(f"Участник {contrib.user_id}: {contrib.commits_count} коммитов")

# 1.4 Подсчитать общее количество участников
# SQL: SELECT COUNT(*) FROM contributors;
def task_1_4():
    with Session(engine) as session:
        stmt = select(func.count(Contributor.user_id))
        count = session.execute(stmt).scalar()
        print(f"Всего участников: {count}")

# 1.5 Найти репозиторий с максимальным количеством звезд
# SQL: SELECT name, stars FROM repositories ORDER BY stars DESC LIMIT 1;
def task_1_5():
    with Session(engine) as session:
        stmt = select(Repository).order_by(Repository.stars.desc()).limit(1)
        repo = session.execute(stmt).scalar()
        print(f"Топ репозиторий: {repo.name} ({repo.stars} звезд)")

# 2. Средние задания на sqlalchemy

# 2.1 Найти участников и их общее количество коммитов
# SQL: SELECT c.username, SUM(co.commits_count) as total FROM contributors c NATURAL JOIN contributions co GROUP BY c.user_id;
def task_2_1():
    with Session(engine) as session:
        stmt = (
            select(Contributor.username, func.sum(Contribution.commits_count).label("total"))
            .join(Contribution)
            .group_by(Contributor.user_id)
        )
        for row in session.execute(stmt):
            print(f"{row.username}: {row.total} коммитов")

# 2.2 Найти все Python проекты через JSON
# SQL: SELECT name FROM repositories WHERE repo_metadata->>'language' = 'Python';
def task_2_2():
    with Session(engine) as session:
        stmt = select(Repository.name).where(
            cast(Repository.repo_metadata['language'], String) == 'Python'
        )
        for name in session.scalars(stmt):
            print(f"Python проект: {name}")

# 2.3 Найти участников, работающих с FastAPI
# SQL: SELECT c.full_name, r.name FROM contributions co NATURAL JOIN contributors c NATURAL JOIN repositories r WHERE r.repo_metadata->>'framework' = 'FastAPI';
def task_2_3():
    with Session(engine) as session:
        stmt = (
            select(Contributor.full_name, Repository.name)
            .select_from(Contribution)
            .join(Contributor)
            .join(Repository)
            .where(cast(Repository.repo_metadata['framework'], String) == 'FastAPI')
        )
        for row in session.execute(stmt):
            print(f"{row.full_name} работает с {row.name}")

# 2.4 Подсчитать проекты по языкам программирования
# SQL: SELECT repo_metadata->>'language' as language, COUNT(*) as count FROM repositories GROUP BY repo_metadata->>'language';
def task_2_4():
    with Session(engine) as session:
        stmt = (
            select(
                cast(Repository.repo_metadata['language'], String).label('language'),
                func.count().label('count')
            )
            .group_by(cast(Repository.repo_metadata['language'], String))
        )
        for row in session.execute(stmt):
            print(f"{row.language}: {row.count} проектов")

# 2.5 Найти участников с активностью в последние 3 месяца
# SQL: SELECT DISTINCT c.full_name FROM contributors c NATURAL JOIN contributions co WHERE co.last_activity >= '2025-09-01';
def task_2_5():
    with Session(engine) as session:
        stmt = (
            select(Contributor.full_name)
            .join(Contribution)
            .where(Contribution.last_activity >= date(2025, 9, 1))
            .distinct()
        )
        for row in session.execute(stmt):
            print(f"Активный участник: {row.full_name}")

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
        stmt = (
            select(
                Contributor.full_name,
                func.sum(Contribution.commits_count).label('total'),
                func.rank().over(order_by=func.sum(Contribution.commits_count).desc()).label('rank')
            )
            .join(Contribution)
            .group_by(Contributor.user_id, Contributor.full_name)
        )
        for row in session.execute(stmt):
            print(f"#{row.rank} {row.full_name}: {row.total} коммитов")

# 3.3 Найти проекты с активностью выше средней через CTE
# SQL: WITH avg_commits AS (SELECT AVG(commits_count) as avg_commits FROM contributions) SELECT r.name, c.commits_count FROM repositories r NATURAL JOIN contributions c WHERE c.commits_count > (SELECT avg_commits FROM avg_commits);
def task_3_3():
    with Session(engine) as session:
        avg_commits = (
            select(func.avg(Contribution.commits_count).label('avg_commits'))
            .cte('avg_commits')
        )
        
        stmt = (
            select(Repository.name, Contribution.commits_count)
            .select_from(Contribution)
            .join(Repository)
            .where(Contribution.commits_count > select(avg_commits.c.avg_commits))
        )
        for row in session.execute(stmt):
            print(f"{row.name}: {row.commits_count} коммитов (выше среднего)")

# 3.4 Обновить JSON метаданные - добавить новый тег
# SQL: UPDATE repositories SET repo_metadata = '{"language": "Python", "framework": "FastAPI", "tags": ["web", "api", "обновлено"]}' WHERE name = 'веб-шаблон';
def task_3_4():
    with Session(engine) as session:
        # Простое обновление JSON поля
        new_metadata = {
            "language": "Python",
            "framework": "FastAPI", 
            "tags": ["web", "api", "обновлено"]
        }
        stmt = (
            update(Repository)
            .where(Repository.name == 'веб-шаблон')
            .values(repo_metadata=new_metadata)
        )
        session.execute(stmt)
        session.commit()
        print("Обновлены метаданные проекта 'веб-шаблон'")

# 3.5 Сложный запрос с множественными JOIN и агрегацией
# SQL: SELECT r.name, r.repo_metadata->>'language' as language, COUNT(c.user_id) as contributors_count, SUM(c.commits_count) as total_commits, AVG(c.commits_count) as avg_commits FROM repositories r NATURAL JOIN contributions c GROUP BY r.repo_id, r.name, r.repo_metadata->>'language' HAVING COUNT(c.user_id) > 1 ORDER BY SUM(c.commits_count) DESC;
def task_3_5():
    with Session(engine) as session:
        stmt = (
            select(
                Repository.name,
                cast(Repository.repo_metadata['language'], String).label('language'),
                func.count(Contribution.user_id).label('contributors_count'),
                func.sum(Contribution.commits_count).label('total_commits'),
                func.avg(Contribution.commits_count).label('avg_commits')
            )
            .join(Contribution)
            .group_by(Repository.repo_id, Repository.name, cast(Repository.repo_metadata['language'], String))
            .having(func.count(Contribution.user_id) > 1)
            .order_by(func.sum(Contribution.commits_count).desc())
        )
        for row in session.execute(stmt):
            print(f"{row.name} ({row.language}): {row.contributors_count} участников, "
                  f"{row.total_commits} коммитов, среднее: {row.avg_commits:.1f}")

if __name__ == "__main__":
    print("=== 1. Простые задания ===")
    # task_1_1()
    # task_1_2()
    # task_1_3()
    # task_1_4()
    # task_1_5()
    
    print("\n=== 2. Средние задания ===")
    # task_2_1()
    task_2_2()
    # task_2_3()
    # task_2_4()
    # task_2_5()
    
    # print("\n=== 3. Сложные задания ===")
    # task_3_1()
    # task_3_2()
    # task_3_3()
    # task_3_4()
    # task_3_5()