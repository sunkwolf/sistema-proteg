"""Authorization endpoints — payment proposals + generic approval requests."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.authorization.schemas import (
    ApprovalRequestResponse,
    ApprovalReview,
    ProposalCreate,
    ProposalListResponse,
    ProposalResponse,
    ProposalReview,
)
from app.modules.authorization.service import AuthorizationService

router = APIRouter()


# ── Payment Proposals ────────────────────────────────────────────────


@router.get("/payments", response_model=ProposalListResponse)
async def list_proposals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("proposals.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    collector_id: int | None = None,
    policy_id: int | None = None,
):
    """List all payment proposals with optional filters."""
    service = AuthorizationService(db)
    return await service.list_proposals(
        skip=skip,
        limit=limit,
        status_filter=status,
        collector_id=collector_id,
        policy_id=policy_id,
    )


@router.get("/payments/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("proposals.read")],
):
    """Get a payment proposal by ID."""
    service = AuthorizationService(db)
    return await service.get_proposal(proposal_id)


@router.post("/payments", response_model=ProposalResponse, status_code=201)
async def create_proposal(
    data: ProposalCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.create")],
):
    """Create a payment proposal (cobrador submits from field)."""
    service = AuthorizationService(db)
    return await service.create_proposal(data, user_id=user.id)


@router.post(
    "/payments/{proposal_id}/approve", response_model=ProposalResponse
)
async def approve_proposal(
    proposal_id: int,
    data: ProposalReview,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.approve")],
):
    """Approve a payment proposal (applies data to original payment)."""
    service = AuthorizationService(db)
    return await service.approve_proposal(proposal_id, data, reviewer_id=user.id)


@router.post(
    "/payments/{proposal_id}/reject", response_model=ProposalResponse
)
async def reject_proposal(
    proposal_id: int,
    data: ProposalReview,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.reject")],
):
    """Reject a payment proposal."""
    service = AuthorizationService(db)
    return await service.reject_proposal(proposal_id, data, reviewer_id=user.id)


@router.post(
    "/payments/{proposal_id}/cancel", response_model=ProposalResponse
)
async def cancel_proposal(
    proposal_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.create")],
):
    """Cancel a payment proposal (only the creator or an admin)."""
    service = AuthorizationService(db)
    return await service.cancel_proposal(proposal_id, user_id=user.id)


# ── Generic Approval Requests ────────────────────────────────────────


@router.get("/requests/pending", response_model=list[ApprovalRequestResponse])
async def list_pending_approvals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("proposals.read")],
    request_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List pending approval requests."""
    service = AuthorizationService(db)
    result = await service.list_pending_approvals(
        request_type=request_type, skip=skip, limit=limit
    )
    return result["items"]


@router.post(
    "/requests/{request_id}/approve",
    response_model=ApprovalRequestResponse,
)
async def approve_request(
    request_id: int,
    data: ApprovalReview,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.approve")],
):
    """Approve a generic approval request."""
    service = AuthorizationService(db)
    return await service.approve_request(request_id, data, reviewer_id=user.id)


@router.post(
    "/requests/{request_id}/reject",
    response_model=ApprovalRequestResponse,
)
async def reject_request(
    request_id: int,
    data: ApprovalReview,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("proposals.reject")],
):
    """Reject a generic approval request."""
    service = AuthorizationService(db)
    return await service.reject_request(request_id, data, reviewer_id=user.id)
