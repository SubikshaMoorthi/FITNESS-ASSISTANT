from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.models.baseline_model_comparison import compare_models
from ml.models.readiness_model import train_and_save_model


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare, train, and save the readiness model.')
    parser.add_argument('dataset_path', help='Path to the CSV dataset')
    args = parser.parse_args()

    comparison = compare_models(args.dataset_path)
    metadata = train_and_save_model(args.dataset_path)

    print('Model comparison:')
    for model_name, metrics in comparison['results'].items():
        print(
            f"{model_name}: accuracy={metrics['accuracy']:.4f}, "
            f"precision={metrics['precision']:.4f}, "
            f"recall={metrics['recall']:.4f}, f1={metrics['f1']:.4f}"
        )

    print(f"Best comparison model: {comparison['best_model']}")
    print(f"Saved model: {Path('ml/models/artifacts/readiness_pipeline.joblib')}")
    print(f"Saved features: {metadata['feature_columns']}")
    print(f"Saved classes: {metadata['classes']}")


if __name__ == '__main__':
    main()
