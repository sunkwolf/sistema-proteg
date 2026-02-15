"""
Endorsement and Renewal tables.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import EndorsementStatusType, EndorsementTypeEnum, RenewalStatusType

if TYPE_CHECKING:
    from app.models.business import Client, Policy, Vehicle


class Endorsement(Base):
    __tablename__ = "endorsement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    endorsement_type: Mapped[EndorsementTypeEnum] = mapped_column(
        Enum(EndorsementTypeEnum, name="endorsement_type_enum", create_type=False),
        nullable=False,
    )
    request_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    application_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[EndorsementStatusType] = mapped_column(
        Enum(EndorsementStatusType, name="endorsement_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    change_details: Mapped[dict] = mapped_column(JSONB, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_contractor_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("client.id"), nullable=True
    )
    previous_vehicle_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("vehicle.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy] = relationship(back_populates="endorsements")
    new_contractor: Mapped[Client | None] = relationship(
        back_populates="endorsements_as_new_contractor",
        foreign_keys=[new_contractor_id],
    )
    previous_vehicle: Mapped[Vehicle | None] = relationship(
        back_populates="endorsements_as_previous",
        foreign_keys=[previous_vehicle_id],
    )


class Renewal(Base):
    __tablename__ = "renewal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    old_policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    new_policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="SET NULL"), nullable=True
    )
    renewal_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[RenewalStatusType] = mapped_column(
        Enum(RenewalStatusType, name="renewal_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    old_policy: Mapped[Policy] = relationship(
        back_populates="renewals_as_old",
        foreign_keys=[old_policy_id],
    )
    new_policy: Mapped[Policy | None] = relationship(
        back_populates="renewals_as_new",
        foreign_keys=[new_policy_id],
    )
