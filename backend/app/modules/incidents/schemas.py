"""Pydantic schemas for the Incidents module."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ── Incident ────────────────────────────────────────────────────────

class IncidentCreate(BaseModel):
    policy_id: int
    requester_name: str = Field(max_length=100)
    phone: str | None = Field(None, max_length=20)
    incident_type: str | None = None
    description: str | None = None
    responsibility: str | None = None
    client_misconduct: bool = False
    adjuster_id: int
    comments: str | None = None


class IncidentUpdate(BaseModel):
    requester_name: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    incident_type: str | None = None
    description: str | None = None
    responsibility: str | None = None
    client_misconduct: bool | None = None
    adjuster_id: int | None = None
    service_status: str | None = None
    contact_time: datetime | None = None
    completion_time: datetime | None = None
    comments: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int | None
    report_number: str
    requester_name: str
    phone: str | None
    origin_address_id: int | None
    incident_type: str | None
    description: str | None
    responsibility: str | None
    client_misconduct: bool
    adjuster_id: int
    report_time: datetime
    contact_time: datetime | None
    completion_time: datetime | None
    attended_by_user_id: int | None
    service_status: str
    satisfaction_rating: int | None
    comments: str | None
    created_at: datetime
    updated_at: datetime


class IncidentListResponse(BaseModel):
    items: list[IncidentResponse]
    total: int
    skip: int
    limit: int


# ── Medical Pass ────────────────────────────────────────────────────

class MedicalPassCreate(BaseModel):
    hospital_id: int
    pass_number: str = Field(max_length=50)
    beneficiary_name: str | None = Field(None, max_length=100)
    injuries: str | None = None
    observations: str | None = None
    cost: Decimal | None = Field(None, ge=0)


class MedicalPassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    hospital_id: int
    pass_number: str
    beneficiary_name: str | None
    injuries: str | None
    observations: str | None
    cost: Decimal | None
    status: str
    created_at: datetime


# ── Workshop Pass ───────────────────────────────────────────────────

class WorkshopPassCreate(BaseModel):
    workshop_id: int
    pass_number: str = Field(max_length=50)
    beneficiary_name: str | None = Field(None, max_length=100)
    pass_type: str
    vehicle_damages: str | None = None
    observations: str | None = None
    cost: Decimal | None = Field(None, ge=0)


class WorkshopPassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    workshop_id: int
    pass_number: str
    beneficiary_name: str | None
    pass_type: str
    vehicle_damages: str | None
    observations: str | None
    cost: Decimal | None
    status: str
    created_at: datetime


# ── Satisfaction Survey ─────────────────────────────────────────────

class SurveyCreate(BaseModel):
    response_time_rating: int = Field(ge=1, le=10)
    service_rating: int = Field(ge=1, le=10)
    overall_service_rating: int = Field(ge=1, le=10)
    company_impression: int = Field(ge=1, le=10)
    comments: str | None = None


class SurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    survey_date: datetime
    response_time_rating: int
    service_rating: int
    overall_service_rating: int
    company_impression: int
    comments: str | None
    average_rating: Decimal
    surveyed_by_user_id: int | None
    created_at: datetime


# ── Adjuster Shift ──────────────────────────────────────────────────

class AdjusterShiftCreate(BaseModel):
    shift_date: date
    adjuster_id: int
    shift_order: str


class AdjusterShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shift_date: date
    adjuster_id: int
    shift_order: str
    created_at: datetime


class AdjusterShiftListResponse(BaseModel):
    items: list[AdjusterShiftResponse]
    total: int
