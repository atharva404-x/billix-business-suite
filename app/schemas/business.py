import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class BusinessBase(BaseModel):
    business_name: str = Field(..., max_length=255, description="The display name of the business")
    legal_name: Optional[str] = Field(None, max_length=255, description="The legal name of the entity")
    gstin: Optional[str] = Field(None, max_length=15, pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", description="The 15-digit GSTIN number")
    pan: Optional[str] = Field(None, max_length=10, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="The 10-digit Permanent Account Number (PAN)")
    email: Optional[EmailStr] = Field(None, description="Contact email for the business")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    website: Optional[str] = Field(None, max_length=255, description="Business website URL")
    logo_url: Optional[str] = Field(None, max_length=1024, description="URL of the business logo")

    # Address details
    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field("India", max_length=100)

    # Regional preferences
    currency: str = Field("INR", max_length=10)
    timezone: str = Field("Asia/Kolkata", max_length=50)

    # Invoice prefixes
    invoice_prefix: Optional[str] = Field(None, max_length=50)
    invoice_start_number: int = Field(1, ge=1)


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    business_name: Optional[str] = Field(None, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    gstin: Optional[str] = Field(None, max_length=15, pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
    pan: Optional[str] = Field(None, max_length=10, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=1024)

    address_line_1: Optional[str] = Field(None, max_length=255)
    address_line_2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)

    currency: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)

    invoice_prefix: Optional[str] = Field(None, max_length=50)
    invoice_start_number: Optional[int] = Field(None, ge=1)


class BusinessResponse(BusinessBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
