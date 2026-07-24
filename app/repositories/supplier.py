
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supplier import Supplier, SupplierType
from app.repositories.base import BaseRepository

class SupplierRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Supplier)

    async def list_by_business(
        self, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        supplier_type: Optional[SupplierType] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[Supplier], int]:
        # Base query: business scoped
        query = select(Supplier).where(Supplier.business_id == business_id)

        # Filter by active status
        if is_active is not None:
            query = query.where(Supplier.is_active == is_active)
        else:
            query = query.where(Supplier.is_active == True)  # Default: only active

        # Filter by supplier type
        if supplier_type:
            query = query.where(Supplier.type == supplier_type)

        # Filter by city
        if city:
            query = query.where(Supplier.city.ilike(f"%{city}%"))

        # Filter by state
        if state:
            query = query.where(Supplier.state.ilike(f"%{state}%"))

        # Search
        if search_query:
            search_terms = [
                Supplier.name.ilike(f"%{search_query}%"),
                Supplier.gstin.ilike(f"%{search_query}%"),
                Supplier.phone.ilike(f"%{search_query}%"),
                Supplier.supplier_code.ilike(f"%{search_query}%")
            ]
            query = query.where(or_(*search_terms))

        # Sorting
        if sort_by:
            sort_column = None
            if sort_by == "name":
                sort_column = Supplier.name
            elif sort_by == "created_at":
                sort_column = Supplier.created_at
            elif sort_by == "updated_at":
                sort_column = Supplier.updated_at

            if sort_column:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        else:
            # Default sort
            query = query.order_by(asc(Supplier.name))

        # Count total (without limit/offset)
        count_query = select(func.count(Supplier.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        suppliers = list(result.scalars().all())

        return suppliers, total

    async def get_by_business_and_id(
        self, business_id: uuid.UUID, supplier_id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[Supplier]:
        query = select(Supplier).where(
            and_(
                Supplier.id == supplier_id,
                Supplier.business_id == business_id
            )
        )
        if not include_inactive:
            query = query.where(Supplier.is_active == True)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_business_and_gstin(
        self, business_id: uuid.UUID, gstin: str
    ) -> Optional[Supplier]:
        result = await self.session.execute(
            select(Supplier)
            .where(
                and_(
                    Supplier.gstin == gstin,
                    Supplier.business_id == business_id,
                    Supplier.is_active == True
                )
            )
        )
        return result.scalars().first()

    async def count_by_business(self, business_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(Supplier.id)).where(
                and_(Supplier.business_id == business_id, Supplier.is_active == True)
            )
        )
        return result.scalar() or 0
