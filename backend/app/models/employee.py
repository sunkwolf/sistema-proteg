"""
Models for employees (nueva estructura unificada)

Claudy ✨ — 2026-02-27
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from sqlalchemy import (
    ForeignKey, 
    String, 
    Date, 
    Numeric, 
    Text,
    Boolean,
    BigInteger,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


# ─── Enums ─────────────────────────────────────────────────────────────────────

class DepartmentType(str, Enum):
    SALES = "sales"
    COLLECTION = "collection"
    CLAIMS = "claims"
    ADMIN = "admin"
    HR = "hr"
    MANAGEMENT = "management"


class RoleLevelType(str, Enum):
    STAFF = "staff"
    MANAGER = "manager"
    DIRECTOR = "director"


class EntityStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"


class SellerClassType(str, Enum):
    SELLER = "seller"
    COLLABORATOR = "collaborator"


# ─── Models ────────────────────────────────────────────────────────────────────

class Employee(Base, TimestampMixin):
    """
    Empleado de la empresa - persona física.
    Fuente única de verdad para RRHH.
    """
    
    __tablename__ = "employee"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Datos personales
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    birth_date: Mapped[Optional[date]]
    gender: Mapped[Optional[GenderType]]
    
    # Contacto
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    phone_2: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    
    # Documentos
    rfc: Mapped[Optional[str]] = mapped_column(String(13))
    curp: Mapped[Optional[str]] = mapped_column(String(18))
    
    # Dirección
    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey("address.id"))
    
    # Datos laborales
    hire_date: Mapped[date]
    termination_date: Mapped[Optional[date]]
    status: Mapped[EntityStatus] = mapped_column(default=EntityStatus.ACTIVE)
    
    # Relationships
    roles: Mapped[List["EmployeeRole"]] = relationship(back_populates="employee", cascade="all, delete-orphan")
    loans: Mapped[List["EmployeeLoan"]] = relationship(back_populates="employee")
    user: Mapped[Optional["AppUser"]] = relationship(back_populates="employee")
    
    __table_args__ = (
        Index("idx_employee_status", "status"),
        Index("idx_employee_telegram", "telegram_id", postgresql_where="telegram_id IS NOT NULL"),
        Index("idx_employee_name", "last_name", "first_name"),
    )
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class EmployeeRole(Base, TimestampMixin):
    """
    Roles de cada empleado.
    Un empleado puede tener múltiples roles activos.
    """
    
    __tablename__ = "employee_role"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    
    # Rol
    department: Mapped[DepartmentType]
    level: Mapped[RoleLevelType] = mapped_column(default=RoleLevelType.STAFF)
    
    # Vigencia
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[date] = mapped_column(default=date.today)
    end_date: Mapped[Optional[date]]
    
    # Supervisión
    supervisor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employee.id"))
    
    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="roles", foreign_keys=[employee_id])
    supervisor: Mapped[Optional["Employee"]] = relationship(foreign_keys=[supervisor_id])
    
    # Perfiles específicos (1:1)
    seller_profile: Mapped[Optional["SellerProfile"]] = relationship(back_populates="employee_role", uselist=False)
    collector_profile: Mapped[Optional["CollectorProfile"]] = relationship(back_populates="employee_role", uselist=False)
    adjuster_profile: Mapped[Optional["AdjusterProfile"]] = relationship(back_populates="employee_role", uselist=False)
    
    # Liquidaciones
    settlements: Mapped[List["Settlement"]] = relationship(back_populates="employee_role")
    
    __table_args__ = (
        Index("idx_employee_role_employee", "employee_id"),
        Index("idx_employee_role_active", "employee_id", "is_active", postgresql_where="is_active = true"),
        Index("idx_employee_role_dept", "department"),
    )


class SellerProfile(Base, TimestampMixin):
    """Datos específicos de vendedores."""
    
    __tablename__ = "seller_profile"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_role_id: Mapped[int] = mapped_column(ForeignKey("employee_role.id"), unique=True)
    
    code: Mapped[str] = mapped_column(String(10), unique=True)  # V1, V2...
    seller_class: Mapped[SellerClassType] = mapped_column(default=SellerClassType.COLLABORATOR)
    sales_target: Mapped[Optional[int]]
    
    # Relationship
    employee_role: Mapped["EmployeeRole"] = relationship(back_populates="seller_profile")
    
    __table_args__ = (
        Index("idx_seller_profile_role", "employee_role_id"),
        Index("idx_seller_profile_class", "seller_class"),
    )


class CollectorProfile(Base, TimestampMixin):
    """Datos específicos de cobradores."""
    
    __tablename__ = "collector_profile"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_role_id: Mapped[int] = mapped_column(ForeignKey("employee_role.id"), unique=True)
    
    code: Mapped[str] = mapped_column(String(10), unique=True)  # C1, C2...
    receipt_limit: Mapped[int] = mapped_column(default=50)
    zone: Mapped[Optional[str]] = mapped_column(String(50))
    route: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationship
    employee_role: Mapped["EmployeeRole"] = relationship(back_populates="collector_profile")
    
    __table_args__ = (
        Index("idx_collector_profile_role", "employee_role_id"),
        Index("idx_collector_profile_zone", "zone", postgresql_where="zone IS NOT NULL"),
    )


class AdjusterProfile(Base, TimestampMixin):
    """Datos específicos de ajustadores."""
    
    __tablename__ = "adjuster_profile"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_role_id: Mapped[int] = mapped_column(ForeignKey("employee_role.id"), unique=True)
    
    code: Mapped[str] = mapped_column(String(10), unique=True)  # M1, M2...
    shift_preference: Mapped[Optional[str]] = mapped_column(String(20))  # first, second, third, rest
    
    # Relationship
    employee_role: Mapped["EmployeeRole"] = relationship(back_populates="adjuster_profile")
    
    __table_args__ = (
        Index("idx_adjuster_profile_role", "employee_role_id"),
    )


class SettlementPermission(Base):
    """Permisos para pagar liquidaciones. Solo Elena y Oscar tienen can_pay=true."""
    
    __tablename__ = "settlement_permission"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), unique=True)
    can_pay: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationship
    employee: Mapped["Employee"] = relationship()


# ─── Commission Tables ─────────────────────────────────────────────────────────

class SellerLevelThreshold(Base):
    """Rangos de ventas mensuales para determinar nivel del vendedor."""
    
    __tablename__ = "seller_level_threshold"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    level: Mapped[int] = mapped_column(unique=True)
    min_sales: Mapped[int]
    max_sales: Mapped[Optional[int]]  # NULL = sin límite (nivel 7)


class SellerCommissionRate(Base):
    """Comisiones de vendedores con vigencia histórica."""
    
    __tablename__ = "seller_commission_rate"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    seller_class: Mapped[SellerClassType]
    level: Mapped[int]
    coverage_name: Mapped[str] = mapped_column(String(50))
    effective_from: Mapped[date]
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint("seller_class", "level", "coverage_name", "effective_from", name="uq_commission_rate"),
        Index("idx_commission_rate_lookup", "seller_class", "level", "coverage_name", "effective_from"),
    )
