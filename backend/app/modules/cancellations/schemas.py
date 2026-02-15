"""Pydantic schemas for the Cancellations module."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class CancellationCreate(BaseModel):
    policy_id: int
    reason: str | None = Field(None, max_length=255)
    code: str = Field(..., pattern=r"^C[1-5]$", max_length=45)
    payments_made: int = Field(0, ge=0)
    update_card: bool = True


class CancellationResponse(BaseModel):
    id: int
    policy_id: int
    cancellation_date: date
    reason: str | None = None
    code: str | None = None
    payments_made: int | None = None
    cancelled_by_user_id: int | None = None
    notification_sent_seller: bool
    notification_sent_collector: bool
    notification_sent_client: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CancellationListResponse(BaseModel):
    items: list[CancellationResponse]
    total: int
    skip: int
    limit: int
