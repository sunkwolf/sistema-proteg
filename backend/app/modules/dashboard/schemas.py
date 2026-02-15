"""Pydantic schemas for dashboard endpoints."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


# ── Summary (main dashboard) ─────────────────────────────────────────


class DashboardSummary(BaseModel):
    """Top-level KPI cards for the main dashboard."""

    policies_today: int = 0
    policies_this_month: int = 0
    policies_this_year: int = 0
    active_policies: int = 0
    morosa_policies: int = 0
    pending_proposals: int = 0
    upcoming_renewals_30d: int = 0
    overdue_payments_total: Decimal = Decimal("0.00")


# ── Sales ─────────────────────────────────────────────────────────────


class SalesMonthly(BaseModel):
    month: str  # "YYYY-MM"
    count: int = 0
    total_amount: Decimal = Decimal("0.00")


class TopSeller(BaseModel):
    seller_id: int
    seller_name: str
    policies_count: int = 0
    total_amount: Decimal = Decimal("0.00")


class CoverageBreakdown(BaseModel):
    coverage_name: str
    count: int = 0


class VehicleTypeBreakdown(BaseModel):
    vehicle_type: str
    count: int = 0


class SalesDashboard(BaseModel):
    policies_today: int = 0
    policies_this_month: int = 0
    policies_this_year: int = 0
    monthly_trend: list[SalesMonthly] = []
    top_sellers: list[TopSeller] = []
    coverage_breakdown: list[CoverageBreakdown] = []
    vehicle_type_breakdown: list[VehicleTypeBreakdown] = []


# ── Collection ────────────────────────────────────────────────────────


class CollectorPerformance(BaseModel):
    collector_id: int
    collector_name: str
    assigned_cards: int = 0
    monthly_collections: int = 0
    amount_collected: Decimal = Decimal("0.00")


class PaymentMethodSummary(BaseModel):
    method: str
    count: int = 0
    amount: Decimal = Decimal("0.00")


class CollectionTrend(BaseModel):
    period: str  # "YYYY-MM"
    count: int = 0
    amount: Decimal = Decimal("0.00")


class CollectionDashboard(BaseModel):
    income_today: Decimal = Decimal("0.00")
    income_this_month: Decimal = Decimal("0.00")
    income_this_year: Decimal = Decimal("0.00")
    total_active_policies: int = 0
    morosa_count: int = 0
    morosa_percentage: Decimal = Decimal("0.00")
    pending_proposals: int = 0
    collectors: list[CollectorPerformance] = []
    by_method: list[PaymentMethodSummary] = []
    trend: list[CollectionTrend] = []


# ── Incidents ─────────────────────────────────────────────────────────


class IncidentsByStatus(BaseModel):
    status: str
    count: int = 0


class IncidentsDashboard(BaseModel):
    open_incidents: int = 0
    by_status: list[IncidentsByStatus] = []
    active_tow_services: int = 0
    avg_response_hours: Decimal | None = None
    adjusters_on_duty_today: int = 0


# ── Alerts ────────────────────────────────────────────────────────────


class DashboardAlert(BaseModel):
    severity: str  # "critical" | "warning" | "info"
    category: str
    message: str
    count: int = 0


# ── Activity ──────────────────────────────────────────────────────────


class RecentActivity(BaseModel):
    type: str  # "policy" | "payment" | "incident"
    description: str
    timestamp: datetime


# ── Full general dashboard response ──────────────────────────────────


class GeneralDashboard(BaseModel):
    summary: DashboardSummary
    incidents: IncidentsDashboard
    alerts: list[DashboardAlert] = []
    recent_activity: list[RecentActivity] = []
