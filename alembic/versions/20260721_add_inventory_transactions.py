
"""Add inventory transactions table

Revision ID: 20260721_add_inventory_transactions
Revises: 20260721_add_products_categories_units
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260721_add_inventory_transactions'
down_revision: Union[str, Sequence[str], None] = '20260721_add_products_categories_units'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'inventory_transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('business_id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('previous_stock', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('new_stock', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('reference_type', sa.String(length=100), nullable=True),
        sa.Column('reference_id', sa.UUID(), nullable=True),
        sa.Column('remarks', sa.String(length=1000), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_transactions_business_id'), 'inventory_transactions', ['business_id'], unique=False)
    op.create_index(op.f('ix_inventory_transactions_product_id'), 'inventory_transactions', ['product_id'], unique=False)
    op.create_index(op.f('ix_inventory_transactions_transaction_type'), 'inventory_transactions', ['transaction_type'], unique=False)
    op.create_index(op.f('ix_inventory_transactions_reference_type'), 'inventory_transactions', ['reference_type'], unique=False)
    op.create_index(op.f('ix_inventory_transactions_reference_id'), 'inventory_transactions', ['reference_id'], unique=False)
    op.create_index(op.f('ix_inventory_transactions_created_by'), 'inventory_transactions', ['created_by'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_inventory_transactions_created_by'), table_name='inventory_transactions')
    op.drop_index(op.f('ix_inventory_transactions_reference_id'), table_name='inventory_transactions')
    op.drop_index(op.f('ix_inventory_transactions_reference_type'), table_name='inventory_transactions')
    op.drop_index(op.f('ix_inventory_transactions_transaction_type'), table_name='inventory_transactions')
    op.drop_index(op.f('ix_inventory_transactions_product_id'), table_name='inventory_transactions')
    op.drop_index(op.f('ix_inventory_transactions_business_id'), table_name='inventory_transactions')
    op.drop_table('inventory_transactions')
