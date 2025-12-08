from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import get_db
from service import StudentService
from schemas import StudentResponse, StudentCreate
from sqlalchemy.orm import Session
# from auth import authenticate_user_with_role  # HTTP Basic Auth
from oauth import authenticate_oauth, create_access_token  # OAuth2 Bearer Token
from roles import Role, get_user_role, check_permission

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
    from roles import USERS
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"id": 1, "username": username, "role": user["role"]}
    return None

@router.post("/oauth/token")
def get_token(credentials: TokenRequest):
    # Проверка логина/пароля
    user = authenticate_user_for_token(credentials.username, credentials.password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Выдача токена
    access_token = create_access_token(data={"sub": user["id"], "username": user["username"]})
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
    # Проверяем права доступа
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN, Role.TEACHER])
    
    try:
        print(f"Пользователь {current_user} ({user_role}) создает студента: {student_data.name}")
        return service.create(student_data)
    except Exception as e:
        return {"error": f"Failed to create student: {str(e)}"}

@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 Auth
):
    # Проверяем права доступа (все роли могут просматривать)
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN, Role.TEACHER, Role.STUDENT])
    
    try:
        print(f"Пользователь {current_user} ({user_role}) запросил список студентов")
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)
):
    # Только admin может удалять
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN])
    
    try:
        result = service.delete(student_id)
        if not result:
            raise HTTPException(404, "Student not found")
        print(f"Пользователь {current_user} ({user_role}) удалил студента ID: {student_id}")
        return result
    except Exception as e:
        return {"error": f"Failed to delete student: {str(e)}"}