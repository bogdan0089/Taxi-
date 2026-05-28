"""rename create_at to created_at in trips

Revision ID: 464931de79c3
Revises: 4a613485f933
Create Date: 2026-05-04 18:56:45.979678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '464931de79c3'
down_revision: Union[str, Sequence[str], None] = '4a613485f933'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('trips', 'create_at', new_column_name='created_at')

def downgrade() -> None:
    op.alter_column('trips', 'created_at', new_column_name='create_at')

