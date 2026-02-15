"""
Incident tables: Adjuster, AdjusterShift, Incident, Hospital, MedicalPass,
Workshop, WorkshopPass, TowProvider, TowService,
IncidentSatisfactionSurvey, TowSatisfactionSurvey.
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import (
    EntityStatusType,
    IncidentTypeEnum,
    ResponsibilityType,
    ServiceStatusType,
    ShiftOrderType,
    WorkshopPassTypeEnum,
)

if TYPE_CHECKING:
    from app.models.auth import AppUser
    from app.models.business import Policy
    from app.models.catalog import Address


class Adjuster(Base):
    __tablename__ = "adjuster"
    __table_args__ = (
        UniqueConstraint("code", name="uq_adjuster_code"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[EntityStatusType] = mapped_column(
        Enum(EntityStatusType, name="entity_status_type", create_type=False),
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
    shifts: Mapped[list[AdjusterShift]] = relationship(
        back_populates="adjuster", cascade="all, delete-orphan"
    )
    incidents: Mapped[list[Incident]] = relationship(back_populates="adjuster")


class AdjusterShift(Base):
    __tablename__ = "adjuster_shift"
    __table_args__ = (
        UniqueConstraint("shift_date", "adjuster_id", name="uq_shift_date_adjuster"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shift_date: Mapped[date] = mapped_column(Date, nullable=False)
    adjuster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("adjuster.id", ondelete="CASCADE"), nullable=False
    )
    shift_order: Mapped[ShiftOrderType] = mapped_column(
        Enum(ShiftOrderType, name="shift_order_type", create_type=False),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    adjuster: Mapped[Adjuster] = relationship(back_populates="shifts")


class Incident(Base):
    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=True
    )
    report_number: Mapped[str] = mapped_column(String(20), nullable=False)
    requester_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    origin_address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id", ondelete="SET NULL"), nullable=True
    )
    incident_type: Mapped[IncidentTypeEnum | None] = mapped_column(
        Enum(IncidentTypeEnum, name="incident_type_enum", create_type=False),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibility: Mapped[ResponsibilityType | None] = mapped_column(
        Enum(ResponsibilityType, name="responsibility_type", create_type=False),
        nullable=True,
    )
    client_misconduct: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    adjuster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("adjuster.id", ondelete="RESTRICT"), nullable=False
    )
    report_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    contact_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completion_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attended_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id"), nullable=True
    )
    service_status: Mapped[ServiceStatusType] = mapped_column(
        Enum(ServiceStatusType, name="service_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    satisfaction_rating: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy | None] = relationship(back_populates="incidents")
    origin_address: Mapped[Address | None] = relationship(
        back_populates="incidents_origin",
        foreign_keys=[origin_address_id],
    )
    adjuster: Mapped[Adjuster] = relationship(back_populates="incidents")
    attended_by_user: Mapped[AppUser | None] = relationship(
        back_populates="attended_incidents",
        foreign_keys=[attended_by_user_id],
    )
    medical_passes: Mapped[list[MedicalPass]] = relationship(back_populates="incident")
    workshop_passes: Mapped[list[WorkshopPass]] = relationship(
        back_populates="incident"
    )
    survey: Mapped[IncidentSatisfactionSurvey | None] = relationship(
        back_populates="incident", uselist=False
    )


class Hospital(Base):
    __tablename__ = "hospital"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id"), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[EntityStatusType] = mapped_column(
        Enum(EntityStatusType, name="entity_status_type", create_type=False),
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
    address: Mapped[Address | None] = relationship(back_populates="hospitals")
    medical_passes: Mapped[list[MedicalPass]] = relationship(back_populates="hospital")


class MedicalPass(Base):
    __tablename__ = "medical_pass"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incident.id", ondelete="RESTRICT"), nullable=False
    )
    hospital_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("hospital.id", ondelete="RESTRICT"), nullable=False
    )
    pass_number: Mapped[str] = mapped_column(String(50), nullable=False)
    beneficiary_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    injuries: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[ServiceStatusType] = mapped_column(
        Enum(ServiceStatusType, name="service_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    incident: Mapped[Incident] = relationship(back_populates="medical_passes")
    hospital: Mapped[Hospital] = relationship(back_populates="medical_passes")


class Workshop(Base):
    __tablename__ = "workshop"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id"), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[EntityStatusType] = mapped_column(
        Enum(EntityStatusType, name="entity_status_type", create_type=False),
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
    address: Mapped[Address | None] = relationship(back_populates="workshops")
    workshop_passes: Mapped[list[WorkshopPass]] = relationship(
        back_populates="workshop"
    )


class WorkshopPass(Base):
    __tablename__ = "workshop_pass"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incident.id", ondelete="RESTRICT"), nullable=False
    )
    workshop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workshop.id", ondelete="RESTRICT"), nullable=False
    )
    pass_number: Mapped[str] = mapped_column(String(50), nullable=False)
    beneficiary_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pass_type: Mapped[WorkshopPassTypeEnum] = mapped_column(
        Enum(WorkshopPassTypeEnum, name="workshop_pass_type_enum", create_type=False),
        nullable=False,
    )
    vehicle_damages: Mapped[str | None] = mapped_column(Text, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[ServiceStatusType] = mapped_column(
        Enum(ServiceStatusType, name="service_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    incident: Mapped[Incident] = relationship(back_populates="workshop_passes")
    workshop: Mapped[Workshop] = relationship(back_populates="workshop_passes")


class TowProvider(Base):
    __tablename__ = "tow_provider"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telegram_group_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[EntityStatusType] = mapped_column(
        Enum(EntityStatusType, name="entity_status_type", create_type=False),
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
    address: Mapped[Address | None] = relationship(back_populates="tow_providers")
    tow_services: Mapped[list[TowService]] = relationship(
        back_populates="tow_provider"
    )


class TowService(Base):
    __tablename__ = "tow_service"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="RESTRICT"), nullable=True
    )
    report_number: Mapped[str] = mapped_column(String(20), nullable=False)
    requester_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    origin_address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id", ondelete="SET NULL"), nullable=True
    )
    destination_address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id", ondelete="SET NULL"), nullable=True
    )
    vehicle_failure: Mapped[str] = mapped_column(String(100), nullable=False)
    load_weight: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tow_provider_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("tow_provider.id", ondelete="SET NULL"), nullable=True
    )
    tow_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    extra_charge: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_arrival_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    report_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    attended_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id"), nullable=True
    )
    contact_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_status: Mapped[ServiceStatusType] = mapped_column(
        Enum(ServiceStatusType, name="service_status_type", create_type=False),
        nullable=False,
        server_default="pending",
    )
    satisfaction_rating: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy | None] = relationship(back_populates="tow_services")
    origin_address: Mapped[Address | None] = relationship(
        back_populates="tow_services_origin",
        foreign_keys=[origin_address_id],
    )
    destination_address: Mapped[Address | None] = relationship(
        back_populates="tow_services_destination",
        foreign_keys=[destination_address_id],
    )
    tow_provider: Mapped[TowProvider | None] = relationship(
        back_populates="tow_services"
    )
    attended_by_user: Mapped[AppUser | None] = relationship(
        back_populates="attended_tow_services",
        foreign_keys=[attended_by_user_id],
    )
    survey: Mapped[TowSatisfactionSurvey | None] = relationship(
        back_populates="tow_service", uselist=False
    )


class IncidentSatisfactionSurvey(Base):
    __tablename__ = "incident_satisfaction_survey"
    __table_args__ = (
        UniqueConstraint("incident_id", name="uq_incident_survey"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    incident_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("incident.id", ondelete="RESTRICT"), nullable=False
    )
    survey_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    response_time_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    service_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    overall_service_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    company_impression: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    surveyed_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    incident: Mapped[Incident] = relationship(back_populates="survey")
    surveyed_by_user: Mapped[AppUser | None] = relationship(
        back_populates="incident_surveys",
        foreign_keys=[surveyed_by_user_id],
    )


class TowSatisfactionSurvey(Base):
    __tablename__ = "tow_satisfaction_survey"
    __table_args__ = (
        UniqueConstraint("tow_service_id", name="uq_tow_survey"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tow_service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tow_service.id", ondelete="RESTRICT"), nullable=False
    )
    survey_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    response_time_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    service_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    overall_service_rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    company_impression: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    surveyed_by_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    tow_service: Mapped[TowService] = relationship(back_populates="survey")
    surveyed_by_user: Mapped[AppUser | None] = relationship(
        back_populates="tow_surveys",
        foreign_keys=[surveyed_by_user_id],
    )
