
import uuid
from typing import List, Tuple, Optional
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.invoice import Invoice, InvoiceItem, InvoiceStatus, PaymentStatus, Payment, PaymentMethod
from app.models.business import BusinessProfile
from app.models.customer import Customer
from app.models.inventory import StockMovement, InventoryTransaction
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceItemCreate, PaymentCreate, InvoiceCancel
from app.repositories.invoice import InvoiceRepository, PaymentRepository
from app.repositories.customer import CustomerRepository
from app.repositories.product import ProductRepository
from app.repositories.business import BusinessMemberRepository, BusinessProfileRepository
from app.services.inventory import InventoryService
from app.schemas.inventory import StockOut
from app.utils.invoice_calculator import InvoiceCalculator
from app.services.audit_log import AuditLogService
from app.models.audit_log import AuditAction


class InvoiceService:
    def __init__(self, session: AsyncSession):
        self.invoice_repo = InvoiceRepository(session)
        self.payment_repo = PaymentRepository(session)
        self.customer_repo = CustomerRepository(session)
        self.product_repo = ProductRepository(session)
        self.member_repo = BusinessMemberRepository(session)
        self.business_repo = BusinessProfileRepository(session)
        self.inventory_service = InventoryService(session)
        self.audit_service = AuditLogService(session)
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

    async def _get_business_and_customer(
        self, business_id: uuid.UUID, customer_id: uuid.UUID
    ) -> Tuple[BusinessProfile, Customer]:
        business = await self.business_repo.get_by_id(business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

        customer = await self.customer_repo.get_by_business_and_id(business_id, customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        return business, customer

    async def _prepare_items_for_calculation(
        self, business_id: uuid.UUID, items_data: List[InvoiceItemCreate]
    ) -> List[dict]:
        prepared_items = []
        for item_data in items_data:
            # Validate product
            product = await self.product_repo.get_by_business_and_id(business_id, item_data.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {item_data.product_id} not found"
                )

            # Use product's gst rate if not provided
            gst_rate = item_data.gst_rate or product.gst_rate or 0.0

            prepared_items.append({
                "product_id": str(item_data.product_id),
                "quantity": item_data.quantity,
                "unit_price": item_data.unit_price,
                "discount": item_data.discount or 0.0,
                "gst_rate": gst_rate
            })
        return prepared_items

    async def _generate_invoice_number(
        self, business_id: uuid.UUID
    ) -> str:
        # Concurrency-safe invoice number generation
        # Get the latest invoice number with FOR UPDATE to prevent race conditions
        last_invoice = await self.invoice_repo.get_latest_invoice_for_update(business_id)
        
        if not last_invoice:
            return "INV-00001"
        
        # Extract numeric part
        try:
            parts = last_invoice.invoice_number.split("-")
            last_num = int(parts[-1])
            new_num = last_num + 1
            return f"INV-{new_num:05d}"
        except Exception:
            return "INV-00001"

    async def _reverse_invoice_stock(
        self,
        invoice: Invoice,
        user_id: uuid.UUID,
        business_id: uuid.UUID
    ) -> None:
        # Reverse stock for each invoice item
        for item in invoice.items:
            # Get product with FOR UPDATE
            product = await self.inventory_service.get_product_and_validate_access(
                user_id, business_id, item.product_id, for_update=True
            )
            previous_stock = product.current_stock
            new_stock = previous_stock + item.quantity

            # Create SALES_RETURN transaction
            transaction = InventoryTransaction(
                business_id=business_id,
                product_id=item.product_id,
                transaction_type=StockMovement.SALES_RETURN,
                quantity=item.quantity,
                previous_stock=previous_stock,
                new_stock=new_stock,
                reference_type="invoice_cancellation",
                reference_id=invoice.id,
                remarks=f"Invoice {invoice.invoice_number} cancelled",
                created_by=user_id
            )
            self.session.add(transaction)
            product.current_stock = new_stock

    async def create_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_data: InvoiceCreate
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        business, customer = await self._get_business_and_customer(business_id, invoice_data.customer_id)

        # Generate invoice number (concurrency-safe)
        invoice_number = await self._generate_invoice_number(business_id)

        # Prepare items for calculation
        prepared_items = await self._prepare_items_for_calculation(business_id, invoice_data.items)

        # Calculate invoice totals using InvoiceCalculator
        invoice_calc = InvoiceCalculator.calculate_invoice(
            items_data=prepared_items,
            discount_amount=Decimal(str(invoice_data.discount_amount)) if invoice_data.discount_amount else None,
            business_state=business.state,
            customer_state=customer.state
        )

        # Create invoice
        invoice = Invoice(
            business_id=business_id,
            customer_id=invoice_data.customer_id,
            invoice_number=invoice_number,
            invoice_date=invoice_data.invoice_date,
            due_date=invoice_data.due_date,
            subtotal=invoice_calc.subtotal,
            discount_amount=invoice_calc.discount_amount or None,
            taxable_amount=invoice_calc.taxable_amount,
            cgst_amount=invoice_calc.cgst_amount,
            sgst_amount=invoice_calc.sgst_amount,
            igst_amount=invoice_calc.igst_amount,
            total_tax=invoice_calc.total_tax,
            round_off=invoice_calc.round_off or None,
            grand_total=invoice_calc.grand_total,
            outstanding_balance=invoice_calc.grand_total,
            payment_status=PaymentStatus.UNPAID,
            status=InvoiceStatus.ISSUED,
            notes=invoice_data.notes,
            created_by=user_id
        )

        self.session.add(invoice)
        await self.session.flush()

        # Create invoice items
        for calc_item in invoice_calc.items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=uuid.UUID(calc_item.product_id),
                quantity=calc_item.quantity, unit_price=calc_item.unit_price,
                discount=calc_item.discount or None, gst_rate=calc_item.gst_rate or None,
                taxable_amount=calc_item.taxable_amount, tax_amount=calc_item.tax_amount or None,
                total=calc_item.total
            )
            self.session.add(invoice_item)

        # Inventory and invoice are flushed within the request transaction; a
        # stock failure rolls back the invoice and its items together.
        for item in invoice_calc.items:
            await self.inventory_service.stock_out(
                user_id=user_id,
                business_id=business_id,
                data=StockOut(
                    product_id=uuid.UUID(item.product_id),
                    quantity=item.quantity,
                    reference_type="invoice",
                    reference_id=invoice.id,
                    remarks=f"Invoice {invoice_number}"
                )
            )

        await self.session.flush()
        await self.session.refresh(invoice, ["items", "payments"])
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Invoice",
            entity_id=invoice.id,
            action=AuditAction.CREATE,
            after_values={"invoice_number": invoice.invoice_number, "customer_id": str(invoice.customer_id), "grand_total": str(invoice.grand_total)}
        )
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

        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.VOID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update a cancelled or void invoice"
            )

        business, customer = await self._get_business_and_customer(business_id, invoice.customer_id)

        # If items are updated, recalculate everything
        if update_data.items:
            # Get new customer if changed
            if update_data.customer_id:
                business, customer = await self._get_business_and_customer(business_id, update_data.customer_id)
            
            prepared_items = await self._prepare_items_for_calculation(business_id, update_data.items)
            invoice_calc = InvoiceCalculator.calculate_invoice(
                items_data=prepared_items,
                discount_amount=Decimal(str(update_data.discount_amount)) if update_data.discount_amount is not None else Decimal(str(invoice.discount_amount)) if invoice.discount_amount else None,
                business_state=business.state,
                customer_state=customer.state
            )

            # Update invoice fields
            invoice.subtotal = invoice_calc.subtotal
            invoice.discount_amount = invoice_calc.discount_amount or None
            invoice.taxable_amount = invoice_calc.taxable_amount
            invoice.cgst_amount = invoice_calc.cgst_amount
            invoice.sgst_amount = invoice_calc.sgst_amount
            invoice.igst_amount = invoice_calc.igst_amount
            invoice.total_tax = invoice_calc.total_tax
            invoice.round_off = invoice_calc.round_off or None
            invoice.grand_total = invoice_calc.grand_total
            invoice.outstanding_balance = invoice_calc.grand_total
            invoice.updated_by = user_id

            # Remove old items
            for item in invoice.items:
                await self.session.delete(item)

            # Add new items
            for calc_item in invoice_calc.items:
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    product_id=uuid.UUID(calc_item.product_id),
                    quantity=calc_item.quantity, unit_price=calc_item.unit_price,
                    discount=calc_item.discount or None, gst_rate=calc_item.gst_rate or None,
                    taxable_amount=calc_item.taxable_amount, tax_amount=calc_item.tax_amount or None,
                    total=calc_item.total
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
                # Recalculate everything if discount changes
                prepared_items = [
                    {
                        "product_id": str(item.product_id),
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "discount": item.discount or 0.0,
                        "gst_rate": item.gst_rate or 0.0
                    } for item in invoice.items
                ]
                invoice_calc = InvoiceCalculator.calculate_invoice(
                    items_data=prepared_items,
                    discount_amount=Decimal(str(update_data.discount_amount)),
                    business_state=business.state,
                    customer_state=customer.state
                )
                invoice.subtotal = invoice_calc.subtotal
                invoice.discount_amount = invoice_calc.discount_amount or None
                invoice.taxable_amount = invoice_calc.taxable_amount
                invoice.cgst_amount = invoice_calc.cgst_amount
                invoice.sgst_amount = invoice_calc.sgst_amount
                invoice.igst_amount = invoice_calc.igst_amount
                invoice.total_tax = invoice_calc.total_tax
                invoice.round_off = invoice_calc.round_off or None
                invoice.grand_total = invoice_calc.grand_total
                invoice.outstanding_balance = invoice_calc.grand_total
            if update_data.notes is not None:
                invoice.notes = update_data.notes
            invoice.updated_by = user_id

        await self.session.flush()
        await self.session.refresh(invoice, ["items", "payments"])

        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Invoice",
            entity_id=invoice_id,
            action=AuditAction.UPDATE,
            before_values={"invoice_number": invoice.invoice_number, "grand_total": str(invoice.grand_total)},
            after_values={"invoice_number": invoice.invoice_number, "grand_total": str(invoice.grand_total)}
        )

        return invoice

    async def cancel_invoice(
        self, user_id: uuid.UUID, business_id: uuid.UUID, invoice_id: uuid.UUID, cancel_data: InvoiceCancel
    ) -> Invoice:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.get_invoice(user_id, business_id, invoice_id)

        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.VOID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice is already cancelled or void"
            )

        # Reverse inventory
        await self._reverse_invoice_stock(invoice, user_id, business_id)

        # Update invoice status
        invoice.status = InvoiceStatus.CANCELLED
        invoice.cancelled_by = user_id
        invoice.cancelled_at = datetime.now(timezone.utc)
        invoice.cancellation_reason = cancel_data.reason
        invoice.updated_by = user_id

        await self.session.flush()
        await self.session.refresh(invoice, ["items", "payments"])

        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Invoice",
            entity_id=invoice_id,
            action=AuditAction.DELETE,
            before_values={"invoice_number": invoice.invoice_number, "status": "ISSUED"},
            after_values={"invoice_number": invoice.invoice_number, "status": "CANCELLED", "reason": cancel_data.reason}
        )

        return invoice

    async def record_payment(
        self, user_id: uuid.UUID, business_id: uuid.UUID, payment_data: PaymentCreate
    ) -> Payment:
        await self._ensure_business_access(user_id, business_id)
        invoice = await self.get_invoice(user_id, business_id, payment_data.invoice_id)

        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.VOID]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record payment for a cancelled or void invoice"
            )

        if invoice.outstanding_balance <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invoice is already fully paid"
            )

        payment_amount = Decimal(str(payment_data.amount))
        if payment_amount > invoice.outstanding_balance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment exceeds outstanding balance")

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

        # Update payment status and invoice status
        if invoice.outstanding_balance <= 0:
            invoice.payment_status = PaymentStatus.PAID
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.payment_status = PaymentStatus.PARTIALLY_PAID
            invoice.status = InvoiceStatus.PARTIALLY_PAID

        await self.session.flush()
        await self.session.refresh(payment)
        # Audit log
        await self.audit_service.log_event(
            user_id=user_id,
            business_id=business_id,
            entity_type="Payment",
            entity_id=payment.id,
            action=AuditAction.CREATE,
            after_values={"invoice_id": str(payment.invoice_id), "amount": str(payment.amount), "payment_method": payment.payment_method.value}
        )
        return payment
