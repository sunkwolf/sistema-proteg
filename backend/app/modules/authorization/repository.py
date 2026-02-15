"""Data access layer for authorization (proposals + approvals)."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ApprovalRequest
from app.models.payments import Payment, PaymentProposal


class AuthorizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Payment Proposals ────────────────────────────────────────────

    async def get_proposal_by_id(self, proposal_id: int) -> PaymentProposal | None:
        result = await self.session.execute(
            select(PaymentProposal).where(PaymentProposal.id == proposal_id)
        )
        return result.scalar_one_or_none()

    async def list_proposals(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status: str | None = None,
        collector_id: int | None = None,
        policy_id: int | None = None,
    ) -> tuple[list[PaymentProposal], int]:
        query = select(PaymentProposal)
        count_query = select(func.count(PaymentProposal.id))

        if status is not None:
            query = query.where(PaymentProposal.draft_status == status)
            count_query = count_query.where(PaymentProposal.draft_status == status)
        if collector_id is not None:
            query = query.where(PaymentProposal.collector_id == collector_id)
            count_query = count_query.where(PaymentProposal.collector_id == collector_id)
        if policy_id is not None:
            query = query.where(PaymentProposal.policy_id == policy_id)
            count_query = count_query.where(PaymentProposal.policy_id == policy_id)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(PaymentProposal.id.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        proposals = list(result.scalars().all())

        return proposals, total

    async def active_proposal_exists(self, original_payment_id: int) -> bool:
        result = await self.session.execute(
            select(func.count(PaymentProposal.id)).where(
                PaymentProposal.original_payment_id == original_payment_id,
                PaymentProposal.draft_status == "active",
            )
        )
        return result.scalar_one() > 0

    async def create_proposal(self, proposal: PaymentProposal) -> PaymentProposal:
        self.session.add(proposal)
        await self.session.flush()
        await self.session.refresh(proposal)
        return proposal

    async def update_proposal(self, proposal: PaymentProposal) -> PaymentProposal:
        await self.session.flush()
        await self.session.refresh(proposal)
        return proposal

    # ── Original Payment ─────────────────────────────────────────────

    async def get_payment(self, payment_id: int) -> Payment | None:
        result = await self.session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()

    # ── Approval Requests ────────────────────────────────────────────

    async def get_approval_by_id(self, request_id: int) -> ApprovalRequest | None:
        result = await self.session.execute(
            select(ApprovalRequest).where(ApprovalRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def list_pending_approvals(
        self,
        *,
        request_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[ApprovalRequest], int]:
        query = select(ApprovalRequest).where(ApprovalRequest.status == "pending")
        count_query = select(func.count(ApprovalRequest.id)).where(
            ApprovalRequest.status == "pending"
        )

        if request_type is not None:
            query = query.where(ApprovalRequest.request_type == request_type)
            count_query = count_query.where(ApprovalRequest.request_type == request_type)

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(ApprovalRequest.submitted_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        requests = list(result.scalars().all())

        return requests, total

    async def update_approval(self, request: ApprovalRequest) -> ApprovalRequest:
        await self.session.flush()
        await self.session.refresh(request)
        return request
