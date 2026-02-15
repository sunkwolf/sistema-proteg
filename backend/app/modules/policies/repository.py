from sqlalchemy.ext.asyncio import AsyncSession


class PolicyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
