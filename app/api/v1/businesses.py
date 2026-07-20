import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
from app.services.business import BusinessService

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"],
    dependencies=[Depends(get_current_user)]  # Globally require authentication for all endpoints
)

# Instantiate the service
business_service = BusinessService()


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
