"""
Payment tables: Payment, PaymentProposal, Receipt, ReceiptLossSchedule.
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    OfficeDeliveryType,
    PaymentMethodType,
    PaymentProposalStatusType,
    PaymentStatusType,
    ReceiptStatusType,
)

if TYPE_CHECKING:
    from app.models.auth import AppUser
    from app.models.business import Collector, Policy, Seller
    from app.models.collections import VisitNotice


class Payment(Base):
    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    seller_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("seller.id", ondelete="SET NULL"), nullable=True
    )
    collector_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("collector.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    payment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    receipt_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    payment_method: Mapped[PaymentMethodType | None] = mapped_column(
        Enum(PaymentMethodType, name="payment_method_type", create_type=False),
        nullable=True,
    )
    office_delivery_status: Mapped[OfficeDeliveryType | None] = mapped_column(
        Enum(OfficeDeliveryType, name="office_delivery_type", create_type=False),
        nullable=True,
    )
    office_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    policy_delivered: Mapped[bool | None] = mapped_column(
        Boolean, server_default="false", nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PaymentStatusType] = mapped_column(
        Enum(PaymentStatusType, name="payment_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy] = relationship(back_populates="payments")
    seller: Mapped[Seller | None] = relationship(
        back_populates="payments", foreign_keys=[seller_id]
    )
    collector: Mapped[Collector | None] = relationship(
        back_populates="payments", foreign_keys=[collector_id]
    )
    user: Mapped[AppUser | None] = relationship(
        back_populates="payments", foreign_keys=[user_id]
    )
    proposals: Mapped[list[PaymentProposal]] = relationship(
        back_populates="original_payment"
    )
    receipts: Mapped[list[Receipt]] = relationship(back_populates="payment")
    visit_notices: Mapped[list[VisitNotice]] = relationship(back_populates="payment")


class PaymentProposal(Base):
    __tablename__ = "payment_proposal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_payment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("payment.id", ondelete="RESTRICT"), nullable=False
    )
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    seller_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("seller.id", ondelete="SET NULL"), nullable=True
    )
    collector_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("collector.id", ondelete="SET NULL"), nullable=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    payment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    receipt_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    payment_method: Mapped[PaymentMethodType | None] = mapped_column(
        Enum(PaymentMethodType, name="payment_method_type", create_type=False),
        nullable=True,
    )
    office_delivery_status: Mapped[OfficeDeliveryType | None] = mapped_column(
        Enum(OfficeDeliveryType, name="office_delivery_type", create_type=False),
        nullable=True,
    )
    office_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    policy_delivered: Mapped[bool | None] = mapped_column(
        Boolean, server_default="false", nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_status: Mapped[PaymentStatusType] = mapped_column(
        Enum(PaymentStatusType, name="payment_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    draft_status: Mapped[PaymentProposalStatusType] = mapped_column(
        Enum(
            PaymentProposalStatusType,
            name="payment_proposal_status_type",
            create_type=False,
        ),
        nullable=False,
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    original_payment: Mapped[Payment] = relationship(back_populates="proposals")
    policy: Mapped[Policy] = relationship(
        back_populates="payment_proposals", foreign_keys=[policy_id]
    )
    seller: Mapped[Seller | None] = relationship(
        back_populates="payment_proposals", foreign_keys=[seller_id]
    )
    collector: Mapped[Collector | None] = relationship(
        back_populates="payment_proposals", foreign_keys=[collector_id]
    )
    user: Mapped[AppUser | None] = relationship(
        back_populates="payment_proposals", foreign_keys=[user_id]
    )


class Receipt(Base):
    __tablename__ = "receipt"
    __table_args__ = (
        UniqueConstraint("receipt_number", name="uq_receipt_number"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receipt_number: Mapped[str] = mapped_column(String(10), nullable=False)
    policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=True
    )
    collector_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("collector.id", ondelete="SET NULL"), nullable=True
    )
    payment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("payment.id", ondelete="SET NULL"), nullable=True
    )
    assignment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    usage_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[ReceiptStatusType] = mapped_column(
        Enum(ReceiptStatusType, name="receipt_status_type", create_type=False),
        nullable=False,
        server_default="unassigned",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy | None] = relationship(back_populates="receipts")
    collector: Mapped[Collector | None] = relationship(back_populates="receipts")
    payment: Mapped[Payment | None] = relationship(back_populates="receipts")


class ReceiptLossSchedule(Base):
    __tablename__ = "receipt_loss_schedule"

    receipt_number: Mapped[str] = mapped_column(String(10), primary_key=True)
    deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
