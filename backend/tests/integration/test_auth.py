"""Integration tests for auth endpoints."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.core.config import get_settings

settings = get_settings()
PREFIX = settings.API_V1_PREFIX


class TestLoginEndpoint:
    """Test POST /auth/login."""

    async def test_login_missing_body_returns_422(self, client: AsyncClient):
        resp = await client.post(f"{PREFIX}/auth/login")
        assert resp.status_code == 422

    async def test_login_empty_credentials_returns_422(self, client: AsyncClient):
        resp = await client.post(
            f"{PREFIX}/auth/login",
            json={"username": "", "password": ""},
        )
        assert resp.status_code == 422

    async def test_login_invalid_credentials_returns_401(
        self, client: AsyncClient, mock_db, mock_redis
    ):
        # Mock: user not found
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        resp = await client.post(
            f"{PREFIX}/auth/login",
            json={"username": "noexiste", "password": "wrong"},
        )
        assert resp.status_code == 401
        assert "Credenciales invalidas" in resp.json()["detail"]

    async def test_login_locked_account_returns_423(
        self, client: AsyncClient, mock_redis
    ):
        # Mock: account is locked
        mock_redis.exists = AsyncMock(return_value=True)

        resp = await client.post(
            f"{PREFIX}/auth/login",
            json={"username": "locked_user", "password": "test"},
        )
        assert resp.status_code == 423
        assert "bloqueada" in resp.json()["detail"].lower()

    async def test_login_rate_limited_returns_429(
        self, client: AsyncClient, mock_redis
    ):
        # Mock: no lockout but rate-limited (5+ attempts)
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.get = AsyncMock(return_value=b"6")

        resp = await client.post(
            f"{PREFIX}/auth/login",
            json={"username": "ratelimited", "password": "test"},
        )
        assert resp.status_code == 429


class TestLogoutEndpoint:
    """Test POST /auth/logout."""

    async def test_logout_without_cookie_returns_204(self, client: AsyncClient):
        resp = await client.post(f"{PREFIX}/auth/logout")
        assert resp.status_code == 204


class TestMeEndpoint:
    """Test GET /auth/me."""

    async def test_me_without_token_returns_401(self, client: AsyncClient):
        resp = await client.get(f"{PREFIX}/auth/me")
        # HTTPBearer(auto_error=True) returns 401 when no token provided
        assert resp.status_code in (401, 403)

    async def test_me_with_invalid_token_returns_401(self, client: AsyncClient):
        resp = await client.get(
            f"{PREFIX}/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert resp.status_code == 401


class TestRefreshEndpoint:
    """Test POST /auth/refresh."""

    async def test_refresh_without_cookie_returns_401(self, client: AsyncClient):
        resp = await client.post(f"{PREFIX}/auth/refresh")
        assert resp.status_code == 401
        assert "no encontrado" in resp.json()["detail"].lower()

    async def test_refresh_with_invalid_token_returns_401(
        self, client: AsyncClient, mock_redis
    ):
        # Mock: token not found in Redis
        mock_redis.get = AsyncMock(return_value=None)

        # Set cookie on client directly to avoid deprecation warning
        client.cookies.set("refresh_token", "invalid-token-value")
        resp = await client.post(f"{PREFIX}/auth/refresh")
        assert resp.status_code == 401
