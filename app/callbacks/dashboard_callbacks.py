"""Live Python callbacks connecting widgets, Pandas, and Bokeh sources."""

from __future__ import annotations

from html import escape
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from bokeh.models import (
    ColorBar,
    ColumnDataSource,
    Div,
    FactorRange,
    GeoJSONDataSource,
    LinearColorMapper,
    Range1d,
)

from app.components.controls import DashboardControls
from app.components.metrics import set_metric
from app.data.preprocessing import aggregate_by_country, filter_earthquakes

METRIC_LABELS = {
    "earthquake_count": "Earthquake count",
    "average_magnitude": "Average magnitude",
    "maximum_magnitude": "Maximum magnitude",
    "average_depth": "Average depth (km)",
}
SEVERITY_COLORS = {
    "Minor": "#55a868",
    "Light": "#4c78a8",
    "Moderate": "#f2a93b",
    "Strong": "#e66c44",
    "Major": "#c53b53",
    "Great": "#7b2cbf",
    "Unknown": "#6b7280",
}


def _timestamp(value: Any) -> pd.Timestamp:
    if isinstance(value, (int, float)):
        return pd.to_datetime(value, unit="ms", utc=True)
    parsed = pd.Timestamp(value)
    return parsed.tz_localize("UTC") if parsed.tzinfo is None else parsed.tz_convert("UTC")


def earthquake_source_data(frame: pd.DataFrame) -> dict[str, Any]:
    """Format filtered rows for the point source and hover UI."""

    if frame.empty:
        columns = [
            "event_id", "time", "latitude", "longitude", "depth", "magnitude", "place",
            "event_type", "url", "severity", "depth_class", "country", "x", "y",
            "point_size", "color", "time_display",
        ]
        return {column: [] for column in columns}
    display = frame.reset_index(drop=True).copy()
    display["point_size"] = (5 + np.square(display["magnitude"].clip(lower=0)) * 0.55).clip(7, 32)
    display["color"] = display["severity"].map(SEVERITY_COLORS).fillna("#6b7280")
    display["time_display"] = display["time"].dt.strftime("%Y-%m-%d %H:%M UTC")
    return ColumnDataSource.from_df(display)


