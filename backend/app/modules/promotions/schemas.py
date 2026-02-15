"""Pydantic schemas for the Promotions module."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Promotion ───────────────────────────────────────────────────────

class PromotionCreate(BaseModel):
    name: str = Field(max_length=100)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class PromotionUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class PromotionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    status: str
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime


class PromotionListResponse(BaseModel):
    items: list[PromotionResponse]
    total: int
    skip: int
    limit: int


# ── Promotion Rule ──────────────────────────────────────────────────

class PromotionRuleCreate(BaseModel):
    discount_type: str
    discount_value: Decimal = Field(ge=0)
    applies_to_payment_number: int | None = None
    min_payments: int | None = None
    max_payments: int | None = None
    coverage_ids: list[int] | None = None
    vehicle_types: list[str] | None = None
    requires_referral: bool = False
    description: str | None = None


class PromotionRuleUpdate(BaseModel):
    discount_type: str | None = None
    discount_value: Decimal | None = Field(None, ge=0)
    applies_to_payment_number: int | None = None
    min_payments: int | None = None
    max_payments: int | None = None
    coverage_ids: list[int] | None = None
    vehicle_types: list[str] | None = None
    requires_referral: bool | None = None
    description: str | None = None


class PromotionRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    promotion_id: int
    discount_type: str
    discount_value: Decimal
    applies_to_payment_number: int | None
    min_payments: int | None
    max_payments: int | None
    coverage_ids: Any
    vehicle_types: Any
    requires_referral: bool
    description: str | None
    created_at: datetime


# ── Promotion Application ──────────────────────────────────────────

class PromotionApplyRequest(BaseModel):
    policy_id: int
    referrer_policy_id: int | None = None
    comments: str | None = None


class PromotionApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    promotion_id: int
    promotion_rule_id: int
    policy_id: int
    referrer_policy_id: int | None
    discount_applied: Decimal
    applied_by_user_id: int | None
    comments: str | None
    applied_at: datetime


class PromotionApplicationListResponse(BaseModel):
    items: list[PromotionApplicationResponse]
    total: int
