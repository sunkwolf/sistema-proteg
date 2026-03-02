"""
Collections Module — Service (business logic)
Claudy ✨ + Fer — 2026-03-02

Design: policy status is COMPUTED, not stored.
Payment late/overdue is computed from due_date vs today.
"""
from datetime import date, datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import CollectionRepository
from .schemas import (
    DashboardResponse, DashboardSummary,
    FolioCard, FolioDetail,
    FolioDetailClient, FolioDetailVehicle, FolioDetailPolicy, FolioDetailPayment,
    RouteStop, CashPending,
)


def _overdue_level(days: int, status: str) -> str:
    """Compute overdue level from days overdue."""
    if status == "paid":
        return "collected"
    if days <= 0:
        return "on_time"
    if days <= 5:
        return "low"
    if days <= 15:
        return "mid"
    return "high"


def _format_money(amount) -> str:
    if amount is None:
        return "0.00"
    return f"{float(amount):.2f}"


def _computed_policy_status(policy, payments) -> str:
    """Compute real policy status from payments + dates."""
    today = date.today()

    if policy.status in ("cancelled", "suspended"):
        return policy.status
    if policy.expiration_date and today > policy.expiration_date:
        return "expired"
    if policy.effective_date and today < policy.effective_date:
        return "pre_effective"
    if not payments:
        return "pending"

    has_overdue = any(
        p.status == "pending" and p.due_date and p.due_date < today
        for p in payments
    )
    if has_overdue:
        return "morosa"

    return "active"


class CollectionService:
    def __init__(self, session: AsyncSession):
        self.repo = CollectionRepository(session)
        self.session = session

    async def get_dashboard(self, collector_code: str) -> DashboardResponse:
        collector = await self.repo.get_collector_by_code(collector_code)
        if not collector:
            return DashboardResponse(
                collector_name="Desconocido",
                date=date.today().isoformat(),
                summary=DashboardSummary(),
            )

        today = date.today()
        stats = await self.repo.get_collector_stats(collector.id, today)

        return DashboardResponse(
            collector_name=collector.full_name or collector.code_name,
            date=today.isoformat(),
            cash_pending="0.00",  # TODO: compute from approved cash proposals
            cash_limit=None,
            cash_pct=0.0,
            summary=DashboardSummary(
                collections_count=stats["collections_count"],
                collected_amount=_format_money(stats["collected_amount"]),
                pending_approval=0,  # TODO: count pending proposals
                commission_today="0.00",  # TODO: compute commission
            ),
        )

    async def get_folios(
        self,
        collector_code: str,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> List[FolioCard]:
        rows = await self.repo.get_cards_for_collector(
            collector_code, status_filter, search
        )

        cards = []
        today = date.today()

        for card, policy, client, payment in rows:
            if not payment:
                # No pending payment — fully paid
                continue

            days = max(0, (today - payment.due_date).days) if payment.due_date else 0
            total_payments = await self.repo.get_total_payments_for_policy(policy.id)

            cards.append(FolioCard(
                folio=str(policy.folio),
                client_name=client.full_name,
                payment_number=payment.payment_number,
                total_payments=total_payments,
                amount=_format_money(payment.amount),
                due_date=payment.due_date.isoformat() if payment.due_date else "",
                days_overdue=days,
                overdue_level=_overdue_level(days, payment.status),
                has_proposal_today=False,
                proposal_status=None,
            ))

        # Sort
        if sort == "overdue":
            cards.sort(key=lambda c: c.days_overdue, reverse=True)
        elif sort == "amount":
            cards.sort(key=lambda c: float(c.amount), reverse=True)
        # Default: already sorted by due_date from query

        return cards

    async def get_folio_detail(self, folio: int) -> Optional[FolioDetail]:
        policy = await self.repo.get_policy_by_folio(folio)
        if not policy:
            return None

        today = date.today()
        client = policy.client
        vehicle = policy.vehicle
        coverage = policy.coverage

        # Find current (next pending) payment
        current = None
        for p in sorted(policy.payments, key=lambda x: x.payment_number):
            if p.status not in ("paid", "cancelled"):
                current = p
                break

        # If all paid, show last payment
        if not current and policy.payments:
            current = sorted(policy.payments, key=lambda x: x.payment_number)[-1]

        if not current:
            return None

        days = max(0, (today - current.due_date).days) if current.due_date else 0

        return FolioDetail(
            folio=str(policy.folio),
            client=FolioDetailClient(
                name=client.full_name,
                phone=client.phone_1 or "",
                address=client.full_address,
                lat=None,
                lng=None,
            ),
            vehicle=FolioDetailVehicle(
                description=vehicle.description,
                plates=vehicle.plates or "",
                color=vehicle.color or "",
            ),
            policy=FolioDetailPolicy(
                coverage_type=coverage.name,
                start_date=policy.effective_date.isoformat() if policy.effective_date else "",
                end_date=policy.expiration_date.isoformat() if policy.expiration_date else "",
                status=_computed_policy_status(policy, policy.payments),
            ),
            current_payment=FolioDetailPayment(
                number=current.payment_number,
                total=len(policy.payments),
                amount=_format_money(current.amount),
                due_date=current.due_date.isoformat() if current.due_date else "",
                days_overdue=days,
            ),
        )

    async def get_route(self, collector_code: str) -> List[RouteStop]:
        """Build route from cards assigned to collector, ordered by due date."""
        rows = await self.repo.get_cards_for_collector(collector_code)

        stops = []
        for i, (card, policy, client, payment) in enumerate(rows):
            if not payment:
                continue
            stops.append(RouteStop(
                order=i + 1,
                folio=str(policy.folio),
                client_name=client.full_name,
                address=client.full_address,
                lat=None,
                lng=None,
                status="pending",
            ))

        return stops

    async def get_cash_pending(self, collector_code: str) -> CashPending:
        """Cash pending to deliver to office."""
        # TODO: implement when proposals are working
        return CashPending()
