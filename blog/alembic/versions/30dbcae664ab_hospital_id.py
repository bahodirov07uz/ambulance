"""hospital_id

Revision ID: 30dbcae664ab
Revises: 064bf5743922
Create Date: 2025-07-26 09:32:12.478201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30dbcae664ab'
down_revision: Union[str, Sequence[str], None] = '064bf5743922'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
