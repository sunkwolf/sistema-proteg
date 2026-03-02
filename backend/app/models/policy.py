"""
Policy, Vehicle, Coverage, Seller, Collector models.

Design decision: policy.status is STORED but treated as a CACHE.
The real status is always computed from payments + dates.
A trigger on payment changes recalculates it.
"""
from datetime import date, datetime
from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Date, Integer, Numeric, Boolean, ForeignKey,
    DateTime, func, BigInteger, text, Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


# ── Enums ──────────────────────────────────────────────────────────────────

class PolicyStatus(str, PyEnum):
    ACTIVE = "active"
    PENDING = "pending"
    MOROSA = "morosa"
    PRE_EFFECTIVE = "pre_effective"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    NO_STATUS = "no_status"


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    # late/overdue are COMPUTED, not stored
    LATE = "late"
    OVERDUE = "overdue"


class PaymentMethod(str, PyEnum):
    CASH = "cash"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    CRUCERO = "crucero"
    KONFIO = "konfio"
    TERMINAL_BANORTE = "terminal_banorte"


class CardStatus(str, PyEnum):
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    CANCELLED = "cancelled"
    RECOVERY = "recovery"


class EntityStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class SellerClass(str, PyEnum):
    SELLER = "seller"
    COLLABORATOR = "collaborator"


# ── Models ─────────────────────────────────────────────────────────────────

class Seller(Base, TimestampMixin):
    __tablename__ = "seller"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_name: Mapped[str] = mapped_column(String(50), unique=True)
    full_name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(SAEnum('active','inactive', name='entity_status_type', create_type=False), server_default="active")
    seller_class: Mapped[str] = mapped_column("class", String(20), server_default="collaborator")
    sales_target: Mapped[Optional[int]] = mapped_column(Integer)


class Collector(Base, TimestampMixin):
    __tablename__ = "collector"

    id: Mapped[int] = mapped_column(primary_key=True)
    code_name: Mapped[str] = mapped_column(String(50), unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    receipt_limit: Mapped[int] = mapped_column(Integer, server_default="50")
    status: Mapped[str] = mapped_column(SAEnum('active','inactive', name='entity_status_type', create_type=False), server_default="active")


class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(45))
    model_type: Mapped[Optional[str]] = mapped_column(String(45))
    model_year: Mapped[Optional[str]] = mapped_column(String(10))
    color: Mapped[Optional[str]] = mapped_column(String(45))
    vehicle_key: Mapped[Optional[int]] = mapped_column(Integer)
    serial_number: Mapped[Optional[str]] = mapped_column(String(45))
    plates: Mapped[Optional[str]] = mapped_column(String(20))
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(20))

    @property
    def description(self) -> str:
        parts = [self.brand or ""]
        if self.model_type:
            parts.append(self.model_type)
        if self.model_year:
            parts.append(self.model_year)
        return " ".join(parts).strip()


