"""add admin to role enum

Revision ID: 0a524ed2b350
Revises: 3016a3a36064
Create Date: 2026-05-12 15:26:47.610326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a524ed2b350'
down_revision: Union[str, Sequence[str], None] = '3016a3a36064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE role ADD VALUE IF NOT EXISTS 'admin'")


def downgrade() -> None:
    pass
