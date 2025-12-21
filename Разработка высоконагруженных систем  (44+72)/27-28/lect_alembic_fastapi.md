# Alembic для FastAPI
## Миграции баз данных в высоконагруженных системах

---

## Слайд 1: Введение в Alembic

**Alembic** — инструмент миграций БД для SQLAlchemy

**Основные возможности:**
- Версионирование схемы БД
- Автогенерация миграций
- Откат изменений
- Поддержка множества СУБД

**Зачем нужен в FastAPI?**
- Управление эволюцией схемы
- Синхронизация между окружениями
- История изменений БД

---

## Слайд 2: Установка и настройка

```bash
pip install alembic
pip install sqlalchemy
pip install asyncpg  # для PostgreSQL
```

**Инициализация проекта:**
```bash
alembic init alembic
```

**Структура проекта:**
```
project/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
└── app/
```

---

## Слайд 3: Конфигурация alembic.ini

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

**Важно:** Не храните пароли в конфиге!

---

## Слайд 4: Динамическая конфигурация

**alembic/env.py:**
```python
from app.config import settings
from app.models import Base

config = context.config
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
target_metadata = Base.metadata
```

**Использование переменных окружения:**
```python
import os
DATABASE_URL = os.getenv('DATABASE_URL')
```

---

## Слайд 5: Модели SQLAlchemy

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## Слайд 6: Создание первой миграции

```bash
alembic revision --autogenerate -m "create users table"
```

**Результат:**
```
alembic/versions/abc123_create_users_table.py
```

**Содержимое:**
```python
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
```

---

## Слайд 7: Применение миграций

```bash
# Применить все миграции
alembic upgrade head

# Применить конкретную версию
alembic upgrade abc123

# Откатить одну миграцию
alembic downgrade -1

# Откатить все
alembic downgrade base
```

---

## Слайд 8: История миграций

```bash
# Текущая версия
alembic current

# История всех миграций
alembic history

# Подробная история
alembic history --verbose
```

**Вывод:**
```
abc123 -> def456 (head), create users table
<base> -> abc123, initial migration
```

---

## Слайд 9: Ручные миграции

```bash
alembic revision -m "add index on email"
```

```python
def upgrade():
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade():
    op.drop_index('ix_users_email', 'users')
```

**Когда использовать:**
- Сложные изменения данных
- Специфичные для СУБД операции
- Миграция данных

---

## Слайд 10: Операции с таблицами

```python
# Создание таблицы
op.create_table('posts',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('title', sa.String(200), nullable=False)
)

# Удаление таблицы
op.drop_table('posts')

# Переименование таблицы
op.rename_table('posts', 'articles')
```

---

## Слайд 11: Операции с колонками

```python
# Добавление колонки
op.add_column('users', 
    sa.Column('phone', sa.String(20), nullable=True))

# Удаление колонки
op.drop_column('users', 'phone')

# Изменение типа
op.alter_column('users', 'phone',
    type_=sa.String(30))

# Переименование
op.alter_column('users', 'phone',
    new_column_name='phone_number')
```

---

## Слайд 12: Индексы и ограничения

```python
# Создание индекса
op.create_index('ix_users_email', 'users', ['email'])

# Уникальный индекс
op.create_index('ix_users_username', 'users', ['username'], 
    unique=True)

# Составной индекс
op.create_index('ix_posts_user_created', 'posts', 
    ['user_id', 'created_at'])

# Удаление индекса
op.drop_index('ix_users_email')
```

---

## Слайд 13: Foreign Keys

```python
# Добавление FK
op.create_foreign_key(
    'fk_posts_user_id',
    'posts', 'users',
    ['user_id'], ['id'],
    ondelete='CASCADE'
)

# Удаление FK
op.drop_constraint('fk_posts_user_id', 'posts', 
    type_='foreignkey')
```

---

## Слайд 14: Миграция данных

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Добавляем колонку
    op.add_column('users', sa.Column('status', sa.String(20)))
    
    # Заполняем данные
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE users SET status = 'active'")
    )
    
    # Делаем NOT NULL
    op.alter_column('users', 'status', nullable=False)
```

---

## Слайд 15: Batch операции

```python
with op.batch_alter_table('users') as batch_op:
    batch_op.add_column(sa.Column('age', sa.Integer()))
    batch_op.create_index('ix_users_age', ['age'])
    batch_op.alter_column('email', nullable=False)
```

**Преимущества:**
- Одна транзакция
- Меньше блокировок
- Быстрее для SQLite

---

## Слайд 16: Интеграция с FastAPI

```python
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@localhost/db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Слайд 17: Async поддержка

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
```

---

## Слайд 18: Async миграции

**alembic/env.py:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations_online():
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url")
    )
    
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

asyncio.run(run_migrations_online())
```

