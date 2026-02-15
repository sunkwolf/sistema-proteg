"""Business logic for promotions, rules, and applications."""

from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.promotions import Promotion, PromotionApplication, PromotionRule
from app.modules.promotions.repository import PromotionRepository
from app.modules.promotions.schemas import (
    PromotionApplyRequest,
    PromotionApplicationListResponse,
    PromotionApplicationResponse,
    PromotionCreate,
    PromotionListResponse,
    PromotionResponse,
    PromotionRuleCreate,
    PromotionRuleResponse,
    PromotionRuleUpdate,
    PromotionUpdate,
)


class PromotionService:
    def __init__(self, session: AsyncSession):
        self.repo = PromotionRepository(session)

    # ── Promotion CRUD ─────────────────────────────────────────────

    async def list_promotions(
        self, *, skip: int = 0, limit: int = 50, status_filter: str | None = None
    ) -> PromotionListResponse:
        items, total = await self.repo.list_promotions(
            skip=skip, limit=limit, status=status_filter
        )
        return PromotionListResponse(
            items=[_promotion_to_response(p) for p in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_promotion(self, promotion_id: int) -> PromotionResponse:
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        return _promotion_to_response(promo)

    async def create_promotion(self, data: PromotionCreate) -> PromotionResponse:
        promo = Promotion(
            name=data.name,
            description=data.description,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        promo = await self.repo.create(promo)
        return _promotion_to_response(promo)

    async def update_promotion(
        self, promotion_id: int, data: PromotionUpdate
    ) -> PromotionResponse:
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(promo, field, value)
        promo = await self.repo.update(promo)
        return _promotion_to_response(promo)

    async def list_active_promotions(self) -> list[PromotionResponse]:
        promos = await self.repo.list_active_promotions()
        return [_promotion_to_response(p) for p in promos]

    # ── Promotion Rules ────────────────────────────────────────────

    async def list_rules(self, promotion_id: int) -> list[PromotionRuleResponse]:
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        rules = await self.repo.list_rules(promotion_id)
        return [_rule_to_response(r) for r in rules]

    async def create_rule(
        self, promotion_id: int, data: PromotionRuleCreate
    ) -> PromotionRuleResponse:
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        rule = PromotionRule(
            promotion_id=promotion_id,
            discount_type=data.discount_type,
            discount_value=data.discount_value,
            applies_to_payment_number=data.applies_to_payment_number,
            min_payments=data.min_payments,
            max_payments=data.max_payments,
            coverage_ids=data.coverage_ids,
            vehicle_types=data.vehicle_types,
            requires_referral=data.requires_referral,
            description=data.description,
        )
        rule = await self.repo.create_rule(rule)
        return _rule_to_response(rule)

    async def update_rule(
        self, promotion_id: int, rule_id: int, data: PromotionRuleUpdate
    ) -> PromotionRuleResponse:
        rule = await self.repo.get_rule_by_id(rule_id)
        if rule is None or rule.promotion_id != promotion_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion rule not found",
            )
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)
        rule = await self.repo.update_rule(rule)
        return _rule_to_response(rule)

    async def delete_rule(self, promotion_id: int, rule_id: int) -> None:
        rule = await self.repo.get_rule_by_id(rule_id)
        if rule is None or rule.promotion_id != promotion_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion rule not found",
            )
        await self.repo.delete_rule(rule)

    # ── Apply Promotion ────────────────────────────────────────────

    async def apply_promotion(
        self,
        promotion_id: int,
        rule_id: int,
        data: PromotionApplyRequest,
        user_id: int | None = None,
    ) -> PromotionApplicationResponse:
        # Validate promotion is active
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        promo_status = promo.status
        if hasattr(promo_status, "value"):
            promo_status = promo_status.value
        if promo_status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promotion is not active",
            )

        # Validate rule belongs to promotion
        rule = await self.repo.get_rule_by_id(rule_id)
        if rule is None or rule.promotion_id != promotion_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion rule not found",
            )

        # Validate policy exists
        policy = await self.repo.get_policy(data.policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found",
            )

        # Validate referral if required
        if rule.requires_referral and data.referrer_policy_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This rule requires a referrer policy",
            )
        if data.referrer_policy_id is not None:
            ref_policy = await self.repo.get_policy(data.referrer_policy_id)
            if ref_policy is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Referrer policy not found",
                )

        # Check duplicate application
        existing = await self.repo.get_existing_application(
            promotion_id, data.policy_id, rule_id
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Promotion already applied to this policy with this rule",
            )

        # Calculate discount
        discount_applied = _calculate_discount(rule)

        app = PromotionApplication(
            promotion_id=promotion_id,
            promotion_rule_id=rule_id,
            policy_id=data.policy_id,
            referrer_policy_id=data.referrer_policy_id,
            discount_applied=discount_applied,
            applied_by_user_id=user_id,
            comments=data.comments,
        )
        app = await self.repo.create_application(app)
        return _application_to_response(app)

    async def simulate_promotion(
        self, promotion_id: int, rule_id: int
    ) -> dict:
        """Return calculated discount without persisting."""
        rule = await self.repo.get_rule_by_id(rule_id)
        if rule is None or rule.promotion_id != promotion_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion rule not found",
            )
        discount = _calculate_discount(rule)
        discount_type = rule.discount_type
        if hasattr(discount_type, "value"):
            discount_type = discount_type.value
        return {
            "discount_type": discount_type,
            "discount_value": rule.discount_value,
            "calculated_discount": discount,
            "description": rule.description,
        }

    async def list_applications(
        self, promotion_id: int
    ) -> PromotionApplicationListResponse:
        promo = await self.repo.get_by_id(promotion_id)
        if promo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Promotion not found",
            )
        items, total = await self.repo.list_applications(promotion_id)
        return PromotionApplicationListResponse(
            items=[_application_to_response(a) for a in items],
            total=total,
        )


