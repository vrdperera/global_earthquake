"""Central application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Runtime settings, overridable through environment variables."""

    days: int = int(os.getenv("USGS_QUERY_DAYS", "30"))
    minimum_magnitude: float = float(os.getenv("USGS_MIN_MAGNITUDE", "2.5"))
    request_timeout: float = float(os.getenv("USGS_TIMEOUT_SECONDS", "15"))
    cache_dir: Path = PROJECT_ROOT / "data" / "cache"
    geography_dir: Path = PROJECT_ROOT / "data" / "geography"


SETTINGS = Settings()
