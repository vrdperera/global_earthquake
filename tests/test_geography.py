from __future__ import annotations

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from app.data.geography import add_web_mercator_coordinates, attach_countries


def test_spatial_join_assigns_country_and_ocean() -> None:
    world = gpd.GeoDataFrame(
        {"country": ["Testland"]},
        geometry=[Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])],
        crs="EPSG:4326",
    )
    events = pd.DataFrame(
        {
            "event_id": ["inside", "outside"],
            "longitude": [1.0, 10.0],
            "latitude": [1.0, 10.0],
        }
    )
    result = attach_countries(events, world)
    assert result["country"].tolist() == ["Testland", "Ocean / Unassigned"]


def test_web_mercator_conversion_is_explicit() -> None:
    events = pd.DataFrame({"longitude": [0.0, 10.0], "latitude": [0.0, 10.0]})
    result = add_web_mercator_coordinates(events)
    assert result.loc[0, "x"] == 0.0
    assert result.loc[0, "y"] == 0.0
    assert result.loc[1, "x"] > 1_000_000
    assert result.loc[1, "y"] > 1_000_000
