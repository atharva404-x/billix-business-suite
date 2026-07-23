import uuid
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.auth.permissions import PermissionChecker, Permission
from app.models.audit_log import AuditAction
from app.schemas.audit_log import AuditLogListResponse
from app.services.audit_log import AuditLogService
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[uuid.UUID] = Query(None),
    action: Optional[AuditAction] = Query(None),
    user_id_filter: Optional[uuid.UUID] = Query(None, alias="user_id"),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """
    List audit logs for a business with filtering and pagination.
    """
    audit_service = AuditLogService(session)
    return await audit_service.get_audit_logs(
        user_id=current_user.id,
        business_id=business_id,
        skip=skip,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id_filter=user_id_filter,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=AuditLogListResponse)
async def get_entity_audit_history(
    business_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Get audit history for a specific entity.
    """
    audit_service = AuditLogService(session)
    return await audit_service.get_entity_history(
        user_id=current_user.id,
        business_id=business_id,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )
