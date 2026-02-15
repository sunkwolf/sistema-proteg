"""Coverage endpoints — CRUD, search, payment schemes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.coverages.schemas import (
    CoverageCreate,
    CoverageListResponse,
    CoveragePaymentSchemesResponse,
    CoverageResponse,
    CoverageUpdate,
)
from app.modules.coverages.service import CoverageService

router = APIRouter()


@router.get("", response_model=CoverageListResponse)
async def list_coverages(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    is_active: bool | None = None,
    vehicle_key: int | None = None,
    category: str | None = Query(None, pattern="^(liability|comprehensive|platform)$"),
    service_type: str | None = Query(None, pattern="^(private|commercial)$"),
):
    """List all coverages with optional filters."""
    service = CoverageService(db)
    return await service.list_coverages(
        skip=skip,
        limit=limit,
        is_active=is_active,
        vehicle_key=vehicle_key,
        category=category,
        service_type=service_type,
    )


@router.get("/search", response_model=list[CoverageResponse])
async def search_coverages(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.read")],
    vehicle_type: str | None = Query(None),
    name: str | None = Query(None, max_length=50),
    service_type: str | None = Query(None, pattern="^(private|commercial)$"),
    cylinder_capacity: str | None = Query(None, max_length=20),
):
    """Search coverages by criteria. Only returns active coverages."""
    service = CoverageService(db)
    return await service.search_coverages(
        vehicle_type=vehicle_type,
        name=name,
        service_type=service_type,
        cylinder_capacity=cylinder_capacity,
    )


@router.get("/{coverage_id}/payment-schemes", response_model=CoveragePaymentSchemesResponse)
async def get_payment_schemes(
    coverage_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.read")],
):
    """Get payment scheme options for a coverage."""
    service = CoverageService(db)
    return await service.get_payment_schemes(coverage_id)


@router.get("/{coverage_id}", response_model=CoverageResponse)
async def get_coverage(
    coverage_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.read")],
):
    """Get coverage by ID."""
    service = CoverageService(db)
    return await service.get_coverage(coverage_id)


@router.post("", response_model=CoverageResponse, status_code=201)
async def create_coverage(
    data: CoverageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.create")],
):
    """Create a new coverage."""
    service = CoverageService(db)
    return await service.create_coverage(data)


@router.put("/{coverage_id}", response_model=CoverageResponse)
async def update_coverage(
    coverage_id: int,
    data: CoverageUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("coverages.update")],
):
    """Update coverage fields (prices, tow services, active status)."""
    service = CoverageService(db)
    return await service.update_coverage(coverage_id, data)
