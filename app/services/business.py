
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.business import BusinessProfile, BusinessMember
from app.schemas.business import (
    BusinessProfileCreate, BusinessProfileUpdate
)
from app.repositories.business import BusinessProfileRepository, BusinessMemberRepository
from app.services.audit_log import AuditLogService
from app.models.audit_log import AuditAction


class BusinessProfileService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessProfileRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.audit_service = AuditLogService(session)

    async def create_business(
        self, user_id: uuid.UUID, business_data: BusinessProfileCreate
    ) -> BusinessProfile:
        from app.models.roles import BusinessRole
        business = await self.repo.create(**business_data.model_dump())
        await self.member_repo.create(
            user_id=user_id,
            business_id=business.id,
            is_owner=True,
            role=BusinessRole.OWNER,
        )
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business.id,
            entity_type="BusinessProfile",
            entity_id=business.id,
            action=AuditAction.CREATE,
            after_values=business_data.model_dump()
        )
        return business

    async def get_user_businesses(self, user_id: uuid.UUID) -> List[BusinessProfile]:
        return await self.repo.list_by_user(user_id)

    async def get_business_by_id(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessProfile:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        business = await self.repo.get_by_id(business_id)
        if not business or not business.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        return business

    async def update_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID, update_data: BusinessProfileUpdate
    ) -> BusinessProfile:
        business = await self.get_business_by_id(user_id, business_id)
        # Capture before values
        before_values = {
            "name": business.name,
            "gstin": business.gstin,
            "address": business.address,
            "city": business.city,
            "state": business.state,
            "pincode": business.pincode,
            "phone": business.phone,
            "email": business.email
        }
        updated_business = await self.repo.update(business, **update_data.model_dump(exclude_unset=True))
        # Capture after values
        after_values = {
            "name": updated_business.name,
            "gstin": updated_business.gstin,
            "address": updated_business.address,
            "city": updated_business.city,
            "state": updated_business.state,
            "pincode": updated_business.pincode,
            "phone": updated_business.phone,
            "email": updated_business.email
        }
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessProfile",
            entity_id=business_id,
            action=AuditAction.UPDATE,
            before_values=before_values,
            after_values=after_values
        )
        return updated_business

    async def deactivate_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessProfile:
        business = await self.get_business_by_id(user_id, business_id)
        deactivated_business = await self.repo.deactivate(business)
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessProfile",
            entity_id=business_id,
            action=AuditAction.DELETE,
            before_values={"is_active": True},
            after_values={"is_active": False}
        )
        return deactivated_business


class BusinessMemberService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessMemberRepository(session)
