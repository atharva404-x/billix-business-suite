
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.notification import NotificationChannel, NotificationStatus, NotificationType
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationListResponse, NotificationResponse
from app.services.notification import NotificationService

router = APIRouter()

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    business_id: uuid.UUID,
    notification_data: NotificationCreate,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_CREATE))],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new notification for a user within a business.
    """
    notification_service = NotificationService(session)
    return await notification_service.create_notification(
        user_id=current_user.id,
        business_id=business_id,
        notification_data=notification_data
    )

@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List notifications for a business with pagination (skip/limit).
    """
    notification_service = NotificationService(session)
    notifications, total = await notification_service.list_notifications(
        user_id=current_user.id,
        business_id=business_id,
        skip=skip,
        limit=limit
    )
    return NotificationListResponse(items=notifications, total=total)

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Retrieve a specific notification.
    """
    notification_service = NotificationService(session)
    return await notification_service.get_notification(
        user_id=current_user.id,
        business_id=business_id,
        notification_id=notification_id
    )

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: uuid.UUID,
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Mark a specific notification as read.
    """
    notification_service = NotificationService(session)
    return await notification_service.mark_as_read(
        user_id=current_user.id,
        business_id=business_id,
        notification_id=notification_id
    )

@router.patch("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Mark all unread notifications as read.
    """
    notification_service = NotificationService(session)
    count = await notification_service.mark_all_as_read(
        user_id=current_user.id,
        business_id=business_id
    )
    return {"count": count}

@router.delete("/{notification_id}", response_model=NotificationResponse)
async def deactivate_notification(
    notification_id: uuid.UUID,
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.NOTIFICATION_UPDATE))],
    session: AsyncSession = Depends(get_db_session)
):
    """
    Deactivate (soft-delete) a notification.
    """
    notification_service = NotificationService(session)
    return await notification_service.deactivate_notification(
        user_id=current_user.id,
        business_id=business_id,
        notification_id=notification_id
    )
