"""Vehicle endpoints — CRUD + lookup by serial/plates."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.vehicles.schemas import (
    VehicleCreate,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdate,
)
from app.modules.vehicles.service import VehicleService

router = APIRouter()


@router.get("", response_model=VehicleListResponse)
async def list_vehicles(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    vehicle_type: str | None = Query(None),
    vehicle_key: int | None = Query(None),
    search: str | None = Query(None, max_length=100),
):
    """List vehicles with optional filters and pagination."""
    service = VehicleService(db)
    return await service.list_vehicles(
        skip=skip,
        limit=limit,
        vehicle_type=vehicle_type,
        vehicle_key=vehicle_key,
        search=search,
    )


@router.get("/by-serial/{serial_number}", response_model=VehicleResponse)
async def get_vehicle_by_serial(
    serial_number: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.read")],
):
    """Lookup vehicle by serial number."""
    service = VehicleService(db)
    return await service.get_by_serial(serial_number)


@router.get("/by-plates/{plates}", response_model=VehicleResponse)
async def get_vehicle_by_plates(
    plates: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.read")],
):
    """Lookup vehicle by plates."""
    service = VehicleService(db)
    return await service.get_by_plates(plates)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.read")],
):
    """Get vehicle by ID."""
    service = VehicleService(db)
    return await service.get_vehicle(vehicle_id)


@router.post("", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    data: VehicleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.create")],
):
    """Create a new vehicle."""
    service = VehicleService(db)
    return await service.create_vehicle(data)


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("vehicles.update")],
):
    """Update vehicle fields."""
    service = VehicleService(db)
    return await service.update_vehicle(vehicle_id, data)
