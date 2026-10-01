#!/usr/bin/env python3

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

METRICS_PATH = Path("results/cicids2017_metrics.json")
OUTPUT_DIR = Path("results/figures")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metrics = json.loads(
        METRICS_PATH.read_text(encoding="utf-8")
    )

    # Confusion matrix
    cm = np.array(metrics["confusion_matrix"])

    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(cm)

    ax.set_title("CICIDS2017 - Confusion Matrix")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_xticks([0, 1], labels=["BENIGN", "ATTACK"])
    ax.set_yticks([0, 1], labels=["BENIGN", "ATTACK"])

    for i in range(2):
        for j in range(2):
            ax.text(
                j,
                i,
                f"{cm[i, j]:,}",
                ha="center",
                va="center",
            )

    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "confusion_matrix.png",
        dpi=160,
    )
    plt.close(fig)

    # Feature importance
    importance = metrics["feature_importance"]

    features = list(importance.keys())[::-1]
    values = list(importance.values())[::-1]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(features, values)

    ax.set_title(
        "CICIDS2017 Random Forest - Feature Importance"
    )
    ax.set_xlabel("Importance")

    fig.tight_layout()
    fig.savefig(
        OUTPUT_DIR / "feature_importance.png",
        dpi=160,
    )
    plt.close(fig)

    print("Generated:")
    print(OUTPUT_DIR / "confusion_matrix.png")
    print(OUTPUT_DIR / "feature_importance.png")


if __name__ == "__main__":
    main()
