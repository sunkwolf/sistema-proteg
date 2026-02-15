"""Pydantic schemas for the Coverages module."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.modules.vehicles.schemas import VALID_VEHICLE_KEYS, VEHICLE_KEY_TYPE_MAP

# AMPLIA (comprehensive) only available for these keys
AMPLIA_ELIGIBLE_KEYS = {101, 103, 105}


class CoverageCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    vehicle_type: str = Field(..., max_length=50)
    vehicle_key: int
    service_type: Literal["private", "commercial"]
    category: Literal["liability", "comprehensive", "platform"] = "liability"
    cylinder_capacity: str | None = Field(None, max_length=20)
    credit_price: Decimal = Field(..., ge=0)
    initial_payment: Decimal = Field(..., ge=0)
    cash_price: Decimal = Field(..., ge=0)
    tow_services_included: int = Field(0, ge=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_coverage_rules(self) -> CoverageCreate:
        if self.vehicle_key not in VALID_VEHICLE_KEYS:
            raise ValueError(
                f"vehicle_key debe ser uno de: {sorted(VALID_VEHICLE_KEYS)}"
            )
        # Validate vehicle_type matches key
        expected = VEHICLE_KEY_TYPE_MAP[self.vehicle_key]
        if self.vehicle_type != expected:
            raise ValueError(
                f"vehicle_key {self.vehicle_key} requiere vehicle_type='{expected}', "
                f"se recibio '{self.vehicle_type}'"
            )
        # Comprehensive only for eligible keys
        if self.category == "comprehensive" and self.vehicle_key not in AMPLIA_ELIGIBLE_KEYS:
            raise ValueError(
                f"Cobertura AMPLIA solo disponible para claves {sorted(AMPLIA_ELIGIBLE_KEYS)}"
            )
        return self


class CoverageUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    credit_price: Decimal | None = Field(None, ge=0)
    initial_payment: Decimal | None = Field(None, ge=0)
    cash_price: Decimal | None = Field(None, ge=0)
    tow_services_included: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CoverageResponse(BaseModel):
    id: int
    name: str
    vehicle_type: str
    vehicle_key: int
    service_type: str
    category: str
    cylinder_capacity: str | None = None
    credit_price: Decimal
    initial_payment: Decimal
    cash_price: Decimal
    tow_services_included: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CoverageListResponse(BaseModel):
    items: list[CoverageResponse]
    total: int
    skip: int
    limit: int


class PaymentScheme(BaseModel):
    total: Decimal
    first_payment_editable: bool = False
    payments: list[dict]


class CoveragePaymentSchemesResponse(BaseModel):
    coverage: CoverageResponse
    schemes: dict[str, PaymentScheme]
