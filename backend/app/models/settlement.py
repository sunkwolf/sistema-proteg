"""
Models for settlements (liquidaciones)

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
    Computed,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


# ─── Enums ─────────────────────────────────────────────────────────────────────

class SettlementStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"


class SettlementMethod(str, Enum):
    CASH = "cash"
    TRANSFER = "transfer"


class DeductionType(str, Enum):
    FUEL = "fuel"
    LOAN = "loan"
    SHORTAGE = "shortage"
    ADVANCE = "advance"
    OTHER = "other"


class LoanStatus(str, Enum):
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    CANCELLED = "cancelled"


# ─── Models ────────────────────────────────────────────────────────────────────

class EmployeeLoan(Base, TimestampMixin):
    """Préstamos a cobradores/vendedores con pago quincenal."""
    
    __tablename__ = "employee_loan"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    collector_id: Mapped[Optional[int]] = mapped_column(ForeignKey("collector.id"))
    seller_id: Mapped[Optional[int]] = mapped_column(ForeignKey("seller.id"))
    
    concept: Mapped[str] = mapped_column(String(100))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    installment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total_installments: Mapped[int]
    paid_installments: Mapped[int] = mapped_column(default=0)
    remaining_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    
    status: Mapped[LoanStatus] = mapped_column(default=LoanStatus.ACTIVE)
    start_date: Mapped[date]
    end_date: Mapped[Optional[date]]
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    collector: Mapped[Optional["Collector"]] = relationship(back_populates="loans")
    seller: Mapped[Optional["Seller"]] = relationship(back_populates="loans")
    deductions: Mapped[List["SettlementDeduction"]] = relationship(back_populates="loan")
    
    __table_args__ = (
        CheckConstraint(
            "(collector_id IS NOT NULL AND seller_id IS NULL) OR "
            "(collector_id IS NULL AND seller_id IS NOT NULL)",
            name="chk_loan_employee"
        ),
        Index("idx_employee_loan_collector", "collector_id", postgresql_where="collector_id IS NOT NULL"),
        Index("idx_employee_loan_seller", "seller_id", postgresql_where="seller_id IS NOT NULL"),
        Index("idx_employee_loan_status", "status"),
    )


class Settlement(Base, TimestampMixin):
    """Liquidación quincenal de un cobrador."""
    
    __tablename__ = "settlement"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    collector_id: Mapped[int] = mapped_column(ForeignKey("collector.id"))
    
    # Período
    period_start: Mapped[date]
    period_end: Mapped[date]
    
    # Comisiones
    commission_regular: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    commission_cash: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    commission_delivery: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_commissions: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        Computed("commission_regular + commission_cash + commission_delivery")
    )
    
    # Deducciones
    deduction_fuel: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    deduction_loan: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    deduction_shortage: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    deduction_other: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_deductions: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        Computed("deduction_fuel + deduction_loan + deduction_shortage + deduction_other")
    )
    
    # Neto (calculado)
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        Computed(
            "(commission_regular + commission_cash + commission_delivery) - "
            "(deduction_fuel + deduction_loan + deduction_shortage + deduction_other)"
        )
    )
    
    # Estado y pago
    status: Mapped[SettlementStatus] = mapped_column(default=SettlementStatus.PENDING)
    payment_method: Mapped[Optional[SettlementMethod]]
    paid_at: Mapped[Optional[datetime]]
    paid_by: Mapped[Optional[int]] = mapped_column(ForeignKey("app_user.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    collector: Mapped["Collector"] = relationship(back_populates="settlements")
    deductions: Mapped[List["SettlementDeduction"]] = relationship(
        back_populates="settlement", 
        cascade="all, delete-orphan"
    )
    payments: Mapped[List["SettlementPayment"]] = relationship(
        back_populates="settlement",
        cascade="all, delete-orphan"
    )
    paid_by_user: Mapped[Optional["AppUser"]] = relationship()
    
    __table_args__ = (
        UniqueConstraint("collector_id", "period_start", "period_end", name="uq_settlement_period"),
        Index("idx_settlement_collector", "collector_id"),
        Index("idx_settlement_period", "period_start", "period_end"),
        Index("idx_settlement_status", "status"),
    )


class SettlementDeduction(Base):
    """Detalle de deducciones individuales en una liquidación."""
    
    __tablename__ = "settlement_deduction"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    settlement_id: Mapped[int] = mapped_column(ForeignKey("settlement.id", ondelete="CASCADE"))
    
    deduction_type: Mapped[DeductionType]
    concept: Mapped[str] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    loan_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employee_loan.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    settlement: Mapped["Settlement"] = relationship(back_populates="deductions")
    loan: Mapped[Optional["EmployeeLoan"]] = relationship(back_populates="deductions")
    
    __table_args__ = (
        Index("idx_settlement_deduction_settlement", "settlement_id"),
    )


class SettlementPayment(Base):
    """Pagos incluidos en una liquidación para trazabilidad."""
    
    __tablename__ = "settlement_payment"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    settlement_id: Mapped[int] = mapped_column(ForeignKey("settlement.id", ondelete="CASCADE"))
    payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id"), unique=True)
    
    commission_type: Mapped[str] = mapped_column(String(20))  # regular, cash, delivery
    amount_collected: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    settlement: Mapped["Settlement"] = relationship(back_populates="payments")
    payment: Mapped["Payment"] = relationship()
    
    __table_args__ = (
        Index("idx_settlement_payment_settlement", "settlement_id"),
        Index("idx_settlement_payment_payment", "payment_id"),
    )
