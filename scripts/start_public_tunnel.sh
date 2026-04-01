#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared is not installed."
  echo "Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

if ! python -c "import fastapi" >/dev/null 2>&1; then
  pip install -r requirements.txt
fi

APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-8000}"

python -m uvicorn backend.app.main:app --host "$APP_HOST" --port "$APP_PORT" &
APP_PID=$!

cleanup() {
  if ps -p "$APP_PID" >/dev/null 2>&1; then
    kill "$APP_PID"
  fi
}

trap cleanup EXIT INT TERM

sleep 2

echo "Starting public tunnel..."
echo "Share the https://*.trycloudflare.com URL shown below."
cloudflared tunnel --url "http://$APP_HOST:$APP_PORT"
