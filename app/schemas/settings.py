
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# MODULE 1 — Business Settings
# ---------------------------------------------------------------------------

class BusinessSettingsBase(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    company_address: Optional[str] = None
    gstin: Optional[str] = Field(None, min_length=15, max_length=15)
    pan: Optional[str] = Field(None, min_length=10, max_length=10)
    invoice_prefix: Optional[str] = Field(None, max_length=20)
    invoice_suffix: Optional[str] = Field(None, max_length=20)
    invoice_number_format: Optional[str] = Field(None, max_length=100)
    financial_year_start: Optional[int] = Field(None, ge=1, le=12)
    currency: Optional[str] = Field(None, max_length=10)
    timezone: Optional[str] = Field(None, max_length=50)
    date_format: Optional[str] = Field(None, max_length=20)
    default_invoice_notes: Optional[str] = None
    default_payment_terms: Optional[str] = None
    logo_file_id: Optional[str] = Field(None, max_length=255)

    @field_validator("gstin")
    @classmethod
    def validate_gstin(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re
        pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid GSTIN format")
        return v

    @field_validator("pan")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        import re
        if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", v):
            raise ValueError("Invalid PAN format")
        return v

class BusinessSettingsCreate(BusinessSettingsBase):
    pass

class BusinessSettingsUpdate(BusinessSettingsBase):
    pass

class BusinessSettingsResponse(BusinessSettingsBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

# ---------------------------------------------------------------------------
# MODULE 2 — Business Preferences
# ---------------------------------------------------------------------------

class BusinessPreferencesBase(BaseModel):
    notify_low_stock: Optional[bool] = None
    notify_invoice_due: Optional[bool] = None
    notify_payment_received: Optional[bool] = None
    decimal_precision: Optional[int] = Field(None, ge=0, le=4)
    low_stock_threshold: Optional[int] = Field(None, ge=0)
    default_tax_mode: Optional[str] = Field(None, pattern=r"^(inclusive|exclusive)$")
    track_inventory: Optional[bool] = None
    allow_negative_stock: Optional[bool] = None
    report_preferences: Optional[Dict[str, Any]] = None

class BusinessPreferencesCreate(BusinessPreferencesBase):
    pass

class BusinessPreferencesUpdate(BusinessPreferencesBase):
    pass

class BusinessPreferencesResponse(BusinessPreferencesBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
