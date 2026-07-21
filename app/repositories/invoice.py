
import uuid
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.invoice import Invoice, InvoiceStatus, PaymentStatus, Payment


class InvoiceRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Invoice)

    async def list_by_business(
        self,
        business_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[InvoiceStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        search_query: Optional[str] = None,
        customer_id: Optional[uuid.UUID] = None,
        invoice_date_from: Optional[datetime] = None,
        invoice_date_to: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Tuple[List[Invoice], int]:
        query = select(Invoice).where(Invoice.business_id == business_id).options(
            selectinload(Invoice.items)
        )
        if status:
            query = query.where(Invoice.status == status)
        if payment_status:
            query = query.where(Invoice.payment_status == payment_status)
        if customer_id:
            query = query.where(Invoice.customer_id == customer_id)
        if invoice_date_from:
            query = query.where(Invoice.invoice_date >= invoice_date_from)
        if invoice_date_to:
            query = query.where(Invoice.invoice_date <= invoice_date_to)
        if min_amount is not None:
            query = query.where(Invoice.grand_total >= min_amount)
        if max_amount is not None:
            query = query.where(Invoice.grand_total <= max_amount)
        if search_query:
            query = query.where(or_(
                Invoice.invoice_number.ilike(f"%{search_query}%"),
            ))

        if sort_by:
            sort_col = None
            if sort_by == "invoice_date":
                sort_col = Invoice.invoice_date
            elif sort_by == "invoice_number":
                sort_col = Invoice.invoice_number
            elif sort_by == "grand_total":
                sort_col = Invoice.grand_total
            elif sort_by == "created_at":
                sort_col = Invoice.created_at
            elif sort_by == "due_date":
                sort_col = Invoice.due_date

            if sort_col:
                if sort_order == "desc":
                    query = query.order_by(desc(sort_col))
                else:
                    query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(Invoice.created_at))

        count_query = select(func.count(Invoice.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_by_business_and_id(
        self, business_id: uuid.UUID, invoice_id: uuid.UUID, include_inactive: bool = False
    ) -> Optional[Invoice]:
        query = select(Invoice).where(
            and_(
                Invoice.id == invoice_id,
                Invoice.business_id == business_id
            )
        ).options(selectinload(Invoice.items), selectinload(Invoice.payments))
        if not include_inactive:
            query = query.where(Invoice.is_active == True)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_business_and_invoice_number(
        self, business_id: uuid.UUID, invoice_number: str
    ) -> Optional[Invoice]:
        result = await self.session.execute(
            select(Invoice).where(
                and_(
                    Invoice.invoice_number == invoice_number,
                    Invoice.business_id == business_id,
                    Invoice.is_active == True
                )
            )
        )
        return result.scalars().first()

    async def get_next_invoice_number(self, business_id: uuid.UUID) -> str:
        # Simple implementation: get last invoice number, increment
        # TODO: Add business-specific prefix from business profile later
        result = await self.session.execute(
            select(Invoice.invoice_number).where(
                Invoice.business_id == business_id
            ).order_by(desc(Invoice.created_at)).limit(1)
        )
        last_number_str = result.scalar()
        if not last_number_str:
            return "INV-00001"
        # Extract numeric part
        try:
            parts = last_number_str.split("-")
            last_num = int(parts[-1])
            new_num = last_num + 1
            return f"INV-{new_num:05d}"
        except Exception:
            return "INV-00001"


class PaymentRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Payment)

    async def list_by_invoice(
        self,
        business_id: uuid.UUID,
        invoice_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Payment], int]:
        query = select(Payment).where(
            and_(Payment.business_id == business_id, Payment.invoice_id == invoice_id)
        )
        count_query = select(func.count(Payment.id)).where(query.whereclause)
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.offset(skip).limit(limit).order_by(desc(Payment.created_at))
        result = await self.session.execute(query)
        return list(result.scalars().all()), total
