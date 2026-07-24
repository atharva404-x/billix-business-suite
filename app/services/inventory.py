
import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryTransaction, StockMovement
from app.models.product import Product
from app.repositories.business import BusinessMemberRepository
from app.repositories.inventory import InventoryRepository
from app.schemas.inventory import Adjustment, StockIn, StockOut

class InventoryService:
    def __init__(self, session: AsyncSession):
        self.inventory_repo = InventoryRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.session = session

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def get_product_and_validate_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID, product_id: uuid.UUID, for_update: bool = False
    ) -> Product:
        await self._ensure_business_access(user_id, business_id)
        query = select(Product).where(
            Product.id == product_id,
            Product.business_id == business_id,
            Product.is_active == True
        )
        if for_update:
            query = query.with_for_update()
        result = await self.session.execute(query)
        product = result.scalars().first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    async def _create_transaction(
        self,
        business_id: uuid.UUID,
        product_id: uuid.UUID,
        transaction_type: StockMovement,
        quantity: float,
        previous_stock: float,
        new_stock: float,
        created_by: uuid.UUID,
        reference_type: Optional[str] = None,
        reference_id: Optional[uuid.UUID] = None,
        remarks: Optional[str] = None
    ) -> InventoryTransaction:
        transaction = InventoryTransaction(
            business_id=business_id,
            product_id=product_id,
            transaction_type=transaction_type,
            quantity=quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reference_type=reference_type,
            reference_id=reference_id,
            remarks=remarks,
            created_by=created_by
        )
        self.session.add(transaction)
        return transaction

    async def _update_product_stock(
        self,
        product: Product,
        new_stock: float
    ) -> Product:
        product.current_stock = new_stock
        return product

    async def stock_in(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        data: StockIn
    ) -> Tuple[InventoryTransaction, Product]:
        product = await self.get_product_and_validate_access(user_id, business_id, data.product_id, for_update=True)
        previous_stock = product.current_stock
        new_stock = previous_stock + data.quantity
        transaction = await self._create_transaction(
            business_id=business_id,
            product_id=data.product_id,
            transaction_type=StockMovement.PURCHASE,
            quantity=data.quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            created_by=user_id,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            remarks=data.remarks
        )
        product = await self._update_product_stock(product, new_stock)
        await self.session.flush()
        await self.session.refresh(transaction)
        await self.session.refresh(product)
        return transaction, product

    async def stock_out(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        data: StockOut
    ) -> Tuple[InventoryTransaction, Product]:
        product = await self.get_product_and_validate_access(user_id, business_id, data.product_id, for_update=True)
        previous_stock = product.current_stock
        await self.validate_stock_availability(product, data.quantity)
        new_stock = previous_stock - data.quantity
        transaction = await self._create_transaction(
            business_id=business_id,
            product_id=data.product_id,
            transaction_type=StockMovement.SALE,
            quantity=data.quantity,
            previous_stock=previous_stock,
            new_stock=new_stock,
            created_by=user_id,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            remarks=data.remarks
        )
        product = await self._update_product_stock(product, new_stock)
        await self.session.flush()
        await self.session.refresh(transaction)
        await self.session.refresh(product)
        return transaction, product

    async def adjust_stock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        data: Adjustment
    ) -> Tuple[InventoryTransaction, Product]:
        product = await self.get_product_and_validate_access(user_id, business_id, data.product_id, for_update=True)
        previous_stock = product.current_stock
        new_stock = data.quantity
        quantity_change = new_stock - previous_stock
        if quantity_change > 0:
            transaction_type = StockMovement.ADJUSTMENT_IN
        elif quantity_change < 0:
            transaction_type = StockMovement.ADJUSTMENT_OUT
        else:
            transaction_type = StockMovement.MANUAL_UPDATE
        transaction = await self._create_transaction(
            business_id=business_id,
            product_id=data.product_id,
            transaction_type=transaction_type,
            quantity=abs(quantity_change),
            previous_stock=previous_stock,
            new_stock=new_stock,
            created_by=user_id,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            remarks=data.remarks
        )
        product = await self._update_product_stock(product, new_stock)
        await self.session.flush()
        await self.session.refresh(transaction)
        await self.session.refresh(product)
        return transaction, product

    async def get_current_stock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> dict:
        product = await self.get_product_and_validate_access(user_id, business_id, product_id)
        is_low_stock = False
        is_out_of_stock = product.current_stock <= 0
        is_overstock = False
        if product.minimum_stock is not None:
            is_low_stock = product.current_stock <= product.minimum_stock
        if product.maximum_stock is not None:
            is_overstock = product.current_stock >= product.maximum_stock
        return {
            "product_id": product.id,
            "current_stock": product.current_stock,
            "is_low_stock": is_low_stock,
            "is_out_of_stock": is_out_of_stock,
            "is_overstock": is_overstock
        }

    async def validate_stock_availability(
        self,
        product: Product,
        required_quantity: float
    ):
        if product.current_stock < required_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Current stock: {product.current_stock}, Required: {required_quantity}"
            )

    async def get_inventory_history(
        self,
        user_id: uuid.UUID,
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
    ):
        await self._ensure_business_access(user_id, business_id)
        return await self.inventory_repo.get_history_by_product(
            business_id, product_id, skip, limit, start_date, end_date, transaction_type, created_by, sort_by, sort_order
        )

    async def calculate_stock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> float:
        await self._ensure_business_access(user_id, business_id)
        product = await self.get_product_and_validate_access(user_id, business_id, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product.current_stock

    async def check_low_stock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> bool:
        stock_info = await self.get_current_stock(user_id, business_id, product_id)
        return stock_info["is_low_stock"]

    async def check_out_of_stock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> bool:
        stock_info = await self.get_current_stock(user_id, business_id, product_id)
        return stock_info["is_out_of_stock"]

    async def check_overstock(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        product_id: uuid.UUID
    ) -> bool:
        stock_info = await self.get_current_stock(user_id, business_id, product_id)
        return stock_info["is_overstock"]
