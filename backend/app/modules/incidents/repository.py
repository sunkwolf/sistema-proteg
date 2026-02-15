"""Data access layer for incidents, passes, shifts, and surveys."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Policy
from app.models.incidents import (
    Adjuster,
    AdjusterShift,
    Hospital,
    Incident,
    IncidentSatisfactionSurvey,
    MedicalPass,
    Workshop,
    WorkshopPass,
)


class IncidentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Incident CRUD ──────────────────────────────────────────────

    async def get_by_id(self, incident_id: int) -> Incident | None:
        result = await self.session.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()

    async def list_incidents(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        adjuster_id: int | None = None,
        service_status: str | None = None,
    ) -> tuple[list[Incident], int]:
        query = select(Incident)
        count_query = select(func.count(Incident.id))

        if policy_id is not None:
            query = query.where(Incident.policy_id == policy_id)
            count_query = count_query.where(Incident.policy_id == policy_id)
        if adjuster_id is not None:
            query = query.where(Incident.adjuster_id == adjuster_id)
            count_query = count_query.where(Incident.adjuster_id == adjuster_id)
        if service_status is not None:
            query = query.where(Incident.service_status == service_status)
            count_query = count_query.where(Incident.service_status == service_status)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Incident.report_time.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, incident: Incident) -> Incident:
        self.session.add(incident)
        await self.session.flush()
        await self.session.refresh(incident)
        return incident

    async def update(self, incident: Incident) -> Incident:
        await self.session.flush()
        await self.session.refresh(incident)
        return incident

    # ── Policy ─────────────────────────────────────────────────────

    async def get_policy(self, policy_id: int) -> Policy | None:
        result = await self.session.execute(
            select(Policy).where(Policy.id == policy_id)
        )
        return result.scalar_one_or_none()

    # ── Adjuster ───────────────────────────────────────────────────

    async def get_adjuster(self, adjuster_id: int) -> Adjuster | None:
        result = await self.session.execute(
            select(Adjuster).where(Adjuster.id == adjuster_id)
        )
        return result.scalar_one_or_none()

    # ── Medical Passes ─────────────────────────────────────────────

    async def list_medical_passes(
        self, incident_id: int
    ) -> list[MedicalPass]:
        result = await self.session.execute(
            select(MedicalPass)
            .where(MedicalPass.incident_id == incident_id)
            .order_by(MedicalPass.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_medical_pass(self, mp: MedicalPass) -> MedicalPass:
        self.session.add(mp)
        await self.session.flush()
        await self.session.refresh(mp)
        return mp

    async def get_hospital(self, hospital_id: int) -> Hospital | None:
        result = await self.session.execute(
            select(Hospital).where(Hospital.id == hospital_id)
        )
        return result.scalar_one_or_none()

    # ── Workshop Passes ────────────────────────────────────────────

    async def list_workshop_passes(
        self, incident_id: int
    ) -> list[WorkshopPass]:
        result = await self.session.execute(
            select(WorkshopPass)
            .where(WorkshopPass.incident_id == incident_id)
            .order_by(WorkshopPass.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_workshop_pass(self, wp: WorkshopPass) -> WorkshopPass:
        self.session.add(wp)
        await self.session.flush()
        await self.session.refresh(wp)
        return wp

    async def get_workshop(self, workshop_id: int) -> Workshop | None:
        result = await self.session.execute(
            select(Workshop).where(Workshop.id == workshop_id)
        )
        return result.scalar_one_or_none()

    # ── Satisfaction Survey ────────────────────────────────────────

    async def get_survey(self, incident_id: int) -> IncidentSatisfactionSurvey | None:
        result = await self.session.execute(
            select(IncidentSatisfactionSurvey).where(
                IncidentSatisfactionSurvey.incident_id == incident_id
            )
        )
        return result.scalar_one_or_none()

    async def create_survey(
        self, survey: IncidentSatisfactionSurvey
    ) -> IncidentSatisfactionSurvey:
        self.session.add(survey)
        await self.session.flush()
        await self.session.refresh(survey)
        return survey

    # ── Adjuster Shifts ────────────────────────────────────────────

    async def list_shifts(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        adjuster_id: int | None = None,
    ) -> tuple[list[AdjusterShift], int]:
        query = select(AdjusterShift)
        count_query = select(func.count(AdjusterShift.id))

        if start_date is not None:
            query = query.where(AdjusterShift.shift_date >= start_date)
            count_query = count_query.where(AdjusterShift.shift_date >= start_date)
        if end_date is not None:
            query = query.where(AdjusterShift.shift_date <= end_date)
            count_query = count_query.where(AdjusterShift.shift_date <= end_date)
        if adjuster_id is not None:
            query = query.where(AdjusterShift.adjuster_id == adjuster_id)
            count_query = count_query.where(AdjusterShift.adjuster_id == adjuster_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(AdjusterShift.shift_date.asc()).offset(0)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_on_duty(self, duty_date: date) -> list[AdjusterShift]:
        result = await self.session.execute(
            select(AdjusterShift)
            .where(
                AdjusterShift.shift_date == duty_date,
                AdjusterShift.shift_order != "rest",
            )
            .order_by(AdjusterShift.shift_order.asc())
        )
        return list(result.scalars().all())

    async def create_shift(self, shift: AdjusterShift) -> AdjusterShift:
        self.session.add(shift)
        await self.session.flush()
        await self.session.refresh(shift)
        return shift

    async def get_existing_shift(
        self, shift_date: date, adjuster_id: int
    ) -> AdjusterShift | None:
        result = await self.session.execute(
            select(AdjusterShift).where(
                AdjusterShift.shift_date == shift_date,
                AdjusterShift.adjuster_id == adjuster_id,
            )
        )
        return result.scalar_one_or_none()

    async def generate_report_number(self) -> str:
        """Generate next incident report number (INC-YYYYMMDD-NNNN)."""
        today = date.today()
        prefix = f"INC-{today.strftime('%Y%m%d')}-"

        result = await self.session.execute(
            select(func.count(Incident.id)).where(
                Incident.report_number.like(f"{prefix}%")
            )
        )
        count = result.scalar_one()
        return f"{prefix}{(count + 1):04d}"
