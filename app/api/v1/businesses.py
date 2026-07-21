import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.business import Business
from app.auth.dependencies import get_current_user
from app.auth.business_context import get_current_business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from app.schemas.membership import MemberAdd, MembershipResponse
from app.services.business import BusinessService
from app.services.membership import MembershipService

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"],
    dependencies=[Depends(get_current_user)]  # Globally require authentication for all endpoints
)

# Instantiate the services
business_service = BusinessService()
membership_service = MembershipService()


@router.get("/current", response_model=BusinessResponse, status_code=status.HTTP_200_OK)
async def get_current_business_context(
    current_business: Business = Depends(get_current_business)
):
    """
    Retrieves the details of the active business context.

    Expects the active business ID to be supplied in the 'X-Business-ID' custom header.
    """
    return current_business


@router.post("/select/{business_id}", status_code=status.HTTP_200_OK)
async def select_business(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates that the current user has an active membership in the business
    and returns a success confirmation.

    The client should use the returned business_id to set the 'X-Business-ID'
    header in all subsequent requests.
    """
    await membership_service.validate_membership(db, current_user.id, business_id)
    return {
        "status": "selected",
        "business_id": str(business_id)
    }


@router.get("/{business_id}/members", response_model=List[MembershipResponse], status_code=status.HTTP_200_OK)
async def list_business_members(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all active team memberships of a specific business profile.
    Only authorized members of the business are permitted to access.
    """
    return await membership_service.list_members(db, current_user, business_id)


@router.post("/{business_id}/members", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
async def add_business_member(
    business_id: uuid.UUID,
    member_in: MemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Adds a new member to the business.
    Only the business OWNER is authorized to add team members.
    """
    return await membership_service.add_member(
        db, current_user, business_id, member_in.email, member_in.role
    )


@router.delete("/{business_id}/members/{member_user_id}", response_model=MembershipResponse, status_code=status.HTTP_200_OK)
async def remove_business_member(
    business_id: uuid.UUID,
    member_user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Removes a member from the business.
    Only the business OWNER is authorized to remove team members.
    """
    return await membership_service.remove_member(db, current_user, business_id, member_user_id)


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_in: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new Business Profile and associates the creator as the OWNER.
    """
    return await business_service.create_business(db, current_user, business_in)


@router.get("/", response_model=List[BusinessResponse], status_code=status.HTTP_200_OK)
async def list_user_businesses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists all active businesses where the current authenticated user has an active membership.
    """
    return await business_service.list_user_businesses(db, current_user)


@router.get("/{business_id}", response_model=BusinessResponse, status_code=status.HTTP_200_OK)
async def get_business_by_id(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the details of a specific business profile.
    Only authorized members of the business are permitted to access.
    """
    return await business_service.get_business_by_id(db, current_user, business_id)


@router.patch("/{business_id}", response_model=BusinessResponse, status_code=status.HTTP_200_OK)
async def update_business(
    business_id: uuid.UUID,
    business_in: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates specific fields of an existing business profile.
    Only the business OWNER is authorized to perform updates.
    """
    return await business_service.update_business(db, current_user, business_id, business_in)


@router.delete("/{business_id}", response_model=BusinessResponse, status_code=status.HTTP_200_OK)
async def deactivate_business(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivates (soft-deletes) a business profile.
    Only the business OWNER is authorized to deactivate.
    """
    return await business_service.deactivate_business(db, current_user, business_id)
