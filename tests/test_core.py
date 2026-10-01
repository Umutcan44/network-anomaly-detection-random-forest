import unittest

from src.feature_schema import FEATURE_NAMES, validate_feature_columns
from src.events import build_detection_event


class FeatureSchemaTests(unittest.TestCase):
    def test_expected_schema_is_accepted(self):
        validate_feature_columns(FEATURE_NAMES)

    def test_wrong_schema_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_feature_columns(("feature1", "feature2"))


class DetectionEventTests(unittest.TestCase):
    def test_anomaly_event_has_expected_contract(self):
        event = build_detection_event(
            source_ip="192.0.2.10",
            source_port=5353,
            protocol="UDP",
            packet_length=120,
            prediction=1,
            contextual_label="Anomalous UDP traffic",
        )

        self.assertEqual(event["event_type"], "network_anomaly_detection")
        self.assertTrue(event["ml"]["is_anomaly"])
        self.assertEqual(event["source"]["port"], 5353)
        self.assertEqual(event["schema_version"], "1.0")


if __name__ == "__main__":
    unittest.main()
