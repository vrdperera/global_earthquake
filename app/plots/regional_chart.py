"""Dynamic ranking of affected countries."""

from __future__ import annotations

from bokeh.models import ColumnDataSource, FactorRange, HoverTool
from bokeh.plotting import figure

from app.plots.styling import style_plot


def create_regional_chart(source: ColumnDataSource):
    """Create a horizontal top-country ranking."""

    plot = figure(
        title="Top affected countries",
        height=330,
        sizing_mode="stretch_width",
        tools="tap,reset,save",
        toolbar_location="above",
        x_axis_label="Earthquake count",
        y_range=FactorRange(factors=[]),
    )
    renderer = plot.hbar(
        y="country",
        right="count",
        height=0.66,
        source=source,
        fill_color="#2d6cdf",
        fill_alpha=0.9,
        line_color=None,
    )
    plot.add_tools(
        HoverTool(
            renderers=[renderer],
            tooltips=[("Country", "@country"), ("Earthquakes", "@count{0}")],
        )
    )
    plot.ygrid.grid_line_color = None
    style_plot(plot)
    plot.ygrid.grid_line_color = None
    return plot
