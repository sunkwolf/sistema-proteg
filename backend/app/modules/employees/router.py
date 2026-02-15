"""Employee endpoints — CRUD, departments, permission overrides, role shortcuts."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.employees.schemas import (
    DepartmentAssignment,
    DepartmentInfo,
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeUpdate,
    PermissionOverrideInfo,
    PermissionOverrideInput,
)
from app.modules.employees.service import EmployeeService

router = APIRouter()


# ── CRUD ─────────────────────────────────────────────────────────────


@router.get("", response_model=EmployeeListResponse)
async def list_employees(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None, pattern="^(active|inactive)$"),
    es_vendedor: bool | None = None,
    es_cobrador: bool | None = None,
    es_ajustador: bool | None = None,
    department_id: int | None = None,
    search: str | None = Query(None, max_length=100),
):
    """List employees with optional filters and pagination."""
    service = EmployeeService(db)
    return await service.list_employees(
        skip=skip,
        limit=limit,
        status=status,
        es_vendedor=es_vendedor,
        es_cobrador=es_cobrador,
        es_ajustador=es_ajustador,
        department_id=department_id,
        search=search,
    )


@router.get("/by-role/sellers", response_model=EmployeeListResponse)
async def list_sellers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List employees with es_vendedor=true."""
    service = EmployeeService(db)
    return await service.list_employees(
        skip=skip, limit=limit, es_vendedor=True, status="active"
    )


@router.get("/by-role/collectors", response_model=EmployeeListResponse)
async def list_collectors(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List employees with es_cobrador=true."""
    service = EmployeeService(db)
    return await service.list_employees(
        skip=skip, limit=limit, es_cobrador=True, status="active"
    )


@router.get("/by-role/adjusters", response_model=EmployeeListResponse)
async def list_adjusters(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List employees with es_ajustador=true."""
    service = EmployeeService(db)
    return await service.list_employees(
        skip=skip, limit=limit, es_ajustador=True, status="active"
    )


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
):
    """Get employee by ID."""
    service = EmployeeService(db)
    return await service.get_employee(employee_id)


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.create")],
):
    """Create a new employee."""
    service = EmployeeService(db)
    return await service.create_employee(data)


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.update")],
):
    """Update employee fields."""
    service = EmployeeService(db)
    return await service.update_employee(employee_id, data)


@router.patch("/{employee_id}/toggle-status", response_model=EmployeeResponse)
async def toggle_employee_status(
    employee_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.toggle_status")],
):
    """Toggle employee active/inactive status."""
    service = EmployeeService(db)
    return await service.toggle_status(employee_id)


# ── Department assignments ───────────────────────────────────────────


@router.get(
    "/{employee_id}/departments", response_model=list[DepartmentInfo]
)
async def get_employee_departments(
    employee_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
):
    """Get departments assigned to an employee."""
    service = EmployeeService(db)
    return await service.get_departments(employee_id)


@router.put(
    "/{employee_id}/departments", response_model=list[DepartmentInfo]
)
async def update_employee_departments(
    employee_id: int,
    assignments: list[DepartmentAssignment],
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.update")],
):
    """Replace department assignments for an employee."""
    service = EmployeeService(db)
    return await service.update_departments(employee_id, assignments)


# ── Permission overrides ─────────────────────────────────────────────


@router.get(
    "/{employee_id}/permissions",
    response_model=list[PermissionOverrideInfo],
)
async def get_employee_permissions(
    employee_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.read")],
):
    """Get permission overrides for an employee."""
    service = EmployeeService(db)
    return await service.get_permission_overrides(employee_id)


@router.put(
    "/{employee_id}/permissions",
    response_model=list[PermissionOverrideInfo],
)
async def update_employee_permissions(
    employee_id: int,
    overrides: list[PermissionOverrideInput],
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("employees.update")],
):
    """Replace permission overrides for an employee."""
    service = EmployeeService(db)
    return await service.update_permission_overrides(employee_id, overrides)
