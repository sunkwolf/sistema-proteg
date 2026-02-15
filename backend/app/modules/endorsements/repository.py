"""Data access layer for endorsements."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.endorsements import Endorsement


class EndorsementRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, endorsement_id: int) -> Endorsement | None:
        result = await self.session.execute(
            select(Endorsement).where(Endorsement.id == endorsement_id)
        )
        return result.scalar_one_or_none()

    async def list_endorsements(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        endorsement_type: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Endorsement], int]:
        query = select(Endorsement)
        count_query = select(func.count(Endorsement.id))

        if policy_id is not None:
            query = query.where(Endorsement.policy_id == policy_id)
            count_query = count_query.where(Endorsement.policy_id == policy_id)
        if endorsement_type is not None:
            query = query.where(Endorsement.endorsement_type == endorsement_type)
            count_query = count_query.where(Endorsement.endorsement_type == endorsement_type)
        if status is not None:
            query = query.where(Endorsement.status == status)
            count_query = count_query.where(Endorsement.status == status)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Endorsement.request_date.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, endorsement: Endorsement) -> Endorsement:
        self.session.add(endorsement)
        await self.session.flush()
        await self.session.refresh(endorsement)
        return endorsement

    async def update(self, endorsement: Endorsement) -> Endorsement:
        await self.session.flush()
        await self.session.refresh(endorsement)
        return endorsement

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()
