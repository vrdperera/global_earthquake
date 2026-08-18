"""Country boundaries, spatial joining, and explicit map projection."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import httpx
import pandas as pd
from pyproj import Transformer

WORLD_FILENAME = "ne_110m_admin_0_countries.geojson"
WORLD_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_110m_admin_0_countries.geojson"
)
WEB_MERCATOR_LIMIT = 20_037_508.34


def ensure_world_boundaries(geography_dir: Path, timeout: float = 20.0) -> Path:
    """Return cached Natural Earth country boundaries, downloading once if absent."""

    target = geography_dir / WORLD_FILENAME
    if target.exists():
        return target
    geography_dir.mkdir(parents=True, exist_ok=True)
    response = httpx.get(WORLD_URL, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def load_world_boundaries(path: Path) -> gpd.GeoDataFrame:
    """Load legitimate Natural Earth polygons and standardize country names."""

    world = gpd.read_file(path)
    name_column = next(
        column for column in ("NAME", "ADMIN", "SOVEREIGNT", "name") if column in world.columns
    )
    world = world[[name_column, "geometry"]].rename(columns={name_column: "country"})
    world = world[world.geometry.notna() & ~world.geometry.is_empty].copy()
    return world.to_crs("EPSG:4326")


def attach_countries(frame: pd.DataFrame, world: gpd.GeoDataFrame) -> pd.DataFrame:
    """Spatially join earthquake longitude/latitude points to country polygons."""

    if frame.empty:
        return frame.assign(country=pd.Series(dtype="object"))
    points = gpd.GeoDataFrame(
        frame.copy(),
        geometry=gpd.points_from_xy(frame["longitude"], frame["latitude"]),
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(points, world[["country", "geometry"]], how="left", predicate="within")
    joined["country"] = joined["country"].fillna("Ocean / Unassigned")
    return pd.DataFrame(joined.drop(columns=["geometry", "index_right"], errors="ignore"))


def add_web_mercator_coordinates(frame: pd.DataFrame) -> pd.DataFrame:
    """Project WGS84 longitude/latitude into EPSG:3857 metres."""

    result = frame.copy()
    if result.empty:
        return result.assign(x=pd.Series(dtype=float), y=pd.Series(dtype=float))
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(result["longitude"].to_numpy(), result["latitude"].to_numpy())
    result["x"] = x
    result["y"] = y
    result["y"] = result["y"].clip(-WEB_MERCATOR_LIMIT, WEB_MERCATOR_LIMIT)
    return result


def world_web_mercator(world: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Project country polygons for display on a Web Mercator tile map."""

    return world.to_crs("EPSG:3857")
