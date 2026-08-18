"""Bokeh widget construction."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from bokeh.models import Button, DateRangeSlider, RangeSlider, Select

METRIC_OPTIONS = [
    ("earthquake_count", "Earthquake Count"),
    ("average_magnitude", "Average Magnitude"),
    ("maximum_magnitude", "Maximum Magnitude"),
    ("average_depth", "Average Depth"),
]
SEVERITY_OPTIONS = ["All severities", "Minor", "Light", "Moderate", "Strong", "Major", "Great"]


@dataclass
class DashboardControls:
    """The complete filter widget set."""

    magnitude: RangeSlider
    depth: RangeSlider
    dates: DateRangeSlider
    country: Select
    severity: Select
    metric: Select
    reset: Button
    map_reset: Button


def create_controls(frame: pd.DataFrame) -> DashboardControls:
    """Build controls using safe bounds derived from the loaded data."""

    magnitude_min = float(frame["magnitude"].min()) if not frame.empty else 0.0
    magnitude_max = float(frame["magnitude"].max()) if not frame.empty else 10.0
    depth_min = max(0.0, float(frame["depth"].min())) if not frame.empty else 0.0
    depth_max = max(10.0, float(frame["depth"].max())) if not frame.empty else 700.0
    start = frame["time"].min().date() if not frame.empty else pd.Timestamp.utcnow().date()
    end = frame["time"].max().date() if not frame.empty else pd.Timestamp.utcnow().date()
    countries = sorted(frame.loc[frame["country"].ne("Ocean / Unassigned"), "country"].unique())
    return DashboardControls(
        magnitude=RangeSlider(
            title="Magnitude range",
            start=round(magnitude_min, 1),
            end=max(round(magnitude_max + 0.1, 1), round(magnitude_min + 0.1, 1)),
            value=(round(magnitude_min, 1), round(magnitude_max + 0.1, 1)),
            step=0.1,
            sizing_mode="stretch_width",
        ),
        depth=RangeSlider(
            title="Depth range (km)",
            start=0,
            end=max(700, int(depth_max + 1)),
            value=(depth_min, depth_max + 1),
            step=1,
            sizing_mode="stretch_width",
        ),
        dates=DateRangeSlider(
            title="Date range (UTC)",
            start=start,
            end=end,
            value=(start, end),
            step=24 * 60 * 60 * 1000,
            sizing_mode="stretch_width",
        ),
        country=Select(
            title="Country",
            value="All countries",
            options=["All countries", *countries],
            sizing_mode="stretch_width",
        ),
        severity=Select(
            title="Severity",
            value="All severities",
            options=SEVERITY_OPTIONS,
            sizing_mode="stretch_width",
        ),
        metric=Select(
            title="Country color metric",
            value="earthquake_count",
            options=METRIC_OPTIONS,
            sizing_mode="stretch_width",
        ),
        reset=Button(
            label="Reset all filters",
            button_type="primary",
            height=31,
            margin=(22, 0, 0, 0),
            sizing_mode="stretch_width",
        ),
        map_reset=Button(
            label="↺  Reset map view",
            button_type="primary",
            width=158,
            height=34,
            margin=(5, 0, 5, 0),
        ),
    )
