"""Pydantic schemas for the Endorsements module."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EndorsementCreate(BaseModel):
    policy_id: int
    endorsement_type: str
    change_details: dict[str, Any]
    comments: str | None = None
    new_contractor_id: int | None = None
    previous_vehicle_id: int | None = None


class EndorsementUpdate(BaseModel):
    change_details: dict[str, Any] | None = None
    comments: str | None = None
    new_contractor_id: int | None = None
    previous_vehicle_id: int | None = None


class EndorsementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    policy_id: int
    endorsement_type: str
    request_date: datetime
    application_date: datetime | None
    status: str
    change_details: dict[str, Any]
    comments: str | None
    new_contractor_id: int | None
    previous_vehicle_id: int | None
    created_at: datetime
    updated_at: datetime


class EndorsementListResponse(BaseModel):
    items: list[EndorsementResponse]
    total: int
    skip: int
    limit: int


class CostCalculationResponse(BaseModel):
    endorsement_id: int
    endorsement_type: str
    calculated_cost: str
    calculation_details: dict[str, Any]
