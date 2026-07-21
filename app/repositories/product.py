
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.product import Product


class ProductRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def list_by_business(
        self, 
        business_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[uuid.UUID] = None,
        is_service: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[Product], int]:
        query = select(Product).where(Product.business_id == business_id)
        
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        else:
            query = query.where(Product.is_active == True)
            
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
            
        if is_service is not None:
            query = query.where(Product.is_service == is_service)
            
        if search_query:
            search_terms = [
                Product.name.ilike(f"%{search_query}%"),
                Product.sku.ilike(f"%{search_query}%"),
                Product.barcode.ilike(f"%{search_query}%"),
                Product.hsn_sac_code.ilike(f"%{search_query}%")
            ]
            query = query.where(or_(*search_terms))
            
        if sort_by:
            sort_col = None
            if sort_by == "name":
                sort_col = Product.name
            elif sort_by == "created_at":
                sort_col = Product.created_at
            elif sort_by == "updated_at":
                sort_col = Product.updated_at
                
            if sort_col:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_col))
                else:
                    query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(asc(Product.name))
            
        count_query = select(func.count(Product.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_business_and_id(
        self, business_id: uuid.UUID, product_id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[Product]:
        query = select(Product).where(
            and_(Product.id == product_id, Product.business_id == business_id)
        )
        if not include_inactive:
            query = query.where(Product.is_active == True)
        result = await self.session.execute(query)
        return result.scalars().first()
        
    async def get_by_business_and_sku(
        self, business_id: uuid.UUID, sku: str
    ) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(
                and_(
                    Product.sku == sku,
                    Product.business_id == business_id,
                    Product.is_active == True
                )
            )
        )
        return result.scalars().first()
        
    async def get_by_business_and_barcode(
        self, business_id: uuid.UUID, barcode: str
    ) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(
                and_(
                    Product.barcode == barcode,
                    Product.business_id == business_id,
                    Product.is_active == True
                )
            )
        )
        return result.scalars().first()
