#!/usr/bin/env python3
"""
Real-time network anomaly detection demo.

The bundled legacy Random Forest performs binary anomaly inference with two
live values: packet length and source port. The serialized model was fitted
with generic column names (feature1, feature2), so inference preserves those
names for scikit-learn compatibility.

Human-readable labels are heuristic context only; they are not multiclass
Random Forest predictions. The historical training provenance of the bundled
model is not treated as a reproducible evaluation result.
"""

import datetime
import os

import joblib
import pandas as pd
import pyshark

from events import append_jsonl, build_detection_event

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "model", "rf_model.joblib")
LOG_FILE = os.path.join(PROJECT_ROOT, "alerts_log.txt")
EVENTS_FILE = os.path.join(PROJECT_ROOT, "events.jsonl")
INTERFACE = os.getenv("NAD_INTERFACE", "eth0")

print("[INFO] Starting real-time network anomaly detector")
print(f"[INFO] Loading model from: {MODEL_PATH}")
model = joblib.load(MODEL_PATH)
print("[INFO] Model loaded successfully")


def log_event(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} - {message}\n")


def extract_features(packet):
    """Return a one-row DataFrame compatible with the bundled legacy model."""
    try:
        protocol = packet.transport_layer
        if protocol not in ("TCP", "UDP"):
            return None

        packet_length = float(packet.length)
        source_port = float(packet[protocol].srcport)

        # The legacy artifact was fitted with these generic column names.
        # Live extraction maps feature1 -> packet length and feature2 -> source
        # port to preserve the historical demo contract without claiming that
        # the original training pipeline is reproducible from this repository.
        return pd.DataFrame(
            [[packet_length, source_port]],
            columns=["feature1", "feature2"],
        )
    except (AttributeError, KeyError, TypeError, ValueError):
        return None


def get_source(packet):
    source_ip = "unknown"
    source_port_text = "unknown"
    source_port_int = None

    try:
        if "IP" in packet:
            source_ip = packet.ip.src
        elif "IPv6" in packet:
            source_ip = packet.ipv6.src
    except (AttributeError, KeyError):
        pass

    try:
        protocol = packet.transport_layer
        if protocol:
            source_port_text = packet[protocol].srcport
            source_port_int = int(source_port_text)
    except (AttributeError, KeyError, TypeError, ValueError):
        pass

    return source_ip, source_port_text, source_port_int


def contextual_label(packet, source_port_int, prediction):
    """Return a heuristic demo label, separate from the ML prediction."""
    try:
        if hasattr(packet, "tcp") and "0x002" in str(packet.tcp.flags):
            return "Possible TCP SYN / scan activity"
    except AttributeError:
        pass

    if hasattr(packet, "udp") and prediction == 1:
        return "Anomalous UDP traffic"

    if source_port_int is not None and source_port_int > 1024 and prediction == 1:
        return "Anomalous high-source-port traffic"

    if prediction == 1:
        return "ML anomaly"

    return None


print(f"[INFO] Listening on interface: {INTERFACE}")
capture = pyshark.LiveCapture(interface=INTERFACE)
print("[INFO] Sniffing started. Press Ctrl+C to stop.\n")

try:
    for packet in capture.sniff_continuously():
        features = extract_features(packet)
        if features is None:
            continue

        source_ip, source_port_text, source_port_int = get_source(packet)

        try:
            prediction = model.predict(features)[0]
        except (ValueError, TypeError) as error:
            print(f"[ERROR] Prediction failed: {error}")
            continue

        label = contextual_label(packet, source_port_int, prediction)

        if prediction == 1:
            message = (
                f"{label or 'ML anomaly'} detected from "
                f"{source_ip}:{source_port_text} [prediction={prediction}]"
            )
            print(f"[ALERT] {message}")
            log_event(message)

            protocol = packet.transport_layer or "unknown"
            packet_length = int(float(packet.length))
            event = build_detection_event(
                source_ip=source_ip,
                source_port=source_port_int,
                protocol=protocol,
                packet_length=packet_length,
                prediction=prediction,
                contextual_label=label,
            )
            append_jsonl(EVENTS_FILE, event)
        else:
            print("[OK] Normal traffic")

except KeyboardInterrupt:
    print("\n[INFO] Stopped by user.")
