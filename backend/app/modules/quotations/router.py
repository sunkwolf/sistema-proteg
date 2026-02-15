"""Quotation proxy endpoints — validate and approve external quotes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import require_permission
from app.modules.quotations.schemas import (
    QuoteApproveRequest,
    QuoteApproveResponse,
    QuoteValidateRequest,
    QuoteValidateResponse,
)
from app.modules.quotations.service import QuotationService

router = APIRouter()


@router.post("/validate", response_model=QuoteValidateResponse)
async def validate_quote(
    data: QuoteValidateRequest,
    _perm: Annotated[None, require_permission("policies.create")],
):
    """Validate a quote number against the external quotation system."""
    service = QuotationService()
    return await service.validate_quote(data.quote_number)


@router.post("/approve", response_model=QuoteApproveResponse)
async def approve_quote(
    data: QuoteApproveRequest,
    _perm: Annotated[None, require_permission("policies.create")],
):
    """Approve a quote in the external quotation system."""
    service = QuotationService()
    return await service.approve_quote(data.quote_number)
