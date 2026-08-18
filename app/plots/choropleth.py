"""Country choropleth layer attached to the primary map."""

from __future__ import annotations

from bokeh.models import ColorBar, GeoJSONDataSource, HoverTool, LinearColorMapper
from bokeh.palettes import Blues256
from bokeh.transform import transform


def add_choropleth_layer(plot, source: GeoJSONDataSource):
    """Render projected country polygons beneath earthquake points."""

    mapper = LinearColorMapper(palette=Blues256, low=0, high=1, nan_color="#e5e7eb")
    renderer = plot.patches(
        xs="xs",
        ys="ys",
        source=source,
        fill_color=transform("metric_value", mapper),
        fill_alpha=0.52,
        line_color="#6b7280",
        line_alpha=0.45,
        line_width=0.5,
        level="underlay",
    )
    hover = HoverTool(
        renderers=[renderer],
        tooltips=[
            ("Country", "@country"),
            ("Selected metric", "@metric_display"),
            ("Earthquakes", "@earthquake_count{0}"),
            ("Average magnitude", "@average_magnitude{0.00}"),
            ("Maximum magnitude", "@maximum_magnitude{0.00}"),
            ("Average depth", "@average_depth{0.0} km"),
        ],
    )
    plot.add_tools(hover)
    color_bar = ColorBar(
        color_mapper=mapper,
        title="Earthquake count",
        label_standoff=7,
        width=9,
        location=(0, 0),
        background_fill_alpha=0.8,
    )
    plot.add_layout(color_bar, "left")
    return mapper, color_bar
