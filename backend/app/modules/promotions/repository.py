from sqlalchemy.ext.asyncio import AsyncSession


class PromotionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
