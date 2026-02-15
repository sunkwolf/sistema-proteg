"""Pydantic schemas for the Tow Services module."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ── Tow Service ─────────────────────────────────────────────────────

class TowServiceCreate(BaseModel):
    policy_id: int
    requester_name: str = Field(max_length=100)
    phone: str | None = Field(None, max_length=20)
    vehicle_failure: str = Field(max_length=100)
    load_weight: int | None = None
    tow_provider_id: int | None = None
    tow_cost: Decimal | None = Field(None, ge=0)
    extra_charge: Decimal | None = Field(None, ge=0)
    comments: str | None = None


class TowServiceUpdate(BaseModel):
    requester_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    vehicle_failure: str | None = Field(None, max_length=100)
    load_weight: int | None = None
    tow_provider_id: int | None = None
    tow_cost: Decimal | None = Field(None, ge=0)
    extra_charge: Decimal | None = Field(None, ge=0)
    estimated_arrival_time: datetime | None = None
    contact_time: datetime | None = None
    end_time: datetime | None = None
    service_status: str | None = None
    comments: str | None = None


class TowServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int | None
    report_number: str
    requester_name: str
    phone: str | None
    origin_address_id: int | None
    destination_address_id: int | None
    vehicle_failure: str
    load_weight: int | None
    tow_provider_id: int | None
    tow_cost: Decimal | None
    extra_charge: Decimal | None
    estimated_arrival_time: datetime | None
    report_time: datetime
    attended_by_user_id: int | None
    contact_time: datetime | None
    end_time: datetime | None
    comments: str | None
    service_status: str
    satisfaction_rating: int | None
    created_at: datetime
    updated_at: datetime


class TowServiceListResponse(BaseModel):
    items: list[TowServiceResponse]
    total: int
    skip: int
    limit: int


# ── Tow Provider ───────────────────────────────────────────────────

class TowProviderCreate(BaseModel):
    name: str = Field(max_length=255)
    phone: str | None = Field(None, max_length=20)
    telegram_group_id: int | None = None
    contact_person: str | None = Field(None, max_length=100)
    notes: str | None = None


class TowProviderUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=20)
    telegram_group_id: int | None = None
    contact_person: str | None = Field(None, max_length=100)
    notes: str | None = None
    status: str | None = None


class TowProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str | None
    telegram_group_id: int | None
    contact_person: str | None
    address_id: int | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class TowProviderListResponse(BaseModel):
    items: list[TowProviderResponse]
    total: int


# ── Satisfaction Survey ─────────────────────────────────────────────

class TowSurveyCreate(BaseModel):
    response_time_rating: int = Field(ge=1, le=10)
    service_rating: int = Field(ge=1, le=10)
    overall_service_rating: int = Field(ge=1, le=10)
    company_impression: int = Field(ge=1, le=10)
    comments: str | None = None


class TowSurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tow_service_id: int
    survey_date: datetime
    response_time_rating: int
    service_rating: int
    overall_service_rating: int
    company_impression: int
    comments: str | None
    average_rating: Decimal
    surveyed_by_user_id: int | None
    created_at: datetime
