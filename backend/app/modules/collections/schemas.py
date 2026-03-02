"""
Collections Module — Pydantic Schemas
Claudy ✨ + Fer — 2026-03-02
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Dashboard ────────────────────────────────────────────────────────────────

class DashboardSummary(BaseModel):
    collections_count: int = 0
    collected_amount: str = "0.00"
    pending_approval: int = 0
    commission_today: str = "0.00"


class DashboardNotification(BaseModel):
    id: int
    type: str
    title: str
    body: str
    read: bool = False
    created_at: str
    deep_link: Optional[str] = None


class DashboardResponse(BaseModel):
    collector_name: str
    date: str
    cash_pending: str = "0.00"
    cash_limit: Optional[str] = None
    cash_pct: float = 0.0
    summary: DashboardSummary
    recent_notifications: List[DashboardNotification] = []


# ── Folios / Cards ───────────────────────────────────────────────────────────

class FolioCard(BaseModel):
    folio: str
    client_name: str
    payment_number: int
    total_payments: int
    amount: str
    due_date: str
    days_overdue: int
    overdue_level: str  # high, mid, low, on_time, collected
    has_proposal_today: bool = False
    proposal_status: Optional[str] = None


class FolioDetailClient(BaseModel):
    name: str
    phone: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None


class FolioDetailVehicle(BaseModel):
    description: str
    plates: str
    color: str


class FolioDetailPolicy(BaseModel):
    coverage_type: str
    start_date: str
    end_date: str
    status: str


class FolioDetailPayment(BaseModel):
    number: int
    total: int
    amount: str
    due_date: str
    days_overdue: int
    partial_paid: str = "0.00"
    partial_remaining: str = "0.00"
    partial_seq: int = 0


class FolioDetail(BaseModel):
    folio: str
    client: FolioDetailClient
    vehicle: FolioDetailVehicle
    policy: FolioDetailPolicy
    current_payment: FolioDetailPayment


# ── Proposals ────────────────────────────────────────────────────────────────

class ProposalCreate(BaseModel):
    folio: str
    payment_number: int
    amount: str
    method: str  # efectivo, deposito, transferencia
    receipt_number: str
    receipt_photo_url: Optional[str] = None
    lat: float
    lng: float
    is_partial: bool = False


class ProposalResponse(BaseModel):
    id: int
    folio: str
    client_name: str
    payment_number: int
    amount: str
    method: str
    receipt_number: str
    receipt_photo_url: Optional[str] = None
    status: str  # pendiente, aprobado, rechazado, corregido
    rejection_reason: Optional[str] = None
    created_at: str
    reviewed_at: Optional[str] = None
    reviewed_by: Optional[str] = None
    is_partial: bool = False
    partial_seq: Optional[int] = None


# ── Visit Notice ─────────────────────────────────────────────────────────────

class VisitNoticeCreate(BaseModel):
    folio: str
    reason: str  # no_estaba, sin_efectivo, pagara_despues, otro
    reason_detail: Optional[str] = None
    photo_url: str
    lat: float
    lng: float


class VisitNoticeResponse(BaseModel):
    id: int
    folio: str
    client_name: str
    reason: str
    reason_detail: Optional[str] = None
    photo_url: str
    created_at: str


# ── Cash ─────────────────────────────────────────────────────────────────────

class CashItem(BaseModel):
    proposal_id: int
    folio: str
    client_name: str
    amount: str
    date: str


class CashDelivery(BaseModel):
    date: str
    amount: str
    confirmed_by: str


class CashPending(BaseModel):
    total: str = "0.00"
    limit: Optional[str] = None
    pct: float = 0.0
    items: List[CashItem] = []
    delivery_history: List[CashDelivery] = []


# ── Route ────────────────────────────────────────────────────────────────────

class RouteStop(BaseModel):
    order: int
    folio: str
    client_name: str
    address: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    status: str = "pending"  # completed, next, pending
    time: Optional[str] = None


# ── API Response Wrapper ─────────────────────────────────────────────────────

class ApiResponse(BaseModel):
    ok: bool = True
    data: object
    meta: Optional[dict] = None
