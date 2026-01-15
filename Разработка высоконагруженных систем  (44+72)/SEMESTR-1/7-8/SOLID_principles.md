# SOLID принципы в project-pattern

## ✅ **S - Single Responsibility Principle (Принцип единственной ответственности)**

**Каждый класс отвечает за одну задачу:**

```py
# StudentRepository - только работа с данными студентов
class StudentRepository:
    def get_all(self) -> list[Student]
    def create(self, student_data: dict) -> Student
    def update(self, name: str, data: dict) -> Student

# StudentService - только бизнес-логика студентов  
class StudentService:
    def get_all(self, year=None, group=None) -> list[Student]
    def search(self, query: str) -> list[Student]

# API Router - только HTTP обработка
@router.get("/")
def get_all(year: int | None = None):
    return service.get_all(year, group)
```

## ✅ **O - Open/Closed Principle (Принцип открытости/закрытости)**

**Можно расширять функциональность без изменения существующего кода:**

```py
# Можно добавить новые репозитории без изменения сервиса
class FileStudentRepository(StudentRepository):
    def get_all(self):
        # Чтение из файла
        pass

class DatabaseStudentRepository(StudentRepository):
    def get_all(self):
        # Чтение из БД
        pass
```

## ❌ **L - Liskov Substitution Principle (Принцип подстановки Лисков)**

**НЕ ПРИМЕНЕН** - нет наследования и полиморфизма в текущей реализации.

## ✅ **I - Interface Segregation Principle (Принцип разделения интерфейсов)**

**Разделены схемы для разных целей:**

```py
# Отдельные схемы для разных операций
class StudentCreate(BaseModel):    # Только для создания
    name: str
    group: str
    year: int

class StudentUpdate(BaseModel):    # Только для обновления
    name: str | None = None
    group: str | None = None

class StudentResponse(BaseModel):  # Только для ответа API
    name: str
    group: str
    year: int
    courses: list[int]
```

## ✅ **D - Dependency Inversion Principle (Принцип инверсии зависимостей)**

**Сервис зависит от репозитория (абстракции), а не от конкретной реализации:**

```py
# Сервис зависит от репозитория
class StudentService:
    def __init__(self):
        self.repository = StudentRepository()  # Зависимость от абстракции
    
    def get_all(self):
        return self.repository.get_all()  # Делегирование

# API зависит от сервиса
@router.get("/")
def get_all():
    return service.get_all()  # Зависимость от абстракции
```

## **Итог применения SOLID:**

- ✅ **S** - Разделение ответственности по слоям
- ✅ **O** - Возможность расширения без изменений
- ❌ **L** - Не применимо (нет наследования)
- ✅ **I** - Разделенные схемы для разных операций
- ✅ **D** - Зависимость от абстракций, а не реализаций

**4 из 5 принципов SOLID применены** в архитектуре проекта.

## Архитектурные слои проекта:

```
project-pattern/
├── main.py                    # Точка входа
├── api/                       # API слой (Представление)
│   ├── students.py           # REST эндпоинты студентов
│   ├── courses.py            # REST эндпоинты курсов
│   └── fixtures.py           # Управление тестовыми данными
├── services/                  # Уровень бизнес-логики
│   ├── student_service.py    # Бизнес-правила студентов
│   └── course_service.py     # Бизнес-правила курсов
├── repositories/              # Уровень доступа к данным
│   ├── student_repository.py # Операции с данными студентов
│   └── course_repository.py  # Операции с данными курсов
├── models/                    # Доменные модели
│   ├── student.py            # Модель Student
│   └── course.py             # Модель Course
├── schemas/                   # Схемы API
│   ├── student.py            # DTO студентов
│   └── course.py             # DTO курсов
└── fixtures_full.json        # Тестовые данные
```