"""Cancellation endpoints — create, undo, notify."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.cancellations.schemas import (
    CancellationCreate,
    CancellationListResponse,
    CancellationResponse,
)
from app.modules.cancellations.service import CancellationService

router = APIRouter()


@router.get("", response_model=CancellationListResponse)
async def list_cancellations(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("cancellations.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    code: str | None = Query(None),
    policy_id: int | None = None,
):
    """List cancellations with optional filters."""
    service = CancellationService(db)
    return await service.list_cancellations(
        skip=skip, limit=limit, code=code, policy_id=policy_id
    )


@router.get("/{cancellation_id}", response_model=CancellationResponse)
async def get_cancellation(
    cancellation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("cancellations.read")],
):
    """Get cancellation by ID."""
    service = CancellationService(db)
    return await service.get_cancellation(cancellation_id)


@router.post("", response_model=CancellationResponse, status_code=201)
async def create_cancellation(
    data: CancellationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("cancellations.create")],
):
    """Cancel a policy (C1-C5). Cascades to payments and card."""
    service = CancellationService(db)
    return await service.create_cancellation(data, user_id=user.id)


@router.post("/{cancellation_id}/undo", response_model=CancellationResponse)
async def undo_cancellation(
    cancellation_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("cancellations.undo")],
):
    """Undo a cancellation (admin only). Restores payments and card."""
    service = CancellationService(db)
    return await service.undo_cancellation(cancellation_id)


@router.post(
    "/{cancellation_id}/notify/{recipient}",
    response_model=CancellationResponse,
)
async def notify_cancellation(
    cancellation_id: int,
    recipient: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("cancellations.create")],
):
    """Mark notification as sent for a recipient (seller/collector/client)."""
    service = CancellationService(db)
    return await service.mark_notification_sent(cancellation_id, recipient)
