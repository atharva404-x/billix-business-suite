
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.category import CategoryRepository
from app.repositories.business import BusinessMemberRepository


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.category_repo = CategoryRepository(session)
        self.member_repo = BusinessMemberRepository(session)

    async def _ensure_business_access(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> None:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this business"
            )

    async def create_category(
        self, user_id: uuid.UUID, business_id: uuid.UUID, category_data: CategoryCreate
    ) -> Category:
        await self._ensure_business_access(user_id, business_id)
        # If parent_id is provided, check if parent exists and belongs to the same business
        if category_data.parent_id:
            parent = await self.category_repo.get_by_business_and_id(business_id, category_data.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found"
                )
        return await self.category_repo.create(business_id=business_id, **category_data.model_dump())

    async def get_category(
        self, user_id: uuid.UUID, business_id: uuid.UUID, category_id: uuid.UUID, include_inactive: bool = False
    ) -> Category:
        await self._ensure_business_access(user_id, business_id)
        category = await self.category_repo.get_by_business_and_id(business_id, category_id, include_inactive)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category

    async def list_categories(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        parent_id: Optional[uuid.UUID] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Category], int]:
        await self._ensure_business_access(user_id, business_id)
        return await self.category_repo.list_by_business(
            business_id, skip, limit, search_query, is_active, parent_id, sort_by, sort_order
        )

    async def update_category(
        self, user_id: uuid.UUID, business_id: uuid.UUID, category_id: uuid.UUID, update_data: CategoryUpdate
    ) -> Category:
        category = await self.get_category(user_id, business_id, category_id)
        # Check parent_id if present
        if update_data.parent_id is not None and update_data.parent_id != category.parent_id:
            if update_data.parent_id:
                parent = await self.category_repo.get_by_business_and_id(business_id, update_data.parent_id)
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Parent category not found"
                    )
        return await self.category_repo.update(category, **update_data.model_dump(exclude_unset=True))

    async def deactivate_category(
        self, user_id: uuid.UUID, business_id: uuid.UUID, category_id: uuid.UUID
    ) -> Category:
        category = await self.get_category(user_id, business_id, category_id)
        return await self.category_repo.deactivate(category)
