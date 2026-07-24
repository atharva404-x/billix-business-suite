
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.customer import CustomerType
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerListResponse, CustomerResponse, CustomerUpdate
from app.services.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    business_id: uuid.UUID,
    customer_data: CustomerCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.CUSTOMER_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CustomerService(session)
    return await service.create_customer(
        current_user.id,
        business_id,
        customer_data
    )

@router.get("", response_model=CustomerListResponse)
async def list_customers(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.CUSTOMER_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search_query: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    customer_type: Optional[CustomerType] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None, description="Options: name, created_at, updated_at"),
    sort_order: str = Query("asc", description="Options: asc, desc")
):
    service = CustomerService(session)
    customers, total = await service.list_customers(
        current_user.id,
        business_id,
        skip=skip,
        limit=limit,
        search_query=search_query,
        is_active=is_active,
        customer_type=customer_type,
        city=city,
        state=state,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return CustomerListResponse(items=customers, total=total)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.CUSTOMER_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CustomerService(session)
    return await service.get_customer(
        current_user.id, business_id, customer_id
    )

@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    update_data: CustomerUpdate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.CUSTOMER_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CustomerService(session)
    return await service.update_customer(
        current_user.id, business_id, customer_id, update_data
    )

@router.delete("/{customer_id}", response_model=CustomerResponse)
async def deactivate_customer(
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.CUSTOMER_DELETE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = CustomerService(session)
    return await service.deactivate_customer(
        current_user.id, business_id, customer_id
    )
