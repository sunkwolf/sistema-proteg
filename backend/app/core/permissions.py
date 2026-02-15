from functools import wraps
from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user


def require_permission(permission: str):
    """Dependency that checks if the current user has the required permission.

    Usage: current_user = Depends(require_permission("payments.edit"))
    """
    async def _check_permission(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_permissions: list[str] = current_user.get("permissions", [])

        # Admin wildcard
        if "*" in user_permissions:
            return current_user

        # Check exact match
        if permission in user_permissions:
            return current_user

        # Check module wildcard (e.g., "payments.*" matches "payments.edit")
        module = permission.split(".")[0]
        if f"{module}.*" in user_permissions:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permiso requerido: {permission}",
        )

    return _check_permission
