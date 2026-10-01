# Architecture

## Current live-detection pipeline

```text
Network interface
      |
      v
PyShark / TShark
      |
      v
TCP/UDP filtering
      |
      v
Feature extraction
(packet length, source port)
      |
      v
Random Forest
(binary prediction)
      |
      +---- 0 ----> Normal traffic
      |
      +---- 1 ----> Contextual heuristic label
                         |
                         v
                    Alert log
```

## Design boundary

The Random Forest output and the contextual label are deliberately separated.

The model answers: **Does this two-feature observation look anomalous according to the trained binary model?**

The contextual layer answers: **What network context can be displayed to make the demo easier to interpret?**

The contextual layer is not a validated multiclass attack classifier.

## Planned evolution

Future iterations will introduce reproducible training, richer flow-level features,
evaluation artifacts, structured event output, SIEM/XDR integration, cloud
telemetry, and security automation.
