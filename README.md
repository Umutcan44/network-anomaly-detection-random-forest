# Real-Time Network Anomaly Detection

A machine-learning network intrusion detection prototype combining Random Forest classification with live packet capture using PyShark.

Originally developed as a Bachelor's Thesis project, this repository is being refactored into a reproducible security engineering portfolio project.

## Overview

The project has two main stages:

1. **Offline model development** using network traffic data derived from CICIDS2017.
2. **Real-time detection** on Linux using PyShark for packet capture, lightweight feature extraction, Random Forest inference, and alert logging.

> **Important:** The current live Random Forest model performs binary anomaly detection. Human-readable attack names shown by the live detector are heuristic contextual labels and must not be interpreted as multiclass ML predictions.

## Architecture

```text
CICIDS2017 / training data
          |
          v
Data preprocessing & feature selection
          |
          v
Random Forest training
          |
          v
Serialized model artifact
          |
          v
PyShark live packet capture
          |
          v
Feature extraction
          |
          v
Binary anomaly prediction
          |
          v
Contextual labeling + alert logging
```

See `docs/architecture.md` for design notes and `docs/training.md` for the reproducible baseline training contract.

## Key Capabilities

- Random Forest-based binary anomaly detection
- Live TCP/UDP packet capture with PyShark
- Automated feature extraction
- Real-time console alerts
- Detection event logging
- Tkinter-based thesis demonstration interface
- Linux/Kali Linux demonstration workflow

## Technology Stack

- Python
- scikit-learn
- pandas
- NumPy
- Joblib
- PyShark / TShark
- Tkinter
- CICIDS2017

## Repository Structure

```text
.
├── data/                  # Small safe sample inputs only
├── docs/                  # Architecture notes and screenshots
├── model/                 # Serialized demo model
├── results/               # Evaluation notes/results
├── src/                   # Detection, training, schema, and demo source code
├── README.md
├── requirements.txt
└── LICENSE
```

## Installation

Python 3.10+ is recommended.

```bash
git clone https://github.com/Umutcan44/network-anomaly-detection-random-forest.git
cd network-anomaly-detection-random-forest

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

PyShark also requires TShark/Wireshark to be installed on the host operating system.

## Real-Time Detection

The live detector currently extracts two features:

- packet length
- source port

It then runs binary Random Forest inference and records suspicious events.

The network interface is currently configured as `eth0` in the detector and should be changed to match the host system before execution.

```bash
sudo python src/detect.py
```

## Batch Demo

A desktop batch-inference demo is available with:

```bash
python src/thesis_demo.py
```

It validates the CSV feature schema before inference. The included sample CSV is intended to demonstrate input shape, not model quality.

## Reproducible Baseline Training

The repository now includes `src/train_model.py` for retraining a two-feature binary Random Forest baseline from a prepared CSV.

```bash
python src/train_model.py --input path/to/training.csv
```

See `docs/training.md` for the required schema and an explicit explanation of what is and is not currently reproducible from the original thesis environment.

## Model and Detection Limitations

This repository is a research/portfolio prototype, not a production IDS.

Current limitations include:

- The live model uses a small two-feature representation.
- Binary anomaly detection does not identify a definitive attack family.
- Contextual labels such as `Port Scan` or `UDP Flood Attempt` are heuristic demo labels.
- A single UDP packet is not sufficient evidence of a DDoS attack in a production environment.
- Production deployment would require flow aggregation, richer telemetry, calibrated thresholds, testing, monitoring, and SIEM/XDR integration.

## Results

The thesis evaluation used CICIDS2017 and Random Forest. Detailed, reproducible metrics and evaluation artifacts will be added under `results/`.

Accuracy alone is not treated as sufficient evidence for IDS quality; future repository updates will document precision, recall, F1-score, ROC-AUC, confusion matrix, and class distribution where reproducible.

## Roadmap

- [x] Publish thesis prototype
- [x] Separate live detection logic from documentation
- [x] Add reproducible two-feature baseline training pipeline
- [ ] Add evaluation metrics and confusion matrix
- [ ] Add architecture diagram and screenshots
- [ ] Add configuration for capture interface and model path
- [ ] Add automated tests
- [ ] Containerize non-capture components
- [ ] Add SIEM/XDR-style event output
- [ ] Explore cloud telemetry and security automation integrations

## Responsible Use

Use this project only on networks and systems you own or are explicitly authorized to monitor.

## Author

**Umutcan Kargın**

Computer Engineering graduate focused on cybersecurity, detection engineering, security automation, and applied AI.
