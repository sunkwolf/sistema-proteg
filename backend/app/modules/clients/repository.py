"""Data access layer for clients."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.business import Client
from app.models.catalog import Address, Municipality


class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Helpers ──────────────────────────────────────────────────────

    def _base_query(self) -> Select:
        return select(Client).options(
            selectinload(Client.address).selectinload(Address.municipality)
        )

    # ── Read ─────────────────────────────────────────────────────────

    async def get_by_id(self, client_id: int) -> Client | None:
        result = await self.session.execute(
            self._base_query().where(
                Client.id == client_id, Client.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list_clients(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        phone: str | None = None,
        municipality_id: int | None = None,
    ) -> tuple[list[Client], int]:
        """Return (clients, total) with filters. Only non-deleted."""
        query = self._base_query().where(Client.deleted_at.is_(None))
        count_query = select(func.count(Client.id)).where(
            Client.deleted_at.is_(None)
        )

        if search:
            pattern = f"%{search}%"
            name_filter = (
                func.concat(
                    Client.first_name,
                    " ",
                    Client.paternal_surname,
                    " ",
                    func.coalesce(Client.maternal_surname, ""),
                ).ilike(pattern)
                | Client.rfc.ilike(pattern)
            )
            query = query.where(name_filter)
            count_query = count_query.where(name_filter)

        if phone:
            phone_filter = (Client.phone_1 == phone) | (Client.phone_2 == phone)
            query = query.where(phone_filter)
            count_query = count_query.where(phone_filter)

        if municipality_id is not None:
            query = query.join(Address, Client.address_id == Address.id).where(
                Address.municipality_id == municipality_id
            )
            count_query = count_query.join(
                Address, Client.address_id == Address.id
            ).where(Address.municipality_id == municipality_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(
            Client.paternal_surname, Client.first_name
        ).offset(skip).limit(limit)
        result = await self.session.execute(query)
        clients = list(result.scalars().unique().all())

        return clients, total

    # ── Create / Update ──────────────────────────────────────────────

    async def create(self, client: Client) -> Client:
        self.session.add(client)
        await self.session.flush()
        return await self.get_by_id(client.id)  # type: ignore[return-value]

    async def update(self, client: Client) -> Client:
        await self.session.flush()
        return await self.get_by_id(client.id)  # type: ignore[return-value]

    # ── Address ──────────────────────────────────────────────────────

    async def create_address(self, address: Address) -> Address:
        self.session.add(address)
        await self.session.flush()
        return address

    async def get_address(self, address_id: int) -> Address | None:
        result = await self.session.execute(
            select(Address)
            .options(selectinload(Address.municipality))
            .where(Address.id == address_id)
        )
        return result.scalar_one_or_none()

    async def municipality_exists(self, municipality_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(Municipality.id)).where(
                Municipality.id == municipality_id
            )
        )
        return result.scalar_one() > 0
