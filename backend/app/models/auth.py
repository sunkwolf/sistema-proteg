"""
Auth tables: Department, Role, Permission, RolePermission, AppUser, Session, DeviceSession.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AppTypeEnum, DeviceTypeEnum

if TYPE_CHECKING:
    from app.models.audit import ApprovalRequest, AuditLog, MobileActionLog
    from app.models.business import Policy
    from app.models.incidents import Incident, TowService
    from app.models.notifications import SentMessage
    from app.models.payments import Payment, PaymentProposal
    from app.models.promotions import PromotionApplication


class Department(Base):
    __tablename__ = "department"
    __table_args__ = (
        UniqueConstraint("name", name="uq_department_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    users: Mapped[list[AppUser]] = relationship(back_populates="department")


class Role(Base):
    __tablename__ = "role"
    __table_args__ = (
        UniqueConstraint("name", name="uq_role_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    users: Mapped[list[AppUser]] = relationship(back_populates="role")
    role_permissions: Mapped[list[RolePermission]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )


class Permission(Base):
    __tablename__ = "permission"
    __table_args__ = (
        UniqueConstraint("name", name="uq_permission_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    role_permissions: Mapped[list[RolePermission]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    role: Mapped[Role] = relationship(back_populates="role_permissions")
    permission: Mapped[Permission] = relationship(back_populates="role_permissions")


class AppUser(Base):
    __tablename__ = "app_user"
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("department.id", ondelete="SET NULL"), nullable=True
    )
    role_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("role.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    totp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped[Department | None] = relationship(back_populates="users")
    role: Mapped[Role | None] = relationship(back_populates="users")
    sessions: Mapped[list[Session]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    device_sessions: Mapped[list[DeviceSession]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # Policies where this user is data_entry
    data_entry_policies: Mapped[list[Policy]] = relationship(
        back_populates="data_entry_user",
        foreign_keys="[Policy.data_entry_user_id]",
    )
    # Payments
    payments: Mapped[list[Payment]] = relationship(
        back_populates="user", foreign_keys="[Payment.user_id]"
    )
    payment_proposals: Mapped[list[PaymentProposal]] = relationship(
        back_populates="user", foreign_keys="[PaymentProposal.user_id]"
    )
    # Incidents
    attended_incidents: Mapped[list[Incident]] = relationship(
        back_populates="attended_by_user",
        foreign_keys="[Incident.attended_by_user_id]",
    )
    attended_tow_services: Mapped[list[TowService]] = relationship(
        back_populates="attended_by_user",
        foreign_keys="[TowService.attended_by_user_id]",
    )
    # Cancellations
    cancellations: Mapped[list["Cancellation"]] = relationship(  # noqa: F821
        back_populates="cancelled_by_user",
        foreign_keys="[Cancellation.cancelled_by_user_id]",
    )
    # Approval requests submitted
    submitted_approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        back_populates="submitted_by_user",
        foreign_keys="[ApprovalRequest.submitted_by_user_id]",
    )
    # Approval requests reviewed
    reviewed_approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        back_populates="reviewed_by_user",
        foreign_keys="[ApprovalRequest.reviewed_by_user_id]",
    )
    # Mobile action logs
    mobile_action_logs: Mapped[list[MobileActionLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    # Sent messages
    sent_messages: Mapped[list[SentMessage]] = relationship(
        back_populates="sent_by_user",
        foreign_keys="[SentMessage.sent_by_user_id]",
    )
    # Promotion applications
    promotion_applications: Mapped[list[PromotionApplication]] = relationship(
        back_populates="applied_by_user",
        foreign_keys="[PromotionApplication.applied_by_user_id]",
    )
    # Satisfaction surveys
    incident_surveys: Mapped[list["IncidentSatisfactionSurvey"]] = relationship(  # noqa: F821
        back_populates="surveyed_by_user",
        foreign_keys="[IncidentSatisfactionSurvey.surveyed_by_user_id]",
    )
    tow_surveys: Mapped[list["TowSatisfactionSurvey"]] = relationship(  # noqa: F821
        back_populates="surveyed_by_user",
        foreign_keys="[TowSatisfactionSurvey.surveyed_by_user_id]",
    )


class Session(Base):
    __tablename__ = "session"
    __table_args__ = (
        UniqueConstraint("token", name="uq_session_token"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[AppUser] = relationship(back_populates="sessions")


class DeviceSession(Base):
    __tablename__ = "device_session"
    __table_args__ = (
        UniqueConstraint("token", name="uq_device_session_token"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="CASCADE"), nullable=False
    )
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[DeviceTypeEnum] = mapped_column(
        Enum(DeviceTypeEnum, name="device_type_enum", create_type=False),
        nullable=False,
    )
    app_type: Mapped[AppTypeEnum] = mapped_column(
        Enum(AppTypeEnum, name="app_type_enum", create_type=False),
        nullable=False,
    )
    app_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    push_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped[AppUser] = relationship(back_populates="device_sessions")
    approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        back_populates="submitted_from_device",
        foreign_keys="[ApprovalRequest.submitted_from_device_id]",
    )
    mobile_action_logs: Mapped[list[MobileActionLog]] = relationship(
        back_populates="device_session", cascade="all, delete-orphan"
    )
