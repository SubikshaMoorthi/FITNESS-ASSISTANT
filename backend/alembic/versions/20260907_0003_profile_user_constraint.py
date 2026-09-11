"""Enforce one profile per user.

Revision ID: 20260907_0003
Revises: 20260907_0002
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260907_0003'
down_revision = '20260907_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    constraints = inspector.get_unique_constraints('profiles')
    if any(item.get('column_names') == ['user_id'] for item in constraints):
        return

    for index in inspector.get_indexes('profiles'):
        if index.get('unique') and index.get('column_names') == ['user_id']:
            op.drop_index(index['name'], table_name='profiles')
            break

    op.create_unique_constraint('uq_profiles_user_id', 'profiles', ['user_id'])


def downgrade() -> None:
    op.drop_constraint('uq_profiles_user_id', 'profiles', type_='unique')
    op.create_index('ix_profiles_user_id', 'profiles', ['user_id'], unique=True)
