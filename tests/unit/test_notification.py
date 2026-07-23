
import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import (
    Notification,
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)
from app.repositories.notification import NotificationRepository
from app.services.notification import (
    NotificationService,
    NotificationProvider,
    NotificationManager,
)


class MockNotificationProvider(NotificationProvider):
    """Mock provider for testing."""
    async def send(self, notification: Notification) -> bool:
        return True


@pytest.mark.asyncio
async def test_notification_create(db_session: AsyncSession):
    """Test creating a notification."""
    repo = NotificationRepository(db_session)
    
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    notification = await repo.create(
        business_id=business_id,
        user_id=user_id,
        type=NotificationType.INFO,
        title="Test Notification",
        message="This is a test notification",
        channel=NotificationChannel.EMAIL,
        status=NotificationStatus.PENDING,
    )
    
    assert notification is not None
    assert notification.business_id == business_id
    assert notification.user_id == user_id
    assert notification.type == NotificationType.INFO
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.channel == NotificationChannel.EMAIL
    assert notification.status == NotificationStatus.PENDING


@pytest.mark.asyncio
async def test_notification_list_by_business(db_session: AsyncSession):
    """Test listing notifications by business."""
    repo = NotificationRepository(db_session)
    
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create multiple notifications
    for i in range(5):
        await repo.create(
            business_id=business_id,
            user_id=user_id,
            type=NotificationType.INFO,
            title=f"Test {i}",
            message=f"Message {i}",
            channel=NotificationChannel.EMAIL,
        )
    
    # List notifications
    notifications, total = await repo.list_by_business(business_id=business_id)
    
    assert total == 5
    assert len(notifications) == 5


@pytest.mark.asyncio
async def test_notification_mark_as_read(db_session: AsyncSession):
    """Test marking a notification as read."""
    repo = NotificationRepository(db_session)
    
    business_id = uuid.uuid4()
    
    notification = await repo.create(
        business_id=business_id,
        type=NotificationType.INFO,
        title="Test",
        message="Test",
        channel=NotificationChannel.EMAIL,
    )
    
    marked = await repo.mark_as_read(notification.id, business_id)
    
    assert marked is not None
    assert marked.status == NotificationStatus.READ
    assert marked.read_at is not None


@pytest.mark.asyncio
async def test_notification_manager_send(db_session: AsyncSession):
    """Test NotificationManager.send_notification."""
    manager = NotificationManager(db_session)
    provider = MockNotificationProvider()
    manager.register_provider(NotificationChannel.EMAIL, provider)
    
    repo = NotificationRepository(db_session)
    business_id = uuid.uuid4()
    notification = await repo.create(
        business_id=business_id,
        type=NotificationType.INFO,
        title="Test",
        message="Test",
        channel=NotificationChannel.EMAIL,
    )
    
    sent = await manager.send_notification(notification.id)
    
    assert sent.status == NotificationStatus.SENT
    assert sent.sent_at is not None

