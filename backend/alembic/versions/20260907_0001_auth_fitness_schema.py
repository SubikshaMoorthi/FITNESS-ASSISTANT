"""Create the authenticated fitness schema.

Revision ID: 20260907_0001
Revises:
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = '20260907_0001'
down_revision = None
branch_labels = None
depends_on = None


def _tables(bind):
    return set(sa.inspect(bind).get_table_names())


def _rename_legacy_tables(bind):
    legacy_names = {
        'user_profiles': 'profiles',
        'recommendation_records': 'recommendations',
        'workout_plan_records': 'workout_plans',
        'meal_recommendation_records': 'meal_recommendations',
    }
    tables = _tables(bind)
    for old_name, new_name in legacy_names.items():
        if old_name in tables and new_name not in tables:
            op.rename_table(old_name, new_name)
            tables.remove(old_name)
            tables.add(new_name)


def upgrade() -> None:
    bind = op.get_bind()
    _rename_legacy_tables(bind)
    tables = _tables(bind)

    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('email', sa.String(length=255), nullable=False),
            sa.Column('password_hash', sa.String(length=255), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint('email', name='uq_users_email'),
        )
        op.create_index('ix_users_email', 'users', ['email'], unique=True)

    if 'profiles' not in tables:
        op.create_table(
            'profiles',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('age', sa.Integer(), nullable=False),
            sa.Column('gender', sa.String(length=20)),
            sa.Column('height', sa.Float(), nullable=False),
            sa.Column('weight', sa.Float(), nullable=False),
            sa.Column('bmi', sa.Float(), nullable=False),
            sa.Column('fitness_goal', sa.String(length=50), nullable=False),
            sa.Column('fitness_level', sa.String(length=30), nullable=False),
            sa.Column('workout_preference', sa.String(length=30), nullable=False),
            sa.Column('dietary_preference', sa.String(length=30), nullable=False),
            sa.Column('available_workout_minutes', sa.Integer(), server_default='45', nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint('user_id', name='uq_profiles_user_id'),
        )
        op.create_index('ix_profiles_user_id', 'profiles', ['user_id'])

    if 'daily_checks' not in tables:
        op.create_table(
            'daily_checks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('check_date', sa.Date(), server_default=sa.func.current_date(), nullable=False),
            sa.Column('payload', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_daily_checks_user_id', 'daily_checks', ['user_id'])

    if 'recommendations' not in tables:
        op.create_table(
            'recommendations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('payload', sa.JSON(), nullable=False),
            sa.Column('result', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_recommendations_user_id', 'recommendations', ['user_id'])

    if 'workout_plans' not in tables:
        op.create_table(
            'workout_plans',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('plan', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_workout_plans_user_id', 'workout_plans', ['user_id'])

    if 'workout_feedback' not in tables:
        op.create_table(
            'workout_feedback',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('profile_id', sa.Integer(), sa.ForeignKey('profiles.id')), 
            sa.Column('workout_name', sa.String(length=120), nullable=False),
            sa.Column('readiness_level', sa.String(length=30), nullable=False),
            sa.Column('intervention', sa.String(length=50), nullable=False),
            sa.Column('completion_status', sa.String(length=30), nullable=False),
            sa.Column('completion_percentage', sa.Float(), nullable=False),
            sa.Column('difficulty', sa.String(length=30), nullable=False),
            sa.Column('feedback', sa.Text()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_workout_feedback_user_id', 'workout_feedback', ['user_id'])

    if 'meal_recommendations' not in tables:
        op.create_table(
            'meal_recommendations',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('meals', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_meal_recommendations_user_id', 'meal_recommendations', ['user_id'])

    if 'progress_history' not in tables:
        op.create_table(
            'progress_history',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('source', sa.String(length=50), nullable=False),
            sa.Column('data', sa.JSON(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index('ix_progress_history_user_id', 'progress_history', ['user_id'])


def downgrade() -> None:
    bind = op.get_bind()
    tables = _tables(bind)
    for table_name in ('progress_history', 'meal_recommendations', 'workout_feedback', 'workout_plans', 'recommendations', 'daily_checks', 'profiles', 'users'):
        if table_name in tables:
            op.drop_table(table_name)
