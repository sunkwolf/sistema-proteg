"""Business logic for the Collections (Cards/Cobranza) module."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collections import Card, CollectionAssignment, VisitNotice
from app.modules.collections.repository import CollectionRepository
from app.modules.collections.schemas import CardReassign, VisitNoticeCreate


class CollectionService:
    def __init__(self, session: AsyncSession):
        self.repo = CollectionRepository(session)

    # ── Cards ─────────────────────────────────────────────────────────

    async def list_cards(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        holder: str | None = None,
    ) -> dict:
        cards, total = await self.repo.list_cards(
            skip=skip, limit=limit, status=status_filter, holder=holder
        )
        return {"items": cards, "total": total, "skip": skip, "limit": limit}

    async def get_card(self, card_id: int) -> Card:
        card = await self.repo.get_card_by_id(card_id)
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada",
            )
        return card

    async def get_card_by_policy(self, policy_id: int) -> Card:
        card = await self.repo.get_card_by_policy(policy_id)
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existe tarjeta para esta poliza",
            )
        return card

    async def get_cards_by_collector(self, collector_name: str) -> list[Card]:
        return await self.repo.list_cards_by_collector(collector_name.upper())

    async def reassign_card(self, card_id: int, data: CardReassign) -> Card:
        card = await self.get_card(card_id)

        c_status = card.status
        if hasattr(c_status, "value"):
            c_status = c_status.value
        if c_status != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede reasignar una tarjeta con status '{c_status}'",
            )

        # Create assignment record
        assignment = CollectionAssignment(
            card_id=card.id,
            policy_id=card.policy_id,
            assigned_to=data.assigned_to.upper(),
            zone=data.zone,
            route=data.route,
            assignment_date=date.today(),
            observations=data.observations,
        )
        await self.repo.create_assignment(assignment)

        # Update card current holder
        card.current_holder = data.assigned_to.upper()
        card.assignment_date = date.today()

        return await self.repo.update_card(card)

    async def get_assignment_history(
        self, card_id: int
    ) -> list[CollectionAssignment]:
        # Verify card exists
        await self.get_card(card_id)
        return await self.repo.get_assignment_history(card_id)

    # ── Visit Notices ─────────────────────────────────────────────────

    async def list_visit_notices(
        self,
        *,
        policy_id: int | None = None,
        card_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        notices, total = await self.repo.list_visit_notices(
            policy_id=policy_id, card_id=card_id, skip=skip, limit=limit
        )
        return {"items": notices, "total": total, "skip": skip, "limit": limit}

    async def create_visit_notice(self, data: VisitNoticeCreate) -> VisitNotice:
        notice = VisitNotice(
            card_id=data.card_id,
            policy_id=data.policy_id,
            visit_date=data.visit_date,
            comments=data.comments,
            payment_id=data.payment_id,
            notice_number=data.notice_number,
        )
        return await self.repo.create_visit_notice(notice)
