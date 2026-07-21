
import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, UUID, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, BaseModelMixin
import enum


class StockMovement(str, enum.Enum):
    OPENING_STOCK = "OPENING_STOCK"
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    SALES_RETURN = "SALES_RETURN"
    PURCHASE_RETURN = "PURCHASE_RETURN"
    ADJUSTMENT_IN = "ADJUSTMENT_IN"
    ADJUSTMENT_OUT = "ADJUSTMENT_OUT"
    MANUAL_UPDATE = "MANUAL_UPDATE"


class InventoryTransaction(Base, BaseModelMixin):
    __tablename__ = "inventory_transactions"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False, index=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    transaction_type: Mapped[StockMovement] = mapped_column(String(50), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    previous_stock: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    new_stock: Mapped[float] = mapped_column(Numeric(15, 3), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    remarks: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
