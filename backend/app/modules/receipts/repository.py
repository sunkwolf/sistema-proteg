"""Data access layer for receipts."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Employee
from app.models.payments import Receipt, ReceiptLossSchedule


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Single Receipt ────────────────────────────────────────────────

    async def get_by_id(self, receipt_id: int) -> Receipt | None:
        result = await self.session.execute(
            select(Receipt).where(Receipt.id == receipt_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, receipt_number: str) -> Receipt | None:
        result = await self.session.execute(
            select(Receipt).where(Receipt.receipt_number == receipt_number)
        )
        return result.scalar_one_or_none()

    # ── Listing ───────────────────────────────────────────────────────

    async def list_receipts(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        collector_id: int | None = None,
        policy_id: int | None = None,
    ) -> tuple[list[Receipt], int]:
        query = select(Receipt)
        count_query = select(func.count(Receipt.id))

        if status is not None:
            query = query.where(Receipt.status == status)
            count_query = count_query.where(Receipt.status == status)
        if collector_id is not None:
            query = query.where(Receipt.collector_id == collector_id)
            count_query = count_query.where(Receipt.collector_id == collector_id)
        if policy_id is not None:
            query = query.where(Receipt.policy_id == policy_id)
            count_query = count_query.where(Receipt.policy_id == policy_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Receipt.receipt_number.asc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        receipts = list(result.scalars().all())

        return receipts, total

    async def get_by_collector(self, collector_id: int) -> list[Receipt]:
        result = await self.session.execute(
            select(Receipt)
            .where(Receipt.collector_id == collector_id)
            .order_by(Receipt.receipt_number.asc())
        )
        return list(result.scalars().all())

    # ── Batch Creation ────────────────────────────────────────────────

    async def existing_receipt_numbers(self, numbers: list[str]) -> set[str]:
        """Return which of the given receipt numbers already exist."""
        result = await self.session.execute(
            select(Receipt.receipt_number).where(
                Receipt.receipt_number.in_(numbers)
            )
        )
        return set(result.scalars().all())

    async def create_many(self, receipts: list[Receipt]) -> list[Receipt]:
        self.session.add_all(receipts)
        await self.session.flush()
        for r in receipts:
            await self.session.refresh(r)
        return receipts

    # ── Assignment ────────────────────────────────────────────────────

    async def get_collector(self, collector_id: int) -> Employee | None:
        result = await self.session.execute(
            select(Employee).where(
                Employee.id == collector_id,
                Employee.es_cobrador.is_(True),
                Employee.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def count_active_receipts_for_collector(self, collector_id: int) -> int:
        """Count receipts with active statuses for a collector."""
        active_statuses = ["assigned", "used", "lost", "cancelled_undelivered"]
        result = await self.session.execute(
            select(func.count(Receipt.id)).where(
                Receipt.collector_id == collector_id,
                Receipt.status.in_(active_statuses),
            )
        )
        return result.scalar_one()

    async def get_receipts_by_ids(
        self, receipt_ids: list[int], status_filter: str | None = None
    ) -> list[Receipt]:
        query = select(Receipt).where(Receipt.id.in_(receipt_ids))
        if status_filter is not None:
            query = query.where(Receipt.status == status_filter)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ── Verification helpers ──────────────────────────────────────────

    async def get_skipped_receipts(
        self, collector_id: int, receipt_number: str
    ) -> list[str]:
        """Find assigned receipts with lower number for the same collector."""
        prefix = receipt_number[0]
        result = await self.session.execute(
            select(Receipt.receipt_number)
            .where(
                Receipt.collector_id == collector_id,
                Receipt.status == "assigned",
                Receipt.receipt_number < receipt_number,
                Receipt.receipt_number.like(f"{prefix}%"),
            )
            .order_by(Receipt.receipt_number.asc())
        )
        return list(result.scalars().all())

    # ── Loss Schedule ─────────────────────────────────────────────────

    async def schedule_loss(self, receipt_number: str, deadline: date) -> None:
        schedule = ReceiptLossSchedule(
            receipt_number=receipt_number,
            deadline=deadline,
        )
        await self.session.merge(schedule)
        await self.session.flush()

    async def cancel_loss_schedule(self, receipt_number: str) -> None:
        result = await self.session.execute(
            select(ReceiptLossSchedule).where(
                ReceiptLossSchedule.receipt_number == receipt_number
            )
        )
        schedule = result.scalar_one_or_none()
        if schedule is not None:
            await self.session.delete(schedule)
            await self.session.flush()

    # ── Update ────────────────────────────────────────────────────────

    async def update(self, receipt: Receipt) -> Receipt:
        await self.session.flush()
        await self.session.refresh(receipt)
        return receipt
