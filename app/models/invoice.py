
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, ForeignKey, UUID, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin
import enum


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    VOID = "void"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    UPI = "upi"
    CARD = "card"
    CHEQUE = "cheque"
    NEFT = "neft"
    RTGS = "rtgs"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class Invoice(Base, BaseModelMixin):
    __tablename__ = "invoices"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False, index=True
    )
    invoice_number: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    subtotal: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    discount_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    taxable_amount: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    cgst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    sgst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    igst_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    total_tax: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    round_off: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    grand_total: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    outstanding_balance: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        String(50), default=PaymentStatus.UNPAID, nullable=False, index=True
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        String(50), default=InvoiceStatus.DRAFT, nullable=False, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(
        String(2000), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    cancelled_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True
    )

    items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )


class Payment(Base, BaseModelMixin):
    __tablename__ = "payments"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        String(50), default=PaymentMethod.OTHER, nullable=False, index=True
    )
    transaction_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(
        String(2000), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")


class InvoiceItem(Base, BaseModelMixin):
    __tablename__ = "invoice_items"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    quantity: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=3), nullable=False
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    discount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    gst_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=5, scale=2), nullable=True
    )
    taxable_amount: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )
    tax_amount: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2), nullable=True
    )
    total: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
