"""Harden tenant and invoice integrity.

Revision ID: 20260722_harden_core_integrity
Revises: 20260721_harden_invoice_engine
"""
from alembic import op

revision = "20260722_harden_core_integrity"
down_revision = "20260721_harden_invoice_engine"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_business_members_user_business", "business_members", ["user_id", "business_id"])
    op.create_unique_constraint("uq_invoices_business_number", "invoices", ["business_id", "invoice_number"])
    op.create_unique_constraint("uq_products_business_sku", "products", ["business_id", "sku"])
    op.create_unique_constraint("uq_products_business_barcode", "products", ["business_id", "barcode"])
    op.create_index("ix_invoices_business_status_date", "invoices", ["business_id", "status", "invoice_date"])


def downgrade() -> None:
    op.drop_index("ix_invoices_business_status_date", table_name="invoices")
    op.drop_constraint("uq_products_business_barcode", "products", type_="unique")
    op.drop_constraint("uq_products_business_sku", "products", type_="unique")
    op.drop_constraint("uq_invoices_business_number", "invoices", type_="unique")
    op.drop_constraint("uq_business_members_user_business", "business_members", type_="unique")
