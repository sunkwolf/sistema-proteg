"""Data access layer for renewals."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.endorsements import Renewal
from app.models.notifications import RenewalNotificationLog


class RenewalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Renewal CRUD ────────────────────────────────────────────────

    async def get_by_id(self, renewal_id: int) -> Renewal | None:
        result = await self.session.execute(
            select(Renewal).where(Renewal.id == renewal_id)
        )
        return result.scalar_one_or_none()

    async def list_renewals(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        old_policy_id: int | None = None,
    ) -> tuple[list[Renewal], int]:
        query = select(Renewal)
        count_query = select(func.count(Renewal.id))

        if status is not None:
            query = query.where(Renewal.status == status)
            count_query = count_query.where(Renewal.status == status)
        if old_policy_id is not None:
            query = query.where(Renewal.old_policy_id == old_policy_id)
            count_query = count_query.where(Renewal.old_policy_id == old_policy_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Renewal.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, renewal: Renewal) -> Renewal:
        self.session.add(renewal)
        await self.session.flush()
        await self.session.refresh(renewal)
        return renewal

    async def update(self, renewal: Renewal) -> Renewal:
        await self.session.flush()
        await self.session.refresh(renewal)
        return renewal

    async def get_renewal_by_old_policy(
        self, old_policy_id: int, status: str = "pending"
    ) -> Renewal | None:
        result = await self.session.execute(
            select(Renewal).where(
                Renewal.old_policy_id == old_policy_id,
                Renewal.status == status,
            )
        )
        return result.scalar_one_or_none()

    # ── Pending renewal detection ──────────────────────────────────

    async def get_policies_near_expiration(
        self,
        *,
        days_before: int = 30,
        days_after: int = 0,
        seller_id: int | None = None,
    ) -> list[dict]:
        """Find active policies expiring within the given window.

        days_before: policies expiring within the next N days
        days_after: policies already expired up to N days ago
        """
        today = date.today()
        start = today - timedelta(days=days_after)
        end = today + timedelta(days=days_before)

        query = (
            select(Policy)
            .where(
                Policy.expiration_date.isnot(None),
                Policy.expiration_date >= start,
                Policy.expiration_date <= end,
                Policy.status.notin_(["cancelled"]),
            )
            .order_by(Policy.expiration_date.asc())
        )

        if seller_id is not None:
            query = query.where(Policy.seller_id == seller_id)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ── Policy ─────────────────────────────────────────────────────

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    # ── Notification logs ──────────────────────────────────────────

    async def get_notification_logs(
        self, policy_id: int
    ) -> list[RenewalNotificationLog]:
        result = await self.session.execute(
            select(RenewalNotificationLog)
            .where(RenewalNotificationLog.policy_id == policy_id)
            .order_by(RenewalNotificationLog.sent_at.desc())
        )
        return list(result.scalars().all())

    async def create_notification_log(
        self, log: RenewalNotificationLog
    ) -> RenewalNotificationLog:
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log
