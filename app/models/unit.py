
import uuid
from typing import Optional
from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, BaseModelMixin


class Unit(Base, BaseModelMixin):
    __tablename__ = "units"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("business_profiles.id"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    symbol: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True
    )
