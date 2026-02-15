"""Data access layer for tow services and providers."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.incidents import TowProvider, TowSatisfactionSurvey, TowService


class TowServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Tow Service CRUD ───────────────────────────────────────────

    async def get_by_id(self, tow_service_id: int) -> TowService | None:
        result = await self.session.execute(
            select(TowService).where(TowService.id == tow_service_id)
        )
        return result.scalar_one_or_none()

    async def list_tow_services(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        service_status: str | None = None,
        tow_provider_id: int | None = None,
    ) -> tuple[list[TowService], int]:
        query = select(TowService)
        count_query = select(func.count(TowService.id))

        if policy_id is not None:
            query = query.where(TowService.policy_id == policy_id)
            count_query = count_query.where(TowService.policy_id == policy_id)
        if service_status is not None:
            query = query.where(TowService.service_status == service_status)
            count_query = count_query.where(TowService.service_status == service_status)
        if tow_provider_id is not None:
            query = query.where(TowService.tow_provider_id == tow_provider_id)
            count_query = count_query.where(TowService.tow_provider_id == tow_provider_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(TowService.report_time.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, tow_service: TowService) -> TowService:
        self.session.add(tow_service)
        await self.session.flush()
        await self.session.refresh(tow_service)
        return tow_service

    async def update(self, tow_service: TowService) -> TowService:
        await self.session.flush()
        await self.session.refresh(tow_service)
        return tow_service

    async def generate_report_number(self) -> str:
        """Generate next tow report number (TOW-YYYYMMDD-NNNN).

        Uses MAX instead of COUNT to avoid race conditions.
        """
        today = date.today()
        prefix = f"TOW-{today.strftime('%Y%m%d')}-"

        result = await self.session.execute(
            select(func.max(TowService.report_number)).where(
                TowService.report_number.like(f"{prefix}%")
            )
        )
        last = result.scalar_one_or_none()
        if last:
            seq = int(last.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"

    # ── Policy ─────────────────────────────────────────────────────

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    # ── Tow Provider CRUD ──────────────────────────────────────────

    async def get_provider_by_id(self, provider_id: int) -> TowProvider | None:
        result = await self.session.execute(
            select(TowProvider).where(TowProvider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def list_providers(
        self, *, active_only: bool = True
    ) -> tuple[list[TowProvider], int]:
        query = select(TowProvider)
        count_query = select(func.count(TowProvider.id))

        if active_only:
            query = query.where(TowProvider.status == "active")
            count_query = count_query.where(TowProvider.status == "active")

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(TowProvider.name.asc())
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create_provider(self, provider: TowProvider) -> TowProvider:
        self.session.add(provider)
        await self.session.flush()
        await self.session.refresh(provider)
        return provider

    async def update_provider(self, provider: TowProvider) -> TowProvider:
        await self.session.flush()
        await self.session.refresh(provider)
        return provider

    # ── Satisfaction Survey ────────────────────────────────────────

    async def get_survey(self, tow_service_id: int) -> TowSatisfactionSurvey | None:
        result = await self.session.execute(
            select(TowSatisfactionSurvey).where(
                TowSatisfactionSurvey.tow_service_id == tow_service_id
            )
        )
        return result.scalar_one_or_none()

    async def create_survey(
        self, survey: TowSatisfactionSurvey
    ) -> TowSatisfactionSurvey:
        self.session.add(survey)
        await self.session.flush()
        await self.session.refresh(survey)
        return survey
