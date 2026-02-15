"""Business logic for clients."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Client
from app.models.catalog import Address
from app.modules.clients.repository import ClientRepository
from app.modules.clients.schemas import (
    AddressInput,
    AddressResponse,
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
    MunicipalityInfo,
    NearbyClientResult,
    WhatsAppVerifyResponse,
)


class ClientService:
    def __init__(self, db: AsyncSession):
        self.repo = ClientRepository(db)

    # ── Serialization helpers ────────────────────────────────────────

    @staticmethod
    def _address_response(addr: Address | None) -> AddressResponse | None:
        if addr is None:
            return None
        municipality = None
        if addr.municipality is not None:
            municipality = MunicipalityInfo(
                id=addr.municipality.id, name=addr.municipality.name
            )
        return AddressResponse(
            id=addr.id,
            street=addr.street,
            exterior_number=addr.exterior_number,
            interior_number=addr.interior_number,
            cross_street_1=addr.cross_street_1,
            cross_street_2=addr.cross_street_2,
            neighborhood=addr.neighborhood,
            municipality=municipality,
            postal_code=addr.postal_code,
        )

    @classmethod
    def _to_response(cls, client: Client) -> ClientResponse:
        return ClientResponse(
            id=client.id,
            first_name=client.first_name,
            paternal_surname=client.paternal_surname,
            maternal_surname=client.maternal_surname,
            rfc=client.rfc,
            birth_date=client.birth_date,
            gender=client.gender.value if client.gender else None,
            marital_status=client.marital_status.value if client.marital_status else None,
            whatsapp=client.phone_1,
            phone_additional=client.phone_2,
            email=client.email,
            address=cls._address_response(client.address),
            created_at=client.created_at,
            updated_at=client.updated_at,
        )

    # ── Address helper ───────────────────────────────────────────────

    async def _upsert_address(
        self, addr_input: AddressInput, existing_address: Address | None = None
    ) -> Address:
        if addr_input.municipality_id is not None:
            if not await self.repo.municipality_exists(addr_input.municipality_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Municipio con id {addr_input.municipality_id} no existe",
                )

        geom = None
        if addr_input.latitude is not None and addr_input.longitude is not None:
            geom = from_shape(
                Point(addr_input.longitude, addr_input.latitude), srid=4326
            )

        if existing_address is not None:
            existing_address.street = addr_input.street
            existing_address.exterior_number = addr_input.exterior_number
            existing_address.interior_number = addr_input.interior_number
            existing_address.cross_street_1 = addr_input.cross_street_1
            existing_address.cross_street_2 = addr_input.cross_street_2
            existing_address.neighborhood = addr_input.neighborhood
            existing_address.municipality_id = addr_input.municipality_id
            existing_address.postal_code = addr_input.postal_code
            existing_address.geom = geom
            return existing_address

        address = Address(
            street=addr_input.street,
            exterior_number=addr_input.exterior_number,
            interior_number=addr_input.interior_number,
            cross_street_1=addr_input.cross_street_1,
            cross_street_2=addr_input.cross_street_2,
            neighborhood=addr_input.neighborhood,
            municipality_id=addr_input.municipality_id,
            postal_code=addr_input.postal_code,
            geom=geom,
        )
        return await self.repo.create_address(address)

    # ── CRUD ─────────────────────────────────────────────────────────

    async def list_clients(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        search: str | None = None,
        phone: str | None = None,
        municipality_id: int | None = None,
    ) -> ClientListResponse:
        clients, total = await self.repo.list_clients(
            skip=skip,
            limit=limit,
            search=search,
            phone=phone,
            municipality_id=municipality_id,
        )
        return ClientListResponse(
            items=[self._to_response(c) for c in clients],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_client(self, client_id: int) -> ClientResponse:
        client = await self.repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return self._to_response(client)

    async def create_client(self, data: ClientCreate) -> ClientResponse:
        address_id = None
        if data.address is not None:
            address = await self._upsert_address(data.address)
            address_id = address.id

        client = Client(
            first_name=data.first_name,
            paternal_surname=data.paternal_surname,
            maternal_surname=data.maternal_surname,
            rfc=data.rfc,
            birth_date=data.birth_date,
            gender=data.gender,
            marital_status=data.marital_status,
            phone_1=data.whatsapp,
            phone_2=data.phone_additional,
            email=data.email,
            address_id=address_id,
        )
        client = await self.repo.create(client)
        return self._to_response(client)

    async def update_client(
        self, client_id: int, data: ClientUpdate
    ) -> ClientResponse:
        client = await self.repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        update_data = data.model_dump(exclude_unset=True, exclude={"address"})

        # Map API field names to model field names
        field_map = {"whatsapp": "phone_1", "phone_additional": "phone_2"}
        for api_name, model_name in field_map.items():
            if api_name in update_data:
                update_data[model_name] = update_data.pop(api_name)

        for field, value in update_data.items():
            setattr(client, field, value)

        # Handle address update
        if data.address is not None:
            if client.address_id is not None:
                existing_addr = await self.repo.get_address(client.address_id)
                await self._upsert_address(data.address, existing_addr)
            else:
                address = await self._upsert_address(data.address)
                client.address_id = address.id

        client = await self.repo.update(client)
        return self._to_response(client)

    async def soft_delete_client(self, client_id: int) -> None:
        client = await self.repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        client.deleted_at = datetime.now(timezone.utc)
        await self.repo.update(client)

    # ── pg_trgm similarity search ─────────────────────────────────────

    async def search_similar(
        self, query: str, limit: int = 20
    ) -> list[ClientResponse]:
        clients = await self.repo.search_by_similarity(query, limit=limit)
        return [self._to_response(c) for c in clients]

    # ── PostGIS nearby search ─────────────────────────────────────────

    async def find_nearby(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 5000,
        limit: int = 50,
    ) -> list[NearbyClientResult]:
        results = await self.repo.find_nearby(
            latitude, longitude, radius_meters, limit
        )
        return [
            NearbyClientResult(
                client=self._to_response(client),
                distance_meters=round(distance, 1),
            )
            for client, distance in results
        ]

    # ── WhatsApp verification ─────────────────────────────────────────

    async def verify_whatsapp(self, client_id: int) -> WhatsAppVerifyResponse:
        """Verify if client's phone is a valid WhatsApp number via Evolution API."""
        import httpx

        from app.core.config import get_settings

        client = await self.repo.get_by_id(client_id)
        if client is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )

        phone = client.phone_1
        if not phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cliente no tiene numero de WhatsApp registrado",
            )

        settings = get_settings()
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Evolution API no configurada",
            )

        # Add Mexico country code if not present
        check_phone = phone if phone.startswith("52") else f"52{phone}"

        try:
            async with httpx.AsyncClient(timeout=10) as http:
                resp = await http.post(
                    f"{settings.EVOLUTION_API_URL}/chat/whatsappNumbers/protegrt",
                    json={"numbers": [check_phone]},
                    headers={"apikey": settings.EVOLUTION_API_KEY},
                )
                resp.raise_for_status()
                data = resp.json()

            # Evolution API returns list of objects with "exists" and "jid"
            is_whatsapp = False
            if isinstance(data, list) and data:
                is_whatsapp = data[0].get("exists", False)

            return WhatsAppVerifyResponse(
                phone=phone,
                is_whatsapp=is_whatsapp,
                verified=True,
            )
        except httpx.HTTPError:
            return WhatsAppVerifyResponse(
                phone=phone,
                is_whatsapp=False,
                verified=False,
            )
