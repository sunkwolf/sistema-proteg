"""Business logic for policies."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.collections import Card
from app.models.payments import Payment
from app.modules.policies.repository import PolicyRepository
from app.modules.policies.schemas import (
    ChangeSeller,
    ClientSummary,
    CoverageSummary,
    PaymentsSummary,
    PolicyCreate,
    PolicyListResponse,
    PolicyResponse,
    PolicyUpdate,
    SellerSummary,
    VehicleSummary,
)


class PolicyService:
    def __init__(self, db: AsyncSession):
        self.repo = PolicyRepository(db)

    # ── Serialization ─────────────────────────────────────────────────

    @staticmethod
    def _to_response(
        p: Policy, payments_summary: PaymentsSummary | None = None
    ) -> PolicyResponse:
        client = ClientSummary(
            id=p.client.id,
            full_name=p.client.full_name,
        )
        vehicle = VehicleSummary(
            id=p.vehicle.id,
            brand=p.vehicle.brand,
            model_type=p.vehicle.model_type,
            model_year=p.vehicle.model_year,
        )
        coverage = CoverageSummary(
            id=p.coverage.id,
            name=p.coverage.name,
            vehicle_type=p.coverage.vehicle_type,
        )
        seller = None
        if p.seller:
            seller = SellerSummary(
                id=p.seller.id,
                code_name=p.seller.code_name,
                full_name=p.seller.full_name,
            )

        return PolicyResponse(
            id=p.id,
            folio=p.folio,
            renewal_folio=p.renewal_folio,
            client=client,
            vehicle=vehicle,
            coverage=coverage,
            seller=seller,
            service_type=p.service_type.value if hasattr(p.service_type, "value") else p.service_type,
            contract_folio=p.contract_folio,
            effective_date=p.effective_date,
            expiration_date=p.expiration_date,
            sale_date=p.sale_date,
            elaboration_date=p.elaboration_date,
            status=p.status.value if hasattr(p.status, "value") else str(p.status),
            payment_plan=p.payment_plan.value if hasattr(p.payment_plan, "value") else p.payment_plan,
            prima_total=p.prima_total,
            tow_services_available=p.tow_services_available,
            comments=p.comments,
            has_fraud_observation=p.has_fraud_observation,
            has_payment_issues=p.has_payment_issues,
            contract_image_path=p.contract_image_path,
            quote_external_id=p.quote_external_id,
            payments_summary=payments_summary,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────

    async def list_policies(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        seller_id: int | None = None,
        client_id: int | None = None,
        coverage_name: str | None = None,
        effective_date_from: date | None = None,
        effective_date_to: date | None = None,
        search: str | None = None,
        sort_by: str = "folio",
        sort_order: str = "desc",
    ) -> PolicyListResponse:
        policies, total = await self.repo.list_policies(
            skip=skip,
            limit=limit,
            status=status,
            seller_id=seller_id,
            client_id=client_id,
            coverage_name=coverage_name,
            effective_date_from=effective_date_from,
            effective_date_to=effective_date_to,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return PolicyListResponse(
            items=[self._to_response(p) for p in policies],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_policy(self, policy_id: int) -> PolicyResponse:
        p = await self.repo.get_by_id(policy_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )
        summary = await self._build_payments_summary(p.id)
        return self._to_response(p, payments_summary=summary)

    async def get_by_folio(self, folio: int) -> PolicyResponse:
        p = await self.repo.get_by_folio(folio)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada con ese folio",
            )
        summary = await self._build_payments_summary(p.id)
        return self._to_response(p, payments_summary=summary)

    async def create_policy(
        self, data: PolicyCreate, current_user_id: int | None = None
    ) -> PolicyResponse:
        # ── Validations ──────────────────────────────────────────
        if not await self.repo.client_exists(data.client_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cliente no encontrado o eliminado",
            )
        if not await self.repo.vehicle_exists(data.vehicle_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehiculo no encontrado",
            )
        if not await self.repo.coverage_exists_and_active(data.coverage_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cobertura no encontrada o inactiva",
            )
        if data.seller_id is not None:
            if not await self.repo.seller_is_vendedor(data.seller_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El vendedor no existe, no esta activo, o no tiene rol de vendedor",
                )
        if data.contract_folio is not None:
            if await self.repo.contract_folio_exists(data.contract_folio):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe una poliza con contract_folio {data.contract_folio}",
                )

        # ── Determine initial status ─────────────────────────────
        today = date.today()
        if data.effective_date and data.effective_date > today:
            initial_status = "pre_effective"
        else:
            initial_status = "pending"

        # ── Auto-generate folio ──────────────────────────────────
        folio = await self.repo.get_next_folio()

        # ── Get coverage for payment calculation ─────────────────
        coverage = await self.repo.get_coverage(data.coverage_id)

        # ── Create policy ────────────────────────────────────────
        policy = Policy(
            folio=folio,
            client_id=data.client_id,
            vehicle_id=data.vehicle_id,
            coverage_id=data.coverage_id,
            seller_id=data.seller_id,
            service_type=data.service_type,
            contract_folio=data.contract_folio,
            effective_date=data.effective_date,
            expiration_date=data.expiration_date,
            sale_date=today,
            elaboration_date=today,
            status=initial_status,
            payment_plan=data.payment_plan,
            prima_total=data.prima_total,
            tow_services_available=data.tow_services_available,
            contract_image_path=data.contract_image_path,
            quote_external_id=data.quote_external_id,
            comments=data.comments,
            data_entry_user_id=current_user_id,
        )
        policy = await self.repo.create(policy)

        # ── Auto-generate payments ───────────────────────────────
        if data.payment_plan and coverage:
            payments = self._generate_payments(
                policy_id=policy.id,
                seller_id=data.seller_id,
                payment_plan=data.payment_plan,
                coverage=coverage,
                prima_total=data.prima_total,
                effective_date=data.effective_date,
            )
            if payments:
                await self.repo.create_payments(payments)

        # ── Auto-create card with "OFICINA" holder ───────────────
        card = Card(
            policy_id=policy.id,
            current_holder="OFICINA",
            assignment_date=today,
            seller_id=data.seller_id,
        )
        await self.repo.create_card(card)

        summary = await self._build_payments_summary(policy.id)
        return self._to_response(policy, payments_summary=summary)

    async def update_policy(
        self, policy_id: int, data: PolicyUpdate
    ) -> PolicyResponse:
        p = await self.repo.get_by_id(policy_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )

        update_data = data.model_dump(exclude_unset=True)

        # Validate contract_folio uniqueness if changing
        if "contract_folio" in update_data and update_data["contract_folio"] is not None:
            if await self.repo.contract_folio_exists(update_data["contract_folio"], exclude_id=policy_id):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe una poliza con contract_folio {update_data['contract_folio']}",
                )

        for field, value in update_data.items():
            setattr(p, field, value)

        p = await self.repo.update(p)
        summary = await self._build_payments_summary(p.id)
        return self._to_response(p, payments_summary=summary)

    async def change_seller(
        self, policy_id: int, data: ChangeSeller
    ) -> PolicyResponse:
        p = await self.repo.get_by_id(policy_id)
        if p is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )

        if not await self.repo.seller_is_vendedor(data.seller_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El vendedor no existe, no esta activo, o no tiene rol de vendedor",
            )

        p.seller_id = data.seller_id
        p = await self.repo.update(p)

        # Cascade seller change to all payments
        await self.repo.update_payments_seller(policy_id, data.seller_id)

        summary = await self._build_payments_summary(p.id)
        return self._to_response(p, payments_summary=summary)

    # ── Payment generation ────────────────────────────────────────────

    @staticmethod
    def _generate_payments(
        *,
        policy_id: int,
        seller_id: int | None,
        payment_plan: str,
        coverage,
        prima_total: Decimal | None,
        effective_date: date | None,
    ) -> list[Payment]:
        """Generate payment records based on payment plan and coverage prices."""
        from dateutil.relativedelta import relativedelta

        payments: list[Payment] = []
        base_date = effective_date or date.today()

        if payment_plan == "cash":
            amount = prima_total or coverage.cash_price
            payments.append(Payment(
                policy_id=policy_id,
                seller_id=seller_id,
                payment_number=1,
                amount=amount,
                due_date=base_date,
                status="pending",
            ))

        elif payment_plan == "cash_2_installments":
            total = prima_total or coverage.cash_price
            half = (total / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            remainder = total - half
            payments.append(Payment(
                policy_id=policy_id,
                seller_id=seller_id,
                payment_number=1,
                amount=half,
                due_date=base_date,
                status="pending",
            ))
            payments.append(Payment(
                policy_id=policy_id,
                seller_id=seller_id,
                payment_number=2,
                amount=remainder,
                due_date=base_date + relativedelta(months=1),
                status="pending",
            ))

        elif payment_plan == "monthly_7":
            total = prima_total or coverage.credit_price
            initial = coverage.initial_payment
            monthly = ((total - initial) / 6).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

            # Payment 1: enganche
            payments.append(Payment(
                policy_id=policy_id,
                seller_id=seller_id,
                payment_number=1,
                amount=initial,
                due_date=base_date,
                status="pending",
            ))
            # Payments 2-7: monthly
            for i in range(2, 8):
                payments.append(Payment(
                    policy_id=policy_id,
                    seller_id=seller_id,
                    payment_number=i,
                    amount=monthly,
                    due_date=base_date + relativedelta(months=i - 1),
                    status="pending",
                ))

        return payments

    # ── Helpers ───────────────────────────────────────────────────────

    async def _build_payments_summary(self, policy_id: int) -> PaymentsSummary | None:
        payments = await self.repo.get_payments_for_policy(policy_id)
        if not payments:
            return None

        first_amount = payments[0].amount if payments else None
        monthly_amount = None
        if len(payments) > 1:
            monthly_amount = payments[1].amount

        return PaymentsSummary(
            total_payments=len(payments),
            first_payment_amount=first_amount,
            monthly_amount=monthly_amount,
        )
