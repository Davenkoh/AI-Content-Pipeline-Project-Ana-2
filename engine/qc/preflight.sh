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

# 2. Google service-account key (Sheets dashboard + Drive delivery)
if ls "$ROOT"/holicay-*.json "$ROOT"/masquerade-*.json "$ROOT"/*service_account*.json "$ROOT"/*-service-account.json >/dev/null 2>&1; then
  echo "  [ok]   Google service-account key present"
else echo "  [warn] service-account key missing — Sheets dashboard + Drive delivery will fail"; fi

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

# 4. Playwright resolvable — the one canonical install (build.js + route_map_shot.js walk up to it)
CANON="$ROOT/engine/node_modules"
if [ -d "$CANON/playwright" ]; then echo "  [ok]   Playwright install found (engine/node_modules)"
else echo "  [FAIL] Playwright not installed at engine/node_modules — run 'npm ci' in engine/ (renders will fail)"; fail=1; fi

# 5. Framework renderer fonts (TikTok Sans, bundled locally so renders don't depend on the network)
FONTS="$ROOT/engine/render/assets/fonts"
if [ -f "$FONTS/tiktok-sans.css" ] && [ -f "$FONTS/TikTokSans-latin.woff2" ] && [ -f "$FONTS/TikTokSans-latin-ext.woff2" ]; then
  echo "  [ok]   TikTok Sans fonts present (css + 2 woff2)"
else echo "  [FAIL] TikTok Sans fonts missing at engine/render/assets/fonts/ (renders would fall back to Montserrat)"; fail=1; fi

if [ "$fail" -eq 0 ]; then echo "== preflight OK =="; else echo "== preflight HAD FAILURES =="; fi
exit "$fail"
