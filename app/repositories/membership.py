import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.membership import Membership
from app.models.user import User


class MembershipRepository:
    """
    Encapsulates database operations for Memberships and User queries.
    """

    async def get_by_id(self, db: AsyncSession, membership_id: uuid.UUID) -> Optional[Membership]:
        query = select(Membership).where(Membership.id == membership_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_business_id(self, db: AsyncSession, business_id: uuid.UUID) -> List[Membership]:
        # Lists all active memberships for a business, eager loading user profile details
        query = (
            select(Membership)
            .where(Membership.business_id == business_id, Membership.is_active == True)
            .options(selectinload(Membership.user))
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_user_and_business(
        self, db: AsyncSession, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Optional[Membership]:
        # Retrieves the active membership matching user and business profile
        query = select(Membership).where(
            Membership.user_id == user_id,
            Membership.business_id == business_id,
            Membership.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        # Finds a registered user profile by email
        query = select(User).where(User.email == email, User.is_active == True)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, membership: Membership) -> Membership:
        db.add(membership)
        await db.commit()
        await db.refresh(membership)
        return membership

    async def update(self, db: AsyncSession, membership: Membership) -> Membership:
        await db.commit()
        await db.refresh(membership)
        return membership
