
import uuid
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.models.user import User
from app.schemas.unit import (
    UnitCreate,
    UnitUpdate,
    UnitResponse,
    UnitListResponse
)
from app.services.unit import UnitService


router = APIRouter(prefix="/units", tags=["units"])


@router.post("", response_model=UnitResponse, status_code=201)
async def create_unit(
    business_id: uuid.UUID,
    unit_data: UnitCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = UnitService(session)
    return await service.create_unit(current_user.id, business_id, unit_data)


@router.get("", response_model=UnitListResponse)
async def list_units(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc")
):
    service = UnitService(session)
    units, total = await service.list_units(
        current_user.id, business_id, skip, limit, search_query, is_active, sort_by, sort_order
    )
    return UnitListResponse(items=units, total=total)


@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(
    business_id: uuid.UUID,
    unit_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = UnitService(session)
    return await service.get_unit(current_user.id, business_id, unit_id)


@router.patch("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    business_id: uuid.UUID,
    unit_id: uuid.UUID,
    update_data: UnitUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = UnitService(session)
    return await service.update_unit(current_user.id, business_id, unit_id, update_data)


@router.delete("/{unit_id}", response_model=UnitResponse)
async def deactivate_unit(
    business_id: uuid.UUID,
    unit_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = UnitService(session)
    return await service.deactivate_unit(current_user.id, business_id, unit_id)
