#!/usr/bin/env python3
"""Reproducible baseline trainer for the repository's two-feature binary model.

Expected CSV columns:
    packet_length, source_port, label

The full CICIDS2017 preprocessing pipeline is intentionally not invented here.
Prepare/export a binary training CSV that follows the documented schema, then
run this script to train and evaluate the baseline model.
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from feature_schema import FEATURE_NAMES

LABEL_COLUMN = "label"


def parse_args():
    parser = argparse.ArgumentParser(description="Train the binary Random Forest baseline.")
    parser.add_argument("--input", required=True, help="Training CSV path.")
    parser.add_argument("--model-out", default="model/rf_model_retrained.joblib")
    parser.add_argument("--metrics-out", default="results/metrics.json")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main():
    args = parse_args()
    dataframe = pd.read_csv(args.input)
    dataframe.columns = dataframe.columns.str.strip()

    required = list(FEATURE_NAMES) + [LABEL_COLUMN]
    missing = [column for column in required if column not in dataframe.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    X = dataframe.loc[:, FEATURE_NAMES]
    y = dataframe[LABEL_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=args.random_state,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": roc_auc_score(y_test, probabilities),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "features": list(FEATURE_NAMES),
        "random_state": args.random_state,
    }

    model_path = Path(args.model_out)
    metrics_path = Path(args.metrics_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    print(f"Model saved to {model_path}")
    print(f"Metrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
