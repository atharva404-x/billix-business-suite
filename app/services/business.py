
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.business import BusinessProfile, BusinessMember
from app.schemas.business import (
    BusinessProfileCreate, BusinessProfileUpdate
)
from app.repositories.business import BusinessProfileRepository, BusinessMemberRepository


class BusinessProfileService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessProfileRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def create_business(
        self, user_id: uuid.UUID, business_data: BusinessProfileCreate
    ) -> BusinessProfile:
        business = await self.repo.create(**business_data.model_dump())
        await self.member_repo.create(
            user_id=user_id,
            business_id=business.id,
            is_owner=True
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
        return await self.repo.update(business, **update_data.model_dump(exclude_unset=True))

    async def deactivate_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessProfile:
        business = await self.get_business_by_id(user_id, business_id)
        return await self.repo.deactivate(business)


class BusinessMemberService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessMemberRepository(session)
