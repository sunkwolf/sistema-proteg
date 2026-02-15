"""Pydantic schemas for the admin module."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ── Audit Log ─────────────────────────────────────────────────────────


class AuditLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    table_name: str
    record_id: int
    action: str
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    changed_by_user_id: int | None = None
    changed_by: str | None = None
    changed_at: datetime


class AuditLogListResponse(BaseModel):
    items: list[AuditLogEntry]
    total: int
    skip: int
    limit: int


# ── Roles ─────────────────────────────────────────────────────────────


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime


class RoleWithPermissions(RoleResponse):
    permissions: list[PermissionResponse] = []


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


# ── Permissions ───────────────────────────────────────────────────────


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None


class RolePermissionAssign(BaseModel):
    """Assign a list of permission IDs to a role (replaces existing)."""
    permission_ids: list[int]


# ── Departments ───────────────────────────────────────────────────────


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime


# ── System Info ───────────────────────────────────────────────────────


class SystemInfoResponse(BaseModel):
    app_name: str
    app_version: str
    total_users: int
    active_users: int
    total_roles: int
    total_permissions: int
    total_departments: int


# ── Status Updater ───────────────────────────────────────────────────


class StatusUpdaterResponse(BaseModel):
    payments_updated: int
    policies_updated: int
