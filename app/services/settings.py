import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.settings import BusinessSettings, BusinessPreferences
from app.schemas.settings import (
    BusinessSettingsCreate,
    BusinessSettingsUpdate,
    BusinessPreferencesCreate,
    BusinessPreferencesUpdate,
)
from app.repositories.settings import (
    BusinessSettingsRepository,
    BusinessPreferencesRepository,
)
from app.repositories.business import BusinessMemberRepository


class BusinessSettingsService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessSettingsRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def _assert_access(self, user_id: uuid.UUID, business_id: uuid.UUID) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

    async def get_or_create(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessSettings:
        await self._assert_access(user_id, business_id)
        settings = await self.repo.get_by_business(business_id)
        if not settings:
            settings = await self.repo.create(business_id=business_id)
        return settings

    async def update(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        data: BusinessSettingsUpdate,
    ) -> BusinessSettings:
        settings = await self.get_or_create(user_id, business_id)
        return await self.repo.update(settings, **data.model_dump(exclude_unset=True))


class BusinessPreferencesService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessPreferencesRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def _assert_access(self, user_id: uuid.UUID, business_id: uuid.UUID) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

    async def get_or_create(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessPreferences:
        await self._assert_access(user_id, business_id)
        prefs = await self.repo.get_by_business(business_id)
        if not prefs:
            prefs = await self.repo.create(business_id=business_id)
        return prefs

    async def update(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        data: BusinessPreferencesUpdate,
    ) -> BusinessPreferences:
        prefs = await self.get_or_create(user_id, business_id)
        return await self.repo.update(prefs, **data.model_dump(exclude_unset=True))
