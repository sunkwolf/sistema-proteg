"""add_unique_employee_user_id

Prevent multiple employees from linking to the same app_user.
scalar_one_or_none() in permission resolution would throw if duplicated.

Revision ID: 90e6fc3c4808
Revises: dcb529267be5
Create Date: 2026-02-15 02:12:16.972429

"""
from typing import Sequence, Union

from alembic import op

revision: str = '90e6fc3c4808'
down_revision: Union[str, None] = 'dcb529267be5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_employee_user_id', 'employee', ['user_id'])


def downgrade() -> None:
    op.drop_constraint('uq_employee_user_id', 'employee', type_='unique')
