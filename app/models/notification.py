
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, JSON, String, Text, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, BaseModelMixin

class NotificationType(str, Enum):
    """Enum for notification types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class NotificationStatus(str, Enum):
    """Enum for notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class NotificationChannel(str, Enum):
    """Enum for notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"

class Notification(Base, BaseModelMixin):
    """SQLAlchemy model for notifications.
    
    Attributes:
        business_id: Foreign key to business profile (tenant isolation)
        user_id: Foreign key to user (recipient)
        type: Notification type (info, warning, error, success)
        title: Notification title
        message: Notification message body
        channel: Delivery channel (email, sms, whatsapp, push)
        status: Delivery status (pending, sent, failed, read)
        metadata: JSON metadata for additional context
        sent_at: Timestamp when notification was sent
        read_at: Timestamp when notification was read
    """
    __tablename__ = "notifications"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, create_constraint=True, native_enum=False), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[NotificationChannel] = mapped_column(
        SQLEnum(NotificationChannel, create_constraint=True, native_enum=False), nullable=False, index=True)
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus, create_constraint=True, native_enum=False), nullable=False, default=NotificationStatus.PENDING, index=True)
    notification_metadata: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    business = relationship("BusinessProfile", back_populates="notifications")
    user = relationship("User", back_populates="notifications")

