from sqlalchemy.ext.asyncio import AsyncSession


class HRRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
