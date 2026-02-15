from sqlalchemy.ext.asyncio import AsyncSession


class TowServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
