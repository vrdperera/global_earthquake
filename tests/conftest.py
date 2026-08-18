from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def earthquake_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": ["a", "b", "c"],
            "time": pd.to_datetime(
                ["2026-08-01T10:00:00Z", "2026-08-02T10:00:00Z", "2026-08-03T10:00:00Z"],
                utc=True,
            ),
            "latitude": [35.0, -6.0, 38.0],
            "longitude": [139.0, 106.0, -122.0],
            "depth": [20.0, 120.0, 310.0],
            "magnitude": [3.2, 5.4, 7.1],
            "place": ["Japan", "Indonesia", "California"],
            "event_type": ["earthquake"] * 3,
            "url": [""] * 3,
            "severity": ["Minor", "Moderate", "Major"],
            "depth_class": ["Shallow", "Intermediate", "Deep"],
            "country": ["Japan", "Indonesia", "United States of America"],
        }
    )
