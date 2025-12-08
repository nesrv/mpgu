# auth.py - HTTP Basic Auth аутентификация для FastAPI приложения

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# ========== НАСТРОЙКА BASIC AUTH ==========
# Создаем объект для HTTP Basic Auth
security = HTTPBasic()



# ========== BASIC AUTH ФУНКЦИЯ ==========
def authenticate_user_with_role(credentials = Depends(security)):
    from roles import USERS
    
    user = USERS.get(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Проверяем пароль
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), user["password"].encode("utf8")
    )
    
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

