"""Policy endpoints — CRUD, folio lookup, seller change."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.policies.schemas import (
    ChangeSeller,
    PolicyCreate,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdate,
)
from app.modules.policies.service import PolicyService

router = APIRouter()


@router.get("", response_model=PolicyListResponse)
async def list_policies(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("policies.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    seller_id: int | None = None,
    client_id: int | None = None,
    coverage_name: str | None = Query(None, max_length=50),
    effective_date_from: date | None = None,
    effective_date_to: date | None = None,
    search: str | None = Query(None, max_length=100),
    sort_by: str = Query("folio", pattern="^(folio|effective_date|created_at|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """List policies with filters, search, sorting, and pagination."""
    service = PolicyService(db)
    return await service.list_policies(
        skip=skip,
        limit=limit,
        status=status,
        seller_id=seller_id,
        client_id=client_id,
        coverage_name=coverage_name,
        effective_date_from=effective_date_from,
        effective_date_to=effective_date_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/by-folio/{folio}", response_model=PolicyResponse)
async def get_policy_by_folio(
    folio: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("policies.read")],
):
    """Lookup policy by business folio."""
    service = PolicyService(db)
    return await service.get_by_folio(folio)


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("policies.read")],
):
    """Get policy by ID with full details."""
    service = PolicyService(db)
    return await service.get_policy(policy_id)


@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(
    data: PolicyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("policies.create")],
):
    """Create a new policy. Auto-generates folio, payments, and card."""
    service = PolicyService(db)
    return await service.create_policy(data, current_user_id=user.id)


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: int,
    data: PolicyUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("policies.update")],
):
    """Update policy fields."""
    service = PolicyService(db)
    return await service.update_policy(policy_id, data)


@router.put("/{policy_id}/seller", response_model=PolicyResponse)
async def change_policy_seller(
    policy_id: int,
    data: ChangeSeller,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("policies.change_seller")],
):
    """Change seller assigned to a policy. Cascades to all payments."""
    service = PolicyService(db)
    return await service.change_seller(policy_id, data)
