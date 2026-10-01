#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


FEATURES = [
    "Destination Port",
    "Bwd Packet Length Max",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "Average Packet Size",
    "Avg Bwd Segment Size",
    "Max Packet Length",
]

LABEL = "Label"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Preprocess CICIDS2017 for binary anomaly detection."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chunksize", type=int, default=50000)
    return parser.parse_args()


def main():
    args = parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_csv = output_dir / "cicids2017_binary.csv"
    report_file = output_dir / "preprocessing_report.json"

    files = sorted(input_dir.glob("*.csv"))

    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    if output_csv.exists():
        output_csv.unlink()

    raw_rows = 0
    clean_rows = 0
    removed_rows = 0
    benign_rows = 0
    attack_rows = 0
    first_write = True

    usecols = FEATURES + [LABEL]

    print(f"Found {len(files)} CICIDS2017 CSV files.")

    for file in files:
        print(f"\nProcessing: {file.name}")

        file_raw = 0
        file_clean = 0

        for chunk in pd.read_csv(
            file,
            usecols=lambda c: c.strip() in usecols,
            chunksize=args.chunksize,
            low_memory=False,
        ):
            chunk.columns = chunk.columns.str.strip()

            missing = [column for column in usecols if column not in chunk.columns]
            if missing:
                raise ValueError(
                    f"{file.name} is missing required columns: {missing}"
                )

            file_raw += len(chunk)
            raw_rows += len(chunk)

            labels = chunk[LABEL].astype(str).str.strip()

            features = chunk[FEATURES].apply(
                pd.to_numeric,
                errors="coerce",
            )

            features = features.replace(
                [np.inf, -np.inf],
                np.nan,
            )

            valid = ~features.isna().any(axis=1)

            features = features.loc[valid].copy()
            labels = labels.loc[valid]

            binary_labels = (
                labels.str.upper() != "BENIGN"
            ).astype("int8")

            features.columns = [
                column.lower().replace(" ", "_")
                for column in FEATURES
            ]

            features["label"] = binary_labels.to_numpy()

            benign_rows += int((binary_labels == 0).sum())
            attack_rows += int((binary_labels == 1).sum())

            clean_rows += len(features)
            file_clean += len(features)

            features.to_csv(
                output_csv,
                mode="w" if first_write else "a",
                header=first_write,
                index=False,
            )

            first_write = False

        file_removed = file_raw - file_clean
        removed_rows += file_removed

        print(f"  Raw rows:     {file_raw:,}")
        print(f"  Clean rows:   {file_clean:,}")
        print(f"  Removed rows: {file_removed:,}")

    report = {
        "source": "CICIDS2017 MachineLearningCVE",
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "removed_rows": removed_rows,
        "benign_rows": benign_rows,
        "attack_rows": attack_rows,
        "features": FEATURES,
        "feature_count": len(FEATURES),
        "label_mapping": {
            "BENIGN": 0,
            "ATTACK": 1,
        },
        "output": str(output_csv),
    }

    report_file.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    print(f"Raw rows:     {raw_rows:,}")
    print(f"Clean rows:   {clean_rows:,}")
    print(f"Removed rows: {removed_rows:,}")
    print(f"BENIGN:       {benign_rows:,}")
    print(f"ATTACK:       {attack_rows:,}")
    print()
    print(f"Dataset: {output_csv}")
    print(f"Report:  {report_file}")


if __name__ == "__main__":
    main()
