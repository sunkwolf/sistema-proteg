"""Pydantic schemas for the Renewals module."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


# ── Request schemas ─────────────────────────────────────────────────

class RenewalCreate(BaseModel):
    old_policy_id: int
    new_policy_id: int | None = None
    renewal_date: date
    comments: str | None = None


class RenewalComplete(BaseModel):
    new_policy_id: int
    comments: str | None = None


# ── Response schemas ────────────────────────────────────────────────

class RenewalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    old_policy_id: int
    new_policy_id: int | None
    renewal_date: date
    status: str
    comments: str | None
    created_at: datetime
    updated_at: datetime


class RenewalListResponse(BaseModel):
    items: list[RenewalResponse]
    total: int
    skip: int
    limit: int


class PendingRenewalPolicy(BaseModel):
    """A policy approaching or past its expiration date."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_number: str | None
    client_id: int | None
    seller_id: int | None
    expiration_date: date | None
    status: str
    days_until_expiration: int


class PendingRenewalListResponse(BaseModel):
    items: list[PendingRenewalPolicy]
    total: int


class RenewalNotificationLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int
    notification_type: str
    sent_at: datetime
    sent_by: str
