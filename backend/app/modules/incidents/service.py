"""Business logic for the Incidents module."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incidents import (
    AdjusterShift,
    Incident,
    IncidentSatisfactionSurvey,
    MedicalPass,
    WorkshopPass,
)
from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.schemas import (
    AdjusterShiftCreate,
    IncidentCreate,
    IncidentUpdate,
    MedicalPassCreate,
    SurveyCreate,
    WorkshopPassCreate,
)


class IncidentService:
    def __init__(self, session: AsyncSession):
        self.repo = IncidentRepository(session)

    # ── Incident CRUD ──────────────────────────────────────────────

    async def list_incidents(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        adjuster_id: int | None = None,
        service_status: str | None = None,
    ) -> dict:
        items, total = await self.repo.list_incidents(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            adjuster_id=adjuster_id,
            service_status=service_status,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def get_incident(self, incident_id: int) -> Incident:
        incident = await self.repo.get_by_id(incident_id)
        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Siniestro no encontrado",
            )
        return incident

    async def create_incident(
        self, data: IncidentCreate, user_id: int
    ) -> Incident:
        # Validate policy exists
        policy = await self.repo.get_policy(data.policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )

        # Validate policy is not cancelled
        p_status = policy.status
        if hasattr(p_status, "value"):
            p_status = p_status.value
        if p_status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede reportar siniestro para una poliza cancelada",
            )

        # Validate adjuster exists
        adjuster = await self.repo.get_adjuster(data.adjuster_id)
        if adjuster is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ajustador no encontrado",
            )

        report_number = await self.repo.generate_report_number()

        incident = Incident(
            policy_id=data.policy_id,
            report_number=report_number,
            requester_name=data.requester_name,
            phone=data.phone,
            incident_type=data.incident_type,
            description=data.description,
            responsibility=data.responsibility,
            client_misconduct=data.client_misconduct,
            adjuster_id=data.adjuster_id,
            attended_by_user_id=user_id,
            comments=data.comments,
        )
        return await self.repo.create(incident)

    async def update_incident(
        self, incident_id: int, data: IncidentUpdate
    ) -> Incident:
        incident = await self.get_incident(incident_id)

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(incident, field, value)

        return await self.repo.update(incident)

    # ── Medical Passes ─────────────────────────────────────────────

    async def list_medical_passes(self, incident_id: int) -> list[MedicalPass]:
        await self.get_incident(incident_id)
        return await self.repo.list_medical_passes(incident_id)

    async def create_medical_pass(
        self, incident_id: int, data: MedicalPassCreate
    ) -> MedicalPass:
        await self.get_incident(incident_id)

        hospital = await self.repo.get_hospital(data.hospital_id)
        if hospital is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital no encontrado",
            )

        mp = MedicalPass(
            incident_id=incident_id,
            hospital_id=data.hospital_id,
            pass_number=data.pass_number,
            beneficiary_name=data.beneficiary_name,
            injuries=data.injuries,
            observations=data.observations,
            cost=data.cost,
        )
        return await self.repo.create_medical_pass(mp)

    # ── Workshop Passes ────────────────────────────────────────────

    async def list_workshop_passes(self, incident_id: int) -> list[WorkshopPass]:
        await self.get_incident(incident_id)
        return await self.repo.list_workshop_passes(incident_id)

    async def create_workshop_pass(
        self, incident_id: int, data: WorkshopPassCreate
    ) -> WorkshopPass:
        await self.get_incident(incident_id)

        workshop = await self.repo.get_workshop(data.workshop_id)
        if workshop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Taller no encontrado",
            )

        wp = WorkshopPass(
            incident_id=incident_id,
            workshop_id=data.workshop_id,
            pass_number=data.pass_number,
            beneficiary_name=data.beneficiary_name,
            pass_type=data.pass_type,
            vehicle_damages=data.vehicle_damages,
            observations=data.observations,
            cost=data.cost,
        )
        return await self.repo.create_workshop_pass(wp)

    # ── Satisfaction Survey ────────────────────────────────────────

    async def create_survey(
        self, incident_id: int, data: SurveyCreate, user_id: int
    ) -> IncidentSatisfactionSurvey:
        await self.get_incident(incident_id)

        existing = await self.repo.get_survey(incident_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una encuesta para este siniestro",
            )

        average = Decimal(
            data.response_time_rating
            + data.service_rating
            + data.overall_service_rating
            + data.company_impression
        ) / Decimal(4)

        survey = IncidentSatisfactionSurvey(
            incident_id=incident_id,
            response_time_rating=data.response_time_rating,
            service_rating=data.service_rating,
            overall_service_rating=data.overall_service_rating,
            company_impression=data.company_impression,
            comments=data.comments,
            average_rating=round(average, 2),
            surveyed_by_user_id=user_id,
        )
        return await self.repo.create_survey(survey)

    # ── Adjuster Shifts ────────────────────────────────────────────

    async def list_shifts(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        adjuster_id: int | None = None,
    ) -> dict:
        items, total = await self.repo.list_shifts(
            start_date=start_date,
            end_date=end_date,
            adjuster_id=adjuster_id,
        )
        return {"items": items, "total": total}

    async def get_on_duty(self, duty_date: date) -> list[AdjusterShift]:
        return await self.repo.get_on_duty(duty_date)

    async def create_shift(self, data: AdjusterShiftCreate) -> AdjusterShift:
        adjuster = await self.repo.get_adjuster(data.adjuster_id)
        if adjuster is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ajustador no encontrado",
            )

        existing = await self.repo.get_existing_shift(
            data.shift_date, data.adjuster_id
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un turno para este ajustador en esta fecha",
            )

        shift = AdjusterShift(
            shift_date=data.shift_date,
            adjuster_id=data.adjuster_id,
            shift_order=data.shift_order,
        )
        return await self.repo.create_shift(shift)
