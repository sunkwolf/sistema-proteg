from sqlalchemy.ext.asyncio import AsyncSession


class AuthorizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
