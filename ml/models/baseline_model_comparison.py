from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover
    XGBClassifier = None

from ml.preprocessing.preprocess import FEATURE_COLUMNS, build_feature_matrix


MODEL_REGISTRY: dict[str, Any] = {
    'logistic_regression': LogisticRegression(max_iter=2000, class_weight='balanced', random_state=42),
    'decision_tree': DecisionTreeClassifier(max_depth=6, random_state=42),
    'random_forest': RandomForestClassifier(
        n_estimators=250,
        max_depth=None,
        random_state=42,
        class_weight='balanced_subsample',
    ),
}

if XGBClassifier is not None:
    MODEL_REGISTRY['xgboost'] = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric='mlogloss',
        random_state=42,
    )


def build_model_pipeline(model_name: str) -> Pipeline:
    numeric_features = [
        col for col in FEATURE_COLUMNS if col in FEATURE_COLUMNS and col not in {'fitness_level', 'goal'}
    ]
    categorical_features = ['fitness_level', 'goal']

    preprocessing = ColumnTransformer(
        transformers=[
            ('numeric', Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler()),
            ]), numeric_features),
            ('categorical', Pipeline([
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('onehot', OneHotEncoder(handle_unknown='ignore')),
            ]), categorical_features),
        ],
        remainder='drop',
    )

    model = MODEL_REGISTRY[model_name]
    return Pipeline([
        ('preprocessing', preprocessing),
        ('model', model),
    ])


def evaluate_model(model_name: str, X: pd.DataFrame, y: pd.Series) -> dict[str, Any]:
    label_encoder = LabelEncoder()
    encoded_y = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        encoded_y,
        test_size=0.2,
        random_state=42,
        stratify=encoded_y,
    )

    pipeline = build_model_pipeline(model_name)
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    y_true_labels = label_encoder.inverse_transform(y_test)
    y_pred_labels = label_encoder.inverse_transform(y_pred)

    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_test, y_pred, average='weighted', zero_division=0),
        'classification_report': classification_report(y_true_labels, y_pred_labels, zero_division=0),
    }
    return metrics


def compare_models(dataset_path: str | Path) -> dict[str, Any]:
    df = pd.read_csv(dataset_path)
    X, y = build_feature_matrix(df)

    model_results: dict[str, Any] = {}
    for model_name in MODEL_REGISTRY:
        model_results[model_name] = evaluate_model(model_name, X, y)

    best_model = max(
        model_results.items(),
        key=lambda item: item[1]['f1'],
    )

    return {
        'results': model_results,
        'best_model': best_model[0],
        'best_f1': best_model[1]['f1'],
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description='Train and compare baseline readiness models.')
    parser.add_argument('dataset_path', help='Path to the CSV dataset to train against.')
    args = parser.parse_args()

    results = compare_models(args.dataset_path)
    print('Best model:', results['best_model'])
    print('Best F1:', round(results['best_f1'], 4))
    print('\nModel results:')
    for model_name, metrics in results['results'].items():
        print(f'\n{model_name}:')
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"F1: {metrics['f1']:.4f}")


if __name__ == '__main__':
    main()
