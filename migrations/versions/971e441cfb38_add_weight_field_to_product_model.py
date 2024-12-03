"""Add weight field to Product model

Revision ID: 971e441cfb38
Revises: 84a13703dd02
Create Date: 2024-12-03 18:44:50.870930

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '971e441cfb38'
down_revision = '84a13703dd02'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table with all the desired columns
    op.execute("""
        CREATE TABLE product_new (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price NUMERIC(10, 2) NOT NULL,
            weight NUMERIC(10, 3) NOT NULL DEFAULT '1.000'
        )
    """)
    
    # Copy data from the old table to the new one
    op.execute("""
        INSERT INTO product_new (id, name, price)
        SELECT id, name, price FROM product
    """)
    
    # Drop the old table
    op.drop_table('product')
    
    # Rename the new table to the original name
    op.rename_table('product_new', 'product')


def downgrade():
    # Create a new table with the old schema
    op.execute("""
        CREATE TABLE product_new (
            id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price NUMERIC(10, 2) NOT NULL,
            sku VARCHAR(50)
        )
    """)
    
    # Copy data back, excluding the weight column
    op.execute("""
        INSERT INTO product_new (id, name, price)
        SELECT id, name, price FROM product
    """)
    
    # Drop the new table
    op.drop_table('product')
    
    # Rename the old table back
    op.rename_table('product_new', 'product')
