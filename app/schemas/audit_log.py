
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.audit_log import AuditAction

class AuditLogBase(BaseModel):
    entity_type: str = Field(..., description="Type of entity (e.g., 'Customer', 'Invoice')")
    entity_id: uuid.UUID = Field(..., description="ID of the entity")
    action: AuditAction = Field(..., description="Action performed (CREATE, UPDATE, DELETE, VIEW)")
    before_values: Optional[str] = Field(None, description="JSON string of before values")
    after_values: Optional[str] = Field(None, description="JSON string of after values")
    ip_address: Optional[str] = Field(None, description="IP address of the user")
    user_agent: Optional[str] = Field(None, description="User agent string")

class AuditLogCreate(AuditLogBase):
    user_id: uuid.UUID = Field(..., description="ID of the user who performed the action")
    business_id: uuid.UUID = Field(..., description="ID of the business")

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    business_id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    action: AuditAction
    before_values: Optional[str]
    after_values: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
