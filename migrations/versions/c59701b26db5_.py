"""Added additional user fields

Revision ID: c59701b26db5
Revises: 9e660bfd8719
Create Date: 2022-02-28 13:39:53.436909

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c59701b26db5'
down_revision = '9e660bfd8719'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('address_line_1', sa.String(), nullable=True))
    op.add_column('users', sa.Column('address_line_2', sa.String(), nullable=True))
    op.add_column('users', sa.Column('zip_code', sa.String(), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(), nullable=True))
    op.add_column('users', sa.Column('logged_in', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('users', 'logged_in')
    op.drop_column('users', 'country')
    op.drop_column('users', 'state')
    op.drop_column('users', 'city')
    op.drop_column('users', 'zip_code')
    op.drop_column('users', 'address_line_2')
    op.drop_column('users', 'address_line_1')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
