import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.business import Business
from app.models.membership import Membership


class BusinessRepository:
    """
    Encapsulates all database operations (SQLAlchemy 2.0 async queries)
    for Business Profiles and Memberships.
    """

    async def create(self, db: AsyncSession, business: Business) -> Business:
        db.add(business)
        await db.commit()
        await db.refresh(business)
        return business

    async def get_by_id(self, db: AsyncSession, business_id: uuid.UUID) -> Optional[Business]:
        query = select(Business).where(Business.id == business_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_gstin(self, db: AsyncSession, gstin: str) -> Optional[Business]:
        query = select(Business).where(Business.gstin == gstin)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> List[Business]:
        # Lists all businesses where the user has an active membership link
        query = (
            select(Business)
            .join(Membership, Membership.business_id == Business.id)
            .where(
                Membership.user_id == user_id,
                Membership.is_active == True,
                Business.is_active == True
            )
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_user_membership(
        self, db: AsyncSession, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Optional[Membership]:
        # Returns the user's membership for a specific business to verify roles / status
        query = select(Membership).where(
            Membership.user_id == user_id,
            Membership.business_id == business_id,
            Membership.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create_membership(self, db: AsyncSession, membership: Membership) -> Membership:
        db.add(membership)
        await db.commit()
        await db.refresh(membership)
        return membership

    async def update(self, db: AsyncSession, business: Business) -> Business:
        await db.commit()
        await db.refresh(business)
        return business
