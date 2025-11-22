# Продвинутая работа с базами данных

**Лекция 11-12**  
Дисциплина: Проектирование и разработка высоконагруженных сервисов  
МПГУ, 4 курс бакалавриата

---

## Слайд 1: OLAP и OLTP

### OLTP (Online Transaction Processing)
- **Назначение**: обработка транзакций в реальном времени
- **Операции**: INSERT, UPDATE, DELETE
- **Характеристики**: много коротких запросов, высокая скорость записи
- **Примеры**: банковские операции, интернет-магазины, CRM-системы

### OLAP (Online Analytical Processing)
- **Назначение**: аналитическая обработка данных
- **Операции**: SELECT с агрегацией (SUM, AVG, GROUP BY)
- **Характеристики**: сложные запросы на чтение больших объемов данных
- **Примеры**: отчеты, аналитика продаж, BI-системы

---

## Слайд 2: СУБД для OLAP и OLTP

### OLTP СУБД
- **PostgreSQL** — универсальная реляционная СУБД
- **MySQL/MariaDB** — популярная для веб-приложений
- **Oracle Database** — enterprise решение
- **MS SQL Server** — корпоративная СУБД от Microsoft

### OLAP СУБД
- **ClickHouse** — колоночная СУБД для аналитики
- **Apache Druid** — для real-time аналитики
- **Greenplum** — MPP база данных
- **Vertica** — колоночное хранилище

---

## Слайд 3: OLAP и OLTP на российском рынке

### Российские решения OLTP
- **PostgresPro** — российская версия PostgreSQL
- **Tarantool** — in-memory СУБД
- **YDB** — распределенная СУБД от Yandex

### Российские решения OLAP
- **ClickHouse** — разработка Yandex (open source)
- **Greenplum** — поддержка Arenadata
- **1C:Enterprise** — для бизнес-аналитики

### Импортозамещение
- Переход с Oracle на PostgresPro
- Замена MS SQL Server на отечественные решения

---

## Слайд 4: PostgreSQL как OLAP или OLTP

### PostgreSQL для OLTP
✅ **Сильные стороны**:
- ACID-транзакции
- Поддержка индексов (B-tree, Hash, GiST, GIN)
- Высокая надежность

### PostgreSQL для OLAP
⚠️ **Ограничения**:
- Строковое хранение (медленнее колоночного)
- Не оптимизирован для больших аналитических запросов

💡 **Решение**: использовать расширения
- **Citus** — для горизонтального масштабирования
- **TimescaleDB** — для временных рядов
- **pg_analytics** — колоночное хранение

---

## Слайд 5: Хранилища и витрины данных

### Data Warehouse (Хранилище данных)
- Централизованное хранилище для всех данных компании
- Интеграция данных из разных источников
- Исторические данные для анализа
- **Зарубежные**: Snowflake, Amazon Redshift, Google BigQuery
- **Российские**: Yandex DataLens + ClickHouse, Arenadata DB, Postgres Pro Enterprise

### Data Mart (Витрина данных)
- Подмножество хранилища для конкретного отдела
- Оптимизирована под конкретные задачи
- Быстрый доступ к нужным данным
- **Примеры**: витрина продаж (Яндекс.Маркет), витрина аналитики (Сбер)

### ETL процесс
- **Extract** — извлечение данных из источников
- **Transform** — преобразование и очистка
- **Load** — загрузка в хранилище
- **Российские инструменты**: Apache NiFi, Loginom, DataGrip

---

## Слайд 6: Data Mart и ETL — детальный разбор

### Когда нужны Data Mart?
**Проблема**: хранилище содержит терабайты данных, запросы медленные  
**Решение**: создать витрину для конкретного отдела

**Примеры использования**:
- **Отдел продаж**: витрина с данными о клиентах, заказах, выручке за последний год
- **Маркетинг**: витрина с метриками кампаний, конверсиями, ROI
- **Финансы**: витрина с транзакциями, балансами, отчетностью
- **HR**: витрина с данными о сотрудниках, зарплатах, KPI

### ETL процесс — зачем и как?

**Зачем нужен ETL?**
- Данные разбросаны по разным системам (CRM, ERP, логи, Excel)
- Форматы данных различаются
- Нужна очистка от дубликатов и ошибок
- Требуется агрегация и расчет метрик

**Этапы ETL**:

1. **Extract (Извлечение)**
   - Из PostgreSQL (OLTP база)
   - Из API внешних сервисов
   - Из файлов (CSV, JSON, XML)
   - Из логов приложений

