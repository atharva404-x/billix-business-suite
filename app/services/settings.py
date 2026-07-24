
import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction
from app.models.settings import BusinessPreferences, BusinessSettings
from app.repositories.business import BusinessMemberRepository
from app.repositories.settings import BusinessPreferencesRepository, BusinessSettingsRepository
from app.schemas.settings import BusinessPreferencesCreate, BusinessPreferencesUpdate, BusinessSettingsCreate, BusinessSettingsUpdate
from app.services.audit_log import AuditLogService

class BusinessSettingsService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessSettingsRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.audit_service = AuditLogService(session)

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
        before_values = {"company_name": settings.company_name, "gstin": settings.gstin}
        updated_settings = await self.repo.update(settings, **data.model_dump(exclude_unset=True))
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessSettings",
            entity_id=updated_settings.id,
            action=AuditAction.UPDATE,
            before_values=before_values,
            after_values=data.model_dump(exclude_unset=True)
        )
        return updated_settings

class BusinessPreferencesService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessPreferencesRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.audit_service = AuditLogService(session)

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
        before_values = {"decimal_precision": prefs.decimal_precision, "track_inventory": prefs.track_inventory}
        updated_prefs = await self.repo.update(prefs, **data.model_dump(exclude_unset=True))
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessPreferences",
            entity_id=updated_prefs.id,
            action=AuditAction.UPDATE,
            before_values=before_values,
            after_values=data.model_dump(exclude_unset=True)
        )
        return updated_prefs
