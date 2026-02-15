"""Pydantic schemas for the Collections (Cards/Cobranza) module."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Card ──────────────────────────────────────────────────────────────

class CardResponse(BaseModel):
    id: int
    policy_id: int
    current_holder: str
    assignment_date: date
    seller_id: int | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CardListResponse(BaseModel):
    items: list[CardResponse]
    total: int
    skip: int
    limit: int


class CardReassign(BaseModel):
    assigned_to: str = Field(..., min_length=1, max_length=50)
    zone: str | None = Field(None, max_length=50)
    route: str | None = Field(None, max_length=50)
    observations: str | None = None


# ── Collection Assignment ─────────────────────────────────────────────

class AssignmentResponse(BaseModel):
    id: int
    card_id: int
    policy_id: int
    assigned_to: str
    zone: str | None = None
    route: str | None = None
    assignment_date: date
    observations: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Visit Notices ─────────────────────────────────────────────────────

class VisitNoticeCreate(BaseModel):
    card_id: int | None = None
    policy_id: int
    visit_date: date
    comments: str | None = None
    payment_id: int | None = None
    notice_number: int | None = None


class VisitNoticeResponse(BaseModel):
    id: int
    card_id: int | None = None
    policy_id: int
    visit_date: date
    comments: str | None = None
    payment_id: int | None = None
    notice_number: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class VisitNoticeListResponse(BaseModel):
    items: list[VisitNoticeResponse]
    total: int
    skip: int
    limit: int
