"""Shared feature schema for the current two-feature demo model."""

FEATURE_NAMES = ("packet_length", "source_port")


def validate_feature_columns(columns) -> None:
    """Raise a clear error when a CSV does not match the model input schema."""
    actual = tuple(columns)
    if actual != FEATURE_NAMES:
        raise ValueError(
            "Feature mismatch. Expected columns "
            f"{list(FEATURE_NAMES)}, received {list(actual)}."
        )
