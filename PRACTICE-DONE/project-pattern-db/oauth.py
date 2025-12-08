# oauth.py - OAuth2 аутентификация для FastAPI приложения

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
    
    return USER_DATA.get("username", "oauth_user")

# ========== ФУНКЦИЯ СОЗДАНИЯ ПРОСТОГО ТОКЕНА ==========
# Сохраняем информацию о пользователе для токена
USER_DATA = {}

def create_access_token(data: dict):
    """Создает простой UUID токен"""
    global VALID_TOKEN, USER_DATA
    token = str(uuid.uuid4())
    VALID_TOKEN = token
    USER_DATA = data  # Сохраняем данные пользователя
    return token