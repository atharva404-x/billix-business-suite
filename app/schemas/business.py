
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BusinessProfileBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    address: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None


class BusinessProfileCreate(BusinessProfileBase):
    pass


class BusinessProfileUpdate(BusinessProfileBase):
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)


class BusinessProfileResponse(BusinessProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool


class BusinessProfileListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[BusinessProfileResponse]
    total: int


class BusinessMemberBase(BaseModel):
    user_id: uuid.UUID
    business_id: uuid.UUID
    is_owner: bool = True


class BusinessMemberCreate(BusinessMemberBase):
    pass


class BusinessMemberResponse(BusinessMemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
