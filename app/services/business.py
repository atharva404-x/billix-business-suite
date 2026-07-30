
import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction
from app.models.business import BusinessMember, BusinessProfile
from app.repositories.business import BusinessMemberRepository, BusinessProfileRepository
from app.schemas.business import BusinessProfileCreate, BusinessProfileUpdate
from app.services.audit_log import AuditLogService

class BusinessProfileService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessProfileRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.audit_service = AuditLogService(session)

    async def create_business(
        self, user_id: uuid.UUID, business_data: BusinessProfileCreate
    ) -> BusinessProfile:
        from app.models.roles import BusinessRole
        business = await self.repo.create(**business_data.model_dump())
        await self.member_repo.create(
            user_id=user_id,
            business_id=business.id,
            is_owner=True,
            role=BusinessRole.OWNER,
        )
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business.id,
            entity_type="BusinessProfile",
            entity_id=business.id,
            action=AuditAction.CREATE,
            after_values=business_data.model_dump()
        )
        return business

    async def get_user_businesses(self, user_id: uuid.UUID) -> List[BusinessProfile]:
        return await self.repo.list_by_user(user_id)

    async def get_business_by_id(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessProfile:
        membership = await self.member_repo.get_by_user_and_business(user_id, business_id)
        if not membership:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        business = await self.repo.get_by_id(business_id)
        if not business or not business.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
        return business

    async def update_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID, update_data: BusinessProfileUpdate
    ) -> BusinessProfile:
        business = await self.get_business_by_id(user_id, business_id)
        # Capture before values
        before_values = {
            "business_name": business.business_name,
            "gstin": business.gstin,
            "address": business.address,
            "city": business.city,
            "state": business.state,
            "pincode": business.pincode,
            "phone": business.phone,
            "email": business.email
        }
        updated_business = await self.repo.update(business, **update_data.model_dump(exclude_unset=True))
        # Capture after values
        after_values = {
            "business_name": updated_business.business_name,
            "gstin": updated_business.gstin,
            "address": updated_business.address,
            "city": updated_business.city,
            "state": updated_business.state,
            "pincode": updated_business.pincode,
            "phone": updated_business.phone,
            "email": updated_business.email
        }
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessProfile",
            entity_id=business_id,
            action=AuditAction.UPDATE,
            before_values=before_values,
            after_values=after_values
        )
        return updated_business

    async def deactivate_business(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> BusinessProfile:
        from sqlalchemy import select, func
        from app.models.invoice import Invoice
        from app.models.customer import Customer
        from app.models.product import Product

        business = await self.get_business_by_id(user_id, business_id)

        # Safety Check: Prevent deletion if active child records exist
        inv_stmt = select(func.count(Invoice.id)).where(Invoice.business_id == business_id, Invoice.is_active == True)
        inv_count = (await self.repo.session.execute(inv_stmt)).scalar() or 0

        cust_stmt = select(func.count(Customer.id)).where(Customer.business_id == business_id, Customer.is_active == True)
        cust_count = (await self.repo.session.execute(cust_stmt)).scalar() or 0

        prod_stmt = select(func.count(Product.id)).where(Product.business_id == business_id, Product.is_active == True)
        prod_count = (await self.repo.session.execute(prod_stmt)).scalar() or 0

        if inv_count > 0 or cust_count > 0 or prod_count > 0:
            details = []
            if inv_count > 0: details.append(f"{inv_count} invoice(s)")
            if cust_count > 0: details.append(f"{cust_count} customer(s)")
            if prod_count > 0: details.append(f"{prod_count} product(s)")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete business. Active records exist: {', '.join(details)}. Please clear or archive dependent items first."
            )

        deactivated_business = await self.repo.deactivate(business)
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="BusinessProfile",
            entity_id=business_id,
            action=AuditAction.DELETE,
            before_values={"is_active": True},
            after_values={"is_active": False}
        )
        return deactivated_business

class BusinessMemberService:
    def __init__(self, session: AsyncSession):
        self.repo = BusinessMemberRepository(session)
