"""Business logic for the Cancellations module."""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Cancellation
from app.modules.cancellations.repository import CancellationRepository
from app.modules.cancellations.schemas import CancellationCreate


class CancellationService:
    def __init__(self, session: AsyncSession):
        self.repo = CancellationRepository(session)

    async def list_cancellations(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        code: str | None = None,
        policy_id: int | None = None,
    ) -> dict:
        items, total = await self.repo.list_cancellations(
            skip=skip, limit=limit, code=code, policy_id=policy_id
        )
        return {"items": items, "total": total, "skip": skip, "limit": limit}

    async def get_cancellation(self, cancellation_id: int) -> Cancellation:
        cancellation = await self.repo.get_by_id(cancellation_id)
        if cancellation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cancelacion no encontrada",
            )
        return cancellation

    async def create_cancellation(
        self, data: CancellationCreate, user_id: int
    ) -> Cancellation:
        # Validate policy exists
        policy = await self.repo.get_policy(data.policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Poliza no encontrada",
            )

        # Check not already cancelled
        p_status = policy.status
        if hasattr(p_status, "value"):
            p_status = p_status.value
        if p_status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La poliza ya esta cancelada",
            )

        # Create cancellation record
        cancellation = Cancellation(
            policy_id=data.policy_id,
            cancellation_date=date.today(),
            reason=data.reason,
            code=data.code,
            payments_made=data.payments_made,
            cancelled_by_user_id=user_id,
        )
        cancellation = await self.repo.create(cancellation)

        # Update policy status to cancelled
        await self.repo.update_policy_status(data.policy_id, "cancelled")

        # Cancel pending payments after payments_made
        await self.repo.cancel_payments_after(data.policy_id, data.payments_made)

        # Archive card if requested
        if data.update_card:
            await self.repo.archive_card(data.policy_id)

        return cancellation

    async def undo_cancellation(self, cancellation_id: int) -> Cancellation:
        cancellation = await self.get_cancellation(cancellation_id)

        # Restore payments
        await self.repo.restore_payments_after(
            cancellation.policy_id, cancellation.payments_made or 0
        )

        # Restore card to OFICINA
        await self.repo.restore_card(cancellation.policy_id)

        # Set policy to pending (StatusUpdater will recalculate)
        await self.repo.update_policy_status(cancellation.policy_id, "pending")

        # Delete cancellation record
        await self.repo.delete(cancellation)

        # Return a copy with the id before deletion
        return cancellation

    async def mark_notification_sent(
        self, cancellation_id: int, recipient: str
    ) -> Cancellation:
        cancellation = await self.get_cancellation(cancellation_id)

        field_map = {
            "seller": "notification_sent_seller",
            "collector": "notification_sent_collector",
            "client": "notification_sent_client",
        }

        if recipient not in field_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Destinatario invalido: {recipient}. Usar: seller, collector, client",
            )

        setattr(cancellation, field_map[recipient], True)
        return await self.repo.update(cancellation)
