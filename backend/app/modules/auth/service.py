import json
import logging

import pyotp
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    needs_rehash,
    verify_password,
)
from app.modules.auth.repository import AuthRepository

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession, redis_client: redis.Redis):
        self.repo = AuthRepository(db)
        self.redis = redis_client
        self.db = db

    async def check_rate_limit_and_lockout(
        self, username: str, client_ip: str
    ) -> tuple[bool, bool]:
        """Check rate-limit and lockout status. Returns (is_rate_limited, is_locked).

        IMPORTANT: Even when rate-limited, we still increment the failure counter
        so the lockout threshold (10 attempts) can be reached. Without this,
        the counter freezes at the rate-limit (5) and lockout is unreachable.
        """
        # Check account lockout first (hard block, independent of rate limit)
        lockout_key = f"auth:lockout:{username}"
        if await self.redis.exists(lockout_key):
            return False, True

        # Check rate limit (soft block per window)
        user_key = f"auth:fail:user:{username}"
        ip_key = f"auth:fail:ip:{client_ip}"
        user_count = await self.redis.get(user_key)
        ip_count = await self.redis.get(ip_key)

        is_rate_limited = False
        if user_count and int(user_count) >= settings.LOGIN_RATE_LIMIT_USER:
            is_rate_limited = True
        elif ip_count and int(ip_count) >= settings.LOGIN_RATE_LIMIT_IP:
            is_rate_limited = True

        if is_rate_limited:
            # Still count the attempt toward lockout even though we block it
            await self._record_failed_attempt(username, client_ip)
            return True, False

        return False, False

    async def authenticate(
        self, username: str, password: str, client_ip: str,
        totp_code: str | None = None,
    ) -> dict | None:
        """
        Authenticate user, return tokens + user info, or None if invalid.
        Handles: password verify, 2FA TOTP, rehash, refresh token in Redis.
        Note: rate-limit/lockout checks are done in the router BEFORE this method.
        """
        user = await self.repo.get_user_by_username(username)
        if user is None or not user.is_active:
            await self._record_failed_attempt(username, client_ip)
            return None

        if not verify_password(password, user.password_hash):
            await self._record_failed_attempt(username, client_ip)
            return None

        # 2FA check: if user has TOTP enabled, require code
        if user.totp_enabled and user.totp_secret:
            if not totp_code:
                return {
                    "requires_2fa": True,
                    "user": user,
                }
            totp = pyotp.TOTP(user.totp_secret)
            if not totp.verify(totp_code, valid_window=1):
                await self._record_failed_attempt(username, client_ip)
                return None

        # Rehash if needed (bcrypt -> argon2id migration)
        if needs_rehash(user.password_hash):
            user.password_hash = hash_password(password)

        # Clear failed attempts on success
        await self.redis.delete(f"auth:fail:user:{username}")
        await self.redis.delete(f"auth:fail:ip:{client_ip}")

        # Update last login
        await self.repo.update_last_login(user.id)

        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role_id=user.role_id,
        )

        refresh_token, refresh_hash = generate_refresh_token()

        # Store refresh token hash in Redis with user metadata
        refresh_key = f"auth:refresh:{refresh_hash}"
        refresh_data = json.dumps({
            "user_id": user.id,
            "username": user.username,
            "family_id": refresh_hash,
        })
        await self.redis.setex(
            refresh_key,
            settings.REFRESH_TOKEN_EXPIRE_DAYS_WEB * 86400,
            refresh_data,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user,
        }

    # ── 2FA (TOTP) ───────────────────────────────────────────────────

    async def setup_totp(self, user_id: int, username: str) -> dict:
        """Generate a TOTP secret and return it with provisioning URI."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=username, issuer_name="CRM Protegrt")
        # Store secret but don't enable until verified
        await self.repo.set_totp_secret(user_id, secret)
        # Temporarily disable until user confirms with a valid code
        from sqlalchemy import update as sa_update
        from app.models.auth import AppUser
        await self.db.execute(
            sa_update(AppUser).where(AppUser.id == user_id).values(totp_enabled=False)
        )
        return {"secret": secret, "provisioning_uri": uri}

    async def verify_and_enable_totp(self, user_id: int, code: str) -> bool:
        """Verify a TOTP code against the stored secret and enable 2FA."""
        user = await self.repo.get_user_by_id(user_id)
        if user is None or not user.totp_secret:
            return False
        totp = pyotp.TOTP(user.totp_secret)
        if not totp.verify(code, valid_window=1):
            return False
        # Enable 2FA
        from sqlalchemy import update as sa_update
        from app.models.auth import AppUser
        await self.db.execute(
            sa_update(AppUser).where(AppUser.id == user_id).values(totp_enabled=True)
        )
        return True

    async def disable_totp(self, user_id: int) -> None:
        """Disable 2FA for a user."""
        await self.repo.set_totp_secret(user_id, None)

    async def refresh(self, refresh_token: str) -> dict | None:
        """Rotate refresh token. Returns new access + refresh tokens or None."""
        old_hash = hash_refresh_token(refresh_token)
        old_key = f"auth:refresh:{old_hash}"

        raw = await self.redis.get(old_key)
        if raw is None:
            return None

        data = json.loads(raw)
        family_id = data.get("family_id", old_hash)

        # Revoke old refresh token
        await self.redis.delete(old_key)

        # Load user to verify still active
        user = await self.repo.get_user_by_id(data["user_id"])
        if user is None or not user.is_active:
            # Revoke entire family if user is invalid
            await self._revoke_family(family_id)
            return None

        # Issue new tokens (rotation)
        access_token = create_access_token(
            user_id=user.id,
            username=user.username,
            role_id=user.role_id,
        )

        new_refresh, new_hash = generate_refresh_token()
        new_key = f"auth:refresh:{new_hash}"
        new_data = json.dumps({
            "user_id": user.id,
            "username": user.username,
            "family_id": family_id,
        })
        await self.redis.setex(
            new_key,
            settings.REFRESH_TOKEN_EXPIRE_DAYS_WEB * 86400,
            new_data,
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user,
        }

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = hash_refresh_token(refresh_token)
        await self.redis.delete(f"auth:refresh:{token_hash}")

    async def _record_failed_attempt(self, username: str, client_ip: str) -> None:
        """Record failed login attempt for rate limiting."""
        user_key = f"auth:fail:user:{username}"
        ip_key = f"auth:fail:ip:{client_ip}"
        window = settings.LOGIN_RATE_LIMIT_WINDOW

        user_count = await self.redis.incr(user_key)
        if user_count == 1:
            await self.redis.expire(user_key, window)

        ip_count = await self.redis.incr(ip_key)
        if ip_count == 1:
            await self.redis.expire(ip_key, window)

        # Account lockout at threshold
        if user_count >= settings.LOGIN_LOCKOUT_ATTEMPTS:
            lockout_key = f"auth:lockout:{username}"
            await self.redis.setex(
                lockout_key,
                settings.LOGIN_LOCKOUT_DURATION,
                "locked",
            )
            logger.warning(
                "Account locked: %s after %d failed attempts",
                username,
                user_count,
            )

    async def _revoke_family(self, family_id: str) -> None:
        """Revoke all refresh tokens in a family (token reuse detection)."""
        async for key in self.redis.scan_iter(match="auth:refresh:*"):
            raw = await self.redis.get(key)
            if raw:
                data = json.loads(raw)
                if data.get("family_id") == family_id:
                    await self.redis.delete(key)
