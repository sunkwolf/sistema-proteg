"""Data access layer for policies."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business import Client, Coverage, Employee, Policy, Vehicle
from app.models.collections import Card
from app.models.payments import Payment


class PolicyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        """Base query with relationships eagerly loaded."""
        return select(Policy).options(
            selectinload(Policy.client),
            selectinload(Policy.vehicle),
            selectinload(Policy.coverage),
            selectinload(Policy.seller),
        )

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            self._base_query().where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    async def get_by_folio(self, folio: int) -> Policy | None:
        result = await self.session.execute(
            self._base_query().where(Policy.folio == folio)
        )
        return result.scalar_one_or_none()

    async def get_next_folio(self) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.max(Policy.folio), 0))
        )
        return result.scalar_one() + 1

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
    ) -> tuple[list[Policy], int]:
        """Return (policies, total_count) with filters."""
        query = self._base_query()
        count_query = select(func.count(Policy.id))

        if status is not None:
            query = query.where(Policy.status == status)
            count_query = count_query.where(Policy.status == status)
        if seller_id is not None:
            query = query.where(Policy.seller_id == seller_id)
            count_query = count_query.where(Policy.seller_id == seller_id)
        if client_id is not None:
            query = query.where(Policy.client_id == client_id)
            count_query = count_query.where(Policy.client_id == client_id)
        if coverage_name is not None:
            query = query.join(Policy.coverage).where(
                Coverage.name.ilike(f"%{coverage_name}%")
            )
            count_query = count_query.join(Coverage).where(
                Coverage.name.ilike(f"%{coverage_name}%")
            )
        if effective_date_from is not None:
            query = query.where(Policy.effective_date >= effective_date_from)
            count_query = count_query.where(Policy.effective_date >= effective_date_from)
        if effective_date_to is not None:
            query = query.where(Policy.effective_date <= effective_date_to)
            count_query = count_query.where(Policy.effective_date <= effective_date_to)
        if search:
            pattern = f"%{search}%"
            # Search in client name or folio (cast to string)
            query = query.join(Policy.client).where(
                Client.full_name.ilike(pattern)
                | cast(Policy.folio, String).ilike(pattern)
            )
            count_query = count_query.join(Client).where(
                Client.full_name.ilike(pattern)
                | cast(Policy.folio, String).ilike(pattern)
            )

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Sorting
        sort_column = {
            "folio": Policy.folio,
            "effective_date": Policy.effective_date,
            "created_at": Policy.created_at,
            "status": Policy.status,
        }.get(sort_by, Policy.folio)

        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        policies = list(result.scalars().unique().all())

        return policies, total

    # ── Validation helpers ────────────────────────────────────────────

    async def client_exists(self, client_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Client.id)).where(
                Client.id == client_id, Client.deleted_at.is_(None)
            )
        )
        return result.scalar_one() > 0

    async def vehicle_exists(self, vehicle_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Vehicle.id)).where(Vehicle.id == vehicle_id)
        )
        return result.scalar_one() > 0

    async def coverage_exists_and_active(self, coverage_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Coverage.id)).where(
                Coverage.id == coverage_id, Coverage.is_active == True  # noqa: E712
            )
        )
        return result.scalar_one() > 0

    async def get_coverage(self, coverage_id: int) -> Coverage | None:
        result = await self.session.execute(
            select(Coverage).where(Coverage.id == coverage_id)
        )
        return result.scalar_one_or_none()

    async def seller_is_vendedor(self, seller_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Employee.id)).where(
                Employee.id == seller_id,
                Employee.es_vendedor == True,  # noqa: E712
                Employee.status == "active",
            )
        )
        return result.scalar_one() > 0

    async def contract_folio_exists(self, contract_folio: int, exclude_id: int | None = None) -> bool:
        query = select(func.count(Policy.id)).where(
            Policy.contract_folio == contract_folio
        )
        if exclude_id is not None:
            query = query.where(Policy.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one() > 0

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, policy: Policy) -> Policy:
        self.session.add(policy)
        await self.session.flush()
        return await self.get_by_id(policy.id)  # type: ignore[return-value]

    async def update(self, policy: Policy) -> Policy:
        await self.session.flush()
        return await self.get_by_id(policy.id)  # type: ignore[return-value]

    # ── Payments ─────────────────────────────────────────────────────

    async def create_payments(self, payments: list[Payment]) -> None:
        self.session.add_all(payments)
        await self.session.flush()

    async def get_payments_for_policy(self, policy_id: int) -> list[Payment]:
        result = await self.session.execute(
            select(Payment)
            .where(Payment.policy_id == policy_id)
            .order_by(Payment.payment_number)
        )
        return list(result.scalars().all())

    async def update_payments_seller(self, policy_id: int, seller_id: int | None) -> None:
        """Cascade seller change to all payments of a policy."""
        payments = await self.get_payments_for_policy(policy_id)
        for p in payments:
            p.seller_id = seller_id
        await self.session.flush()

    # ── Card ─────────────────────────────────────────────────────────

    async def create_card(self, card: Card) -> None:
        self.session.add(card)
        await self.session.flush()

    async def get_payment_count(self, policy_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Payment.id)).where(Payment.policy_id == policy_id)
        )
        return result.scalar_one()
