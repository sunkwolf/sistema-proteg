"""Pydantic schemas for the Clients module."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


# ── Address schemas ──────────────────────────────────────────────────


class AddressInput(BaseModel):
    street: str = Field(..., min_length=1, max_length=150)
    exterior_number: str | None = Field(None, max_length=10)
    interior_number: str | None = Field(None, max_length=10)
    cross_street_1: str | None = Field(None, max_length=100)
    cross_street_2: str | None = Field(None, max_length=100)
    neighborhood: str | None = Field(None, max_length=100)
    municipality_id: int | None = None
    postal_code: str | None = Field(None, max_length=10)
    latitude: float | None = None
    longitude: float | None = None


class MunicipalityInfo(BaseModel):
    id: int
    name: str


class AddressResponse(BaseModel):
    id: int
    street: str
    exterior_number: str | None = None
    interior_number: str | None = None
    cross_street_1: str | None = None
    cross_street_2: str | None = None
    neighborhood: str | None = None
    municipality: MunicipalityInfo | None = None
    postal_code: str | None = None


# ── Client schemas ───────────────────────────────────────────────────

_RFC_RE = re.compile(r"^[A-Z0-9]{12,13}$")


def _validate_phone(v: str | None) -> str | None:
    if v is None or v == "":
        return None
    digits = "".join(c for c in v if c.isdigit())
    if len(digits) != 10:
        raise ValueError("El telefono debe tener 10 digitos")
    return digits


class ClientCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    paternal_surname: str = Field(..., min_length=1, max_length=50)
    maternal_surname: str | None = Field(None, max_length=50)
    rfc: str | None = Field(None, max_length=13)
    birth_date: date | None = None
    gender: Literal["male", "female"] | None = None
    marital_status: Literal[
        "single", "married", "divorced", "widowed", "common_law"
    ] | None = None
    whatsapp: str = Field(..., max_length=20)
    phone_additional: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=100)
    address: AddressInput | None = None

    @field_validator("rfc")
    @classmethod
    def validate_rfc(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        v = v.strip().upper()
        if not _RFC_RE.match(v):
            raise ValueError(
                "RFC debe ser 12 o 13 caracteres alfanumericos, mayusculas, sin guiones"
            )
        return v

    @field_validator("whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str) -> str:
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError("WhatsApp debe tener 10 digitos")
        return digits

    @field_validator("phone_additional")
    @classmethod
    def validate_phone_additional(cls, v: str | None) -> str | None:
        return _validate_phone(v)

    @field_validator("maternal_surname", "email")
    @classmethod
    def empty_to_none(cls, v: str | None) -> str | None:
        if v == "":
            return None
        return v


class ClientUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=50)
    paternal_surname: str | None = Field(None, min_length=1, max_length=50)
    maternal_surname: str | None = Field(None, max_length=50)
    rfc: str | None = Field(None, max_length=13)
    birth_date: date | None = None
    gender: Literal["male", "female"] | None = None
    marital_status: Literal[
        "single", "married", "divorced", "widowed", "common_law"
    ] | None = None
    whatsapp: str | None = Field(None, max_length=20)
    phone_additional: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=100)
    address: AddressInput | None = None

    @field_validator("rfc")
    @classmethod
    def validate_rfc(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        v = v.strip().upper()
        if not _RFC_RE.match(v):
            raise ValueError(
                "RFC debe ser 12 o 13 caracteres alfanumericos, mayusculas, sin guiones"
            )
        return v

    @field_validator("whatsapp")
    @classmethod
    def validate_whatsapp(cls, v: str | None) -> str | None:
        return _validate_phone(v)

    @field_validator("phone_additional")
    @classmethod
    def validate_phone_additional(cls, v: str | None) -> str | None:
        return _validate_phone(v)


# ── Response schemas ─────────────────────────────────────────────────


class ClientResponse(BaseModel):
    id: int
    first_name: str
    paternal_surname: str
    maternal_surname: str | None = None
    rfc: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    whatsapp: str | None = None
    phone_additional: str | None = None
    email: str | None = None
    address: AddressResponse | None = None
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseModel):
    items: list[ClientResponse]
    total: int
    skip: int
    limit: int


# ── Similarity search ────────────────────────────────────────────────


class ClientSearchResult(ClientResponse):
    """Client result from pg_trgm similarity search."""
    pass


# ── Nearby search ────────────────────────────────────────────────────


class NearbyClientResult(BaseModel):
    client: ClientResponse
    distance_meters: float


# ── WhatsApp verification ────────────────────────────────────────────


class WhatsAppVerifyResponse(BaseModel):
    phone: str
    is_whatsapp: bool
    verified: bool
