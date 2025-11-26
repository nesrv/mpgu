# Лабораторная работа: Способа авторизации в FastAPI 

## 🎯 Цель работы

Изучить создание и управления ролями




## 🎯 Самостоятельное задание: Роли пользователей

**Задача:** Добавить систему ролей в Basic Auth.

**Требования:**

1. Создать 3 роли: `admin`, `teacher`, `student`
2. Только `admin` может удалять студентов
3. `admin` и `teacher` могут создавать студентов
4. Все роли могут просматривать студентов
5. Роль определяется по username: `admin_*`, `teacher_*`, `student_*`


## Замени HTTP Basic Auth на OAuth2.
Оба эндпоинта используют Bearer токены:

* GET /students/ 
* POST /students/




```py
# api.py
@router.get("/students/")
def get_students(
    service = Depends(get_service),
    current_user = Depends(authenticate_oauth)  # Требуем OAuth2 Auth
):

```

# Создадим роли и внесем изменения в сервисный слой

```py
# roles.py
from fastapi import HTTPException, status
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

# Пользователи с ролями
USERS = {
    "admin": {"password": "admin123", "role": Role.ADMIN},
    "teacher": {"password": "teacher123", "role": Role.TEACHER},
    "student": {"password": "student123", "role": Role.STUDENT}
}

def get_user_role(username: str) -> Role:
    """Получить роль пользователя"""
    user = USERS.get(username)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user["role"]

def check_permission(user_role: Role, required_roles: list[Role]):
    """Проверить права доступа"""
    if user_role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {[r.value for r in required_roles]}"
        )

# api.py

def authenticate_user_for_token(username: str, password: str):
    """Проверка пользователя для выдачи токена"""
    from roles import USERS
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"id": 1, "username": username, "role": user["role"]}
    return None


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
    current_user = Depends(authenticate_user_with_role)  # Требуем Basic Auth
):
    # Проверяем права доступа (все роли могут просматривать)
    user_role = get_user_role(current_user)
    check_permission(user_role, [Role.ADMIN, Role.TEACHER, Role.STUDENT])
    
    try:
        print(f"Пользователь {current_user} ({user_role}) запросил список студентов")
        return service.get_all()
    except Exception as e:
        return {"error": f"Failed to get students: {str(e)}"}

```


Добавьте эндпоинт для удаления студентов:

DELETE /students/{student_id} - только admin может удалять


```py
# app.py
@router.delete("/students/{student_id}")
def delete_student(
    ...
):
   ...

# service.py

def delete(self, student_id: int):
    student = ...
    ...
    return {"message": f"Student {student.name} deleted"}
```