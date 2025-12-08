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