"""Evolution API client for WhatsApp messaging."""

from __future__ import annotations

import logging
import re

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def normalize_phone(number: str) -> str | None:
    """Normalize a Mexican phone number to WhatsApp format (521XXXXXXXXXX)."""
    digits = re.sub(r"\D", "", number)
    if len(digits) == 10:
        return "521" + digits
    if len(digits) == 13 and digits.startswith("521"):
        return digits
    return None


async def send_whatsapp_text(phone: str, text: str) -> dict | None:
    """Send a text message via Evolution API.

    Returns the API response dict on success, None on failure.
    """
    base_url = settings.EVOLUTION_API_URL.rstrip("/")
    if not base_url or not settings.EVOLUTION_API_KEY:
        logger.warning("WhatsApp not configured (EVOLUTION_API_URL / EVOLUTION_API_KEY)")
        return None

    url = f"{base_url}/message/sendText"
    payload = {
        "number": phone,
        "text": text,
    }
    headers = {
        "apikey": settings.EVOLUTION_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code < 300:
            data = resp.json()
            logger.info("WhatsApp sent to %s", phone)
            return data
        logger.error("WhatsApp API error %s: %s", resp.status_code, resp.text[:200])
        return None
    except httpx.HTTPError as exc:
        logger.error("WhatsApp send failed: %s", exc)
        return None
