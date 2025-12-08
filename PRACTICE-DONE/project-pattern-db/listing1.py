# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import create_tables
from api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
    yield

app = FastAPI(title="Student Management API", version="1.0.0", lifespan=lifespan)

app.include_router(router)

# api.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import get_db
from service import StudentService
from schemas import StudentResponse, StudentCreate
from sqlalchemy.orm import Session
from auth import authenticate_user  # HTTP Basic Auth
from oauth import authenticate_oauth, create_access_token  # OAuth2 Bearer Token

router = APIRouter()

# ========== DEPENDENCY INJECTION ==========
def get_service(db = Depends(get_db)):
    return StudentService(db)

# ========== OAUTH СЕРВЕР АВТОРИЗАЦИИ ==========

class TokenRequest(BaseModel):
    username: str
    password: str

def authenticate_user_for_token(username: str, password: str):
    """Проверка пользователя для выдачи токена"""
    # Заглушка - в реальности проверка в БД
    if username == "admin" and password == "password":
        return {"id": 1, "username": username}
    return None

@router.post("/oauth/token")
def get_token(credentials: TokenRequest):
    # Проверка логина/пароля
    user = authenticate_user_for_token(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Выдача токена
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/students/load-fixture")
def load_fixture(service = Depends(get_service)):
    """
    Загружает тестовые данные студентов из fixtures.json
    Доступен без аутентификации для удобства тестирования
    """
    try:
        service.load_fixture()
        return {"message": "Loaded students from fixture"}
    except Exception as e:
        return {"error": f"Failed to load fixture: {str(e)}"}

@router.post("/students/")
def create_student(
    student_data: StudentCreate,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 аутентификацию
):
   
    try:
        print(f"Пользователь {current_user} создает студента: {student_data.name}")  # Логирование
        return service.create(student_data)
    except Exception as e:
        return {"error": f"Failed to create student: {str(e)}"}

@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_user)  # Требуем Basic Auth
):
   
    try:
        print(f"Пользователь {current_user} запросил список студентов")  # Логирование
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

# oauth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
import secrets
import uuid

# ========== НАСТРОЙКА OAUTH2 ==========
# Создаем объект для Bearer Token (проще для Swagger)
oauth2_scheme = HTTPBearer()

# OAuth2 токен (в реальном проекте хранить в переменных окружения)
VALID_TOKEN = None  # Будет установлен при создании токена

# ========== ФУНКЦИЯ OAUTH2 АУТЕНТИФИКАЦИИ ==========
def authenticate_oauth(credentials = Depends(oauth2_scheme)):
    if VALID_TOKEN is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не создан",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем токен с защитой от timing attacks
    is_valid_token = secrets.compare_digest(
        credentials.credentials.encode("utf8"), VALID_TOKEN.encode("utf8")
    )
    
    if not is_valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return "oauth_user"

# ========== ФУНКЦИЯ СОЗДАНИЯ ПРОСТОГО ТОКЕНА ==========
def create_access_token(data: dict):
    """Создает простой UUID токен"""
    global VALID_TOKEN
    token = str(uuid.uuid4())
    VALID_TOKEN = token  # Сохраняем токен для проверки
    return token

# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# ========== НАСТРОЙКА BASIC AUTH ==========
# Создаем объект для HTTP Basic Auth
security = HTTPBasic()

# Учетные данные для доступа (в реальном проекте хранить в переменных окружения)
VALID_USERNAME = "admin"
VALID_PASSWORD = "secret123"

# ========== BASIC AUTH ФУНКЦИЯ ==========
def authenticate_user(credentials = Depends(security)):
   
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

# models.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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
from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str
    data: dict = {}

class StudentResponse(BaseModel):
    id: int
    name: str
    data: dict

# service.py
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from models import StudentModel, CourseModel, Base, engine
from schemas import StudentResponse, StudentCreate
import json

class StudentService:
    def __init__(self, db):
        self.db = db
    
    def load_fixture(self):
        # Удаляем и создаем таблицы заново
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        with open("fixtures.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Загружаем студентов как есть (с ID из фикстур)
        for student_data in data["students"]:
            student = StudentModel(**student_data)
            self.db.add(student)
        
        # Загружаем курсы
        for course_data in data["courses"]:
            course_id = course_data["id"]
            course_name = course_data["name"]
            
            enrolled_students = [e["student_id"] for e in data["enrollments"] if e["course_id"] == course_id]
            
            for student_id in enrolled_students:
                course = CourseModel(name=course_name, student_id=student_id)
                self.db.add(course)
        
        self.db.commit()
        
        # Сбрасываем последовательность чтобы новые студенты получали правильные ID  
        max_id = self.db.query(func.max(StudentModel.id)).scalar() or 0
        self.db.execute(func.setval('students_id_seq', max_id))
    
    def get_all(self):
        students = self.db.query(StudentModel).all()
        return [StudentResponse(
            id=s.id,
            name=s.name,
            data=s.data or {}
        ) for s in students]
    
    def create(self, student_data):
        # Не указываем ID - PostgreSQL автоматически присвоит следующий
        student = StudentModel(name=student_data.name, data=student_data.data or {})
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return StudentResponse(id=student.id, name=student.name, data=student.data or {})
