import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import Business
from app.models.membership import Membership
from app.models.user import User
from app.models.roles import UserRole
from app.repositories.business import BusinessRepository
from app.schemas.business import BusinessCreate, BusinessUpdate


class BusinessService:
    """
    Handles all business logic, authorization checks, and orchestrates
    repository transactions for Business Profiles and Memberships.
    """
    def __init__(self, repository: Optional[BusinessRepository] = None):
        self.repository = repository or BusinessRepository()

    async def create_business(
        self, db: AsyncSession, user: User, business_in: BusinessCreate
    ) -> Business:
        """
        Creates a new Business Profile and automatically designates the creator
        as the OWNER by creating an active Membership.
        """
        # Validate duplicate GSTIN
        if business_in.gstin:
            existing = await self.repository.get_by_gstin(db, business_in.gstin)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Business with GSTIN '{business_in.gstin}' already exists."
                )

        # Map schema to SQLAlchemy model
        business = Business(**business_in.model_dump())
        business = await self.repository.create(db, business)

        # Automatically associate creator as the OWNER
        membership = Membership(
            user_id=user.id,
            business_id=business.id,
            role=UserRole.OWNER,
            joined_at=datetime.now(timezone.utc)
        )
        await self.repository.create_membership(db, membership)

        return business

    async def get_business_by_id(
        self, db: AsyncSession, user: User, business_id: uuid.UUID
    ) -> Business:
        """
        Retrieves business details.
        Enforces that only authenticated members can access details.
        """
        business = await self.repository.get_by_id(db, business_id)
        if not business or not business.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found."
            )

        # Enforce membership check (403 Forbidden if not a member)
        membership = await self.repository.get_user_membership(db, user.id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have membership in this business."
            )

        return business

    async def list_user_businesses(self, db: AsyncSession, user: User) -> List[Business]:
        """
        Lists all active businesses where the user has an active membership.
        """
        return await self.repository.list_by_user_id(db, user.id)

    async def update_business(
        self, db: AsyncSession, user: User, business_id: uuid.UUID, business_in: BusinessUpdate
    ) -> Business:
        """
        Updates an existing Business Profile.
        Enforces that only the OWNER of the business can apply updates.
        """
        business = await self.repository.get_by_id(db, business_id)
        if not business or not business.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found."
            )

        # Only the OWNER can modify business settings
        membership = await self.repository.get_user_membership(db, user.id, business_id)
        if not membership or membership.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action denied. Only the business OWNER is authorized to perform updates."
            )

        # Validate duplicate GSTIN if modified
        update_data = business_in.model_dump(exclude_unset=True)
        if "gstin" in update_data and update_data["gstin"] and update_data["gstin"] != business.gstin:
            existing = await self.repository.get_by_gstin(db, update_data["gstin"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Business with GSTIN '{update_data['gstin']}' already exists."
                )

        # Apply updates
        for field, value in update_data.items():
            setattr(business, field, value)

        return await self.repository.update(db, business)

    async def deactivate_business(
        self, db: AsyncSession, user: User, business_id: uuid.UUID
    ) -> Business:
        """
        Deactivates (soft-deletes) a Business Profile.
        Enforces that only the OWNER of the business can deactivate it.
        """
        business = await self.repository.get_by_id(db, business_id)
        if not business or not business.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business profile not found."
            )

        # Only the OWNER can deactivate a business
        membership = await self.repository.get_user_membership(db, user.id, business_id)
        if not membership or membership.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action denied. Only the business OWNER is authorized to deactivate this profile."
            )

        # Soft-delete deactivation
        business.is_active = False
        business.deleted_at = datetime.now(timezone.utc)

        return await self.repository.update(db, business)
