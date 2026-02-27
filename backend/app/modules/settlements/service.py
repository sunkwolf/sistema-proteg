"""
Settlement service — Business logic for liquidaciones

Claudy ✨ — 2026-02-27
Updated to use employee_role_id (new employee structure)
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Employee,
    EmployeeRole,
    CollectorProfile,
    DepartmentType,
)
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
    SettlementPayRequest,
    EmployeeBasic,
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
    
    # ─── Get Collectors ────────────────────────────────────────────────────────
    
    def get_active_collectors(self) -> List[EmployeeBasic]:
        """Obtiene todos los cobradores activos."""
        
        query = (
            select(EmployeeRole, Employee, CollectorProfile)
            .join(Employee, EmployeeRole.employee_id == Employee.id)
            .join(CollectorProfile, EmployeeRole.id == CollectorProfile.employee_role_id)
            .where(
                EmployeeRole.department == DepartmentType.COLLECTION,
                EmployeeRole.is_active == True,
            )
        )
        
        results = self.db.execute(query).all()
        
        return [
            EmployeeBasic(
                employee_id=emp.id,
                employee_role_id=role.id,
                code=profile.code,
                full_name=emp.full_name,
            )
            for role, emp, profile in results
        ]
    
    # ─── Preview ───────────────────────────────────────────────────────────────
    
    def get_preview(
        self,
        employee_role_id: int,
        period_start: date,
        period_end: date,
    ) -> SettlementPreview:
        """
        Calcula el preview de liquidación sin guardar.
        Incluye comisiones, deducciones y alertas.
        """
        
        # Obtener cobrador
        employee_data = self._get_collector_by_role(employee_role_id)
        if not employee_data:
            raise ValueError(f"Cobrador con role_id {employee_role_id} no encontrado")
        
        # Calcular comisiones
        commissions = self._calculate_commissions(employee_role_id, period_start, period_end)
        
        # Calcular deducciones
        deductions = self._calculate_deductions(employee_data['employee_id'], period_start, period_end)
        
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
        
        return SettlementPreview(
            employee=EmployeeBasic(
                employee_id=employee_data['employee_id'],
                employee_role_id=employee_role_id,
                code=employee_data['code'],
                full_name=employee_data['full_name'],
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
    
    def get_all_previews(
        self,
        period_start: date,
        period_end: date,
    ) -> List[SettlementPreview]:
        """Calcula previews para TODOS los cobradores activos."""
        
        collectors = self.get_active_collectors()
        
        previews = []
        for collector in collectors:
            try:
                preview = self.get_preview(collector.employee_role_id, period_start, period_end)
                previews.append(preview)
            except ValueError:
                continue
        
        return previews
    
    # ─── Create Settlement ─────────────────────────────────────────────────────
    
    def create_settlement(
        self,
        data: SettlementCreate,
        paid_by_user_id: int,
    ) -> SettlementResponse:
        """Crea y registra una liquidación."""
        
        # Verificar que no exista ya
        existing = self.db.execute(
            select(Settlement).where(
                Settlement.employee_role_id == data.employee_role_id,
                Settlement.period_start == data.period_start,
                Settlement.period_end == data.period_end,
            )
        ).scalar_one_or_none()
        
        if existing:
            raise ValueError("Ya existe una liquidación para este período")
        
        # Calcular montos
        preview = self.get_preview(data.employee_role_id, data.period_start, data.period_end)
        
        # Determinar monto a pagar
        pay_amount = data.amount if data.amount else preview.net_amount
        
        # Determinar status
        if pay_amount >= preview.net_amount:
            status = SettlementStatus.PAID
            amount_paid = preview.net_amount
        elif pay_amount > 0:
            status = SettlementStatus.PARTIAL
            amount_paid = pay_amount
        else:
            status = SettlementStatus.PENDING
            amount_paid = Decimal("0")
        
        # Crear settlement
        settlement = Settlement(
            employee_role_id=data.employee_role_id,
            period_start=data.period_start,
            period_end=data.period_end,
            commission_regular=preview.commissions.regular.commission,
            commission_cash=preview.commissions.cash.commission,
            commission_delivery=preview.commissions.delivery.commission,
            deduction_fuel=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.FUEL),
            deduction_loan=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.LOAN),
            deduction_shortage=sum(d.amount for d in preview.deductions.items if d.type == DeductionType.SHORTAGE),
            deduction_other=sum(d.amount for d in preview.deductions.items if d.type in [DeductionType.ADVANCE, DeductionType.OTHER]),
            amount_paid=amount_paid,
            status=status,
            payment_method=data.payment_method,
            paid_at=datetime.utcnow() if status != SettlementStatus.PENDING else None,
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
        
        # Actualizar cuotas de préstamos si se pagó completo
        if status == SettlementStatus.PAID:
            self._update_loan_payments(preview.employee.employee_id, data.period_start, data.period_end)
        
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
        for role_id in data.employee_role_ids:
            single = SettlementCreate(
                employee_role_id=role_id,
                period_start=data.period_start,
                period_end=data.period_end,
                payment_method=data.payment_method,
                notes=data.notes,
            )
            result = self.create_settlement(single, paid_by_user_id)
            results.append(result)
        
        return results
    
    # ─── Pay Settlement ────────────────────────────────────────────────────────
    
    def pay_settlement(
        self,
        settlement_id: int,
        data: SettlementPayRequest,
        paid_by_user_id: int,
    ) -> SettlementResponse:
        """Registra un pago (parcial o total) en una liquidación existente."""
        
        settlement = self.db.get(Settlement, settlement_id)
        if not settlement:
            raise ValueError("Liquidación no encontrada")
        
        if settlement.status == SettlementStatus.PAID:
            raise ValueError("Esta liquidación ya está completamente pagada")
        
        # Calcular nuevo monto pagado
        new_amount_paid = settlement.amount_paid + data.amount
        
        # Actualizar settlement
        settlement.amount_paid = new_amount_paid
        settlement.payment_method = data.payment_method
        settlement.paid_by = paid_by_user_id
        
        if data.notes:
            existing_notes = settlement.notes or ""
            settlement.notes = f"{existing_notes}\n[Pago] {data.notes}".strip()
        
        # Actualizar status
        if new_amount_paid >= settlement.net_amount:
            settlement.status = SettlementStatus.PAID
            settlement.paid_at = datetime.utcnow()
            # Actualizar préstamos
            employee_data = self._get_collector_by_role(settlement.employee_role_id)
            if employee_data:
                self._update_loan_payments(employee_data['employee_id'], settlement.period_start, settlement.period_end)
        else:
            settlement.status = SettlementStatus.PARTIAL
        
        self.db.commit()
        self.db.refresh(settlement)
        
        return self._to_response(settlement)
    
    # ─── History ───────────────────────────────────────────────────────────────
    
    def get_history(
        self,
        employee_role_id: int,
        limit: int = 10,
    ) -> SettlementHistoryResponse:
        """Obtiene el historial de liquidaciones de un cobrador."""
        
        employee_data = self._get_collector_by_role(employee_role_id)
        if not employee_data:
            raise ValueError(f"Cobrador con role_id {employee_role_id} no encontrado")
        
        settlements = self.db.execute(
            select(Settlement)
            .where(Settlement.employee_role_id == employee_role_id)
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
                amount_paid=s.amount_paid,
                status=s.status,
                paid_at=s.paid_at,
            )
            for s in settlements
        ]
        
        total_paid = sum(s.amount_paid for s in settlements)
        
        return SettlementHistoryResponse(
            employee=EmployeeBasic(
                employee_id=employee_data['employee_id'],
                employee_role_id=employee_role_id,
                code=employee_data['code'],
                full_name=employee_data['full_name'],
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
            raise ValueError("No se puede modificar una liquidación ya pagada completamente")
        
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
    
    def _get_collector_by_role(self, employee_role_id: int) -> Optional[dict]:
        """Obtiene datos de un cobrador por su employee_role_id."""
        
        query = (
            select(EmployeeRole, Employee, CollectorProfile)
            .join(Employee, EmployeeRole.employee_id == Employee.id)
            .join(CollectorProfile, EmployeeRole.id == CollectorProfile.employee_role_id)
            .where(EmployeeRole.id == employee_role_id)
        )
        
        result = self.db.execute(query).first()
        
        if result:
            role, emp, profile = result
            return {
                'employee_id': emp.id,
                'employee_role_id': role.id,
                'code': profile.code,
                'full_name': emp.full_name,
            }
        return None
    
    def _calculate_commissions(
        self,
        employee_role_id: int,
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
        employee_id: int,
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
                EmployeeLoan.employee_id == employee_id,
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
        
        total = sum(item.amount for item in items)
        
        return DeductionBreakdown(items=items, total=total)
    
    def _update_loan_payments(
        self,
        employee_id: int,
        period_start: date,
        period_end: date,
    ):
        """Actualiza el progreso de préstamos al liquidar."""
        
        loans = self.db.execute(
            select(EmployeeLoan)
            .where(
                EmployeeLoan.employee_id == employee_id,
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
        
        employee_data = self._get_collector_by_role(settlement.employee_role_id)
        
        return SettlementResponse(
            id=settlement.id,
            employee=EmployeeBasic(
                employee_id=employee_data['employee_id'],
                employee_role_id=employee_data['employee_role_id'],
                code=employee_data['code'],
                full_name=employee_data['full_name'],
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
            amount_paid=settlement.amount_paid,
            amount_remaining=settlement.amount_remaining,
            status=settlement.status,
            payment_method=settlement.payment_method,
            paid_at=settlement.paid_at,
            notes=settlement.notes,
            created_at=settlement.created_at,
        )
