#!/usr/bin/env bash
# Preflight for the content loop. Ensures the CDP Chrome (cover gen + inspo pullers),
# the Playwright install, and API keys/creds are ready. Idempotent; safe to re-run.
# Exit 0 = ready, non-zero = a hard dependency is missing.
set -uo pipefail

PORT=9222
PROFILE="$HOME/.masquerade_chrome"
# Chrome binary: override with $CHROME_BIN for non-macOS / non-default installs.
CHROME="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
# engine/qc -> up two = repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
fail=0

echo "== preflight =="

# 1. API keys (sourcing)
if [ -f "$ROOT/keys.env" ]; then echo "  [ok]   keys.env present"
else echo "  [FAIL] keys.env missing at repo root"; fail=1; fi

# 2. Sheets service-account key (dashboard)
if ls "$ROOT"/holicay-*.json >/dev/null 2>&1; then echo "  [ok]   Sheets service-account key present"
else echo "  [warn] Sheets key missing — dashboard sync will fail"; fi

# 3. CDP Chrome on :9222 (cover gen + TikTok inspo pullers)
if curl -s --max-time 3 "http://localhost:$PORT/json/version" >/dev/null 2>&1; then
  echo "  [ok]   Chrome CDP up on :$PORT"
else
  echo "  [..]   Chrome CDP down — launching masquerade profile"
  "$CHROME" --remote-debugging-port=$PORT --user-data-dir="$PROFILE" \
            --no-first-run --no-default-browser-check "https://chatgpt.com/" >/dev/null 2>&1 &
  up=0
  for i in $(seq 1 30); do
    sleep 1
    if curl -s --max-time 3 "http://localhost:$PORT/json/version" >/dev/null 2>&1; then
      echo "  [ok]   Chrome CDP came up on :$PORT (login persists in the profile)"; up=1; break
    fi
  done
  [ "$up" -eq 0 ] && { echo "  [FAIL] Chrome CDP did not come up on :$PORT"; fail=1; }
fi

# 4. Playwright resolvable (the one canonical install everything symlinks to)
CANON="$ROOT/engine/node_modules"
if [ -d "$CANON/playwright" ]; then echo "  [ok]   Playwright install found"
else echo "  [warn] canonical Playwright node_modules not found — per-post symlinks may be broken"; fi

if [ "$fail" -eq 0 ]; then echo "== preflight OK =="; else echo "== preflight HAD FAILURES =="; fi
exit "$fail"
