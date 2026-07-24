
import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Numeric, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseModelMixin

class Product(Base, BaseModelMixin):
    __tablename__ = "products"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        nullable=False,
        index=True
    )

    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )

    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id"),
        nullable=True,
        index=True
    )

    sku: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        unique=False  # Unique per business, not global
    )

    barcode: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        unique=False  # Unique per business
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True
    )

    hsn_sac_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True
    )

    gst_rate: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True
    )

    purchase_price: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=True
    )

    selling_price: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=True
    )

    opening_stock: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=True,
        default=0.0
    )

    minimum_stock: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=True
    )

    maximum_stock: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=True
    )

    current_stock: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=3),
        nullable=False,
        default=0.0
    )

    is_service: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
