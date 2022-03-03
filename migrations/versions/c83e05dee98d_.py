"""Added users.is_bot

Revision ID: c83e05dee98d
Revises: 874d5b7f14ad
Create Date: 2022-03-03 21:45:19.543693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c83e05dee98d'
down_revision = '874d5b7f14ad'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('is_bot', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('users', 'is_bot')
