from __future__ import annotations

from bokeh.models import ColumnDataSource, ResetTool

from app.plots.earthquake_map import create_earthquake_map


def test_map_keeps_standard_bokeh_reset_tool() -> None:
    plot = create_earthquake_map(ColumnDataSource(data={"x": [], "y": []}))
    reset_tools = [tool for tool in plot.toolbar.tools if isinstance(tool, ResetTool)]

    assert len(reset_tools) == 1
