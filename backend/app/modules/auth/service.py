"""
Authentication Service

Claudy ✨ — 2026-02-27 (fixed async 2026-03-02)
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.user import AppUser
from app.core.security import verify_password, create_access_token
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

async def authenticate_user(
    db: AsyncSession, 
    username: str, 
    password: str
) -> AppUser:
    """Valida credenciales y devuelve el usuario si es correcto."""
    result = await db.execute(
        select(AppUser).where(AppUser.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Intento de login fallido: usuario {username} no existe")
        raise AppException(status_code=401, detail="Credenciales incorrectas")
        
    if not user.is_active:
        logger.warning(f"Intento de login: usuario {username} está inactivo")
        raise AppException(status_code=403, detail="Usuario inactivo")
        
    if not verify_password(password, user.password_hash):
        logger.warning(f"Intento de login fallido: contraseña incorrecta para {username}")
        raise AppException(status_code=401, detail="Credenciales incorrectas")
        
    # Actualizar último login
    user.last_login = datetime.now(timezone.utc)
    
    return user

def create_user_tokens(user: AppUser) -> dict:
    """Genera los tokens de acceso para el usuario."""
    access_token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username,
        "employee_id": user.employee_id,
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "name": user.username,  # TODO: join employee for full_name
        }
    }
