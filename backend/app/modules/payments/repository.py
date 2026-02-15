"""Data access layer for payments."""

from __future__ import annotations

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment


class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        return select(Payment)

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, payment_id: int) -> Payment | None:
        result = await self.session.execute(
            self._base_query().where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    async def list_payments(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        status: str | None = None,
        seller_id: int | None = None,
        collector_id: int | None = None,
    ) -> tuple[list[Payment], int]:
        """Return (payments, total_count) with filters."""
        query = self._base_query()
        count_query = select(func.count(Payment.id))

        if policy_id is not None:
            query = query.where(Payment.policy_id == policy_id)
            count_query = count_query.where(Payment.policy_id == policy_id)
        if status is not None:
            query = query.where(Payment.status == status)
            count_query = count_query.where(Payment.status == status)
        if seller_id is not None:
            query = query.where(Payment.seller_id == seller_id)
            count_query = count_query.where(Payment.seller_id == seller_id)
        if collector_id is not None:
            query = query.where(Payment.collector_id == collector_id)
            count_query = count_query.where(Payment.collector_id == collector_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Payment.policy_id, Payment.payment_number).offset(skip).limit(limit)
        result = await self.session.execute(query)
        payments = list(result.scalars().all())

        return payments, total

    async def get_by_policy(self, policy_id: int) -> list[Payment]:
        result = await self.session.execute(
            self._base_query()
            .where(Payment.policy_id == policy_id)
            .order_by(Payment.payment_number)
        )
        return list(result.scalars().all())

    async def get_max_payment_number(self, policy_id: int) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(Payment.payment_number), 0))
            .where(Payment.policy_id == policy_id)
        )
        return result.scalar_one()

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def update(self, payment: Payment) -> Payment:
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def increment_payment_numbers_after(
        self, policy_id: int, after_number: int
    ) -> None:
        """Increment payment_number by 1 for all payments after a given number."""
        await self.session.execute(
            update(Payment)
            .where(Payment.policy_id == policy_id, Payment.payment_number > after_number)
            .values(payment_number=Payment.payment_number + 1)
        )
        await self.session.flush()

    async def all_payments_paid(self, policy_id: int) -> bool:
        """Check if all payments for a policy are paid."""
        result = await self.session.execute(
            select(func.count(Payment.id)).where(
                Payment.policy_id == policy_id,
                Payment.status != "paid",
                Payment.status != "cancelled",
            )
        )
        return result.scalar_one() == 0
