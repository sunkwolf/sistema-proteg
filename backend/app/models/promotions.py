"""
Promotion tables: Promotion, PromotionRule, PromotionApplication, CommissionRate.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    EntityStatusType,
    PromotionDiscountType,
    SellerClassType,
)

if TYPE_CHECKING:
    from app.models.auth import AppUser
    from app.models.business import Coverage, Policy


class Promotion(Base):
    __tablename__ = "promotion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EntityStatusType] = mapped_column(
        Enum(EntityStatusType, name="entity_status_type", create_type=False),
        nullable=False,
        server_default="active",
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    rules: Mapped[list[PromotionRule]] = relationship(
        back_populates="promotion", cascade="all, delete-orphan"
    )
    applications: Mapped[list[PromotionApplication]] = relationship(
        back_populates="promotion"
    )


class PromotionRule(Base):
    __tablename__ = "promotion_rule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    promotion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("promotion.id", ondelete="CASCADE"), nullable=False
    )
    discount_type: Mapped[PromotionDiscountType] = mapped_column(
        Enum(
            PromotionDiscountType,
            name="promotion_discount_type",
            create_type=False,
        ),
        nullable=False,
    )
    discount_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    applies_to_payment_number: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    min_payments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_payments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coverage_ids: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    vehicle_types: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    requires_referral: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    promotion: Mapped[Promotion] = relationship(back_populates="rules")
    applications: Mapped[list[PromotionApplication]] = relationship(
        back_populates="promotion_rule"
    )


class PromotionApplication(Base):
    __tablename__ = "promotion_application"
    __table_args__ = (
        UniqueConstraint(
            "promotion_id",
            "policy_id",
            "promotion_rule_id",
            name="uq_promo_application",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    promotion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("promotion.id", ondelete="RESTRICT"), nullable=False
    )
    promotion_rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("promotion_rule.id", ondelete="RESTRICT"), nullable=False
    )
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    referrer_policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="SET NULL"), nullable=True
    )
    discount_applied: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    applied_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    promotion: Mapped[Promotion] = relationship(back_populates="applications")
    promotion_rule: Mapped[PromotionRule] = relationship(back_populates="applications")
    policy: Mapped[Policy] = relationship(
        back_populates="promotion_applications",
        foreign_keys=[policy_id],
    )
    referrer_policy: Mapped[Policy | None] = relationship(
        back_populates="referrer_promotion_applications",
        foreign_keys=[referrer_policy_id],
    )
    applied_by_user: Mapped[AppUser | None] = relationship(
        back_populates="promotion_applications",
        foreign_keys=[applied_by_user_id],
    )


class CommissionRate(Base):
    __tablename__ = "commission_rate"
    __table_args__ = (
        UniqueConstraint("role", "level", "coverage_id", name="uq_commission"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[SellerClassType] = mapped_column(
        Enum(SellerClassType, name="seller_class_type", create_type=False),
        nullable=False,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    coverage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("coverage.id", ondelete="RESTRICT"), nullable=False
    )
    percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    coverage: Mapped[Coverage] = relationship(back_populates="commission_rates")
