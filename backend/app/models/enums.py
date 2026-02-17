"""
PostgreSQL ENUM types as Python enums.

All 31 ENUM types from schema.sql v2.1, mapped 1:1.
"""

import enum


class GenderType(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class MaritalStatusType(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    COMMON_LAW = "common_law"


class EntityStatusType(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PolicyStatusType(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    MOROSA = "morosa"
    PRE_EFFECTIVE = "pre_effective"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"
    NO_STATUS = "no_status"


class PaymentStatusType(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    LATE = "late"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethodType(str, enum.Enum):
    CASH = "cash"
    DEPOSIT = "deposit"
    TRANSFER = "transfer"
    CRUCERO = "crucero"
    KONFIO = "konfio"
    TERMINAL_BANORTE = "terminal_banorte"


class PaymentPlanType(str, enum.Enum):
    CASH = "cash"
    CASH_2_INSTALLMENTS = "cash_2_installments"
    MONTHLY_7 = "monthly_7"
    QUARTERLY_4 = "quarterly_4"
    SEMIANNUAL_2 = "semiannual_2"
    MONTHLY_12 = "monthly_12"


class PreapprovalStatusType(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class OfficeDeliveryType(str, enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"


class ReceiptStatusType(str, enum.Enum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    USED = "used"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    LOST = "lost"
    CANCELLED_UNDELIVERED = "cancelled_undelivered"


class ServiceType(str, enum.Enum):
    PRIVATE = "private"
    COMMERCIAL = "commercial"


class VehicleTypeEnum(str, enum.Enum):
    AUTOMOBILE = "automobile"
    TRUCK = "truck"
    SUV = "suv"
    MOTORCYCLE = "motorcycle"
    MOTOTAXI = "mototaxi"


class CoverageCategoryType(str, enum.Enum):
    LIABILITY = "liability"
    COMPREHENSIVE = "comprehensive"
    PLATFORM = "platform"


class IncidentTypeEnum(str, enum.Enum):
    COLLISION = "collision"
    THEFT = "theft"
    TOTAL_LOSS = "total_loss"
    VANDALISM = "vandalism"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class ResponsibilityType(str, enum.Enum):
    NOT_RESPONSIBLE = "not_responsible"
    AT_FAULT = "at_fault"
    SHARED = "shared"


class ServiceStatusType(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EndorsementTypeEnum(str, enum.Enum):
    PLATE_CHANGE = "plate_change"
    VEHICLE_CHANGE = "vehicle_change"
    COVERAGE_CHANGE = "coverage_change"
    CONTRACTOR_CHANGE = "contractor_change"
    RIGHTS_TRANSFER = "rights_transfer"


class EndorsementStatusType(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"


class ShiftOrderType(str, enum.Enum):
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    REST = "rest"


class MessageTypeEnum(str, enum.Enum):
    REMINDER = "reminder"
    OVERDUE = "overdue"


class NotificationPeriodType(str, enum.Enum):
    RENEWAL_15D = "renewal_15d"
    RENEWAL_3D = "renewal_3d"
    EXPIRED_7D = "expired_7d"
    EXPIRED_30D = "expired_30d"


class SellerClassType(str, enum.Enum):
    SELLER = "seller"
    COLLABORATOR = "collaborator"


class WorkshopPassTypeEnum(str, enum.Enum):
    REPAIR = "repair"
    VALUATION_PAYMENT = "valuation_payment"
    OPEN_REPAIR_VALUATION = "open_repair_valuation"
    AGREED_PAYMENT = "agreed_payment"
    AGREEMENT = "agreement"


class RenewalStatusType(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class PaymentProposalStatusType(str, enum.Enum):
    ACTIVE = "active"
    APPLIED = "applied"
    DISCARDED = "discarded"


class CardStatusType(str, enum.Enum):
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    CANCELLED = "cancelled"
    RECOVERY = "recovery"


class MessageChannelType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    SMS = "sms"
    EMAIL = "email"


class MessageDeliveryStatusType(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class PromotionDiscountType(str, enum.Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_MONTHS = "free_months"
    ZERO_DOWN_PAYMENT = "zero_down_payment"


class ApprovalRequestType(str, enum.Enum):
    POLICY_SUBMISSION = "policy_submission"
    PAYMENT_SUBMISSION = "payment_submission"


class ApprovalStatusType(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DeviceTypeEnum(str, enum.Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class AppTypeEnum(str, enum.Enum):
    COLLECTOR_APP = "collector_app"
    SELLER_APP = "seller_app"
    ADJUSTER_APP = "adjuster_app"
    DESKTOP = "desktop"
