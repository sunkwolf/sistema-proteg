"""Data access layer for collections (cards, assignments, visit notices)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.collections import Card, CollectionAssignment, VisitNotice


class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Cards ─────────────────────────────────────────────────────────

    async def get_card_by_id(self, card_id: int) -> Card | None:
        result = await self.session.execute(
            select(Card).where(Card.id == card_id)
        )
        return result.scalar_one_or_none()

    async def get_card_by_policy(self, policy_id: int) -> Card | None:
        result = await self.session.execute(
            select(Card).where(Card.policy_id == policy_id)
        )
        return result.scalar_one_or_none()

    async def list_cards(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        holder: str | None = None,
    ) -> tuple[list[Card], int]:
        query = select(Card)
        count_query = select(func.count(Card.id))

        if status is not None:
            query = query.where(Card.status == status)
            count_query = count_query.where(Card.status == status)
        if holder is not None:
            query = query.where(Card.current_holder == holder)
            count_query = count_query.where(Card.current_holder == holder)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Card.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        cards = list(result.scalars().all())

        return cards, total

    async def list_cards_by_collector(self, collector_name: str) -> list[Card]:
        result = await self.session.execute(
            select(Card)
            .where(Card.current_holder == collector_name, Card.status == "active")
            .order_by(Card.id.asc())
        )
        return list(result.scalars().all())

    async def update_card(self, card: Card) -> Card:
        await self.session.flush()
        await self.session.refresh(card)
        return card

    # ── Assignments ───────────────────────────────────────────────────

    async def create_assignment(
        self, assignment: CollectionAssignment
    ) -> CollectionAssignment:
        self.session.add(assignment)
        await self.session.flush()
        await self.session.refresh(assignment)
        return assignment

    async def get_assignment_history(
        self, card_id: int
    ) -> list[CollectionAssignment]:
        result = await self.session.execute(
            select(CollectionAssignment)
            .where(CollectionAssignment.card_id == card_id)
            .order_by(CollectionAssignment.created_at.desc())
        )
        return list(result.scalars().all())

    # ── Visit Notices ─────────────────────────────────────────────────

    async def create_visit_notice(self, notice: VisitNotice) -> VisitNotice:
        self.session.add(notice)
        await self.session.flush()
        await self.session.refresh(notice)
        return notice

    async def list_visit_notices(
        self,
        *,
        policy_id: int | None = None,
        card_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[VisitNotice], int]:
        query = select(VisitNotice)
        count_query = select(func.count(VisitNotice.id))

        if policy_id is not None:
            query = query.where(VisitNotice.policy_id == policy_id)
            count_query = count_query.where(VisitNotice.policy_id == policy_id)
        if card_id is not None:
            query = query.where(VisitNotice.card_id == card_id)
            count_query = count_query.where(VisitNotice.card_id == card_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(VisitNotice.visit_date.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        notices = list(result.scalars().all())

        return notices, total
