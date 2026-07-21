
import uuid
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import (
    Invoice, InvoiceItem, Payment, Customer, Supplier, Product,
    InventoryTransaction, StockMovement, InvoiceStatus, PaymentStatus
)
from app.repositories.business import BusinessMemberRepository
from app.schemas.reports import (
    DashboardSummary,
    TopSellingProductItem,
    RecentInvoiceItem,
    DashboardResponse,
    SalesReportItem,
    SalesReportResponse,
    TopCustomerItem,
    OutstandingCustomerItem,
    CustomerPurchaseHistoryItem,
    CustomerReportsResponse,
    ProductSalesItem,
    StockValueItem,
    ProductReportsResponse,
    PaymentMethodDistributionItem,
    PaymentReportsResponse,
    InventoryValuationItem,
    StockMovementReportItem,
    InventoryReportsResponse
)


class ReportingService:
    def __init__(self, session: AsyncSession):
        self.session = session
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

    async def get_dashboard(
        self, user_id: uuid.UUID, business_id: uuid.UUID
    ) -> DashboardResponse:
        await self._ensure_business_access(user_id, business_id)
        now = datetime.now(timezone.utc)
        
        # Calculate summary metrics
        summary = await self._get_dashboard_summary(business_id, now)
        
        # Get top selling products
        top_selling = await self._get_top_selling_products(business_id, limit=5)
        
        # Get recent invoices
        recent_invoices = await self._get_recent_invoices(business_id, limit=10)
        
        return DashboardResponse(
            summary=summary,
            top_selling_products=top_selling,
            recent_invoices=recent_invoices
        )

    async def _get_dashboard_summary(
        self, business_id: uuid.UUID, now: datetime
    ) -> DashboardSummary:
        # Date ranges
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        year_start = today_start.replace(month=1, day=1)

        # Sales metrics
        sales_today = await self._get_sales_for_period(business_id, today_start, now)
        sales_this_week = await self._get_sales_for_period(business_id, week_start, now)
        sales_this_month = await self._get_sales_for_period(business_id, month_start, now)
        sales_this_year = await self._get_sales_for_period(business_id, year_start, now)
        
        # Outstanding receivables
        outstanding_query = select(func.sum(Invoice.outstanding_balance)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.outstanding_balance > 0,
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID,
                Invoice.is_active == True
            )
        )
        outstanding_result = await self.session.execute(outstanding_query)
        outstanding_receivables = outstanding_result.scalar() or 0.0

        # Customer/supplier/product counts
        customer_count_query = select(func.count(Customer.id)).where(
            and_(Customer.business_id == business_id, Customer.is_active == True)
        )
        customer_count_result = await self.session.execute(customer_count_query)
        total_customers = customer_count_result.scalar() or 0

        supplier_count_query = select(func.count(Supplier.id)).where(
            and_(Supplier.business_id == business_id, Supplier.is_active == True)
        )
        supplier_count_result = await self.session.execute(supplier_count_query)
        total_suppliers = supplier_count_result.scalar() or 0

        product_count_query = select(func.count(Product.id)).where(
            and_(Product.business_id == business_id, Product.is_active == True)
        )
        product_count_result = await self.session.execute(product_count_query)
        total_products = product_count_result.scalar() or 0

        active_product_query = select(func.count(Product.id)).where(
            and_(Product.business_id == business_id, Product.is_active == True, Product.status == "active")
        )
        active_product_result = await self.session.execute(active_product_query)
        active_products = active_product_result.scalar() or 0

        out_of_stock_query = select(func.count(Product.id)).where(
            and_(Product.business_id == business_id, Product.is_active == True, Product.current_stock <= 0)
        )
        out_of_stock_result = await self.session.execute(out_of_stock_query)
        out_of_stock_products = out_of_stock_result.scalar() or 0

        low_stock_query = select(func.count(Product.id)).where(
            and_(
                Product.business_id == business_id,
                Product.is_active == True,
                Product.minimum_stock != None,
                Product.current_stock <= Product.minimum_stock,
                Product.current_stock > 0
            )
        )
        low_stock_result = await self.session.execute(low_stock_query)
        low_stock_products = low_stock_result.scalar() or 0

        # Inventory value
        inventory_value_query = select(func.sum(Product.current_stock * Product.selling_price)).where(
            and_(Product.business_id == business_id, Product.is_active == True)
        )
        inventory_value_result = await self.session.execute(inventory_value_query)
        inventory_value = inventory_value_result.scalar() or 0.0

        # Invoice counts
        paid_invoice_query = select(func.count(Invoice.id)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.payment_status == PaymentStatus.PAID
            )
        )
        paid_invoice_result = await self.session.execute(paid_invoice_query)
        paid_invoices = paid_invoice_result.scalar() or 0

        pending_invoice_query = select(func.count(Invoice.id)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.payment_status.in_([PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID]),
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        )
        pending_invoice_result = await self.session.execute(pending_invoice_query)
        pending_invoices = pending_invoice_result.scalar() or 0

        cancelled_invoice_query = select(func.count(Invoice.id)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.status.in_([InvoiceStatus.CANCELLED, InvoiceStatus.VOID])
            )
        )
        cancelled_invoice_result = await self.session.execute(cancelled_invoice_query)
        cancelled_invoices = cancelled_invoice_result.scalar() or 0

        # Total revenue and average invoice value
        total_revenue_query = select(func.sum(Invoice.grand_total)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        )
        total_revenue_result = await self.session.execute(total_revenue_query)
        total_revenue = total_revenue_result.scalar() or 0.0

        avg_invoice_query = select(func.avg(Invoice.grand_total)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        )
        avg_invoice_result = await self.session.execute(avg_invoice_query)
        average_invoice_value = avg_invoice_result.scalar() or 0.0

        return DashboardSummary(
            sales_today=float(sales_today),
            sales_this_week=float(sales_this_week),
            sales_this_month=float(sales_this_month),
            sales_this_year=float(sales_this_year),
            outstanding_receivables=float(outstanding_receivables),
            total_customers=total_customers,
            total_suppliers=total_suppliers,
            total_products=total_products,
            active_products=active_products,
            out_of_stock_products=out_of_stock_products,
            low_stock_products=low_stock_products,
            inventory_value=float(inventory_value),
            paid_invoices=paid_invoices,
            pending_invoices=pending_invoices,
            cancelled_invoices=cancelled_invoices,
            total_revenue=float(total_revenue),
            average_invoice_value=float(average_invoice_value)
        )

    async def _get_sales_for_period(
        self, business_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> float:
        query = select(func.sum(Invoice.grand_total)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date,
                Invoice.is_active == True,
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        )
        result = await self.session.execute(query)
        return float(result.scalar() or 0.0)

    async def _get_top_selling_products(
        self, business_id: uuid.UUID, limit: int = 10
    ) -> List[TopSellingProductItem]:
        query = (
            select(
                InvoiceItem.product_id,
                Product.name.label("product_name"),
                func.sum(InvoiceItem.quantity).label("total_quantity"),
                func.sum(InvoiceItem.total).label("total_revenue")
            )
            .join(Product, InvoiceItem.product_id == Product.id)
            .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
            .where(
                and_(
                    Invoice.business_id == business_id,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .group_by(InvoiceItem.product_id, Product.name)
            .order_by(desc(func.sum(InvoiceItem.quantity)))
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            TopSellingProductItem(
                product_id=row.product_id,
                product_name=row.product_name,
                quantity_sold=float(row.total_quantity),
                total_revenue=float(row.total_revenue)
            ) for row in rows
        ]

    async def _get_recent_invoices(
        self, business_id: uuid.UUID, limit: int = 10
    ) -> List[RecentInvoiceItem]:
        query = (
            select(
                Invoice.id.label("invoice_id"),
                Invoice.invoice_number,
                Invoice.customer_id,
                Customer.name.label("customer_name"),
                Invoice.grand_total.label("total_amount"),
                Invoice.status,
                Invoice.invoice_date
            )
            .join(Customer, Invoice.customer_id == Customer.id)
            .where(
                and_(
                    Invoice.business_id == business_id,
                    Invoice.is_active == True
                )
            )
            .order_by(desc(Invoice.invoice_date))
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            RecentInvoiceItem(
                invoice_id=row.invoice_id,
                invoice_number=row.invoice_number,
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                total_amount=float(row.total_amount),
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                invoice_date=row.invoice_date
            ) for row in rows
        ]

    # Sales Reports
    async def get_sales_report(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        group_by: str = "day",
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> SalesReportResponse:
        await self._ensure_business_access(user_id, business_id)
        
        now = datetime.now(timezone.utc)
        if not date_from:
            if group_by == "day":
                date_from = now - timedelta(days=30)
            elif group_by == "week":
                date_from = now - timedelta(weeks=12)
            elif group_by == "month":
                date_from = now - timedelta(days=365)
            else:  # year
                date_from = now - timedelta(days=3*365)
        if not date_to:
            date_to = now

        # Build date truncation expression based on group_by
        if group_by == "day":
            date_expr = func.date_trunc('day', Invoice.invoice_date)
        elif group_by == "week":
            date_expr = func.date_trunc('week', Invoice.invoice_date)
        elif group_by == "month":
            date_expr = func.date_trunc('month', Invoice.invoice_date)
        else:  # year
            date_expr = func.date_trunc('year', Invoice.invoice_date)

        query = (
            select(
                date_expr.label("period"),
                func.sum(Invoice.grand_total).label("total_sales"),
                func.count(Invoice.id).label("total_invoices"),
                func.avg(Invoice.grand_total).label("average_invoice_value")
            )
            .where(
                and_(
                    Invoice.business_id == business_id,
                    Invoice.invoice_date >= date_from,
                    Invoice.invoice_date <= date_to,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .group_by(date_expr)
            .order_by(date_expr)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()

        items = []
        for row in rows:
            # Format period string
            if group_by == "day":
                period_str = row.period.strftime("%Y-%m-%d")
            elif group_by == "week":
                period_str = row.period.strftime("%Y-W%W")
            elif group_by == "month":
                period_str = row.period.strftime("%Y-%m")
            else:  # year
                period_str = row.period.strftime("%Y")

            items.append(SalesReportItem(
                period=period_str,
                total_sales=float(row.total_sales),
                total_invoices=row.total_invoices,
                average_invoice_value=float(row.average_invoice_value)
            ))

        return SalesReportResponse(items=items)

    # Customer Reports
    async def get_customer_reports(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        report_type: Optional[str] = None,
        customer_id: Optional[uuid.UUID] = None
    ) -> CustomerReportsResponse:
        await self._ensure_business_access(user_id, business_id)
        
        response = CustomerReportsResponse()
        
        if not report_type or report_type == "top":
            response.top_customers = await self._get_top_customers(business_id)
        if not report_type or report_type == "highest_spending":
            response.highest_spending_customers = await self._get_highest_spending_customers(business_id)
        if not report_type or report_type == "outstanding":
            response.outstanding_customers = await self._get_outstanding_customers(business_id)
        if report_type == "purchase_history" and customer_id:
            response.customer_purchase_history = await self._get_customer_purchase_history(business_id, customer_id)
        if not report_type or report_type == "revenue":
            response.customer_revenue = await self._get_customer_revenue(business_id)
            
        return response

    async def _get_top_customers(self, business_id: uuid.UUID) -> List[TopCustomerItem]:
        query = (
            select(
                Customer.id.label("customer_id"),
                Customer.name.label("customer_name"),
                func.count(Invoice.id).label("total_purchases"),
                func.sum(Invoice.grand_total).label("total_revenue")
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                and_(
                    Customer.business_id == business_id,
                    Customer.is_active == True,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .group_by(Customer.id, Customer.name)
            .order_by(desc(func.count(Invoice.id)))
            .limit(10)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            TopCustomerItem(
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                total_purchases=row.total_purchases,
                total_revenue=float(row.total_revenue)
            ) for row in rows
        ]

    async def _get_highest_spending_customers(self, business_id: uuid.UUID) -> List[TopCustomerItem]:
        query = (
            select(
                Customer.id.label("customer_id"),
                Customer.name.label("customer_name"),
                func.count(Invoice.id).label("total_purchases"),
                func.sum(Invoice.grand_total).label("total_revenue")
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                and_(
                    Customer.business_id == business_id,
                    Customer.is_active == True,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .group_by(Customer.id, Customer.name)
            .order_by(desc(func.sum(Invoice.grand_total)))
            .limit(10)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            TopCustomerItem(
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                total_purchases=row.total_purchases,
                total_revenue=float(row.total_revenue)
            ) for row in rows
        ]

    async def _get_outstanding_customers(self, business_id: uuid.UUID) -> List[OutstandingCustomerItem]:
        query = (
            select(
                Customer.id.label("customer_id"),
                Customer.name.label("customer_name"),
                func.sum(Invoice.outstanding_balance).label("outstanding_balance")
            )
            .join(Invoice, Customer.id == Invoice.customer_id)
            .where(
                and_(
                    Customer.business_id == business_id,
                    Customer.is_active == True,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID,
                    Invoice.outstanding_balance > 0
                )
            )
            .group_by(Customer.id, Customer.name)
            .order_by(desc(func.sum(Invoice.outstanding_balance)))
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            OutstandingCustomerItem(
                customer_id=row.customer_id,
                customer_name=row.customer_name,
                outstanding_balance=float(row.outstanding_balance)
            ) for row in rows
        ]

    async def _get_customer_purchase_history(
        self, business_id: uuid.UUID, customer_id: uuid.UUID
    ) -> List[CustomerPurchaseHistoryItem]:
        query = (
            select(
                Invoice.id.label("invoice_id"),
                Invoice.invoice_number,
                Invoice.invoice_date,
                Invoice.grand_total.label("total_amount"),
                (Invoice.grand_total - Invoice.outstanding_balance).label("paid_amount"),
                Invoice.outstanding_balance
            )
            .where(
                and_(
                    Invoice.business_id == business_id,
                    Invoice.customer_id == customer_id,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .order_by(desc(Invoice.invoice_date))
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            CustomerPurchaseHistoryItem(
                invoice_id=row.invoice_id,
                invoice_number=row.invoice_number,
                invoice_date=row.invoice_date,
                total_amount=float(row.total_amount),
                paid_amount=float(row.paid_amount),
                outstanding_balance=float(row.outstanding_balance)
            ) for row in rows
        ]

    async def _get_customer_revenue(self, business_id: uuid.UUID) -> List[TopCustomerItem]:
        # Same as highest spending
        return await self._get_highest_spending_customers(business_id)

    # Product Reports
    async def get_product_reports(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        report_type: Optional[str] = None
    ) -> ProductReportsResponse:
        await self._ensure_business_access(user_id, business_id)
        
        response = ProductReportsResponse()
        
        if not report_type or report_type == "top_selling":
            response.top_selling_products = await self._get_product_sales_report(business_id, order_by="desc")
        if not report_type or report_type == "least_selling":
            response.least_selling_products = await self._get_product_sales_report(business_id, order_by="asc")
        if not report_type or report_type == "inactive":
            response.inactive_products = await self._get_inactive_products(business_id)
        if not report_type or report_type == "stock_value":
            response.stock_value = await self._get_stock_value(business_id)
        if report_type == "current_stock":
            response.current_stock = await self._get_current_stock(business_id)
        if report_type == "stock_movement":
            response.stock_movement_summary = await self._get_stock_movement_summary(business_id)
            
        return response

    async def _get_product_sales_report(
        self, business_id: uuid.UUID, order_by: str = "desc", limit: int = 20
    ) -> List[ProductSalesItem]:
        order_expr = desc(func.sum(InvoiceItem.quantity)) if order_by == "desc" else asc(func.sum(InvoiceItem.quantity))
        query = (
            select(
                InvoiceItem.product_id,
                Product.name.label("product_name"),
                Product.sku,
                func.sum(InvoiceItem.quantity).label("quantity_sold"),
                func.sum(InvoiceItem.total).label("total_revenue")
            )
            .join(Product, InvoiceItem.product_id == Product.id)
            .join(Invoice, InvoiceItem.invoice_id == Invoice.id)
            .where(
                and_(
                    Invoice.business_id == business_id,
                    Invoice.is_active == True,
                    Invoice.status != InvoiceStatus.CANCELLED,
                    Invoice.status != InvoiceStatus.VOID
                )
            )
            .group_by(InvoiceItem.product_id, Product.name, Product.sku)
            .order_by(order_expr)
            .limit(limit)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            ProductSalesItem(
                product_id=row.product_id,
                product_name=row.product_name,
                sku=row.sku,
                quantity_sold=float(row.quantity_sold),
                total_revenue=float(row.total_revenue)
            ) for row in rows
        ]

    async def _get_inactive_products(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Product).where(
            and_(
                Product.business_id == business_id,
                Product.is_active == True,
                Product.status == "inactive"
            )
        )
        result = await self.session.execute(query)
        products = result.scalars().all()
        
        return [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku
            } for p in products
        ]

    async def _get_stock_value(self, business_id: uuid.UUID) -> List[StockValueItem]:
        query = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.current_stock,
                Product.selling_price.label("unit_price"),
                (Product.current_stock * Product.selling_price).label("total_value")
            )
            .where(
                and_(Product.business_id == business_id, Product.is_active == True)
            )
            .order_by(desc(Product.current_stock * Product.selling_price))
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            StockValueItem(
                product_id=row.product_id,
                product_name=row.product_name,
                current_stock=float(row.current_stock),
                unit_price=float(row.unit_price),
                total_value=float(row.total_value)
            ) for row in rows
        ]

    async def _get_current_stock(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Product).where(
            and_(Product.business_id == business_id, Product.is_active == True)
        )
        result = await self.session.execute(query)
        products = result.scalars().all()
        
        return [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current_stock": float(p.current_stock),
                "minimum_stock": float(p.minimum_stock) if p.minimum_stock else None
            } for p in products
        ]

    async def _get_stock_movement_summary(self, business_id: uuid.UUID) -> List[dict]:
        query = (
            select(
                InventoryTransaction.product_id,
                Product.name.label("product_name"),
                InventoryTransaction.transaction_type,
                func.sum(InventoryTransaction.quantity).label("total_quantity")
            )
            .join(Product, InventoryTransaction.product_id == Product.id)
            .where(InventoryTransaction.business_id == business_id)
            .group_by(
                InventoryTransaction.product_id,
                Product.name,
                InventoryTransaction.transaction_type
            )
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "transaction_type": row.transaction_type.value if hasattr(row.transaction_type, "value") else str(row.transaction_type),
                "total_quantity": float(row.total_quantity)
            } for row in rows
        ]

    # Payment Reports
    async def get_payment_reports(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        report_type: Optional[str] = None
    ) -> PaymentReportsResponse:
        await self._ensure_business_access(user_id, business_id)
        
        response = PaymentReportsResponse()
        
        if not report_type or report_type == "received":
            response.payments_received = await self._get_payments_received(business_id)
        if not report_type or report_type == "pending":
            response.pending_payments = await self._get_pending_payments(business_id)
        if not report_type or report_type == "overdue":
            response.overdue_payments = await self._get_overdue_payments(business_id)
        if not report_type or report_type == "distribution":
            response.payment_method_distribution = await self._get_payment_method_distribution(business_id)
        if not report_type or report_type == "outstanding":
            response.outstanding_balance = await self._get_total_outstanding_balance(business_id)
            
        return response

    async def _get_payments_received(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Payment).where(
            and_(Payment.business_id == business_id, Payment.is_active == True)
        ).order_by(desc(Payment.created_at))
        result = await self.session.execute(query)
        payments = result.scalars().all()
        
        return [
            {
                "payment_id": p.id,
                "invoice_id": p.invoice_id,
                "amount": float(p.amount),
                "payment_method": p.payment_method.value if hasattr(p.payment_method, "value") else str(p.payment_method),
                "transaction_id": p.transaction_id,
                "created_at": p.created_at
            } for p in payments
        ]

    async def _get_pending_payments(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Invoice).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.payment_status.in_([PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID]),
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        ).order_by(desc(Invoice.invoice_date))
        result = await self.session.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "invoice_id": i.id,
                "invoice_number": i.invoice_number,
                "customer_id": i.customer_id,
                "total_amount": float(i.grand_total),
                "outstanding_balance": float(i.outstanding_balance),
                "invoice_date": i.invoice_date,
                "due_date": i.due_date
            } for i in invoices
        ]

    async def _get_overdue_payments(self, business_id: uuid.UUID) -> List[dict]:
        now = datetime.now(timezone.utc)
        query = select(Invoice).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.is_active == True,
                Invoice.payment_status.in_([PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID]),
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID,
                Invoice.due_date != None,
                Invoice.due_date < now
            )
        ).order_by(desc(Invoice.invoice_date))
        result = await self.session.execute(query)
        invoices = result.scalars().all()
        
        return [
            {
                "invoice_id": i.id,
                "invoice_number": i.invoice_number,
                "customer_id": i.customer_id,
                "total_amount": float(i.grand_total),
                "outstanding_balance": float(i.outstanding_balance),
                "invoice_date": i.invoice_date,
                "due_date": i.due_date
            } for i in invoices
        ]

    async def _get_payment_method_distribution(
        self, business_id: uuid.UUID
    ) -> List[PaymentMethodDistributionItem]:
        query = (
            select(
                Payment.payment_method,
                func.count(Payment.id).label("count"),
                func.sum(Payment.amount).label("total_amount")
            )
            .where(
                and_(Payment.business_id == business_id, Payment.is_active == True)
            )
            .group_by(Payment.payment_method)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            PaymentMethodDistributionItem(
                payment_method=row.payment_method.value if hasattr(row.payment_method, "value") else str(row.payment_method),
                count=row.count,
                total_amount=float(row.total_amount)
            ) for row in rows
        ]

    async def _get_total_outstanding_balance(self, business_id: uuid.UUID) -> float:
        query = select(func.sum(Invoice.outstanding_balance)).where(
            and_(
                Invoice.business_id == business_id,
                Invoice.outstanding_balance > 0,
                Invoice.is_active == True,
                Invoice.status != InvoiceStatus.CANCELLED,
                Invoice.status != InvoiceStatus.VOID
            )
        )
        result = await self.session.execute(query)
        return float(result.scalar() or 0.0)

    # Inventory Reports
    async def get_inventory_reports(
        self,
        user_id: uuid.UUID,
        business_id: uuid.UUID,
        report_type: Optional[str] = None
    ) -> InventoryReportsResponse:
        await self._ensure_business_access(user_id, business_id)
        
        response = InventoryReportsResponse()
        
        if not report_type or report_type == "valuation":
            response.inventory_valuation = await self._get_inventory_valuation(business_id)
        if not report_type or report_type == "low_stock":
            response.low_stock_report = await self._get_low_stock_report(business_id)
        if not report_type or report_type == "out_of_stock":
            response.out_of_stock_report = await self._get_out_of_stock_report(business_id)
        if report_type == "stock_movement":
            response.stock_movement_report = await self._get_stock_movement_report(business_id)
            
        return response

    async def _get_inventory_valuation(self, business_id: uuid.UUID) -> List[InventoryValuationItem]:
        query = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Product.current_stock,
                Product.selling_price.label("unit_price"),
                (Product.current_stock * Product.selling_price).label("total_value")
            )
            .where(
                and_(Product.business_id == business_id, Product.is_active == True)
            )
            .order_by(desc(Product.current_stock * Product.selling_price))
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            InventoryValuationItem(
                product_id=row.product_id,
                product_name=row.product_name,
                current_stock=float(row.current_stock),
                unit_price=float(row.unit_price),
                total_value=float(row.total_value)
            ) for row in rows
        ]

    async def _get_low_stock_report(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Product).where(
            and_(
                Product.business_id == business_id,
                Product.is_active == True,
                Product.minimum_stock != None,
                Product.current_stock <= Product.minimum_stock,
                Product.current_stock > 0
            )
        ).order_by(asc(Product.current_stock))
        result = await self.session.execute(query)
        products = result.scalars().all()
        
        return [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current_stock": float(p.current_stock),
                "minimum_stock": float(p.minimum_stock)
            } for p in products
        ]

    async def _get_out_of_stock_report(self, business_id: uuid.UUID) -> List[dict]:
        query = select(Product).where(
            and_(
                Product.business_id == business_id,
                Product.is_active == True,
                Product.current_stock <= 0
            )
        ).order_by(Product.name)
        result = await self.session.execute(query)
        products = result.scalars().all()
        
        return [
            {
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current_stock": float(p.current_stock)
            } for p in products
        ]

    async def _get_stock_movement_report(self, business_id: uuid.UUID) -> List[StockMovementReportItem]:
        query = (
            select(
                InventoryTransaction.created_at.label("date"),
                InventoryTransaction.product_id,
                Product.name.label("product_name"),
                InventoryTransaction.transaction_type.label("movement_type"),
                InventoryTransaction.quantity,
                InventoryTransaction.reference_type,
                InventoryTransaction.reference_id
            )
            .join(Product, InventoryTransaction.product_id == Product.id)
            .where(InventoryTransaction.business_id == business_id)
            .order_by(desc(InventoryTransaction.created_at))
            .limit(100)
        )
        result = await self.session.execute(query)
        rows = result.fetchall()
        
        return [
            StockMovementReportItem(
                date=row.date,
                product_id=row.product_id,
                product_name=row.product_name,
                movement_type=row.movement_type.value if hasattr(row.movement_type, "value") else str(row.movement_type),
                quantity=float(row.quantity),
                reference_type=row.reference_type,
                reference_id=row.reference_id
            ) for row in rows
        ]

