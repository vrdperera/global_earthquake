#!/usr/bin/env bash
set -euo pipefail

server_port="${PORT:-5006}"
deployment_host="${BOKEH_ALLOW_WS_ORIGIN:-${RAILWAY_PUBLIC_DOMAIN:-${RENDER_EXTERNAL_HOSTNAME:-}}}"

if [[ -n "${deployment_host}" ]]; then
  exec uv run bokeh serve app \
    --address 0.0.0.0 \
    --port "${server_port}" \
    --use-xheaders \
    "--allow-websocket-origin=${deployment_host}"
fi

exec uv run bokeh serve app \
  --address 0.0.0.0 \
  --port "${server_port}" \
  --use-xheaders
