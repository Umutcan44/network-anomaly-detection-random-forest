# Training and Evaluation

The original thesis training environment is not fully represented in this repository yet.
For that reason, this project does **not** claim that the new `train_model.py` exactly
recreates the historical thesis model.

Instead, `src/train_model.py` provides a reproducible baseline for the current live
two-feature schema.

## Expected training input

Prepare a CSV with:

```text
packet_length,source_port,label
74,443,0
1500,5353,1
60,22,0
```

Where:

- `0` = benign
- `1` = anomaly

Run:

```bash
python src/train_model.py --input path/to/training.csv
```

The script writes:

- `model/rf_model_retrained.joblib`
- `results/metrics.json`

The metrics include accuracy, precision, recall, F1, ROC-AUC, and a confusion matrix.

## CICIDS2017

A future iteration will reconstruct and document the exact mapping from CICIDS2017
flow columns to the feature schema used by the live detector. Until that work is
verified, the repository deliberately avoids claiming full end-to-end CICIDS2017
reproducibility.
