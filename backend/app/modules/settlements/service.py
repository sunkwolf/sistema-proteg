"""
Settlement service — Business logic for liquidaciones

Claudy ✨ — 2026-02-27
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.settlement import (
    Settlement,
    SettlementDeduction,
    SettlementPayment,
    EmployeeLoan,
    SettlementStatus,
    SettlementMethod,
    DeductionType,
    LoanStatus,
)
from .schemas import (
    SettlementPreview,
    SettlementCreate,
    SettlementBatchCreate,
    SettlementResponse,
    SettlementHistoryResponse,
    SettlementHistoryItem,
    CollectorBasic,
    PeriodInfo,
    CommissionBreakdown,
    CommissionDetail,
    DeductionBreakdown,
    DeductionItem,
    ManualDeductionCreate,
)


# ─── Commission Rates ──────────────────────────────────────────────────────────

COMMISSION_RATE_REGULAR = Decimal("0.10")   # 10% cobranza normal
COMMISSION_RATE_CASH = Decimal("0.05")      # 5% pagos de contado
COMMISSION_DELIVERY = Decimal("50.00")       # $50 fijos por entrega
FUEL_DEDUCTION_RATE = Decimal("0.50")        # 50% del gasto de gasolina


class SettlementService:
    """Servicio para gestión de liquidaciones."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ─── Preview ───────────────────────────────────────────────────────────────
    
    def get_preview(
        self,
        collector_id: int,
        period_start: date,
        period_end: date,
    ) -> SettlementPreview:
        """
        Calcula el preview de liquidación sin guardar.
        Incluye comisiones, deducciones y alertas.
        """
        
        # Obtener cobrador
        collector = self._get_collector(collector_id)
        if not collector:
            raise ValueError(f"Cobrador {collector_id} no encontrado")
        
        # Calcular comisiones
        commissions = self._calculate_commissions(collector_id, period_start, period_end)
        
        # Calcular deducciones
        deductions = self._calculate_deductions(collector_id, period_start, period_end)
        
        # Calcular neto
        net = commissions.total - deductions.total
        
        # Obtener meta (por ahora hardcodeada, luego de config)
        goal_amount = Decimal("15000.00")  # TODO: obtener de config o collector
        total_collected = commissions.regular.amount_collected + commissions.cash.amount_collected
        goal_percentage = float((total_collected / goal_amount) * 100) if goal_amount > 0 else 0
        
        # Detectar alertas
        alerts = []
        has_alerts = False
        
        if net < 0:
            alerts.append("Saldo negativo — las deducciones superan las comisiones")
            has_alerts = True
        
        # TODO: Verificar diferencias de efectivo sin justificar
        
        return SettlementPreview(
            collector=CollectorBasic(
                id=collector.id,
                code_name=collector.code_name,
                full_name=collector.full_name,
            ),
            period=PeriodInfo(
                start=period_start,
                end=period_end,
                label=self._format_period_label(period_start, period_end),
            ),
            goal_amount=goal_amount,
            total_collected=total_collected,
            goal_percentage=round(goal_percentage, 1),
            commissions=commissions,
            deductions=deductions,
            net_amount=net,
            has_alerts=has_alerts,
            alerts=alerts,
        )
    
    # ─── Create Settlement ─────────────────────────────────────────────────────
    
    def create_settlement(
        self,
        data: SettlementCreate,
        paid_by_user_id: int,
    ) -> SettlementResponse:
        """Crea y registra una liquidación como pagada."""
        
        # Verificar que no exista ya
        existing = self.db.execute(
            select(Settlement).where(
                Settlement.collector_id == data.collector_id,
                Settlement.period_start == data.period_start,
                Settlement.period_end == data.period_end,
            )
        ).scalar_one_or_none()
        
        if existing:
            raise ValueError("Ya existe una liquidación para este período")
        
        # Calcular montos
        preview = self.get_preview(data.collector_id, data.period_start, data.period_end)
        
        # Crear settlement
        settlement = Settlement(
            collector_id=data.collector_id,
            period_start=data.period_start,
            period_end=data.period_end,
            commission_regular=preview.commissions.regular.commission,
            commission_cash=preview.commissions.cash.commission,
            commission_delivery=preview.commissions.delivery.commission,
            deduction_fuel=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.FUEL),
            deduction_loan=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.LOAN),
            deduction_shortage=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.SHORTAGE),
            deduction_other=sum(d.amount for d in preview.deductions.items if d.type in [DeductionType.ADVANCE, DeductionType.OTHER]),
            status=SettlementStatus.PAID,
            payment_method=data.payment_method,
            paid_at=datetime.utcnow(),
            paid_by=paid_by_user_id,
            notes=data.notes,
        )
        
        self.db.add(settlement)
        
        # Registrar deducciones detalladas
        for deduction in preview.deductions.items:
            self.db.add(SettlementDeduction(
                settlement=settlement,
                deduction_type=deduction.type,
                concept=deduction.concept,
                amount=deduction.amount,
                loan_id=deduction.loan_id,
            ))
        
        # Actualizar cuotas de préstamos
        self._update_loan_payments(data.collector_id, data.period_start, data.period_end)
        
        # Marcar pagos como liquidados
        # TODO: Implementar cuando tengamos la relación con payments
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return self._to_response(settlement)
    
    def create_batch_settlement(
        self,
        data: SettlementBatchCreate,
        paid_by_user_id: int,
    ) -> List[SettlementResponse]:
        """Crea liquidaciones para múltiples cobradores."""
        
        results = []
        for collector_id in data.collector_ids:
            single = SettlementCreate(
                collector_id=collector_id,
                period_start=data.period_start,
                period_end=data.period_end,
                payment_method=data.payment_method,
                notes=data.notes,
            )
            result = self.create_settlement(single, paid_by_user_id)
            results.append(result)
        
        return results
    
    # ─── History ───────────────────────────────────────────────────────────────
    
    def get_history(
        self,
        collector_id: int,
        limit: int = 10,
    ) -> SettlementHistoryResponse:
        """Obtiene el historial de liquidaciones de un cobrador."""
        
        collector = self._get_collector(collector_id)
        if not collector:
            raise ValueError(f"Cobrador {collector_id} no encontrado")
        
        settlements = self.db.execute(
            select(Settlement)
            .where(Settlement.collector_id == collector_id)
            .order_by(Settlement.period_end.desc())
            .limit(limit)
        ).scalars().all()
        
        items = [
            SettlementHistoryItem(
                id=s.id,
                period_start=s.period_start,
                period_end=s.period_end,
                period_label=self._format_period_label(s.period_start, s.period_end),
                net_amount=s.net_amount,
                status=s.status,
                paid_at=s.paid_at,
            )
            for s in settlements
        ]
        
        total_paid = sum(s.net_amount for s in settlements if s.status == SettlementStatus.PAID)
        
        return SettlementHistoryResponse(
            collector=CollectorBasic(
                id=collector.id,
                code_name=collector.code_name,
                full_name=collector.full_name,
            ),
            items=items,
            total_paid=total_paid,
        )
    
    # ─── Manual Deduction ──────────────────────────────────────────────────────
    
    def add_manual_deduction(self, data: ManualDeductionCreate) -> SettlementDeduction:
        """Agrega una deducción manual a una liquidación existente."""
        
        settlement = self.db.get(Settlement, data.settlement_id)
        if not settlement:
            raise ValueError("Liquidación no encontrada")
        
        if settlement.status == SettlementStatus.PAID:
            raise ValueError("No se puede modificar una liquidación ya pagada")
        
        deduction = SettlementDeduction(
            settlement_id=data.settlement_id,
            deduction_type=data.type,
            concept=data.concept,
            amount=data.amount,
            notes=data.notes,
        )
        
        self.db.add(deduction)
        
        # Actualizar totales en settlement
        if data.type == DeductionType.FUEL:
            settlement.deduction_fuel += data.amount
        elif data.type == DeductionType.LOAN:
            settlement.deduction_loan += data.amount
        elif data.type == DeductionType.SHORTAGE:
            settlement.deduction_shortage += data.amount
        else:
            settlement.deduction_other += data.amount
        
        self.db.commit()
        self.db.refresh(deduction)
        
        return deduction
    
    # ─── Private Helpers ───────────────────────────────────────────────────────
    
    def _get_collector(self, collector_id: int):
        """Obtiene un cobrador por ID."""
        # TODO: Usar el modelo real de Collector
        from sqlalchemy import text
        result = self.db.execute(
            text("SELECT id, code_name, full_name FROM collector WHERE id = :id"),
            {"id": collector_id}
        ).fetchone()
        
        if result:
            class CollectorRow:
                def __init__(self, row):
                    self.id = row[0]
                    self.code_name = row[1]
                    self.full_name = row[2]
            return CollectorRow(result)
        return None
    
    def _calculate_commissions(
        self,
        collector_id: int,
        period_start: date,
        period_end: date,
    ) -> CommissionBreakdown:
        """Calcula las comisiones del período."""
        
        # TODO: Implementar query real a payments
        # Por ahora retornamos datos de ejemplo
        
        return CommissionBreakdown(
            regular=CommissionDetail(
                count=12,
                amount_collected=Decimal("13200.00"),
                percentage=10.0,
                commission=Decimal("1320.00"),
            ),
            cash=CommissionDetail(
                count=3,
                amount_collected=Decimal("8500.00"),
                percentage=5.0,
                commission=Decimal("425.00"),
            ),
            delivery=CommissionDetail(
                count=5,
                amount_collected=Decimal("0"),
                percentage=None,
                commission=Decimal("250.00"),
            ),
            total=Decimal("1995.00"),
        )
    
    def _calculate_deductions(
        self,
        collector_id: int,
        period_start: date,
        period_end: date,
    ) -> DeductionBreakdown:
        """Calcula las deducciones del período."""
        
        items = []
        
        # 1. Gasolina (50% del gasto)
        # TODO: Query a cargas_combustible
        fuel_total = Decimal("800.00")  # Mock
        if fuel_total > 0:
            items.append(DeductionItem(
                type=DeductionType.FUEL,
                concept="Gasolina (50%)",
                description=f"6 cargas · ${fuel_total} total",
                amount=fuel_total * FUEL_DEDUCTION_RATE,
            ))
        
        # 2. Préstamos activos
        loans = self.db.execute(
            select(EmployeeLoan)
            .where(
                EmployeeLoan.collector_id == collector_id,
                EmployeeLoan.status == LoanStatus.ACTIVE,
            )
        ).scalars().all()
        
        for loan in loans:
            items.append(DeductionItem(
                type=DeductionType.LOAN,
                concept=loan.concept,
                description=f"Cuota {loan.paid_installments + 1} de {loan.total_installments}",
                amount=loan.installment_amount,
                loan_id=loan.id,
            ))
        
        # 3. Diferencias de efectivo
        # TODO: Query a entregas_efectivo
        
        total = sum(item.amount for item in items)
        
        return DeductionBreakdown(items=items, total=total)
    
    def _update_loan_payments(
        self,
        collector_id: int,
        period_start: date,
        period_end: date,
    ):
        """Actualiza el progreso de préstamos al liquidar."""
        
        loans = self.db.execute(
            select(EmployeeLoan)
            .where(
                EmployeeLoan.collector_id == collector_id,
                EmployeeLoan.status == LoanStatus.ACTIVE,
            )
        ).scalars().all()
        
        for loan in loans:
            loan.paid_installments += 1
            loan.remaining_balance -= loan.installment_amount
            
            if loan.paid_installments >= loan.total_installments:
                loan.status = LoanStatus.PAID_OFF
                loan.end_date = period_end
    
    def _format_period_label(self, start: date, end: date) -> str:
        """Formatea el label del período: '2da Quincena · Febrero 2026'."""
        
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        quincena = "1ra" if start.day <= 15 else "2da"
        month = months[end.month - 1]
        year = end.year
        
        return f"{quincena} Quincena · {month} {year}"
    
    def _to_response(self, settlement: Settlement) -> SettlementResponse:
        """Convierte un Settlement a SettlementResponse."""
        
        collector = self._get_collector(settlement.collector_id)
        
        return SettlementResponse(
            id=settlement.id,
            collector=CollectorBasic(
                id=collector.id,
                code_name=collector.code_name,
                full_name=collector.full_name,
            ),
            period_start=settlement.period_start,
            period_end=settlement.period_end,
            commission_regular=settlement.commission_regular,
            commission_cash=settlement.commission_cash,
            commission_delivery=settlement.commission_delivery,
            total_commissions=settlement.total_commissions,
            deduction_fuel=settlement.deduction_fuel,
            deduction_loan=settlement.deduction_loan,
            deduction_shortage=settlement.deduction_shortage,
            deduction_other=settlement.deduction_other,
            total_deductions=settlement.total_deductions,
            net_amount=settlement.net_amount,
            status=settlement.status,
            payment_method=settlement.payment_method,
            paid_at=settlement.paid_at,
            notes=settlement.notes,
            created_at=settlement.created_at,
        )
