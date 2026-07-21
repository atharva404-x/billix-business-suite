
"""Add customer_code and new indexes

Revision ID: 20260721_add_customer_code_and_indexes
Revises: 20260720_add_business_and_customers
Create Date: 2026-07-21

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260721_add_customer_code_and_indexes'
down_revision: Union[str, Sequence[str], None] = '20260720_add_business_and_customers'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add customer_code column
    op.add_column('customers', sa.Column('customer_code', sa.String(length=50), nullable=True))
    
    # Create indexes
    op.create_index(op.f('ix_customers_customer_code'), 'customers', ['customer_code'], unique=False)
    op.create_index(op.f('ix_customers_name'), 'customers', ['name'], unique=False)
    op.create_index(op.f('ix_customers_type'), 'customers', ['type'], unique=False)
    op.create_index(op.f('ix_customers_phone'), 'customers', ['phone'], unique=False)
    op.create_index(op.f('ix_customers_city'), 'customers', ['city'], unique=False)
    op.create_index(op.f('ix_customers_state'), 'customers', ['state'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_customers_state'), table_name='customers')
    op.drop_index(op.f('ix_customers_city'), table_name='customers')
    op.drop_index(op.f('ix_customers_phone'), table_name='customers')
    op.drop_index(op.f('ix_customers_type'), table_name='customers')
    op.drop_index(op.f('ix_customers_name'), table_name='customers')
    op.drop_index(op.f('ix_customers_customer_code'), table_name='customers')
    
    # Drop customer_code column
    op.drop_column('customers', 'customer_code')
