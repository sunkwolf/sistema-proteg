from sqlalchemy.ext.asyncio import AsyncSession


class CollectionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
