"""Add business_settings and business_preferences tables.

Revision ID: 20260723_add_business_settings_and_preferences
Revises: 20260722_harden_core_integrity
"""
import sqlalchemy as sa
from alembic import op

revision = "20260723_add_business_settings_and_preferences"
down_revision = "20260722_harden_core_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # MODULE 1 — business_settings
    op.create_table(
        "business_settings",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "business_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("business_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("company_address", sa.Text, nullable=True),
        sa.Column("gstin", sa.String(15), nullable=True),
        sa.Column("pan", sa.String(10), nullable=True),
        sa.Column("invoice_prefix", sa.String(20), nullable=True),
        sa.Column("invoice_suffix", sa.String(20), nullable=True),
        sa.Column(
            "invoice_number_format",
            sa.String(100),
            nullable=True,
            server_default="{PREFIX}{YYYY}-{MM}-{SEQ}",
        ),
        sa.Column("financial_year_start", sa.Integer, nullable=True, server_default="4"),
        sa.Column("currency", sa.String(10), nullable=True, server_default="INR"),
        sa.Column("timezone", sa.String(50), nullable=True, server_default="Asia/Kolkata"),
        sa.Column("date_format", sa.String(20), nullable=True, server_default="DD/MM/YYYY"),
        sa.Column("default_invoice_notes", sa.Text, nullable=True),
        sa.Column("default_payment_terms", sa.Text, nullable=True),
        sa.Column("logo_file_id", sa.String(255), nullable=True),
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
    op.create_index(
        "ix_business_settings_business_id",
        "business_settings",
        ["business_id"],
        unique=True,
    )

    # MODULE 2 — business_preferences
    op.create_table(
        "business_preferences",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "business_id",
            sa.UUID(as_uuid=True),
            sa.ForeignKey("business_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notify_low_stock", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notify_invoice_due", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "notify_payment_received", sa.Boolean, nullable=False, server_default="true"
        ),
        sa.Column("decimal_precision", sa.Integer, nullable=False, server_default="2"),
        sa.Column("low_stock_threshold", sa.Integer, nullable=False, server_default="10"),
        sa.Column(
            "default_tax_mode", sa.String(20), nullable=True, server_default="exclusive"
        ),
        sa.Column("track_inventory", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "allow_negative_stock", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("report_preferences", sa.JSON, nullable=True),
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
    op.create_index(
        "ix_business_preferences_business_id",
        "business_preferences",
        ["business_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("business_preferences")
    op.drop_table("business_settings")
