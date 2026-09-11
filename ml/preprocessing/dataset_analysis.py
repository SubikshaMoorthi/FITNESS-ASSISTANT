from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataset(csv_path: str | Path) -> pd.DataFrame:
    """Load the dataset and validate expected columns."""
    df = pd.read_csv(csv_path)
    return df


def derive_readiness_level(df: pd.DataFrame) -> pd.Series:
    """Create a transparent readiness target based on recovery and training load.

    This is a documented, explainable rule that is suitable for a first ML iteration.
    It deliberately avoids opaque synthetic labels.
    """
    conditions = pd.Series('Moderate', index=df.index)

    low_mask = (
        (df.get('sleep_hours', 0) < 6) |
        (df.get('fatigue_score', 0) >= 7) |
        (df.get('previous_workout_intensity', 0) >= 8) |
        (df.get('recovery_score', 0) <= 30)
    )

    high_mask = (
        (df.get('sleep_hours', 0) >= 7.5) &
        (df.get('fatigue_score', 0) <= 4) &
        (df.get('recovery_score', 0) >= 60) &
        (df.get('previous_workout_intensity', 0) <= 6)
    )

    conditions[low_mask] = 'Low'
    conditions[high_mask] = 'High'
    return conditions


def analyze_dataset(csv_path: str | Path) -> dict:
    """Return a concise summary useful for Phase 2 dataset review."""
    df = load_dataset(csv_path)
    summary = {
        'rows': int(len(df)),
        'columns': list(df.columns),
        'missing_values': df.isna().sum().to_dict(),
        'dtypes': {key: str(value) for key, value in df.dtypes.to_dict().items()},
        'basic_describe': df.describe(include='all').to_dict(),
    }

    if {'sleep_hours', 'fatigue_score', 'recovery_score', 'previous_workout_intensity'}.issubset(df.columns):
        df = df.copy()
        df['readiness_level'] = derive_readiness_level(df)
        summary['target_distribution'] = df['readiness_level'].value_counts().to_dict()
        summary['target_definition'] = (
            'readiness_level is derived from sleep, recovery, fatigue, and recent workout intensity; '
            'Low indicates poor readiness and High indicates strong readiness.'
        )
    else:
        summary['target_distribution'] = None
        summary['target_definition'] = (
            'Target variable needs to be derived from the available dataset once the required columns are present.'
        )

    return summary


def main() -> None:
    """Example usage: python dataset_analysis.py <path-to-data.csv>"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze a structured fitness dataset for readiness modeling.')
    parser.add_argument('csv_path', help='Path to the dataset CSV file')
    args = parser.parse_args()

    summary = analyze_dataset(args.csv_path)
    print('Dataset summary:')
    print(f"Rows: {summary['rows']}")
    print(f"Columns: {summary['columns']}")
    print(f"Missing values: {summary['missing_values']}")
    print(f"Target distribution: {summary['target_distribution']}")
    print(summary['target_definition'])


if __name__ == '__main__':
    main()
