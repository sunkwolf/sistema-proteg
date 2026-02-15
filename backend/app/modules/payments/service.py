"""Business logic for payments."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import (
    MarkProblem,
    PartialPayment,
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
    PaymentUpdate,
    RevertPayment,
)


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.repo = PaymentRepository(db)

    # ── Serialization ─────────────────────────────────────────────────

    @staticmethod
    def _to_response(p: Payment) -> PaymentResponse:
        return PaymentResponse(
            id=p.id,
            policy_id=p.policy_id,
            seller_id=p.seller_id,
            collector_id=p.collector_id,
            user_id=p.user_id,
            payment_number=p.payment_number,
            receipt_number=p.receipt_number,
            due_date=p.due_date,
            actual_date=p.actual_date,
            amount=p.amount,
            payment_method=p.payment_method.value if hasattr(p.payment_method, "value") else p.payment_method,
            office_delivery_status=(
                p.office_delivery_status.value
                if hasattr(p.office_delivery_status, "value")
                else p.office_delivery_status
            ),
            office_delivery_date=p.office_delivery_date,
            policy_delivered=p.policy_delivered,
            comments=p.comments,
            status=p.status.value if hasattr(p.status, "value") else str(p.status),
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────

    async def list_payments(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        status: str | None = None,
        seller_id: int | None = None,
        collector_id: int | None = None,
    ) -> PaymentListResponse:
        payments, total = await self.repo.list_payments(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            status=status,
            seller_id=seller_id,
            collector_id=collector_id,
        )
        return PaymentListResponse(
            items=[self._to_response(p) for p in payments],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_payment(self, payment_id: int) -> PaymentResponse:
        p = await self.repo.get_by_id(payment_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )
        return self._to_response(p)

    async def get_by_policy(self, policy_id: int) -> list[PaymentResponse]:
        payments = await self.repo.get_by_policy(policy_id)
        return [self._to_response(p) for p in payments]

    async def create_payment(self, data: PaymentCreate) -> PaymentResponse:
        payment = Payment(
            policy_id=data.policy_id,
            payment_number=data.payment_number,
            amount=data.amount,
            due_date=data.due_date,
            seller_id=data.seller_id,
            comments=data.comments,
            status="pending",
        )
        payment = await self.repo.create(payment)
        return self._to_response(payment)

    async def update_payment(
        self, payment_id: int, data: PaymentUpdate
    ) -> PaymentResponse:
        p = await self.repo.get_by_id(payment_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate actual_date range: not more than 8 months back or 1 month ahead
        if "actual_date" in update_data and update_data["actual_date"]:
            from dateutil.relativedelta import relativedelta
            today = date.today()
            min_date = today - relativedelta(months=8)
            max_date = today + relativedelta(months=1)
            if update_data["actual_date"] < min_date or update_data["actual_date"] > max_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="actual_date no puede ser mayor a 8 meses atras ni 1 mes adelante",
                )

        # Validate delivery date vs actual date difference
        actual = update_data.get("actual_date", p.actual_date)
        delivery = update_data.get("office_delivery_date", p.office_delivery_date)
        if actual and delivery:
            diff = abs((delivery - actual).days)
            if diff > 30:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Diferencia entre office_delivery_date y actual_date no puede ser mayor a 30 dias",
                )

        for field, value in update_data.items():
            setattr(p, field, value)

        p = await self.repo.update(p)
        return self._to_response(p)

    # ── Partial payment (abono) ───────────────────────────────────────

    async def register_partial(
        self, payment_id: int, data: PartialPayment
    ) -> PaymentResponse:
        p = await self.repo.get_by_id(payment_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )

        if p.amount is None or data.partial_amount >= p.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El abono parcial debe ser menor al monto original",
            )

        original_amount = p.amount
        remaining = original_amount - data.partial_amount

        # Update original payment as paid with partial amount
        p.amount = data.partial_amount
        p.status = "paid"
        p.actual_date = date.today()
        p.receipt_number = data.receipt_number
        p.payment_method = data.payment_method
        p.collector_id = data.collector_id
        p = await self.repo.update(p)

        # Increment subsequent payment numbers
        await self.repo.increment_payment_numbers_after(p.policy_id, p.payment_number)

        # Create new payment for remaining amount
        new_payment = Payment(
            policy_id=p.policy_id,
            seller_id=p.seller_id,
            payment_number=p.payment_number + 1,
            amount=remaining,
            due_date=p.due_date,
            status="pending",
        )
        await self.repo.create(new_payment)

        return self._to_response(p)

    # ── Revert payment ────────────────────────────────────────────────

    async def revert_payment(
        self, payment_id: int, data: RevertPayment
    ) -> PaymentResponse:
        p = await self.repo.get_by_id(payment_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )

        if str(p.status) not in ("paid",) and (not hasattr(p.status, "value") or p.status.value != "paid"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden revertir pagos con status 'paid'",
            )

        p.status = "pending"
        p.actual_date = None
        p.payment_method = None
        p.receipt_number = None
        p.collector_id = None
        p.office_delivery_status = None
        p.office_delivery_date = None
        p.comments = f"REVERTIDO: {data.reason}"
        p = await self.repo.update(p)
        return self._to_response(p)

    # ── Mark problem ──────────────────────────────────────────────────

    async def mark_problem(
        self, payment_id: int, data: MarkProblem
    ) -> PaymentResponse:
        p = await self.repo.get_by_id(payment_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago no encontrado",
            )

        p.comments = f"PROBLEMA: {data.comments}"
        p = await self.repo.update(p)
        return self._to_response(p)
