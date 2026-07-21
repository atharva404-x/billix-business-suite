
import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, UUID, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, BaseModelMixin


class CustomerType(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


class Customer(Base, BaseModelMixin):
    __tablename__ = "customers"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        nullable=False,
        index=True
    )

    customer_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    type: Mapped[CustomerType] = mapped_column(
        String(10),
        default=CustomerType.B2C,
        nullable=False,
        index=True
    )

    gstin: Mapped[Optional[str]] = mapped_column(
        String(15),
        nullable=True,
        index=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    pincode: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    credit_limit: Mapped[Optional[float]] = mapped_column(
        Numeric(precision=15, scale=2),
        nullable=True
    )

    outstanding_balance: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2),
        default=0.0,
        nullable=False
    )
