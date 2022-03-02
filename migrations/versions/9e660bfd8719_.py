"""Initial migration including users and data_points

Revision ID: 9e660bfd8719
Revises: 
Create Date: 2022-02-24 14:41:24.115740

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9e660bfd8719'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('password_salt', sa.LargeBinary(), nullable=True),
        sa.Column('password_hash', sa.LargeBinary(), nullable=True),
        sa.PrimaryKeyConstraint('uuid'),
        sa.UniqueConstraint('email')
    )
    op.create_table('data_points',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('user_uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('data_points')
    op.drop_table('users')
