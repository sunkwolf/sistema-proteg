"""Data access layer for promotions, rules, and applications."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.promotions import Promotion, PromotionApplication, PromotionRule


class PromotionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Promotion CRUD ─────────────────────────────────────────────

    async def get_by_id(self, promotion_id: int) -> Promotion | None:
        result = await self.session.execute(
            select(Promotion).where(Promotion.id == promotion_id)
        )
        return result.scalar_one_or_none()

    async def list_promotions(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
    ) -> tuple[list[Promotion], int]:
        query = select(Promotion)
        count_query = select(func.count(Promotion.id))

        if status is not None:
            query = query.where(Promotion.status == status)
            count_query = count_query.where(Promotion.status == status)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Promotion.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def list_active_promotions(self) -> list[Promotion]:
        today = date.today()
        query = (
            select(Promotion)
            .where(
                Promotion.status == "active",
            )
            .order_by(Promotion.start_date.asc())
        )
        result = await self.session.execute(query)
        promos = list(result.scalars().all())

        # Filter by date range in Python (nullable dates)
        active = []
        for p in promos:
            if p.start_date and today < p.start_date:
                continue
            if p.end_date and today > p.end_date:
                continue
            active.append(p)
        return active

    async def create(self, promotion: Promotion) -> Promotion:
        self.session.add(promotion)
        await self.session.flush()
        await self.session.refresh(promotion)
        return promotion

    async def update(self, promotion: Promotion) -> Promotion:
        await self.session.flush()
        await self.session.refresh(promotion)
        return promotion

    # ── Promotion Rules ────────────────────────────────────────────

    async def get_rule_by_id(self, rule_id: int) -> PromotionRule | None:
        result = await self.session.execute(
            select(PromotionRule).where(PromotionRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def list_rules(self, promotion_id: int) -> list[PromotionRule]:
        result = await self.session.execute(
            select(PromotionRule)
            .where(PromotionRule.promotion_id == promotion_id)
            .order_by(PromotionRule.id.asc())
        )
        return list(result.scalars().all())

    async def create_rule(self, rule: PromotionRule) -> PromotionRule:
        self.session.add(rule)
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def update_rule(self, rule: PromotionRule) -> PromotionRule:
        await self.session.flush()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule: PromotionRule) -> None:
        await self.session.delete(rule)
        await self.session.flush()

    # ── Promotion Applications ─────────────────────────────────────

    async def list_applications(
        self, promotion_id: int
    ) -> tuple[list[PromotionApplication], int]:
        query = select(PromotionApplication).where(
            PromotionApplication.promotion_id == promotion_id
        )
        count_query = select(func.count(PromotionApplication.id)).where(
            PromotionApplication.promotion_id == promotion_id
        )

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        result = await self.session.execute(
            query.order_by(PromotionApplication.applied_at.desc())
        )
        items = list(result.scalars().all())

        return items, total

    async def get_existing_application(
        self, promotion_id: int, policy_id: int, rule_id: int
    ) -> PromotionApplication | None:
        result = await self.session.execute(
            select(PromotionApplication).where(
                PromotionApplication.promotion_id == promotion_id,
                PromotionApplication.policy_id == policy_id,
                PromotionApplication.promotion_rule_id == rule_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_application(
        self, app: PromotionApplication
    ) -> PromotionApplication:
        self.session.add(app)
        await self.session.flush()
        await self.session.refresh(app)
        return app

    # ── Policy ─────────────────────────────────────────────────────

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()
