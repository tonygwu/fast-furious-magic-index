#!/usr/bin/env bash
# Render the social cards from the same page and the same data the site serves.
# Usage: scripts/render_cards.sh   (from the repo root)
set -euo pipefail
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PORT="${PORT:-8799}"
OUT="web/social"
TMP="$(mktemp -d)"
trap 'kill %1 2>/dev/null || true; rm -rf "$TMP"' EXIT

[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME; set CHROME=..." >&2; exit 1; }
python3 -m http.server "$PORT" --directory web >/dev/null 2>&1 &
sleep 1
mkdir -p "$OUT"

render() { # kind width height filename
  cat > "$TMP/$1.html" <<HTML
<!doctype html><meta charset=utf-8><body style="margin:0">
<iframe src="http://127.0.0.1:$PORT/index.html?card=$1&theme=dark"
        style="width:$2px;height:$3px;border:0;display:block"></iframe>
HTML
  "$CHROME" --headless --disable-gpu --no-sandbox --allow-file-access-from-files \
    --window-size="$2,$3" --virtual-time-budget=6000 \
    --screenshot="$OUT/$4" "file://$TMP/$1.html" 2>/dev/null
  echo "rendered $OUT/$4 ($2x$3)"
}

render main 1200 1500 fast-magic-index.png
render og   1200 630  og-card.png
