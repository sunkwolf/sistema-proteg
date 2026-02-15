"""Business logic for vehicles."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Vehicle
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)


class VehicleService:
    def __init__(self, db: AsyncSession):
        self.repo = VehicleRepository(db)

    # ── Serialization ─────────────────────────────────────────────────

    @staticmethod
    def _to_response(v: Vehicle) -> VehicleResponse:
        return VehicleResponse(
            id=v.id,
            brand=v.brand,
            model_type=v.model_type,
            model_year=v.model_year,
            color=v.color,
            vehicle_key=v.vehicle_key,
            vehicle_type=v.vehicle_type.value if hasattr(v.vehicle_type, "value") else v.vehicle_type,
            serial_number=v.serial_number,
            plates=v.plates,
            seats=v.seats,
            load_capacity=v.load_capacity,
            cylinder_capacity=v.cylinder_capacity,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────

    async def list_vehicles(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        vehicle_type: str | None = None,
        vehicle_key: int | None = None,
        search: str | None = None,
    ) -> VehicleListResponse:
        vehicles, total = await self.repo.list_vehicles(
            skip=skip,
            limit=limit,
            vehicle_type=vehicle_type,
            vehicle_key=vehicle_key,
            search=search,
        )
        return VehicleListResponse(
            items=[self._to_response(v) for v in vehicles],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_vehicle(self, vehicle_id: int) -> VehicleResponse:
        v = await self.repo.get_by_id(vehicle_id)
        if v is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehiculo no encontrado",
            )
        return self._to_response(v)

    async def get_by_serial(self, serial_number: str) -> VehicleResponse:
        v = await self.repo.get_by_serial(serial_number)
        if v is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehiculo no encontrado con ese numero de serie",
            )
        return self._to_response(v)

    async def get_by_plates(self, plates: str) -> VehicleResponse:
        v = await self.repo.get_by_plates(plates)
        if v is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehiculo no encontrado con esas placas",
            )
        return self._to_response(v)

    async def create_vehicle(self, data: VehicleCreate) -> VehicleResponse:
        # Check serial_number uniqueness if provided
        if data.serial_number:
            existing = await self.repo.get_by_serial(data.serial_number)
            if existing is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un vehiculo con numero de serie '{data.serial_number}'",
                )

        vehicle = Vehicle(
            brand=data.brand,
            model_type=data.model_type,
            model_year=data.model_year,
            color=data.color,
            vehicle_key=data.vehicle_key,
            vehicle_type=data.vehicle_type,
            serial_number=data.serial_number,
            plates=data.plates,
            seats=data.seats,
            load_capacity=data.load_capacity,
            cylinder_capacity=data.cylinder_capacity,
        )
        vehicle = await self.repo.create(vehicle)
        return self._to_response(vehicle)

    async def update_vehicle(
        self, vehicle_id: int, data: VehicleUpdate
    ) -> VehicleResponse:
        v = await self.repo.get_by_id(vehicle_id)
        if v is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehiculo no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True)

        # If serial_number is changing, check uniqueness
        if "serial_number" in update_data and update_data["serial_number"]:
            existing = await self.repo.get_by_serial(update_data["serial_number"])
            if existing is not None and existing.id != vehicle_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un vehiculo con numero de serie '{update_data['serial_number']}'",
                )

        for field, value in update_data.items():
            setattr(v, field, value)

        v = await self.repo.update(v)
        return self._to_response(v)
