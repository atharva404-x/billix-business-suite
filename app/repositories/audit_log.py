
import uuid
from datetime import datetime
from typing import Any, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog
from app.repositories.base import BaseRepository

class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)

    async def create(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        action: AuditAction,
        before_values: Optional[Any] = None,
        after_values: Optional[Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        import json
        before_str = json.dumps(before_values) if isinstance(before_values, (dict, list)) else before_values
        after_str = json.dumps(after_values) if isinstance(after_values, (dict, list)) else after_values

        audit_log = AuditLog(
            user_id=user_id,
            business_id=business_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_values=before_str,
            after_values=after_str,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(audit_log)
        await self.session.flush()
        await self.session.refresh(audit_log)
        return audit_log

    async def list_by_business(
        self,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
        action: Optional[AuditAction] = None,
        user_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[AuditLog], int]:
        query = select(AuditLog).where(AuditLog.business_id == business_id)

        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)

        if entity_id:
            query = query.where(AuditLog.entity_id == entity_id)

        if action:
            query = query.where(AuditLog.action == action)

        if user_id:
            query = query.where(AuditLog.user_id == user_id)

        if start_date:
            query = query.where(AuditLog.created_at >= start_date)

        if end_date:
            query = query.where(AuditLog.created_at <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        if sort_by and hasattr(AuditLog, sort_by):
            sort_column = getattr(AuditLog, sort_by)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        audit_logs = result.scalars().all()

        return list(audit_logs), total

    async def get_by_entity(
        self,
        business_id: uuid.UUID,
        entity_type: str,
        entity_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AuditLog], int]:
        return await self.list_by_business(
            business_id=business_id,
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit
        )