class Coverage(Base, TimestampMixin):
    __tablename__ = "coverage"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    vehicle_type: Mapped[str] = mapped_column(String(50))
    vehicle_key: Mapped[int] = mapped_column(Integer)
    service_type: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(20), server_default="liability")
    credit_price: Mapped[float] = mapped_column(Numeric(12, 2))
    initial_payment: Mapped[float] = mapped_column(Numeric(12, 2))
    cash_price: Mapped[float] = mapped_column(Numeric(12, 2))
    tow_services_included: Mapped[int] = mapped_column(Integer, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")


class Policy(Base, TimestampMixin):
    __tablename__ = "policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    folio: Mapped[int] = mapped_column(Integer, unique=True)
    renewal_folio: Mapped[Optional[int]] = mapped_column(Integer)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("client.id"))
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("vehicle.id"))
    coverage_id: Mapped[int] = mapped_column(Integer, ForeignKey("coverage.id"))
    seller_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("seller.id"))
    service_type: Mapped[Optional[str]] = mapped_column(String(20))
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date)
    elaboration_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(SAEnum('active','pending','morosa','pre_effective','expired','cancelled','suspended','no_status', name='policy_status_type', create_type=False), server_default="active")
    payment_plan: Mapped[Optional[str]] = mapped_column(SAEnum('cash','cash_2_installments','monthly_7', name='payment_plan_type', create_type=False))
    prima_total: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    comments: Mapped[Optional[str]] = mapped_column(String)

    # Relationships
    client: Mapped["Client"] = relationship(lazy="joined")
    vehicle: Mapped["Vehicle"] = relationship(lazy="joined")
    coverage: Mapped["Coverage"] = relationship(lazy="joined")
    seller: Mapped[Optional["Seller"]] = relationship(lazy="joined")
    payments: Mapped[List["Payment"]] = relationship(
        back_populates="policy", lazy="selectin",
        order_by="Payment.payment_number",
    )

    @property
    def computed_status(self) -> str:
        """Compute real policy status from payments and dates."""
        from datetime import date as dt_date
        today = dt_date.today()

        # Explicitly cancelled/suspended
        if self.status in ("cancelled", "suspended"):
            return self.status

        # Expired by date
        if self.expiration_date and today > self.expiration_date:
            return PolicyStatus.EXPIRED

        # Pre-effective
        if self.effective_date and today < self.effective_date:
            return PolicyStatus.PRE_EFFECTIVE

        # Check payments
        if not self.payments:
            return PolicyStatus.PENDING

        has_overdue = any(
            p.status == "pending" and p.due_date and p.due_date < today
            for p in self.payments
        )
        if has_overdue:
            return PolicyStatus.MOROSA

        all_paid = all(
            p.status in ("paid", "cancelled")
            for p in self.payments
        )
        if all_paid:
            return PolicyStatus.ACTIVE

        return PolicyStatus.ACTIVE


class Payment(Base, TimestampMixin):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(Integer, ForeignKey("policy.id"))
    seller_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("seller.id"))
    collector_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("collector.id"))
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("app_user.id"))
    payment_number: Mapped[int] = mapped_column(Integer)
    receipt_number: Mapped[Optional[str]] = mapped_column(String(10))
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_date: Mapped[Optional[date]] = mapped_column(Date)
    amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[Optional[str]] = mapped_column(SAEnum('cash','deposit','transfer','crucero','konfio','terminal_banorte', name='payment_method_type', create_type=False))
    office_delivery_status: Mapped[Optional[str]] = mapped_column(SAEnum('pending','delivered', name='office_delivery_type', create_type=False))
    office_delivery_date: Mapped[Optional[date]] = mapped_column(Date)
    policy_delivered: Mapped[Optional[bool]] = mapped_column(Boolean)
    comments: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(SAEnum('pending','paid','late','overdue','cancelled', name='payment_status_type', create_type=False), server_default="pending")

    policy: Mapped["Policy"] = relationship(back_populates="payments")
    collector: Mapped[Optional["Collector"]] = relationship(lazy="joined")

    @property
    def computed_status(self) -> str:
        """Real status: paid/cancelled are facts; pending is computed."""
        from datetime import date as dt_date
        if self.status in ("paid", "cancelled"):
            return self.status
        today = dt_date.today()
        if self.due_date and self.due_date < today:
            days_overdue = (today - self.due_date).days
            return "overdue" if days_overdue > 5 else "late"
        return "pending"

    @property
    def days_overdue(self) -> int:
        from datetime import date as dt_date
        if self.status == "paid" or not self.due_date:
            return 0
        today = dt_date.today()
        diff = (today - self.due_date).days
        return max(0, diff)


class Card(Base, TimestampMixin):
    __tablename__ = "card"

    id: Mapped[int] = mapped_column(primary_key=True)
    policy_id: Mapped[int] = mapped_column(Integer, ForeignKey("policy.id"))
    current_holder: Mapped[str] = mapped_column(String(50))
    assignment_date: Mapped[date] = mapped_column(Date)
    seller_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("seller.id"))
    status: Mapped[str] = mapped_column(SAEnum('active','paid_off','cancelled','recovery', name='card_status_type', create_type=False), server_default="active")

    policy: Mapped["Policy"] = relationship(lazy="joined")


# Need to import Client for relationship resolution
from .client import Client  # noqa: E402
