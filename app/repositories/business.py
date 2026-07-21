
import uuid
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.business import BusinessProfile, BusinessMember
from app.models.user import User


class BusinessProfileRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BusinessProfile)

    async def list_by_user(self, user_id: uuid.UUID) -> List[BusinessProfile]:
        result = await self.session.execute(
            select(BusinessProfile)
            .join(BusinessMember)
            .where(
                and_(
                    BusinessMember.user_id == user_id,
                    BusinessMember.is_active == True,
                    BusinessProfile.is_active == True
                )
            )
        )
        return list(result.scalars().all())


class BusinessMemberRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BusinessMember)

    async def get_by_user_and_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Optional[BusinessMember]:
        result = await self.session.execute(
            select(BusinessMember)
            .where(
                and_(
                    BusinessMember.user_id == user_id,
                    BusinessMember.business_id == business_id,
                    BusinessMember.is_active == True
                )
            )
        )
        return result.scalars().first()
