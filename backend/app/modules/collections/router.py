"""
Collections Module — API Router
Claudy ✨ + Fer — 2026-03-02

Endpoints for the collector mobile app.
"""
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from .service import CollectionService
from .schemas import (
    ApiResponse, DashboardResponse, FolioCard, FolioDetail,
    RouteStop, CashPending,
)

router = APIRouter(prefix="/collections", tags=["Collections"])


def get_service(session: AsyncSession = Depends(get_db)) -> CollectionService:
    return CollectionService(session)


# TODO: Replace hardcoded collector_code with JWT user extraction
# For now, accept it as a query param for testing

@router.get("/dashboard")
async def get_dashboard(
    collector_code: str = Query(default="EDGAR", description="Código del cobrador"),
    svc: CollectionService = Depends(get_service),
):
    data = await svc.get_dashboard(collector_code)
    return ApiResponse(data=data)


@router.get("/cards")
async def get_cards(
    collector_code: str = Query(default="EDGAR"),
    status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    sort: Optional[str] = Query(default=None),
    svc: CollectionService = Depends(get_service),
):
    items = await svc.get_folios(collector_code, status, search, sort)
    return ApiResponse(
        data=items,
        meta={"total": len(items), "page": 1, "per_page": len(items)},
    )


@router.get("/cards/{folio}")
async def get_card_detail(
    folio: int,
    svc: CollectionService = Depends(get_service),
):
    detail = await svc.get_folio_detail(folio)
    if not detail:
        raise HTTPException(status_code=404, detail="Folio no encontrado")
    return ApiResponse(data=detail)


@router.get("/route")
async def get_route(
    collector_code: str = Query(default="EDGAR"),
    svc: CollectionService = Depends(get_service),
):
    stops = await svc.get_route(collector_code)
    return ApiResponse(data=stops)


@router.get("/cash")
async def get_cash(
    collector_code: str = Query(default="EDGAR"),
    svc: CollectionService = Depends(get_service),
):
    data = await svc.get_cash_pending(collector_code)
    return ApiResponse(data=data)


# ── Proposals (stubs — next phase) ──────────────────────────────────────────

class PaymentRegisterRequest(BaseModel):
    folio: str
    payment_number: int
    amount: str
    method: str  # cash, deposit, transfer
    receipt_number: str
    collector_code: str = "EDGAR"  # TODO: from JWT


@router.post("/proposals")
async def create_proposal(
    req: PaymentRegisterRequest,
    svc: CollectionService = Depends(get_service),
):
    """Register a payment collection from the mobile app."""
    try:
        # Map frontend method names to backend enum values
        method_map = {
            "efectivo": "cash",
            "deposito": "deposit",
            "transferencia": "transfer",
            "cash": "cash",
            "deposit": "deposit",
            "transfer": "transfer",
        }
        method = method_map.get(req.method, req.method)

        result = await svc.register_payment(
            folio=int(req.folio),
            payment_number=req.payment_number,
            amount=float(req.amount),
            method=method,
            receipt_number=req.receipt_number,
            collector_code=req.collector_code,
        )
        return ApiResponse(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/proposals/mine")
async def get_my_proposals():
    """TODO: Get proposals submitted by current collector."""
    return ApiResponse(data=[], meta={"total": 0, "page": 1, "per_page": 0})


# ── Visit Notices (stubs) ───────────────────────────────────────────────────

@router.post("/visits")
async def create_visit_notice():
    """TODO: Register a visit notice."""
    raise HTTPException(status_code=501, detail="Próximamente")
