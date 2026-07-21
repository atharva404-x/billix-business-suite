
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.unit import Unit


class UnitRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Unit)

    async def list_by_business(
        self, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[Unit], int]:
        query = select(Unit).where(Unit.business_id == business_id)
        
        if is_active is not None:
            query = query.where(Unit.is_active == is_active)
        else:
            query = query.where(Unit.is_active == True)
            
        if search_query:
            query = query.where(
                or_(
                    Unit.name.ilike(f"%{search_query}%"),
                    Unit.symbol.ilike(f"%{search_query}%")
                )
            )
            
        if sort_by:
            sort_col = None
            if sort_by == "name":
                sort_col = Unit.name
            elif sort_by == "created_at":
                sort_col = Unit.created_at
            elif sort_by == "updated_at":
                sort_col = Unit.updated_at
                
            if sort_col:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_col))
                else:
                    query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(asc(Unit.name))
            
        count_query = select(func.count(Unit.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_business_and_id(
        self, business_id: uuid.UUID, unit_id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[Unit]:
        query = select(Unit).where(
            and_(Unit.id == unit_id, Unit.business_id == business_id)
        )
        if not include_inactive:
            query = query.where(Unit.is_active == True)
        result = await self.session.execute(query)
        return result.scalars().first()