class DashboardController:
    """Own dashboard state and update existing Bokeh models in place."""

    def __init__(
        self,
        *,
        master: pd.DataFrame,
        world_mercator: gpd.GeoDataFrame,
        controls: DashboardControls,
        earthquake_source: ColumnDataSource,
        country_source: GeoJSONDataSource,
        histogram_source: ColumnDataSource,
        ranking_source: ColumnDataSource,
        ranking_range: FactorRange,
        color_mapper: LinearColorMapper,
        color_bar: ColorBar,
        metric_cards: dict[str, Div],
        details: Div,
        insight: Div,
        result_status: Div,
        map_x_range: Range1d,
        map_y_range: Range1d,
    ) -> None:
        self.master = master
        self.world_mercator = world_mercator
        self.controls = controls
        self.earthquake_source = earthquake_source
        self.country_source = country_source
        self.histogram_source = histogram_source
        self.ranking_source = ranking_source
        self.ranking_range = ranking_range
        self.color_mapper = color_mapper
        self.color_bar = color_bar
        self.metric_cards = metric_cards
        self.details = details
        self.insight = insight
        self.result_status = result_status
        self.map_x_range = map_x_range
        self.map_y_range = map_y_range
        self.default_map_bounds = (
            float(map_x_range.start),
            float(map_x_range.end),
            float(map_y_range.start),
            float(map_y_range.end),
        )

    def connect(self) -> None:
        """Register real Bokeh Server Python callbacks."""

        for widget in (self.controls.severity, self.controls.metric):
            widget.on_change("value", self._on_filter_change)
        self.controls.country.on_change("value", self._on_country_change)
        for slider in (self.controls.magnitude, self.controls.depth, self.controls.dates):
            slider.on_change("value_throttled", self._on_filter_change)
        self.controls.reset.on_click(self._reset_filters)
        self.controls.map_reset.on_click(self._reset_map_view)
        self.earthquake_source.selected.on_change("indices", self._on_selection)

    def _filtered(self) -> pd.DataFrame:
        start, end = self.controls.dates.value
        return filter_earthquakes(
            self.master,
            magnitude_range=tuple(self.controls.magnitude.value),
            depth_range=tuple(self.controls.depth.value),
            date_range=(_timestamp(start), _timestamp(end)),
            country=self.controls.country.value,
            severity=self.controls.severity.value,
        )

    def _on_filter_change(self, _attr: str, _old: Any, _new: Any) -> None:
        self.update()

    def _on_country_change(self, _attr: str, _old: str, country: str) -> None:
        self.update()
        self._zoom_to_country(country)

    def _zoom_to_country(self, country: str) -> None:
        """Frame a selected country's projected bounds with readable padding."""

        if country == "All countries":
            x_start, x_end, y_start, y_end = self.default_map_bounds
        else:
            selected = self.world_mercator[self.world_mercator["country"].eq(country)]
            if selected.empty:
                return
            min_x, min_y, max_x, max_y = selected.total_bounds
            if not np.isfinite([min_x, min_y, max_x, max_y]).all():
                return

            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            width = max((max_x - min_x) * 1.28, 1_000_000.0)
            height = max((max_y - min_y) * 1.28, 650_000.0)
            target_aspect = 2.0
            if width / height < target_aspect:
                width = height * target_aspect
            else:
                height = width / target_aspect
            x_start, x_end = center_x - width / 2, center_x + width / 2
            y_start, y_end = center_y - height / 2, center_y + height / 2

        self.map_x_range.start = x_start
        self.map_x_range.end = x_end
        self.map_y_range.start = y_start
        self.map_y_range.end = y_end

    def _reset_filters(self) -> None:
        self.controls.magnitude.value = (self.controls.magnitude.start, self.controls.magnitude.end)
        self.controls.depth.value = (self.controls.depth.start, self.controls.depth.end)
        self.controls.dates.value = (self.controls.dates.start, self.controls.dates.end)
        self.controls.country.value = "All countries"
        self.controls.severity.value = "All severities"
        self.controls.metric.value = "earthquake_count"
        self.update()
        self._zoom_to_country("All countries")

    def _reset_map_view(self) -> None:
        """Restore the global map extent without changing active filters."""

        self._zoom_to_country("All countries")

    def update(self) -> None:
        """Apply filters once, then update every connected view and metric."""

        filtered = self._filtered()
        self.earthquake_source.selected.indices = []
        self.earthquake_source.data = earthquake_source_data(filtered)
        aggregates = aggregate_by_country(filtered)
        self._update_choropleth(aggregates)
        self._update_histogram(filtered)
        self._update_ranking(aggregates)
        self._update_metrics(filtered, aggregates)
        self._update_insight(filtered, aggregates)
        count = len(filtered)
        state = "No earthquakes match the current filters." if count == 0 else f"Showing {count:,} earthquakes"
        self.result_status.text = (
            '<div style="font-family:Inter,ui-sans-serif,system-ui,sans-serif">'
            f'<span style="display:inline-block;width:6px;height:6px;margin-right:7px;border-radius:50%;'
            f'background:{"#16a085" if count else "#e11d48"}"></span>{state}</div>'
        )

    def _update_choropleth(self, aggregates: pd.DataFrame) -> None:
        metric = self.controls.metric.value
        metric_label = METRIC_LABELS[metric]
        merged = self.world_mercator.merge(aggregates, on="country", how="left")
        stat_columns = ["earthquake_count", "average_magnitude", "maximum_magnitude", "average_depth"]
        for column in stat_columns:
            merged[column] = pd.to_numeric(merged[column], errors="coerce")
        merged["metric_value"] = merged[metric]
        merged["metric_display"] = merged[metric].map(
            lambda value: "No data" if pd.isna(value) else f"{value:,.2f}" if metric != "earthquake_count" else f"{value:,.0f}"
        )
        finite = merged["metric_value"].dropna()
        low = float(finite.min()) if not finite.empty else 0.0
        high = float(finite.max()) if not finite.empty else 1.0
        if high <= low:
            high = low + 1.0
        self.color_mapper.low = low
        self.color_mapper.high = high
        self.color_bar.title = metric_label
        self.country_source.geojson = merged.to_json(drop_id=True)

    def _update_histogram(self, filtered: pd.DataFrame) -> None:
        if filtered.empty:
            self.histogram_source.data = {"top": [], "left": [], "right": [], "label": []}
            return
        values = filtered["magnitude"].to_numpy()
        lower = np.floor(values.min() * 2) / 2
        upper = np.ceil(values.max() * 2) / 2 + 0.5
        bins = np.arange(lower, upper + 0.001, 0.5)
        counts, edges = np.histogram(values, bins=bins)
        self.histogram_source.data = {
            "top": counts,
            "left": edges[:-1],
            "right": edges[1:],
            "label": [f"{left:.1f}–{right:.1f}" for left, right in zip(edges[:-1], edges[1:])],
        }

    def _update_ranking(self, aggregates: pd.DataFrame) -> None:
        if aggregates.empty:
            self.ranking_source.data = {"country": [], "count": []}
            self.ranking_range.factors = []
            return
        ranked = aggregates.nlargest(10, "earthquake_count").sort_values("earthquake_count")
        countries = ranked["country"].tolist()
        self.ranking_source.data = {
            "country": countries,
            "count": ranked["earthquake_count"].astype(int).tolist(),
        }
        self.ranking_range.factors = countries

    def _update_metrics(self, filtered: pd.DataFrame, aggregates: pd.DataFrame) -> None:
        strongest = f"{filtered['magnitude'].max():.1f}" if not filtered.empty else "—"
        average_depth = f"{filtered['depth'].mean():.1f} km" if not filtered.empty else "—"
        set_metric(self.metric_cards["total"], "Total earthquakes", f"{len(filtered):,}")
        set_metric(self.metric_cards["strongest"], "Strongest magnitude", strongest)
        set_metric(self.metric_cards["depth"], "Average depth", average_depth)
        set_metric(self.metric_cards["countries"], "Countries affected", f"{len(aggregates):,}")

    def _update_insight(self, filtered: pd.DataFrame, aggregates: pd.DataFrame) -> None:
        if filtered.empty:
            sentence = "Adjust the filters to restore matching earthquakes."
        else:
            strongest = filtered.loc[filtered["magnitude"].idxmax()]
            if aggregates.empty:
                lead = "Most events in this selection are offshore or unassigned."
            else:
                top = aggregates.loc[aggregates["earthquake_count"].idxmax()]
                lead = f"{escape(str(top['country']))} has the highest on-land count ({int(top['earthquake_count'])})."
            sentence = (
                f"{lead} The strongest event is magnitude {strongest['magnitude']:.1f} "
                f"near {escape(str(strongest['place']))}."
            )
        self.insight.text = (
            '<div style="display:flex;align-items:flex-start;gap:12px;'
            'font-family:Inter,ui-sans-serif,system-ui,sans-serif">'
            '<div style="display:flex;align-items:center;justify-content:center;width:26px;height:26px;'
            'flex:0 0 26px;border-radius:8px;background:#dbeafe;color:#2563eb;font-size:14px">✦</div>'
            '<div><div style="font-size:10px;font-weight:850;letter-spacing:.1em;color:#2563eb">CURRENT INSIGHT</div>'
            f'<div style="margin-top:3px;font-size:12px;line-height:1.5;color:#44546d">{sentence}</div></div></div>'
        )

    def _on_selection(self, _attr: str, _old: list[int], indices: list[int]) -> None:
        if not indices:
            return
        index = indices[0]
        data = self.earthquake_source.data
        if index >= len(data.get("event_id", [])):
            return

        def field(name: str) -> str:
            return escape(str(data[name][index]))

        url = field("url")
        link = (
            f'<a href="{url}" target="_blank" rel="noopener" style="display:inline-block;margin-top:14px;'
            'font-size:11px;font-weight:750;color:#2563eb;text-decoration:none">'
            'Open official USGS event page&nbsp; ↗</a>'
            if url
            else ""
        )

        def detail_item(label: str, value: str, *, accent: bool = False) -> str:
            value_color = "#e11d48" if accent else "#172b4d"
            return (
                '<div style="padding:10px 12px;border-radius:10px;background:#f7f9fc;border:1px solid #edf1f6">'
                f'<div style="font-size:9px;font-weight:800;letter-spacing:.085em;color:#8290a5">{label}</div>'
                f'<div style="margin-top:4px;font-size:12px;font-weight:730;color:{value_color}">{value}</div></div>'
            )

        self.details.text = f"""
        <div style="font-family:Inter,ui-sans-serif,system-ui,sans-serif">
          <div style="font-size:9px;font-weight:850;letter-spacing:.14em;color:#2563eb">
            SELECTED EARTHQUAKE · {field('event_id')}
          </div>
          <div style="margin-top:5px;font-size:18px;font-weight:750;color:#172b4d">{field('place')}</div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:9px;margin-top:14px">
            {detail_item('MAGNITUDE', f"{float(data['magnitude'][index]):.1f}", accent=True)}
            {detail_item('DEPTH', f"{float(data['depth'][index]):.1f} km")}
            {detail_item('COUNTRY', field('country'))}
            {detail_item('SEVERITY', field('severity'))}
            {detail_item('TIME', field('time_display'))}
            {detail_item('COORDINATES', f"{float(data['latitude'][index]):.3f}, {float(data['longitude'][index]):.3f}")}
          </div>{link}
        </div>
        """
