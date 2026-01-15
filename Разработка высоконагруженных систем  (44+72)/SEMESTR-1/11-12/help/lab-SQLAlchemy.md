# Лабораторная работа: FastAPI + Работа с бд

## 🎯 Цель работы

Изучить работу FastAPI с СУБД PostgreSQL c помощью SQLAlchemy

# SQLAlchemy ШПАРГАЛКА для студентов

```py
# ============= ОСНОВНЫЕ ОПЕРАЦИИ =============

# CREATE - Создать студента
student = StudentModel(name="Иван", group="ИВТ-21", year=2, courses=[1,2])
db.add(student)
db.commit()

# READ - Получить студентов
db.query(StudentModel).all()                           # Все студенты
db.query(StudentModel).first()                         # Первый студент
db.query(StudentModel).filter(StudentModel.name == "Иван").first()  # По имени

# UPDATE - Обновить студента
student = db.query(StudentModel).filter(StudentModel.name == "Иван").first()
student.year = 3
db.commit()

# DELETE - Удалить студента
student = db.query(StudentModel).filter(StudentModel.name == "Иван").first()
db.delete(student)
db.commit()

# ============= ФИЛЬТРАЦИЯ =============

# По году
db.query(StudentModel).filter(StudentModel.year == 2)

# По группе
db.query(StudentModel).filter(StudentModel.group == "ИВТ-21")

# Несколько условий
db.query(StudentModel).filter(StudentModel.year == 2, StudentModel.group == "ИВТ-21")

# Поиск по имени (без учета регистра)
db.query(StudentModel).filter(StudentModel.name.ilike("%иван%"))

# Студенты на курсе (JSON поле)
db.query(StudentModel).filter(StudentModel.courses.contains([1]))

# ============= ПОЛЕЗНЫЕ КОМАНДЫ =============

# Подсчет
db.query(StudentModel).count()

# Сортировка
db.query(StudentModel).order_by(StudentModel.name)

# Лимит
db.query(StudentModel).limit(10)

# Обновить после изменений
db.refresh(student)

# ============= РАБОТА С JSON (курсы) =============

# Добавить курс
courses = student.courses or []
courses.append(course_id)
student.courses = courses
db.commit()

# Удалить курс
courses = student.courses or []
courses.remove(course_id)
student.courses = courses
db.commit()

```


# Самостоятельная работа:
## Сделать логику для указанных эндпоинтов в сервисном слое c помощью SQLAlchemy


```py
@app.get("/courses")
def get_all() -> list[Course]:
    ...

@app.get("/courses/{name}")
def get_one(name: str) -> Course:
    ...

@router.get("/{course_id}")
def get_one(course_id: int) -> Course:
    ...


@app.post("/course")
def create(course: Course) -> Course:
   ...

@app.patch("/students/{name}")
def update(name: str, update: StudentUpdate) -> Student:
   ...

@router.patch("/{course_id}")
def update(course_id: int, data: CourseUpdate) -> Course:
    ...

@router.delete("/{course_id}")
def delete(course_id: int):
   ...

@router.get("/{course_id}/students")
def get_students(course_id: int) -> list[Student]:
   ....


@router.post("/{name}/enroll/{course_id}")
def enroll(name: str, course_id: int):
    ...

@router.delete("/{name}/unenroll/{course_id}")
def unenroll(name: str, course_id: int):
   ...

@router.get("/search")
def search(query: str = Query(...)) -> list[Student]:
   ...

#GET /students?year=2&group=ИВТ-21
@router.get("/")
def get_all(year: int | None = None, group: str | None = None) -> list[Student]:
  ...

@router.post("/load-all")
def load_all_fixtures():
    ...
```


