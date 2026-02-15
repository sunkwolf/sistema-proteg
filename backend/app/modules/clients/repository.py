"""Data access layer for clients."""

from __future__ import annotations

from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint, ST_SetSRID
from sqlalchemy import Select, cast, func, select, text
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

    # ── pg_trgm similarity search ─────────────────────────────────────

    async def search_by_similarity(
        self, query: str, *, limit: int = 20, threshold: float = 0.3
    ) -> list[Client]:
        """Search clients using pg_trgm similarity on name + RFC."""
        full_name = func.concat(
            Client.first_name, " ",
            Client.paternal_surname, " ",
            func.coalesce(Client.maternal_surname, ""),
        )
        similarity = func.similarity(full_name, query)

        stmt = (
            self._base_query()
            .where(Client.deleted_at.is_(None))
            .where(similarity > threshold)
            .order_by(similarity.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    # ── PostGIS nearby search ─────────────────────────────────────────

    async def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 5000,
        limit: int = 50,
    ) -> list[tuple[Client, float]]:
        """Find clients within radius_meters of a point. Returns (client, distance_m)."""
        point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        geog_geom = cast(Address.geom, Geography)
        geog_point = cast(point, Geography)
        distance = ST_Distance(geog_geom, geog_point)

        stmt = (
            self._base_query()
            .join(Address, Client.address_id == Address.id)
            .where(
                Client.deleted_at.is_(None),
                Address.geom.isnot(None),
                ST_DWithin(geog_geom, geog_point, radius_meters),
            )
            .add_columns(distance.label("distance_m"))
            .order_by(distance)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.unique().all()
        return [(row[0], row[1]) for row in rows]
