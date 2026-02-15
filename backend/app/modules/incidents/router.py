"""Incident endpoints — CRUD, passes, survey, adjuster shifts."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_permission
from app.modules.incidents.schemas import (
    AdjusterShiftCreate,
    AdjusterShiftListResponse,
    AdjusterShiftResponse,
    IncidentCreate,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdate,
    MedicalPassCreate,
    MedicalPassResponse,
    SurveyCreate,
    SurveyResponse,
    WorkshopPassCreate,
    WorkshopPassResponse,
)
from app.modules.incidents.service import IncidentService

router = APIRouter()


# ── Incident CRUD ──────────────────────────────────────────────────

@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    policy_id: int | None = None,
    adjuster_id: int | None = None,
    service_status: str | None = Query(None),
):
    """List incidents with optional filters."""
    service = IncidentService(db)
    return await service.list_incidents(
        skip=skip,
        limit=limit,
        policy_id=policy_id,
        adjuster_id=adjuster_id,
        service_status=service_status,
    )


@router.get("/assigned", response_model=IncidentListResponse)
async def list_assigned_incidents(
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("incidents.read_assigned")],
    adjuster_id: int = Query(..., description="Adjuster ID (from adjuster table)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service_status: str | None = Query(None),
):
    """List incidents assigned to a specific adjuster."""
    service = IncidentService(db)
    return await service.list_incidents(
        skip=skip,
        limit=limit,
        adjuster_id=adjuster_id,
        service_status=service_status,
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
):
    """Get incident by ID."""
    service = IncidentService(db)
    return await service.get_incident(incident_id)


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    data: IncidentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("incidents.create")],
):
    """Create a new incident report. Generates report number automatically."""
    service = IncidentService(db)
    return await service.create_incident(data, user_id=user.id)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("incidents.create")],
):
    """Update incident fields (status, times, adjuster, etc.)."""
    service = IncidentService(db)
    return await service.update_incident(incident_id, data)


# ── Medical Passes ─────────────────────────────────────────────────

@router.get(
    "/{incident_id}/medical-passes",
    response_model=list[MedicalPassResponse],
)
async def list_medical_passes(
    incident_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
):
    """List medical passes for an incident."""
    service = IncidentService(db)
    return await service.list_medical_passes(incident_id)


@router.post(
    "/{incident_id}/medical-passes",
    response_model=MedicalPassResponse,
    status_code=201,
)
async def create_medical_pass(
    incident_id: int,
    data: MedicalPassCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("incidents.create")],
):
    """Create a medical pass for an incident."""
    service = IncidentService(db)
    return await service.create_medical_pass(incident_id, data)


# ── Workshop Passes ────────────────────────────────────────────────

@router.get(
    "/{incident_id}/workshop-passes",
    response_model=list[WorkshopPassResponse],
)
async def list_workshop_passes(
    incident_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
):
    """List workshop passes for an incident."""
    service = IncidentService(db)
    return await service.list_workshop_passes(incident_id)


@router.post(
    "/{incident_id}/workshop-passes",
    response_model=WorkshopPassResponse,
    status_code=201,
)
async def create_workshop_pass(
    incident_id: int,
    data: WorkshopPassCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("incidents.create")],
):
    """Create a workshop pass for an incident."""
    service = IncidentService(db)
    return await service.create_workshop_pass(incident_id, data)


# ── Satisfaction Survey ────────────────────────────────────────────

@router.post(
    "/{incident_id}/survey",
    response_model=SurveyResponse,
    status_code=201,
)
async def create_survey(
    incident_id: int,
    data: SurveyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: CurrentUser,
    _perm: Annotated[None, require_permission("incidents.create")],
):
    """Register a satisfaction survey for a completed incident."""
    service = IncidentService(db)
    return await service.create_survey(incident_id, data, user_id=user.id)


# ── Adjuster Shifts ────────────────────────────────────────────────

@router.get("/shifts", response_model=AdjusterShiftListResponse)
async def list_shifts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    adjuster_id: int | None = None,
):
    """List adjuster shift calendar."""
    service = IncidentService(db)
    return await service.list_shifts(
        start_date=start_date, end_date=end_date, adjuster_id=adjuster_id
    )


@router.get("/shifts/on-duty", response_model=list[AdjusterShiftResponse])
async def get_on_duty(
    db: Annotated[AsyncSession, Depends(get_db)],
    _user: Annotated[None, require_permission("incidents.read")],
    duty_date: date = Query(default=None),
):
    """Get adjusters on duty for a given date (defaults to today)."""
    service = IncidentService(db)
    return await service.get_on_duty(duty_date or date.today())


@router.post("/shifts", response_model=AdjusterShiftResponse, status_code=201)
async def create_shift(
    data: AdjusterShiftCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _perm: Annotated[None, require_permission("incidents.admin")],
):
    """Assign a shift to an adjuster (admin only)."""
    service = IncidentService(db)
    return await service.create_shift(data)
