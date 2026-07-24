"""Add audit_logs table.

Revision ID: 20260723_add_audit_logs
Revises: 20260723_add_business_settings_and_preferences
"""
import sqlalchemy as sa
from alembic import op

revision = "20260723_add_audit_logs"
down_revision = "20260723_add_business_settings_and_preferences"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "business_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("business_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("before_values", sa.Text, nullable=True),
        sa.Column("after_values", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_business_id", "audit_logs", ["business_id"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])


def downgrade() -> None:
    op.drop_table("audit_logs")
