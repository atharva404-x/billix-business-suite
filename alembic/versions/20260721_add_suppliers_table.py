
"""Add suppliers table

Revision ID: 20260721_add_suppliers_table
Revises: 20260721_add_customer_code_and_indexes
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260721_add_suppliers_table'
down_revision: Union[str, Sequence[str], None] = '20260721_add_customer_code_and_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('suppliers',
    sa.Column('business_id', sa.UUID(), nullable=False),
    sa.Column('supplier_code', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(length=20), nullable=False),
    sa.Column('gstin', sa.String(length=15), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('address', sa.String(length=1000), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('state', sa.String(length=100), nullable=True),
    sa.Column('pincode', sa.String(length=10), nullable=True),
    sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('outstanding_balance', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_suppliers_business_id'), 'suppliers', ['business_id'], unique=False)
    op.create_index(op.f('ix_suppliers_supplier_code'), 'suppliers', ['supplier_code'], unique=False)
    op.create_index(op.f('ix_suppliers_name'), 'suppliers', ['name'], unique=False)
    op.create_index(op.f('ix_suppliers_type'), 'suppliers', ['type'], unique=False)
    op.create_index(op.f('ix_suppliers_gstin'), 'suppliers', ['gstin'], unique=False)
    op.create_index(op.f('ix_suppliers_phone'), 'suppliers', ['phone'], unique=False)
    op.create_index(op.f('ix_suppliers_city'), 'suppliers', ['city'], unique=False)
    op.create_index(op.f('ix_suppliers_state'), 'suppliers', ['state'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_suppliers_state'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_city'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_phone'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_gstin'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_type'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_name'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_supplier_code'), table_name='suppliers')
    op.drop_index(op.f('ix_suppliers_business_id'), table_name='suppliers')
    op.drop_table('suppliers')
