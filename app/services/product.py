
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.product import ProductRepository
from app.repositories.business import BusinessMemberRepository
from app.repositories.category import CategoryRepository
from app.repositories.unit import UnitRepository
from app.utils.validation import validate_hsn_sac


class ProductService:
    def __init__(self, session: AsyncSession):
        self.product_repo = ProductRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.category_repo = CategoryRepository(session)
        self.unit_repo = UnitRepository(session)

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def create_product(
        self, user_id: uuid.UUID, business_id: uuid.UUID, product_data: ProductCreate
    ) -> Product:
        await self._ensure_business_access(user_id, business_id)
        # Validate category exists
        if product_data.category_id:
            category = await self.category_repo.get_by_business_and_id(business_id, product_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
        # Validate unit exists
        if product_data.unit_id:
            unit = await self.unit_repo.get_by_business_and_id(business_id, product_data.unit_id)
            if not unit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Unit not found"
                )
        # Validate HSN/SAC
        if product_data.hsn_sac_code:
            if not validate_hsn_sac(product_data.hsn_sac_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid HSN/SAC code (must be 4-8 digits)"
                )
        # Check duplicate SKU
        if product_data.sku:
            existing_sku = await self.product_repo.get_by_business_and_sku(business_id, product_data.sku)
            if existing_sku:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Product with this SKU already exists"
                )
        # Check duplicate barcode
        if product_data.barcode:
            existing_barcode = await self.product_repo.get_by_business_and_barcode(business_id, product_data.barcode)
            if existing_barcode:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Product with this barcode already exists"
                )
        # Set current_stock = opening_stock if provided
        current_stock = product_data.opening_stock or 0.0
        return await self.product_repo.create(
            business_id=business_id,
            **product_data.model_dump(exclude={"opening_stock"}),
            current_stock=current_stock
        )

    async def get_product(
        self, user_id: uuid.UUID, business_id: uuid.UUID, product_id: uuid.UUID, include_inactive: bool = False
    ) -> Product:
        await self._ensure_business_access(user_id, business_id)
        product = await self.product_repo.get_by_business_and_id(business_id, product_id, include_inactive)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        return product

    async def list_products(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        category_id: Optional[uuid.UUID] = None,
        is_service: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Product], int]:
        await self._ensure_business_access(user_id, business_id)
        return await self.product_repo.list_by_business(
            business_id, skip, limit, search_query, is_active, category_id, is_service, sort_by, sort_order
        )

    async def update_product(
        self, user_id: uuid.UUID, business_id: uuid.UUID, product_id: uuid.UUID, update_data: ProductUpdate
    ) -> Product:
        product = await self.get_product(user_id, business_id, product_id)
        # Validate category exists if updating
        if update_data.category_id is not None and update_data.category_id != product.category_id:
            if update_data.category_id:
                category = await self.category_repo.get_by_business_and_id(business_id, update_data.category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found"
                    )
        # Validate unit exists if updating
        if update_data.unit_id is not None and update_data.unit_id != product.unit_id:
            if update_data.unit_id:
                unit = await self.unit_repo.get_by_business_and_id(business_id, update_data.unit_id)
                if not unit:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Unit not found"
                    )
        # Validate HSN/SAC if updating
        if update_data.hsn_sac_code is not None and update_data.hsn_sac_code != product.hsn_sac_code:
            if update_data.hsn_sac_code and not validate_hsn_sac(update_data.hsn_sac_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid HSN/SAC code (must be 4-8 digits)"
                )
        # Check duplicate SKU
        if update_data.sku is not None and update_data.sku != product.sku:
            if update_data.sku:
                existing_sku = await self.product_repo.get_by_business_and_sku(business_id, update_data.sku)
                if existing_sku:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Product with this SKU already exists"
                    )
        # Check duplicate barcode
        if update_data.barcode is not None and update_data.barcode != product.barcode:
            if update_data.barcode:
                existing_barcode = await self.product_repo.get_by_business_and_barcode(business_id, update_data.barcode)
                if existing_barcode:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Product with this barcode already exists"
                    )
        return await self.product_repo.update(
            product, **update_data.model_dump(exclude_unset=True)
        )

    async def deactivate_product(
        self, user_id: uuid.UUID, business_id: uuid.UUID, product_id: uuid.UUID
    ) -> Product:
        product = await self.get_product(user_id, business_id, product_id)
        return await self.product_repo.deactivate(product)
