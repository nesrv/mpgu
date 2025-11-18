
```py
# main.py

# ========== НАСТРОЙКА ПРИЛОЖЕНИЯ ==========
# Управление жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Выполняется при запуске и остановке приложения"""
    # Код выполняется при запуске
    try:
        create_tables()  # Создаем таблицы в БД
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")    
    yield  # Приложение работает
    # Код выполняется при остановке (если нужно)
    # Здесь можно добавить очистку ресурсов


app = FastAPI(
    title="Student Management API",  # Название API
    version="1.0.0",  # Версия
    lifespan=lifespan  # Управление жизненным циклом
)

app.include_router(router)

# models.py
DATABASE_URL = "postgresql://student:password@localhost:5435/students_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(JSON, default={})
    courses = relationship("CourseModel", back_populates="student")

class CourseModel(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("StudentModel", back_populates="courses")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

# schemas.py
class StudentResponse(BaseModel):
    id: int
    name: str
    data: dict

# service.py
class StudentService:
    def __init__(self, db: Session):
        self.db = db
    
    def load_fixture(self):
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Load students
        for student_data in data["students"]:
            student = StudentModel(**student_data)
            self.db.merge(student)
        
        # Load courses with enrollments
        for course_data in data["courses"]:
            course_id = course_data["id"]
            course_name = course_data["name"]
            
            # Find students enrolled in this course
            enrolled_students = [e["student_id"] for e in data["enrollments"] if e["course_id"] == course_id]
            
            for student_id in enrolled_students:
                course = CourseModel(
                    name=course_name,
                    student_id=student_id
                )
                self.db.merge(course)
        
        self.db.commit()
    
    def get_all(self) -> List[StudentResponse]:
        students = self.db.query(StudentModel).all()
        return [StudentResponse(
            id=s.id,
            name=s.name,
            data=s.data or {}
        ) for s in students]

# api.py
router = APIRouter()

def get_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(db)

@router.post("/students/load-fixture")
def load_fixture(service: StudentService = Depends(get_service)):
    try:
        service.load_fixture()
        return {"message": "Loaded students from fixture"}
    except Exception as e:
        return {"error": f"Failed to load fixture: {str(e)}"}

@router.get("/students/")
def get_students(service: StudentService = Depends(get_service)):
    try:
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}


```

# Сделаем для эндпоинта @router.get("/students/") аутентификацию HTTP Basic Auth


```py
# auth.py - Модуль аутентификации для FastAPI приложения

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Создаем объект для HTTP Basic Auth
security = HTTPBasic()


VALID_USERNAME = "admin"
VALID_PASSWORD = "secret123"


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
  
    # Проверяем username с защитой от timing attacks
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), VALID_USERNAME.encode("utf8")
    )
    # Проверяем password с защитой от timing attacks
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), VALID_PASSWORD.encode("utf8")
    )
    
    # Если учетные данные неверны, возвращаем ошибку 401
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},  # Указываем тип аутентификации
        )
    
    return credentials.username


# api.py

from auth import authenticate_user 



@router.get("/students/")
def get_students(
    service: StudentService = Depends(get_service),
    current_user: str = Depends(authenticate_user)  # Требуем аутентификацию
):

    try:
        print(f"Пользователь {current_user} запросил список студентов")  # Логирование
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

```


### добавь @router.post("/") и логику для него

```py
#api.py

@router.post("/students/", response_model=StudentResponse)
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_user)  # Требуем аутентификацию
):
   
    try:
        print(f"Пользователь {current_user} создает студента: {student_data.name}")  # Логирование
        return service.create(student_data)
    except Exception as e:
        return {"error": f"Failed to create student: {str(e)}"}

# schemas.py

class StudentCreate(BaseModel):
    name: str
    data: dict = {}


# service.py
class StudentService:
    ...


     def create(self, student_data):
        student = StudentModel(name=student_data.name, data=student_data.data or {})
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return StudentResponse(id=student.id, name=student.name, data=student.data or {})


```

## Добавь OAuth для этого эндпоинта @router.post("/students/")

```py

# oauth.py - OAuth2 аутентификация для FastAPI приложения

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import secrets


# Создаем объект для OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# OAuth2 токен (в реальном проекте хранить в переменных окружения)
VALID_TOKEN = "secret-oauth-token"

# ========== ФУНКЦИЯ OAUTH2 АУТЕНТИФИКАЦИИ ==========
def authenticate_oauth(token = Depends(oauth2_scheme)):

    # Проверяем токен с защитой от timing attacks
    is_valid_token = secrets.compare_digest(
        token.encode("utf8"), VALID_TOKEN.encode("utf8")
    )
    
    if not is_valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return "oauth_user"


# api.py

from oauth import authenticate_oauth  # OAuth2 Bearer Token


@router.post("/students/")
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 аутентификацию
):
   
 ...

```


В Swagger UI для OAuth2 нужно ввести токен напрямую:

Вариант 1 - Простой (используйте токен напрямую):

В Swagger UI нажмите "Authorize" и введите:
Token : secret-oauth-token

Остальные поля оставьте пустыми

Вариант 1 Правильный 
Шаг 1 - Получить токен:
Найдите эндпоинт POST /token

Нажмите "Try it out"

Введите:

username: admin

password: secret123

Нажмите "Execute"

Скопируйте access_token из ответа

Шаг 2 - Авторизоваться:
Нажмите кнопку "Authorize" вверху страницы

В разделе OAuth2PasswordBearer введите:

username: admin

password: secret123

Нажмите "Authorize"

Или просто введите токен:
В поле авторизации можете сразу ввести: secret-oauth-token

Теперь эндпоинт POST /students/ будет работать с OAuth2 аутентификацией через Swagger