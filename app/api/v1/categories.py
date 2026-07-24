
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryListResponse, CategoryResponse, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    business_id: uuid.UUID,
    category_data: CategoryCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(session)
    return await service.create_category(current_user.id, business_id, category_data)

@router.get("", response_model=CategoryListResponse)
async def list_categories(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    parent_id: Optional[uuid.UUID] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc")
):
    service = CategoryService(session)
    categories, total = await service.list_categories(
        current_user.id, business_id, skip, limit, search_query, is_active, parent_id, sort_by, sort_order
    )
    return CategoryListResponse(items=categories, total=total)

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    business_id: uuid.UUID,
    category_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(session)
    return await service.get_category(current_user.id, business_id, category_id)

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    business_id: uuid.UUID,
    category_id: uuid.UUID,
    update_data: CategoryUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(session)
    return await service.update_category(current_user.id, business_id, category_id, update_data)

@router.delete("/{category_id}", response_model=CategoryResponse)
async def deactivate_category(
    business_id: uuid.UUID,
    category_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CategoryService(session)
    return await service.deactivate_category(current_user.id, business_id, category_id)
