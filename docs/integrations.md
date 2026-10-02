# SIEM / XDR Integration Direction

The live detector now supports a vendor-neutral JSONL event contract.

Example:

```json
{
  "timestamp": "2026-10-01T12:00:00+00:00",
  "event_type": "network_anomaly_detection",
  "source": {"ip": "192.0.2.10", "port": 5353},
  "network": {"transport": "UDP", "packet_length": 120},
  "ml": {
    "prediction": 1,
    "is_anomaly": true,
    "model_type": "random_forest"
  },
  "contextual_label": "Anomalous UDP traffic",
  "schema_version": "1.0"
}
```

## Why vendor-neutral first?

The detector should own its event semantics. A separate integration layer can
later map these fields to a target SIEM/XDR schema.

This makes future work possible for:

- Cortex XSIAM/XDR ingestion experiments
- syslog/CEF-style forwarding
- cloud log pipelines
- alert enrichment and automation
- AI-assisted incident investigation

No Palo Alto Networks product integration is claimed in the current version.