2. **Transform (Преобразование)**
   - Очистка: удаление дубликатов, исправление ошибок
   - Нормализация: приведение к единому формату
   - Обогащение: добавление справочных данных
   - Агрегация: расчет сумм, средних, группировок

3. **Load (Загрузка)**
   - В ClickHouse (для аналитики)
   - В витрины данных (Data Mart)
   - Инкрементальная или полная загрузка

**Пример**: Интернет-магазин
- **Extract**: заказы из PostgreSQL, клики из логов, платежи из банка
- **Transform**: объединение по ID клиента, расчет LTV, сегментация
- **Load**: в витрину маркетинга для анализа эффективности рекламы

---

## Слайд 7: SQL против ORM

### Чистый SQL
✅ **Преимущества**:
- Полный контроль над запросами
- Максимальная производительность
- Использование специфичных функций СУБД

❌ **Недостатки**:
- Больше кода
- Риск SQL-инъекций
- Сложность поддержки

### ORM (Object-Relational Mapping)
✅ **Преимущества**:
- Работа с объектами вместо SQL
- Защита от SQL-инъекций
- Быстрая разработка

❌ **Недостатки**:
- Overhead производительности
- Сложные запросы могут быть неэффективными
- Абстракция скрывает детали

---

## Слайд 7: SQL + PL/pgSQL

### PL/pgSQL — процедурный язык PostgreSQL

```sql
-- Создание функции
CREATE OR REPLACE FUNCTION get_student_count()
RETURNS INTEGER AS $$
DECLARE
    student_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO student_count FROM students;
    RETURN student_count;
END;
$$ LANGUAGE plpgsql;

-- Использование
SELECT get_student_count();
```

**Применение**:
- Хранимые процедуры
- Триггеры
- Сложная бизнес-логика на уровне БД

---

## Слайд 8: SQL + PL/pgSQL (продолжение)

### Пример триггера

```sql
-- Функция для триггера
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера
CREATE TRIGGER student_update_trigger
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE FUNCTION update_modified_timestamp();
```

**Преимущества**:
- Логика выполняется на стороне БД
- Гарантия целостности данных
- Снижение нагрузки на приложение

---

## Слайд 9: Современные ORM

| Язык | ORM | Особенности |
|------|-----|-------------|
| **Python** | SQLAlchemy | Гибкий, мощный, поддержка сырого SQL |
| **Python** | Django ORM | Простой, интегрирован с Django |
| **JavaScript** | Prisma | Типобезопасность, автогенерация |
| **JavaScript** | TypeORM | Декораторы, поддержка TypeScript |
| **Java** | Hibernate | Стандарт JPA, кэширование |
| **C#** | Entity Framework | Интеграция с .NET, LINQ |
| **Ruby** | ActiveRecord | Convention over configuration |
| **Go** | GORM | Простой API, миграции |
| **PHP** | Eloquent | Часть Laravel, выразительный синтаксис |

---

## Слайд 10: Сравнение SQLAlchemy и Django ORM

### SQLAlchemy
- **Тип**: независимая библиотека
- **Подход**: Data Mapper pattern
- **Гибкость**: высокая, поддержка сырого SQL
- **Сложность**: выше, больше контроля
- **Использование**: любые Python-проекты

### Django ORM
- **Тип**: часть Django framework
- **Подход**: Active Record pattern
- **Гибкость**: средняя, ориентирован на простоту
- **Сложность**: ниже, быстрый старт
- **Использование**: Django-проекты

---

## Слайд 11: Синтаксис — Определение моделей

| SQLAlchemy | Django ORM |
|------------|------------|
| `from sqlalchemy import Column, Integer, String`<br>`from sqlalchemy.ext.declarative import declarative_base`<br><br>`Base = declarative_base()`<br><br>`class Student(Base):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`__tablename__ = 'students'`<br>&nbsp;&nbsp;&nbsp;&nbsp;`id = Column(Integer, primary_key=True)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name = Column(String(100))`<br>&nbsp;&nbsp;&nbsp;&nbsp;`email = Column(String(100), unique=True)` | `from django.db import models`<br><br>`class Student(models.Model):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name = models.CharField(max_length=100)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`email = models.EmailField(unique=True)`<br><br>&nbsp;&nbsp;&nbsp;&nbsp;`class Meta:`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`db_table = 'students'` |

---

## Слайд 12: Синтаксис — Создание записей

