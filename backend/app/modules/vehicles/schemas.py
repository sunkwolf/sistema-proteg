"""Pydantic schemas for the Vehicles module."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# Valid vehicle keys and their corresponding types
VEHICLE_KEY_TYPE_MAP: dict[int, str] = {
    101: "automobile",
    103: "truck",
    105: "suv",
    107: "motorcycle",
    108: "mototaxi",
    109: "truck",  # CAMION
}
VALID_VEHICLE_KEYS = set(VEHICLE_KEY_TYPE_MAP.keys())


class VehicleCreate(BaseModel):
    brand: str = Field(..., min_length=1, max_length=45)
    model_type: str | None = Field(None, max_length=45)
    model_year: str | None = Field(None, max_length=10)
    color: str | None = Field(None, max_length=45)
    vehicle_key: int | None = None
    vehicle_type: Literal[
        "automobile", "truck", "suv", "motorcycle", "mototaxi"
    ] | None = None
    serial_number: str | None = Field(None, max_length=45)
    plates: str | None = Field(None, max_length=20)
    seats: int | None = None
    load_capacity: str | None = Field(None, max_length=15)
    cylinder_capacity: str | None = Field(None, max_length=25)

    @model_validator(mode="after")
    def validate_vehicle_key_and_type(self) -> VehicleCreate:
        if self.vehicle_key is not None:
            if self.vehicle_key not in VALID_VEHICLE_KEYS:
                raise ValueError(
                    f"vehicle_key debe ser uno de: {sorted(VALID_VEHICLE_KEYS)}"
                )
            expected_type = VEHICLE_KEY_TYPE_MAP[self.vehicle_key]
            if self.vehicle_type is None:
                self.vehicle_type = expected_type
            elif self.vehicle_type != expected_type:
                raise ValueError(
                    f"vehicle_key {self.vehicle_key} requiere vehicle_type='{expected_type}', "
                    f"se recibio '{self.vehicle_type}'"
                )
        return self

    @model_validator(mode="after")
    def cylinder_required_for_motos(self) -> VehicleCreate:
        if self.vehicle_type in ("motorcycle", "mototaxi"):
            if not self.cylinder_capacity:
                raise ValueError(
                    "cylinder_capacity es obligatorio para motocicletas y mototaxis"
                )
        return self


class VehicleUpdate(BaseModel):
    brand: str | None = Field(None, min_length=1, max_length=45)
    model_type: str | None = Field(None, max_length=45)
    model_year: str | None = Field(None, max_length=10)
    color: str | None = Field(None, max_length=45)
    vehicle_key: int | None = None
    vehicle_type: Literal[
        "automobile", "truck", "suv", "motorcycle", "mototaxi"
    ] | None = None
    serial_number: str | None = Field(None, max_length=45)
    plates: str | None = Field(None, max_length=20)
    seats: int | None = None
    load_capacity: str | None = Field(None, max_length=15)
    cylinder_capacity: str | None = Field(None, max_length=25)


class VehicleResponse(BaseModel):
    id: int
    brand: str
    model_type: str | None = None
    model_year: str | None = None
    color: str | None = None
    vehicle_key: int | None = None
    vehicle_type: str | None = None
    serial_number: str | None = None
    plates: str | None = None
    seats: int | None = None
    load_capacity: str | None = None
    cylinder_capacity: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    skip: int
    limit: int
