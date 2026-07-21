
import uuid
from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, PaymentStatus, Payment, PaymentMethod
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate, PaymentCreate
from app.repositories.invoice import InvoiceRepository, PaymentRepository
from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.business import BusinessMemberRepository
from app.services.inventory import InventoryService
from app.schemas.inventory import StockOut


class InvoiceService:
    def __init__(self, session: AsyncSession):
        self.invoice_repo = InvoiceRepository(session)
        self.payment_repo = PaymentRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.product_repo = ProductRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.inventory_service = InventoryService(session)
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

    async def _validate_customer(
        self, business_id: uuid.UUID, customer_id: uuid.UUID
    ) -> None:
        customer = await self.customer_repo.get_by_business_and_id(business_id, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

    async def _calculate_item(
        self, business_id: uuid.UUID, item_data: InvoiceItemCreate
    ) -> Tuple[dict, float]:
        # Validate product
        product = await self.product_repo.get_by_business_and_id(business_id, item_data.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found"
            )

        # Use product's gst rate if not provided
        gst_rate = item_data.gst_rate or product.gst_rate or 0.0

        # Calculate item values
        line_total = item_data.quantity * item_data.unit_price
        discount = item_data.discount or 0.0
        taxable_amount = line_total - discount
        tax_amount = (taxable_amount * gst_rate) / 100 if gst_rate else 0.0
        total = taxable_amount + tax_amount

        item_dict = {
            "product_id": item_data.product_id,
            "quantity": item_data.quantity,
            "unit_price": item_data.unit_price,
            "discount": discount,
            "gst_rate": gst_rate,
            "taxable_amount": taxable_amount,
            "tax_amount": tax_amount,
            "total": total
        }

        return item_dict, tax_amount

    async def _calculate_invoice(
        self, business_id: uuid.UUID, items_data: List[InvoiceItemCreate], discount_amount: Optional[float] = None
    ) -> dict:
        subtotal = 0.0
        total_tax = 0.0
        calculated_items = []

        for item_data in items_data:
            item_dict, item_tax = await self._calculate_item(business_id, item_data)
            calculated_items.append(item_dict)
            subtotal += item_dict["taxable_amount"] + (item_dict["discount"] or 0.0)
            total_tax += item_tax

        # Apply invoice-level discount
        discount_amount = discount_amount or 0.0
        taxable_amount = subtotal - discount_amount
        # For now, assume GST is already calculated on items, so CGST/SGST/IGST is split equally if needed
        # For simplicity, let's split total_tax into CGST and SGST each half
        cgst_amount = total_tax / 2 if total_tax > 0 else None
        sgst_amount = total_tax / 2 if total_tax > 0 else None
        igst_amount = None  # TODO: Implement based on business and customer location

        # Calculate grand total and round off
        total_before_round = taxable_amount + total_tax
        grand_total = round(total_before_round, 2)
        round_off = grand_total - total_before_round

        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "taxable_amount": taxable_amount,
            "cgst_amount": cgst_amount,
            "sgst_amount": sgst_amount,
            "igst_amount": igst_amount,
            "total_tax": total_tax,
            "round_off": round_off,
            "grand_total": grand_total,
            "items": calculated_items
        }

    async def create_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_data: InvoiceCreate
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        await self._validate_customer(business_id, invoice_data.customer_id)

        # Generate invoice number
        invoice_number = await self.invoice_repo.get_next_invoice_number(business_id)

        # Calculate invoice totals
        invoice_calc = await self._calculate_invoice(
            business_id, invoice_data.items, invoice_data.discount_amount
        )

        # Create invoice
        invoice = Invoice(
            business_id=business_id,
            customer_id=invoice_data.customer_id,
            invoice_number=invoice_number,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            subtotal=invoice_calc["subtotal"],
            discount_amount=invoice_calc["discount_amount"],
            taxable_amount=invoice_calc["taxable_amount"],
            cgst_amount=invoice_calc["cgst_amount"],
            sgst_amount=invoice_calc["sgst_amount"],
            igst_amount=invoice_calc["igst_amount"],
            total_tax=invoice_calc["total_tax"],
            round_off=invoice_calc["round_off"],
            grand_total=invoice_calc["grand_total"],
            outstanding_balance=invoice_calc["grand_total"],
            payment_status=PaymentStatus.UNPAID,
            status=InvoiceStatus.UNPAID,
            notes=invoice_data.notes,
            created_by=user_id
        )

        self.session.add(invoice)
        await self.session.flush()

        # Create invoice items
        for item_dict in invoice_calc["items"]:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                **item_dict
            )
            self.session.add(invoice_item)

            # Deduct inventory
            await self.inventory_service.stock_out(
                user_id=user_id,
                business_id=business_id,
                data=StockOut(
                    product_id=item_dict["product_id"],
                    quantity=item_dict["quantity"],
                    reference_type="invoice",
                    reference_id=invoice.id,
                    remarks=f"Invoice {invoice_number}"
                )
            )

        await self.session.commit()
        await self.session.refresh(invoice, ["items"])

        return invoice

    async def get_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_id: uuid.UUID
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.invoice_repo.get_by_business_and_id(business_id, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice

    async def list_invoices(
        self,
        user_id: uuid.UUID,
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
        await self._ensure_business_access(user_id, business_id)
        return await self.invoice_repo.list_by_business(
            business_id, skip, limit, status, payment_status, search_query, customer_id, 
            invoice_date_from, invoice_date_to, min_amount, max_amount, sort_by, sort_order
        )

    async def update_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_id: uuid.UUID, update_data: InvoiceUpdate
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.get_invoice(user_id, business_id, invoice_id)

        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled invoice"
            )

        # Validate customer if updated
        if update_data.customer_id:
            await self._validate_customer(business_id, update_data.customer_id)

        # If items are updated, recalculate everything
        if update_data.items:
            invoice_calc = await self._calculate_invoice(
                business_id, update_data.items, update_data.discount_amount or invoice.discount_amount
            )

            # Update invoice fields
            for key, value in invoice_calc.items():
                if key != "items":
                    setattr(invoice, key, value)
            invoice.outstanding_balance = invoice_calc["grand_total"]  # Reset outstanding balance when items updated

            # Remove old items
            for item in invoice.items:
                await self.session.delete(item)

            # Add new items
            for item_dict in invoice_calc["items"]:
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    **item_dict
                )
                self.session.add(invoice_item)
        else:
            # Update other fields if provided
            if update_data.customer_id:
                invoice.customer_id = update_data.customer_id
            if update_data.invoice_date:
                invoice.invoice_date = update_data.invoice_date
            if update_data.due_date:
                invoice.due_date = update_data.due_date
            if update_data.discount_amount is not None:
                # TODO: Recalculate everything if discount changes
                invoice.discount_amount = update_data.discount_amount
            if update_data.notes is not None:
                invoice.notes = update_data.notes

        await self.session.commit()
        await self.session.refresh(invoice, ["items"])

        return invoice

    async def cancel_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_id: uuid.UUID
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.get_invoice(user_id, business_id, invoice_id)

        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice is already cancelled"
            )

        # TODO: Reverse inventory transactions
        # For now, just mark as cancelled
        invoice.status = InvoiceStatus.CANCELLED
        invoice.payment_status = PaymentStatus.UNPAID

        await self.session.commit()
        await self.session.refresh(invoice, ["items"])

        return invoice

    async def record_payment(
        self, user_id: uuid.UUID, business_id: uuid.UUID, payment_data: PaymentCreate
    ) -> Payment:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.get_invoice(user_id, business_id, payment_data.invoice_id)

        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record payment for a cancelled invoice"
            )

        if invoice.outstanding_balance <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice is already fully paid"
            )

        payment_amount = min(payment_data.amount, invoice.outstanding_balance)

        # Create payment record
        payment = Payment(
            business_id=business_id,
            invoice_id=invoice.id,
            amount=payment_amount,
            payment_method=payment_data.payment_method,
            transaction_id=payment_data.transaction_id,
            notes=payment_data.notes,
            created_by=user_id
        )
        self.session.add(payment)
        await self.session.flush()

        # Update invoice outstanding balance
        invoice.outstanding_balance -= payment_amount

        # Update payment status
        if invoice.outstanding_balance <= 0:
            invoice.payment_status = PaymentStatus.PAID
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.payment_status = PaymentStatus.PARTIALLY_PAID

        await self.session.commit()
        await self.session.refresh(payment)

        return payment
