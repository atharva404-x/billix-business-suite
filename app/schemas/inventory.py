
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.inventory import StockMovement


class StockIn(BaseModel):
    product_id: uuid.UUID
    quantity: float = Field(..., ge=0)
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class StockOut(BaseModel):
    product_id: uuid.UUID
    quantity: float = Field(..., ge=0)
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class Adjustment(BaseModel):
    product_id: uuid.UUID
    quantity: float
    reference_type: Optional[str] = None
    reference_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    product_id: uuid.UUID
    transaction_type: StockMovement
    quantity: float
    previous_stock: float
    new_stock: float
    reference_type: Optional[str]
    reference_id: Optional[uuid.UUID]
    remarks: Optional[str]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class InventoryHistoryListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[InventoryTransactionResponse]
    total: int


class ProductStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: uuid.UUID
    current_stock: float
    is_low_stock: bool
    is_out_of_stock: bool
    is_overstock: bool
