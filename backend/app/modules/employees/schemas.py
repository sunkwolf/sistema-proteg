"""Pydantic schemas for the Employees module."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Request schemas ──────────────────────────────────────────────────


class DepartmentAssignment(BaseModel):
    department_id: int
    es_gerente: bool = False


class PermissionOverrideInput(BaseModel):
    permission_id: int
    granted: bool = True


class EmployeeCreate(BaseModel):
    code_name: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    telegram_id: int | None = None

    es_vendedor: bool = False
    es_cobrador: bool = False
    es_ajustador: bool = False

    seller_class: Literal["seller", "collaborator"] | None = None
    sales_target: int | None = None
    receipt_limit: int = Field(50, ge=1)

    user_id: int | None = None
    departments: list[DepartmentAssignment] = Field(default_factory=list)

    @field_validator("code_name")
    @classmethod
    def code_name_uppercase(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError("El telefono debe tener 10 digitos")
        return digits

    @model_validator(mode="after")
    def at_least_one_role(self) -> EmployeeCreate:
        if not (self.es_vendedor or self.es_cobrador or self.es_ajustador):
            raise ValueError(
                "El empleado debe tener al menos un rol: vendedor, cobrador o ajustador"
            )
        return self

    @model_validator(mode="after")
    def seller_fields_consistency(self) -> EmployeeCreate:
        if not self.es_vendedor:
            self.seller_class = None
            self.sales_target = None
        return self


class EmployeeUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = None
    telegram_id: int | None = None

    es_vendedor: bool | None = None
    es_cobrador: bool | None = None
    es_ajustador: bool | None = None

    seller_class: Literal["seller", "collaborator"] | None = None
    sales_target: int | None = None
    receipt_limit: int | None = Field(None, ge=1)

    user_id: int | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError("El telefono debe tener 10 digitos")
        return digits


# ── Response schemas ─────────────────────────────────────────────────


class DepartmentInfo(BaseModel):
    department_id: int
    department_name: str
    es_gerente: bool


class PermissionOverrideInfo(BaseModel):
    id: int
    permission_id: int
    permission_name: str
    granted: bool


class EmployeeResponse(BaseModel):
    id: int
    code_name: str
    full_name: str
    phone: str | None = None
    telegram_id: int | None = None

    es_vendedor: bool
    es_cobrador: bool
    es_ajustador: bool

    seller_class: str | None = None
    sales_target: int | None = None
    receipt_limit: int

    user_id: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    departments: list[DepartmentInfo] = []

    model_config = {"from_attributes": True}


class EmployeeListResponse(BaseModel):
    items: list[EmployeeResponse]
    total: int
    skip: int
    limit: int
