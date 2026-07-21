
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class UnitBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    symbol: Optional[str] = Field(None, max_length=20)


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class UnitResponse(UnitBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool


class UnitListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[UnitResponse]
    total: int
