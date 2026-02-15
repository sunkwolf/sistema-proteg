"""
SQLAlchemy models for CRM Protegrt.

Import all models here so Alembic's Base.metadata can discover them.
"""

from app.models.base import Base

# Enums
from app.models.enums import (
    ApprovalRequestType,
    ApprovalStatusType,
    AppTypeEnum,
    CardStatusType,
    CoverageCategoryType,
    DeviceTypeEnum,
    EndorsementStatusType,
    EndorsementTypeEnum,
    EntityStatusType,
    GenderType,
    IncidentTypeEnum,
    MaritalStatusType,
    MessageChannelType,
    MessageDeliveryStatusType,
    MessageTypeEnum,
    NotificationPeriodType,
    OfficeDeliveryType,
    PaymentMethodType,
    PaymentPlanType,
    PaymentProposalStatusType,
    PaymentStatusType,
    PolicyStatusType,
    PromotionDiscountType,
    ReceiptStatusType,
    RenewalStatusType,
    ResponsibilityType,
    SellerClassType,
    ServiceStatusType,
    ServiceType,
    ShiftOrderType,
    VehicleTypeEnum,
    WorkshopPassTypeEnum,
)

# Catalog
from app.models.catalog import Address, Municipality

# Auth
from app.models.auth import AppUser, Department, DeviceSession, Permission, Role, RolePermission, Session

# Business
from app.models.business import Client, Collector, Coverage, Policy, PolicyAmpliaDetail, Seller, Vehicle

# Payments
from app.models.payments import Payment, PaymentProposal, Receipt, ReceiptLossSchedule

# Collections
from app.models.collections import Card, CollectionAssignment, VisitNotice

# Incidents
from app.models.incidents import (
    Adjuster,
    AdjusterShift,
    Hospital,
    Incident,
    IncidentSatisfactionSurvey,
    MedicalPass,
    TowProvider,
    TowService,
    TowSatisfactionSurvey,
    Workshop,
    WorkshopPass,
)

# Endorsements
from app.models.endorsements import Endorsement, Renewal

# Promotions
from app.models.promotions import CommissionRate, Promotion, PromotionApplication, PromotionRule

# Notifications
from app.models.notifications import PolicyNotification, RenewalNotificationLog, SentMessage

# Audit
from app.models.audit import (
    ApprovalRequest,
    AuditLog,
    Cancellation,
    ExecutionLog,
    MobileActionLog,
    ReportNumberSequence,
)

__all__ = [
    "Base",
    # Catalog
    "Municipality",
    "Address",
    # Auth
    "Department",
    "Role",
    "Permission",
    "RolePermission",
    "AppUser",
    "Session",
    "DeviceSession",
    # Business
    "Client",
    "Seller",
    "Collector",
    "Vehicle",
    "Coverage",
    "Policy",
    "PolicyAmpliaDetail",
    # Payments
    "Payment",
    "PaymentProposal",
    "Receipt",
    "ReceiptLossSchedule",
    # Collections
    "Card",
    "CollectionAssignment",
    "VisitNotice",
    # Incidents
    "Adjuster",
    "AdjusterShift",
    "Incident",
    "Hospital",
    "MedicalPass",
    "Workshop",
    "WorkshopPass",
    "TowProvider",
    "TowService",
    "IncidentSatisfactionSurvey",
    "TowSatisfactionSurvey",
    # Endorsements
    "Endorsement",
    "Renewal",
    # Promotions
    "Promotion",
    "PromotionRule",
    "PromotionApplication",
    "CommissionRate",
    # Notifications
    "SentMessage",
    "PolicyNotification",
    "RenewalNotificationLog",
    # Audit
    "ExecutionLog",
    "AuditLog",
    "ApprovalRequest",
    "MobileActionLog",
    "Cancellation",
    "ReportNumberSequence",
]
