"""Payment endpoints — CRUD, partial payments, revert, mark problem."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.payments.schemas import (
    MarkProblem,
    PartialPayment,
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
    PaymentUpdate,
    RevertPayment,
)
from app.modules.payments.service import PaymentService

router = APIRouter()


@router.get("", response_model=PaymentListResponse)
async def list_payments(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    policy_id: int | None = None,
    status: str | None = Query(None),
    seller_id: int | None = None,
    collector_id: int | None = None,
):
    """List payments with optional filters and pagination."""
    service = PaymentService(db)
    return await service.list_payments(
        skip=skip,
        limit=limit,
        policy_id=policy_id,
        status=status,
        seller_id=seller_id,
        collector_id=collector_id,
    )


@router.get("/by-policy/{policy_id}", response_model=list[PaymentResponse])
async def get_payments_by_policy(
    policy_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.read")],
):
    """Get all payments for a specific policy."""
    service = PaymentService(db)
    return await service.get_by_policy(policy_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.read")],
):
    """Get payment by ID."""
    service = PaymentService(db)
    return await service.get_payment(payment_id)


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.create")],
):
    """Create a manual payment."""
    service = PaymentService(db)
    return await service.create_payment(data)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    data: PaymentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.update")],
):
    """Full payment revision (Cobranza department only)."""
    service = PaymentService(db)
    return await service.update_payment(payment_id, data)


@router.post("/{payment_id}/partial", response_model=PaymentResponse)
async def register_partial_payment(
    payment_id: int,
    data: PartialPayment,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.update")],
):
    """Register a partial payment (abono). Creates a new payment for the remainder."""
    service = PaymentService(db)
    return await service.register_partial(payment_id, data)


@router.post("/{payment_id}/revert", response_model=PaymentResponse)
async def revert_payment(
    payment_id: int,
    data: RevertPayment,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.reverse")],
):
    """Revert a paid payment back to pending."""
    service = PaymentService(db)
    return await service.revert_payment(payment_id, data)


@router.post("/{payment_id}/mark-problem", response_model=PaymentResponse)
async def mark_payment_problem(
    payment_id: int,
    data: MarkProblem,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("payments.update")],
):
    """Mark a payment as having a problem."""
    service = PaymentService(db)
    return await service.mark_problem(payment_id, data)
