
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.models.notification import NotificationChannel, NotificationStatus, NotificationType

class NotificationBase(BaseModel):
    """Base Pydantic schema for notifications."""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    channel: NotificationChannel
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        validation_alias=AliasChoices("notification_metadata", "metadata"),
        serialization_alias="metadata"
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if v is None:
            return v
        
        if len(v) > 50:
            raise ValueError("Metadata cannot contain more than 50 keys")
            
        def _check_value(val: Any, depth: int = 1) -> None:
            if depth > 3:
                raise ValueError("Metadata nesting depth cannot exceed 3 levels")
            if val is None:
                return
            if isinstance(val, (str, int, float, bool)):
                if isinstance(val, str) and len(val) > 1000:
                    raise ValueError("Metadata string values cannot exceed 1000 characters")
                return
            if isinstance(val, list):
                for item in val:
                    _check_value(item, depth + 1)
            elif isinstance(val, dict):
                for k, value in val.items():
                    if not isinstance(k, str):
                        raise ValueError("Metadata keys must be strings")
                    if len(k) > 100:
                        raise ValueError("Metadata keys cannot exceed 100 characters")
                    _check_value(value, depth + 1)
            else:
                raise ValueError(f"Unsupported metadata value type: {type(val).__name__}")
                
        for key, value in v.items():
            if not isinstance(key, str):
                raise ValueError("Metadata keys must be strings")
            if len(key) > 100:
                raise ValueError("Metadata keys cannot exceed 100 characters")
            _check_value(value)
            
        return v

class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: Optional[uuid.UUID] = None

class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

class NotificationResponse(NotificationBase):
    """Schema for returning notification data."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    status: NotificationStatus
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool

class NotificationListResponse(BaseModel):
    """Schema for returning a list of notifications with pagination."""
    model_config = ConfigDict(from_attributes=True)
    items: List[NotificationResponse]
    total: int

