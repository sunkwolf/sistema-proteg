"""Pydantic schemas for the Quotations integration module."""

from decimal import Decimal

from pydantic import BaseModel, Field


class QuoteValidateRequest(BaseModel):
    quote_number: str = Field(max_length=50)


class QuoteDeductibles(BaseModel):
    damage: Decimal
    theft: Decimal


class QuoteDetail(BaseModel):
    quote_number: str
    brand: str
    model_type: str
    model_year: str
    purchase_price: Decimal
    sale_price: Decimal
    commercial_value: Decimal
    deductibles: QuoteDeductibles


class QuoteValidateResponse(BaseModel):
    valid: bool
    quote: QuoteDetail | None = None


class QuoteApproveRequest(BaseModel):
    quote_number: str = Field(max_length=50)


class QuoteApproveResponse(BaseModel):
    success: bool
    quote_number: str
    status: str
