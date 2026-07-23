
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Notification)

    async def list_by_business(
        self,
        business_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        channel: Optional[NotificationChannel] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Notification], int]:
        """List notifications for a business with filters and pagination."""
        # Base query
        query = select(Notification).where(
            and_(
                Notification.business_id == business_id,
                Notification.is_active == True
            )
        )

        # Apply filters
        if user_id is not None:
            query = query.where(Notification.user_id == user_id)
        if type is not None:
            query = query.where(Notification.type == type)
        if status is not None:
            query = query.where(Notification.status == status)
        if channel is not None:
            query = query.where(Notification.channel == channel)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)

        result = await self.session.execute(query)
        notifications = list(result.scalars().all())

        return notifications, total

    async def get_by_id_and_business(
        self,
        notification_id: uuid.UUID,
        business_id: uuid.UUID
    ) -> Optional[Notification]:
        """Get a notification by ID and business ID (tenant isolation)."""
        query = select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.business_id == business_id,
                Notification.is_active == True
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def mark_as_read(self, notification_id: uuid.UUID, business_id: uuid.UUID) -> Optional[Notification]:
        """Mark a notification as read."""
        notification = await self.get_by_id_and_business(notification_id, business_id)
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now(timezone.utc)
            await self.session.flush()
            return notification
        return None

    async def mark_all_as_read(self, business_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> int:
        """Mark all notifications as read for a business (and optional user)."""
        query = select(Notification).where(
            and_(
                Notification.business_id == business_id,
                Notification.is_active == True,
                Notification.status != NotificationStatus.READ
            )
        )
        if user_id:
            query = query.where(Notification.user_id == user_id)
        
        result = await self.session.execute(query)
        notifications = result.scalars().all()
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.status = NotificationStatus.READ
            notification.read_at = now
        
        await self.session.flush()
        return len(notifications)

