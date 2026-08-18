"""Process-wide application data loading pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import geopandas as gpd
import pandas as pd

from app.config import SETTINGS
from app.data.geography import (
    add_web_mercator_coordinates,
    attach_countries,
    ensure_world_boundaries,
    load_world_boundaries,
    world_web_mercator,
)
from app.data.preprocessing import parse_usgs_geojson
from app.data.usgs import UsgsResult, fetch_earthquakes


@dataclass(frozen=True)
class ApplicationData:
    """Prepared immutable-by-convention data shared by Bokeh sessions."""

    earthquakes: pd.DataFrame
    world_mercator: gpd.GeoDataFrame
    usgs_result: UsgsResult


@lru_cache(maxsize=1)
def load_application_data() -> ApplicationData:
    """Download and preprocess once per server process, never per callback."""

    result = fetch_earthquakes(
        days=SETTINGS.days,
        minimum_magnitude=SETTINGS.minimum_magnitude,
        cache_dir=SETTINGS.cache_dir,
        timeout=SETTINGS.request_timeout,
    )
    earthquakes = parse_usgs_geojson(result.payload)
    world = load_world_boundaries(ensure_world_boundaries(SETTINGS.geography_dir))
    earthquakes = add_web_mercator_coordinates(attach_countries(earthquakes, world))
    return ApplicationData(earthquakes, world_web_mercator(world), result)
