"""Data access layer for employees."""

from __future__ import annotations

from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.auth import Department, Permission
from app.models.business import Employee, EmployeeDepartment, EmployeePermissionOverride


class EmployeeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        """Base query with department relationship eagerly loaded."""
        return select(Employee).options(
            selectinload(Employee.departments).selectinload(
                EmployeeDepartment.department
            )
        )

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, employee_id: int) -> Employee | None:
        result = await self.session.execute(
            self._base_query().where(Employee.id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code_name(self, code_name: str) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(Employee.code_name == code_name)
        )
        return result.scalar_one_or_none()

    async def list_employees(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        es_vendedor: bool | None = None,
        es_cobrador: bool | None = None,
        es_ajustador: bool | None = None,
        department_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Employee], int]:
        """Return (employees, total_count) with filters applied."""
        query = self._base_query()
        count_query = select(func.count(Employee.id))

        # Apply filters
        if status is not None:
            query = query.where(Employee.status == status)
            count_query = count_query.where(Employee.status == status)
        if es_vendedor is not None:
            query = query.where(Employee.es_vendedor == es_vendedor)
            count_query = count_query.where(Employee.es_vendedor == es_vendedor)
        if es_cobrador is not None:
            query = query.where(Employee.es_cobrador == es_cobrador)
            count_query = count_query.where(Employee.es_cobrador == es_cobrador)
        if es_ajustador is not None:
            query = query.where(Employee.es_ajustador == es_ajustador)
            count_query = count_query.where(Employee.es_ajustador == es_ajustador)
        if department_id is not None:
            query = query.join(EmployeeDepartment).where(
                EmployeeDepartment.department_id == department_id
            )
            count_query = count_query.join(EmployeeDepartment).where(
                EmployeeDepartment.department_id == department_id
            )
        if search:
            pattern = f"%{search}%"
            query = query.where(
                Employee.full_name.ilike(pattern)
                | Employee.code_name.ilike(pattern)
            )
            count_query = count_query.where(
                Employee.full_name.ilike(pattern)
                | Employee.code_name.ilike(pattern)
            )

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Employee.full_name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        employees = list(result.scalars().unique().all())

        return employees, total

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        # Reload with relationships
        return await self.get_by_id(employee.id)  # type: ignore[return-value]

    async def update(self, employee: Employee) -> Employee:
        await self.session.flush()
        return await self.get_by_id(employee.id)  # type: ignore[return-value]

    # ── Departments ──────────────────────────────────────────────────

    async def get_departments(self, employee_id: int) -> list[EmployeeDepartment]:
        result = await self.session.execute(
            select(EmployeeDepartment)
            .options(selectinload(EmployeeDepartment.department))
            .where(EmployeeDepartment.employee_id == employee_id)
        )
        return list(result.scalars().all())

    async def set_departments(
        self, employee_id: int, assignments: list[dict]
    ) -> None:
        """Replace all department assignments for an employee."""
        await self.session.execute(
            delete(EmployeeDepartment).where(
                EmployeeDepartment.employee_id == employee_id
            )
        )
        for assignment in assignments:
            self.session.add(
                EmployeeDepartment(
                    employee_id=employee_id,
                    department_id=assignment["department_id"],
                    es_gerente=assignment.get("es_gerente", False),
                )
            )
        await self.session.flush()

    async def department_exists(self, department_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Department.id)).where(Department.id == department_id)
        )
        return result.scalar_one() > 0

    # ── Permission overrides ─────────────────────────────────────────

    async def get_permission_overrides(
        self, employee_id: int
    ) -> list[EmployeePermissionOverride]:
        result = await self.session.execute(
            select(EmployeePermissionOverride)
            .options(selectinload(EmployeePermissionOverride.permission))
            .where(EmployeePermissionOverride.employee_id == employee_id)
        )
        return list(result.scalars().all())

    async def set_permission_overrides(
        self, employee_id: int, overrides: list[dict]
    ) -> None:
        """Replace all permission overrides for an employee."""
        await self.session.execute(
            delete(EmployeePermissionOverride).where(
                EmployeePermissionOverride.employee_id == employee_id
            )
        )
        for override in overrides:
            self.session.add(
                EmployeePermissionOverride(
                    employee_id=employee_id,
                    permission_id=override["permission_id"],
                    granted=override.get("granted", True),
                )
            )
        await self.session.flush()

    async def permission_exists(self, permission_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Permission.id)).where(Permission.id == permission_id)
        )
        return result.scalar_one() > 0
