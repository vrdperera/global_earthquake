"""Selected-event details panel."""

from __future__ import annotations

from bokeh.models import Div

DETAILS_STYLES = {
    "background": "#ffffff",
    "border": "1px solid #e4eaf2",
    "border-radius": "16px",
    "box-shadow": "0 6px 20px rgba(30, 50, 85, 0.06)",
    "box-sizing": "border-box",
    "padding": "20px 22px",
    "min-height": "138px",
}


def empty_details() -> Div:
    """Create the initial linked-selection panel."""

    return Div(
        text=(
            '<div style="font-family:Inter,ui-sans-serif,system-ui,sans-serif">'
            '<div style="font-size:10px;font-weight:800;letter-spacing:.14em;color:#2563eb">SELECTED EARTHQUAKE</div>'
            '<div style="margin-top:7px;font-size:18px;font-weight:720;color:#172b4d">'
            'Click any earthquake point to inspect it</div>'
            '<div style="margin-top:8px;max-width:780px;font-size:13px;line-height:1.55;color:#6b7890">'
            'Magnitude, depth, location, country, UTC time, coordinates and the USGS event ID '
            "will appear here.</div></div>"
        ),
        styles=DETAILS_STYLES,
        sizing_mode="stretch_width",
    )
