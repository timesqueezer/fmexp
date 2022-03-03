"""Added data_type to data_points

Revision ID: d972b1649f3e
Revises: c59701b26db5
Create Date: 2022-03-03 15:29:59.702318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd972b1649f3e'
down_revision = 'c59701b26db5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_points', sa.Column('data_type', sa.Integer(), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('data_points', 'data_type')
