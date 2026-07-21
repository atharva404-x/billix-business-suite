import uuid
from typing import Optional
from fastapi import Header, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.business import Business
from app.models.roles import UserRole, has_minimum_role
from app.auth.dependencies import get_current_user
from app.services.business import BusinessService
from app.services.membership import MembershipService

# Instantiate services
business_service = BusinessService()
membership_service = MembershipService()


async def get_current_business(
    x_business_id: Optional[str] = Header(None, alias="X-Business-ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Business:
    """
    FastAPI dependency to retrieve and validate the active business context.

    Reads the 'X-Business-ID' custom HTTP header, verifies that the user is an active member
    of that business, and returns the Business profile.

    Raises:
        HTTPException (400): If the header is missing or malformed.
        HTTPException (403): If the user does not have membership in the business.
        HTTPException (404): If the business does not exist or is inactive.
    """
    if not x_business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business context header 'X-Business-ID' is missing."
        )

    try:
        business_uuid = uuid.UUID(x_business_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 'X-Business-ID' header format. Must be a valid UUID."
        )

    # Reuses BusinessService.get_business_by_id which enforces membership & status checks!
    return await business_service.get_business_by_id(db, current_user, business_uuid)


class RequireBusinessRole:
    """
    FastAPI dependency that restricts route access to users with a minimum role privilege
    within the active business (tenant) context.

    Acts as a reusable authorization helper for future module endpoints.
    """
    def __init__(self, required_role: UserRole):
        self.required_role = required_role

    async def __call__(
        self,
        x_business_id: Optional[str] = Header(None, alias="X-Business-ID"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not x_business_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business context header 'X-Business-ID' is missing."
            )

        try:
            business_uuid = uuid.UUID(x_business_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 'X-Business-ID' header format. Must be a valid UUID."
            )

        # Retrieve user membership for the active business
        membership = await membership_service.get_membership(db, current_user.id, business_uuid)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have membership in this business."
            )

        # Validate minimum role hierarchy requirement
        if not has_minimum_role(membership.role, self.required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Minimum role required in this business context: {self.required_role.value}"
            )

        return current_user
