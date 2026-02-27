"""
Schemas for settlements

Claudy ✨ — 2026-02-27
Updated to use employee_role_id (new structure)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.settlement import SettlementStatus, SettlementMethod, DeductionType


# ─── Employee Info ─────────────────────────────────────────────────────────────

class EmployeeBasic(BaseModel):
    """Información básica del empleado."""
    
    employee_id: int
    employee_role_id: int
    code: str = Field(description="Código del cobrador: C1, C2...")
    full_name: str
    
    class Config:
        from_attributes = True


# ─── Commission Breakdown ──────────────────────────────────────────────────────

class CommissionBreakdown(BaseModel):
    """Desglose de comisiones por tipo."""
    
    regular: "CommissionDetail"
    cash: "CommissionDetail"
    delivery: "CommissionDetail"
    total: Decimal


class CommissionDetail(BaseModel):
    """Detalle de un tipo de comisión."""
    
    count: int = Field(description="Número de cobros/entregas")
    amount_collected: Decimal = Field(description="Monto total cobrado")
    percentage: Optional[float] = Field(None, description="Porcentaje aplicado (si aplica)")
    commission: Decimal = Field(description="Comisión calculada")


# ─── Deduction Breakdown ───────────────────────────────────────────────────────

class DeductionItem(BaseModel):
    """Una deducción individual."""
    
    id: Optional[int] = None
    type: DeductionType
    concept: str
    description: Optional[str] = None
    amount: Decimal
    loan_id: Optional[int] = None


class DeductionBreakdown(BaseModel):
    """Desglose de deducciones."""
    
    items: List[DeductionItem]
    total: Decimal


# ─── Settlement Preview ────────────────────────────────────────────────────────

class SettlementPreview(BaseModel):
    """
    Preview de liquidación — calcula sin guardar.
    Usado por GET /settlements/preview/{employee_role_id}
    """
    
    employee: EmployeeBasic
    period: "PeriodInfo"
    
    # Metas y progreso
    goal_amount: Decimal = Field(description="Meta de cobro del período")
    total_collected: Decimal = Field(description="Total cobrado en el período")
    goal_percentage: float = Field(description="Porcentaje de meta alcanzada")
    
    # Desglose
    commissions: CommissionBreakdown
    deductions: DeductionBreakdown
    
    # Totales
    net_amount: Decimal = Field(description="Neto a pagar")
    
    # Estado
    has_alerts: bool = Field(description="Tiene alertas que revisar")
    alerts: List[str] = Field(default_factory=list)


class PeriodInfo(BaseModel):
    """Información del período de liquidación."""
    
    start: date
    end: date
    label: str = Field(description="Ej: '2da Quincena · Febrero 2026'")


# ─── Settlement Create ─────────────────────────────────────────────────────────

class SettlementCreate(BaseModel):
    """Datos para crear/registrar una liquidación."""
    
    employee_role_id: int
    period_start: date
    period_end: date
    payment_method: SettlementMethod
    amount: Optional[Decimal] = Field(None, description="Monto a pagar (para pagos parciales). None = pago total.")
    notes: Optional[str] = None


class SettlementBatchCreate(BaseModel):
    """Liquidación masiva de múltiples cobradores."""
    
    employee_role_ids: List[int]
    period_start: date
    period_end: date
    payment_method: SettlementMethod
    notes: Optional[str] = None


# ─── Settlement Response ───────────────────────────────────────────────────────

class SettlementResponse(BaseModel):
    """Respuesta de una liquidación creada/consultada."""
    
    id: int
    employee: EmployeeBasic
    
    period_start: date
    period_end: date
    
    commission_regular: Decimal
    commission_cash: Decimal
    commission_delivery: Decimal
    total_commissions: Decimal
    
    deduction_fuel: Decimal
    deduction_loan: Decimal
    deduction_shortage: Decimal
    deduction_other: Decimal
    total_deductions: Decimal
    
    net_amount: Decimal
    amount_paid: Decimal
    amount_remaining: Decimal
    
    status: SettlementStatus
    payment_method: Optional[SettlementMethod]
    paid_at: Optional[datetime]
    notes: Optional[str]
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# ─── Settlement History ────────────────────────────────────────────────────────

class SettlementHistoryItem(BaseModel):
    """Un item del historial de liquidaciones."""
    
    id: int
    period_start: date
    period_end: date
    period_label: str
    net_amount: Decimal
    amount_paid: Decimal
    status: SettlementStatus
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SettlementHistoryResponse(BaseModel):
    """Historial de liquidaciones de un cobrador."""
    
    employee: EmployeeBasic
    items: List[SettlementHistoryItem]
    total_paid: Decimal = Field(description="Total histórico pagado")


# ─── Manual Deduction ──────────────────────────────────────────────────────────

class ManualDeductionCreate(BaseModel):
    """Agregar una deducción manual a una liquidación."""
    
    settlement_id: int
    type: DeductionType
    concept: str
    amount: Decimal
    notes: Optional[str] = None


# ─── Pay Settlement ────────────────────────────────────────────────────────────

class SettlementPayRequest(BaseModel):
    """Registrar un pago (parcial o total) en una liquidación."""
    
    amount: Decimal = Field(description="Monto a pagar")
    payment_method: SettlementMethod
    notes: Optional[str] = None


# Forward refs
CommissionBreakdown.model_rebuild()
SettlementPreview.model_rebuild()
