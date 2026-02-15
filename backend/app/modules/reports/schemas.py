"""Pydantic schemas for the Reports module."""

from datetime import date

from pydantic import BaseModel, Field


class ReportFilters(BaseModel):
    """Common filters for report generation."""
    date_from: date | None = None
    date_to: date | None = None
    month: str | None = Field(None, pattern=r"^\d{4}-\d{2}$")
    seller_id: int | None = None
    collector_id: int | None = None
