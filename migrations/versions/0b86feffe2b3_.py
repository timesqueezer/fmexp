"""Added bot_request_mode and bot_mouse_mode to users

Revision ID: 0b86feffe2b3
Revises: 49ce629bdad7
Create Date: 2022-05-04 11:07:36.384751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b86feffe2b3'
down_revision = '49ce629bdad7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('bot_request_mode', sa.String(), nullable=True))
    op.add_column('users', sa.Column('bot_mouse_mode', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'bot_mouse_mode')
    op.drop_column('users', 'bot_request_mode')
