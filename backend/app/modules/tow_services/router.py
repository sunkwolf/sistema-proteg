"""Tow service endpoints — CRUD, providers, survey."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.tow_services.schemas import (
    TowProviderCreate,
    TowProviderListResponse,
    TowProviderResponse,
    TowProviderUpdate,
    TowServiceCreate,
    TowServiceListResponse,
    TowServiceResponse,
    TowServiceUpdate,
    TowSurveyCreate,
    TowSurveyResponse,
)
from app.modules.tow_services.service import TowServiceManager

router = APIRouter()


# ── Tow Service CRUD ──────────────────────────────────────────────

@router.get("", response_model=TowServiceListResponse)
async def list_tow_services(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("tow_services.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    policy_id: int | None = None,
    service_status: str | None = Query(None),
    tow_provider_id: int | None = None,
):
    """List tow services with optional filters."""
    svc = TowServiceManager(db)
    return await svc.list_tow_services(
        skip=skip,
        limit=limit,
        policy_id=policy_id,
        service_status=service_status,
        tow_provider_id=tow_provider_id,
    )


@router.get("/{tow_service_id}", response_model=TowServiceResponse)
async def get_tow_service(
    tow_service_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("tow_services.read")],
):
    """Get tow service by ID."""
    svc = TowServiceManager(db)
    return await svc.get_tow_service(tow_service_id)


@router.post("", response_model=TowServiceResponse, status_code=201)
async def create_tow_service(
    data: TowServiceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("tow_services.create")],
):
    """Request a new tow service. Generates report number automatically."""
    svc = TowServiceManager(db)
    return await svc.create_tow_service(data, user_id=user.id)


@router.put("/{tow_service_id}", response_model=TowServiceResponse)
async def update_tow_service(
    tow_service_id: int,
    data: TowServiceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("tow_services.create")],
):
    """Update tow service fields (status, times, costs, etc.)."""
    svc = TowServiceManager(db)
    return await svc.update_tow_service(tow_service_id, data)


# ── Satisfaction Survey ────────────────────────────────────────────

@router.post(
    "/{tow_service_id}/survey",
    response_model=TowSurveyResponse,
    status_code=201,
)
async def create_tow_survey(
    tow_service_id: int,
    data: TowSurveyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("tow_services.create")],
):
    """Register a satisfaction survey for a completed tow service."""
    svc = TowServiceManager(db)
    return await svc.create_survey(tow_service_id, data, user_id=user.id)


# ── Tow Providers ─────────────────────────────────────────────────

@router.get("/providers", response_model=TowProviderListResponse)
async def list_providers(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("tow_services.read")],
    active_only: bool = Query(True),
):
    """List tow providers."""
    svc = TowServiceManager(db)
    return await svc.list_providers(active_only=active_only)


@router.get("/providers/{provider_id}", response_model=TowProviderResponse)
async def get_provider(
    provider_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("tow_services.read")],
):
    """Get tow provider by ID."""
    svc = TowServiceManager(db)
    return await svc.get_provider(provider_id)


@router.post(
    "/providers",
    response_model=TowProviderResponse,
    status_code=201,
)
async def create_provider(
    data: TowProviderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("tow_services.admin")],
):
    """Create a new tow provider (admin only)."""
    svc = TowServiceManager(db)
    return await svc.create_provider(data)


@router.put("/providers/{provider_id}", response_model=TowProviderResponse)
async def update_provider(
    provider_id: int,
    data: TowProviderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("tow_services.admin")],
):
    """Update a tow provider (admin only)."""
    svc = TowServiceManager(db)
    return await svc.update_provider(provider_id, data)
