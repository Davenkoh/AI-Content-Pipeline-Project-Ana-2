#!/usr/bin/env bash
# Project Ana 2.0 — the "git push" for media + posts.
#
# Makes the CLOUD copies (Drive) an exact mirror of your local working copy — the clone model:
# a real local copy that you sync up on demand (robust offline; nothing breaks when the Drive mount is
# unmounted). Run it after you edit or generate anything locally. (The Google Sheet itself is always
# live via sheets.py — there's no local Sheet to sync; this reconciles the MEDIA + posts.)
#
#   ./sync.sh
#
# What it does:
#   1. all character refs + _shared (wardrobe/pfp) + brand + chars + media/graded + media/brand
#      -> Drive, with --prune (deletions propagate; media/library scratch is never mirrored)
#   2. any built-but-undelivered post                       -> Drive
set -euo pipefail
cd "$(dirname "$0")"

echo "== sync 1/2: media -> Drive (mirror + prune) =="
python3 engine/drive/drive_sync.py --mirror-all --prune

echo "== sync 2/2: undelivered posts -> Drive =="
python3 engine/sheets/sheets.py deliver-missing

echo "[sync] done — the cloud now mirrors local."
