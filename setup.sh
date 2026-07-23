#!/usr/bin/env bash
# Project Ana 2.0 — one-command onboarding for a fresh clone (wraps engine/setup/bootstrap.py).
# Passes flags straight through, e.g.  bash setup.sh --full  (also pull media/library scratch).
set -euo pipefail
cd "$(dirname "$0")"
exec python3 engine/setup/bootstrap.py "$@"
