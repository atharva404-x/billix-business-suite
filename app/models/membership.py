import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import UUID, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin
from app.models.roles import UserRole


class Membership(Base, BaseModelMixin):
    """
    SQLAlchemy Membership model.
    Establishes a many-to-many link between Users and Businesses, defining roles on a per-business basis.
    """
    __tablename__ = "memberships"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    role: Mapped[UserRole] = mapped_column(
        String(50),
        default=UserRole.VIEWER,
        nullable=False
    )

    invited_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    joined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships",
        foreign_keys=[user_id]
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="memberships",
        foreign_keys=[business_id]
    )
