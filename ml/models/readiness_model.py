from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from ml.preprocessing.preprocess import FEATURE_COLUMNS, build_feature_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / 'ml' / 'models' / 'artifacts'
MODEL_PATH = ARTIFACT_DIR / 'readiness_pipeline.joblib'
LABEL_ENCODER_PATH = ARTIFACT_DIR / 'readiness_label_encoder.joblib'
METADATA_PATH = ARTIFACT_DIR / 'readiness_model_metadata.json'


def build_readiness_pipeline() -> Pipeline:
    numeric_features = [
        column for column in FEATURE_COLUMNS
        if column not in {'fitness_level', 'goal'}
    ]
    categorical_features = ['fitness_level', 'goal']

    preprocessor = ColumnTransformer(
        transformers=[
            (
                'numeric',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                ]),
                numeric_features,
            ),
            (
                'categorical',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='most_frequent')),
                    ('onehot', OneHotEncoder(handle_unknown='ignore')),
                ]),
                categorical_features,
            ),
        ],
        remainder='drop',
    )

    return Pipeline([
        ('preprocessor', preprocessor),
        ('model', DecisionTreeClassifier(max_depth=6, random_state=42)),
    ])


def train_and_save_model(dataset_path: str | Path) -> dict[str, Any]:
    dataset = pd.read_csv(dataset_path)
    features, target = build_feature_matrix(dataset)

    label_encoder = LabelEncoder()
    encoded_target = label_encoder.fit_transform(target)
    pipeline = build_readiness_pipeline()
    pipeline.fit(features, encoded_target)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    metadata = {
        'dataset_path': str(Path(dataset_path)),
        'target_column': 'readiness_level',
        'target_source': 'derived by ml.preprocessing.preprocess.derive_readiness_level',
        'feature_columns': list(features.columns),
        'classes': label_encoder.classes_.tolist(),
        'training_rows': int(len(features)),
        'model': 'DecisionTreeClassifier(max_depth=6, random_state=42)',
        'leakage_check': {
            'target_excluded_from_features': 'readiness_level' not in features.columns,
            'target_derived_from': [
                'sleep_hours',
                'fatigue_score',
                'previous_workout_intensity',
                'recovery_score',
            ],
        },
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    return metadata


def load_readiness_model() -> tuple[Pipeline, LabelEncoder]:
    if not MODEL_PATH.exists() or not LABEL_ENCODER_PATH.exists():
        raise FileNotFoundError(
            f'Readiness model artifacts are missing. Run: '
            f'python -m ml.models.train_readiness_model data/raw/fitness_dataset.csv'
        )

    return joblib.load(MODEL_PATH), joblib.load(LABEL_ENCODER_PATH)
