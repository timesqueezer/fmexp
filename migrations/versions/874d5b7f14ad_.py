"""Added user_type to data_points

Revision ID: 874d5b7f14ad
Revises: d972b1649f3e
Create Date: 2022-03-03 21:37:38.837750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '874d5b7f14ad'
down_revision = 'd972b1649f3e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('data_points', sa.Column('user_type', sa.Integer(), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('data_points', 'user_type')
