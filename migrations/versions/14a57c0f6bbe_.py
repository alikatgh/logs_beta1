"""empty message

Revision ID: 14a57c0f6bbe
Revises: c7562bd13283
Create Date: 2024-06-08 16:35:31.061837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14a57c0f6bbe'
down_revision = 'c7562bd13283'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('supermarket', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=sa.VARCHAR(length=200),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('supermarket', schema=None) as batch_op:
        batch_op.alter_column('address',
               existing_type=sa.VARCHAR(length=200),
               nullable=True)

    # ### end Alembic commands ###