
import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction
from app.models.customer import Customer, CustomerType
from app.repositories.business import BusinessMemberRepository
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit_log import AuditLogService
from app.utils.validation import validate_gstin

class CustomerService:
    def __init__(self, session: AsyncSession):
        self.customer_repo = CustomerRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.audit_service = AuditLogService(session)

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        membership = await self.member_repo.get_by_user_and_business(
            user_id, business_id
        )
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def create_customer(
        self, user_id: uuid.UUID, business_id: uuid.UUID, customer_data: CustomerCreate
    ) -> Customer:
        await self._ensure_business_access(user_id, business_id)
        if customer_data.gstin:
            if not validate_gstin(customer_data.gstin):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )
            existing = await self.customer_repo.get_by_business_and_gstin(
                business_id, customer_data.gstin
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Customer with this GSTIN already exists"
                )
        customer = await self.customer_repo.create(
            business_id=business_id, **customer_data.model_dump(),
            outstanding_balance=0.0
        )
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Customer",
            entity_id=customer.id,
            action=AuditAction.CREATE,
            after_values=customer_data.model_dump()
        )
        return customer

    async def get_customer(
        self, user_id: uuid.UUID, business_id: uuid.UUID, customer_id: uuid.UUID, include_inactive: bool = False
    ) -> Customer:
        await self._ensure_business_access(user_id, business_id)
        customer = await self.customer_repo.get_by_business_and_id(
            business_id, customer_id, include_inactive=include_inactive
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer

    async def list_customers(
        self, 
        user_id: uuid.UUID, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        customer_type: Optional[CustomerType] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Customer], int]:
        await self._ensure_business_access(user_id, business_id)
        customers, total = await self.customer_repo.list_by_business(
            business_id, 
            skip=skip, 
            limit=limit, 
            search_query=search_query, 
            is_active=is_active, 
            customer_type=customer_type, 
            city=city, 
            state=state, 
            sort_by=sort_by, 
            sort_order=sort_order
        )
        return customers, total

    async def update_customer(
        self, user_id: uuid.UUID, business_id: uuid.UUID, customer_id: uuid.UUID,
        update_data: CustomerUpdate
    ) -> Customer:
        customer = await self.get_customer(user_id, business_id, customer_id)
        if update_data.gstin:
            if not validate_gstin(update_data.gstin):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )
            existing = await self.customer_repo.get_by_business_and_gstin(
                business_id, update_data.gstin
            )
            if existing and existing.id != customer_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Customer with this GSTIN already exists"
                )
        updated_customer = await self.customer_repo.update(
            customer, **update_data.model_dump(exclude_unset=True)
        )
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Customer",
            entity_id=customer_id,
            action=AuditAction.UPDATE,
            before_values={"name": customer.name, "email": customer.email, "phone": customer.phone},
            after_values=update_data.model_dump(exclude_unset=True)
        )
        return updated_customer

    async def deactivate_customer(
        self, user_id: uuid.UUID, business_id: uuid.UUID, customer_id: uuid.UUID
    ) -> Customer:
        customer = await self.get_customer(user_id, business_id, customer_id)
        deactivated_customer = await self.customer_repo.deactivate(customer)
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Customer",
            entity_id=customer_id,
            action=AuditAction.DELETE,
            before_values={"name": customer.name, "is_active": True},
            after_values={"is_active": False}
        )
        return deactivated_customer
