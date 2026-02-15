"""Client endpoints — CRUD with soft-delete, address/PostGIS support."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.clients.schemas import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
    NearbyClientResult,
    WhatsAppVerifyResponse,
)
from app.modules.clients.service import ClientService

router = APIRouter()


@router.get("", response_model=ClientListResponse)
async def list_clients(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str | None = Query(None, max_length=200),
    phone: str | None = Query(None, max_length=20),
    municipality_id: int | None = None,
):
    """List clients with filters and pagination. Soft-deleted excluded."""
    service = ClientService(db)
    return await service.list_clients(
        skip=skip,
        limit=limit,
        search=search,
        phone=phone,
        municipality_id=municipality_id,
    )


# ── pg_trgm similarity search ──────────────────────────────────────


@router.get("/search/similar", response_model=list[ClientResponse])
async def search_similar(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.read")],
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(20, ge=1, le=100),
):
    """Fuzzy search clients by name using pg_trgm similarity."""
    service = ClientService(db)
    return await service.search_similar(q, limit=limit)


# ── PostGIS nearby search ──────────────────────────────────────────


@router.get("/search/nearby", response_model=list[NearbyClientResult])
async def find_nearby(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.read")],
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(5000, ge=100, le=50000),
    limit: int = Query(50, ge=1, le=200),
):
    """Find clients within radius of a geographic point (PostGIS)."""
    service = ClientService(db)
    return await service.find_nearby(
        latitude, longitude, radius_meters=radius_meters, limit=limit
    )


# ── CRUD by ID (must come AFTER /search/* routes) ──────────────────


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.read")],
):
    """Get client by ID."""
    service = ClientService(db)
    return await service.get_client(client_id)


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    data: ClientCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.create")],
):
    """Create a new client with optional address (PostGIS)."""
    service = ClientService(db)
    return await service.create_client(data)


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.update")],
):
    """Update client fields and/or address."""
    service = ClientService(db)
    return await service.update_client(client_id, data)


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.delete")],
):
    """Soft-delete a client (sets deleted_at timestamp)."""
    service = ClientService(db)
    await service.soft_delete_client(client_id)


# ── WhatsApp verification ──────────────────────────────────────────


@router.get("/{client_id}/verify-whatsapp", response_model=WhatsAppVerifyResponse)
async def verify_whatsapp(
    client_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("clients.read")],
):
    """Check if client's WhatsApp number is valid via Evolution API."""
    service = ClientService(db)
    return await service.verify_whatsapp(client_id)
