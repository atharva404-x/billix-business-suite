
"""Add products, categories, units tables

Revision ID: 20260721_add_products_categories_units
Revises: 20260721_add_suppliers_table
Create Date: 2026-07-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260721_add_products_categories_units'
down_revision: Union[str, Sequence[str], None] = '20260721_add_suppliers_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Units table
    op.create_table(
        'units',
        sa.Column('business_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_units_business_id'), 'units', ['business_id'], unique=False)
    op.create_index(op.f('ix_units_name'), 'units', ['name'], unique=False)

    # Categories table
    op.create_table(
        'categories',
        sa.Column('business_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('parent_id', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_business_id'), 'categories', ['business_id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'], unique=False)

    # Products table
    op.create_table(
        'products',
        sa.Column('business_id', sa.UUID(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('unit_id', sa.UUID(), nullable=True),
        sa.Column('sku', sa.String(length=100), nullable=True),
        sa.Column('barcode', sa.String(length=100), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('hsn_sac_code', sa.String(length=20), nullable=True),
        sa.Column('gst_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('purchase_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('selling_price', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('opening_stock', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('minimum_stock', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('maximum_stock', sa.Numeric(precision=15, scale=3), nullable=True),
        sa.Column('current_stock', sa.Numeric(precision=15, scale=3), nullable=False),
        sa.Column('is_service', sa.Boolean(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_profiles.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_business_id'), 'products', ['business_id'], unique=False)
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
    op.create_index(op.f('ix_products_unit_id'), 'products', ['unit_id'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)
    op.create_index(op.f('ix_products_barcode'), 'products', ['barcode'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_index(op.f('ix_products_hsn_sac_code'), 'products', ['hsn_sac_code'], unique=False)
    op.create_index(op.f('ix_products_is_service'), 'products', ['is_service'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_products_is_service'), table_name='products')
    op.drop_index(op.f('ix_products_hsn_sac_code'), table_name='products')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_barcode'), table_name='products')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_unit_id'), table_name='products')
    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    op.drop_index(op.f('ix_products_business_id'), table_name='products')
    op.drop_table('products')
    
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_business_id'), table_name='categories')
    op.drop_table('categories')
    
    op.drop_index(op.f('ix_units_name'), table_name='units')
    op.drop_index(op.f('ix_units_business_id'), table_name='units')
    op.drop_table('units')
