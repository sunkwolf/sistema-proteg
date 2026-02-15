"""Promotion endpoints — CRUD, rules, apply, simulate."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permission
from app.models.auth import AppUser
from app.modules.promotions.schemas import (
    PromotionApplyRequest,
    PromotionApplicationListResponse,
    PromotionApplicationResponse,
    PromotionCreate,
    PromotionListResponse,
    PromotionResponse,
    PromotionRuleCreate,
    PromotionRuleResponse,
    PromotionRuleUpdate,
    PromotionUpdate,
)
from app.modules.promotions.service import PromotionService

router = APIRouter()

CurrentUser = Annotated[AppUser, Depends(get_current_user)]


# ── Promotion CRUD ─────────────────────────────────────────────────


@router.get("", response_model=PromotionListResponse)
async def list_promotions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
):
    """List promotions with optional status filter."""
    service = PromotionService(db)
    return await service.list_promotions(
        skip=skip, limit=limit, status_filter=status
    )


@router.get("/active", response_model=list[PromotionResponse])
async def list_active_promotions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
):
    """List currently active promotions (within date range)."""
    service = PromotionService(db)
    return await service.list_active_promotions()


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion(
    promotion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
):
    """Get promotion by ID."""
    service = PromotionService(db)
    return await service.get_promotion(promotion_id)


@router.post("", response_model=PromotionResponse, status_code=201)
async def create_promotion(
    data: PromotionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.create")],
):
    """Create a new promotion."""
    service = PromotionService(db)
    return await service.create_promotion(data)


@router.put("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: int,
    data: PromotionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.create")],
):
    """Update promotion details."""
    service = PromotionService(db)
    return await service.update_promotion(promotion_id, data)


# ── Promotion Rules ────────────────────────────────────────────────


@router.get(
    "/{promotion_id}/rules", response_model=list[PromotionRuleResponse]
)
async def list_rules(
    promotion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
):
    """List rules for a promotion."""
    service = PromotionService(db)
    return await service.list_rules(promotion_id)


@router.post(
    "/{promotion_id}/rules",
    response_model=PromotionRuleResponse,
    status_code=201,
)
async def create_rule(
    promotion_id: int,
    data: PromotionRuleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.create")],
):
    """Add a rule to a promotion."""
    service = PromotionService(db)
    return await service.create_rule(promotion_id, data)


@router.put(
    "/{promotion_id}/rules/{rule_id}",
    response_model=PromotionRuleResponse,
)
async def update_rule(
    promotion_id: int,
    rule_id: int,
    data: PromotionRuleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.create")],
):
    """Update a promotion rule."""
    service = PromotionService(db)
    return await service.update_rule(promotion_id, rule_id, data)


@router.delete(
    "/{promotion_id}/rules/{rule_id}", status_code=204
)
async def delete_rule(
    promotion_id: int,
    rule_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.create")],
):
    """Delete a promotion rule."""
    service = PromotionService(db)
    await service.delete_rule(promotion_id, rule_id)


# ── Apply & Simulate ──────────────────────────────────────────────


@router.post(
    "/{promotion_id}/rules/{rule_id}/apply",
    response_model=PromotionApplicationResponse,
    status_code=201,
)
async def apply_promotion(
    promotion_id: int,
    rule_id: int,
    data: PromotionApplyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("promotions.apply")],
):
    """Apply a promotion rule to a policy."""
    service = PromotionService(db)
    return await service.apply_promotion(
        promotion_id, rule_id, data, user_id=user.id
    )


@router.post("/{promotion_id}/rules/{rule_id}/simulate")
async def simulate_promotion(
    promotion_id: int,
    rule_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
):
    """Simulate a promotion discount without persisting."""
    service = PromotionService(db)
    return await service.simulate_promotion(promotion_id, rule_id)


# ── Applications ───────────────────────────────────────────────────


@router.get(
    "/{promotion_id}/applications",
    response_model=PromotionApplicationListResponse,
)
async def list_applications(
    promotion_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("promotions.read")],
):
    """List all applications of a promotion."""
    service = PromotionService(db)
    return await service.list_applications(promotion_id)
