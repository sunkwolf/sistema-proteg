"""Admin business logic — audit log, roles/permissions, system info."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.auth import Role
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AuditLogEntry,
    AuditLogListResponse,
    DepartmentResponse,
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleWithPermissions,
    SystemInfoResponse,
)


class AdminService:
    def __init__(self, session: AsyncSession):
        self.repo = AdminRepository(session)

    # ── Audit Log ─────────────────────────────────────────────────────

    async def list_audit_logs(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        table_name: str | None = None,
        action: str | None = None,
        user_id: int | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AuditLogListResponse:
        items, total = await self.repo.list_audit_logs(
            skip=skip,
            limit=limit,
            table_name=table_name,
            action=action,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )
        return AuditLogListResponse(
            items=[AuditLogEntry.model_validate(i) for i in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    # ── Roles ─────────────────────────────────────────────────────────

    async def list_roles(self) -> list[RoleResponse]:
        roles = await self.repo.list_roles()
        return [RoleResponse.model_validate(r) for r in roles]

    async def get_role(self, role_id: int) -> RoleWithPermissions:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        perms = [
            PermissionResponse.model_validate(rp.permission)
            for rp in role.role_permissions
        ]
        return RoleWithPermissions(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            permissions=perms,
        )

    async def create_role(self, data: RoleCreate) -> RoleResponse:
        existing = await self.repo.get_role_by_name(data.name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un rol con nombre '{data.name}'",
            )
        role = Role(name=data.name, description=data.description)
        role = await self.repo.create_role(role)
        return RoleResponse.model_validate(role)

    async def update_role(self, role_id: int, data: RoleUpdate) -> RoleResponse:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        updates = data.model_dump(exclude_unset=True)
        if "name" in updates and updates["name"] != role.name:
            dup = await self.repo.get_role_by_name(updates["name"])
            if dup is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un rol con nombre '{updates['name']}'",
                )

        for field, value in updates.items():
            setattr(role, field, value)

        role = await self.repo.update_role(role)
        return RoleResponse.model_validate(role)

    async def assign_permissions_to_role(
        self, role_id: int, permission_ids: list[int]
    ) -> RoleWithPermissions:
        role = await self.repo.get_role_by_id(role_id)
        if role is None:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        if permission_ids:
            valid = await self.repo.permissions_exist(permission_ids)
            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uno o mas IDs de permisos no existen",
                )

        await self.repo.set_role_permissions(role_id, permission_ids)

        # Re-fetch with permissions
        return await self.get_role(role_id)

    # ── Permissions ───────────────────────────────────────────────────

    async def list_permissions(self) -> list[PermissionResponse]:
        perms = await self.repo.list_permissions()
        return [PermissionResponse.model_validate(p) for p in perms]

    # ── Departments ───────────────────────────────────────────────────

    async def list_departments(self) -> list[DepartmentResponse]:
        depts = await self.repo.list_departments()
        return [DepartmentResponse.model_validate(d) for d in depts]

    # ── System Info ───────────────────────────────────────────────────

    async def get_system_info(self) -> SystemInfoResponse:
        settings = get_settings()
        return SystemInfoResponse(
            app_name=settings.APP_NAME,
            app_version=settings.APP_VERSION,
            total_users=await self.repo.count_users(),
            active_users=await self.repo.count_active_users(),
            total_roles=await self.repo.count_roles(),
            total_permissions=await self.repo.count_permissions(),
            total_departments=await self.repo.count_departments(),
        )
