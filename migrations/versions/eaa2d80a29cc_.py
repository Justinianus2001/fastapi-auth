"""empty message

Revision ID: eaa2d80a29cc
Revises: 001
Create Date: 2025-04-16 10:47:50.642397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eaa2d80a29cc'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column("abc", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'abc')