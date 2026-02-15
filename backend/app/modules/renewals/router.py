"""Renewal endpoints — pending detection, CRUD, complete/reject."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.renewals.schemas import (
    PendingRenewalListResponse,
    RenewalComplete,
    RenewalCreate,
    RenewalListResponse,
    RenewalNotificationLogResponse,
    RenewalResponse,
)
from app.modules.renewals.service import RenewalService

router = APIRouter()


@router.get("", response_model=RenewalListResponse)
async def list_renewals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("renewals.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    old_policy_id: int | None = None,
):
    """List all renewal records with optional filters."""
    service = RenewalService(db)
    return await service.list_renewals(
        skip=skip, limit=limit, renewal_status=status, old_policy_id=old_policy_id
    )


@router.get("/pending", response_model=PendingRenewalListResponse)
async def get_pending_renewals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("renewals.read")],
    days_before: int = Query(30, ge=0, le=365),
    days_after: int = Query(0, ge=0, le=365),
    seller_id: int | None = None,
):
    """Detect policies approaching or past expiration (pending renewal)."""
    service = RenewalService(db)
    return await service.get_pending_policies(
        days_before=days_before, days_after=days_after, seller_id=seller_id
    )


@router.get("/{renewal_id}", response_model=RenewalResponse)
async def get_renewal(
    renewal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("renewals.read")],
):
    """Get renewal by ID."""
    service = RenewalService(db)
    return await service.get_renewal(renewal_id)


@router.post("", response_model=RenewalResponse, status_code=201)
async def create_renewal(
    data: RenewalCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("renewals.create")],
):
    """Create a renewal record for an expiring policy."""
    service = RenewalService(db)
    return await service.create_renewal(data)


@router.post("/{renewal_id}/complete", response_model=RenewalResponse)
async def complete_renewal(
    renewal_id: int,
    data: RenewalComplete,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("renewals.create")],
):
    """Mark a renewal as completed by linking the new policy."""
    service = RenewalService(db)
    return await service.complete_renewal(renewal_id, data)


@router.post("/{renewal_id}/reject", response_model=RenewalResponse)
async def reject_renewal(
    renewal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("renewals.create")],
    comments: str | None = Query(None),
):
    """Reject a renewal (client declined to renew)."""
    service = RenewalService(db)
    return await service.reject_renewal(renewal_id, comments)


@router.get(
    "/{renewal_id}/notifications",
    response_model=list[RenewalNotificationLogResponse],
)
async def get_renewal_notifications(
    renewal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("renewals.read")],
):
    """Get notification history for a renewal's policy."""
    service = RenewalService(db)
    renewal = await service.get_renewal(renewal_id)
    return await service.get_notification_logs(renewal.old_policy_id)
