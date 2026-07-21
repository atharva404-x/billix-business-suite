
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.customer import CustomerType


class CustomerBase(BaseModel):
    customer_code: Optional[str] = Field(None, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    type: CustomerType = CustomerType.B2C
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    credit_limit: Optional[float] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[CustomerType] = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    outstanding_balance: float


class CustomerListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[CustomerResponse]
    total: int
