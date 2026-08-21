#!/usr/bin/env python3
"""
Real-time IDS using CICIDS2017 attack labels.
Model: rf_model_cicids.joblib
"""

import pyshark
import joblib
import numpy as np
import datetime
import os

print("[INFO] Starting CICIDS-based real-time IDS")

# 1) CICIDS modelini yükle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "rf_model_cicids.joblib")

print(f"[INFO] Loading CICIDS model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print("[INFO] CICIDS model loaded successfully")

# 2) Log dosyası
LOG_FILE = os.path.join(BASE_DIR, "alerts_log_cicids.txt")

def log_event(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} - {msg}\n")

# 3) Özellik çıkarma
# DİKKAT: Burayı Kaggle’da modeli eğittiğin feature sayısına göre
# güncellememiz gerekecek.
def extract_features(packet):
    try:
        proto = packet.transport_layer
        if proto not in ("TCP", "UDP"):
            return None

        length = float(packet.length)
        src_port = float(packet[proto].srcport)

        X = np.array([[length, src_port]])  # Şimdilik 2 feature
        return X
    except Exception:
        return None

# 4) Saldırgan bilgisi
def get_attacker_info(packet):
    src_ip = "unknown"
    try:
        if "IP" in packet:
            src_ip = packet.ip.src
        elif "IPv6" in packet:
            src_ip = packet.ipv6.src
    except:
        pass

    src_port = "unknown"
    try:
        if hasattr(packet, "transport_layer"):
            src_port = packet[packet.transport_layer].srcport
    except:
        pass

    return src_ip, src_port

# 5) CICIDS label → aile ismi
CICIDS_FAMILY_MAP = {
    "BENIGN": "Benign",
    "DoS Hulk": "DoS",
    "DoS GoldenEye": "DoS",
    "DoS slowloris": "DoS",
    "DoS slowhttptest": "DoS",
    "DDoS": "DDoS",
    "PortScan": "PortScan",
    "FTP-Patator": "Brute Force",
    "SSH-Patator": "Brute Force",
    "Bot": "Botnet",
    "Web Attack – Brute Force": "Web Attack",
    "Web Attack – XSS": "Web Attack",
    "Web Attack – Sql Injection": "Web Attack",
    "Infiltration": "Infiltration",
}

def get_attack_name_from_cicids(label: str):
    if label == "BENIGN":
        return None
    family = CICIDS_FAMILY_MAP.get(label, "Unknown CICIDS Attack")
    return f"{family} ({label})"

# 6) Canlı dinleme
INTERFACE = "eth0"

print(f"[INFO] Listening on interface: {INTERFACE}")
capture = pyshark.LiveCapture(interface=INTERFACE)
print("[INFO] Sniffing started. Press Ctrl+C to stop.\n")

try:
    for packet in capture.sniff_continuously():
        X = extract_features(packet)
        if X is None:
            continue

        src_ip, src_port = get_attacker_info(packet)

        try:
            label = model.predict(X)[0]  # Örn: "DoS Hulk", "BENIGN", "PortScan"
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            continue

        attack_name = get_attack_name_from_cicids(str(label))

        if attack_name is not None:
            msg = f"{attack_name} detected from {src_ip}:{src_port}"
            print(f"🔴 {msg}")
            log_event(msg)
        else:
            print("🟢 Normal Traffic")

except KeyboardInterrupt:
    print("\n[INFO] Stopped by user.")
