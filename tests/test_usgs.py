from __future__ import annotations

import json
from pathlib import Path

import httpx

from app.data.usgs import fetch_earthquakes


def test_fetch_falls_back_to_latest_cache(tmp_path: Path) -> None:
    cached = {"type": "FeatureCollection", "features": [{"id": "cached"}]}
    (tmp_path / "usgs_20260801T000000Z.json").write_text(json.dumps(cached), encoding="utf-8")

    def fail(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "offline"})

    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        result = fetch_earthquakes(
            days=30,
            minimum_magnitude=2.5,
            cache_dir=tmp_path,
            client=client,
        )
    assert result.source == "cache"
    assert result.payload == cached
