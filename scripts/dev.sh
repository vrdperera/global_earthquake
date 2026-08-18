#!/usr/bin/env bash
set -euo pipefail

exec uv run bokeh serve app --show --dev
