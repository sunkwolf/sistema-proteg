"""Dashboard endpoints — general, sales, collection, incidents."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.dashboard.schemas import (
    CollectionDashboard,
    GeneralDashboard,
    IncidentsDashboard,
    SalesDashboard,
)
from app.modules.dashboard.service import DashboardService

router = APIRouter()


@router.get("/general", response_model=GeneralDashboard)
async def get_general_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("dashboard.view")],
):
    """Main dashboard: summary KPIs, incidents overview, alerts, activity."""
    service = DashboardService(db)
    return await service.get_general()


@router.get("/sales", response_model=SalesDashboard)
async def get_sales_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("dashboard.view")],
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
    seller_id: int | None = Query(None),
):
    """Sales dashboard: policies, trends, top sellers, breakdowns."""
    service = DashboardService(db)
    return await service.get_sales(
        date_from=date_from, date_to=date_to, seller_id=seller_id
    )


@router.get("/collection", response_model=CollectionDashboard)
async def get_collection_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("dashboard.collection")],
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
):
    """Collection dashboard: income, morosa, collectors, payment methods, trends."""
    service = DashboardService(db)
    return await service.get_collection(date_from=date_from, date_to=date_to)


@router.get("/incidents", response_model=IncidentsDashboard)
async def get_incidents_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("dashboard.view")],
    date_from: date | None = Query(None, alias="from"),
    date_to: date | None = Query(None, alias="to"),
):
    """Incidents dashboard: open incidents, by status, tow services, adjusters."""
    service = DashboardService(db)
    return await service.get_incidents(date_from=date_from, date_to=date_to)
