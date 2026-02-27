"""
Schemas for employee management module

Claudy ✨ — 2026-02-27
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.employee import DepartmentType, RoleLevelType, EntityStatus


class RoleSummary(BaseModel):
    id: int
    department: DepartmentType
    level: RoleLevelType
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeSummary(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    status: EntityStatus
    hire_date: date
    roles: List[RoleSummary]
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(BaseModel):
    items: List[EmployeeSummary]
    total: int
