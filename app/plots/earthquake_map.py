"""Interactive Web Mercator earthquake map."""

from __future__ import annotations

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
from xyzservices import providers

from app.plots.styling import style_plot


def create_earthquake_map(source: ColumnDataSource):
    """Create the primary tile map and selectable earthquake point renderer."""

    plot = figure(
        title="Global activity map · points and country intensity",
        x_axis_type="mercator",
        y_axis_type="mercator",
        x_range=(-20_037_508, 20_037_508),
        y_range=(-8_000_000, 12_000_000),
        height=570,
        sizing_mode="stretch_width",
        tools="pan,wheel_zoom,box_zoom,reset,save,tap",
        active_scroll="wheel_zoom",
        toolbar_location="right",
    )
    plot.add_tile(providers.CartoDB.Positron, retina=True)
    renderer = plot.scatter(
        x="x",
        y="y",
        source=source,
        marker="circle",
        size="point_size",
        fill_color="color",
        fill_alpha=0.82,
        line_color="#ffffff",
        line_width=0.7,
        selection_fill_color="#ffd166",
        selection_line_color="#111827",
        selection_line_width=2,
        nonselection_fill_alpha=0.42,
    )
    plot.add_tools(
        HoverTool(
            renderers=[renderer],
            tooltips=[
                ("Location", "@place"),
                ("Country", "@country"),
                ("Magnitude", "@magnitude{0.0}"),
                ("Depth", "@depth{0.0} km"),
                ("Time", "@time_display"),
                ("Coordinates", "@latitude{0.000}, @longitude{0.000}"),
                ("Severity", "@severity"),
            ],
            point_policy="follow_mouse",
        )
    )
    plot.axis.visible = False
    plot.grid.visible = False
    style_plot(plot, show_grid=False)
    plot.min_border_left = 12
    plot.min_border_right = 12
    plot.min_border_bottom = 12
    return plot
