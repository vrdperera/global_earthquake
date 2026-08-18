"""Bokeh Server entry point for the Global USGS Earthquake Explorer."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# Bokeh executes a directory app's main.py as a script, so make the project
# package importable without requiring users to install it first.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bokeh.io import curdoc
from bokeh.layouts import column, gridplot, row
from bokeh.models import ColumnDataSource, Div, GeoJSONDataSource

from app.callbacks.dashboard_callbacks import DashboardController
from app.components.controls import create_controls
from app.components.details import empty_details
from app.components.metrics import metric_card
from app.config import SETTINGS
from app.data.pipeline import load_application_data
from app.plots.choropleth import add_choropleth_layer
from app.plots.earthquake_map import create_earthquake_map
from app.plots.magnitude_chart import create_magnitude_chart
from app.plots.regional_chart import create_regional_chart

HERO_STYLES = {
    "background": "linear-gradient(122deg, #102a56 0%, #174e91 58%, #087d88 100%)",
    "border": "1px solid rgba(255, 255, 255, 0.12)",
    "border-radius": "20px",
    "box-shadow": "0 16px 38px rgba(17, 43, 86, 0.20)",
    "box-sizing": "border-box",
    "padding": "27px 30px",
    "min-height": "185px",
}
PANEL_STYLES = {
    "background": "#ffffff",
    "border": "1px solid #e4eaf2",
    "border-radius": "16px",
    "box-shadow": "0 7px 22px rgba(30, 50, 85, 0.07)",
    "box-sizing": "border-box",
    "padding": "17px 18px 11px",
}


def section_label(kicker: str, title: str) -> Div:
    """Create a compact visual section heading."""

    return Div(
        text=(
            '<div style="font-family:Inter,ui-sans-serif,system-ui,sans-serif">'
            f'<div style="font-size:9px;font-weight:850;letter-spacing:.15em;color:#2d6cdf">{kicker}</div>'
            f'<div style="margin-top:3px;font-size:16px;font-weight:740;color:#172b4d">{title}</div></div>'
        ),
        height=44,
        sizing_mode="stretch_width",
    )


def build_dashboard():
    """Acquire data once and assemble the complete server-backed document."""

    application_data = load_application_data()
    result = application_data.usgs_result
    earthquakes = application_data.earthquakes
    world_mercator = application_data.world_mercator

    controls = create_controls(earthquakes)
    earthquake_source = ColumnDataSource(data={})
    country_source = GeoJSONDataSource(geojson=world_mercator.assign(
        earthquake_count=float("nan"), average_magnitude=float("nan"),
        maximum_magnitude=float("nan"), average_depth=float("nan"),
        metric_value=float("nan"), metric_display="No data",
    ).to_json(drop_id=True))
    histogram_source = ColumnDataSource(data={"top": [], "left": [], "right": [], "label": []})
    ranking_source = ColumnDataSource(data={"country": [], "count": []})

    map_plot = create_earthquake_map(earthquake_source)
    color_mapper, color_bar = add_choropleth_layer(map_plot, country_source)
    histogram = create_magnitude_chart(histogram_source)
    ranking = create_regional_chart(ranking_source)

    cards = {
        "total": metric_card("Total earthquakes"),
        "strongest": metric_card("Strongest magnitude"),
        "depth": metric_card("Average depth"),
        "countries": metric_card("Countries affected"),
    }
    details = empty_details()
    insight = Div(
        styles={
            "background": "linear-gradient(90deg, #edf5ff, #f5f9ff)",
            "border": "1px solid #d9e8ff",
            "border-left": "4px solid #2d6cdf",
            "border-radius": "11px",
            "box-sizing": "border-box",
            "padding": "12px 15px",
        },
        sizing_mode="stretch_width",
    )
    result_status = Div(
        styles={"color": "#66758d", "font-size": "11px", "padding": "0 3px"},
        sizing_mode="stretch_width",
    )
    live_label = "Live USGS data" if result.source == "live" else "Cached USGS data"
    hero = Div(
        text=(
            '<header style="display:flex;align-items:center;justify-content:space-between;gap:28px;'
            'font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#fff">'
            '<div style="min-width:0">'
            '<div style="display:inline-flex;align-items:center;gap:7px;padding:5px 9px;border-radius:99px;'
            'background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.16);'
            'font-size:9px;font-weight:850;letter-spacing:.14em;color:#dceaff">'
            '<span style="width:6px;height:6px;border-radius:50%;background:#55d6be"></span>'
            'ADVANCED PLOTTING · BOKEH SERVER</div>'
            '<div style="margin-top:13px;font-size:32px;line-height:1.08;font-weight:780;'
            'letter-spacing:-.04em">Global USGS Earthquake Explorer</div>'
            f'<div style="margin-top:10px;max-width:760px;font-size:13px;line-height:1.55;color:#d9e7fb">'
            f'Explore magnitude, depth, time and geographic patterns from the latest {SETTINGS.days}-day '
            'USGS catalog window.</div></div>'
            '<div style="min-width:210px;padding:15px 16px;border-radius:14px;background:rgba(7,22,48,.22);'
            'border:1px solid rgba(255,255,255,.15);backdrop-filter:blur(8px)">'
            f'<div style="font-size:11px;font-weight:750;color:#fff"><span style="color:#5ee2b8">●</span> {live_label}</div>'
            '<div style="display:flex;gap:18px;margin-top:13px">'
            f'<div><div style="font-size:19px;font-weight:760">{len(earthquakes):,}</div>'
            '<div style="font-size:9px;letter-spacing:.08em;color:#bcd0ed">EVENTS</div></div>'
            f'<div><div style="font-size:19px;font-weight:760">M{SETTINGS.minimum_magnitude}+</div>'
            '<div style="font-size:9px;letter-spacing:.08em;color:#bcd0ed">THRESHOLD</div></div>'
            f'<div><div style="font-size:19px;font-weight:760">{SETTINGS.days}d</div>'
            '<div style="font-size:9px;letter-spacing:.08em;color:#bcd0ed">WINDOW</div></div>'
            '</div></div></header>'
        ),
        styles=HERO_STYLES,
        sizing_mode="stretch_width",
    )
    control_panel = column(
        row(controls.magnitude, controls.depth, controls.dates, sizing_mode="stretch_width"),
        row(controls.country, controls.severity, controls.metric, controls.reset, sizing_mode="stretch_width"),
        styles=PANEL_STYLES,
        sizing_mode="stretch_width",
    )
    controller = DashboardController(
        master=earthquakes,
        world_mercator=world_mercator,
        controls=controls,
        earthquake_source=earthquake_source,
        country_source=country_source,
        histogram_source=histogram_source,
        ranking_source=ranking_source,
        ranking_range=ranking.y_range,
        color_mapper=color_mapper,
        color_bar=color_bar,
        metric_cards=cards,
        details=details,
        insight=insight,
        result_status=result_status,
        map_x_range=map_plot.x_range,
        map_y_range=map_plot.y_range,
    )
    controller.connect()
    controller.update()

    map_heading = row(
        section_label("GEOSPATIAL VIEW", "Explore location, intensity and regional patterns"),
        controls.map_reset,
        sizing_mode="stretch_width",
    )

    layout = column(
        hero,
        section_label("CATALOG CONTROLS", "Focus the earthquake selection"),
        control_panel,
        row(*cards.values(), sizing_mode="stretch_width"),
        insight,
        result_status,
        map_heading,
        map_plot,
        section_label("DISTRIBUTION & RANKING", "Compare magnitude frequency and affected countries"),
        gridplot([[histogram, ranking]], sizing_mode="stretch_width", merge_tools=False),
        section_label("LINKED SELECTION", "Selected earthquake details"),
        details,
        sizing_mode="stretch_width",
        width_policy="max",
        margin=(22, 28, 36, 28),
        spacing=14,
    )
    return layout


document = curdoc()
document.title = "Global USGS Earthquake Explorer"
try:
    document.add_root(build_dashboard())
except Exception as exc:  # Keep a deployment/network issue visible instead of a blank app.
    traceback.print_exc()
    document.add_root(
        Div(
            text=(
                '<div style="font-family:Inter,system-ui,sans-serif">'
                '<h2 style="margin:0;color:#172b4d">Dashboard could not initialize</h2>'
                f'<p style="color:#b42318">{type(exc).__name__}: {exc}</p>'
                '<p style="color:#66758d">Check network access and ensure data/cache contains '
                "a recent USGS cache file.</p></div>"
            ),
            styles=PANEL_STYLES,
            sizing_mode="stretch_width",
        )
    )
