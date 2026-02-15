from sqlalchemy.ext.asyncio import AsyncSession


class VehicleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
