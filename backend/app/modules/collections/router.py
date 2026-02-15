"""Collections endpoints — cards, assignments, visit notices."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.collections.schemas import (
    AssignmentResponse,
    CardListResponse,
    CardReassign,
    CardResponse,
    VisitNoticeCreate,
    VisitNoticeListResponse,
    VisitNoticeResponse,
)
from app.modules.collections.service import CollectionService

router = APIRouter()


# ── Cards ─────────────────────────────────────────────────────────────


@router.get("/cards", response_model=CardListResponse)
async def list_cards(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    holder: str | None = Query(None),
):
    """List cards with optional filters and pagination."""
    service = CollectionService(db)
    return await service.list_cards(
        skip=skip, limit=limit, status_filter=status, holder=holder
    )


@router.get("/cards/by-policy/{policy_id}", response_model=CardResponse)
async def get_card_by_policy(
    policy_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
):
    """Get the card for a specific policy."""
    service = CollectionService(db)
    return await service.get_card_by_policy(policy_id)


@router.get(
    "/cards/by-collector/{collector_name}",
    response_model=list[CardResponse],
)
async def get_cards_by_collector(
    collector_name: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
):
    """Get all active cards assigned to a collector."""
    service = CollectionService(db)
    return await service.get_cards_by_collector(collector_name)


@router.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
):
    """Get card by ID."""
    service = CollectionService(db)
    return await service.get_card(card_id)


@router.post("/cards/{card_id}/reassign", response_model=CardResponse)
async def reassign_card(
    card_id: int,
    data: CardReassign,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.reassign")],
):
    """Reassign a card to a different collector."""
    service = CollectionService(db)
    return await service.reassign_card(card_id, data)


@router.get(
    "/cards/{card_id}/history", response_model=list[AssignmentResponse]
)
async def get_assignment_history(
    card_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
):
    """Get assignment history for a card."""
    service = CollectionService(db)
    return await service.get_assignment_history(card_id)


# ── Visit Notices ─────────────────────────────────────────────────────


@router.get("/visit-notices", response_model=VisitNoticeListResponse)
async def list_visit_notices(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
    policy_id: int | None = None,
    card_id: int | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List visit notices with optional filters."""
    service = CollectionService(db)
    return await service.list_visit_notices(
        policy_id=policy_id, card_id=card_id, skip=skip, limit=limit
    )


@router.post(
    "/visit-notices",
    response_model=VisitNoticeResponse,
    status_code=201,
)
async def create_visit_notice(
    data: VisitNoticeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("collections.read")],
):
    """Create a visit notice for a policy."""
    service = CollectionService(db)
    return await service.create_visit_notice(data)
