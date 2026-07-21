import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.membership import Membership
from app.models.user import User
from app.models.roles import UserRole
from app.repositories.membership import MembershipRepository


class MembershipService:
    """
    Orchestrates business logic for team membership operations,
    role validations, and tenant access controls.
    """
    def __init__(self, repository: Optional[MembershipRepository] = None):
        self.repository = repository or MembershipRepository()

    async def add_member(
        self, db: AsyncSession, caller: User, business_id: uuid.UUID, email: str, role: UserRole
    ) -> Membership:
        """
        Adds a new member to a business.
        Only the business OWNER is authorized to add members.
        """
        # 1. Validate that the caller is the OWNER of the business
        caller_membership = await self.repository.get_by_user_and_business(db, caller.id, business_id)
        if not caller_membership or caller_membership.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action denied. Only the business OWNER can add team members."
            )

        # 2. Find the target user profile by email (user must already be registered)
        target_user = await self.repository.get_user_by_email(db, email)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{email}' is not registered in Billix. Please have them register first."
            )

        # 3. Check if target user is already a member of this business
        existing_membership = await self.repository.get_by_user_and_business(db, target_user.id, business_id)
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user is already a member of the business."
            )

        # 4. Create and save the new Membership
        membership = Membership(
            user_id=target_user.id,
            business_id=business_id,
            role=role,
            invited_by=caller.id,
            joined_at=datetime.now(timezone.utc)
        )
        return await self.repository.create(db, membership)

    async def remove_member(
        self, db: AsyncSession, caller: User, business_id: uuid.UUID, member_user_id: uuid.UUID
    ) -> Membership:
        """
        Removes a member from a business.
        Only the business OWNER can remove members. An OWNER cannot remove themselves.
        """
        # 1. Validate that the caller is the OWNER of the business
        caller_membership = await self.repository.get_by_user_and_business(db, caller.id, business_id)
        if not caller_membership or caller_membership.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Action denied. Only the business OWNER can remove team members."
            )

        # 2. Prevent the owner from removing themselves
        if caller.id == member_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Action denied. You cannot remove yourself from the business. Deactivate the business instead."
            )

        # 3. Retrieve target membership
        target_membership = await self.repository.get_by_user_and_business(db, member_user_id, business_id)
        if not target_membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership record not found for this user in the specified business."
            )

        # 4. Deactivate membership (soft-delete)
        target_membership.is_active = False
        target_membership.deleted_at = datetime.now(timezone.utc)
        return await self.repository.update(db, target_membership)

    async def list_members(
        self, db: AsyncSession, caller: User, business_id: uuid.UUID
    ) -> List[Membership]:
        """
        Lists all active team members of a business.
        Only active members of the business can retrieve this list.
        """
        caller_membership = await self.repository.get_by_user_and_business(db, caller.id, business_id)
        if not caller_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have membership in this business."
            )

        return await self.repository.list_by_business_id(db, business_id)

    async def get_membership(
        self, db: AsyncSession, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Optional[Membership]:
        """
        Retrieves the active membership details of a user for a business.
        """
        return await self.repository.get_by_user_and_business(db, user_id, business_id)

    async def validate_membership(
        self, db: AsyncSession, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Membership:
        """
        Validates that the user is an active member. Raises 403 if not.
        """
        membership = await self.repository.get_by_user_and_business(db, user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Active membership required."
            )
        return membership

    async def validate_owner(
        self, db: AsyncSession, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> Membership:
        """
        Validates that the user is the OWNER of the business. Raises 403 if not.
        """
        membership = await self.repository.get_by_user_and_business(db, user_id, business_id)
        if not membership or membership.role != UserRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only the business OWNER is authorized to perform this operation."
            )
        return membership
