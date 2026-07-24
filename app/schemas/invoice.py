
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.invoice import InvoiceStatus, PaymentMethod, PaymentStatus

class InvoiceItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    discount: Optional[float] = Field(None, ge=0)
    gst_rate: Optional[float] = Field(None, ge=0, le=100)

class InvoiceItemUpdate(BaseModel):
    product_id: Optional[uuid.UUID] = None
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[float] = Field(None, ge=0)
    discount: Optional[float] = Field(None, ge=0)
    gst_rate: Optional[float] = Field(None, ge=0, le=100)

class InvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    invoice_id: uuid.UUID
    product_id: uuid.UUID
    quantity: float
    unit_price: float
    discount: Optional[float]
    gst_rate: Optional[float]
    taxable_amount: float
    tax_amount: Optional[float]
    total: float
    created_at: datetime
    updated_at: datetime

class InvoiceCreate(BaseModel):
    customer_id: uuid.UUID
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    discount_amount: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    items: List[InvoiceItemCreate] = Field(..., min_length=1)

class InvoiceUpdate(BaseModel):
    customer_id: Optional[uuid.UUID] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    discount_amount: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=2000)
    items: Optional[List[InvoiceItemCreate]] = Field(None, min_length=1)

class InvoiceCancel(BaseModel):
    reason: str = Field(..., max_length=1000)

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    customer_id: uuid.UUID
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]
    subtotal: float
    discount_amount: Optional[float]
    taxable_amount: float
    cgst_amount: Optional[float]
    sgst_amount: Optional[float]
    igst_amount: Optional[float]
    total_tax: float
    round_off: Optional[float]
    grand_total: float
    outstanding_balance: float
    payment_status: PaymentStatus
    status: InvoiceStatus
    notes: Optional[str]
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID]
    cancelled_by: Optional[uuid.UUID]
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse]

class InvoiceListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[InvoiceResponse]
    total: int

class PaymentCreate(BaseModel):
    invoice_id: uuid.UUID
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod = PaymentMethod.OTHER
    transaction_id: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=2000)

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    business_id: uuid.UUID
    invoice_id: uuid.UUID
    amount: float
    payment_method: PaymentMethod
    transaction_id: Optional[str]
    notes: Optional[str]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

class PaymentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[PaymentResponse]
    total: int
