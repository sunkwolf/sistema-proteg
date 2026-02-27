"""
Settlement router — API endpoints for liquidaciones

Claudy ✨ — 2026-02-27
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from .service import SettlementService
from .schemas import (
    SettlementPreview,
    SettlementCreate,
    SettlementBatchCreate,
    SettlementResponse,
    SettlementHistoryResponse,
    ManualDeductionCreate,
)

router = APIRouter(prefix="/settlements", tags=["Settlements"])


# ─── Preview ───────────────────────────────────────────────────────────────────

@router.get("/preview/{collector_id}", response_model=SettlementPreview)
def get_settlement_preview(
    collector_id: int,
    period_start: date = Query(..., description="Inicio del período (YYYY-MM-DD)"),
    period_end: date = Query(..., description="Fin del período (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Calcula el preview de liquidación sin guardar.
    
    Retorna comisiones, deducciones, neto y alertas.
    Usado por la pantalla de detalle de liquidación.
    """
    
    service = SettlementService(db)
    
    try:
        return service.get_preview(collector_id, period_start, period_end)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/preview", response_model=List[SettlementPreview])
def get_all_previews(
    period_start: date = Query(..., description="Inicio del período"),
    period_end: date = Query(..., description="Fin del período"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Calcula previews para TODOS los cobradores activos.
    
    Usado por la pantalla principal de liquidaciones.
    """
    
    service = SettlementService(db)
    
    # TODO: Obtener lista de cobradores activos
    # Por ahora retornamos lista vacía
    collector_ids = []  # service.get_active_collector_ids()
    
    previews = []
    for cid in collector_ids:
        try:
            preview = service.get_preview(cid, period_start, period_end)
            previews.append(preview)
        except ValueError:
            continue
    
    return previews


# ─── Create Settlement ─────────────────────────────────────────────────────────

@router.post("/", response_model=SettlementResponse, status_code=201)
def create_settlement(
    data: SettlementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Registra una liquidación como pagada.
    
    Calcula comisiones y deducciones, las guarda,
    actualiza préstamos y marca pagos como liquidados.
    """
    
    service = SettlementService(db)
    
    try:
        return service.create_settlement(data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch", response_model=List[SettlementResponse], status_code=201)
def create_batch_settlement(
    data: SettlementBatchCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Registra liquidaciones para múltiples cobradores.
    
    Usado por el botón "Pagar todos los listos".
    """
    
    service = SettlementService(db)
    
    try:
        return service.create_batch_settlement(data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── History ───────────────────────────────────────────────────────────────────

@router.get("/history/{collector_id}", response_model=SettlementHistoryResponse)
def get_settlement_history(
    collector_id: int,
    limit: int = Query(10, ge=1, le=100, description="Número máximo de resultados"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Obtiene el historial de liquidaciones de un cobrador.
    
    Ordenado por fecha descendente (más recientes primero).
    """
    
    service = SettlementService(db)
    
    try:
        return service.get_history(collector_id, limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Manual Deduction ──────────────────────────────────────────────────────────

@router.post("/deductions", status_code=201)
def add_manual_deduction(
    data: ManualDeductionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Agrega una deducción manual a una liquidación pendiente.
    
    Usado para adelantos, préstamos, faltantes, etc.
    Solo funciona si la liquidación aún no está pagada.
    """
    
    service = SettlementService(db)
    
    try:
        deduction = service.add_manual_deduction(data)
        return {"id": deduction.id, "message": "Deducción agregada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Get Single Settlement ─────────────────────────────────────────────────────

@router.get("/{settlement_id}", response_model=SettlementResponse)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtiene una liquidación por ID."""
    
    from app.models.settlement import Settlement
    
    settlement = db.get(Settlement, settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Liquidación no encontrada")
    
    service = SettlementService(db)
    return service._to_response(settlement)
