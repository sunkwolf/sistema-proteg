"""Pydantic schemas for the Authorization module."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


# ── Payment Proposals ────────────────────────────────────────────────

class ProposalCreate(BaseModel):
    original_payment_id: int
    policy_id: int
    collector_id: int = Field(..., description="Employee ID of the collector")
    receipt_number: str | None = Field(None, max_length=10)
    actual_date: date
    amount: Decimal = Field(..., gt=0)
    payment_method: Literal[
        "cash", "deposit", "transfer", "crucero", "konfio", "terminal_banorte"
    ]
    comments: str | None = None
    geo_latitude: float | None = None
    geo_longitude: float | None = None
    evidence_photo_url: str | None = Field(None, max_length=500)


class ProposalReview(BaseModel):
    review_notes: str | None = None


class ProposalResponse(BaseModel):
    id: int
    original_payment_id: int
    policy_id: int
    seller_id: int | None = None
    collector_id: int | None = None
    payment_number: int
    receipt_number: str | None = None
    actual_date: date | None = None
    amount: Decimal | None = None
    payment_method: str | None = None
    comments: str | None = None
    payment_status: str
    draft_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProposalListResponse(BaseModel):
    items: list[ProposalResponse]
    total: int
    skip: int
    limit: int


# ── Approval Requests (generic) ──────────────────────────────────────

class ApprovalRequestResponse(BaseModel):
    id: int
    request_type: str
    status: str
    entity_type: str
    entity_id: int | None = None
    payload: dict
    submitted_by_user_id: int
    reviewed_by_user_id: int | None = None
    review_notes: str | None = None
    submitted_at: datetime
    reviewed_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalReview(BaseModel):
    review_notes: str | None = None
