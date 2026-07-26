# network-anomaly-detection-random-forest
Machine Learning-based Network Anomaly Detection using Random Forest, CICIDS2017 and a Python GUI developed as a Bachelor's Thesis.
# Network Anomaly Detection Using Machine Learning

## Overview

This project was developed as my Bachelor's Thesis at **Wroclaw University of Horyzont Applied Informatics**.

The objective of this project is to develop a machine learning-based anomaly detection system capable of identifying malicious network traffic using the Random Forest algorithm trained on the CICIDS2017 dataset.

A graphical interface developed in Python demonstrates the complete detection workflow, including packet analysis, anomaly detection, attack classification, risk evaluation, and alert generation.

---

## Features

- Random Forest Classifier
- Network Traffic Analysis
- CICIDS2017 Dataset
- Python Tkinter GUI
- Attack Detection
- Risk Level Assessment
- Detection Log Generation
- Kali Linux Demonstration

---

## Technologies

- Python
- Scikit-learn
- Pandas
- NumPy
- Joblib
- Tkinter
- Kali Linux
- CICIDS2017

---

## Project Structure

```
src/
│
├── thesis_demo.py
├── train_model.py
├── detect.py
└── detect_cicids.py

model/
│
└── rf_model.joblib

screenshots/

docs/
```

---

## Demonstration

The graphical application demonstrates:

- Loading the trained Random Forest model
- Analysing network traffic
- Detecting anomalous behaviour
- Classifying attacks
- Displaying the risk level
- Generating detection logs

---

## Results

Dataset:

- CICIDS2017

Machine Learning Algorithm:

- Random Forest

Performance:

- Accuracy: 99.99%

---

## Future Improvements

- Real-time packet capture using PyShark
- Live dashboard
- Multiple attack classification
- SIEM integration
- Threat intelligence support

---

## Author

Umutcan Kargın

Bachelor of Computer Engineering

Cybersecurity • Machine Learning • Network Security
