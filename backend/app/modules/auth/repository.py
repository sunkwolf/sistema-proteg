from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import AppUser


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_username(self, username: str) -> AppUser | None:
        result = await self.session.execute(
            select(AppUser).where(AppUser.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> AppUser | None:
        result = await self.session.execute(
            select(AppUser).where(AppUser.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_last_login(self, user_id: int) -> None:
        from datetime import datetime, timezone

        await self.session.execute(
            update(AppUser)
            .where(AppUser.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )

    async def set_totp_secret(self, user_id: int, secret: str | None) -> None:
        enabled = secret is not None
        await self.session.execute(
            update(AppUser)
            .where(AppUser.id == user_id)
            .values(totp_secret=secret, totp_enabled=enabled)
        )
