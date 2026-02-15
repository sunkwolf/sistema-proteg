from sqlalchemy.ext.asyncio import AsyncSession


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
