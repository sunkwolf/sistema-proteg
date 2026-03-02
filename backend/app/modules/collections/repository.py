"""
Collections Module — Repository (DB queries)
Claudy ✨ + Fer — 2026-03-02
from sqlalchemy import String
"""
from datetime import date, datetime
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, or_, case, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.models.policy import (
    Policy, Payment, Card, Collector, Seller, Vehicle, Coverage,
)
from app.models.client import Client


class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_collector_by_code(self, code_name: str) -> Optional[Collector]:
        result = await self.session.execute(
            select(Collector).where(Collector.code_name == code_name)
        )
        return result.scalar_one_or_none()

    async def get_collector_by_id(self, collector_id: int) -> Optional[Collector]:
        result = await self.session.execute(
            select(Collector).where(Collector.id == collector_id)
        )
        return result.scalar_one_or_none()

    async def get_cards_for_collector(
        self,
        collector_code: str,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Tuple[Card, Policy, Client, Payment]]:
        """
        Get all cards assigned to a collector with their current pending payment.
        Returns tuples of (card, policy, client, next_pending_payment).
        """
        # Subquery: next pending payment per policy
        next_payment_sq = (
            select(
                Payment.policy_id,
                func.min(Payment.payment_number).label("next_number"),
            )
            .where(Payment.status == "pending")
            .group_by(Payment.policy_id)
            .subquery()
        )

        query = (
            select(Card, Policy, Client, Payment)
            .join(Policy, Card.policy_id == Policy.id)
            .join(Client, Policy.client_id == Client.id)
            .outerjoin(
                next_payment_sq,
                next_payment_sq.c.policy_id == Policy.id,
            )
            .outerjoin(
                Payment,
                and_(
                    Payment.policy_id == Policy.id,
                    Payment.payment_number == next_payment_sq.c.next_number,
                ),
            )
            .where(Card.current_holder == collector_code)
            .where(Card.status == "active")
        )

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    func.cast(Policy.folio, String).ilike(search_term),
                    (Client.first_name + " " + Client.paternal_surname).ilike(search_term),
                )
            )

        query = query.order_by(Payment.due_date.asc().nullslast())

        result = await self.session.execute(query)
        return result.all()

    async def get_policy_by_folio(self, folio: int) -> Optional[Policy]:
        """Get a policy with all relationships loaded."""
        result = await self.session.execute(
            select(Policy)
            .options(
                joinedload(Policy.client).joinedload(Client.address),
                joinedload(Policy.vehicle),
                joinedload(Policy.coverage),
                selectinload(Policy.payments),
            )
            .where(Policy.folio == folio)
        )
        return result.unique().scalar_one_or_none()

    async def get_payments_for_collector(
        self,
        collector_id: int,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Payment]:
        query = (
            select(Payment)
            .where(Payment.collector_id == collector_id)
        )
        if status:
            query = query.where(Payment.status == status)
        if start_date:
            query = query.where(Payment.actual_date >= start_date)
        if end_date:
            query = query.where(Payment.actual_date <= end_date)
        query = query.order_by(Payment.actual_date.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_collector_stats(
        self, collector_id: int, today: date
    ) -> dict:
        """Get dashboard stats for a collector for today."""
        # Collections today
        result = await self.session.execute(
            select(
                func.count(Payment.id).label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("total"),
            )
            .where(Payment.collector_id == collector_id)
            .where(Payment.status == "paid")
            .where(Payment.actual_date == today)
        )
        row = result.one()
        return {
            "collections_count": row.count,
            "collected_amount": float(row.total),
        }

    async def get_total_payments_for_policy(self, policy_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Payment.id))
            .where(Payment.policy_id == policy_id)
        )
        return result.scalar_one()
