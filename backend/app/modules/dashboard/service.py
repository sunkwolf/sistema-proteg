"""Dashboard business logic — aggregation queries across modules."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ApprovalRequest
from app.models.business import Coverage, Employee, Policy, Vehicle
from app.models.collections import Card
from app.models.enums import (
    ApprovalStatusType,
    CardStatusType,
    PaymentProposalStatusType,
    PaymentStatusType,
    PolicyStatusType,
    ServiceStatusType,
    ShiftOrderType,
)
from app.models.incidents import AdjusterShift, Incident, TowService
from app.models.payments import Payment, PaymentProposal

from app.modules.dashboard.schemas import (
    CollectionDashboard,
    CollectionTrend,
    CollectorPerformance,
    CoverageBreakdown,
    DashboardAlert,
    DashboardSummary,
    GeneralDashboard,
    IncidentsByStatus,
    IncidentsDashboard,
    PaymentMethodSummary,
    RecentActivity,
    SalesDashboard,
    SalesMonthly,
    TopSeller,
    VehicleTypeBreakdown,
)


class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── General dashboard ─────────────────────────────────────────────

    async def get_general(self) -> GeneralDashboard:
        summary = await self._get_summary()
        incidents = await self._get_incidents_summary()
        alerts = await self._get_alerts()
        activity = await self._get_recent_activity()
        return GeneralDashboard(
            summary=summary,
            incidents=incidents,
            alerts=alerts,
            recent_activity=activity,
        )

    # ── Summary KPIs ──────────────────────────────────────────────────

    async def _get_summary(self) -> DashboardSummary:
        today = date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        in_30d = today + timedelta(days=30)

        # Policies today
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date == today
            )
        )
        policies_today = r.scalar_one()

        # Policies this month
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date >= month_start,
                Policy.sale_date <= today,
            )
        )
        policies_this_month = r.scalar_one()

        # Policies this year
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date >= year_start,
                Policy.sale_date <= today,
            )
        )
        policies_this_year = r.scalar_one()

        # Active policies
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.ACTIVE
            )
        )
        active_policies = r.scalar_one()

        # Morosa policies
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.MOROSA
            )
        )
        morosa_policies = r.scalar_one()

        # Pending proposals
        r = await self.session.execute(
            select(func.count(PaymentProposal.id)).where(
                PaymentProposal.draft_status == PaymentProposalStatusType.ACTIVE
            )
        )
        pending_proposals = r.scalar_one()

        # Upcoming renewals in 30 days
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.ACTIVE,
                Policy.expiration_date >= today,
                Policy.expiration_date <= in_30d,
            )
        )
        upcoming_renewals_30d = r.scalar_one()

        # Overdue payments total
        r = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == PaymentStatusType.OVERDUE
            )
        )
        overdue_payments_total = r.scalar_one()

        return DashboardSummary(
            policies_today=policies_today,
            policies_this_month=policies_this_month,
            policies_this_year=policies_this_year,
            active_policies=active_policies,
            morosa_policies=morosa_policies,
            pending_proposals=pending_proposals,
            upcoming_renewals_30d=upcoming_renewals_30d,
            overdue_payments_total=Decimal(str(overdue_payments_total)),
        )

    # ── Incidents summary ─────────────────────────────────────────────

    async def _get_incidents_summary(self) -> IncidentsDashboard:
        today = date.today()

        # Open incidents (pending + in_progress)
        r = await self.session.execute(
            select(func.count(Incident.id)).where(
                Incident.service_status.in_([
                    ServiceStatusType.PENDING,
                    ServiceStatusType.IN_PROGRESS,
                ])
            )
        )
        open_incidents = r.scalar_one()

        # By status
        r = await self.session.execute(
            select(
                Incident.service_status,
                func.count(Incident.id),
            )
            .group_by(Incident.service_status)
        )
        by_status = []
        for status_val, cnt in r.all():
            s = status_val.value if hasattr(status_val, "value") else str(status_val)
            by_status.append(IncidentsByStatus(status=s, count=cnt))

        # Active tow services
        r = await self.session.execute(
            select(func.count(TowService.id)).where(
                TowService.service_status.in_([
                    ServiceStatusType.PENDING,
                    ServiceStatusType.IN_PROGRESS,
                ])
            )
        )
        active_tow = r.scalar_one()

        # Adjusters on duty today
        r = await self.session.execute(
            select(func.count(AdjusterShift.id)).where(
                AdjusterShift.shift_date == today,
                AdjusterShift.shift_order != ShiftOrderType.REST,
            )
        )
        adjusters_on_duty = r.scalar_one()

        return IncidentsDashboard(
            open_incidents=open_incidents,
            by_status=by_status,
            active_tow_services=active_tow,
            adjusters_on_duty_today=adjusters_on_duty,
        )

    # ── Alerts ────────────────────────────────────────────────────────

    async def _get_alerts(self) -> list[DashboardAlert]:
        alerts: list[DashboardAlert] = []
        today = date.today()
        two_days_ago = today - timedelta(days=2)

        # Pending approval requests older than 48h
        r = await self.session.execute(
            select(func.count(ApprovalRequest.id)).where(
                ApprovalRequest.status == ApprovalStatusType.PENDING,
                ApprovalRequest.created_at <= datetime.combine(two_days_ago, datetime.min.time()),
            )
        )
        stale_approvals = r.scalar_one()
        if stale_approvals > 0:
            alerts.append(DashboardAlert(
                severity="critical",
                category="approvals",
                message=f"{stale_approvals} solicitudes pendientes con mas de 48h sin revisar",
                count=stale_approvals,
            ))

        # Overdue payments
        r = await self.session.execute(
            select(func.count(Payment.id)).where(
                Payment.status == PaymentStatusType.OVERDUE
            )
        )
        overdue_count = r.scalar_one()
        if overdue_count > 0:
            alerts.append(DashboardAlert(
                severity="warning",
                category="payments",
                message=f"{overdue_count} pagos vencidos",
                count=overdue_count,
            ))

        # Morosa policies
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.MOROSA
            )
        )
        morosa_count = r.scalar_one()
        if morosa_count > 0:
            alerts.append(DashboardAlert(
                severity="warning",
                category="policies",
                message=f"{morosa_count} polizas en estado morosa",
                count=morosa_count,
            ))

        # Policies expiring in 7 days
        in_7d = today + timedelta(days=7)
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.ACTIVE,
                Policy.expiration_date >= today,
                Policy.expiration_date <= in_7d,
            )
        )
        expiring_soon = r.scalar_one()
        if expiring_soon > 0:
            alerts.append(DashboardAlert(
                severity="info",
                category="renewals",
                message=f"{expiring_soon} polizas vencen en los proximos 7 dias",
                count=expiring_soon,
            ))

        return alerts

    # ── Recent activity ───────────────────────────────────────────────

    async def _get_recent_activity(self, limit: int = 10) -> list[RecentActivity]:
        activities: list[RecentActivity] = []

        # Recent policies
        r = await self.session.execute(
            select(Policy.folio, Policy.created_at)
            .order_by(Policy.created_at.desc())
            .limit(limit)
        )
        for folio, ts in r.all():
            activities.append(RecentActivity(
                type="policy",
                description=f"Poliza #{folio} creada",
                timestamp=ts,
            ))

        # Recent payments
        r = await self.session.execute(
            select(Payment.id, Payment.amount, Payment.created_at)
            .where(Payment.status == PaymentStatusType.PAID)
            .order_by(Payment.created_at.desc())
            .limit(limit)
        )
        for pid, amt, ts in r.all():
            activities.append(RecentActivity(
                type="payment",
                description=f"Pago #{pid} por ${amt} registrado",
                timestamp=ts,
            ))

        # Recent incidents
        r = await self.session.execute(
            select(Incident.report_number, Incident.created_at)
            .order_by(Incident.created_at.desc())
            .limit(limit)
        )
        for rn, ts in r.all():
            activities.append(RecentActivity(
                type="incident",
                description=f"Siniestro {rn} reportado",
                timestamp=ts,
            ))

        # Sort all by timestamp desc, take top N
        activities.sort(key=lambda a: a.timestamp, reverse=True)
        return activities[:limit]

    # ── Sales dashboard ───────────────────────────────────────────────

    async def get_sales(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        seller_id: int | None = None,
    ) -> SalesDashboard:
        today = date.today()
        if date_from is None:
            date_from = today.replace(month=1, day=1)
        if date_to is None:
            date_to = today
        month_start = today.replace(day=1)

        # Base filter
        base_filters = [
            Policy.sale_date >= date_from,
            Policy.sale_date <= date_to,
        ]
        if seller_id is not None:
            base_filters.append(Policy.seller_id == seller_id)

        # Policies today
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date == today,
                *([] if seller_id is None else [Policy.seller_id == seller_id]),
            )
        )
        policies_today = r.scalar_one()

        # Policies this month
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date >= month_start,
                Policy.sale_date <= today,
                *([] if seller_id is None else [Policy.seller_id == seller_id]),
            )
        )
        policies_this_month = r.scalar_one()

        # Policies this year
        year_start = today.replace(month=1, day=1)
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.sale_date >= year_start,
                Policy.sale_date <= today,
                *([] if seller_id is None else [Policy.seller_id == seller_id]),
            )
        )
        policies_this_year = r.scalar_one()

        # Monthly trend
        r = await self.session.execute(
            select(
                func.to_char(Policy.sale_date, "YYYY-MM").label("month"),
                func.count(Policy.id),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .join(Payment, Payment.policy_id == Policy.id, isouter=True)
            .where(
                *base_filters,
                Payment.payment_number == 1,  # First payment = sale amount
            )
            .group_by(func.to_char(Policy.sale_date, "YYYY-MM"))
            .order_by(func.to_char(Policy.sale_date, "YYYY-MM"))
        )
        monthly_trend = [
            SalesMonthly(month=m, count=c, total_amount=Decimal(str(a)))
            for m, c, a in r.all()
        ]

        # Top sellers
        r = await self.session.execute(
            select(
                Employee.id,
                Employee.full_name,
                func.count(Policy.id),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .join(Policy, Policy.seller_id == Employee.id)
            .join(Payment, Payment.policy_id == Policy.id, isouter=True)
            .where(
                Policy.sale_date >= date_from,
                Policy.sale_date <= date_to,
                Payment.payment_number == 1,
            )
            .group_by(Employee.id, Employee.full_name)
            .order_by(func.count(Policy.id).desc())
            .limit(10)
        )
        top_sellers = [
            TopSeller(seller_id=sid, seller_name=sn, policies_count=pc, total_amount=Decimal(str(ta)))
            for sid, sn, pc, ta in r.all()
        ]

        # Coverage breakdown
        r = await self.session.execute(
            select(
                Coverage.name,
                func.count(Policy.id),
            )
            .join(Policy, Policy.coverage_id == Coverage.id)
            .where(*base_filters)
            .group_by(Coverage.name)
            .order_by(func.count(Policy.id).desc())
        )
        coverage_breakdown = [
            CoverageBreakdown(coverage_name=cn, count=c)
            for cn, c in r.all()
        ]

        # Vehicle type breakdown
        r = await self.session.execute(
            select(
                Vehicle.vehicle_type,
                func.count(Policy.id),
            )
            .join(Policy, Policy.vehicle_id == Vehicle.id)
            .where(*base_filters)
            .group_by(Vehicle.vehicle_type)
            .order_by(func.count(Policy.id).desc())
        )
        vehicle_type_breakdown = [
            VehicleTypeBreakdown(
                vehicle_type=vt.value if hasattr(vt, "value") else str(vt) if vt else "unknown",
                count=c,
            )
            for vt, c in r.all()
        ]

        return SalesDashboard(
            policies_today=policies_today,
            policies_this_month=policies_this_month,
            policies_this_year=policies_this_year,
            monthly_trend=monthly_trend,
            top_sellers=top_sellers,
            coverage_breakdown=coverage_breakdown,
            vehicle_type_breakdown=vehicle_type_breakdown,
        )

    # ── Collection dashboard ──────────────────────────────────────────

    async def get_collection(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> CollectionDashboard:
        today = date.today()
        if date_from is None:
            date_from = today.replace(month=1, day=1)
        if date_to is None:
            date_to = today
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        paid_filter = Payment.status == PaymentStatusType.PAID

        # Income today
        r = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                paid_filter,
                Payment.actual_date == today,
            )
        )
        income_today = Decimal(str(r.scalar_one()))

        # Income this month
        r = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                paid_filter,
                Payment.actual_date >= month_start,
                Payment.actual_date <= today,
            )
        )
        income_this_month = Decimal(str(r.scalar_one()))

        # Income this year
        r = await self.session.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                paid_filter,
                Payment.actual_date >= year_start,
                Payment.actual_date <= today,
            )
        )
        income_this_year = Decimal(str(r.scalar_one()))

        # Active policies
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.ACTIVE
            )
        )
        total_active = r.scalar_one()

        # Morosa
        r = await self.session.execute(
            select(func.count(Policy.id)).where(
                Policy.status == PolicyStatusType.MOROSA
            )
        )
        morosa_count = r.scalar_one()
        morosa_pct = Decimal("0.00")
        if total_active + morosa_count > 0:
            morosa_pct = round(
                Decimal(morosa_count * 100) / Decimal(total_active + morosa_count), 2
            )

        # Pending proposals
        r = await self.session.execute(
            select(func.count(PaymentProposal.id)).where(
                PaymentProposal.draft_status == PaymentProposalStatusType.ACTIVE
            )
        )
        pending_proposals = r.scalar_one()

        # Collector performance (this month)
        r = await self.session.execute(
            select(
                Employee.id,
                Employee.full_name,
                func.count(Card.id).filter(Card.status == CardStatusType.ACTIVE),
                func.count(Payment.id).filter(
                    Payment.actual_date >= month_start,
                    Payment.actual_date <= today,
                    paid_filter,
                ),
                func.coalesce(
                    func.sum(Payment.amount).filter(
                        Payment.actual_date >= month_start,
                        Payment.actual_date <= today,
                        paid_filter,
                    ),
                    0,
                ),
            )
            .join(Card, Card.current_holder == Employee.full_name, isouter=True)
            .join(Payment, Payment.collector_id == Employee.id, isouter=True)
            .where(Employee.es_cobrador == True)  # noqa: E712
            .group_by(Employee.id, Employee.full_name)
            .order_by(func.count(Payment.id).desc())
        )
        collectors = [
            CollectorPerformance(
                collector_id=cid,
                collector_name=cn,
                assigned_cards=ac,
                monthly_collections=mc,
                amount_collected=Decimal(str(amt)),
            )
            for cid, cn, ac, mc, amt in r.all()
        ]

        # By payment method (date range)
        r = await self.session.execute(
            select(
                Payment.payment_method,
                func.count(Payment.id),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .where(
                paid_filter,
                Payment.actual_date >= date_from,
                Payment.actual_date <= date_to,
            )
            .group_by(Payment.payment_method)
            .order_by(func.count(Payment.id).desc())
        )
        by_method = [
            PaymentMethodSummary(
                method=m.value if hasattr(m, "value") else str(m) if m else "unknown",
                count=c,
                amount=Decimal(str(a)),
            )
            for m, c, a in r.all()
        ]

        # Trend (last 6 months)
        six_months_ago = (today.replace(day=1) - timedelta(days=180)).replace(day=1)
        r = await self.session.execute(
            select(
                func.to_char(Payment.actual_date, "YYYY-MM").label("period"),
                func.count(Payment.id),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .where(
                paid_filter,
                Payment.actual_date >= six_months_ago,
                Payment.actual_date <= today,
            )
            .group_by(func.to_char(Payment.actual_date, "YYYY-MM"))
            .order_by(func.to_char(Payment.actual_date, "YYYY-MM"))
        )
        trend = [
            CollectionTrend(period=p, count=c, amount=Decimal(str(a)))
            for p, c, a in r.all()
        ]

        return CollectionDashboard(
            income_today=income_today,
            income_this_month=income_this_month,
            income_this_year=income_this_year,
            total_active_policies=total_active,
            morosa_count=morosa_count,
            morosa_percentage=morosa_pct,
            pending_proposals=pending_proposals,
            collectors=collectors,
            by_method=by_method,
            trend=trend,
        )

    # ── Incidents dashboard ───────────────────────────────────────────

    async def get_incidents(
        self,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> IncidentsDashboard:
        today = date.today()

        base_filters = []
        if date_from is not None:
            base_filters.append(Incident.report_time >= datetime.combine(date_from, datetime.min.time()))
        if date_to is not None:
            base_filters.append(Incident.report_time <= datetime.combine(date_to, datetime.max.time()))

        # Open incidents
        r = await self.session.execute(
            select(func.count(Incident.id)).where(
                Incident.service_status.in_([
                    ServiceStatusType.PENDING,
                    ServiceStatusType.IN_PROGRESS,
                ]),
                *base_filters,
            )
        )
        open_incidents = r.scalar_one()

        # By status
        r = await self.session.execute(
            select(
                Incident.service_status,
                func.count(Incident.id),
            )
            .where(*base_filters)
            .group_by(Incident.service_status)
        )
        by_status = []
        for sv, cnt in r.all():
            s = sv.value if hasattr(sv, "value") else str(sv)
            by_status.append(IncidentsByStatus(status=s, count=cnt))

        # Active tow services
        r = await self.session.execute(
            select(func.count(TowService.id)).where(
                TowService.service_status.in_([
                    ServiceStatusType.PENDING,
                    ServiceStatusType.IN_PROGRESS,
                ])
            )
        )
        active_tow = r.scalar_one()

        # Adjusters on duty
        r = await self.session.execute(
            select(func.count(AdjusterShift.id)).where(
                AdjusterShift.shift_date == today,
                AdjusterShift.shift_order != ShiftOrderType.REST,
            )
        )
        adjusters = r.scalar_one()

        # Avg response hours (completed incidents with arrival_time)
        r = await self.session.execute(
            select(
                func.avg(
                    extract("epoch", Incident.contact_time - Incident.report_time) / 3600
                )
            ).where(
                Incident.contact_time.isnot(None),
                Incident.report_time.isnot(None),
                *base_filters,
            )
        )
        avg_h = r.scalar_one()
        avg_response = Decimal(str(round(avg_h, 2))) if avg_h is not None else None

        return IncidentsDashboard(
            open_incidents=open_incidents,
            by_status=by_status,
            active_tow_services=active_tow,
            avg_response_hours=avg_response,
            adjusters_on_duty_today=adjusters,
        )
