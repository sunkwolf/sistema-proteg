"""
StatusUpdater: Recalculates payment and policy statuses.

Business rules:
  Payment transitions (daily at midnight):
    pending  → (due_date < today, delay <= 5d)  → late
    pending  → (due_date < today, delay >  5d)  → overdue
    late     → (delay > 5d)                     → overdue

  Policy status (priority order):
    1. cancelled  — any payment cancelled
    2. morosa     — any payment late or overdue
    3. expired    — today > expiration_date
    4. active     — effective_date <= today <= expiration_date AND all due payments paid
    5. pending    — first payment not yet paid
    6. pre_effective — today < effective_date
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.enums import PaymentStatusType, PolicyStatusType
from app.models.payments import Payment

logger = logging.getLogger(__name__)

PAYMENT_LATE_THRESHOLD_DAYS = 5


async def update_payment_statuses(session: AsyncSession) -> int:
    """Update payment statuses based on due_date vs today. Returns count updated."""
    today = date.today()
    late_cutoff = today - timedelta(days=PAYMENT_LATE_THRESHOLD_DAYS)

    # Get all non-terminal payments
    result = await session.execute(
        select(Payment).where(
            Payment.status.in_([
                PaymentStatusType.PENDING,
                PaymentStatusType.LATE,
            ]),
            Payment.due_date.isnot(None),
        )
    )
    payments = list(result.scalars().all())

    updated = 0
    for p in payments:
        old_status = p.status
        if p.due_date >= today:
            new_status = PaymentStatusType.PENDING
        elif p.due_date >= late_cutoff:
            # 1-5 days late
            new_status = PaymentStatusType.LATE
        else:
            # More than 5 days late
            new_status = PaymentStatusType.OVERDUE

        if new_status != old_status:
            p.status = new_status
            updated += 1

    if updated:
        await session.flush()

    return updated


async def update_policy_statuses(session: AsyncSession) -> int:
    """Recalculate all active policy statuses based on payment states. Returns count updated."""
    today = date.today()

    # Only recalculate non-cancelled policies
    result = await session.execute(
        select(Policy).where(
            Policy.status.notin_([PolicyStatusType.CANCELLED])
        )
    )
    policies = list(result.scalars().all())

    updated = 0
    for policy in policies:
        # Get all payments for this policy
        pay_result = await session.execute(
            select(Payment).where(Payment.policy_id == policy.id)
        )
        payments = list(pay_result.scalars().all())

        new_status = _determine_policy_status(policy, payments, today)

        if new_status != policy.status:
            policy.status = new_status
            updated += 1

    if updated:
        await session.flush()

    return updated


def _determine_policy_status(
    policy: Policy, payments: list[Payment], today: date
) -> PolicyStatusType:
    """Determine policy status based on its payments (priority-based)."""
    if not payments:
        # No payments — keep current or set no_status
        return policy.status

    statuses = {p.status for p in payments}

    # Priority 1: Any cancelled payment → cancelled
    if PaymentStatusType.CANCELLED in statuses:
        return PolicyStatusType.CANCELLED

    # Priority 2: Any late/overdue → morosa
    if PaymentStatusType.LATE in statuses or PaymentStatusType.OVERDUE in statuses:
        return PolicyStatusType.MOROSA

    # Priority 3: Expired
    if policy.expiration_date and today > policy.expiration_date:
        return PolicyStatusType.EXPIRED

    # Priority 4: Active — between dates and all due payments paid
    if (
        policy.effective_date
        and policy.expiration_date
        and policy.effective_date <= today <= policy.expiration_date
    ):
        # Check if all payments that are due have been paid
        all_due_paid = all(
            p.status == PaymentStatusType.PAID
            for p in payments
            if p.due_date and p.due_date <= today
        )
        if all_due_paid:
            return PolicyStatusType.ACTIVE

    # Priority 5: Pending — first payment not yet paid
    first_payment = min(payments, key=lambda p: p.payment_number)
    if first_payment.status == PaymentStatusType.PENDING:
        return PolicyStatusType.PENDING

    # Priority 6: Pre-effective
    if policy.effective_date and today < policy.effective_date:
        return PolicyStatusType.PRE_EFFECTIVE

    # Default: active if we got here with all payments paid
    if all(p.status == PaymentStatusType.PAID for p in payments):
        return PolicyStatusType.ACTIVE

    return policy.status


async def run_status_updater(session: AsyncSession) -> dict:
    """Run full status updater: payments first, then policies."""
    payments_updated = await update_payment_statuses(session)
    policies_updated = await update_policy_statuses(session)

    logger.info(
        "StatusUpdater: %d pagos actualizados, %d polizas actualizadas",
        payments_updated,
        policies_updated,
    )

    return {
        "payments_updated": payments_updated,
        "policies_updated": policies_updated,
    }


async def update_single_policy_status(
    session: AsyncSession, policy_id: int
) -> PolicyStatusType | None:
    """Recalculate status for a single policy. Used on-demand after payment changes."""
    today = date.today()

    result = await session.execute(
        select(Policy).where(Policy.id == policy_id)
    )
    policy = result.scalar_one_or_none()
    if policy is None:
        return None

    pay_result = await session.execute(
        select(Payment).where(Payment.policy_id == policy_id)
    )
    payments = list(pay_result.scalars().all())

    new_status = _determine_policy_status(policy, payments, today)
    if new_status != policy.status:
        policy.status = new_status
        await session.flush()

    return new_status
