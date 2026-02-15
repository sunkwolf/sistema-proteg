"""Unit tests for the security module (hashing, JWT)."""

import os
import tempfile
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from jose import jwt

from app.core.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    needs_rehash,
    verify_password,
)


# ── Password hashing ────────────────────────────────────────────────


class TestPasswordHashing:
    def test_hash_password_returns_argon2_hash(self):
        hashed = hash_password("test_password_123")
        assert hashed.startswith("$argon2id$")

    def test_verify_password_correct(self):
        password = "secure_password_456"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty_string(self):
        hashed = hash_password("some_password")
        assert verify_password("", hashed) is False

    def test_different_passwords_produce_different_hashes(self):
        h1 = hash_password("password_one")
        h2 = hash_password("password_two")
        assert h1 != h2

    def test_same_password_produces_different_hashes(self):
        """Salting should ensure different hashes for same password."""
        h1 = hash_password("same_password")
        h2 = hash_password("same_password")
        assert h1 != h2

    def test_needs_rehash_fresh_hash(self):
        hashed = hash_password("fresh_password")
        assert needs_rehash(hashed) is False


# ── Refresh token generation ────────────────────────────────────────


class TestRefreshToken:
    def test_generate_refresh_token_returns_tuple(self):
        token, token_hash = generate_refresh_token()
        assert isinstance(token, str)
        assert isinstance(token_hash, str)

    def test_generate_refresh_token_uuid_format(self):
        token, _ = generate_refresh_token()
        # UUID format: 8-4-4-4-12
        parts = token.split("-")
        assert len(parts) == 5

    def test_generate_refresh_token_hash_is_sha256(self):
        _, token_hash = generate_refresh_token()
        assert len(token_hash) == 64  # SHA-256 hex length

    def test_hash_refresh_token_deterministic(self):
        token = "test-token-value"
        h1 = hash_refresh_token(token)
        h2 = hash_refresh_token(token)
        assert h1 == h2

    def test_different_tokens_different_hashes(self):
        t1, h1 = generate_refresh_token()
        t2, h2 = generate_refresh_token()
        assert t1 != t2
        assert h1 != h2


# ── JWT creation/decoding ────────────────────────────────────────────


class TestJWT:
    @pytest.fixture(autouse=True)
    def setup_keys(self, tmp_path):
        """Generate temporary RSA keys for testing."""
        import subprocess

        private_key_path = tmp_path / "private.pem"
        public_key_path = tmp_path / "public.pem"

        subprocess.run(
            [
                "openssl", "genpkey", "-algorithm", "RSA",
                "-out", str(private_key_path),
                "-pkeyopt", "rsa_keygen_bits:2048",
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "openssl", "rsa", "-pubout",
                "-in", str(private_key_path),
                "-out", str(public_key_path),
            ],
            check=True,
            capture_output=True,
        )

        # Patch the settings to use our test keys
        with patch("app.core.security.settings") as mock_settings:
            mock_settings.JWT_PRIVATE_KEY_PATH = str(private_key_path)
            mock_settings.JWT_PUBLIC_KEY_PATH = str(public_key_path)
            mock_settings.JWT_ALGORITHM = "RS256"
            mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 15

            # Reset cached keys
            import app.core.security as sec
            sec._private_key = None
            sec._public_key = None

            yield

            sec._private_key = None
            sec._public_key = None

    def test_create_and_decode_access_token(self):
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token(
            user_id=42, username="testuser", role_id=1
        )
        payload = decode_access_token(token)

        assert payload["sub"] == "42"
        assert payload["username"] == "testuser"
        assert payload["role_id"] == 1
        assert payload["type"] == "access"

    def test_access_token_expires(self):
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token(
            user_id=1,
            username="test",
            expires_delta=timedelta(seconds=-1),
        )

        from jose import JWTError
        with pytest.raises(JWTError):
            decode_access_token(token)

    def test_access_token_without_role(self):
        from app.core.security import create_access_token, decode_access_token

        token = create_access_token(user_id=10, username="norole")
        payload = decode_access_token(token)

        assert payload["role_id"] is None
