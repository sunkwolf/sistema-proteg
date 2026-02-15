"""Pydantic schemas for the Receipts module."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ── Batch Creation ────────────────────────────────────────────────────

class ReceiptBatchCreate(BaseModel):
    prefix: str = Field(..., min_length=1, max_length=1, pattern=r"^[A-Z]$")
    start: int = Field(..., ge=1)
    end: int = Field(..., ge=1)

    @field_validator("end")
    @classmethod
    def end_gte_start(cls, v: int, info) -> int:
        start = info.data.get("start")
        if start is not None and v < start:
            raise ValueError("end debe ser >= start")
        return v


class ReceiptBatchResponse(BaseModel):
    created: int
    skipped: int
    receipt_numbers: list[str]


# ── Assignment ────────────────────────────────────────────────────────

class ReceiptAssign(BaseModel):
    collector_id: int
    receipt_ids: list[int] = Field(..., min_length=1)


class ReceiptAssignResponse(BaseModel):
    assigned: int
    truncated: int
    message: str | None = None


# ── Verification ──────────────────────────────────────────────────────

class ReceiptVerify(BaseModel):
    receipt_number: str = Field(..., pattern=r"^[A-Z]\d{4}$")
    collector_id: int
    policy_id: int
    payment_id: int


class ReceiptVerifyResponse(BaseModel):
    valid: bool
    receipt: ReceiptResponse | None = None
    skipped_receipts: list[str] = []
    warning: str | None = None


# ── CRUD Responses ────────────────────────────────────────────────────

class ReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    policy_id: int | None = None
    collector_id: int | None = None
    payment_id: int | None = None
    assignment_date: date | None = None
    usage_date: date | None = None
    delivery_date: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReceiptListResponse(BaseModel):
    items: list[ReceiptResponse]
    total: int
    skip: int
    limit: int


# Fix forward reference
ReceiptVerifyResponse.model_rebuild()
