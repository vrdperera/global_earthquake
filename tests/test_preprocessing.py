from __future__ import annotations

import pandas as pd

from app.data.preprocessing import (
    aggregate_by_country,
    classify_severity,
    filter_earthquakes,
    parse_usgs_geojson,
)


def test_parse_usgs_response_extracts_expected_fields() -> None:
    payload = {
        "features": [
            {
                "id": "us7000test",
                "geometry": {"coordinates": [139.7, 35.6, 28.3]},
                "properties": {
                    "time": 1_775_681_520_000,
                    "mag": 6.4,
                    "place": "Near Japan",
                    "type": "earthquake",
                    "url": "https://earthquake.usgs.gov/example",
                },
            }
        ]
    }
    result = parse_usgs_geojson(payload)
    assert len(result) == 1
    assert result.loc[0, "event_id"] == "us7000test"
    assert result.loc[0, "longitude"] == 139.7
    assert result.loc[0, "depth"] == 28.3
    assert result.loc[0, "severity"] == "Strong"
    assert str(result.loc[0, "time"].tz) == "UTC"


def test_parse_ignores_invalid_coordinates_and_handles_empty() -> None:
    malformed = {"features": [{"id": "bad", "geometry": {"coordinates": []}, "properties": {}}]}
    result = parse_usgs_geojson(malformed)
    assert result.empty
    assert "severity" in result.columns


def test_magnitude_filter(earthquake_frame: pd.DataFrame) -> None:
    result = filter_earthquakes(
        earthquake_frame,
        magnitude_range=(5.0, 8.0),
        depth_range=(0, 700),
        date_range=(pd.Timestamp("2026-08-01"), pd.Timestamp("2026-08-03")),
    )
    assert result["event_id"].tolist() == ["b", "c"]


def test_depth_filter(earthquake_frame: pd.DataFrame) -> None:
    result = filter_earthquakes(
        earthquake_frame,
        magnitude_range=(0, 10),
        depth_range=(0, 100),
        date_range=(pd.Timestamp("2026-08-01"), pd.Timestamp("2026-08-03")),
    )
    assert result["event_id"].tolist() == ["a"]


def test_country_aggregation(earthquake_frame: pd.DataFrame) -> None:
    duplicated = pd.concat([earthquake_frame, earthquake_frame.iloc[[0]]], ignore_index=True)
    result = aggregate_by_country(duplicated).set_index("country")
    assert result.loc["Japan", "earthquake_count"] == 2
    assert result.loc["Japan", "average_magnitude"] == 3.2
    assert result.loc["Indonesia", "maximum_magnitude"] == 5.4
    assert result.loc["United States of America", "average_depth"] == 310.0


def test_severity_classification_boundaries() -> None:
    assert classify_severity(2.5) == "Minor"
    assert classify_severity(4.0) == "Light"
    assert classify_severity(5.0) == "Moderate"
    assert classify_severity(6.0) == "Strong"
    assert classify_severity(7.0) == "Major"
    assert classify_severity(8.0) == "Great"


def test_empty_filter_and_aggregation(earthquake_frame: pd.DataFrame) -> None:
    filtered = filter_earthquakes(
        earthquake_frame.iloc[0:0],
        magnitude_range=(0, 10),
        depth_range=(0, 700),
        date_range=(pd.Timestamp("2026-08-01"), pd.Timestamp("2026-08-03")),
    )
    assert filtered.empty
    assert aggregate_by_country(filtered).empty
