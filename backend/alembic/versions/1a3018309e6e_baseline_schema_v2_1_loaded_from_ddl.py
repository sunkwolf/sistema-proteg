"""baseline: schema v2.1 loaded from DDL

Revision ID: 1a3018309e6e
Revises: 
Create Date: 2026-02-15 00:49:07.265865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a3018309e6e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
