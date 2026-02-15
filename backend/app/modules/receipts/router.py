"""Receipt endpoints — batch, assign, verify, cancel, mark-lost."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.receipts.schemas import (
    ReceiptAssign,
    ReceiptAssignResponse,
    ReceiptBatchCreate,
    ReceiptBatchResponse,
    ReceiptListResponse,
    ReceiptResponse,
    ReceiptVerify,
    ReceiptVerifyResponse,
)
from app.modules.receipts.service import ReceiptService

router = APIRouter()


@router.get("", response_model=ReceiptListResponse)
async def list_receipts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    collector_id: int | None = None,
    policy_id: int | None = None,
):
    """List receipts with optional filters and pagination."""
    service = ReceiptService(db)
    return await service.list_receipts(
        skip=skip,
        limit=limit,
        status_filter=status,
        collector_id=collector_id,
        policy_id=policy_id,
    )


@router.get("/by-collector/{collector_id}", response_model=list[ReceiptResponse])
async def get_receipts_by_collector(
    collector_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.read")],
):
    """Get all receipts assigned to a specific collector."""
    service = ReceiptService(db)
    return await service.get_by_collector(collector_id)


@router.get("/by-number/{receipt_number}", response_model=ReceiptResponse)
async def get_receipt_by_number(
    receipt_number: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.read")],
):
    """Search for a receipt by its number."""
    service = ReceiptService(db)
    return await service.get_by_number(receipt_number)


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.read")],
):
    """Get receipt by ID."""
    service = ReceiptService(db)
    return await service.get_receipt(receipt_id)


@router.post("/batch", response_model=ReceiptBatchResponse, status_code=201)
async def create_batch(
    data: ReceiptBatchCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.create_batch")],
):
    """Create a batch of receipt numbers (e.g., A0001–A0100)."""
    service = ReceiptService(db)
    return await service.create_batch(data)


@router.post("/assign", response_model=ReceiptAssignResponse)
async def assign_receipts(
    data: ReceiptAssign,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.assign")],
):
    """Assign receipts to a collector, respecting receipt_limit."""
    service = ReceiptService(db)
    return await service.assign_receipts(data)


@router.post("/verify", response_model=ReceiptVerifyResponse)
async def verify_receipt(
    data: ReceiptVerify,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.use")],
):
    """Verify and use a receipt for a payment."""
    service = ReceiptService(db)
    return await service.verify_receipt(data)


@router.post("/{receipt_id}/cancel", response_model=ReceiptResponse)
async def cancel_receipt(
    receipt_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.cancel")],
):
    """Cancel a receipt."""
    service = ReceiptService(db)
    return await service.cancel_receipt(receipt_id)


@router.post("/{receipt_id}/mark-lost", response_model=ReceiptResponse)
async def mark_receipt_lost(
    receipt_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("receipts.cancel")],
):
    """Mark a receipt as lost."""
    service = ReceiptService(db)
    return await service.mark_lost(receipt_id)
