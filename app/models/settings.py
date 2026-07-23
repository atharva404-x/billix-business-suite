import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, UUID, Integer, Boolean, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin


class BusinessSettings(Base, BaseModelMixin):
    """
    Tenant-specific business settings. One record per business profile.
    Covers identity, GST, invoice numbering, locale, and logo abstraction.
    """
    __tablename__ = "business_settings"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # GST & Tax Identity
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    # Invoice numbering
    invoice_prefix: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    invoice_suffix: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    invoice_number_format: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="{PREFIX}{YYYY}-{MM}-{SEQ}"
    )

    # Financial year — month number when it starts (4 = April, standard Indian FY)
    financial_year_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=4)

    # Locale
    currency: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="INR")
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="Asia/Kolkata")
    date_format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="DD/MM/YYYY")

    # Invoice defaults
    default_invoice_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_payment_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Appwrite-ready logo abstraction — stores Appwrite file ID, not a raw URL
    logo_file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    business: Mapped["BusinessProfile"] = relationship(  # noqa: F821
        "BusinessProfile",
        foreign_keys=[business_id]
    )


class BusinessPreferences(Base, BaseModelMixin):
    """
    Tenant-specific operational preferences. One record per business profile.
    Designed to be easily extensible via the report_preferences JSON column.
    """
    __tablename__ = "business_preferences"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Notification preferences
    notify_low_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_invoice_due: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_payment_received: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Decimal precision for amounts (0–4)
    decimal_precision: Mapped[int] = mapped_column(Integer, nullable=False, default=2)

    # Low stock threshold (units below which alerts fire)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # Default tax mode: "exclusive" (tax added on top) or "inclusive" (tax included in price)
    default_tax_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="exclusive")

    # Inventory behaviour
    track_inventory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_negative_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Extensible report preferences (JSON key-value bag)
    report_preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    business: Mapped["BusinessProfile"] = relationship(  # noqa: F821
        "BusinessProfile",
        foreign_keys=[business_id]
    )
