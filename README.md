# Global USGS Earthquake Explorer

An interactive, server-backed geospatial dashboard for exploring worldwide earthquake
activity. This university coursework project focuses on advanced plotting with Bokeh
Server: every filter runs a live Python callback, filters a prepared Pandas/GeoPandas
dataset, and updates existing Bokeh data sources in the browser.

## Features

- Interactive Web Mercator map with pan, wheel zoom, box zoom, reset, hover, tap
  selection, CartoDB tiles, and magnitude-scaled earthquake markers.
- Natural Earth country choropleth with switchable earthquake count, average magnitude,
  maximum magnitude, and average depth metrics plus a dynamic color bar.
- Magnitude, depth, UTC date, country, and derived severity filters.
- Linked event details with coordinates, country, depth, time, USGS event ID, severity,
  and a link to the official USGS record.
- Filter-aware magnitude histogram, top-country ranking, summary metrics, and
  deterministic narrative insights.
- Live USGS acquisition with a checked-in real-data seed cache and automatic fallback
  for reliable offline demonstrations.
- Focused tests for parsing, filters, classification, aggregation, spatial joining,
  coordinate projection, empty inputs, and cache fallback.

## Architecture

```text
Official USGS Catalog API          Natural Earth country polygons
             |                                  |
             v                                  v
      cache + Pandas parsing --------> GeoPandas spatial join
                                                    |
                                                    v
                                  prepared master DataFrame (once)
                                                    |
                               Bokeh Server Python callbacks
                                                    |
                  filtered ColumnDataSource + GeoJSONDataSource objects
                                                    |
                                                    v
                                  interactive browser dashboard
```

The app downloads once per Bokeh server process, performs the expensive spatial join
once, then filters locally. Slider movement never re-downloads data or rebuilds plots.

## Data sources

- Earthquakes: [USGS Earthquake Catalog API](https://earthquake.usgs.gov/fdsnws/event/1/)
- Boundaries: [Natural Earth 1:110m Admin 0 Countries](https://github.com/nvkelso/natural-earth-vector)
- Basemap: CartoDB Positron through `xyzservices`

The default query uses the latest 30-day window at magnitude 2.5 or higher. Change it
without editing code:

```bash
USGS_QUERY_DAYS=14 USGS_MIN_MAGNITUDE=4.0 uv run bokeh serve app --show
```

## Installation

Python 3.12+ and [`uv`](https://docs.astral.sh/uv/) are required.

```bash
git clone <repository-url>
cd global-earthquake-explorer
uv sync
```

`pyproject.toml` and `uv.lock` are the dependency sources of truth. If another platform
requires a requirements file, export one without replacing them:

```bash
uv export --format requirements-txt > requirements.txt
```

## Local execution

```bash
uv run bokeh serve app --show
```

Then open `http://localhost:5006/app` if a browser is not opened automatically. The
status pill identifies whether the session is using live or cached USGS data.

During development, use the autoreload command so Python and UI changes restart the
Bokeh application automatically:

```bash
bash scripts/dev.sh
```

This runs `uv run bokeh serve app --show --dev`. The `--dev` flag is intentionally not
used by the Render production service.

## Tests

```bash
uv run pytest
```

## Render deployment

The included `render.yaml` installs locked dependencies and starts
[`scripts/start.sh`](scripts/start.sh), which is equivalent to:

```bash
uv run bokeh serve app \
  --address 0.0.0.0 \
  --port "$PORT" \
  --use-xheaders \
  --allow-websocket-origin="$BOKEH_ALLOW_WS_ORIGIN"
```

In Render, set `BOKEH_ALLOW_WS_ORIGIN` to the deployed hostname only, with no protocol
or path, for example `your-service.onrender.com`. Do not commit or hard-code a guessed
hostname. Render supplies `PORT`; the script defaults to 5006 locally.

For a manual Render service use:

- Build command: `pip install uv && uv sync --frozen`
- Start command: `bash scripts/start.sh`
- Health check path: `/app`

No API key or secret is needed for USGS. Optional settings are `USGS_QUERY_DAYS`,
`USGS_MIN_MAGNITUDE`, `USGS_TIMEOUT_SECONDS`, and `BOKEH_ALLOW_WS_ORIGIN`.

## Project layout

```text
app/
  callbacks/     live Bokeh Server update coordination
  components/    controls, metric cards, selected-event details
  data/          USGS acquisition, preprocessing, geography, cached pipeline
  plots/         map, choropleth, histogram, country ranking
  main.py        Bokeh directory-app entry point
data/
  cache/         official USGS JSON fallback
  geography/     Natural Earth country polygons
tests/           data-focused pytest suite
scripts/         deployment start command
```
