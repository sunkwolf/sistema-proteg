"""Admin endpoints — audit log, roles, permissions, departments, system info."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.admin.schemas import (
    AuditLogListResponse,
    BackupInfoResponse,
    DepartmentResponse,
    PermissionResponse,
    RoleCreate,
    RolePermissionAssign,
    RoleResponse,
    RoleUpdate,
    RoleWithPermissions,
    StatusUpdaterResponse,
    SystemInfoResponse,
)
from app.modules.admin.service import AdminService
from app.modules.policies.status_updater import run_status_updater

router = APIRouter()


# ── Audit Log ─────────────────────────────────────────────────────────


@router.get("/audit-log", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.audit_log")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    table_name: str | None = Query(None),
    action: str | None = Query(None),
    user_id: int | None = Query(None),
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
):
    """List audit log entries with filters."""
    service = AdminService(db)
    return await service.list_audit_logs(
        skip=skip,
        limit=limit,
        table_name=table_name,
        action=action,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )


# ── Roles ─────────────────────────────────────────────────────────────


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.access")],
):
    """List all roles."""
    service = AdminService(db)
    return await service.list_roles()


@router.get("/roles/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.access")],
):
    """Get role with its assigned permissions."""
    service = AdminService(db)
    return await service.get_role(role_id)


@router.post("/roles", response_model=RoleResponse, status_code=201)
async def create_role(
    data: RoleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.config")],
):
    """Create a new role."""
    service = AdminService(db)
    return await service.create_role(data)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.config")],
):
    """Update a role."""
    service = AdminService(db)
    return await service.update_role(role_id, data)


@router.post(
    "/roles/{role_id}/permissions",
    response_model=RoleWithPermissions,
)
async def assign_permissions_to_role(
    role_id: int,
    data: RolePermissionAssign,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.config")],
):
    """Replace all permissions for a role."""
    service = AdminService(db)
    return await service.assign_permissions_to_role(role_id, data.permission_ids)


# ── Permissions ───────────────────────────────────────────────────────


@router.get("/permissions", response_model=list[PermissionResponse])
async def list_permissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.access")],
):
    """List all permissions in the system."""
    service = AdminService(db)
    return await service.list_permissions()


# ── Departments ───────────────────────────────────────────────────────


@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.access")],
):
    """List all departments."""
    service = AdminService(db)
    return await service.list_departments()


# ── System Info ───────────────────────────────────────────────────────


@router.get("/info", response_model=SystemInfoResponse)
async def get_system_info(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.access")],
):
    """Get system information and stats."""
    service = AdminService(db)
    return await service.get_system_info()


# ── Status Updater (manual trigger) ──────────────────────────────────


@router.post("/status-update", response_model=StatusUpdaterResponse)
async def trigger_status_update(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("admin.config")],
):
    """Manually trigger the StatusUpdater (normally runs at midnight via Celery)."""
    result = await run_status_updater(db)
    return result


# ── Backup Status ────────────────────────────────────────────────────


@router.get("/backup-status", response_model=BackupInfoResponse)
async def get_backup_status(
    _user: Annotated[None, require_permission("admin.access")],
):
    """Check pgBackRest backup status (runs pgbackrest info command)."""
    import asyncio
    import json as json_lib

    try:
        proc = await asyncio.create_subprocess_exec(
            "pgbackrest", "--stanza=protegrt", "info", "--output=json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)

        if proc.returncode != 0:
            return BackupInfoResponse(
                available=False,
                error=f"pgbackrest retorno codigo {proc.returncode}",
            )

        data = json_lib.loads(stdout.decode())
        if not data or not data[0].get("backup"):
            return BackupInfoResponse(available=True, error="Sin backups registrados")

        last = data[0]["backup"][-1]
        stop_ts = last.get("timestamp", {}).get("stop", "")

        from datetime import datetime, timezone
        age_hours = None
        if stop_ts:
            backup_dt = datetime.fromtimestamp(stop_ts, tz=timezone.utc)
            age_hours = int(
                (datetime.now(timezone.utc) - backup_dt).total_seconds() / 3600
            )

        return BackupInfoResponse(
            available=True,
            last_backup_type=last.get("type"),
            last_backup_time=str(stop_ts),
            age_hours=age_hours,
        )
    except FileNotFoundError:
        return BackupInfoResponse(
            available=False,
            error="pgbackrest no instalado en este entorno",
        )
    except Exception as exc:
        return BackupInfoResponse(available=False, error=str(exc))