---

## Слайд 19: Множественные базы данных

```python
# alembic.ini
[alembic:main]
sqlalchemy.url = postgresql://localhost/main_db

[alembic:analytics]
sqlalchemy.url = postgresql://localhost/analytics_db
```

```bash
alembic -n analytics upgrade head
alembic -n main upgrade head
```

---

## Слайд 20: Ветвление миграций

```bash
# Создание ветки
alembic revision -m "feature branch" --head=abc123

# Слияние веток
alembic merge -m "merge branches" head1 head2
```

**Граф миграций:**
```
    abc123
    /    \
def456  ghi789
    \    /
    jkl012
```

---

## Слайд 21: Тестирование миграций

```python
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    return config

def test_upgrade_downgrade(alembic_config):
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")
```

---

## Слайд 22: CI/CD интеграция

```yaml
# .github/workflows/migrations.yml
name: Database Migrations

on: [push]

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run migrations
        run: |
          pip install alembic
          alembic upgrade head
      - name: Test rollback
        run: alembic downgrade -1
```

---

## Слайд 23: Стратегии развертывания

**Blue-Green Deployment:**
1. Обратно совместимые миграции
2. Развертывание новой версии
3. Переключение трафика
4. Удаление старых колонок

**Пример:**
```python
# Шаг 1: Добавить новую колонку
op.add_column('users', sa.Column('full_name', sa.String()))

# Шаг 2: Заполнить данные
# Шаг 3: Удалить старые колонки (позже)
```

---

## Слайд 24: Обработка ошибок

```python
def upgrade():
    try:
        op.add_column('users', sa.Column('email', sa.String()))
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('email')
```

**Best practices:**
- Всегда тестируйте downgrade
- Делайте бэкапы
- Используйте транзакции

---

## Слайд 25: Производительность миграций

**Оптимизация:**
```python
# Плохо: построчная обработка
for row in connection.execute(sa.text("SELECT * FROM users")):
    connection.execute(sa.text(f"UPDATE users SET status='active' WHERE id={row.id}"))

# Хорошо: массовое обновление
connection.execute(sa.text("UPDATE users SET status='active'"))
```

**Индексы:**
- Создавайте CONCURRENTLY (PostgreSQL)
- Удаляйте неиспользуемые индексы

---

## Слайд 26: Мониторинг миграций

```python
import logging
from datetime import datetime

logger = logging.getLogger('alembic.runtime.migration')

def upgrade():
    start = datetime.now()
    logger.info("Starting migration")
    
    op.create_table('users', ...)
    
    duration = (datetime.now() - start).total_seconds()
    logger.info(f"Migration completed in {duration}s")
```

---

## Слайд 27: Безопасность миграций

**Checklist:**
- ✅ Не храните пароли в коде
- ✅ Используйте переменные окружения
- ✅ Ограничьте права пользователя БД
- ✅ Логируйте все изменения
- ✅ Делайте бэкапы перед миграцией

```python
# Безопасное подключение
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set")
```

---

## Слайд 28: Частые ошибки

**1. Забыли импортировать модели:**
```python
# env.py
from app.models import User, Post  # Важно!
target_metadata = Base.metadata
```

**2. Конфликты миграций:**
```bash
alembic merge -m "resolve conflict" head1 head2
```

**3. Несовместимые изменения:**
- Всегда делайте обратно совместимые миграции
- Разбивайте на несколько этапов

---

## Слайд 29: Best Practices

1. **Именование миграций:** используйте понятные имена
2. **Атомарность:** одна миграция = одна логическая задача
3. **Тестирование:** проверяйте upgrade и downgrade
4. **Документация:** комментируйте сложные миграции
5. **Версионирование:** храните миграции в Git
6. **Автоматизация:** интегрируйте в CI/CD
7. **Мониторинг:** логируйте выполнение
8. **Бэкапы:** всегда делайте перед миграцией

---

## Слайд 30: Полезные ресурсы

**Документация:**
- https://alembic.sqlalchemy.org/
- https://docs.sqlalchemy.org/
- https://fastapi.tiangolo.com/

**Команды для справки:**
```bash
alembic --help
alembic revision --help
alembic upgrade --help
```

**Шпаргалка:**
- `alembic init` - инициализация
- `alembic revision --autogenerate -m "msg"` - создать миграцию
- `alembic upgrade head` - применить все
- `alembic downgrade -1` - откатить одну
- `alembic current` - текущая версия
- `alembic history` - история

---

## Спасибо за внимание!

**Вопросы?**
