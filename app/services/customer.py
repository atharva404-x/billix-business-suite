
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.customer import Customer, CustomerType
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.repositories.customer import CustomerRepository
from app.repositories.business import BusinessMemberRepository


def validate_gstin(gstin: str) -> bool:
    if len(gstin) != 15:
        return False
    if not gstin[:2].isdigit():
            return False
    return True


class CustomerService:
    def __init__(self, session: AsyncSession):
        self.customer_repo = CustomerRepository(session)
        self.member_repo = BusinessMemberRepository(session)

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
        return await self.customer_repo.create(
            business_id=business_id, **customer_data.model_dump(),
            outstanding_balance=0.0
        )

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
        return await self.customer_repo.update(
            customer, **update_data.model_dump(exclude_unset=True)
        )

    async def deactivate_customer(
        self, user_id: uuid.UUID, business_id: uuid.UUID, customer_id: uuid.UUID
    ) -> Customer:
        customer = await self.get_customer(user_id, business_id, customer_id)
        return await self.customer_repo.deactivate(customer)
