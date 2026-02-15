"""Business logic for coverages."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Coverage
from app.modules.coverages.repository import CoverageRepository
from app.modules.coverages.schemas import (
    CoverageCreate,
    CoverageListResponse,
    CoveragePaymentSchemesResponse,
    CoverageResponse,
    CoverageUpdate,
    PaymentScheme,
)


class CoverageService:
    def __init__(self, db: AsyncSession):
        self.repo = CoverageRepository(db)

    # ── Serialization ─────────────────────────────────────────────────

    @staticmethod
    def _to_response(c: Coverage) -> CoverageResponse:
        return CoverageResponse(
            id=c.id,
            name=c.name,
            vehicle_type=c.vehicle_type,
            vehicle_key=c.vehicle_key,
            service_type=c.service_type.value if hasattr(c.service_type, "value") else str(c.service_type),
            category=c.category.value if hasattr(c.category, "value") else str(c.category),
            cylinder_capacity=c.cylinder_capacity,
            credit_price=c.credit_price,
            initial_payment=c.initial_payment,
            cash_price=c.cash_price,
            tow_services_included=c.tow_services_included,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────

    async def list_coverages(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        is_active: bool | None = None,
        vehicle_key: int | None = None,
        category: str | None = None,
        service_type: str | None = None,
    ) -> CoverageListResponse:
        coverages, total = await self.repo.list_coverages(
            skip=skip,
            limit=limit,
            is_active=is_active,
            vehicle_key=vehicle_key,
            category=category,
            service_type=service_type,
        )
        return CoverageListResponse(
            items=[self._to_response(c) for c in coverages],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_coverage(self, coverage_id: int) -> CoverageResponse:
        c = await self.repo.get_by_id(coverage_id)
        if c is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cobertura no encontrada",
            )
        return self._to_response(c)

    async def create_coverage(self, data: CoverageCreate) -> CoverageResponse:
        coverage = Coverage(
            name=data.name,
            vehicle_type=data.vehicle_type,
            vehicle_key=data.vehicle_key,
            service_type=data.service_type,
            category=data.category,
            cylinder_capacity=data.cylinder_capacity,
            credit_price=data.credit_price,
            initial_payment=data.initial_payment,
            cash_price=data.cash_price,
            tow_services_included=data.tow_services_included,
            is_active=data.is_active,
        )
        coverage = await self.repo.create(coverage)
        return self._to_response(coverage)

    async def update_coverage(
        self, coverage_id: int, data: CoverageUpdate
    ) -> CoverageResponse:
        c = await self.repo.get_by_id(coverage_id)
        if c is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cobertura no encontrada",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(c, field, value)

        c = await self.repo.update(c)
        return self._to_response(c)

    # ── Search ────────────────────────────────────────────────────────

    async def search_coverages(
        self,
        *,
        vehicle_type: str | None = None,
        name: str | None = None,
        service_type: str | None = None,
        cylinder_capacity: str | None = None,
    ) -> list[CoverageResponse]:
        is_motorcycle = vehicle_type in ("motorcycle", "mototaxi")
        coverages = await self.repo.search_coverages(
            vehicle_type=vehicle_type,
            name=name,
            service_type=service_type,
            cylinder_capacity=cylinder_capacity,
            is_motorcycle=is_motorcycle,
        )
        return [self._to_response(c) for c in coverages]

    # ── Payment Schemes ───────────────────────────────────────────────

    async def get_payment_schemes(
        self, coverage_id: int
    ) -> CoveragePaymentSchemesResponse:
        c = await self.repo.get_by_id(coverage_id)
        if c is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cobertura no encontrada",
            )

        coverage_resp = self._to_response(c)
        schemes: dict[str, PaymentScheme] = {}

        # Cash (contado)
        schemes["cash"] = PaymentScheme(
            total=c.cash_price,
            payments=[{"number": 1, "amount": str(c.cash_price)}],
        )

        # Cash in 2 installments
        half = (c.cash_price / 2).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        remainder = c.cash_price - half
        schemes["cash_2_installments"] = PaymentScheme(
            total=c.cash_price,
            first_payment_editable=True,
            payments=[
                {"number": 1, "amount": str(half)},
                {"number": 2, "amount": str(remainder)},
            ],
        )

        # Credit (7 payments: initial + 6 monthly)
        if c.credit_price > 0:
            monthly_amount = ((c.credit_price - c.initial_payment) / 6).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            payments = [
                {"number": 1, "amount": str(c.initial_payment), "label": "Enganche"}
            ]
            for i in range(2, 8):
                payments.append({"number": i, "amount": str(monthly_amount)})
            schemes["monthly_7"] = PaymentScheme(
                total=c.credit_price,
                payments=payments,
            )

        return CoveragePaymentSchemesResponse(
            coverage=coverage_resp,
            schemes=schemes,
        )
