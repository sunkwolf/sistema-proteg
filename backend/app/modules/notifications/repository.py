"""Data access layer for notifications (SentMessage history, stats)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notifications import SentMessage


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── History ────────────────────────────────────────────────────

    async def list_messages(
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
    ) -> tuple[list[SentMessage], int]:
        query = select(SentMessage)
        count_query = select(func.count(SentMessage.id))

        filters = []
        if policy_id is not None:
            filters.append(SentMessage.policy_id == policy_id)
        if message_type is not None:
            filters.append(SentMessage.message_type == message_type)
        if channel is not None:
            filters.append(SentMessage.channel == channel)
        if delivery_status is not None:
            filters.append(SentMessage.delivery_status == delivery_status)
        if date_from is not None:
            filters.append(SentMessage.created_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to is not None:
            filters.append(SentMessage.created_at <= datetime.combine(date_to, datetime.max.time()))

        for f in filters:
            query = query.where(f)
            count_query = count_query.where(f)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(SentMessage.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    # ── Frequency checks ──────────────────────────────────────────

    async def count_recent_messages(
        self,
        policy_id: int,
        message_type: str,
        days: int = 7,
    ) -> int:
        """Count messages sent to a policy in the last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await self.session.execute(
            select(func.count(SentMessage.id)).where(
                SentMessage.policy_id == policy_id,
                SentMessage.message_type == message_type,
                SentMessage.created_at >= cutoff,
            )
        )
        return result.scalar_one()

    async def get_last_message_date(
        self,
        policy_id: int,
        message_type: str,
    ) -> datetime | None:
        """Get the date of the last message sent to a policy."""
        result = await self.session.execute(
            select(SentMessage.created_at)
            .where(
                SentMessage.policy_id == policy_id,
                SentMessage.message_type == message_type,
            )
            .order_by(SentMessage.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def count_messages_for_target_date(
        self,
        policy_id: int,
        target_date: date,
    ) -> int:
        """Count reminder messages for a specific target payment date."""
        result = await self.session.execute(
            select(func.count(SentMessage.id)).where(
                SentMessage.policy_id == policy_id,
                SentMessage.message_type == "reminder",
                SentMessage.target_payment_date == target_date,
            )
        )
        return result.scalar_one()

    # ── Create ─────────────────────────────────────────────────────

    async def create(self, msg: SentMessage) -> SentMessage:
        self.session.add(msg)
        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    # ── Stats ──────────────────────────────────────────────────────

    async def get_stats(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        channel: str | None = None,
        message_type: str | None = None,
    ) -> list[dict]:
        """Return rows of (channel, message_type, delivery_status, count)."""
        query = select(
            SentMessage.channel,
            SentMessage.message_type,
            SentMessage.delivery_status,
            func.count(SentMessage.id).label("cnt"),
        ).group_by(
            SentMessage.channel,
            SentMessage.message_type,
            SentMessage.delivery_status,
        )

        if date_from is not None:
            query = query.where(
                SentMessage.created_at >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to is not None:
            query = query.where(
                SentMessage.created_at <= datetime.combine(date_to, datetime.max.time())
            )
        if channel is not None:
            query = query.where(SentMessage.channel == channel)
        if message_type is not None:
            query = query.where(SentMessage.message_type == message_type)

        result = await self.session.execute(query)
        rows = result.all()
        return [
            {
                "channel": r[0].value if hasattr(r[0], "value") else str(r[0]),
                "message_type": r[1].value if hasattr(r[1], "value") else str(r[1]),
                "delivery_status": r[2].value if hasattr(r[2], "value") else str(r[2]),
                "count": r[3],
            }
            for r in rows
        ]
