"""Business logic for the Renewals module."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.endorsements import Renewal
from app.modules.renewals.repository import RenewalRepository
from app.modules.renewals.schemas import RenewalCreate, RenewalComplete


class RenewalService:
    def __init__(self, session: AsyncSession):
        self.repo = RenewalRepository(session)

    async def list_renewals(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        renewal_status: str | None = None,
        old_policy_id: int | None = None,
    ) -> dict:
        items, total = await self.repo.list_renewals(
            skip=skip, limit=limit, status=renewal_status, old_policy_id=old_policy_id
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def get_renewal(self, renewal_id: int) -> Renewal:
        renewal = await self.repo.get_by_id(renewal_id)
        if renewal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Renovacion no encontrada",
            )
        return renewal

    async def get_pending_policies(
        self,
        *,
        days_before: int = 30,
        days_after: int = 0,
        seller_id: int | None = None,
    ) -> dict:
        """Find policies approaching or past expiration."""
        policies = await self.repo.get_policies_near_expiration(
            days_before=days_before,
            days_after=days_after,
            seller_id=seller_id,
        )
        today = date.today()
        items = []
        for p in policies:
            p_status = p.status
            if hasattr(p_status, "value"):
                p_status = p_status.value
            days = (p.expiration_date - today).days if p.expiration_date else 0
            items.append({
                "id": p.id,
                "folio": p.folio,
                "client_id": p.client_id,
                "seller_id": p.seller_id,
                "expiration_date": p.expiration_date,
                "status": p_status,
                "days_until_expiration": days,
            })
        return {"items": items, "total": len(items)}

    async def create_renewal(self, data: RenewalCreate) -> Renewal:
        # Validate old policy exists
        policy = await self.repo.get_policy(data.old_policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza original no encontrada",
            )

        # Check no pending renewal already exists for this policy
        existing = await self.repo.get_renewal_by_old_policy(data.old_policy_id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una renovacion pendiente para esta poliza",
            )

        # Validate new policy if provided
        if data.new_policy_id is not None:
            new_policy = await self.repo.get_policy(data.new_policy_id)
            if new_policy is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Poliza nueva no encontrada",
                )

        renewal = Renewal(
            old_policy_id=data.old_policy_id,
            new_policy_id=data.new_policy_id,
            renewal_date=data.renewal_date,
            comments=data.comments,
        )
        return await self.repo.create(renewal)

    async def complete_renewal(
        self, renewal_id: int, data: RenewalComplete
    ) -> Renewal:
        renewal = await self.get_renewal(renewal_id)

        r_status = renewal.status
        if hasattr(r_status, "value"):
            r_status = r_status.value
        if r_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden completar renovaciones pendientes",
            )

        # Validate new policy exists
        new_policy = await self.repo.get_policy(data.new_policy_id)
        if new_policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza nueva no encontrada",
            )

        renewal.new_policy_id = data.new_policy_id
        renewal.status = "completed"
        if data.comments:
            renewal.comments = data.comments

        return await self.repo.update(renewal)

    async def reject_renewal(
        self, renewal_id: int, comments: str | None = None
    ) -> Renewal:
        renewal = await self.get_renewal(renewal_id)

        r_status = renewal.status
        if hasattr(r_status, "value"):
            r_status = r_status.value
        if r_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden rechazar renovaciones pendientes",
            )

        renewal.status = "rejected"
        if comments:
            renewal.comments = comments

        return await self.repo.update(renewal)

    async def get_notification_logs(self, policy_id: int) -> list:
        return await self.repo.get_notification_logs(policy_id)
