#!/usr/bin/env python3

import argparse
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    PrecisionRecallDisplay,
    RocCurveDisplay,
)
from sklearn.model_selection import train_test_split


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate CICIDS2017 ROC and PR curves."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument(
        "--model",
        default="model/rf_cicids2017.joblib",
    )
    parser.add_argument(
        "--output",
        default="results/figures",
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

    print("Loading processed dataset...")
    df = pd.read_csv(args.input)

    if len(df) > args.max_rows:
        benign = df[df["label"] == 0]
        attack = df[df["label"] == 1]

        attack_ratio = len(attack) / len(df)
        attack_n = round(args.max_rows * attack_ratio)
        benign_n = args.max_rows - attack_n

        benign = benign.sample(
            n=benign_n,
            random_state=args.random_state,
        )

        attack = attack.sample(
            n=attack_n,
            random_state=args.random_state,
        )

        df = pd.concat(
            [benign, attack],
            ignore_index=True,
        ).sample(
            frac=1,
            random_state=args.random_state,
        ).reset_index(drop=True)

    X = df.drop(columns=["label"])
    y = df["label"].astype("int8")

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=y,
    )

    print(f"Test rows: {len(X_test):,}")
    print("Loading model...")

    model = joblib.load(args.model)

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    print("Generating ROC curve...")

    fig, ax = plt.subplots(figsize=(7, 6))
    RocCurveDisplay.from_estimator(
        model,
        X_test,
        y_test,
        ax=ax,
    )
    ax.set_title("CICIDS2017 - ROC Curve")
    fig.tight_layout()
    fig.savefig(
        output / "roc_curve.png",
        dpi=160,
    )
    plt.close(fig)

    print("Generating Precision-Recall curve...")

    fig, ax = plt.subplots(figsize=(7, 6))
    PrecisionRecallDisplay.from_estimator(
        model,
        X_test,
        y_test,
        ax=ax,
    )
    ax.set_title(
        "CICIDS2017 - Precision-Recall Curve"
    )
    fig.tight_layout()
    fig.savefig(
        output / "precision_recall_curve.png",
        dpi=160,
    )
    plt.close(fig)

    print("\nGenerated:")
    print(output / "roc_curve.png")
    print(output / "precision_recall_curve.png")


if __name__ == "__main__":
    main()
