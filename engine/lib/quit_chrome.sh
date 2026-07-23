#!/usr/bin/env bash
# quit_chrome.sh — actually QUIT the masquerade CDP Chrome (not just detach CDP).
#
# Every engine script ends with `browser.close()`, but on a connectOverCDP()
# connection that only drops the CDP client — the Chrome process keeps running
# on :9222 (see the "// leaves Chrome running" comments in scrape/ + design/).
# This is the ONE command that terminates it, so no browser window is left open
# after cover gen / scraping.
#
# Targets ONLY the ~/.masquerade_chrome profile (the launch cmdline carries
# `--user-data-dir=.../.masquerade_chrome`), so it never touches the user's
# personal Chrome. SIGTERM (pkill's default) lets Chrome flush the profile —
# TikTok login cookies persist to disk, so the next scrape reuses the session.
#
# Idempotent + fast: exits 0 whether or not a masquerade Chrome was running,
# so it's safe to call at the end of every run (and from a Stop hook).
pkill -f masquerade_chrome 2>/dev/null
exit 0
