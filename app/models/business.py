
import uuid
from typing import Optional, List
from sqlalchemy import String, ForeignKey, UUID, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin
from app.models.roles import BusinessRole


class BusinessProfile(Base, BaseModelMixin):
    __tablename__ = "business_profiles"

    business_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    gstin: Mapped[Optional[str]] = mapped_column(
        String(15),
        unique=True,
        index=True,
        nullable=True
    )

    address: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    pincode: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    members: Mapped[List["BusinessMember"]] = relationship(
        "BusinessMember",
        back_populates="business",
        cascade="all, delete-orphan"
    )


class BusinessMember(Base, BaseModelMixin):
    __tablename__ = "business_members"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        nullable=False,
        index=True
    )

    is_owner: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )

    role: Mapped[BusinessRole] = mapped_column(
        String(20),
        nullable=False,
        default=BusinessRole.VIEWER
    )

    user: Mapped["User"] = relationship(
        "User",
        backref="business_memberships"
    )

    business: Mapped["BusinessProfile"] = relationship(
        "BusinessProfile",
        back_populates="members"
    )
