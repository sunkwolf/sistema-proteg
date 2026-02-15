"""
Core business entities: Client, Employee, EmployeeDepartment, EmployeePermissionOverride,
Vehicle, Coverage, Policy, PolicyAmpliaDetail.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
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
    CoverageCategoryType,
    EntityStatusType,
    GenderType,
    MaritalStatusType,
    PaymentPlanType,
    PolicyStatusType,
    SellerClassType,
    ServiceType,
    VehicleTypeEnum,
)

if TYPE_CHECKING:
    from app.models.audit import Cancellation
    from app.models.auth import AppUser, Department, Permission
    from app.models.catalog import Address
    from app.models.collections import Card, CollectionAssignment, VisitNotice
    from app.models.endorsements import Endorsement, Renewal
    from app.models.incidents import (
        Incident,
        IncidentSatisfactionSurvey,
        TowSatisfactionSurvey,
        TowService,
    )
    from app.models.notifications import (
        PolicyNotification,
        RenewalNotificationLog,
        SentMessage,
    )
    from app.models.payments import Payment, PaymentProposal, Receipt
    from app.models.promotions import CommissionRate, PromotionApplication


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    paternal_surname: Mapped[str] = mapped_column(String(50), nullable=False)
    maternal_surname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rfc: Mapped[str | None] = mapped_column(String(13), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[GenderType | None] = mapped_column(
        Enum(GenderType, name="gender_type", create_type=False), nullable=True
    )
    marital_status: Mapped[MaritalStatusType | None] = mapped_column(
        Enum(MaritalStatusType, name="marital_status_type", create_type=False), nullable=True
    )
    address_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("address.id"), nullable=True
    )
    phone_1: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone_2: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    address: Mapped[Address | None] = relationship(back_populates="clients")
    policies: Mapped[list[Policy]] = relationship(back_populates="client")
    endorsements_as_new_contractor: Mapped[list[Endorsement]] = relationship(
        back_populates="new_contractor",
        foreign_keys="[Endorsement.new_contractor_id]",
    )


class Employee(Base):
    """Unified employee: replaces separate seller/collector tables.
    An employee can be vendedor AND cobrador AND ajustador simultaneously."""
    __tablename__ = "employee"
    __table_args__ = (
        UniqueConstraint("code_name", name="uq_employee_code"),
        UniqueConstraint("user_id", name="uq_employee_user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id", ondelete="SET NULL"), nullable=True
    )
    code_name: Mapped[str] = mapped_column(String(50), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    # Business role flags (can be combined)
    es_vendedor: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    es_cobrador: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    es_ajustador: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # Seller-specific
    seller_class: Mapped[SellerClassType | None] = mapped_column(
        Enum(SellerClassType, name="seller_class_type", create_type=False), nullable=True
    )
    sales_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Collector-specific
    receipt_limit: Mapped[int] = mapped_column(Integer, nullable=False, server_default="50")
    # Common
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
    user: Mapped[AppUser | None] = relationship(foreign_keys=[user_id])
    departments: Mapped[list[EmployeeDepartment]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    permission_overrides: Mapped[list[EmployeePermissionOverride]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    # As seller
    policies: Mapped[list[Policy]] = relationship(back_populates="seller")
    seller_payments: Mapped[list[Payment]] = relationship(
        back_populates="seller", foreign_keys="[Payment.seller_id]"
    )
    seller_proposals: Mapped[list[PaymentProposal]] = relationship(
        back_populates="seller", foreign_keys="[PaymentProposal.seller_id]"
    )
    cards: Mapped[list[Card]] = relationship(back_populates="seller")
    policy_notifications: Mapped[list[PolicyNotification]] = relationship(
        back_populates="seller", cascade="all, delete-orphan"
    )
    # As collector
    collector_payments: Mapped[list[Payment]] = relationship(
        back_populates="collector", foreign_keys="[Payment.collector_id]"
    )
    collector_proposals: Mapped[list[PaymentProposal]] = relationship(
        back_populates="collector", foreign_keys="[PaymentProposal.collector_id]"
    )
    receipts: Mapped[list[Receipt]] = relationship(back_populates="collector")


class EmployeeDepartment(Base):
    """Junction table: employee ↔ department (M:N) with es_gerente flag."""
    __tablename__ = "employee_department"

    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id", ondelete="CASCADE"), primary_key=True
    )
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("department.id", ondelete="CASCADE"), primary_key=True
    )
    es_gerente: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    # Relationships
    employee: Mapped[Employee] = relationship(back_populates="departments")
    department: Mapped[Department] = relationship()


class EmployeePermissionOverride(Base):
    """Individual permission grant/revoke for an employee, independent of role."""
    __tablename__ = "employee_permission_override"
    __table_args__ = (
        UniqueConstraint("employee_id", "permission_id", name="uq_employee_permission"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False
    )
    permission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("permission.id", ondelete="CASCADE"), nullable=False
    )
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    employee: Mapped[Employee] = relationship(back_populates="permission_overrides")
    permission: Mapped[Permission] = relationship()


class Vehicle(Base):
    __tablename__ = "vehicle"
    __table_args__ = (
        UniqueConstraint("serial_number", name="uq_vehicle_serial"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(String(45), nullable=False)
    model_type: Mapped[str | None] = mapped_column(String(45), nullable=True)
    model_year: Mapped[str | None] = mapped_column(String(10), nullable=True)
    color: Mapped[str | None] = mapped_column(String(45), nullable=True)
    vehicle_key: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(45), nullable=True)
    plates: Mapped[str | None] = mapped_column(String(20), nullable=True)
    load_capacity: Mapped[str | None] = mapped_column(String(15), nullable=True)
    vehicle_type: Mapped[VehicleTypeEnum | None] = mapped_column(
        Enum(VehicleTypeEnum, name="vehicle_type_enum", create_type=False), nullable=True
    )
    cylinder_capacity: Mapped[str | None] = mapped_column(String(25), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policies: Mapped[list[Policy]] = relationship(back_populates="vehicle")
    endorsements_as_previous: Mapped[list[Endorsement]] = relationship(
        back_populates="previous_vehicle",
        foreign_keys="[Endorsement.previous_vehicle_id]",
    )


class Coverage(Base):
    __tablename__ = "coverage"
    __table_args__ = (
        CheckConstraint(
            "credit_price >= 0 AND initial_payment >= 0 AND cash_price >= 0",
            name="chk_coverage_prices",
        ),
        CheckConstraint(
            "tow_services_included >= 0",
            name="chk_coverage_tow",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_key: Mapped[int] = mapped_column(Integer, nullable=False)
    service_type: Mapped[ServiceType] = mapped_column(
        Enum(ServiceType, name="service_type", create_type=False), nullable=False
    )
    category: Mapped[CoverageCategoryType] = mapped_column(
        Enum(CoverageCategoryType, name="coverage_category_type", create_type=False),
        nullable=False,
        server_default="liability",
    )
    cylinder_capacity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    credit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    initial_payment: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    cash_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tow_services_included: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policies: Mapped[list[Policy]] = relationship(back_populates="coverage")
    commission_rates: Mapped[list[CommissionRate]] = relationship(back_populates="coverage")


class Policy(Base):
    __tablename__ = "policy"
    __table_args__ = (
        UniqueConstraint("folio", name="uq_policy_folio"),
        CheckConstraint(
            "expiration_date IS NULL OR effective_date IS NULL OR expiration_date >= effective_date",
            name="chk_policy_dates",
        ),
        CheckConstraint(
            "tow_services_available >= 0",
            name="chk_policy_tow",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    folio: Mapped[int] = mapped_column(Integer, nullable=False)
    renewal_folio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    client_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("client.id", ondelete="RESTRICT"), nullable=False
    )
    vehicle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("vehicle.id", ondelete="RESTRICT"), nullable=False
    )
    coverage_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("coverage.id", ondelete="RESTRICT"), nullable=False
    )
    seller_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("employee.id", ondelete="SET NULL"), nullable=True
    )
    service_type: Mapped[ServiceType | None] = mapped_column(
        Enum(ServiceType, name="service_type", create_type=False), nullable=True
    )
    contract_folio: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sale_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    elaboration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[PolicyStatusType] = mapped_column(
        Enum(PolicyStatusType, name="policy_status_type", create_type=False),
        nullable=False,
        server_default="active",
    )
    payment_plan: Mapped[PaymentPlanType | None] = mapped_column(
        Enum(PaymentPlanType, name="payment_plan_type", create_type=False), nullable=True
    )
    data_entry_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("app_user.id"), nullable=True
    )
    tow_services_available: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    has_fraud_observation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    has_payment_issues: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    contract_image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    prima_total: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    quote_external_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    client: Mapped[Client] = relationship(back_populates="policies")
    vehicle: Mapped[Vehicle] = relationship(back_populates="policies")
    coverage: Mapped[Coverage] = relationship(back_populates="policies")
    seller: Mapped[Employee | None] = relationship(back_populates="policies")
    data_entry_user: Mapped[AppUser | None] = relationship(
        back_populates="data_entry_policies",
        foreign_keys=[data_entry_user_id],
    )
    payments: Mapped[list[Payment]] = relationship(back_populates="policy")
    payment_proposals: Mapped[list[PaymentProposal]] = relationship(
        back_populates="policy", foreign_keys="[PaymentProposal.policy_id]"
    )
    receipts: Mapped[list[Receipt]] = relationship(back_populates="policy")
    cards: Mapped[list[Card]] = relationship(back_populates="policy")
    collection_assignments: Mapped[list[CollectionAssignment]] = relationship(
        back_populates="policy"
    )
    visit_notices: Mapped[list[VisitNotice]] = relationship(back_populates="policy")
    cancellations: Mapped[list[Cancellation]] = relationship(back_populates="policy")
    incidents: Mapped[list[Incident]] = relationship(back_populates="policy")
    tow_services: Mapped[list[TowService]] = relationship(back_populates="policy")
    endorsements: Mapped[list[Endorsement]] = relationship(back_populates="policy")
    renewals_as_old: Mapped[list[Renewal]] = relationship(
        back_populates="old_policy",
        foreign_keys="[Renewal.old_policy_id]",
    )
    renewals_as_new: Mapped[list[Renewal]] = relationship(
        back_populates="new_policy",
        foreign_keys="[Renewal.new_policy_id]",
    )
    amplia_detail: Mapped[PolicyAmpliaDetail | None] = relationship(
        back_populates="policy", uselist=False, cascade="all, delete-orphan"
    )
    sent_messages: Mapped[list[SentMessage]] = relationship(back_populates="policy")
    policy_notifications: Mapped[list[PolicyNotification]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    renewal_notification_logs: Mapped[list[RenewalNotificationLog]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
    promotion_applications: Mapped[list[PromotionApplication]] = relationship(
        back_populates="policy",
        foreign_keys="[PromotionApplication.policy_id]",
    )
    referrer_promotion_applications: Mapped[list[PromotionApplication]] = relationship(
        back_populates="referrer_policy",
        foreign_keys="[PromotionApplication.referrer_policy_id]",
    )


class PolicyAmpliaDetail(Base):
    __tablename__ = "policy_amplia_detail"
    __table_args__ = (
        UniqueConstraint("policy_id", name="uq_amplia_policy"),
        CheckConstraint(
            "commercial_value >= 0 AND damage_deductible >= 0 AND theft_deductible >= 0",
            name="chk_amplia_values",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("policy.id", ondelete="CASCADE"), nullable=False
    )
    quote_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    coverage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    commercial_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    damage_deductible: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    theft_deductible: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    civil_liability_deductible: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    eligible_no_responsible_incidents: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    eligible_no_fraud_observations: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    eligible_no_payment_issues: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    eligible_renewal_period_met: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    eligibility_last_checked: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    eligibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    policy: Mapped[Policy] = relationship(back_populates="amplia_detail")
