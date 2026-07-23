import uuid
from enum import Enum
from typing import Optional
from sqlalchemy import UUID, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, BaseModelMixin


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"


class AuditLog(Base, BaseModelMixin):
    """
    Audit log model for tracking all changes to business entities.
    Captures who changed what, when, and the before/after states.
    """
    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    action: Mapped[AuditAction] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )

    before_values: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    after_values: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True
    )

    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
