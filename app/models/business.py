from typing import Optional, List
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin


class Business(Base, BaseModelMixin):
    """
    SQLAlchemy Business Profile model.
    Represents a tenant business profile (e.g., GSTIN / branch) in the system.
    """
    __tablename__ = "business_profiles"

    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), unique=True, index=True, nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(10), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    # Address details
    address_line_1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line_2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India", nullable=False)

    # Regional preferences
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)

    # Invoice series settings
    invoice_prefix: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    invoice_start_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    memberships: Mapped[List["Membership"]] = relationship(
        "Membership",
        back_populates="business",
        cascade="all, delete-orphan"
    )
