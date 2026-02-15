"""Telegram Bot API client for alerts."""

from __future__ import annotations

import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_telegram_message(
    chat_id: str, text: str, parse_mode: str = "HTML"
) -> dict | None:
    """Send a message via Telegram Bot API.

    Returns the API response dict on success, None on failure.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("Telegram not configured (TELEGRAM_BOT_TOKEN)")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
        if resp.status_code == 200:
            data = resp.json()
            logger.info("Telegram sent to chat %s", chat_id)
            return data.get("result")
        logger.error("Telegram API error %s: %s", resp.status_code, resp.text[:200])
        return None
    except httpx.HTTPError as exc:
        logger.error("Telegram send failed: %s", exc)
        return None
