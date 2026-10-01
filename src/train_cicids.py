#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


LABEL = "label"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train CICIDS2017 binary Random Forest."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--model-out",
        default="model/rf_cicids2017.joblib",
    )
    parser.add_argument(
        "--metrics-out",
        default="results/cicids2017_metrics.json",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=600000,
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.20,
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("Loading processed CICIDS2017 dataset...")
    df = pd.read_csv(args.input)

    if LABEL not in df.columns:
        raise ValueError("Missing label column.")

    print(f"Available rows: {len(df):,}")

    if len(df) > args.max_rows:
        print(
            f"Sampling {args.max_rows:,} rows "
            "while preserving class distribution..."
        )

        benign = df[df[LABEL] == 0]
        attack = df[df[LABEL] == 1]

        attack_ratio = len(attack) / len(df)

        attack_n = round(args.max_rows * attack_ratio)
        benign_n = args.max_rows - attack_n

        benign = benign.sample(
            n=min(benign_n, len(benign)),
            random_state=args.random_state,
        )

        attack = attack.sample(
            n=min(attack_n, len(attack)),
            random_state=args.random_state,
        )

        df = pd.concat(
            [benign, attack],
            ignore_index=True,
        ).sample(
            frac=1,
            random_state=args.random_state,
        ).reset_index(drop=True)

    X = df.drop(columns=[LABEL])
    y = df[LABEL].astype("int8")

    print(f"Training dataset: {len(df):,} rows")
    print(f"Features: {X.shape[1]}")
    print(f"BENIGN: {(y == 0).sum():,}")
    print(f"ATTACK: {(y == 1).sum():,}")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    print()
    print(f"Train rows: {len(X_train):,}")
    print(f"Test rows:  {len(X_test):,}")

    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=None,
        min_samples_split=2,
        class_weight="balanced",
        random_state=args.random_state,
        n_jobs=1,
    )

    print("\nTraining Random Forest...")
    model.fit(X_train, y_train)

    print("Evaluating model...")

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    cm = confusion_matrix(y_test, predictions)

    metrics = {
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "precision": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_test,
                probabilities,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_test,
                probabilities,
            )
        ),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=["BENIGN", "ATTACK"],
            output_dict=True,
            zero_division=0,
        ),
        "training_rows": len(X_train),
        "test_rows": len(X_test),
        "sample_rows": len(df),
        "features": list(X.columns),
        "feature_importance": {
            feature: float(importance)
            for feature, importance in sorted(
                zip(
                    X.columns,
                    model.feature_importances_,
                ),
                key=lambda item: item[1],
                reverse=True,
            )
        },
        "random_state": args.random_state,
    }

    model_path = Path(args.model_out)
    metrics_path = Path(args.metrics_out)

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    metrics_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(model, model_path)

    metrics_path.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print(f"Accuracy:  {metrics['accuracy']:.6f}")
    print(f"Precision: {metrics['precision']:.6f}")
    print(f"Recall:    {metrics['recall']:.6f}")
    print(f"F1:        {metrics['f1']:.6f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.6f}")
    print(f"PR-AUC:    {metrics['pr_auc']:.6f}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nTop Feature Importance:")
    for feature, importance in list(
        metrics["feature_importance"].items()
    )[:10]:
        print(f"{feature:<35} {importance:.6f}")

    print(f"\nModel:   {model_path}")
    print(f"Metrics: {metrics_path}")


if __name__ == "__main__":
    main()
