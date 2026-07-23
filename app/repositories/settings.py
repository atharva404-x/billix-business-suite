import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.settings import BusinessSettings, BusinessPreferences


class BusinessSettingsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BusinessSettings)

    async def get_by_business(self, business_id: uuid.UUID) -> Optional[BusinessSettings]:
        result = await self.session.execute(
            select(BusinessSettings).where(
                BusinessSettings.business_id == business_id,
                BusinessSettings.is_active == True
            )
        )
        return result.scalars().first()


class BusinessPreferencesRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BusinessPreferences)

    async def get_by_business(self, business_id: uuid.UUID) -> Optional[BusinessPreferences]:
        result = await self.session.execute(
            select(BusinessPreferences).where(
                BusinessPreferences.business_id == business_id,
                BusinessPreferences.is_active == True
            )
        )
        return result.scalars().first()
