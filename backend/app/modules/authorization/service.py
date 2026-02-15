"""Business logic for the Authorization module (proposals + approvals)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ApprovalRequest
from app.models.enums import ApprovalRequestType, ApprovalStatusType
from app.models.payments import PaymentProposal
from app.modules.authorization.repository import AuthorizationRepository
from app.modules.authorization.schemas import (
    ApprovalReview,
    ProposalCreate,
    ProposalReview,
)


class AuthorizationService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthorizationRepository(session)

    # ── Payment Proposals ────────────────────────────────────────────

    async def list_proposals(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        collector_id: int | None = None,
        policy_id: int | None = None,
    ) -> dict:
        proposals, total = await self.repo.list_proposals(
            skip=skip,
            limit=limit,
            status=status_filter,
            collector_id=collector_id,
            policy_id=policy_id,
        )
        return {"items": proposals, "total": total, "skip": skip, "limit": limit}

    async def get_proposal(self, proposal_id: int) -> PaymentProposal:
        proposal = await self.repo.get_proposal_by_id(proposal_id)
        if proposal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propuesta de pago no encontrada",
            )
        return proposal

    async def create_proposal(
        self, data: ProposalCreate, user_id: int
    ) -> PaymentProposal:
        # Validate original payment exists
        payment = await self.repo.get_payment(data.original_payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago original no encontrado",
            )

        # Validate policy_id matches the original payment
        if data.policy_id != payment.policy_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El policy_id no corresponde al pago original",
            )

        # Cannot propose for an already paid payment
        pay_status = payment.status
        if hasattr(pay_status, "value"):
            pay_status = pay_status.value
        if pay_status == "paid":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El pago ya esta marcado como pagado",
            )

        # Check no active proposal already exists
        if await self.repo.active_proposal_exists(data.original_payment_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una propuesta activa para este pago",
            )

        # Resolve collector_id from authenticated user
        collector_id = await self.repo.get_employee_id_by_user(user_id)

        proposal = PaymentProposal(
            original_payment_id=data.original_payment_id,
            policy_id=data.policy_id,
            collector_id=collector_id,
            user_id=user_id,
            payment_number=payment.payment_number,
            receipt_number=data.receipt_number,
            actual_date=data.actual_date,
            amount=data.amount,
            payment_method=data.payment_method,
            comments=data.comments,
        )

        return await self.repo.create_proposal(proposal)

    async def approve_proposal(
        self, proposal_id: int, data: ProposalReview, reviewer_id: int
    ) -> PaymentProposal:
        proposal = await self.get_proposal(proposal_id)

        draft = proposal.draft_status
        if hasattr(draft, "value"):
            draft = draft.value
        if draft != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden aprobar propuestas activas",
            )

        # Apply proposal data to the original payment
        payment = await self.repo.get_payment(proposal.original_payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pago original no encontrado",
            )

        payment.actual_date = proposal.actual_date
        payment.amount = proposal.amount
        payment.payment_method = proposal.payment_method
        payment.receipt_number = proposal.receipt_number
        payment.comments = proposal.comments
        payment.collector_id = proposal.collector_id
        payment.status = "paid"

        # Mark proposal as applied
        proposal.draft_status = "applied"
        proposal.comments = (
            f"{proposal.comments or ''}\n[Aprobado por usuario {reviewer_id}] "
            f"{data.review_notes or ''}"
        ).strip()

        await self.repo.update_proposal(proposal)
        return proposal

    async def reject_proposal(
        self, proposal_id: int, data: ProposalReview, reviewer_id: int
    ) -> PaymentProposal:
        proposal = await self.get_proposal(proposal_id)

        draft = proposal.draft_status
        if hasattr(draft, "value"):
            draft = draft.value
        if draft != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden rechazar propuestas activas",
            )

        proposal.draft_status = "discarded"
        proposal.comments = (
            f"{proposal.comments or ''}\n[Rechazado por usuario {reviewer_id}] "
            f"{data.review_notes or ''}"
        ).strip()

        return await self.repo.update_proposal(proposal)

    async def cancel_proposal(
        self, proposal_id: int, user_id: int | None = None
    ) -> PaymentProposal:
        proposal = await self.get_proposal(proposal_id)

        draft = proposal.draft_status
        if hasattr(draft, "value"):
            draft = draft.value
        if draft != "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden cancelar propuestas activas",
            )

        # Only the user who created the proposal can cancel it
        # (admins have proposals.approve which bypasses this endpoint)
        if user_id is not None and proposal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo el usuario que creo la propuesta puede cancelarla",
            )

        proposal.draft_status = "discarded"
        return await self.repo.update_proposal(proposal)

    # ── Generic Approval Requests ─────────────────────────────────────

    async def list_pending_approvals(
        self,
        *,
        request_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        requests, total = await self.repo.list_pending_approvals(
            request_type=request_type, skip=skip, limit=limit
        )
        return {"items": requests, "total": total, "skip": skip, "limit": limit}

    async def approve_request(
        self, request_id: int, data: ApprovalReview, reviewer_id: int
    ):
        approval = await self.repo.get_approval_by_id(request_id)
        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de aprobacion no encontrada",
            )

        req_status = approval.status
        if hasattr(req_status, "value"):
            req_status = req_status.value
        if req_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden aprobar solicitudes pendientes",
            )

        approval.status = "approved"
        approval.reviewed_by_user_id = reviewer_id
        approval.review_notes = data.review_notes
        approval.reviewed_at = datetime.now(timezone.utc)

        # Side effect: if policy_submission, activate the policy
        req_type = approval.request_type
        if hasattr(req_type, "value"):
            req_type = req_type.value
        if req_type == "policy_submission" and approval.entity_id:
            await self._activate_policy(approval.entity_id)

        return await self.repo.update_approval(approval)

    async def reject_request(
        self, request_id: int, data: ApprovalReview, reviewer_id: int
    ):
        approval = await self.repo.get_approval_by_id(request_id)
        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de aprobacion no encontrada",
            )

        req_status = approval.status
        if hasattr(req_status, "value"):
            req_status = req_status.value
        if req_status != "pending":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden rechazar solicitudes pendientes",
            )

        approval.status = "rejected"
        approval.reviewed_by_user_id = reviewer_id
        approval.review_notes = data.review_notes
        approval.reviewed_at = datetime.now(timezone.utc)

        # Side effect: if policy_submission, cancel the policy
        req_type = approval.request_type
        if hasattr(req_type, "value"):
            req_type = req_type.value
        if req_type == "policy_submission" and approval.entity_id:
            policy = await self.repo.get_policy(approval.entity_id)
            if policy:
                policy.status = "cancelled"

        return await self.repo.update_approval(approval)

    # ── Helpers ───────────────────────────────────────────────────────

    async def _activate_policy(self, policy_id: int) -> None:
        """Set a policy to active or pre_effective based on its dates."""
        policy = await self.repo.get_policy(policy_id)
        if policy is None:
            return
        today = date.today()
        if policy.effective_date and today < policy.effective_date:
            policy.status = "pre_effective"
        else:
            policy.status = "active"
