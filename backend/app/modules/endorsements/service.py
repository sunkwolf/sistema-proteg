"""Business logic for the Endorsements module."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.endorsements import Endorsement
from app.modules.endorsements.repository import EndorsementRepository
from app.modules.endorsements.schemas import EndorsementCreate, EndorsementUpdate


class EndorsementService:
    def __init__(self, session: AsyncSession):
        self.repo = EndorsementRepository(session)

    async def list_endorsements(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        endorsement_type: str | None = None,
        endorsement_status: str | None = None,
    ) -> dict:
        items, total = await self.repo.list_endorsements(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            endorsement_type=endorsement_type,
            status=endorsement_status,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def get_endorsement(self, endorsement_id: int) -> Endorsement:
        endorsement = await self.repo.get_by_id(endorsement_id)
        if endorsement is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Endoso no encontrado",
            )
        return endorsement

    async def create_endorsement(self, data: EndorsementCreate) -> Endorsement:
        # Validate policy exists
        policy = await self.repo.get_policy(data.policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )

        p_status = policy.status
        if hasattr(p_status, "value"):
            p_status = p_status.value
        if p_status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede crear endoso para una poliza cancelada",
            )

        endorsement = Endorsement(
            policy_id=data.policy_id,
            endorsement_type=data.endorsement_type,
            change_details=data.change_details,
            comments=data.comments,
            new_contractor_id=data.new_contractor_id,
            previous_vehicle_id=data.previous_vehicle_id,
        )
        return await self.repo.create(endorsement)

    async def update_endorsement(
        self, endorsement_id: int, data: EndorsementUpdate
    ) -> Endorsement:
        endorsement = await self.get_endorsement(endorsement_id)

        e_status = endorsement.status
        if hasattr(e_status, "value"):
            e_status = e_status.value
        if e_status in ("applied", "rejected"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede modificar un endoso aplicado o rechazado",
            )

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(endorsement, field, value)

        return await self.repo.update(endorsement)

    async def approve_endorsement(self, endorsement_id: int) -> Endorsement:
        endorsement = await self.get_endorsement(endorsement_id)

        e_status = endorsement.status
        if hasattr(e_status, "value"):
            e_status = e_status.value
        if e_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden aprobar endosos pendientes",
            )

        endorsement.status = "approved"
        return await self.repo.update(endorsement)

    async def reject_endorsement(
        self, endorsement_id: int, comments: str | None = None
    ) -> Endorsement:
        endorsement = await self.get_endorsement(endorsement_id)

        e_status = endorsement.status
        if hasattr(e_status, "value"):
            e_status = e_status.value
        if e_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden rechazar endosos pendientes",
            )

        endorsement.status = "rejected"
        if comments:
            endorsement.comments = comments
        return await self.repo.update(endorsement)

    async def apply_endorsement(self, endorsement_id: int) -> Endorsement:
        endorsement = await self.get_endorsement(endorsement_id)

        e_status = endorsement.status
        if hasattr(e_status, "value"):
            e_status = e_status.value
        if e_status != "approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden aplicar endosos aprobados",
            )

        endorsement.status = "applied"
        endorsement.application_date = datetime.now(timezone.utc)
        return await self.repo.update(endorsement)

    async def calculate_cost(self, endorsement_id: int) -> dict:
        endorsement = await self.get_endorsement(endorsement_id)

        e_type = endorsement.endorsement_type
        if hasattr(e_type, "value"):
            e_type = e_type.value

        # Cost calculation depends on endorsement type and policy details
        # This is a placeholder — full implementation requires coverage tariff tables
        return {
            "endorsement_id": endorsement.id,
            "endorsement_type": e_type,
            "calculated_cost": "0.00",
            "calculation_details": {
                "note": "Calculo de costo pendiente de implementar con tablas de tarifas",
            },
        }
