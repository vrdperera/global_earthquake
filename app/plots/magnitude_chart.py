"""Dynamic earthquake magnitude distribution."""

from __future__ import annotations

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

from app.plots.styling import style_plot


def create_magnitude_chart(source: ColumnDataSource):
    """Create a compact histogram that updates via its data source."""

    plot = figure(
        title="Magnitude distribution",
        height=330,
        sizing_mode="stretch_width",
        tools="pan,wheel_zoom,reset,save",
        toolbar_location="above",
        x_axis_label="Magnitude",
        y_axis_label="Earthquake count",
    )
    renderer = plot.quad(
        top="top",
        bottom=0,
        left="left",
        right="right",
        source=source,
        fill_color="#f06449",
        fill_alpha=0.88,
        line_color="#ffffff",
    )
    plot.add_tools(
        HoverTool(
            renderers=[renderer],
            tooltips=[("Magnitude band", "@label"), ("Count", "@top{0}")],
        )
    )
    style_plot(plot)
    return plot
