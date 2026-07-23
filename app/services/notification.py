
import uuid
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
)
from app.repositories.notification import NotificationRepository
from app.repositories.business import BusinessMemberRepository


# ------------------------------------------------------
# Notification Provider Interface
# ------------------------------------------------------
class NotificationProvider(ABC):
    """Abstract base class for notification providers (email, SMS, WhatsApp, push)."""

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send a notification using this provider. Returns True if successful."""
        pass


# ------------------------------------------------------
# Notification Service
# ------------------------------------------------------
class NotificationService:
    """Service for managing notifications."""

    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        """Ensure user has access to the business."""
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def create_notification(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        notification_data: NotificationCreate,
    ) -> NotificationResponse:
        """Create a new notification."""
        await self._ensure_business_access(user_id, business_id)

        notification = await self.notification_repo.create(
            business_id=business_id,
            user_id=notification_data.user_id,
            type=notification_data.type,
            title=notification_data.title,
            message=notification_data.message,
            channel=notification_data.channel,
            status=NotificationStatus.PENDING,
            metadata=notification_data.metadata,
        )

        return NotificationResponse.model_validate(notification)

    async def get_notification(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> NotificationResponse:
        """Get a notification by ID."""
        await self._ensure_business_access(user_id, business_id)

        notification = await self.notification_repo.get_by_id_and_business(
            notification_id, business_id
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        return NotificationResponse.model_validate(notification)

    async def list_notifications(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id_filter: Optional[uuid.UUID] = None,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        channel: Optional[NotificationChannel] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> NotificationListResponse:
        """List notifications for a business with filters and pagination."""
        await self._ensure_business_access(user_id, business_id)

        notifications, total = await self.notification_repo.list_by_business(
            business_id=business_id,
            user_id=user_id_filter,
            type=type,
            status=status,
            channel=channel,
            page=page,
            page_size=page_size,
        )

        return NotificationListResponse(
            data=[NotificationResponse.model_validate(n) for n in notifications],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def mark_as_read(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> NotificationResponse:
        """Mark a notification as read."""
        await self._ensure_business_access(user_id, business_id)

        notification = await self.notification_repo.mark_as_read(
            notification_id, business_id
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )

        return NotificationResponse.model_validate(notification)

    async def mark_all_as_read(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        user_id_filter: Optional[uuid.UUID] = None,
    ) -> Dict[str, int]:
        """Mark all notifications as read."""
        await self._ensure_business_access(user_id, business_id)

        count = await self.notification_repo.mark_all_as_read(
            business_id, user_id_filter
        )

        return {"marked_as_read": count}


# ------------------------------------------------------
# Notification Manager
# ------------------------------------------------------
class NotificationManager:
    """Manager for handling notification providers and sending notifications."""

    def __init__(self, session: AsyncSession):
        self.notification_repo = NotificationRepository(session)
        self.providers: Dict[NotificationChannel, NotificationProvider] = {}

    def register_provider(
        self,
        channel: NotificationChannel,
        provider: NotificationProvider
    ) -> None:
        """Register a provider for a specific channel."""
        self.providers[channel] = provider

    async def send_notification(
        self,
        notification_id: uuid.UUID
    ) -> Notification:
        """Send a notification using the appropriate provider."""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise ValueError("Notification not found")

        if notification.channel in self.providers:
            provider = self.providers[notification.channel]
            success = await provider.send(notification)
            
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now(timezone.utc)
            else:
                notification.status = NotificationStatus.FAILED
        else:
            # No provider registered for this channel
            notification.status = NotificationStatus.FAILED

        await self.notification_repo.update(notification)
        return notification

