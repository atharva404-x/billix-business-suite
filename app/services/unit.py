
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate
from app.repositories.unit import UnitRepository
from app.repositories.business import BusinessMemberRepository


class UnitService:
    def __init__(self, session: AsyncSession):
        self.unit_repo = UnitRepository(session)
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

    async def create_unit(
        self, user_id: uuid.UUID, business_id: uuid.UUID, unit_data: UnitCreate
    ) -> Unit:
        await self._ensure_business_access(user_id, business_id)
        return await self.unit_repo.create(business_id=business_id, **unit_data.model_dump())

    async def get_unit(
        self, user_id: uuid.UUID, business_id: uuid.UUID, unit_id: uuid.UUID, include_inactive: bool = False
    ) -> Unit:
        await self._ensure_business_access(user_id, business_id)
        unit = await self.unit_repo.get_by_business_and_id(business_id, unit_id, include_inactive)
        if not unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found"
            )
        return unit

    async def list_units(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        search_query: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> tuple[List[Unit], int]:
        await self._ensure_business_access(user_id, business_id)
        return await self.unit_repo.list_by_business(
            business_id, skip, limit, search_query, is_active, sort_by, sort_order
        )

    async def update_unit(
        self, user_id: uuid.UUID, business_id: uuid.UUID, unit_id: uuid.UUID, update_data: UnitUpdate
    ) -> Unit:
        unit = await self.get_unit(user_id, business_id, unit_id)
        return await self.unit_repo.update(unit, **update_data.model_dump(exclude_unset=True))

    async def deactivate_unit(
        self, user_id: uuid.UUID, business_id: uuid.UUID, unit_id: uuid.UUID
    ) -> Unit:
        unit = await self.get_unit(user_id, business_id, unit_id)
        return await self.unit_repo.deactivate(unit)
