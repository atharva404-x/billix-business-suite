
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    category_id: Optional[uuid.UUID] = None
    unit_id: Optional[uuid.UUID] = None
    sku: Optional[str] = Field(None, max_length=100)
    barcode: Optional[str] = Field(None, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    hsn_sac_code: Optional[str] = Field(None, max_length=20)
    gst_rate: Optional[float] = Field(None, ge=0, le=100)
    purchase_price: Optional[float] = Field(None, ge=0)
    selling_price: Optional[float] = Field(None, ge=0)
    opening_stock: Optional[float] = Field(0.0, ge=0)
    minimum_stock: Optional[float] = Field(None, ge=0)
    maximum_stock: Optional[float] = Field(None, ge=0)
    is_service: bool = False

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    current_stock: Optional[float] = Field(None, ge=0)  # Only for adjustments (manual)

class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    current_stock: float

class ProductListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[ProductResponse]
    total: int
