"""Business logic for notifications — send overdue, reminders, history, stats."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import SentMessage
from app.modules.notifications.channels.whatsapp import normalize_phone
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    ChannelStats,
    NotificationHistoryResponse,
    NotificationStatsResponse,
    SendResultMessage,
    SendResultResponse,
    SentMessageResponse,
)

# Frequency rules for overdue messages
MAX_OVERDUE_PER_WEEK = 2
MIN_DAYS_BETWEEN_OVERDUE = 3
MIN_LATE_DAYS_FIRST = 5
MIN_LATE_DAYS_OTHER = 3

# Frequency rules for reminders
MAX_REMINDERS_PER_TARGET = 2


class NotificationService:
    def __init__(self, session: AsyncSession):
        self.repo = NotificationRepository(session)

    # ── History ────────────────────────────────────────────────────

    async def list_history(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        message_type: str | None = None,
        channel: str | None = None,
        delivery_status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> NotificationHistoryResponse:
        items, total = await self.repo.list_messages(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            message_type=message_type,
            channel=channel,
            delivery_status=delivery_status,
            date_from=date_from,
            date_to=date_to,
        )
        return NotificationHistoryResponse(
            items=[_msg_to_response(m) for m in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    # ── Send overdue ───────────────────────────────────────────────

    async def enqueue_overdue(
        self,
        user_id: int | None = None,
    ) -> SendResultResponse:
        """Enqueue overdue notifications.

        The actual payment queries and phone lookup will be integrated
        when the full payment + client repositories are wired.
        For now, this creates the infrastructure for the queue pattern.
        """
        # TODO: Query payments with late/overdue status, join to client for phone.
        # For each qualifying payment:
        #   1. Check frequency: max 2/week, min 3 days apart
        #   2. Check late days: >=5 for payment 1, >=3 for others
        #   3. Normalize phone
        #   4. Create SentMessage with status=queued
        #   5. Celery worker will pick up and send via WhatsApp
        return SendResultResponse(queued_count=0, skipped_count=0, messages=[])

    # ── Send reminders ─────────────────────────────────────────────

    async def enqueue_reminders(
        self,
        user_id: int | None = None,
    ) -> SendResultResponse:
        """Enqueue reminder notifications for upcoming payments.

        The actual payment queries will be integrated when full payment
        + client repositories are wired.
        """
        # TODO: Query upcoming payments (within 7 days), join to client for phone.
        # For each qualifying payment:
        #   1. Check frequency: max 2 per (folio, target_date)
        #   2. Apply reminder type logic (PREVIO/VENCIMIENTO/URGENTE)
        #   3. Normalize phone
        #   4. Create SentMessage with status=queued, target_payment_date, days_before_due
        return SendResultResponse(queued_count=0, skipped_count=0, messages=[])

    # ── Frequency helpers ──────────────────────────────────────────

    async def can_send_overdue(self, policy_id: int) -> bool:
        """Check if we can send another overdue message to this policy."""
        count = await self.repo.count_recent_messages(policy_id, "overdue", days=7)
        if count >= MAX_OVERDUE_PER_WEEK:
            return False

        last_date = await self.repo.get_last_message_date(policy_id, "overdue")
        if last_date is not None:
            days_since = (datetime.utcnow() - last_date).days
            if days_since < MIN_DAYS_BETWEEN_OVERDUE:
                return False

        return True

    async def can_send_reminder(
        self, policy_id: int, target_date: date, days_remaining: int
    ) -> bool:
        """Check if we can send a reminder for this payment date."""
        count = await self.repo.count_messages_for_target_date(policy_id, target_date)
        if count >= MAX_REMINDERS_PER_TARGET:
            return False

        if count == 0:
            return days_remaining in (5, 4, 3, 0)

        if count == 1:
            last_date = await self.repo.get_last_message_date(policy_id, "reminder")
            if last_date is not None:
                days_since = (datetime.utcnow() - last_date).days
                if days_since >= 3 and days_remaining == 0:
                    return True
            return False

        return False

    # ── Queue a single message ─────────────────────────────────────

    async def queue_message(
        self,
        *,
        policy_id: int | None,
        phone: str,
        message_type: str,
        channel: str = "whatsapp",
        target_payment_date: date | None = None,
        days_before_due: int | None = None,
        user_id: int | None = None,
    ) -> SentMessage:
        """Create a queued message for the async worker to send."""
        msg = SentMessage(
            policy_id=policy_id,
            phone=phone,
            message_type=message_type,
            channel=channel,
            delivery_status="queued",
            target_payment_date=target_payment_date,
            days_before_due=days_before_due,
            sent_by_user_id=user_id,
        )
        return await self.repo.create(msg)

    # ── Stats ──────────────────────────────────────────────────────

    async def get_stats(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        channel: str | None = None,
        message_type: str | None = None,
    ) -> NotificationStatsResponse:
        rows = await self.repo.get_stats(
            date_from=date_from,
            date_to=date_to,
            channel=channel,
            message_type=message_type,
        )

        total = sum(r["count"] for r in rows)
        by_channel: dict[str, ChannelStats] = defaultdict(ChannelStats)
        by_type: dict[str, ChannelStats] = defaultdict(ChannelStats)

        for r in rows:
            ch = r["channel"]
            mt = r["message_type"]
            ds = r["delivery_status"]
            cnt = r["count"]

            if hasattr(by_channel[ch], ds):
                setattr(by_channel[ch], ds, getattr(by_channel[ch], ds) + cnt)
            if hasattr(by_type[mt], ds):
                setattr(by_type[mt], ds, getattr(by_type[mt], ds) + cnt)

        return NotificationStatsResponse(
            total=total,
            by_channel=dict(by_channel),
            by_message_type=dict(by_type),
        )


# ── Helpers ────────────────────────────────────────────────────────


def _msg_to_response(msg: SentMessage) -> SentMessageResponse:
    mt = msg.message_type
    if hasattr(mt, "value"):
        mt = mt.value
    ch = msg.channel
    if hasattr(ch, "value"):
        ch = ch.value
    ds = msg.delivery_status
    if hasattr(ds, "value"):
        ds = ds.value
    return SentMessageResponse(
        id=msg.id,
        policy_id=msg.policy_id,
        phone=msg.phone,
        message_type=mt,
        channel=ch,
        delivery_status=ds,
        external_message_id=msg.external_message_id,
        retry_count=msg.retry_count,
        error_message=msg.error_message,
        target_payment_date=msg.target_payment_date,
        days_before_due=msg.days_before_due,
        sent_by_user_id=msg.sent_by_user_id,
        created_at=msg.created_at,
        sent_at=msg.sent_at,
        delivered_at=msg.delivered_at,
    )
