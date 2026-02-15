"""Business logic for employees."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Employee
from app.modules.employees.repository import EmployeeRepository
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


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.repo = EmployeeRepository(db)

    # ── Serialization helpers ────────────────────────────────────────

    @staticmethod
    def _to_response(emp: Employee) -> EmployeeResponse:
        departments = [
            DepartmentInfo(
                department_id=ed.department_id,
                department_name=ed.department.name,
                es_gerente=ed.es_gerente,
            )
            for ed in emp.departments
        ]
        return EmployeeResponse(
            id=emp.id,
            code_name=emp.code_name,
            full_name=emp.full_name,
            phone=emp.phone,
            telegram_id=emp.telegram_id,
            es_vendedor=emp.es_vendedor,
            es_cobrador=emp.es_cobrador,
            es_ajustador=emp.es_ajustador,
            seller_class=emp.seller_class.value if emp.seller_class else None,
            sales_target=emp.sales_target,
            receipt_limit=emp.receipt_limit,
            user_id=emp.user_id,
            status=emp.status.value if hasattr(emp.status, "value") else str(emp.status),
            created_at=emp.created_at,
            updated_at=emp.updated_at,
            departments=departments,
        )

    # ── CRUD ─────────────────────────────────────────────────────────

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
    ) -> EmployeeListResponse:
        employees, total = await self.repo.list_employees(
            skip=skip,
            limit=limit,
            status=status,
            es_vendedor=es_vendedor,
            es_cobrador=es_cobrador,
            es_ajustador=es_ajustador,
            department_id=department_id,
            search=search,
        )
        return EmployeeListResponse(
            items=[self._to_response(e) for e in employees],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_employee(self, employee_id: int) -> EmployeeResponse:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        return self._to_response(emp)

    async def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        # Check code_name uniqueness
        existing = await self.repo.get_by_code_name(data.code_name)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un empleado con code_name '{data.code_name}'",
            )

        # Validate departments exist
        for dept in data.departments:
            if not await self.repo.department_exists(dept.department_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Departamento con id {dept.department_id} no existe",
                )

        # Create employee
        employee = Employee(
            code_name=data.code_name,
            full_name=data.full_name,
            phone=data.phone,
            telegram_id=data.telegram_id,
            es_vendedor=data.es_vendedor,
            es_cobrador=data.es_cobrador,
            es_ajustador=data.es_ajustador,
            seller_class=data.seller_class,
            sales_target=data.sales_target,
            receipt_limit=data.receipt_limit,
            user_id=data.user_id,
        )
        employee = await self.repo.create(employee)

        # Assign departments
        if data.departments:
            await self.repo.set_departments(
                employee.id,
                [d.model_dump() for d in data.departments],
            )
            employee = await self.repo.get_by_id(employee.id)  # type: ignore[assignment]

        return self._to_response(employee)

    async def update_employee(
        self, employee_id: int, data: EmployeeUpdate
    ) -> EmployeeResponse:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(emp, field, value)

        # Validate at least one role remains
        if not (emp.es_vendedor or emp.es_cobrador or emp.es_ajustador):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El empleado debe tener al menos un rol",
            )

        # Clear seller fields if not vendedor
        if not emp.es_vendedor:
            emp.seller_class = None
            emp.sales_target = None

        emp = await self.repo.update(emp)
        return self._to_response(emp)

    async def toggle_status(self, employee_id: int) -> EmployeeResponse:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        emp.status = "inactive" if str(emp.status) == "active" else "active"
        emp = await self.repo.update(emp)
        return self._to_response(emp)

    # ── Departments ──────────────────────────────────────────────────

    async def get_departments(self, employee_id: int) -> list[DepartmentInfo]:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        dept_list = await self.repo.get_departments(employee_id)
        return [
            DepartmentInfo(
                department_id=ed.department_id,
                department_name=ed.department.name,
                es_gerente=ed.es_gerente,
            )
            for ed in dept_list
        ]

    async def update_departments(
        self, employee_id: int, assignments: list[DepartmentAssignment]
    ) -> list[DepartmentInfo]:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )

        for dept in assignments:
            if not await self.repo.department_exists(dept.department_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Departamento con id {dept.department_id} no existe",
                )

        await self.repo.set_departments(
            employee_id,
            [d.model_dump() for d in assignments],
        )
        return await self.get_departments(employee_id)

    # ── Permission overrides ─────────────────────────────────────────

    async def get_permission_overrides(
        self, employee_id: int
    ) -> list[PermissionOverrideInfo]:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        overrides = await self.repo.get_permission_overrides(employee_id)
        return [
            PermissionOverrideInfo(
                id=o.id,
                permission_id=o.permission_id,
                permission_name=o.permission.name,
                granted=o.granted,
            )
            for o in overrides
        ]

    async def update_permission_overrides(
        self, employee_id: int, overrides: list[PermissionOverrideInput]
    ) -> list[PermissionOverrideInfo]:
        emp = await self.repo.get_by_id(employee_id)
        if emp is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )

        for override in overrides:
            if not await self.repo.permission_exists(override.permission_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Permiso con id {override.permission_id} no existe",
                )

        await self.repo.set_permission_overrides(
            employee_id,
            [o.model_dump() for o in overrides],
        )
        return await self.get_permission_overrides(employee_id)
