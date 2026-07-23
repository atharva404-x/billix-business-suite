
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.permissions import PermissionChecker, Permission
from app.models.user import User
from app.models.notification import (
    NotificationType,
    NotificationStatus,
    NotificationChannel,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationListResponse,
)
from app.services.notification import NotificationService

router = APIRouter()


@router.post("/", response_model=NotificationResponse, status_code=201)
async def create_notification(
    business_id: uuid.UUID,
    notification_data: NotificationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(PermissionChecker(Permission.NOTIFICATION_CREATE)),
):
    """Create a new notification."""
    notification_service = NotificationService(db)
    return await notification_service.create_notification(
        user_id=current_user.id,
        business_id=business_id,
        notification_data=notification_data,
    )


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    business_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = Query(None, alias="user_id"),
    type: Optional[NotificationType] = Query(None),
    status: Optional[NotificationStatus] = Query(None),
    channel: Optional[NotificationChannel] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(PermissionChecker(Permission.NOTIFICATION_READ)),
):
    """List notifications with filters and pagination."""
    notification_service = NotificationService(db)
    return await notification_service.list_notifications(
        user_id=current_user.id,
        business_id=business_id,
        user_id_filter=user_id,
        type=type,
        status=status,
        channel=channel,
        page=page,
        page_size=page_size,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    business_id: uuid.UUID,
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(PermissionChecker(Permission.NOTIFICATION_READ)),
):
    """Get a single notification by ID."""
    notification_service = NotificationService(db)
    return await notification_service.get_notification(
        user_id=current_user.id,
        business_id=business_id,
        notification_id=notification_id,
    )


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    business_id: uuid.UUID,
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(PermissionChecker(Permission.NOTIFICATION_UPDATE)),
):
    """Mark a notification as read."""
    notification_service = NotificationService(db)
    return await notification_service.mark_as_read(
        user_id=current_user.id,
        business_id=business_id,
        notification_id=notification_id,
    )


@router.patch("/read-all")
async def mark_all_notifications_as_read(
    business_id: uuid.UUID,
    user_id: Optional[uuid.UUID] = Query(None, alias="user_id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(PermissionChecker(Permission.NOTIFICATION_UPDATE)),
):
    """Mark all notifications as read."""
    notification_service = NotificationService(db)
    return await notification_service.mark_all_as_read(
        user_id=current_user.id,
        business_id=business_id,
        user_id_filter=user_id,
    )

