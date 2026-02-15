"""Report endpoints — Excel generation for various business reports."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.reports.service import ReportService

router = APIRouter()


def _excel_response(data: bytes, filename: str) -> StreamingResponse:
    """Create a streaming Excel file response."""
    import io

    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/renewals")
async def report_renewals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.read")],
    month: str | None = Query(None, pattern=r"^\d{4}-\d{2}$"),
    seller_id: int | None = None,
):
    """Generate renewals report (multi-sheet Excel)."""
    service = ReportService(db)
    data = await service.generate_renewals_report(month=month, seller_id=seller_id)
    return _excel_response(data, "reporte_renovaciones.xlsx")


@router.get("/collections")
async def report_collections(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.read")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    collector_id: int | None = None,
):
    """Generate collections report (Excel)."""
    service = ReportService(db)
    data = await service.generate_collections_report(
        date_from=date_from, date_to=date_to, collector_id=collector_id
    )
    return _excel_response(data, "reporte_cobranza.xlsx")


@router.get("/sales")
async def report_sales(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.read")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    seller_id: int | None = None,
):
    """Generate sales report (Excel)."""
    service = ReportService(db)
    data = await service.generate_sales_report(
        date_from=date_from, date_to=date_to, seller_id=seller_id
    )
    return _excel_response(data, "reporte_ventas.xlsx")


@router.get("/payment-proposals")
async def report_payment_proposals(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.admin")],
    report_date: date | None = Query(None),
):
    """Generate daily payment proposals report (Excel). Requires manager."""
    service = ReportService(db)
    data = await service.generate_payment_proposals_report(report_date=report_date)
    return _excel_response(data, "reporte_pagos_dia.xlsx")


@router.get("/overdue-payments")
async def report_overdue(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.read")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """Generate overdue payments report (Excel)."""
    service = ReportService(db)
    data = await service.generate_overdue_report(date_from=date_from, date_to=date_to)
    return _excel_response(data, "reporte_morosos.xlsx")


@router.get("/commissions")
async def report_commissions(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.admin")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """Generate commissions report (Excel). Requires admin."""
    service = ReportService(db)
    data = await service.generate_commissions_report(
        date_from=date_from, date_to=date_to
    )
    return _excel_response(data, "reporte_comisiones.xlsx")


@router.get("/cancellations")
async def report_cancellations(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("reports.read")],
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """Generate cancellations report (Excel)."""
    service = ReportService(db)
    data = await service.generate_cancellations_report(
        date_from=date_from, date_to=date_to
    )
    return _excel_response(data, "reporte_cancelaciones.xlsx")
