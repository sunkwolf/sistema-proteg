"""
Audit and log tables: ExecutionLog, AuditLog, ApprovalRequest,
MobileActionLog, Cancellation, ReportNumberSequence.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import ApprovalRequestType, ApprovalStatusType

if TYPE_CHECKING:
    from app.models.auth import AppUser, DeviceSession
    from app.models.business import Policy


class ExecutionLog(Base):
    __tablename__ = "execution_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"postgresql_partition_by": "RANGE (changed_at)"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    table_name: Mapped[str] = mapped_column(String(63), nullable=False)
    record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    old_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    changed_by_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
        primary_key=True,
    )


class ApprovalRequest(Base):
    __tablename__ = "approval_request"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_type: Mapped[ApprovalRequestType] = mapped_column(
        Enum(ApprovalRequestType, name="approval_request_type", create_type=False),
        nullable=False,
    )
    status: Mapped[ApprovalStatusType] = mapped_column(
        Enum(ApprovalStatusType, name="approval_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    submitted_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="RESTRICT"), nullable=False
    )
    submitted_from_device_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("device_session.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    submitted_by_user: Mapped[AppUser] = relationship(
        back_populates="submitted_approval_requests",
        foreign_keys=[submitted_by_user_id],
    )
    submitted_from_device: Mapped[DeviceSession | None] = relationship(
        back_populates="approval_requests",
        foreign_keys=[submitted_from_device_id],
    )
    reviewed_by_user: Mapped[AppUser | None] = relationship(
        back_populates="reviewed_approval_requests",
        foreign_keys=[reviewed_by_user_id],
    )


class MobileActionLog(Base):
    __tablename__ = "mobile_action_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    device_session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("device_session.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(11, 8), nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    request_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    response_status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    device_session: Mapped[DeviceSession] = relationship(
        back_populates="mobile_action_logs"
    )
    user: Mapped[AppUser] = relationship(back_populates="mobile_action_logs")


class Cancellation(Base):
    __tablename__ = "cancellation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=False
    )
    cancellation_date: Mapped[date] = mapped_column(Date, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    code: Mapped[str | None] = mapped_column(String(45), nullable=True)
    payments_made: Mapped[int | None] = mapped_column(
        Integer, server_default="0", nullable=True
    )
    cancelled_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    notification_sent_seller: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    notification_sent_collector: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    notification_sent_client: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy] = relationship(back_populates="cancellations")
    cancelled_by_user: Mapped[AppUser | None] = relationship(
        back_populates="cancellations",
        foreign_keys=[cancelled_by_user_id],
    )


class ReportNumberSequence(Base):
    __tablename__ = "report_number_sequence"
    __table_args__ = (
        UniqueConstraint("prefix", "date_part", name="uq_report_seq"),
    )

    prefix: Mapped[str] = mapped_column(String(10), primary_key=True)
    date_part: Mapped[str] = mapped_column(String(8), nullable=False)
    last_number: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
