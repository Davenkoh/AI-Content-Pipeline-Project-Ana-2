#!/usr/bin/env bash
# One-command onboarding for a fresh clone. See SETUP.md for the full walkthrough.
set -euo pipefail
cd "$(dirname "$0")"
exec python3 engine/setup/bootstrap.py "$@"
