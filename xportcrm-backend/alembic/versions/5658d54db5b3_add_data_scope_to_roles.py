"""add data_scope to roles

Revision ID: 5658d54db5b3
Revises: e42768d9b2a5
Create Date: 2026-07-21 20:20:55.789755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5658d54db5b3'
down_revision: Union[str, None] = 'e42768d9b2a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add as nullable first, with a server-side default so Postgres
    #    can backfill existing rows
    op.add_column(
        'roles',
        sa.Column('data_scope', sa.String(length=20), nullable=True, server_default='Own')
    )

    # 2. Explicit backfill (safe even if server_default already handled it)
    op.execute("UPDATE roles SET data_scope = 'Own' WHERE data_scope IS NULL")

    # 3. Now enforce NOT NULL
    op.alter_column('roles', 'data_scope', nullable=False)


def downgrade() -> None:
    op.drop_column('roles', 'data_scope')