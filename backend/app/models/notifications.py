"""
Notification tables: SentMessage, PolicyNotification, RenewalNotificationLog.
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
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    MessageChannelType,
    MessageDeliveryStatusType,
    MessageTypeEnum,
    NotificationPeriodType,
)

if TYPE_CHECKING:
    from app.models.auth import AppUser
    from app.models.business import Employee, Policy


class SentMessage(Base):
    __tablename__ = "sent_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="SET NULL"), nullable=True
    )
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    message_type: Mapped[MessageTypeEnum] = mapped_column(
        Enum(MessageTypeEnum, name="message_type_enum", create_type=False),
        nullable=False,
    )
    channel: Mapped[MessageChannelType] = mapped_column(
        Enum(MessageChannelType, name="message_channel_type", create_type=False),
        nullable=False,
        server_default="whatsapp",
    )
    delivery_status: Mapped[MessageDeliveryStatusType] = mapped_column(
        Enum(
            MessageDeliveryStatusType,
            name="message_delivery_status_type",
            create_type=False,
        ),
        nullable=False,
        server_default="queued",
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    target_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    days_before_due: Mapped[int | None] = mapped_column(Integer, nullable=True)
    retry_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="0"
    )
    max_retries: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default="3"
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_message_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    source_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    sent_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy | None] = relationship(back_populates="sent_messages")
    sent_by_user: Mapped[AppUser | None] = relationship(
        back_populates="sent_messages",
        foreign_keys=[sent_by_user_id],
    )


class PolicyNotification(Base):
    __tablename__ = "policy_notification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="CASCADE"), nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationPeriodType] = mapped_column(
        Enum(
            NotificationPeriodType,
            name="notification_period_type",
            create_type=False,
        ),
        nullable=False,
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy] = relationship(back_populates="policy_notifications")
    seller: Mapped[Employee] = relationship(back_populates="policy_notifications")


class RenewalNotificationLog(Base):
    __tablename__ = "renewal_notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationPeriodType] = mapped_column(
        Enum(
            NotificationPeriodType,
            name="notification_period_type",
            create_type=False,
        ),
        nullable=False,
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    sent_by: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="system"
    )

    # Relationships
    policy: Mapped[Policy] = relationship(
        back_populates="renewal_notification_logs"
    )
