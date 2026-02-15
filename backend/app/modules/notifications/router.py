"""Notification endpoints — history, send overdue/reminders, stats."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.models.auth import AppUser
from app.modules.notifications.schemas import (
    NotificationHistoryResponse,
    NotificationStatsResponse,
    SendOverdueRequest,
    SendRemindersRequest,
    SendResultResponse,
)
from app.modules.notifications.service import NotificationService

router = APIRouter()

CurrentUser = Annotated[AppUser, Depends(get_current_user)]


@router.get("/history", response_model=NotificationHistoryResponse)
async def list_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("notifications.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    policy_id: int | None = None,
    message_type: str | None = Query(None),
    channel: str | None = Query(None),
    delivery_status: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """List notification history with filters."""
    service = NotificationService(db)
    return await service.list_history(
        skip=skip,
        limit=limit,
        policy_id=policy_id,
        message_type=message_type,
        channel=channel,
        delivery_status=delivery_status,
        date_from=date_from,
        date_to=date_to,
    )


@router.post("/send-overdue", response_model=SendResultResponse)
async def send_overdue(
    data: SendOverdueRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("notifications.send")],
):
    """Enqueue overdue notifications to clients with late payments."""
    service = NotificationService(db)
    return await service.enqueue_overdue(user_id=user.id)


@router.post("/send-reminders", response_model=SendResultResponse)
async def send_reminders(
    data: SendRemindersRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("notifications.send")],
):
    """Enqueue reminder notifications for upcoming payments."""
    service = NotificationService(db)
    return await service.enqueue_reminders(user_id=user.id)


@router.get("/stats", response_model=NotificationStatsResponse)
async def get_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("notifications.read")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    channel: str | None = Query(None),
    message_type: str | None = Query(None),
):
    """Get notification delivery statistics."""
    service = NotificationService(db)
    return await service.get_stats(
        date_from=date_from,
        date_to=date_to,
        channel=channel,
        message_type=message_type,
    )
