"""Structured detection event helpers.

The JSONL schema is intentionally vendor-neutral so events can later be mapped
to a SIEM/XDR ingestion format without coupling the detector to one platform.
"""

import datetime
import json


def build_detection_event(
    source_ip,
    source_port,
    protocol,
    packet_length,
    prediction,
    contextual_label=None,
):
    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event_type": "network_anomaly_detection",
        "source": {
            "ip": source_ip,
            "port": source_port,
        },
        "network": {
            "transport": protocol,
            "packet_length": packet_length,
        },
        "ml": {
            "prediction": int(prediction),
            "is_anomaly": bool(int(prediction) == 1),
            "model_type": "random_forest",
        },
        "contextual_label": contextual_label,
        "schema_version": "1.0",
    }


def append_jsonl(path, event):
    with open(path, "a", encoding="utf-8") as output:
        output.write(json.dumps(event, separators=(",", ":")) + "\n")
