
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.customer import Customer, CustomerType


class CustomerRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Customer)

    async def list_by_business(
        self, 
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
    ) -> Tuple[List[Customer], int]:
        # Base query: business scoped
        query = select(Customer).where(Customer.business_id == business_id)

        # Filter by active status
        if is_active is not None:
            query = query.where(Customer.is_active == is_active)
        else:
            query = query.where(Customer.is_active == True)  # Default: only active

        # Filter by customer type
        if customer_type:
            query = query.where(Customer.type == customer_type)

        # Filter by city
        if city:
            query = query.where(Customer.city.ilike(f"%{city}%"))

        # Filter by state
        if state:
            query = query.where(Customer.state.ilike(f"%{state}%"))

        # Search
        if search_query:
            search_terms = [
                Customer.name.ilike(f"%{search_query}%"),
                Customer.gstin.ilike(f"%{search_query}%"),
                Customer.phone.ilike(f"%{search_query}%"),
                Customer.customer_code.ilike(f"%{search_query}%")
            ]
            query = query.where(or_(*search_terms))

        # Sorting
        if sort_by:
            sort_column = None
            if sort_by == "name":
                sort_column = Customer.name
            elif sort_by == "created_at":
                sort_column = Customer.created_at
            elif sort_by == "updated_at":
                sort_column = Customer.updated_at

            if sort_column:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        else:
            # Default sort
            query = query.order_by(asc(Customer.name))

        # Count total (without limit/offset)
        count_query = select(func.count(Customer.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        customers = list(result.scalars().all())

        return customers, total

    async def get_by_business_and_id(
        self, business_id: uuid.UUID, customer_id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[Customer]:
        query = select(Customer).where(
            and_(
                Customer.id == customer_id,
                Customer.business_id == business_id
            )
        )
        if not include_inactive:
            query = query.where(Customer.is_active == True)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_business_and_gstin(
        self, business_id: uuid.UUID, gstin: str
    ) -> Optional[Customer]:
        result = await self.session.execute(
            select(Customer)
            .where(
                and_(
                    Customer.gstin == gstin,
                    Customer.business_id == business_id,
                    Customer.is_active == True
                )
            )
        )
        return result.scalars().first()

    async def count_by_business(self, business_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(Customer.id)).where(
                and_(Customer.business_id == business_id, Customer.is_active == True)
            )
        )
        return result.scalar() or 0
