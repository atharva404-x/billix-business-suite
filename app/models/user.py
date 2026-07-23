from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, BaseModelMixin
from app.models.roles import UserRole


class User(Base, BaseModelMixin):
    """
    SQLAlchemy User model linked to Clerk authentication identity.
    """
    __tablename__ = "users"

    clerk_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True
    )

    role: Mapped[UserRole] = mapped_column(
        String(50),
        default=UserRole.VIEWER,
        nullable=False
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
