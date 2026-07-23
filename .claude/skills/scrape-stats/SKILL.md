---
name: scrape-stats
description: Refresh post performance from the live TikTok posts into the Sheet. Use when the user says "refresh stats", "update the numbers", "scrape stats", "how are the posts doing", or on a cadence. Harvests each handled character's profile, matches Sheet rows by Post Link, writes the stats, and notes login-gated views.
---

# Scrape Stats (refresh the numbers)

Pulls each character's live post metrics off TikTok into the Sheet's fact tabs, so `analyze` and
`generate-post` (via `tuning/06_performance.md`) work from current numbers. Drives the CDP Chrome, same
profile as the cover gen.

> **`WORKFLOW.md §Stats` is canonical** for the commands. This skill sequences them + handles the
> login-gate and row-matching cases.

## Touches
- **Engine:** `engine/scrape/tiktok_profile.js`, `tiktok_stats.js`, `tiktok_login.js`,
  `engine/sheets/sheets.py` (`post-stats` / `post-set` / `stats-summary`), `engine/lib/quit_chrome.sh`.
- **State:** the `tiktok` @handle per character comes from `state.json` (resolved by `tiktok_profile.js`).

## Steps

**1 · Preflight the browser.** `bash engine/qc/preflight.sh` (launches the masquerade Chrome on :9222 if down).

**2 · Per character WITH a handle** (`state.json` → Ana `@solo.with.ana`, Chloe `@chloe.belletravel`;
**Hannah has no handle yet — skip her**):
```bash
node engine/scrape/tiktok_profile.js <key>        # resolves the @handle, harvests post URLs + stats
```

**3 · Match rows to posts.** Match each scraped post to its Sheet row by **Post Link**. If a posted row
has **no Post Link yet**, backfill it by matching the post's caption to the row's caption first (the
profile scrape gives you the URL + caption together), then write it.

**4 · Write the stats:**
```bash
python3 engine/sheets/sheets.py post-stats --character <key> --all      # every posted row (needs Post Link)
python3 engine/sheets/sheets.py post-stats --character <key> --id <prefix-NN>   # one row
node engine/scrape/tiktok_stats.js "<post url>"                          # one-off, one-line JSON
```

**5 · Login-gated views.** A photo post's **views** (and exact posting date) only hydrate via TikTok's
`/api/item/detail/` XHR **when the profile is logged in**. If `post-stats` warns "no views" or the Sheet's
Views go blank, the session lapsed — re-auth, then re-run step 4:
```bash
node engine/scrape/tiktok_login.js --open        # check state with no flag; --open re-authenticates
```
For anything the scraper still can't reach, enter it by hand:
```bash
python3 engine/sheets/sheets.py post-set --character <key> --id <prefix-NN> --views ... --likes ... --comments ... --share ... --save ...
```

**6 · Quit Chrome + eyeball.** Always:
```bash
bash engine/lib/quit_chrome.sh
python3 engine/sheets/sheets.py stats-summary     # then glance at the Dashboard tab
```

## Rules
- **Only characters with a `tiktok` handle** in `state.json` auto-scrape. Hannah's handle is pending —
  enter her stats by hand with `post-set` once she is live, or wait until her handle is registered.
- **Cite stats from the LIVE Sheet**, never a cached note.
- **Always quit Chrome** when CDP work is done (a Stop hook is the safety net; non-Claude agents run it manually).

## Output
The character fact tabs carry current Views / Likes / Comments / Shares / Saves; missing Post Links are
backfilled; login-gated gaps are flagged or hand-entered. Feeds `analyze`.
