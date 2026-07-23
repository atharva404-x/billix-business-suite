import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.database import get_db_session
from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker

from app.models.user import User
from app.models.business import BusinessProfile, BusinessMember
from app.models.roles import BusinessRole
from app.models.audit_log import AuditLog, AuditAction

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


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    """Clear dependency overrides before and after each test."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


# ==============================================================================
# 1. Repository Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_notification_repo_create(db_session: AsyncSession):
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
        notification_metadata={"key": "value"}
    )
    
    assert notification is not None
    assert notification.business_id == business_id
    assert notification.user_id == user_id
    assert notification.type == NotificationType.INFO
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test notification"
    assert notification.channel == NotificationChannel.EMAIL
    assert notification.status == NotificationStatus.PENDING
    assert notification.notification_metadata == {"key": "value"}


@pytest.mark.asyncio
async def test_notification_repo_list_by_business(db_session: AsyncSession):
    """Test listing notifications by business with skip and limit."""
    repo = NotificationRepository(db_session)
    business_id = uuid.uuid4()
    
    # Create multiple notifications
    for i in range(5):
        await repo.create(
            business_id=business_id,
            type=NotificationType.INFO,
            title=f"Test {i}",
            message=f"Message {i}",
            channel=NotificationChannel.EMAIL,
        )
    
    # List notifications with limit
    notifications, total = await repo.list_by_business(
        business_id=business_id,
        skip=1,
        limit=3
    )
    
    assert total == 5
    assert len(notifications) == 3


@pytest.mark.asyncio
async def test_notification_repo_mark_as_read(db_session: AsyncSession):
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
async def test_notification_repo_mark_all_as_read(db_session: AsyncSession):
    """Test marking all unread notifications as read."""
    repo = NotificationRepository(db_session)
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create unread notifications
    for _ in range(3):
        await repo.create(
            business_id=business_id,
            user_id=user_id,
            type=NotificationType.INFO,
            title="Test",
            message="Test",
            channel=NotificationChannel.EMAIL,
            status=NotificationStatus.PENDING
        )
        
    count = await repo.mark_all_as_read(business_id, user_id)
    assert count == 3
    
    # Check that they are read
    notifications, total = await repo.list_by_business(business_id, user_id=user_id)
    assert all(n.status == NotificationStatus.READ for n in notifications)


# ==============================================================================
# 2. Service Layer Tests
# ==============================================================================

async def setup_test_membership(db_session: AsyncSession) -> tuple[User, BusinessProfile]:
    """Helper to provision a user and a business membership."""
    user = User(
        clerk_id=f"clerk_{uuid.uuid4().hex[:10]}",
        email="test_user@example.com",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    await db_session.flush()

    business = BusinessProfile(
        business_name="Notification Test Co",
        gstin=f"07{uuid.uuid4().hex[:10].upper()}Z1",
        is_active=True
    )
    db_session.add(business)
    await db_session.flush()

    member = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role=BusinessRole.OWNER,
        is_active=True
    )
    db_session.add(member)
    await db_session.commit()
    
    return user, business


@pytest.mark.asyncio
async def test_notification_service_create(db_session: AsyncSession):
    """Test notification service create and audit logging."""
    user, business = await setup_test_membership(db_session)
    service = NotificationService(db_session)
    
    from app.schemas.notification import NotificationCreate
    data = NotificationCreate(
        type=NotificationType.INFO,
        title="Service Title",
        message="Service message body",
        channel=NotificationChannel.EMAIL,
        metadata={"extra": "details"}
    )
    
    notification = await service.create_notification(
        user_id=user.id,
        business_id=business.id,
        notification_data=data
    )
    
    assert notification.title == "Service Title"
    assert notification.notification_metadata == {"extra": "details"}
    
    # Check audit log
    from app.repositories.audit_log import AuditLogRepository
    audit_repo = AuditLogRepository(db_session)
    logs, count = await audit_repo.list_by_business(business.id)
    assert count == 1
    assert logs[0].action == AuditAction.CREATE
    assert logs[0].entity_type == "Notification"


@pytest.mark.asyncio
async def test_notification_service_recipient_validation(db_session: AsyncSession):
    """Test notification service rejects recipient user not in the business."""
    user, business = await setup_test_membership(db_session)
    service = NotificationService(db_session)
    
    # Non-member user ID
    invalid_recipient_id = uuid.uuid4()
    
    from app.schemas.notification import NotificationCreate
    data = NotificationCreate(
        user_id=invalid_recipient_id,
        type=NotificationType.INFO,
        title="Alert",
        message="Alert body",
        channel=NotificationChannel.EMAIL
    )
    
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await service.create_notification(
            user_id=user.id,
            business_id=business.id,
            notification_data=data
        )
        
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Recipient is not a member" in exc.value.detail


@pytest.mark.asyncio
async def test_notification_service_deactivate(db_session: AsyncSession):
    """Test deactivating (soft-deleting) a notification."""
    user, business = await setup_test_membership(db_session)
    service = NotificationService(db_session)
    
    from app.schemas.notification import NotificationCreate
    data = NotificationCreate(
        type=NotificationType.WARNING,
        title="Soft Delete test",
        message="Test body",
        channel=NotificationChannel.PUSH
    )
    
    notification = await service.create_notification(user.id, business.id, data)
    
    # Soft delete
    deactivated = await service.deactivate_notification(user.id, business.id, notification.id)
    assert deactivated.is_active is False
    
    # Verify audit log
    from app.repositories.audit_log import AuditLogRepository
    audit_repo = AuditLogRepository(db_session)
    logs, count = await audit_repo.list_by_business(business.id, entity_type="Notification")
    # 1 log for CREATE, 1 log for DELETE
    assert count == 2
    delete_log = next(log for log in logs if log.action == AuditAction.DELETE)
    assert delete_log is not None


# ==============================================================================
# 3. NotificationManager Multi-Tenant Security
# ==============================================================================

@pytest.mark.asyncio
async def test_notification_manager_tenant_isolation(db_session: AsyncSession):
    """Test NotificationManager prevents tenant bypass."""
    manager = NotificationManager(db_session)
    provider = MockNotificationProvider()
    manager.register_provider(NotificationChannel.EMAIL, provider)
    
    repo = NotificationRepository(db_session)
    business_id = uuid.uuid4()
    other_business_id = uuid.uuid4()
    
    notification = await repo.create(
        business_id=business_id,
        type=NotificationType.INFO,
        title="Secure",
        message="Text",
        channel=NotificationChannel.EMAIL,
    )
    
    # Trying to send with another business ID should raise ValueError
    with pytest.raises(ValueError) as exc:
        await manager.send_notification(notification.id, other_business_id)
        
    assert "Notification not found" in str(exc.value)


# ==============================================================================
# 4. API & Permission Route Tests
# ==============================================================================

def test_api_notification_crud(db_session: AsyncSession):
    """Test notification REST endpoints and RLS verification using TestClient."""
    # 1. Provision user, business, membership
    import asyncio
    user, business = asyncio.run(setup_test_membership(db_session))
    
    # 2. Setup Dependency Overrides
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user
    
    client = TestClient(app)
    
    # 3. POST - Create Notification
    payload = {
        "type": "info",
        "title": "API Notification",
        "message": "This was created via FastAPI router",
        "channel": "email",
        "metadata": {"test": "api"}
    }
    
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": user.clerk_id}
        
        response = client.post(
            f"/api/v1/notifications?business_id={business.id}",
            json=payload,
            headers={"Authorization": "Bearer dummy_token"}
        )
        assert response.status_code == 201
        res_data = response.json()
        assert res_data["title"] == "API Notification"
        assert res_data["metadata"] == {"test": "api"}
        notification_id = res_data["id"]
        
        # 4. GET - List Notifications
        response = client.get(
            f"/api/v1/notifications?business_id={business.id}&skip=0&limit=10",
            headers={"Authorization": "Bearer dummy_token"}
        )
        assert response.status_code == 200
        list_data = response.json()
        assert list_data["total"] == 1
        assert list_data["items"][0]["id"] == notification_id
        
        # 5. PATCH - Mark Read
        response = client.patch(
            f"/api/v1/notifications/{notification_id}/read?business_id={business.id}",
            headers={"Authorization": "Bearer dummy_token"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "read"
        
        # 6. DELETE - Deactivate
        response = client.delete(
            f"/api/v1/notifications/{notification_id}?business_id={business.id}",
            headers={"Authorization": "Bearer dummy_token"}
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False


def test_api_notification_tenant_isolation(db_session: AsyncSession):
    """Test API rejects actions if user belongs to another tenant or lacks access."""
    import asyncio
    user, business = asyncio.run(setup_test_membership(db_session))
    
    # Unrelated tenant business profile
    other_business = BusinessProfile(
        business_name="Foreign Company",
        gstin="07BBBBB2222B2Z2",
        is_active=True
    )
    db_session.add(other_business)
    asyncio.run(db_session.commit())
    
    app.dependency_overrides[get_db_session] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user
    
    client = TestClient(app)
    
    with patch("app.middleware.auth.authenticate_request", new_callable=AsyncMock) as mock_auth:
        mock_auth.return_value = {"sub": user.clerk_id}
        
        # List notifications with other business ID should return 403 Forbidden
        response = client.get(
            f"/api/v1/notifications?business_id={other_business.id}",
            headers={"Authorization": "Bearer dummy_token"}
        )
        assert response.status_code == 403
        assert "You are not a member" in response.json()["detail"]
