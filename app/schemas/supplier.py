
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.supplier import SupplierType

class SupplierBase(BaseModel):
    supplier_code: Optional[str] = Field(None, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    type: SupplierType = SupplierType.BUSINESS
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    credit_limit: Optional[float] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[SupplierType] = None

class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    outstanding_balance: float

class SupplierListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[SupplierResponse]
    total: int
