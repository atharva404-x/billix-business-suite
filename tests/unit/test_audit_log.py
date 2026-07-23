import uuid
import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog, AuditAction
from app.repositories.audit_log import AuditLogRepository
from app.services.audit_log import AuditLogService


@pytest.mark.asyncio
async def test_audit_log_create(db_session: AsyncSession):
    """Test creating an audit log entry."""
    repo = AuditLogRepository(db_session)
    
    user_id = uuid.uuid4()
    business_id = uuid.uuid4()
    entity_id = uuid.uuid4()
    
    audit_log = await repo.create(
        user_id=user_id,
        business_id=business_id,
        entity_type="Customer",
        entity_id=entity_id,
        action=AuditAction.CREATE,
        before_values=None,
        after_values={"name": "Test Customer", "email": "test@example.com"},
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0"
    )
    
    assert audit_log is not None
    assert audit_log.user_id == user_id
    assert audit_log.business_id == business_id
    assert audit_log.entity_type == "Customer"
    assert audit_log.entity_id == entity_id
    assert audit_log.action == AuditAction.CREATE
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "Mozilla/5.0"


@pytest.mark.asyncio
async def test_audit_log_list_by_business(db_session: AsyncSession):
    """Test listing audit logs by business."""
    repo = AuditLogRepository(db_session)
    
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create multiple audit logs
    for i in range(5):
        await repo.create(
            user_id=user_id,
            business_id=business_id,
            entity_type="Customer",
            entity_id=uuid.uuid4(),
            action=AuditAction.CREATE,
            after_values={"name": f"Customer {i}"}
        )
    
    # List audit logs
    audit_logs, total = await repo.list_by_business(business_id=business_id)
    
    assert total == 5
    assert len(audit_logs) == 5


@pytest.mark.asyncio
async def test_audit_log_filter_by_entity_type(db_session: AsyncSession):
    """Test filtering audit logs by entity type."""
    repo = AuditLogRepository(db_session)
    
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create audit logs for different entity types
    await repo.create(
        user_id=user_id,
        business_id=business_id,
        entity_type="Customer",
        entity_id=uuid.uuid4(),
        action=AuditAction.CREATE,
        after_values={"name": "Customer"}
    )
    await repo.create(
        user_id=user_id,
        business_id=business_id,
        entity_type="Product",
        entity_id=uuid.uuid4(),
        action=AuditAction.CREATE,
        after_values={"name": "Product"}
    )
    
    # Filter by entity type
    audit_logs, total = await repo.list_by_business(
        business_id=business_id,
        entity_type="Customer"
    )
    
    assert total == 1
    assert len(audit_logs) == 1
    assert audit_logs[0].entity_type == "Customer"


@pytest.mark.asyncio
async def test_audit_log_filter_by_action(db_session: AsyncSession):
    """Test filtering audit logs by action."""
    repo = AuditLogRepository(db_session)
    
    business_id = uuid.uuid4()
    user_id = uuid.uuid4()
    entity_id = uuid.uuid4()
    
    # Create audit logs with different actions
    await repo.create(
        user_id=user_id,
        business_id=business_id,
        entity_type="Customer",
        entity_id=entity_id,
        action=AuditAction.CREATE,
        after_values={"name": "Customer"}
    )
    await repo.create(
        user_id=user_id,
        business_id=business_id,
        entity_type="Customer",
        entity_id=entity_id,
        action=AuditAction.UPDATE,
        before_values={"name": "Old"},
        after_values={"name": "New"}
    )
    
    # Filter by action
    audit_logs, total = await repo.list_by_business(
        business_id=business_id,
        action=AuditAction.CREATE
    )
    
    assert total == 1
    assert len(audit_logs) == 1
    assert audit_logs[0].action == AuditAction.CREATE


@pytest.mark.asyncio
async def test_audit_log_service_log_event(db_session: AsyncSession):
    """Test AuditLogService.log_event method."""
    service = AuditLogService(db_session)
    
    user_id = uuid.uuid4()
    business_id = uuid.uuid4()
    entity_id = uuid.uuid4()
    
    audit_log = await service.log_event(
        user_id=user_id,
        business_id=business_id,
        entity_type="Invoice",
        entity_id=entity_id,
        action=AuditAction.CREATE,
        after_values={"invoice_number": "INV-001", "amount": 1000.00}
    )
    
    assert audit_log is not None
    assert audit_log.entity_type == "Invoice"
    assert audit_log.action == AuditAction.CREATE
    assert audit_log.after_values is not None
