from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = {
    'sleep_hours',
    'fatigue_score',
    'recovery_score',
    'previous_workout_intensity',
}

FEATURE_COLUMNS = [
    'age',
    'bmi',
    'sleep_hours',
    'steps',
    'active_minutes',
    'calories_burned',
    'workout_frequency',
    'workout_intensity',
    'previous_workout_intensity',
    'fatigue_score',
    'recovery_score',
    'fitness_level',
    'goal',
    'adherence_rate',
    'available_workout_minutes',
]


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def derive_readiness_level(df: pd.DataFrame) -> pd.Series:
    """Transparent rule-based target for initial readiness modeling."""
    conditions = pd.Series('Moderate', index=df.index)

    low_mask = (
        (df.get('sleep_hours', 0).fillna(0) < 6)
        | (df.get('fatigue_score', 0).fillna(0) >= 7)
        | (df.get('previous_workout_intensity', 0).fillna(0) >= 8)
        | (df.get('recovery_score', 0).fillna(0) <= 30)
    )

    high_mask = (
        (df.get('sleep_hours', 0).fillna(0) >= 7.5)
        & (df.get('fatigue_score', 0).fillna(0) <= 4)
        & (df.get('recovery_score', 0).fillna(0) >= 60)
        & (df.get('previous_workout_intensity', 0).fillna(0) <= 6)
    )

    conditions[low_mask] = 'Low'
    conditions[high_mask] = 'High'
    return conditions


def prepare_training_frame(df: pd.DataFrame, target_col: str = 'readiness_level') -> pd.DataFrame:
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise ValueError(
            'Dataset must contain sleep_hours, fatigue_score, recovery_score, and previous_workout_intensity '
            'to derive readiness_level.'
        )

    working = df.copy()
    working[target_col] = derive_readiness_level(working)

    for col in FEATURE_COLUMNS:
        if col not in working.columns:
            working[col] = pd.NA

    return working


def build_feature_matrix(df: pd.DataFrame, target_col: str = 'readiness_level') -> tuple[pd.DataFrame, pd.Series]:
    data = prepare_training_frame(df, target_col)
    selected = [col for col in FEATURE_COLUMNS if col in data.columns]
    X = data[selected].copy()
    y = data[target_col].copy()

    for column in X.select_dtypes(include=['number']).columns:
        X[column] = X[column].fillna(X[column].median())

    for column in X.select_dtypes(exclude=['number']).columns:
        X[column] = X[column].fillna('Unknown').astype(str)

    return X, y
