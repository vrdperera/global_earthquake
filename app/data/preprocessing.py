"""Parsing, classification, filtering, and aggregation logic."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

EARTHQUAKE_COLUMNS = [
    "event_id",
    "time",
    "latitude",
    "longitude",
    "depth",
    "magnitude",
    "place",
    "event_type",
    "url",
]


def classify_severity(magnitude: float | None) -> str:
    """Classify magnitude using commonly used descriptive bands."""

    if magnitude is None or pd.isna(magnitude):
        return "Unknown"
    if magnitude < 4.0:
        return "Minor"
    if magnitude < 5.0:
        return "Light"
    if magnitude < 6.0:
        return "Moderate"
    if magnitude < 7.0:
        return "Strong"
    if magnitude < 8.0:
        return "Major"
    return "Great"


def classify_depth(depth: float | None) -> str:
    """Classify focal depth in kilometres."""

    if depth is None or pd.isna(depth):
        return "Unknown"
    if depth < 70:
        return "Shallow"
    if depth < 300:
        return "Intermediate"
    return "Deep"


def parse_usgs_geojson(payload: dict[str, Any]) -> pd.DataFrame:
    """Turn a USGS feature collection into a clean earthquake DataFrame."""

    rows: list[dict[str, Any]] = []
    for feature in payload.get("features", []):
        geometry = feature.get("geometry") or {}
        coordinates = geometry.get("coordinates") or []
        properties = feature.get("properties") or {}
        if len(coordinates) < 3:
            continue
        rows.append(
            {
                "event_id": feature.get("id", "Unknown"),
                "time": pd.to_datetime(properties.get("time"), unit="ms", utc=True, errors="coerce"),
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "depth": coordinates[2],
                "magnitude": properties.get("mag"),
                "place": properties.get("place") or "Unknown location",
                "event_type": properties.get("type") or "unknown",
                "url": properties.get("url") or "",
            }
        )

    frame = pd.DataFrame(rows, columns=EARTHQUAKE_COLUMNS)
    if frame.empty:
        return frame.assign(
            severity=pd.Series(dtype="object"),
            depth_class=pd.Series(dtype="object"),
        )

    numeric = ["latitude", "longitude", "depth", "magnitude"]
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="coerce")
    frame = frame.dropna(subset=["time", "latitude", "longitude", "depth", "magnitude"])
    frame = frame[
        frame["latitude"].between(-90, 90) & frame["longitude"].between(-180, 180)
    ].copy()
    frame["severity"] = frame["magnitude"].map(classify_severity)
    frame["depth_class"] = frame["depth"].map(classify_depth)
    return frame.sort_values("time", ascending=False).reset_index(drop=True)


def filter_earthquakes(
    frame: pd.DataFrame,
    *,
    magnitude_range: tuple[float, float],
    depth_range: tuple[float, float],
    date_range: tuple[pd.Timestamp, pd.Timestamp],
    country: str = "All countries",
    severity: str = "All severities",
) -> pd.DataFrame:
    """Apply all dashboard filters with inclusive date bounds."""

    if frame.empty:
        return frame.copy()
    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1])
    if start.tzinfo is None:
        start = start.tz_localize("UTC")
    else:
        start = start.tz_convert("UTC")
    if end.tzinfo is None:
        end = end.tz_localize("UTC")
    else:
        end = end.tz_convert("UTC")
    if end == end.normalize():
        end = end + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    mask = (
        frame["magnitude"].between(*magnitude_range)
        & frame["depth"].between(*depth_range)
        & frame["time"].between(start, end)
    )
    if country != "All countries":
        mask &= frame["country"].eq(country)
    if severity != "All severities":
        mask &= frame["severity"].eq(severity)
    return frame.loc[mask].copy()


def aggregate_by_country(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute the required country-level earthquake statistics."""

    columns = [
        "country",
        "earthquake_count",
        "average_magnitude",
        "maximum_magnitude",
        "average_depth",
    ]
    if frame.empty or "country" not in frame:
        return pd.DataFrame(columns=columns)
    valid = frame[frame["country"].notna() & frame["country"].ne("Ocean / Unassigned")]
    if valid.empty:
        return pd.DataFrame(columns=columns)
    result = (
        valid.groupby("country", observed=True)
        .agg(
            earthquake_count=("event_id", "count"),
            average_magnitude=("magnitude", "mean"),
            maximum_magnitude=("magnitude", "max"),
            average_depth=("depth", "mean"),
        )
        .reset_index()
    )
    result[["average_magnitude", "maximum_magnitude", "average_depth"]] = result[
        ["average_magnitude", "maximum_magnitude", "average_depth"]
    ].replace([np.inf, -np.inf], np.nan)
    return result
