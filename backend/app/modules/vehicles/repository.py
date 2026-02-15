"""Data access layer for vehicles."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Vehicle


class VehicleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        return select(Vehicle)

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, vehicle_id: int) -> Vehicle | None:
        result = await self.session.execute(
            self._base_query().where(Vehicle.id == vehicle_id)
        )
        return result.scalar_one_or_none()

    async def get_by_serial(self, serial_number: str) -> Vehicle | None:
        result = await self.session.execute(
            self._base_query().where(Vehicle.serial_number == serial_number)
        )
        return result.scalar_one_or_none()

    async def get_by_plates(self, plates: str) -> Vehicle | None:
        result = await self.session.execute(
            self._base_query().where(Vehicle.plates == plates)
        )
        return result.scalar_one_or_none()

    async def list_vehicles(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        vehicle_type: str | None = None,
        vehicle_key: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Vehicle], int]:
        """Return (vehicles, total_count) with filters applied."""
        query = self._base_query()
        count_query = select(func.count(Vehicle.id))

        if vehicle_type is not None:
            query = query.where(Vehicle.vehicle_type == vehicle_type)
            count_query = count_query.where(Vehicle.vehicle_type == vehicle_type)
        if vehicle_key is not None:
            query = query.where(Vehicle.vehicle_key == vehicle_key)
            count_query = count_query.where(Vehicle.vehicle_key == vehicle_key)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                Vehicle.brand.ilike(pattern)
                | Vehicle.serial_number.ilike(pattern)
                | Vehicle.plates.ilike(pattern)
            )
            count_query = count_query.where(
                Vehicle.brand.ilike(pattern)
                | Vehicle.serial_number.ilike(pattern)
                | Vehicle.plates.ilike(pattern)
            )

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Vehicle.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        vehicles = list(result.scalars().all())

        return vehicles, total

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle

    async def update(self, vehicle: Vehicle) -> Vehicle:
        await self.session.flush()
        await self.session.refresh(vehicle)
        return vehicle
