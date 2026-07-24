
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.settings import BusinessPreferencesResponse, BusinessPreferencesUpdate, BusinessSettingsResponse, BusinessSettingsUpdate
from app.services.settings import BusinessPreferencesService, BusinessSettingsService

router = APIRouter(prefix="/business-profiles", tags=["business-settings"])

# ---------------------------------------------------------------------------
# MODULE 1 — Business Settings endpoints
# ---------------------------------------------------------------------------

@router.get("/{business_id}/settings", response_model=BusinessSettingsResponse)
async def get_business_settings(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SETTINGS_READ))],
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessSettingsService(session)
    return await service.get_or_create(current_user.id, business_id)

@router.patch("/{business_id}/settings", response_model=BusinessSettingsResponse)
async def update_business_settings(
    business_id: uuid.UUID,
    data: BusinessSettingsUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SETTINGS_UPDATE))],
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessSettingsService(session)
    return await service.update(current_user.id, business_id, data)

# ---------------------------------------------------------------------------
# MODULE 2 — Business Preferences endpoints
# ---------------------------------------------------------------------------

@router.get("/{business_id}/preferences", response_model=BusinessPreferencesResponse)
async def get_business_preferences(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SETTINGS_READ))],
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessPreferencesService(session)
    return await service.get_or_create(current_user.id, business_id)

@router.patch("/{business_id}/preferences", response_model=BusinessPreferencesResponse)
async def update_business_preferences(
    business_id: uuid.UUID,
    data: BusinessPreferencesUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SETTINGS_UPDATE))],
    session: AsyncSession = Depends(get_db_session),
):
    service = BusinessPreferencesService(session)
    return await service.update(current_user.id, business_id, data)
