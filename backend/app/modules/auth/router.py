"""
Authentication Router

Claudy ✨ — 2026-02-27
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.auth.service import authenticate_user, create_user_tokens

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y devuelve el token de acceso."""
    user = await authenticate_user(db, data.username, data.password)
    return create_user_tokens(user)

@router.post("/logout", status_code=204)
async def logout():
    """Cierra la sesión (invalida el token en el cliente)."""
    return None
