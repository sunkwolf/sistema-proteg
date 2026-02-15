"""Pydantic schemas for the Notifications module."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# ── History ────────────────────────────────────────────────────────

class SentMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int | None
    phone: str
    message_type: str
    channel: str
    delivery_status: str
    external_message_id: str | None
    retry_count: int
    error_message: str | None
    target_payment_date: date | None
    days_before_due: int | None
    sent_by_user_id: int | None
    created_at: datetime
    sent_at: datetime | None
    delivered_at: datetime | None


class NotificationHistoryResponse(BaseModel):
    items: list[SentMessageResponse]
    total: int
    skip: int
    limit: int


# ── Send requests ─────────────────────────────────────────────────

class SendOverdueFilters(BaseModel):
    coverage: str | None = None
    holder: str | None = None
    payment_status: str | None = None


class SendOverdueRequest(BaseModel):
    filters: SendOverdueFilters = SendOverdueFilters()


class SendRemindersFilters(BaseModel):
    coverage: str | None = None
    payment_number: int | None = None


class SendRemindersRequest(BaseModel):
    filters: SendRemindersFilters = SendRemindersFilters()


class SendResultMessage(BaseModel):
    id: int
    policy_id: int | None
    phone: str
    status: str
    message_type: str
    channel: str


class SendResultResponse(BaseModel):
    queued_count: int
    skipped_count: int
    messages: list[SendResultMessage]


# ── Stats ──────────────────────────────────────────────────────────

class ChannelStats(BaseModel):
    queued: int = 0
    sent: int = 0
    delivered: int = 0
    read: int = 0
    failed: int = 0


class NotificationStatsResponse(BaseModel):
    total: int
    by_channel: dict[str, ChannelStats]
    by_message_type: dict[str, ChannelStats]
