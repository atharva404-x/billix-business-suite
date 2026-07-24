
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from app.services.product import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(
    business_id: uuid.UUID,
    product_data: ProductCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = ProductService(session)
    return await service.create_product(current_user.id, business_id, product_data)

@router.get("", response_model=ProductListResponse)
async def list_products(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    category_id: Optional[uuid.UUID] = Query(None),
    is_service: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc")
):
    service = ProductService(session)
    products, total = await service.list_products(
        current_user.id, business_id, skip, limit, search_query, is_active, category_id, is_service, sort_by, sort_order
    )
    return ProductListResponse(items=products, total=total)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    business_id: uuid.UUID,
    product_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = ProductService(session)
    return await service.get_product(current_user.id, business_id, product_id)

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    business_id: uuid.UUID,
    product_id: uuid.UUID,
    update_data: ProductUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = ProductService(session)
    return await service.update_product(current_user.id, business_id, product_id, update_data)

@router.delete("/{product_id}", response_model=ProductResponse)
async def deactivate_product(
    business_id: uuid.UUID,
    product_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.PRODUCT_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = ProductService(session)
    return await service.deactivate_product(current_user.id, business_id, product_id)
