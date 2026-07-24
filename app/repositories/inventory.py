
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryTransaction, StockMovement
from app.repositories.base import BaseRepository

class InventoryRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, InventoryTransaction)

    async def get_history_by_product(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[StockMovement] = None,
        created_by: Optional[uuid.UUID] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Tuple[List[InventoryTransaction], int]:
        query = select(InventoryTransaction).where(
            and_(InventoryTransaction.business_id == business_id, InventoryTransaction.product_id == product_id)
        )
        if start_date:
            query = query.where(InventoryTransaction.created_at >= start_date)
        if end_date:
            query = query.where(InventoryTransaction.created_at <= end_date)
        if transaction_type:
            query = query.where(InventoryTransaction.transaction_type == transaction_type)
        if created_by:
            query = query.where(InventoryTransaction.created_by == created_by)

        if sort_by:
            sort_col = None
            if sort_by == "created_at":
                sort_col = InventoryTransaction.created_at
            elif sort_by == "quantity":
                sort_col = InventoryTransaction.quantity

            if sort_col:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_col))
                else:
                    query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(InventoryTransaction.created_at))

        count_query = select(func.count(InventoryTransaction.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total
