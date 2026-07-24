
import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.inventory import StockMovement
from app.models.user import User
from app.schemas.inventory import Adjustment, InventoryHistoryListResponse, InventoryTransactionResponse, ProductStockResponse, StockIn, StockOut
from app.services.inventory import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.post("/stock-in", response_model=InventoryTransactionResponse, status_code=201)
async def stock_in_endpoint(
    business_id: uuid.UUID,
    data: StockIn,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.INVENTORY_WRITE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = InventoryService(session)
    transaction, _ = await service.stock_in(current_user.id, business_id, data)
    return transaction

@router.post("/stock-out", response_model=InventoryTransactionResponse, status_code=201)
async def stock_out_endpoint(
    business_id: uuid.UUID,
    data: StockOut,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.INVENTORY_WRITE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = InventoryService(session)
    transaction, _ = await service.stock_out(current_user.id, business_id, data)
    return transaction

@router.post("/adjustment", response_model=InventoryTransactionResponse, status_code=201)
async def adjustment_endpoint(
    business_id: uuid.UUID,
    data: Adjustment,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.INVENTORY_WRITE))],
    session: AsyncSession = Depends(get_db_session)
):
    service = InventoryService(session)
    transaction, _ = await service.adjust_stock(current_user.id, business_id, data)
    return transaction

@router.get("/product/{product_id}", response_model=ProductStockResponse)
async def get_product_stock(
    business_id: uuid.UUID,
    product_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.INVENTORY_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = InventoryService(session)
    return await service.get_current_stock(current_user.id, business_id, product_id)

@router.get("/history/{product_id}", response_model=InventoryHistoryListResponse)
async def get_inventory_history(
    business_id: uuid.UUID,
    product_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.INVENTORY_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    transaction_type: Optional[StockMovement] = Query(None),
    created_by: Optional[uuid.UUID] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc")
):
    service = InventoryService(session)
    transactions, total = await service.get_inventory_history(
        current_user.id, business_id, product_id, skip, limit, start_date, end_date, transaction_type, created_by, sort_by, sort_order
    )
    return InventoryHistoryListResponse(items=transactions, total=total)
