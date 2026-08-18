#!/usr/bin/env bash
set -euo pipefail

server_port="${PORT:-5006}"

if [[ -n "${BOKEH_ALLOW_WS_ORIGIN:-}" ]]; then
  exec uv run bokeh serve app \
    --address 0.0.0.0 \
    --port "${server_port}" \
    --use-xheaders \
    "--allow-websocket-origin=${BOKEH_ALLOW_WS_ORIGIN}"
fi

exec uv run bokeh serve app \
  --address 0.0.0.0 \
  --port "${server_port}" \
  --use-xheaders
