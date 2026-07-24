
import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModelMixin

class Category(Base, BaseModelMixin):
    __tablename__ = "categories"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )

    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id")
