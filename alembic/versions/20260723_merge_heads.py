"""Merge three independent branch heads into a single head.

The three migrations:
  - 20260723_add_audit_logs
  - 20260723_add_member_role
  - 20260723_add_notifications

all declared the same down_revision
(20260723_add_business_settings_and_preferences), creating three separate
branch heads.  This merge migration combines them back into one linear
history so that ``alembic upgrade head`` resolves to exactly one head.

Revision ID: 20260723_merge_heads
Revises: 20260723_add_audit_logs, 20260723_add_member_role, 20260723_add_notifications
Create Date: 2026-07-24
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

# revision identifiers, used by Alembic.
revision: str = "20260723_merge_heads"
down_revision: Union[str, Sequence[str], None] = (
    "20260723_add_audit_logs",
    "20260723_add_member_role",
    "20260723_add_notifications",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No schema changes — this is a pure merge point."""
    pass


def downgrade() -> None:
    """No schema changes — this is a pure merge point."""
    pass
