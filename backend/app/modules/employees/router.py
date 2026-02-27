"""
Router for employee management module

Claudy ✨ — 2026-02-27
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee, EntityStatus, DepartmentType
from .schemas import EmployeeListResponse, EmployeeSummary

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=EmployeeListResponse)
async def list_employees(
    status: Optional[EntityStatus] = None,
    department: Optional[DepartmentType] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los empleados con sus roles.
    Filtros opcionales por estatus, departamento y búsqueda por nombre.
    """
    query = db.query(Employee)
    
    if status:
        query = query.filter(Employee.status == status)
    
    if department:
        query = query.join(Employee.roles).filter(Employee.roles.any(department=department))
        
    if search:
        query = query.filter(
            (Employee.first_name.ilike(f"%{search}%")) | 
            (Employee.last_name.ilike(f"%{search}%"))
        )
        
    employees = query.all()
    
    return {
        "items": employees,
        "total": len(employees)
    }

@router.get("/{employee_id}", response_model=EmployeeSummary)
async def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de un empleado."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return employee
