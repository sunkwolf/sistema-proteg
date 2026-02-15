"""Pydantic schemas for the Policies module."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


# ── Nested summaries for response ────────────────────────────────────

class ClientSummary(BaseModel):
    id: int
    full_name: str


class VehicleSummary(BaseModel):
    id: int
    brand: str
    model_type: str | None = None
    model_year: str | None = None


class CoverageSummary(BaseModel):
    id: int
    name: str
    vehicle_type: str


class SellerSummary(BaseModel):
    id: int
    code_name: str
    full_name: str


class PaymentsSummary(BaseModel):
    total_payments: int
    first_payment_amount: Decimal | None = None
    monthly_amount: Decimal | None = None


# ── Create / Update ──────────────────────────────────────────────────

class PolicyCreate(BaseModel):
    client_id: int
    vehicle_id: int
    coverage_id: int
    seller_id: int | None = None
    service_type: Literal["private", "commercial"] | None = None
    contract_folio: int | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    payment_plan: Literal["cash", "cash_2_installments", "monthly_7"] | None = None
    prima_total: Decimal | None = Field(None, ge=0)
    tow_services_available: int = Field(0, ge=0)
    contract_image_path: str | None = Field(None, max_length=500)
    quote_external_id: str | None = Field(None, max_length=50)
    comments: str | None = None
    promotion_id: int | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> PolicyCreate:
        if self.effective_date and self.expiration_date:
            if self.expiration_date < self.effective_date:
                raise ValueError(
                    "expiration_date debe ser igual o posterior a effective_date"
                )
        return self


class PolicyUpdate(BaseModel):
    service_type: Literal["private", "commercial"] | None = None
    contract_folio: int | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    tow_services_available: int | None = Field(None, ge=0)
    contract_image_path: str | None = Field(None, max_length=500)
    comments: str | None = None
    has_fraud_observation: bool | None = None
    has_payment_issues: bool | None = None


class ChangeSeller(BaseModel):
    seller_id: int


# ── Response ─────────────────────────────────────────────────────────

class PolicyResponse(BaseModel):
    id: int
    folio: int
    renewal_folio: int | None = None
    client: ClientSummary
    vehicle: VehicleSummary
    coverage: CoverageSummary
    seller: SellerSummary | None = None
    service_type: str | None = None
    contract_folio: int | None = None
    effective_date: date | None = None
    expiration_date: date | None = None
    sale_date: date | None = None
    elaboration_date: date | None = None
    status: str
    payment_plan: str | None = None
    prima_total: Decimal | None = None
    tow_services_available: int
    comments: str | None = None
    has_fraud_observation: bool
    has_payment_issues: bool
    contract_image_path: str | None = None
    quote_external_id: str | None = None
    payments_summary: PaymentsSummary | None = None
    created_at: datetime
    updated_at: datetime


class PolicyListResponse(BaseModel):
    items: list[PolicyResponse]
    total: int
    skip: int
    limit: int
