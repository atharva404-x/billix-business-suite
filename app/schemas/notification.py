
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.notification import (
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)


class NotificationBase(BaseModel):
    """Base Pydantic schema for notifications."""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    channel: NotificationChannel
    metadata: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: Optional[uuid.UUID] = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None


class NotificationResponse(NotificationBase):
    """Schema for returning notification data."""
    id: uuid.UUID
    business_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    status: NotificationStatus
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Schema for returning a list of notifications with pagination."""
    data: list[NotificationResponse]
    total: int
    page: int = 1
    page_size: int = 20