# ── Helpers ────────────────────────────────────────────────────────


def _calculate_discount(rule: PromotionRule) -> Decimal:
    """Calculate the discount amount based on rule type.

    - percentage: stored value is the % (e.g. 10 means 10%).
      The actual monetary discount depends on the payment amount,
      so we record the percentage value itself.
    - fixed_amount: direct monetary discount.
    - free_months: number of months free (recorded as the value).
    - zero_down_payment: the enganche is waived (discount = value or 0).
    """
    discount_type = rule.discount_type
    if hasattr(discount_type, "value"):
        discount_type = discount_type.value

    return rule.discount_value


def _promotion_to_response(promo: Promotion) -> PromotionResponse:
    st = promo.status
    if hasattr(st, "value"):
        st = st.value
    return PromotionResponse(
        id=promo.id,
        name=promo.name,
        description=promo.description,
        status=st,
        start_date=promo.start_date,
        end_date=promo.end_date,
        created_at=promo.created_at,
        updated_at=promo.updated_at,
    )


def _rule_to_response(rule: PromotionRule) -> PromotionRuleResponse:
    dt = rule.discount_type
    if hasattr(dt, "value"):
        dt = dt.value
    return PromotionRuleResponse(
        id=rule.id,
        promotion_id=rule.promotion_id,
        discount_type=dt,
        discount_value=rule.discount_value,
        applies_to_payment_number=rule.applies_to_payment_number,
        min_payments=rule.min_payments,
        max_payments=rule.max_payments,
        coverage_ids=rule.coverage_ids,
        vehicle_types=rule.vehicle_types,
        requires_referral=rule.requires_referral,
        description=rule.description,
        created_at=rule.created_at,
    )


def _application_to_response(app: PromotionApplication) -> PromotionApplicationResponse:
    return PromotionApplicationResponse(
        id=app.id,
        promotion_id=app.promotion_id,
        promotion_rule_id=app.promotion_rule_id,
        policy_id=app.policy_id,
        referrer_policy_id=app.referrer_policy_id,
        discount_applied=app.discount_applied,
        applied_by_user_id=app.applied_by_user_id,
        comments=app.comments,
        applied_at=app.applied_at,
    )
