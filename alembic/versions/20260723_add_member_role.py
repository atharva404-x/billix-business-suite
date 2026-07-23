"""Add role column to business_members for per-business RBAC.

Revision ID: 20260723_add_member_role
Revises: 20260723_add_business_settings_and_preferences
"""
import sqlalchemy as sa
from alembic import op

revision = "20260723_add_member_role"
down_revision = "20260723_add_business_settings_and_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add role column; default 'viewer' so existing rows get a safe value
    op.add_column(
        "business_members",
        sa.Column(
            "role",
            sa.String(20),
            nullable=False,
            server_default="viewer",
        ),
    )
    # Back-fill: members flagged as owner get the owner role
    op.execute(
        "UPDATE business_members SET role = 'owner' WHERE is_owner = TRUE"
    )
    op.create_index(
        "ix_business_members_role",
        "business_members",
        ["role"],
    )


def downgrade() -> None:
    op.drop_index("ix_business_members_role", table_name="business_members")
    op.drop_column("business_members", "role")
