
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from uuid import UUID


# Dashboard Schemas
class DashboardSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    sales_today: float
    sales_this_week: float
    sales_this_month: float
    sales_this_year: float
    outstanding_receivables: float
    total_customers: int
    total_suppliers: int
    total_products: int
    active_products: int
    out_of_stock_products: int
    low_stock_products: int
    inventory_value: float
    paid_invoices: int
    pending_invoices: int
    cancelled_invoices: int
    total_revenue: float
    average_invoice_value: float


class TopSellingProductItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: UUID
    product_name: str
    quantity_sold: float
    total_revenue: float


class RecentInvoiceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    invoice_id: UUID
    invoice_number: str
    customer_id: UUID
    customer_name: str
    total_amount: float
    status: str
    invoice_date: datetime


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    top_selling_products: List[TopSellingProductItem]
    recent_invoices: List[RecentInvoiceItem]


# Sales Reports Schemas
class SalesReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    period: str  # e.g., "2026-07-21", "2026-W30", "2026-07", "2026"
    total_sales: float
    total_invoices: int
    average_invoice_value: float


class SalesReportResponse(BaseModel):
    items: List[SalesReportItem]


# Customer Reports Schemas
class TopCustomerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: UUID
    customer_name: str
    total_purchases: int
    total_revenue: float


class OutstandingCustomerItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    customer_id: UUID
    customer_name: str
    outstanding_balance: float


class CustomerPurchaseHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    invoice_id: UUID
    invoice_number: str
    invoice_date: datetime
    total_amount: float
    paid_amount: float
    outstanding_balance: float


class CustomerReportsResponse(BaseModel):
    top_customers: Optional[List[TopCustomerItem]] = None
    highest_spending_customers: Optional[List[TopCustomerItem]] = None
    outstanding_customers: Optional[List[OutstandingCustomerItem]] = None
    customer_purchase_history: Optional[List[CustomerPurchaseHistoryItem]] = None
    customer_revenue: Optional[List[TopCustomerItem]] = None


# Product Reports Schemas
class ProductSalesItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: UUID
    product_name: str
    sku: str
    quantity_sold: float
    total_revenue: float


class StockValueItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: UUID
    product_name: str
    current_stock: float
    unit_price: float
    total_value: float


class ProductReportsResponse(BaseModel):
    top_selling_products: Optional[List[ProductSalesItem]] = None
    least_selling_products: Optional[List[ProductSalesItem]] = None
    inactive_products: Optional[List[dict]] = None
    stock_value: Optional[List[StockValueItem]] = None
    current_stock: Optional[List[dict]] = None
    stock_movement_summary: Optional[List[dict]] = None


# Payment Reports Schemas
class PaymentMethodDistributionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    payment_method: str
    count: int
    total_amount: float


class PaymentReportsResponse(BaseModel):
    payments_received: Optional[List[dict]] = None
    pending_payments: Optional[List[dict]] = None
    overdue_payments: Optional[List[dict]] = None
    payment_method_distribution: Optional[List[PaymentMethodDistributionItem]] = None
    outstanding_balance: Optional[float] = None


# Inventory Reports Schemas
class InventoryValuationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    product_id: UUID
    product_name: str
    current_stock: float
    unit_price: float
    total_value: float


class StockMovementReportItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    date: datetime
    product_id: UUID
    product_name: str
    movement_type: str
    quantity: float
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None


class InventoryReportsResponse(BaseModel):
    inventory_valuation: Optional[List[InventoryValuationItem]] = None
    low_stock_report: Optional[List[dict]] = None
    out_of_stock_report: Optional[List[dict]] = None
    stock_movement_report: Optional[List[StockMovementReportItem]] = None
    opening_stock: Optional[List[dict]] = None
    closing_stock: Optional[List[dict]] = None

