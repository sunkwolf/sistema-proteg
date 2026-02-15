"""Proxy service for the external quotations API."""

from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.modules.quotations.schemas import (
    QuoteApproveResponse,
    QuoteValidateResponse,
)

settings = get_settings()


class QuotationService:
    """Proxies requests to the external quotation system at cotizaciones.protegrt.com."""

    def __init__(self) -> None:
        self.base_url = settings.QUOTATIONS_API_URL.rstrip("/")
        self.api_key = settings.QUOTATIONS_API_KEY
        self.timeout = settings.QUOTATIONS_API_TIMEOUT

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def validate_quote(self, quote_number: str) -> QuoteValidateResponse:
        """Validate a quote by calling the external API."""
        url = f"{self.base_url}/quotes/validate/{quote_number}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self._headers())
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Quotation service timed out",
            )
        except httpx.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Quotation service unavailable",
            )

        if resp.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found in external system",
            )
        if resp.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Quotation service returned an error",
            )

        data = resp.json()
        return QuoteValidateResponse(**data)

    async def approve_quote(self, quote_number: str) -> QuoteApproveResponse:
        """Approve a quote in the external system."""
        url = f"{self.base_url}/quotes/by-number/{quote_number}/approve"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, headers=self._headers())
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Quotation service timed out",
            )
        except httpx.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Quotation service unavailable",
            )

        if resp.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found in external system",
            )
        if resp.status_code == 409:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Quote already approved",
            )
        if resp.status_code >= 400:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Quotation service returned an error",
            )

        data = resp.json()
        return QuoteApproveResponse(**data)
