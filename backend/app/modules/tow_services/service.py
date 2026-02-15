"""Business logic for the Tow Services module."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incidents import TowProvider, TowSatisfactionSurvey, TowService
from app.modules.tow_services.repository import TowServiceRepository
from app.modules.tow_services.schemas import (
    TowProviderCreate,
    TowProviderUpdate,
    TowServiceCreate,
    TowServiceUpdate,
    TowSurveyCreate,
)


class TowServiceManager:
    def __init__(self, session: AsyncSession):
        self.repo = TowServiceRepository(session)

    # ── Tow Service CRUD ───────────────────────────────────────────

    async def list_tow_services(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        policy_id: int | None = None,
        service_status: str | None = None,
        tow_provider_id: int | None = None,
    ) -> dict:
        items, total = await self.repo.list_tow_services(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            service_status=service_status,
            tow_provider_id=tow_provider_id,
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def get_tow_service(self, tow_service_id: int) -> TowService:
        ts = await self.repo.get_by_id(tow_service_id)
        if ts is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio de grua no encontrado",
            )
        return ts

    async def create_tow_service(
        self, data: TowServiceCreate, user_id: int
    ) -> TowService:
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
                detail="No se puede solicitar grua para una poliza cancelada",
            )

        # Validate provider if specified
        if data.tow_provider_id is not None:
            provider = await self.repo.get_provider_by_id(data.tow_provider_id)
            if provider is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Proveedor de grua no encontrado",
                )

        report_number = await self.repo.generate_report_number()

        ts = TowService(
            policy_id=data.policy_id,
            report_number=report_number,
            requester_name=data.requester_name,
            phone=data.phone,
            vehicle_failure=data.vehicle_failure,
            load_weight=data.load_weight,
            tow_provider_id=data.tow_provider_id,
            tow_cost=data.tow_cost,
            extra_charge=data.extra_charge,
            attended_by_user_id=user_id,
            comments=data.comments,
        )
        return await self.repo.create(ts)

    async def update_tow_service(
        self, tow_service_id: int, data: TowServiceUpdate
    ) -> TowService:
        ts = await self.get_tow_service(tow_service_id)

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(ts, field, value)

        return await self.repo.update(ts)

    # ── Satisfaction Survey ────────────────────────────────────────

    async def create_survey(
        self, tow_service_id: int, data: TowSurveyCreate, user_id: int
    ) -> TowSatisfactionSurvey:
        await self.get_tow_service(tow_service_id)

        existing = await self.repo.get_survey(tow_service_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una encuesta para este servicio de grua",
            )

        average = Decimal(
            data.response_time_rating
            + data.service_rating
            + data.overall_service_rating
            + data.company_impression
        ) / Decimal(4)

        survey = TowSatisfactionSurvey(
            tow_service_id=tow_service_id,
            response_time_rating=data.response_time_rating,
            service_rating=data.service_rating,
            overall_service_rating=data.overall_service_rating,
            company_impression=data.company_impression,
            comments=data.comments,
            average_rating=round(average, 2),
            surveyed_by_user_id=user_id,
        )
        return await self.repo.create_survey(survey)

    # ── Tow Provider CRUD ──────────────────────────────────────────

    async def list_providers(self, *, active_only: bool = True) -> dict:
        items, total = await self.repo.list_providers(active_only=active_only)
        return {"items": items, "total": total}

    async def get_provider(self, provider_id: int) -> TowProvider:
        provider = await self.repo.get_provider_by_id(provider_id)
        if provider is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor de grua no encontrado",
            )
        return provider

    async def create_provider(self, data: TowProviderCreate) -> TowProvider:
        provider = TowProvider(
            name=data.name,
            phone=data.phone,
            telegram_group_id=data.telegram_group_id,
            contact_person=data.contact_person,
            notes=data.notes,
        )
        return await self.repo.create_provider(provider)

    async def update_provider(
        self, provider_id: int, data: TowProviderUpdate
    ) -> TowProvider:
        provider = await self.get_provider(provider_id)

        update_fields = data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(provider, field, value)

        return await self.repo.update_provider(provider)
