"""Data access layer for admin: audit log, roles, permissions, departments."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog
from app.models.auth import AppUser, Department, Permission, Role, RolePermission


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if table_name is not None:
            query = query.where(AuditLog.table_name == table_name)
            count_query = count_query.where(AuditLog.table_name == table_name)
        if action is not None:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if user_id is not None:
            query = query.where(AuditLog.changed_by_user_id == user_id)
            count_query = count_query.where(AuditLog.changed_by_user_id == user_id)
        if date_from is not None:
            query = query.where(AuditLog.changed_at >= date_from)
            count_query = count_query.where(AuditLog.changed_at >= date_from)
        if date_to is not None:
            query = query.where(AuditLog.changed_at <= date_to)
            count_query = count_query.where(AuditLog.changed_at <= date_to)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(AuditLog.changed_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    # ── Roles ─────────────────────────────────────────────────────────

    async def list_roles(self) -> list[Role]:
        result = await self.session.execute(
            select(Role).order_by(Role.name.asc())
        )
        return list(result.scalars().all())

    async def get_role_by_id(self, role_id: int) -> Role | None:
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()

    async def create_role(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def update_role(self, role: Role) -> Role:
        await self.session.flush()
        await self.session.refresh(role)
        return role

    async def set_role_permissions(
        self, role_id: int, permission_ids: list[int]
    ) -> None:
        """Replace all permissions for a role."""
        # Delete existing
        existing = await self.session.execute(
            select(RolePermission).where(RolePermission.role_id == role_id)
        )
        for rp in existing.scalars().all():
            await self.session.delete(rp)
        await self.session.flush()

        # Insert new
        for pid in permission_ids:
            self.session.add(RolePermission(role_id=role_id, permission_id=pid))
        await self.session.flush()

    # ── Permissions ───────────────────────────────────────────────────

    async def list_permissions(self) -> list[Permission]:
        result = await self.session.execute(
            select(Permission).order_by(Permission.name.asc())
        )
        return list(result.scalars().all())

    async def get_permission_by_id(self, perm_id: int) -> Permission | None:
        result = await self.session.execute(
            select(Permission).where(Permission.id == perm_id)
        )
        return result.scalar_one_or_none()

    async def permissions_exist(self, ids: list[int]) -> bool:
        """Check that all given permission IDs exist."""
        result = await self.session.execute(
            select(func.count(Permission.id)).where(Permission.id.in_(ids))
        )
        return result.scalar_one() == len(ids)

    # ── Departments ───────────────────────────────────────────────────

    async def list_departments(self) -> list[Department]:
        result = await self.session.execute(
            select(Department).order_by(Department.name.asc())
        )
        return list(result.scalars().all())

    # ── System stats ──────────────────────────────────────────────────

    async def count_users(self) -> int:
        result = await self.session.execute(select(func.count(AppUser.id)))
        return result.scalar_one()

    async def count_active_users(self) -> int:
        result = await self.session.execute(
            select(func.count(AppUser.id)).where(AppUser.is_active == True)  # noqa: E712
        )
        return result.scalar_one()

    async def count_roles(self) -> int:
        result = await self.session.execute(select(func.count(Role.id)))
        return result.scalar_one()

    async def count_permissions(self) -> int:
        result = await self.session.execute(select(func.count(Permission.id)))
        return result.scalar_one()

    async def count_departments(self) -> int:
        result = await self.session.execute(select(func.count(Department.id)))
        return result.scalar_one()
