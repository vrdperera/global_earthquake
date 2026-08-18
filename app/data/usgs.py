"""Reliable USGS Earthquake Catalog acquisition with local fallback."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

USGS_QUERY_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


@dataclass(frozen=True)
class UsgsResult:
    """USGS payload plus its provenance for the dashboard status."""

    payload: dict[str, Any]
    source: str
    message: str


def query_parameters(days: int, minimum_magnitude: float) -> dict[str, str | float]:
    """Create a stable UTC query window ending at the current hour."""

    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)
    return {
        "format": "geojson",
        "starttime": start.isoformat(),
        "endtime": end.isoformat(),
        "minmagnitude": minimum_magnitude,
        "orderby": "time",
        "limit": 20000,
    }


def _latest_cache(cache_dir: Path) -> Path | None:
    candidates = list(cache_dir.glob("usgs_*.json"))
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def _write_cache(payload: dict[str, Any], cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = cache_dir / f"usgs_{stamp}.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    return target


def fetch_earthquakes(
    *,
    days: int,
    minimum_magnitude: float,
    cache_dir: Path,
    timeout: float = 15.0,
    client: httpx.Client | None = None,
) -> UsgsResult:
    """Fetch USGS GeoJSON, caching success and falling back on any failure."""

    owned_client = client is None
    active_client = client or httpx.Client(timeout=timeout, follow_redirects=True)
    try:
        response = active_client.get(
            USGS_QUERY_URL,
            params=query_parameters(days, minimum_magnitude),
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload.get("features"), list):
            raise ValueError("USGS response does not contain a feature list")
        cached_path = _write_cache(payload, cache_dir)
        return UsgsResult(payload, "live", f"Live USGS data · cached {cached_path.name}")
    except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
        cached_path = _latest_cache(cache_dir)
        if cached_path is None:
            raise RuntimeError("USGS is unavailable and no cached dataset exists") from exc
        payload = json.loads(cached_path.read_text(encoding="utf-8"))
        return UsgsResult(payload, "cache", f"Cached USGS data · {cached_path.name}")
    finally:
        if owned_client:
            active_client.close()
