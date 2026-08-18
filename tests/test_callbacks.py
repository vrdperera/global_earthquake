from __future__ import annotations

import pandas as pd
import geopandas as gpd
from bokeh.models import ColumnDataSource, FactorRange, Range1d
from shapely.geometry import Polygon

from app.callbacks.dashboard_callbacks import DashboardController


def test_empty_aggregation_clears_regional_ranking() -> None:
    controller = DashboardController.__new__(DashboardController)
    controller.ranking_source = ColumnDataSource(data={"country": ["Old"], "count": [3]})
    controller.ranking_range = FactorRange(factors=["Old"])

    controller._update_ranking(
        pd.DataFrame(
            columns=[
                "country",
                "earthquake_count",
                "average_magnitude",
                "maximum_magnitude",
                "average_depth",
            ]
        )
    )

    assert controller.ranking_source.data == {"country": [], "count": []}
    assert controller.ranking_range.factors == []


def test_country_selection_updates_and_restores_map_ranges() -> None:
    controller = DashboardController.__new__(DashboardController)
    controller.world_mercator = gpd.GeoDataFrame(
        {"country": ["Testland"]},
        geometry=[Polygon([(1_000_000, 2_000_000), (2_000_000, 2_000_000),
                          (2_000_000, 3_000_000), (1_000_000, 3_000_000)])],
        crs="EPSG:3857",
    )
    controller.map_x_range = Range1d(-20_000_000, 20_000_000)
    controller.map_y_range = Range1d(-8_000_000, 12_000_000)
    controller.default_map_bounds = (-20_000_000, 20_000_000, -8_000_000, 12_000_000)

    controller._zoom_to_country("Testland")
    assert controller.map_x_range.start > 0
    assert controller.map_x_range.end < 4_000_000
    assert controller.map_y_range.start > 1_000_000
    assert controller.map_y_range.end < 4_000_000

    controller._zoom_to_country("All countries")
    assert controller.map_x_range.start == -20_000_000
    assert controller.map_x_range.end == 20_000_000
    assert controller.map_y_range.start == -8_000_000
    assert controller.map_y_range.end == 12_000_000