| SQLAlchemy | Django ORM |
|------------|------------|
| `from sqlalchemy.orm import Session`<br><br>`session = Session(engine)`<br>`student = Student(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name="Иван",`<br>&nbsp;&nbsp;&nbsp;&nbsp;`email="ivan@example.com"`<br>`)`<br>`session.add(student)`<br>`session.commit()` | `student = Student.objects.create(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name="Иван",`<br>&nbsp;&nbsp;&nbsp;&nbsp;`email="ivan@example.com"`<br>`)`<br><br>✅ Автоматический commit |

---

## Слайд 13: Синтаксис — Чтение данных

| SQLAlchemy | Django ORM |
|------------|------------|
| **Все записи:**<br>`students = session.query(Student).all()`<br><br>**Фильтрация:**<br>`student = session.query(Student).filter(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Student.email == "ivan@example.com"`<br>`).first()`<br><br>**С условиями:**<br>`students = session.query(Student).filter(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Student.name.like("%Иван%")`<br>`).all()` | **Все записи:**<br>`students = Student.objects.all()`<br><br>**Фильтрация:**<br>`student = Student.objects.filter(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`email="ivan@example.com"`<br>`).first()`<br><br>**С условиями:**<br>`students = Student.objects.filter(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`name__icontains="Иван"`<br>`)` |

---

## Слайд 14: Синтаксис — Обновление и удаление

| SQLAlchemy | Django ORM |
|------------|------------|
| **Обновление:**<br>`student = session.query(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.filter_by(id=1).first()`<br>`student.name = "Петр"`<br>`session.commit()`<br><br>**Удаление:**<br>`session.query(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.filter_by(id=1).delete()`<br>`session.commit()` | **Обновление (вариант 1):**<br>`Student.objects.filter(id=1)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.update(name="Петр")`<br><br>**Обновление (вариант 2):**<br>`student = Student.objects.get(id=1)`<br>`student.name = "Петр"`<br>`student.save()`<br><br>**Удаление:**<br>`Student.objects.filter(id=1).delete()` |

---

## Слайд 15: Синтаксис — Связи (Relationships)

| SQLAlchemy | Django ORM |
|------------|------------|
| `from sqlalchemy import ForeignKey`<br>`from sqlalchemy.orm import relationship`<br><br>`class Course(Base):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`__tablename__ = 'courses'`<br>&nbsp;&nbsp;&nbsp;&nbsp;`id = Column(Integer, primary_key=True)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`title = Column(String(200))`<br>&nbsp;&nbsp;&nbsp;&nbsp;`students = relationship(`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`"Student", back_populates="course"`<br>&nbsp;&nbsp;&nbsp;&nbsp;`)`<br><br>`class Student(Base):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`course_id = Column(Integer,`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`ForeignKey('courses.id'))`<br>&nbsp;&nbsp;&nbsp;&nbsp;`course = relationship(`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`"Course", back_populates="students"`<br>&nbsp;&nbsp;&nbsp;&nbsp;`)` | `class Course(models.Model):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`title = models.CharField(max_length=200)`<br><br>`class Student(models.Model):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`course = models.ForeignKey(`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`Course,`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`on_delete=models.CASCADE,`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`related_name='students'`<br>&nbsp;&nbsp;&nbsp;&nbsp;`)` |

---

## Слайд 16: Синтаксис — Агрегация и группировка

| SQLAlchemy | Django ORM |
|------------|------------|
| `from sqlalchemy import func`<br><br>**Подсчет:**<br>`count = session.query(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`func.count(Student.id)`<br>`).scalar()`<br><br>**Группировка:**<br>`results = session.query(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`Student.course_id,`<br>&nbsp;&nbsp;&nbsp;&nbsp;`func.count(Student.id)`<br>`).group_by(Student.course_id).all()` | `from django.db.models import Count`<br><br>**Подсчет:**<br>`count = Student.objects.count()`<br><br><br>**Группировка:**<br>`results = Student.objects`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.values('course_id')`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.annotate(student_count=Count('id'))` |

---

## Слайд 17: Синтаксис — JOIN и подгрузка связей

| SQLAlchemy | Django ORM |
|------------|------------|
| **JOIN:**<br>`results = session.query(Student, Course)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.join(Course)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.filter(Course.title == "Python")`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.all()`<br><br>**Eager Loading (N+1 problem):**<br>`from sqlalchemy.orm import joinedload`<br><br>`students = session.query(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.options(joinedload(Student.course))`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.all()`<br><br>✅ Загрузка связей одним запросом | **JOIN:**<br>`results = Student.objects`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.select_related('course')`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.filter(course__title="Python")`<br><br><br>**Eager Loading (N+1 problem):**<br>`# select_related - ForeignKey, OneToOne`<br>`students = Student.objects`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.select_related('course')`<br><br>`# prefetch_related - ManyToMany`<br>`courses = Course.objects`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.prefetch_related('students')`<br><br>✅ Автоматическая оптимизация |

---

## Слайд 18: Синтаксис — Raw SQL и транзакции

| SQLAlchemy | Django ORM |
|------------|------------|
| **Raw SQL:**<br>`from sqlalchemy import text`<br><br>`result = session.execute(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`text("SELECT * FROM students WHERE id = :id"),`<br>&nbsp;&nbsp;&nbsp;&nbsp;`{"id": 1}`<br>`).fetchall()`<br><br>**Транзакции:**<br>`from sqlalchemy import create_engine`<br>`from sqlalchemy.orm import sessionmaker`<br><br>`try:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`session.add(student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`session.commit()`<br>`except:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`session.rollback()`<br>`finally:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`session.close()` | **Raw SQL:**<br>`from django.db import connection`<br><br>`with connection.cursor() as cursor:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`cursor.execute(`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`"SELECT * FROM students WHERE id = %s",`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`[1]`<br>&nbsp;&nbsp;&nbsp;&nbsp;`)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`result = cursor.fetchall()`<br><br>**Транзакции:**<br>`from django.db import transaction`<br><br>`with transaction.atomic():`<br>&nbsp;&nbsp;&nbsp;&nbsp;`student.save()`<br>&nbsp;&nbsp;&nbsp;&nbsp;`course.save()`<br><br>✅ Автоматический rollback |

---

## Слайд 19: SQLAlchemy 1.x vs 2.x — Основные изменения

### Ключевые отличия SQLAlchemy 2.0

| Аспект | SQLAlchemy 1.x | SQLAlchemy 2.x |
|--------|----------------|----------------|
| **Query API** | `session.query(Student)` | `session.execute(select(Student))` |
| **Стиль** | ORM-стиль (legacy) | SQL Expression стиль |
| **Типизация** | Слабая | Сильная (type hints) |
| **Async** | Нет | Полная поддержка |
| **Session** | `sessionmaker()` | `async_sessionmaker()` |
| **Производительность** | Хорошая | Лучше на 20-30% |

### Почему переходить на 2.x?
✅ Современный синтаксис  
✅ Поддержка async/await  
✅ Лучшая типизация для IDE  
✅ Более предсказуемое поведение  
✅ Активная поддержка и обновления

---

## Слайд 20: SQLAlchemy 1.x vs 2.x — Сравнение синтаксиса

| SQLAlchemy 1.x | SQLAlchemy 2.x |
|----------------|----------------|
| **Выборка всех записей:**<br>`students = session.query(Student).all()` | `from sqlalchemy import select`<br><br>`stmt = select(Student)`<br>`result = session.execute(stmt)`<br>`students = result.scalars().all()` |
| **Фильтрация:**<br>`student = session.query(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.filter(Student.id == 1)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.first()` | `stmt = select(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.where(Student.id == 1)`<br>`result = session.execute(stmt)`<br>`student = result.scalar_one_or_none()` |
| **JOIN:**<br>`results = session.query(Student, Course)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.join(Course)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.all()` | `stmt = select(Student, Course)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`.join(Course)`<br>`results = session.execute(stmt).all()` |
| **Агрегация:**<br>`from sqlalchemy import func`<br><br>`count = session.query(`<br>&nbsp;&nbsp;&nbsp;&nbsp;`func.count(Student.id)`<br>`).scalar()` | `from sqlalchemy import func, select`<br><br>`stmt = select(func.count(Student.id))`<br>`count = session.execute(stmt).scalar()` |
| **Async поддержка:**<br>❌ Не поддерживается | `from sqlalchemy.ext.asyncio import AsyncSession`<br><br>`async with AsyncSession(engine) as session:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`stmt = select(Student)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`result = await session.execute(stmt)`<br>&nbsp;&nbsp;&nbsp;&nbsp;`students = result.scalars().all()` |

**Важно**: SQLAlchemy 1.4 поддерживает оба стиля (переходная версия)

---




## Заключение

### Выбор подхода зависит от задачи:
- **Чистый SQL** — для максимальной производительности
- **PL/pgSQL** — для сложной логики на уровне БД
- **ORM** — для быстрой разработки и безопасности

### Рекомендации:
1. Используйте ORM для типовых операций
2. Переходите на SQL для сложных запросов
3. Профилируйте запросы и оптимизируйте узкие места
4. Изучайте возможности вашей СУБД

**Вопросы?**





