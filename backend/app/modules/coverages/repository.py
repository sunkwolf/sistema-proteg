"""Data access layer for coverages."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Coverage


class CoverageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        return select(Coverage)

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, coverage_id: int) -> Coverage | None:
        result = await self.session.execute(
            self._base_query().where(Coverage.id == coverage_id)
        )
        return result.scalar_one_or_none()

    async def list_coverages(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        is_active: bool | None = None,
        vehicle_key: int | None = None,
        category: str | None = None,
        service_type: str | None = None,
    ) -> tuple[list[Coverage], int]:
        """Return (coverages, total_count) with filters."""
        query = self._base_query()
        count_query = select(func.count(Coverage.id))

        if is_active is not None:
            query = query.where(Coverage.is_active == is_active)
            count_query = count_query.where(Coverage.is_active == is_active)
        if vehicle_key is not None:
            query = query.where(Coverage.vehicle_key == vehicle_key)
            count_query = count_query.where(Coverage.vehicle_key == vehicle_key)
        if category is not None:
            query = query.where(Coverage.category == category)
            count_query = count_query.where(Coverage.category == category)
        if service_type is not None:
            query = query.where(Coverage.service_type == service_type)
            count_query = count_query.where(Coverage.service_type == service_type)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Coverage.vehicle_key, Coverage.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        coverages = list(result.scalars().all())

        return coverages, total

    async def search_coverages(
        self,
        *,
        vehicle_type: str | None = None,
        name: str | None = None,
        service_type: str | None = None,
        cylinder_capacity: str | None = None,
        is_motorcycle: bool = False,
    ) -> list[Coverage]:
        """Search coverages following business logic for cylinder_capacity."""
        query = self._base_query().where(Coverage.is_active == True)  # noqa: E712

        if vehicle_type is not None:
            query = query.where(Coverage.vehicle_type == vehicle_type)
        if name is not None:
            query = query.where(Coverage.name.ilike(f"%{name}%"))
        if service_type is not None:
            query = query.where(Coverage.service_type == service_type)

        # Cylinder capacity logic from business rules
        if is_motorcycle and cylinder_capacity:
            query = query.where(Coverage.cylinder_capacity == cylinder_capacity)
        else:
            query = query.where(Coverage.cylinder_capacity.is_(None))

        query = query.order_by(Coverage.name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, coverage: Coverage) -> Coverage:
        self.session.add(coverage)
        await self.session.flush()
        await self.session.refresh(coverage)
        return coverage

    async def update(self, coverage: Coverage) -> Coverage:
        await self.session.flush()
        await self.session.refresh(coverage)
        return coverage
