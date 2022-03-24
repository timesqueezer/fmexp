"""Added data_points.user_uuid index

Revision ID: 49ce629bdad7
Revises: c83e05dee98d
Create Date: 2022-03-24 15:13:22.398526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49ce629bdad7'
down_revision = 'c83e05dee98d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(op.f('ix_data_points_user_uuid'), 'data_points', ['user_uuid'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_data_points_user_uuid'), table_name='data_points')
