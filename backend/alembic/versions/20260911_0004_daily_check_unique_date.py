"""Enforce one daily check per user and date.

Revision ID: 20260911_0004
Revises: 20260907_0003
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260911_0004'
down_revision = '20260907_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_unique_constraints('daily_checks')
    if not any(item.get('column_names') == ['user_id', 'check_date'] for item in constraints):
        # Keep the newest record for each user/date before enforcing uniqueness.
        bind.execute(sa.text('''
            DELETE FROM daily_checks older
            USING daily_checks newer
            WHERE older.user_id = newer.user_id
              AND older.check_date = newer.check_date
              AND older.id < newer.id
        '''))
        op.create_unique_constraint('uq_daily_checks_user_date', 'daily_checks', ['user_id', 'check_date'])


def downgrade() -> None:
    op.drop_constraint('uq_daily_checks_user_date', 'daily_checks', type_='unique')
