"""Add water intake tracking.

Revision ID: 20260911_0005
Revises: 20260911_0004
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260911_0005'
down_revision = '20260911_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'water_intake' not in tables:
        op.create_table(
            'water_intake',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('intake_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
            sa.Column('amount_ml', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_water_intake_user_id', 'water_intake', ['user_id'])
        op.create_index('ix_water_intake_intake_date', 'water_intake', ['intake_date'])
        op.create_index('ix_water_intake_user_date', 'water_intake', ['user_id', 'intake_date'])


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if 'water_intake' in tables:
        op.drop_index('ix_water_intake_user_date', table_name='water_intake')
        op.drop_index('ix_water_intake_intake_date', table_name='water_intake')
        op.drop_index('ix_water_intake_user_id', table_name='water_intake')
        op.drop_table('water_intake')
