#!/usr/bin/env python3
"""
Real-time IDS demo with heuristic CICIDS-style attack naming.

- Uses rf_model.joblib (binary model: classes_ = [0, 1])
- Feature vector: [packet length, source port]
- Heuristics + CICIDS-like attack labels:
    * Port Scan (CICIDS: PortScan)
    * UDP Flood Attempt (CICIDS: DDoS)
    * High-Rate Traffic / Possible Flood (CICIDS: DoS Hulk)
    * Generic ML Anomaly (CICIDS: Infiltration)
"""

import pyshark
import joblib
import numpy as np
import datetime
import os

print("[INFO] Starting real-time IDS (heuristic CICIDS naming)")

# ---------------------------------------------------------
# 1) Load binary RF model (rf_model.joblib)
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "rf_model.joblib")

print(f"[INFO] Loading model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print("[INFO] Model loaded successfully")

# ---------------------------------------------------------
# 2) Logging
# ---------------------------------------------------------
LOG_FILE = os.path.join(BASE_DIR, "alerts_log.txt")

def log_event(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{ts} - {msg}\n")

# ---------------------------------------------------------
# 3) Feature extraction: length + src_port (2 features)
# ---------------------------------------------------------
def extract_features(packet):
    try:
        proto = packet.transport_layer
        if proto not in ("TCP", "UDP"):
            return None

        length = float(packet.length)
        src_port = float(packet[proto].srcport)

        X = np.array([[length, src_port]])
        return X
    except Exception:
        return None

# ---------------------------------------------------------
# 4) Attacker info (IP + port)
# ---------------------------------------------------------
def get_attacker_info(packet):
    src_ip = "unknown"
    try:
        if "IP" in packet:
            src_ip = packet.ip.src
        elif "IPv6" in packet:
            src_ip = packet.ipv6.src
    except Exception:
        pass

    src_port_str = "unknown"
    src_port_int = None
    try:
        if hasattr(packet, "transport_layer"):
            src_port_str = packet[packet.transport_layer].srcport
            src_port_int = int(src_port_str)
    except Exception:
        pass

    return src_ip, src_port_str, src_port_int

# ---------------------------------------------------------
# 5) Heuristic attack type + CICIDS-style label
# ---------------------------------------------------------
def get_attack_and_cicids_label(packet, src_port_int, pred):
    """
    Mevcut binary model + trafik özelliklerine göre:
      - attack_name: İnsan tarafından okunabilir saldırı adı
      - cicids_label: CICIDS2017'deki en yakın saldırı etiketi (heuristic)

    Eğer saldırı yoksa (normal trafik) -> (None, None) döner.
    """

    # 1) TCP SYN → Port Scan (CICIDS: PortScan)
    try:
        if hasattr(packet, "tcp"):
            flags = str(packet.tcp.flags)
            if "0x002" in flags:  # SYN
                return "Port Scan", "PortScan"
    except Exception:
        pass

    # 2) UDP trafiği → UDP Flood Attempt (CICIDS: DDoS)
    try:
        if hasattr(packet, "udp"):
            return "UDP Flood Attempt", "DDoS"
    except Exception:
        pass

    # 3) Yüksek kaynak port → High-Rate Traffic (CICIDS: DoS Hulk)
    if src_port_int is not None and src_port_int > 1024:
        return "High-Rate Traffic / Possible Flood", "DoS Hulk"

    # 4) Model anomali (pred == 1) → Generic ML Anomaly (CICIDS: Infiltration)
    if pred == 1:
        return "Generic ML Anomaly", "Infiltration"

    # Hiçbiri değilse normal trafik
    return None, None

# ---------------------------------------------------------
# 6) Live capture loop
# ---------------------------------------------------------
INTERFACE = "eth0"

print(f"[INFO] Listening on interface: {INTERFACE}")
capture = pyshark.LiveCapture(interface=INTERFACE)
print("[INFO] Sniffing started. Press Ctrl+C to stop.\n")

try:
    for packet in capture.sniff_continuously():
        X = extract_features(packet)
        if X is None:
            continue

        src_ip, src_port_str, src_port_int = get_attacker_info(packet)

        try:
            pred = model.predict(X)[0]  # 0 = normal, 1 = anomaly (demo)
        except Exception as e:
            print(f"[ERROR] Prediction failed: {e}")
            continue

        attack_name, cicids_label = get_attack_and_cicids_label(
            packet, src_port_int, pred
        )

        if attack_name is not None:
            msg = (
                f"{attack_name} detected from {src_ip}:{src_port_str} "
                f"[CICIDS-like: {cicids_label}, pred={pred}]"
            )
            print(f"🔴 {msg}")
            log_event(msg)
        else:
            print("🟢 Normal Traffic")

except KeyboardInterrupt:
    print("\n[INFO] Stopped by user.")
