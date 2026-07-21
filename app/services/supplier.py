
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.supplier import Supplier, SupplierType
from app.schemas.supplier import SupplierCreate, SupplierUpdate
from app.repositories.supplier import SupplierRepository
from app.repositories.business import BusinessMemberRepository
from app.utils.validation import validate_gstin


class SupplierService:
    def __init__(self, session: AsyncSession):
        self.supplier_repo = SupplierRepository(session)
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

    async def create_supplier(
        self, user_id: uuid.UUID, business_id: uuid.UUID, supplier_data: SupplierCreate
    ) -> Supplier:
        await self._ensure_business_access(user_id, business_id)
        if supplier_data.gstin:
            if not validate_gstin(supplier_data.gstin):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )
            existing = await self.supplier_repo.get_by_business_and_gstin(
                business_id, supplier_data.gstin
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Supplier with this GSTIN already exists"
                )
        return await self.supplier_repo.create(
            business_id=business_id, **supplier_data.model_dump(),
            outstanding_balance=0.0
        )

    async def get_supplier(
        self, user_id: uuid.UUID, business_id: uuid.UUID, supplier_id: uuid.UUID, include_inactive: bool = False
    ) -> Supplier:
        await self._ensure_business_access(user_id, business_id)
        supplier = await self.supplier_repo.get_by_business_and_id(
            business_id, supplier_id, include_inactive=include_inactive
        )
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        return supplier

    async def list_suppliers(
        self, 
        user_id: uuid.UUID, 
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
    ) -> tuple[List[Supplier], int]:
        await self._ensure_business_access(user_id, business_id)
        suppliers, total = await self.supplier_repo.list_by_business(
            business_id, 
            skip=skip, 
            limit=limit, 
            search_query=search_query, 
            is_active=is_active, 
            supplier_type=supplier_type, 
            city=city, 
            state=state, 
            sort_by=sort_by, 
            sort_order=sort_order
        )
        return suppliers, total

    async def update_supplier(
        self, user_id: uuid.UUID, business_id: uuid.UUID, supplier_id: uuid.UUID,
        update_data: SupplierUpdate
    ) -> Supplier:
        supplier = await self.get_supplier(user_id, business_id, supplier_id)
        if update_data.gstin:
            if not validate_gstin(update_data.gstin):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid GSTIN format"
                )
            existing = await self.supplier_repo.get_by_business_and_gstin(
                business_id, update_data.gstin
            )
            if existing and existing.id != supplier_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Supplier with this GSTIN already exists"
                )
        return await self.supplier_repo.update(
            supplier, **update_data.model_dump(exclude_unset=True)
        )

    async def deactivate_supplier(
        self, user_id: uuid.UUID, business_id: uuid.UUID, supplier_id: uuid.UUID
    ) -> Supplier:
        supplier = await self.get_supplier(user_id, business_id, supplier_id)
        return await self.supplier_repo.deactivate(supplier)
