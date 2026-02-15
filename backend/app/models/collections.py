"""
Collections tables: Card, CollectionAssignment, VisitNotice.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CardStatusType

if TYPE_CHECKING:
    from app.models.business import Policy, Seller
    from app.models.payments import Payment


class Card(Base):
    __tablename__ = "card"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    current_holder: Mapped[str] = mapped_column(String(50), nullable=False)
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)
    seller_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("seller.id"), nullable=True
    )
    status: Mapped[CardStatusType] = mapped_column(
        Enum(CardStatusType, name="card_status_type", create_type=False),
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
    policy: Mapped[Policy] = relationship(back_populates="cards")
    seller: Mapped[Seller | None] = relationship(back_populates="cards")
    assignments: Mapped[list[CollectionAssignment]] = relationship(
        back_populates="card", cascade="all, delete-orphan"
    )
    visit_notices: Mapped[list[VisitNotice]] = relationship(back_populates="card")


class CollectionAssignment(Base):
    __tablename__ = "collection_assignment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("card.id", ondelete="CASCADE"), nullable=False
    )
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    assigned_to: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    route: Mapped[str | None] = mapped_column(String(50), nullable=True)
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    card: Mapped[Card] = relationship(back_populates="assignments")
    policy: Mapped[Policy] = relationship(back_populates="collection_assignments")


class VisitNotice(Base):
    __tablename__ = "visit_notice"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("card.id", ondelete="SET NULL"), nullable=True
    )
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("payment.id", ondelete="SET NULL"), nullable=True
    )
    notice_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    card: Mapped[Card | None] = relationship(back_populates="visit_notices")
    policy: Mapped[Policy] = relationship(back_populates="visit_notices")
    payment: Mapped[Payment | None] = relationship(back_populates="visit_notices")
