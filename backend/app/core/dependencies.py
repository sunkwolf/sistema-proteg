import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.auth import AppUser

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AppUser:
    """Extract and validate JWT, return the authenticated AppUser."""
    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    result = await db.execute(select(AppUser).where(AppUser.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Type alias for dependency injection
CurrentUser = Annotated[AppUser, Depends(get_current_user)]


def require_permission(permission_name: str):
    """Factory that returns a dependency checking a specific permission.

    Resolution order:
      1. Role-based permissions (role_permission table)
      2. Employee permission overrides (employee_permission_override table)
         - granted=true  → explicitly granted regardless of role
         - granted=false → explicitly revoked regardless of role
    """

    async def _check_permission(
        current_user: CurrentUser,
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> AppUser:
        from app.models.auth import Permission, RolePermission
        from app.models.business import Employee, EmployeePermissionOverride

        # Step 1: Check employee-level overrides first (they take priority)
        employee_result = await db.execute(
            select(Employee.id).where(
                Employee.user_id == current_user.id,
                Employee.status == "active",
            )
        )
        employee_id = employee_result.scalar_one_or_none()

        if employee_id is not None:
            override_result = await db.execute(
                select(EmployeePermissionOverride.granted)
                .join(Permission, Permission.id == EmployeePermissionOverride.permission_id)
                .where(
                    EmployeePermissionOverride.employee_id == employee_id,
                    Permission.name == permission_name,
                )
            )
            override = override_result.scalar_one_or_none()
            if override is not None:
                if not override:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permiso requerido: {permission_name}",
                    )
                return current_user

        # Step 2: Check role-based permissions
        if current_user.role_id is not None:
            role_result = await db.execute(
                select(Permission.name)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(
                    RolePermission.role_id == current_user.role_id,
                    Permission.name == permission_name,
                )
            )
            if role_result.scalar_one_or_none() is not None:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso requerido: {permission_name}",
        )

    return Depends(_check_permission)
