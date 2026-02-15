from fastapi import APIRouter, Depends, Response
from app.modules.auth.schemas import LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """Authenticate user and return access token."""
    # TODO: Implement in Fase 1
    ...


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token():
    """Refresh access token using refresh cookie."""
    # TODO: Implement in Fase 1
    ...


@router.post("/logout", status_code=204)
async def logout():
    """Logout and invalidate refresh token."""
    # TODO: Implement in Fase 1
    ...
