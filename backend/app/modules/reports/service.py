"""Report generation service — queries data and produces Excel workbooks."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Cancellation
from app.models.business import (
    Coverage,
    Employee,
    Policy,
)
from app.models.payments import Payment
from app.models.endorsements import Endorsement, Renewal
from app.models.incidents import Incident, TowService
from app.modules.reports.generators.excel import (
    add_sheet,
    create_workbook,
    workbook_to_bytes,
)


class ReportService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Renewals report (multi-sheet) ──────────────────────────────

    async def generate_renewals_report(
        self,
        *,
        month: str | None = None,
        seller_id: int | None = None,
    ) -> bytes:
        wb = create_workbook()

        # Sheet 1: Renewals
        query = select(Renewal).order_by(Renewal.renewal_date.desc())
        if month:
            # month format: "YYYY-MM"
            query = query.where(
                func.to_char(Renewal.renewal_date, "YYYY-MM") == month
            )
        if seller_id:
            query = query.join(
                Policy, Renewal.old_policy_id == Policy.id
            ).where(Policy.seller_id == seller_id)
        result = await self.session.execute(query)
        renewals = list(result.scalars().all())
        headers = ["ID", "Poliza Anterior", "Poliza Nueva", "Fecha", "Estado", "Comentarios"]
        rows = []
        for r in renewals:
            st = r.status
            if hasattr(st, "value"):
                st = st.value
            rows.append([
                r.id,
                r.old_policy_id,
                r.new_policy_id,
                r.renewal_date,
                st,
                r.comments,
            ])
        add_sheet(wb, "Renovaciones", headers, rows)

        # Sheet 2: Endorsements
        query2 = select(Endorsement).order_by(Endorsement.request_date.desc())
        result2 = await self.session.execute(query2)
        endorsements = list(result2.scalars().all())
        headers2 = ["ID", "Poliza", "Tipo", "Fecha Solicitud", "Estado", "Comentarios"]
        rows2 = []
        for e in endorsements:
            et = e.endorsement_type
            if hasattr(et, "value"):
                et = et.value
            es = e.status
            if hasattr(es, "value"):
                es = es.value
            rows2.append([
                e.id,
                e.policy_id,
                et,
                e.request_date,
                es,
                e.comments,
            ])
        add_sheet(wb, "Endosos", headers2, rows2)

        # Sheet 3: Tow services
        query3 = select(TowService).order_by(TowService.created_at.desc())
        result3 = await self.session.execute(query3)
        tows = list(result3.scalars().all())
        headers3 = ["ID", "Poliza", "Numero Reporte", "Estado", "Origen", "Destino", "Fecha"]
        rows3 = []
        for t in tows:
            ss = t.service_status
            if hasattr(ss, "value"):
                ss = ss.value
            rows3.append([
                t.id,
                t.policy_id,
                t.report_number,
                ss,
                t.origin_address,
                t.destination_address,
                t.created_at,
            ])
        add_sheet(wb, "Gruas", headers3, rows3)

        # Sheet 4: Incidents
        query4 = select(Incident).order_by(Incident.created_at.desc())
        result4 = await self.session.execute(query4)
        incidents = list(result4.scalars().all())
        headers4 = ["ID", "Poliza", "Numero Reporte", "Tipo", "Estado", "Fecha"]
        rows4 = []
        for i in incidents:
            it = i.incident_type
            if hasattr(it, "value"):
                it = it.value
            ss = i.service_status
            if hasattr(ss, "value"):
                ss = ss.value
            rows4.append([
                i.id,
                i.policy_id,
                i.report_number,
                it,
                ss,
                i.created_at,
            ])
        add_sheet(wb, "Siniestros", headers4, rows4)

        return workbook_to_bytes(wb)

    # ── Collections report ─────────────────────────────────────────

    async def generate_collections_report(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        collector_id: int | None = None,
    ) -> bytes:
        wb = create_workbook()
        query = select(Payment).order_by(Payment.due_date.asc())
        if date_from:
            query = query.where(Payment.due_date >= date_from)
        if date_to:
            query = query.where(Payment.due_date <= date_to)
        if collector_id:
            query = query.where(Payment.collector_id == collector_id)

        result = await self.session.execute(query)
        payments = list(result.scalars().all())

        headers = [
            "ID", "Poliza", "Num. Pago", "Monto", "Fecha Limite",
            "Fecha Real", "Estado", "Metodo Pago",
        ]
        rows = []
        for p in payments:
            st = p.status
            if hasattr(st, "value"):
                st = st.value
            rows.append([
                p.id,
                p.policy_id,
                p.payment_number,
                p.amount,
                p.due_date,
                p.actual_date,
                st,
                p.payment_method,
            ])
        add_sheet(wb, "Cobranza", headers, rows)
        return workbook_to_bytes(wb)

    # ── Sales report ───────────────────────────────────────────────

    async def generate_sales_report(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        seller_id: int | None = None,
    ) -> bytes:
        wb = create_workbook()
        query = select(Policy).order_by(Policy.created_at.desc())
        if date_from:
            query = query.where(Policy.effective_date >= date_from)
        if date_to:
            query = query.where(Policy.effective_date <= date_to)
        if seller_id:
            query = query.where(Policy.seller_id == seller_id)

        result = await self.session.execute(query)
        policies = list(result.scalars().all())

        headers = [
            "ID", "Folio", "Cliente", "Vehiculo", "Vendedor",
            "Prima Total", "Vigencia Inicio", "Vigencia Fin", "Estado",
        ]
        rows = []
        for p in policies:
            st = p.status
            if hasattr(st, "value"):
                st = st.value
            rows.append([
                p.id,
                p.folio,
                p.client_id,
                p.vehicle_id,
                p.seller_id,
                p.prima_total,
                p.effective_date,
                p.expiration_date,
                st,
            ])
        add_sheet(wb, "Ventas", headers, rows)
        return workbook_to_bytes(wb)

    # ── Payment proposals report ───────────────────────────────────

    async def generate_payment_proposals_report(
        self,
        *,
        report_date: date | None = None,
    ) -> bytes:
        wb = create_workbook()
        target = report_date or date.today()
        query = (
            select(Payment)
            .where(Payment.actual_date == target)
            .order_by(Payment.policy_id.asc())
        )
        result = await self.session.execute(query)
        payments = list(result.scalars().all())

        headers = [
            "ID", "Poliza", "Num. Pago", "Monto",
            "Fecha Real", "Vendedor", "Recibo",
        ]
        rows = []
        for p in payments:
            rows.append([
                p.id,
                p.policy_id,
                p.payment_number,
                p.amount,
                p.actual_date,
                None,
                p.receipt_number,
            ])
        add_sheet(wb, "Pagos del Dia", headers, rows)
        return workbook_to_bytes(wb)

    # ── Overdue payments report ────────────────────────────────────

    async def generate_overdue_report(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> bytes:
        wb = create_workbook()
        query = (
            select(Payment)
            .where(Payment.status.in_(["late", "overdue"]))
            .order_by(Payment.due_date.asc())
        )
        if date_from:
            query = query.where(Payment.due_date >= date_from)
        if date_to:
            query = query.where(Payment.due_date <= date_to)

        result = await self.session.execute(query)
        payments = list(result.scalars().all())

        headers = [
            "ID", "Poliza", "Num. Pago", "Monto", "Fecha Limite",
            "Estado", "Dias Atraso",
        ]
        today = date.today()
        rows = []
        for p in payments:
            st = p.status
            if hasattr(st, "value"):
                st = st.value
            days_late = (today - p.due_date).days if p.due_date else 0
            rows.append([
                p.id,
                p.policy_id,
                p.payment_number,
                p.amount,
                p.due_date,
                st,
                days_late,
            ])
        add_sheet(wb, "Morosos", headers, rows)
        return workbook_to_bytes(wb)

    # ── Commissions report ─────────────────────────────────────────

    async def generate_commissions_report(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> bytes:
        wb = create_workbook()
        # Commission calculation depends on commission_rate table + paid payments
        # For now, generate basic seller payment summary
        query = (
            select(
                Policy.seller_id,
                func.count(Payment.id).label("total_payments"),
                func.sum(Payment.amount).label("total_amount"),
            )
            .join(Payment, Payment.policy_id == Policy.id)
            .where(Payment.status == "paid")
            .group_by(Policy.seller_id)
            .order_by(Policy.seller_id.asc())
        )
        if date_from:
            query = query.where(Payment.actual_date >= date_from)
        if date_to:
            query = query.where(Payment.actual_date <= date_to)

        result = await self.session.execute(query)
        rows_data = result.all()

        headers = ["Vendedor ID", "Total Pagos", "Monto Total"]
        rows = [[r[0], r[1], r[2]] for r in rows_data]
        add_sheet(wb, "Comisiones", headers, rows)
        return workbook_to_bytes(wb)

    # ── Cancellations report ───────────────────────────────────────

    async def generate_cancellations_report(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> bytes:
        wb = create_workbook()
        query = select(Cancellation).order_by(Cancellation.cancelled_at.desc())
        if date_from:
            query = query.where(Cancellation.cancelled_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.where(Cancellation.cancelled_at <= datetime.combine(date_to, datetime.max.time()))

        result = await self.session.execute(query)
        cancellations = list(result.scalars().all())

        headers = [
            "ID", "Poliza", "Codigo", "Motivo", "Fecha",
            "Cancelado Por", "Reactivada",
        ]
        rows = []
        for c in cancellations:
            rows.append([
                c.id,
                c.policy_id,
                c.cancellation_code,
                c.reason,
                c.cancelled_at,
                c.cancelled_by_user_id,
                "Si" if c.is_reactivated else "No",
            ])
        add_sheet(wb, "Cancelaciones", headers, rows)
        return workbook_to_bytes(wb)
