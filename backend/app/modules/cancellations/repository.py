"""Data access layer for cancellations."""

from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Cancellation
from app.models.business import Policy
from app.models.collections import Card
from app.models.payments import Payment


class CancellationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Cancellation CRUD ─────────────────────────────────────────────

    async def get_by_id(self, cancellation_id: int) -> Cancellation | None:
        result = await self.session.execute(
            select(Cancellation).where(Cancellation.id == cancellation_id)
        )
        return result.scalar_one_or_none()

    async def list_cancellations(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        code: str | None = None,
        policy_id: int | None = None,
    ) -> tuple[list[Cancellation], int]:
        query = select(Cancellation)
        count_query = select(func.count(Cancellation.id))

        if code is not None:
            query = query.where(Cancellation.code == code)
            count_query = count_query.where(Cancellation.code == code)
        if policy_id is not None:
            query = query.where(Cancellation.policy_id == policy_id)
            count_query = count_query.where(Cancellation.policy_id == policy_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Cancellation.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, cancellation: Cancellation) -> Cancellation:
        self.session.add(cancellation)
        await self.session.flush()
        await self.session.refresh(cancellation)
        return cancellation

    async def delete(self, cancellation: Cancellation) -> None:
        await self.session.delete(cancellation)
        await self.session.flush()

    async def update(self, cancellation: Cancellation) -> Cancellation:
        await self.session.flush()
        await self.session.refresh(cancellation)
        return cancellation

    # ── Policy ────────────────────────────────────────────────────────

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def update_policy_status(self, policy_id: int, status: str) -> None:
        await self.session.execute(
            update(Policy).where(Policy.id == policy_id).values(status=status)
        )
        await self.session.flush()

    # ── Payments ──────────────────────────────────────────────────────

    async def cancel_payments_after(
        self, policy_id: int, payments_made: int
    ) -> int:
        """Cancel all payments with payment_number > payments_made."""
        result = await self.session.execute(
            update(Payment)
            .where(
                Payment.policy_id == policy_id,
                Payment.payment_number > payments_made,
                Payment.status != "paid",
                Payment.status != "cancelled",
            )
            .values(status="cancelled")
        )
        await self.session.flush()
        return result.rowcount  # type: ignore[return-value]

    async def restore_payments_after(
        self, policy_id: int, payments_made: int
    ) -> int:
        """Restore cancelled payments with payment_number > payments_made to pending."""
        result = await self.session.execute(
            update(Payment)
            .where(
                Payment.policy_id == policy_id,
                Payment.payment_number > payments_made,
                Payment.status == "cancelled",
            )
            .values(status="pending")
        )
        await self.session.flush()
        return result.rowcount  # type: ignore[return-value]

    # ── Card ──────────────────────────────────────────────────────────

    async def get_card_by_policy(self, policy_id: int) -> Card | None:
        result = await self.session.execute(
            select(Card).where(Card.policy_id == policy_id)
        )
        return result.scalar_one_or_none()

    async def archive_card(self, policy_id: int) -> None:
        card = await self.get_card_by_policy(policy_id)
        if card is not None:
            card.current_holder = "ARCHIVO"
            card.status = "cancelled"
            await self.session.flush()

    async def restore_card(self, policy_id: int) -> None:
        card = await self.get_card_by_policy(policy_id)
        if card is not None:
            card.current_holder = "OFICINA"
            card.status = "active"
            await self.session.flush()
