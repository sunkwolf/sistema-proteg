import logging
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as redis

from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import CurrentUser
from app.core.redis import get_redis
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserInfo
from app.modules.auth.service import AuthService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Set refresh token as httpOnly cookie."""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS_WEB * 86400,
        path=f"{settings.API_V1_PREFIX}/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Clear refresh token cookie."""
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=not settings.DEBUG,
        samesite="strict",
        path=f"{settings.API_V1_PREFIX}/auth",
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
):
    """Authenticate user and return access token + set refresh cookie."""
    service = AuthService(db, redis_client)

    client_ip = request.client.host if request.client else "unknown"

    # Rate limit check (also records the attempt so lockout counter advances)
    is_limited, is_locked = await service.check_rate_limit_and_lockout(
        data.username, client_ip
    )
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Cuenta bloqueada temporalmente por demasiados intentos fallidos.",
        )
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de login. Intenta mas tarde.",
        )

    result = await service.authenticate(data.username, data.password, client_ip)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _set_refresh_cookie(response, result["refresh_token"])

    return LoginResponse(
        access_token=result["access_token"],
        expires_in=result["expires_in"],
        user=UserInfo.model_validate(result["user"]),
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    """Refresh access token using refresh cookie (token rotation)."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token no encontrado",
        )

    service = AuthService(db, redis_client)
    result = await service.refresh(refresh_token)

    if result is None:
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido o expirado",
        )

    _set_refresh_cookie(response, result["refresh_token"])

    return LoginResponse(
        access_token=result["access_token"],
        expires_in=result["expires_in"],
        user=UserInfo.model_validate(result["user"]),
    )


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    redis_client: Annotated[redis.Redis, Depends(get_redis)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    """Logout and invalidate refresh token."""
    if refresh_token:
        service = AuthService.__new__(AuthService)
        service.redis = redis_client
        await service.logout(refresh_token)

    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: CurrentUser):
    """Return current authenticated user info."""
    return UserInfo.model_validate(current_user)
