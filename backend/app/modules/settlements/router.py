"""
Settlement router — API endpoints for liquidaciones

Claudy ✨ — 2026-02-27
Updated to use employee_role_id (new employee structure)
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from .service import SettlementService
from .schemas import (
    SettlementPreview,
    SettlementCreate,
    SettlementBatchCreate,
    SettlementResponse,
    SettlementHistoryResponse,
    SettlementPayRequest,
    ManualDeductionCreate,
    EmployeeBasic,
)

router = APIRouter(prefix="/settlements", tags=["Settlements"])


# ─── List Collectors ───────────────────────────────────────────────────────────

@router.get("/collectors", response_model=List[EmployeeBasic])
def list_active_collectors(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Lista todos los cobradores activos.
    
    Útil para mostrar la lista de cobradores disponibles para liquidar.
    """
    
    service = SettlementService(db)
    return service.get_active_collectors()


# ─── Preview ───────────────────────────────────────────────────────────────────

@router.get("/preview/{employee_role_id}", response_model=SettlementPreview)
def get_settlement_preview(
    employee_role_id: int,
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
        return service.get_preview(employee_role_id, period_start, period_end)
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
    return service.get_all_previews(period_start, period_end)


# ─── Create Settlement ─────────────────────────────────────────────────────────

@router.post("/", response_model=SettlementResponse, status_code=201)
def create_settlement(
    data: SettlementCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Registra una liquidación.
    
    Si se incluye `amount`, se registra como pago parcial.
    Si no se incluye, se registra como pago completo.
    
    Calcula comisiones y deducciones, las guarda,
    y si está pagado completo, actualiza préstamos.
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


# ─── Pay Settlement ────────────────────────────────────────────────────────────

@router.post("/{settlement_id}/pay", response_model=SettlementResponse)
def pay_settlement(
    settlement_id: int,
    data: SettlementPayRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Registra un pago (parcial o total) en una liquidación existente.
    
    Usado cuando una liquidación pendiente o parcial recibe un pago.
    Actualiza amount_paid y status automáticamente.
    """
    
    service = SettlementService(db)
    
    try:
        return service.pay_settlement(settlement_id, data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── History ───────────────────────────────────────────────────────────────────

@router.get("/history/{employee_role_id}", response_model=SettlementHistoryResponse)
def get_settlement_history(
    employee_role_id: int,
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
        return service.get_history(employee_role_id, limit)
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
    Agrega una deducción manual a una liquidación pendiente/parcial.
    
    Usado para adelantos, préstamos, faltantes, etc.
    No funciona si la liquidación ya está pagada completamente.
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
