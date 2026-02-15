"""Pydantic schemas for the Payments module."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ── Create / Update ──────────────────────────────────────────────────

class PaymentCreate(BaseModel):
    """Manual payment creation (rare, typically auto-created by policy)."""
    policy_id: int
    payment_number: int = Field(..., ge=1)
    amount: Decimal = Field(..., ge=0)
    due_date: date | None = None
    seller_id: int | None = None
    comments: str | None = None


class PaymentUpdate(BaseModel):
    """Full payment revision (only Cobranza department)."""
    receipt_number: str | None = Field(None, max_length=10)
    actual_date: date | None = None
    amount: Decimal | None = Field(None, ge=0)
    payment_method: Literal[
        "cash", "deposit", "transfer", "crucero", "konfio", "terminal_banorte"
    ] | None = None
    collector_id: int | None = None
    office_delivery_status: Literal["pending", "delivered"] | None = None
    office_delivery_date: date | None = None
    status: Literal["pending", "paid", "late", "overdue", "cancelled"] | None = None
    policy_delivered: bool | None = None
    comments: str | None = None

    @model_validator(mode="after")
    def validate_delivery_consistency(self) -> PaymentUpdate:
        # If delivery date set, status must be delivered
        if self.office_delivery_date and self.office_delivery_status != "delivered":
            raise ValueError(
                "Si office_delivery_date tiene valor, office_delivery_status debe ser 'delivered'"
            )
        # If delivery status is delivered, date is required
        if self.office_delivery_status == "delivered" and not self.office_delivery_date:
            raise ValueError(
                "Si office_delivery_status es 'delivered', office_delivery_date es obligatoria"
            )
        return self

    @model_validator(mode="after")
    def validate_actual_date_requires_paid(self) -> PaymentUpdate:
        if self.actual_date and self.status and self.status != "paid":
            raise ValueError(
                "Si actual_date tiene valor, status debe ser 'paid'"
            )
        return self


class PartialPayment(BaseModel):
    partial_amount: Decimal = Field(..., gt=0)
    receipt_number: str | None = Field(None, max_length=10)
    payment_method: Literal[
        "cash", "deposit", "transfer", "crucero", "konfio", "terminal_banorte"
    ] | None = None
    collector_id: int | None = None


class RevertPayment(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class MarkProblem(BaseModel):
    comments: str = Field(..., min_length=1, max_length=500)


class CashToInstallments(BaseModel):
    """Convert remaining unpaid cash payments into monthly installments."""
    policy_id: int
    installments: int = Field(..., ge=2, le=12)


# ── Response ─────────────────────────────────────────────────────────

class PaymentResponse(BaseModel):
    id: int
    policy_id: int
    seller_id: int | None = None
    collector_id: int | None = None
    user_id: int | None = None
    payment_number: int
    receipt_number: str | None = None
    due_date: date | None = None
    actual_date: date | None = None
    amount: Decimal | None = None
    payment_method: str | None = None
    office_delivery_status: str | None = None
    office_delivery_date: date | None = None
    policy_delivered: bool | None = None
    comments: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    items: list[PaymentResponse]
    total: int
    skip: int
    limit: int
