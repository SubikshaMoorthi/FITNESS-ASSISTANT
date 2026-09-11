"""Add calendar dates to daily checks.

Revision ID: 20260907_0002
Revises: 20260907_0001
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260907_0002'
down_revision = '20260907_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('daily_checks')}
    if 'check_date' not in columns:
        op.add_column(
            'daily_checks',
            sa.Column('check_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
        )
        op.create_index('ix_daily_checks_check_date', 'daily_checks', ['check_date'])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column['name'] for column in inspector.get_columns('daily_checks')}
    if 'check_date' in columns:
        op.drop_index('ix_daily_checks_check_date', table_name='daily_checks')
        op.drop_column('daily_checks', 'check_date')
