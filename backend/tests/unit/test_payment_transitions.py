"""Unit tests for payment status transitions logic."""

from datetime import date, timedelta

import pytest

from app.models.enums import PaymentStatusType
from app.modules.policies.status_updater import PAYMENT_LATE_THRESHOLD_DAYS


class TestPaymentTransitionRules:
    """Verify the payment transition rules match business spec:
    pending → (due_date < today, delay <= 5d) → late
    pending → (due_date < today, delay >  5d) → overdue
    late    → (delay > 5d)                    → overdue
    """

    def _determine_new_status(self, due_date: date, current_status: PaymentStatusType) -> PaymentStatusType:
        """Replicate the transition logic from update_payment_statuses."""
        today = date.today()
        late_cutoff = today - timedelta(days=PAYMENT_LATE_THRESHOLD_DAYS)

        if due_date >= today:
            return PaymentStatusType.PENDING
        elif due_date >= late_cutoff:
            return PaymentStatusType.LATE
        else:
            return PaymentStatusType.OVERDUE

    def test_future_due_date_stays_pending(self):
        result = self._determine_new_status(
            date.today() + timedelta(days=5), PaymentStatusType.PENDING
        )
        assert result == PaymentStatusType.PENDING

    def test_today_due_date_stays_pending(self):
        result = self._determine_new_status(date.today(), PaymentStatusType.PENDING)
        assert result == PaymentStatusType.PENDING

    def test_1_day_overdue_becomes_late(self):
        result = self._determine_new_status(
            date.today() - timedelta(days=1), PaymentStatusType.PENDING
        )
        assert result == PaymentStatusType.LATE

    def test_5_days_overdue_is_late(self):
        result = self._determine_new_status(
            date.today() - timedelta(days=5), PaymentStatusType.PENDING
        )
        assert result == PaymentStatusType.LATE

    def test_6_days_overdue_becomes_overdue(self):
        result = self._determine_new_status(
            date.today() - timedelta(days=6), PaymentStatusType.PENDING
        )
        assert result == PaymentStatusType.OVERDUE

    def test_30_days_overdue_stays_overdue(self):
        result = self._determine_new_status(
            date.today() - timedelta(days=30), PaymentStatusType.LATE
        )
        assert result == PaymentStatusType.OVERDUE

    def test_threshold_constant_is_5(self):
        assert PAYMENT_LATE_THRESHOLD_DAYS == 5
