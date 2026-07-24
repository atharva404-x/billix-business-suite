
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.business import BusinessProfileCreate, BusinessProfileListResponse, BusinessProfileResponse, BusinessProfileUpdate
from app.services.business import BusinessProfileService

router = APIRouter(prefix="/business-profiles", tags=["business"])

@router.post("", response_model=BusinessProfileResponse, status_code=201)
async def create_business_profile(
    business_data: BusinessProfileCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    # No permission check: any authenticated user may create a new business.
    service = BusinessProfileService(session)
    return await service.create_business(current_user.id, business_data)

@router.get("", response_model=BusinessProfileListResponse)
async def list_business_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    # Lists the caller's own businesses — no per-business permission needed.
    service = BusinessProfileService(session)
    businesses = await service.get_user_businesses(current_user.id)
    return BusinessProfileListResponse(items=businesses, total=len(businesses))

@router.get("/{business_id}", response_model=BusinessProfileResponse)
async def get_business_profile(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.BUSINESS_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = BusinessProfileService(session)
    return await service.get_business_by_id(current_user.id, business_id)

@router.patch("/{business_id}", response_model=BusinessProfileResponse)
async def update_business_profile(
    business_id: uuid.UUID,
    update_data: BusinessProfileUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.BUSINESS_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = BusinessProfileService(session)
    return await service.update_business(current_user.id, business_id, update_data)

@router.delete("/{business_id}", response_model=BusinessProfileResponse)
async def deactivate_business_profile(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.BUSINESS_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = BusinessProfileService(session)
    return await service.deactivate_business(current_user.id, business_id)
