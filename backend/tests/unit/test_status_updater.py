"""Unit tests for StatusUpdater business logic."""

from datetime import date, timedelta

import pytest

from app.models.enums import PaymentStatusType, PolicyStatusType
from app.modules.policies.status_updater import _determine_policy_status
from tests.conftest import make_payment, make_policy


class TestDeterminePolicyStatus:
    """Test the priority-based policy status determination."""

    def _today(self):
        return date.today()

    # ── Priority 1: Cancelled ────────────────────────────────────────

    def test_cancelled_payment_makes_policy_cancelled(self):
        policy = make_policy(status=PolicyStatusType.ACTIVE)
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
            make_payment(payment_number=2, status=PaymentStatusType.CANCELLED),
        ]
        result = _determine_policy_status(policy, payments, self._today())
        assert result == PolicyStatusType.CANCELLED

    # ── Priority 2: Morosa ───────────────────────────────────────────

    def test_late_payment_makes_policy_morosa(self):
        policy = make_policy(status=PolicyStatusType.ACTIVE)
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
            make_payment(payment_number=2, status=PaymentStatusType.LATE),
        ]
        result = _determine_policy_status(policy, payments, self._today())
        assert result == PolicyStatusType.MOROSA

    def test_overdue_payment_makes_policy_morosa(self):
        policy = make_policy(status=PolicyStatusType.ACTIVE)
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
            make_payment(payment_number=2, status=PaymentStatusType.OVERDUE),
        ]
        result = _determine_policy_status(policy, payments, self._today())
        assert result == PolicyStatusType.MOROSA

    # ── Priority 3: Expired ──────────────────────────────────────────

    def test_expired_policy(self):
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.ACTIVE,
            effective_date=today - timedelta(days=400),
            expiration_date=today - timedelta(days=35),
        )
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.EXPIRED

    # ── Priority 4: Active ───────────────────────────────────────────

    def test_active_policy_all_due_paid(self):
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.PENDING,
            effective_date=today - timedelta(days=30),
            expiration_date=today + timedelta(days=335),
        )
        payments = [
            make_payment(
                payment_number=1,
                status=PaymentStatusType.PAID,
                due_date=today - timedelta(days=30),
            ),
            make_payment(
                payment_number=2,
                status=PaymentStatusType.PENDING,
                due_date=today + timedelta(days=1),  # Not due yet
            ),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.ACTIVE

    # ── Priority 5: Pending ──────────────────────────────────────────

    def test_pending_first_payment_not_paid(self):
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.ACTIVE,
            effective_date=today,
            expiration_date=today + timedelta(days=365),
        )
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PENDING),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.PENDING

    # ── Priority 6: Pre-effective ────────────────────────────────────

    def test_pre_effective_future_date(self):
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.PENDING,
            effective_date=today + timedelta(days=30),
            expiration_date=today + timedelta(days=395),
        )
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.PRE_EFFECTIVE

    # ── Edge cases ───────────────────────────────────────────────────

    def test_no_payments_keeps_current_status(self):
        policy = make_policy(status=PolicyStatusType.ACTIVE)
        result = _determine_policy_status(policy, [], self._today())
        assert result == PolicyStatusType.ACTIVE

    def test_all_paid_defaults_to_active(self):
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.PENDING,
            effective_date=today - timedelta(days=200),
            expiration_date=today - timedelta(days=10),
        )
        # All paid but expired
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
            make_payment(payment_number=2, status=PaymentStatusType.PAID),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.EXPIRED

    def test_cancelled_takes_priority_over_morosa(self):
        """Cancelled should win even if there are also late payments."""
        policy = make_policy(status=PolicyStatusType.ACTIVE)
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.LATE),
            make_payment(payment_number=2, status=PaymentStatusType.CANCELLED),
        ]
        result = _determine_policy_status(policy, payments, self._today())
        assert result == PolicyStatusType.CANCELLED

    def test_morosa_takes_priority_over_expired(self):
        """Late payments should take priority over expiration."""
        today = self._today()
        policy = make_policy(
            status=PolicyStatusType.ACTIVE,
            effective_date=today - timedelta(days=400),
            expiration_date=today - timedelta(days=35),
        )
        payments = [
            make_payment(payment_number=1, status=PaymentStatusType.PAID),
            make_payment(payment_number=2, status=PaymentStatusType.OVERDUE),
        ]
        result = _determine_policy_status(policy, payments, today)
        assert result == PolicyStatusType.MOROSA
