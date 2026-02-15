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
