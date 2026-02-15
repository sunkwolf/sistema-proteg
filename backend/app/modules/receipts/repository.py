from sqlalchemy.ext.asyncio import AsyncSession


class ReceiptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
