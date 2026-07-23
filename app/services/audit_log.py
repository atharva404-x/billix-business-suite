import uuid
import json
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.audit_log import AuditLog, AuditAction
from app.schemas.audit_log import AuditLogCreate, AuditLogResponse, AuditLogListResponse
from app.repositories.audit_log import AuditLogRepository
from app.repositories.business import BusinessMemberRepository


class AuditLogService:
    def __init__(self, session: AsyncSession):
        self.audit_repo = AuditLogRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def log_event(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        action: AuditAction,
        before_values: Optional[dict] = None,
        after_values: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        before_json = json.dumps(before_values) if before_values else None
        after_json = json.dumps(after_values) if after_values else None
        
        return await self.audit_repo.create(
            user_id=user_id,
            business_id=business_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_values=before_json,
            after_values=after_json,
            ip_address=ip_address,
            user_agent=user_agent
        )

    async def get_audit_logs(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        action: Optional[AuditAction] = None,
        user_id_filter: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: str = "desc"
    ) -> AuditLogListResponse:
        await self._ensure_business_access(user_id, business_id)
        
        audit_logs, total = await self.audit_repo.list_by_business(
            business_id=business_id,
            skip=skip,
            limit=limit,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id_filter,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(log) for log in audit_logs],
            total=total
        )

    async def get_entity_history(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> AuditLogListResponse:
        await self._ensure_business_access(user_id, business_id)
        
        audit_logs, total = await self.audit_repo.get_by_entity(
            business_id=business_id,
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit
        )
        
        return AuditLogListResponse(
            items=[AuditLogResponse.model_validate(log) for log in audit_logs],
            total=total
        )
