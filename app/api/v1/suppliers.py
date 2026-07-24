
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.supplier import SupplierType
from app.models.user import User
from app.schemas.supplier import SupplierCreate, SupplierListResponse, SupplierResponse, SupplierUpdate
from app.services.supplier import SupplierService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.post("", response_model=SupplierResponse, status_code=201)
async def create_supplier(
    business_id: uuid.UUID,
    supplier_data: SupplierCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SUPPLIER_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = SupplierService(session)
    return await service.create_supplier(
        current_user.id,
        business_id,
        supplier_data
    )

@router.get("", response_model=SupplierListResponse)
async def list_suppliers(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SUPPLIER_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    supplier_type: Optional[SupplierType] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, description="Options: name, created_at, updated_at"),
    sort_order: str = Query("asc", description="Options: asc, desc")
):
    service = SupplierService(session)
    suppliers, total = await service.list_suppliers(
        current_user.id,
        business_id,
        skip=skip,
        limit=limit,
        search_query=search_query,
        is_active=is_active,
        supplier_type=supplier_type,
        city=city,
        state=state,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return SupplierListResponse(items=suppliers, total=total)

@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    business_id: uuid.UUID,
    supplier_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SUPPLIER_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = SupplierService(session)
    return await service.get_supplier(
        current_user.id, business_id, supplier_id
    )

@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    business_id: uuid.UUID,
    supplier_id: uuid.UUID,
    update_data: SupplierUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SUPPLIER_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = SupplierService(session)
    return await service.update_supplier(
        current_user.id, business_id, supplier_id, update_data
    )

@router.delete("/{supplier_id}", response_model=SupplierResponse)
async def deactivate_supplier(
    business_id: uuid.UUID,
    supplier_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.SUPPLIER_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = SupplierService(session)
    return await service.deactivate_supplier(
        current_user.id, business_id, supplier_id
    )
