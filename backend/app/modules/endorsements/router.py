"""Endorsement endpoints — CRUD, approve/reject/apply, cost calculation."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.endorsements.schemas import (
    CostCalculationResponse,
    EndorsementCreate,
    EndorsementListResponse,
    EndorsementResponse,
    EndorsementUpdate,
)
from app.modules.endorsements.service import EndorsementService

router = APIRouter()


@router.get("", response_model=EndorsementListResponse)
async def list_endorsements(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("endorsements.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    policy_id: int | None = None,
    endorsement_type: str | None = Query(None),
    status: str | None = Query(None),
):
    """List endorsements with optional filters."""
    service = EndorsementService(db)
    return await service.list_endorsements(
        skip=skip,
        limit=limit,
        policy_id=policy_id,
        endorsement_type=endorsement_type,
        endorsement_status=status,
    )


@router.get("/{endorsement_id}", response_model=EndorsementResponse)
async def get_endorsement(
    endorsement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("endorsements.read")],
):
    """Get endorsement by ID."""
    service = EndorsementService(db)
    return await service.get_endorsement(endorsement_id)


@router.post("", response_model=EndorsementResponse, status_code=201)
async def create_endorsement(
    data: EndorsementCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("endorsements.create")],
):
    """Create an endorsement request for a policy."""
    service = EndorsementService(db)
    return await service.create_endorsement(data)


@router.put("/{endorsement_id}", response_model=EndorsementResponse)
async def update_endorsement(
    endorsement_id: int,
    data: EndorsementUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("endorsements.create")],
):
    """Update endorsement details (only pending/approved)."""
    service = EndorsementService(db)
    return await service.update_endorsement(endorsement_id, data)


@router.post("/{endorsement_id}/approve", response_model=EndorsementResponse)
async def approve_endorsement(
    endorsement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("endorsements.approve")],
):
    """Approve a pending endorsement."""
    service = EndorsementService(db)
    return await service.approve_endorsement(endorsement_id)


@router.post("/{endorsement_id}/reject", response_model=EndorsementResponse)
async def reject_endorsement(
    endorsement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("endorsements.approve")],
    comments: str | None = Query(None),
):
    """Reject a pending endorsement."""
    service = EndorsementService(db)
    return await service.reject_endorsement(endorsement_id, comments)


@router.post("/{endorsement_id}/apply", response_model=EndorsementResponse)
async def apply_endorsement(
    endorsement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("endorsements.apply")],
):
    """Apply an approved endorsement to the policy."""
    service = EndorsementService(db)
    return await service.apply_endorsement(endorsement_id)


@router.post(
    "/{endorsement_id}/calculate-cost",
    response_model=CostCalculationResponse,
)
async def calculate_cost(
    endorsement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("endorsements.read")],
):
    """Calculate the cost of an endorsement (pro-rata based on remaining policy period)."""
    service = EndorsementService(db)
    return await service.calculate_cost(endorsement_id)
