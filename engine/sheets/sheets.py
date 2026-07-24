#!/usr/bin/env python3
"""
sheets.py — Project Ana 2.0's Google Sheet, the human-facing FRONT-END.

One spreadsheet, spec-driven. SPEC (below) is the SINGLE SOURCE OF TRUTH for every
tab and column: it generates the banded headers, the colours, the cell-notes, the
dropdowns, AND the self-documenting Dictionary tab. Change a column in SPEC and
everything else follows.

2.0 is a FRAMEWORK-POST machine (A / B / C1 / C2 per CONTRACT.md). The 1.0 technique-
library tabs are gone — every post is one of four frameworks in a fixed rotation, each
rendered in a `human` or `nohuman` variant. The rotation is DERIVED from the character's
own fact tab (never a local counter) via `next-slot`; the whole Sheet is the source of truth.

Reading conventions baked into the sheet
  • Each tab is split into visually-banded SECTIONS so the "meat" is obvious vs the
    stats / metadata: POST CREATION=coral, STATS=navy, AI METADATA=grey, and
    HUMAN INPUT=GREEN. Anything GREEN (the Human Feedback column, the Connectors
    Notes column, or the whole Holicay Brand tab) is yours to fill; the AI only
    reads + clears it when you ask.
  • Each character (Ana, Chloe, Hannah, …) has its OWN fact tab (one row per post)
    carrying the framework/variant it ran + that post's own stats. Rotation, the
    Dashboard and the analyze summary all read across these fact tabs — there are
    no cross-tab link columns.

Tabs
  Ana, Chloe, Hannah, …   one row per post, per character (the per-character fact tables).
  Holicay Brand           GREEN — you own this; the AI reads it.
  Connectors              the integrations/credentials register (Notes = GREEN, yours).
  Dashboard               live formulas: pipeline state + performance analytics (dashboard-init).
  Dictionary              auto-generated reference for every tab + column.

Common commands
  python3 sheets.py init                        # build/format every tab + Connectors + Dashboard + Dictionary
  python3 sheets.py migrate-schema              # realign existing rows to the current spec (run BEFORE init)
  python3 sheets.py next-slot --character ana [--country Vietnam] [--reserve]   # the next framework/variant slot
  python3 sheets.py next-number --character ana [--reserve]                     # just the next post number
  python3 sheets.py post-upsert --character ana --id tt-28 --title "..." --framework A --variant human \
        --country Vietnam --iteration 1 --folder "<link>" --caption "..." --notes "..."
  python3 sheets.py post-set --character ana --id tt-28 --post-link "<url>"
  python3 sheets.py post-stats --character ana --id tt-28    # scrape the live post's metrics (needs Post Link)
  python3 sheets.py post-stats --character ana --all
  python3 sheets.py deliver-missing             # push built-but-undelivered posts -> Drive, record the link
  python3 sheets.py dashboard-init              # (re)build the live Dashboard tab
  python3 sheets.py connectors-init             # seed/refresh the Connectors register
  python3 sheets.py stats-summary [--json]      # performance rollups for the analyze skill
  python3 sheets.py read --tab Ana              # -> JSON rows
  python3 sheets.py feedback-poll               # every GREEN cell with content
  python3 sheets.py feedback-clear --tab ana --id tt-28 --note "applied"
"""
import argparse, glob, json, os, subprocess, sys, datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ── shared tab names ──────────────────────────────────────────────────────────
BRAND_TAB = "Holicay Brand"
CONN_TAB  = "Connectors"
ACCT_TAB  = "Accounts"
DASH_TAB  = "Dashboard"
DICT_TAB  = "Dictionary"

# Repo doc the Dictionary tab points newcomers to (the full 2.0 blueprint, on GitHub).
BLUEPRINT_URL = "https://github.com/Davenkoh/Project-Ana-2"


# ── character registry ────────────────────────────────────────────────────────
# state.json is the single source of truth for the roster. Each character has its OWN
# fact-table tab named after it. A 2.0 character = a registry entry (name, id_prefix,
# default content country, TikTok @handle) — no per-character text files.
def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.path.dirname(os.path.abspath(__file__))


def _state():
    sp = os.path.join(_root(), "state.json")
    try:
        return json.load(open(sp)) or {}
    except Exception:
        return {}


def _characters():
    """key -> {key, name, tab, id_prefix, country}. Tab name == character name. Falls
    back to a lone 'ana' if the roster is unset."""
    raw = _state().get("characters") or {"ana": {"name": "Ana", "id_prefix": "tt"}}
    out = {}
    for key, c in raw.items():
        c = c or {}
        name = c.get("name") or key.capitalize()
        out[key] = {"key": key, "name": name, "tab": name,
                    "id_prefix": c.get("id_prefix", "tt"), "country": c.get("country", "")}
    return out


def _default_char_key():
    return _state().get("default_character") or next(iter(_characters()))


def _char_for(arg):
    """Resolve a --character value (key or display name, case-insensitive) to a registry entry."""
    chars = _characters()
    if not arg:
        return chars[_default_char_key()]
    a = str(arg).strip().lower()
    for c in chars.values():
        if a in (c["key"], c["name"].lower(), c["tab"].lower()):
            return c
    sys.exit(f"[sheets] unknown character {arg!r}; known: {', '.join(chars)}")


# ── colours (0..1 rgb) ────────────────────────────────────────────────────────
CORAL  = {"red": 0.949, "green": 0.318, "blue": 0.259}   # POST CREATION (the meat)
NAVY   = {"red": 0.075, "green": 0.227, "blue": 0.290}   # STATS / metadata
GRAY   = {"red": 0.45,  "green": 0.45,  "blue": 0.45}     # AI metadata
GREEN  = {"red": 0.18,  "green": 0.49,  "blue": 0.20}     # HUMAN INPUT
WHITE  = {"red": 1, "green": 1, "blue": 1}
T_CORAL = {"red": 0.992, "green": 0.918, "blue": 0.902}
T_NAVY  = {"red": 0.866, "green": 0.910, "blue": 0.937}
T_GRAY  = {"red": 0.93,  "green": 0.93,  "blue": 0.93}
T_GREEN = {"red": 0.851, "green": 0.929, "blue": 0.827}
SECTION_COLOR = {"meat": (CORAL, T_CORAL), "stats": (NAVY, T_NAVY),
                 "meta": (NAVY, T_NAVY), "ai": (GRAY, T_GRAY), "human": (GREEN, T_GREEN)}

# ── cell-notes ────────────────────────────────────────────────────────────────
HUMAN_NOTE = ("GREEN = your input. Write here; the AI reads it when you ask, acts on it, "
              "and clears the cell. Leave blank when you have nothing to say.")
AI_NOTE    = "AI-only bookkeeping. You don't need to touch this."

# ── framework rotation constants (the durable 2.0 spec) ───────────────────────
FRAMEWORKS = ["A", "B", "C1", "C2"]
VARIANTS   = ["human", "nohuman"]
VARIANT_DEFAULT = {"A": "human", "B": "human", "C1": "human", "C2": "nohuman"}

# ── dropdown options ──────────────────────────────────────────────────────────
# Framework + Variant dropdowns are attached to every character fact tab (built below).
DROPDOWNS = {}


# ── SPEC: the single source of truth ─────────────────────────────────────────
# C(name, section, who, desc, example)
#   section: meat | stats | meta | human | ai
#   who    : "AI" | "Human" | "AI + Human"   (shown in the Dictionary)
def C(name, section, who, desc, example):
    return {"name": name, "section": section, "who": who, "desc": desc, "example": example}


def _fact_spec():
    """The per-character fact table (one row per post). Same schema for every character.
    Columns A–T. Bands: POST CREATION (coral) ID→Notes · STATS (navy) Post Link→Stats Last
    Updated · HUMAN INPUT (green) Human Feedback · AI METADATA (grey) Metadata."""
    return {
        "sections": {"meat": "POST CREATION", "stats": "STATS",
                     "human": "HUMAN INPUT", "ai": "AI METADATA"},
        "columns": [
            C("ID", "meat", "AI", "Unique post id (continues each account's 1.0 numbering). Presence here = a planned/built post.", "tt-28"),
            C("Country", "meat", "AI", "The content country this post targets.", "Vietnam"),
            C("Framework", "meat", "AI", "Which content framework this post runs (A/B/C1/C2). Empty = a 1.0-era marker row (ignored by rotation).", "A"),
            C("Variant", "meat", "AI", "human = character-in-scene cover+ending · nohuman = pure scenic, same text.", "human"),
            C("Copy Iteration", "meat", "AI", "Nth time this (Framework, Country) copy has been run across ALL characters.", "1"),
            C("Title", "meat", "AI", "Post title / the local outputs/<char>/ folder name AND the Drive folder name.", "28 - Hidden Gems in Vietnam"),
            C("Output Folder", "meat", "AI", "Drive link to the built carousel.", "https://drive.google.com/drive/folders/..."),
            C("Caption", "meat", "AI", "The caption posted with the carousel.", "saving you the research for vietnam ..."),
            C("Date Created", "meat", "AI", "When the post was built.", "2026-07-23"),
            C("Notes", "meat", "AI", "Plain-English context the HUMAN should read about this post.", "first framework-A run for Vietnam"),
            C("Post Link", "stats", "AI + Human", "The live TikTok URL once posted. Drop it here; presence = 'posted'. Feeds the stats scraper.", "https://www.tiktok.com/@user/photo/123"),
            C("Posting Date", "stats", "AI", "When it went live (scraped).", "2026-07-24"),
            C("Views", "stats", "AI", "Views (scraped).", "12000"),
            C("Likes", "stats", "AI", "Likes (scraped).", "800"),
            C("Comments", "stats", "AI", "Comments (scraped).", "40"),
            C("Share", "stats", "AI", "Shares (scraped).", "25"),
            C("Save", "stats", "AI", "Saves / bookmarks (scraped).", "300"),
            C("Stats Last Updated", "stats", "AI", "When the stats above were last refreshed.", "2026-07-26 18:00"),
            C("Human Feedback", "human", "Human", "YOUR steer on this post. The AI reads it when you ask, acts, and clears it.", "cover felt flat, try a bolder hook"),
            C("Metadata", "ai", "AI", "AI-only bookkeeping (e.g. when feedback was processed, slot-reservation stamps).", "feedback processed 2026-07-25"),
        ],
    }


def _brand_spec():
    # whole tab is human-owned -> every section is "human" (all green). Kept verbatim from 1.0.
    return {
        "sections": {"human": "HOLICAY BRAND — YOU OWN THIS TAB (the AI reads it)"},
        "columns": [
            C("ID", "human", "Human", "Row id.", "B001"),
            C("Brand Feature", "human", "Human", "A Holicay feature.", "AI trip planner"),
            C("Use Case", "human", "Human", "The job the feature does (name the use case, not the feature).", "auto-build a day-by-day itinerary"),
            C("Description", "human", "Human", "Plain description for the AI to ground copy in.", "describe your trip and it drafts a plan you can edit"),
            C("Media Asset Link", "human", "Human", "Drive/asset link for screenshots/demos.", "https://drive.google.com/.../planner.png"),
            C("Funnel Fit", "human", "Human", "Which funnels this feature suits.", "F4, F5"),
            C("Notes", "human", "Human", "Anything else the AI should know.", "emphasize the use case, never say 'download'"),
        ],
    }


def _connectors_spec():
    # Every column is AI-maintained reference EXCEPT Notes, which is GREEN (yours). Status is
    # seeded but you may edit it. Rows are seeded by `connectors-init`.
    return {
        "sections": {"meat": "CONNECTOR (integration / credential register)", "human": "HUMAN INPUT"},
        "columns": [
            C("Connector", "meat", "AI", "The integration / service.", "Google Places"),
            C("Purpose", "meat", "AI", "What the pipeline uses it for.", "user photos + Maps Embed route shots"),
            C("Auth (env var / credential file)", "meat", "AI", "How it authenticates: keys.env var name or the credential file at repo root.", "keys.env PLACES"),
            C("Account / identity", "meat", "AI", "The account / service identity behind it.", "billed to that key's Google Cloud project"),
            C("Console URL", "meat", "AI", "Where a human manages it.", "console.cloud.google.com"),
            C("Plan & cost", "meat", "AI", "Pricing tier / cost model.", "billed to the Google Cloud project of that key"),
            C("Status", "meat", "AI", "Working state (ACTIVE / PARTIAL / legacy·optional) + a short qualifier.", "ACTIVE — primary UGC source"),
            C("Notes", "human", "Human", "YOUR notes / steers on this connector. The AI reads it when you ask, acts, and clears it.", "rotate the key before launch"),
        ],
    }


def _accounts_spec():
    # Per-character account / login register. Whole tab is human-owned (all green) — YOU keep it
    # current; the AI only reads it (e.g. to know which profile / VPN region an account uses).
    # Credentials are entered on the Sheet, never stored in this repo. Deliberately low-sensitivity
    # accounts only (the human confirmed these are OK to keep here).
    return {
        "sections": {"human": "ACCOUNTS — YOU OWN THIS TAB (per-character logins / VPN; the AI reads it)"},
        "columns": [
            C("Character", "human", "Human", "Which character this account belongs to.", "<character name>"),
            C("TikTok Profile", "human", "Human", "Public TikTok profile URL.", "https://www.tiktok.com/@handle"),
            C("TikTok Login", "human", "Human", "TikTok username, or how to sign in.", "handle (via the Gmail below)"),
            C("Gmail", "human", "Human", "The Gmail account the persona uses.", "persona@gmail.com"),
            C("Gmail Password", "human", "Human", "Gmail password, or who holds it.", "•••• (or: with <teammate>)"),
            C("Created By", "human", "Human", "Who set the account up.", "<teammate>"),
            C("VPN Location", "human", "Human", "VPN region the account is operated from.", "City, Country"),
            C("Notes", "human", "Human", "Anything else (who holds creds, status).", "TikTok login goes through the Gmail"),
        ],
    }


# Build SPEC: one fact tab per character (roster order), then the shared tabs. The Dashboard is
# NOT in SPEC — it is a derived analytics view written by `dashboard-init`.
SPEC = {c["tab"]: _fact_spec() for c in _characters().values()}
SPEC[BRAND_TAB] = _brand_spec()
SPEC[CONN_TAB]  = _connectors_spec()
SPEC[ACCT_TAB]  = _accounts_spec()

# derived: HEADERS[tab] = ordered column names; HEADER_ROWS = 2 for all SPEC tabs
HEADERS = {tab: [c["name"] for c in s["columns"]] for tab, s in SPEC.items()}
HEADER_ROWS = 2

# Framework + Variant dropdowns on every fact tab
for _c in _characters().values():
    DROPDOWNS[(_c["tab"], "Framework")] = FRAMEWORKS
    DROPDOWNS[(_c["tab"], "Variant")]   = VARIANTS


# The set of fact-tab names (character tabs), in roster order.
def _fact_tabs():
    return [c["tab"] for c in _characters().values()]


# ── plumbing ─────────────────────────────────────────────────────────────────
def _sheet_id():
    env = os.environ.get("HOLICAY_SHEET_ID")
    if env:
        return env
    sid = (_state() or {}).get("sheet_id")
    if sid:
        return sid
    sys.exit("[sheets] state.json sheet_id is empty — run engine/setup/provision.py first")


def _find_creds():
    override = os.environ.get("HOLICAY_SA_JSON")
    if override and os.path.exists(override):
        return override
    p = os.path.dirname(os.path.abspath(__file__))
    while True:
        for f in sorted(glob.glob(os.path.join(p, "*.json"))):
            try:
                if json.load(open(f)).get("type") == "service_account":
                    return f
            except Exception:
                pass
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    sys.exit("[sheets] no service-account JSON found at repo root (holicay-*.json) — "
             "run engine/setup/provision.py or place it there (set $HOLICAY_SA_JSON to override)")


def _client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as e:
        sys.exit(f"[sheets] missing dependency: {e}. Run: python3 -m pip install gspread")
    creds = Credentials.from_service_account_file(_find_creds(), scopes=SCOPES)
    return gspread.authorize(creds)


def _open():
    sid = _sheet_id()        # check sheet_id FIRST (the most actionable fix: provision.py fills it)
    return _client().open_by_key(sid)


def _today():
    return datetime.date.today().isoformat()


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _iso_ts():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _a1col(i):                                   # 0-based -> A1 column letters
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def _ws(sh, title):
    for w in sh.worksheets():
        if w.title == title:
            return w
    return None


def _next_id(ws, prefix):
    """Largest prefix+NNN in column A, +1 (3-digit; used for Brand B-ids)."""
    n = 0
    for v in ws.col_values(1):
        if v.startswith(prefix) and v[len(prefix):].isdigit():
            n = max(n, int(v[len(prefix):]))
    return f"{prefix}{n + 1:03d}"


def _next_post_id(ws, prefix):
    """Next `<prefix>-NN` id: scan col A for the character's ids, return (id, nn) = max+1.
    Skips banner/header and any non `<prefix>-<digits>` rows. 2-digit zero-padded (wider if needed)."""
    pre = prefix + "-"
    n = 0
    for v in ws.col_values(1):
        v = (v or "").strip()
        if v.startswith(pre) and v[len(pre):].isdigit():
            n = max(n, int(v[len(pre):]))
    nn = n + 1
    return f"{prefix}-{nn:02d}", nn


def _row_for_id(ws, target, header_rows=HEADER_ROWS):
    ids = ws.col_values(1)
    for i, v in enumerate(ids[header_rows:], start=header_rows + 1):
        if v == target:
            return i
    return None


# ── tab building (banded, spec-driven) ───────────────────────────────────────
def _runs(cols):
    """Contiguous (start, end, section_key) runs for banner merges."""
    out, i = [], 0
    while i < len(cols):
        j = i
        while j < len(cols) and cols[j]["section"] == cols[i]["section"]:
            j += 1
        out.append((i, j, cols[i]["section"]))
        i = j
    return out


def _ensure_tab(sh, tab):
    spec = SPEC[tab]
    cols = spec["columns"]
    headers = HEADERS[tab]
    ncols = len(headers)
    ws = _ws(sh, tab)
    if ws is None:
        first = sh.sheet1
        if first.title in ("Sheet1", "Sheet 1") and not first.get_all_values():
            first.update_title(tab); ws = first
        else:
            ws = sh.add_worksheet(title=tab, rows=1000, cols=ncols + 2)
    if ws.col_count < ncols:                 # widen if the spec added columns
        ws.add_cols(ncols - ws.col_count)
    if ws.row_count < 1000:
        ws.add_rows(1000 - ws.row_count)
    runs = _runs(cols)
    banner = [""] * ncols
    for (s, e, key) in runs:
        banner[s] = spec["sections"].get(key, key.upper())
    end = _a1col(ncols - 1)
    # unmerge the header band FIRST — writing a banner value into a cell that sits inside a
    # stale merge (non-anchor) is silently dropped, which leaves later section labels blank.
    try:
        sh.batch_update({"requests": [{"unmergeCells": {"range": {"sheetId": ws.id,
            "startRowIndex": 0, "endRowIndex": 2, "startColumnIndex": 0,
            "endColumnIndex": max(ncols, ws.col_count)}}}]})
    except Exception:
        pass
    ws.batch_update([
        {"range": f"A1:{end}1", "values": [banner]},
        {"range": f"A2:{end}2", "values": [headers]},
    ])
    _format_tab(sh, ws, tab, cols, runs)
    return ws


def _format_tab(sh, ws, tab, cols, runs):
    gid = ws.id
    ncols = len(cols)

    def rng(r0, r1, c0, c1):
        return {"sheetId": gid, "startRowIndex": r0, "endRowIndex": r1,
                "startColumnIndex": c0, "endColumnIndex": c1}

    # unmerge the ENTIRE header row across the real grid width (a prior layout may have
    # merged a wider range; a partial unmerge range is rejected by the API).
    reqs = [{"unmergeCells": {"range": rng(0, 1, 0, max(ncols, ws.col_count))}}]
    for (s, e, key) in runs:
        banner_bg, tint = SECTION_COLOR[key]
        if e - s > 1:
            reqs.append({"mergeCells": {"range": rng(0, 1, s, e), "mergeType": "MERGE_ALL"}})
        reqs.append({"repeatCell": {"range": rng(0, 1, s, e),
            "cell": {"userEnteredFormat": {"backgroundColor": banner_bg, "horizontalAlignment": "CENTER",
                     "textFormat": {"bold": True, "foregroundColor": WHITE, "fontSize": 11}}},
            "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"}})
        reqs.append({"repeatCell": {"range": rng(1, 2, s, e),
            "cell": {"userEnteredFormat": {"backgroundColor": tint, "wrapStrategy": "WRAP",
                     "textFormat": {"bold": True}}},
            "fields": "userEnteredFormat(backgroundColor,wrapStrategy,textFormat)"}})
    # freeze the 2 header rows
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": gid,
        "gridProperties": {"frozenRowCount": 2}}, "fields": "gridProperties.frozenRowCount"}})
    # tint the whole HUMAN columns green (so the input area is obvious below the header too)
    for i, c in enumerate(cols):
        if c["section"] == "human":
            reqs.append({"repeatCell": {"range": rng(2, 1000, i, i + 1),
                "cell": {"userEnteredFormat": {"backgroundColor": T_GREEN}},
                "fields": "userEnteredFormat.backgroundColor"}})
        note = HUMAN_NOTE if c["section"] == "human" else (AI_NOTE if c["section"] == "ai" else "")
        reqs.append({"repeatCell": {"range": rng(1, 2, i, i + 1),
            "cell": {"note": note}, "fields": "note"}})
        opts = DROPDOWNS.get((tab, c["name"]))
        if opts:
            reqs.append({"setDataValidation": {"range": rng(2, 1000, i, i + 1),
                "rule": {"condition": {"type": "ONE_OF_LIST",
                         "values": [{"userEnteredValue": o} for o in opts]},
                         "showCustomUi": True, "strict": False}}})
    # column widths
    for i, c in enumerate(cols):
        w = _width(c)
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": gid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    try:
        sh.batch_update({"requests": reqs})
    except Exception as e:
        print(f"[sheets] {tab}: formatting partial: {e}", file=sys.stderr)


def _width(c):
    long_text = {"Caption", "Human Feedback", "Notes", "Metadata", "Description",
                 "Use Case", "Purpose", "Account / identity", "Plan & cost", "Status",
                 "Auth (env var / credential file)"}
    ids = {"ID", "Framework", "Variant", "Copy Iteration"}
    if c["name"] in ids:
        return 90
    if c["name"] in long_text:
        return 300
    if c["name"] in ("Output Folder", "Post Link", "Media Asset Link", "Console URL", "Connector"):
        return 200
    return 130


# ── generic read ─────────────────────────────────────────────────────────────
def _read_rows(sh, tab):
    ws = _ws(sh, tab)
    if ws is None:
        return []
    headers = HEADERS[tab]
    vals = ws.get_all_values()[HEADER_ROWS:]
    return [dict(zip(headers, r + [""] * (len(headers) - len(r)))) for r in vals]


# ── commands: build / migrate / dictionary ───────────────────────────────────
# 2.0 starts from a fresh Sheet, so there is no legacy data to remap. These maps are
# intentionally EMPTY (migrate-schema still realigns a hand-edited sheet onto the SPEC by
# column NAME + rebuilds the banded layout). Populate them only if a real migration arises.
TAB_RENAMES = {}          # legacy whole-worksheet renames (old title -> new title)
RENAMES = {}              # per-tab {old col -> new col}
DROPS = {}                # per-tab {cols to discard}


def cmd_init(_):
    sh = _open()
    for tab in SPEC:
        _ensure_tab(sh, tab)
    _build_dictionary(sh)
    try:
        _seed_connectors(sh)
    except Exception as e:
        print(f"[sheets] connectors seed skipped: {e}", file=sys.stderr)
    try:
        _build_dashboard(sh)
    except Exception as e:
        print(f"[sheets] dashboard build skipped: {e}", file=sys.stderr)
    print("[sheets] init OK — tabs: " + ", ".join(list(SPEC) + [DASH_TAB, DICT_TAB]))
    print(f"  https://docs.google.com/spreadsheets/d/{_sheet_id()}/edit")


def cmd_migrate_schema(_):
    """Realign existing rows to the current SPEC by column NAME, honouring RENAMES/DROPS,
    and convert every tab to the 2-row banded layout. Run BEFORE `init`. Idempotent.
    (On a fresh 2.0 sheet this is a no-op; it exists for hand-edited-column recovery.)"""
    sh = _open()
    for old, new in TAB_RENAMES.items():
        if _ws(sh, old) and not _ws(sh, new):
            _ws(sh, old).update_title(new)
            print(f"[migrate-schema] renamed worksheet {old!r} -> {new!r}")
    for tab in SPEC:
        ws = _ws(sh, tab)
        if ws is None:
            print(f"[migrate-schema] {tab}: absent, will be created by init"); continue
        new_headers = HEADERS[tab]
        grid = ws.get_all_values()
        if not grid:
            print(f"[migrate-schema] {tab}: empty"); continue
        first = new_headers[0]
        if grid[0] and grid[0][0] == first:
            hidx = 0
        elif len(grid) > 1 and grid[1] and grid[1][0] == first:
            hidx = 1
        else:
            hidx = 0
        old_headers = grid[hidx]
        if old_headers == new_headers and hidx == 1:
            print(f"[migrate-schema] {tab}: already current"); continue
        ren = RENAMES.get(tab, {})
        drop = DROPS.get(tab, set())
        unknown = [h for h in old_headers if h and h not in new_headers
                   and h not in ren and h not in drop]
        if unknown:
            sys.exit(f"[migrate-schema] {tab}: unmapped old column(s) {unknown}; add to RENAMES/DROPS first")
        out = []
        for r in grid[hidx + 1:]:
            g = {}
            for i, h in enumerate(old_headers):
                if not h or h in drop:
                    continue
                g[ren.get(h, h)] = r[i] if i < len(r) else ""
            out.append([g.get(h, "") for h in new_headers])
        ws.clear()
        _ensure_tab(sh, tab)            # writes banner + headers + formatting
        if out:
            end = _a1col(len(new_headers) - 1)
            ws.batch_update([{"range": f"A3:{end}{2 + len(out)}", "values": out}],
                            value_input_option="USER_ENTERED")
        print(f"[migrate-schema] {tab}: {len(out)} row(s) -> {len(new_headers)} cols (banded)")
    print("[migrate-schema] done. Run `init` to rebuild the Dictionary + Dashboard + Connectors.")


def _build_dictionary(sh):
    """Grouped by tab: a clickable tab heading, then its columns. No Tab/Section columns."""
    NCOL = 4                                   # Column · Who fills it · Meaning · Example value
    ws = _ws(sh, DICT_TAB)
    if ws is None:
        ws = sh.add_worksheet(title=DICT_TAB, rows=400, cols=NCOL + 1)
    ws.clear()
    gid = ws.id
    try:                                       # drop stale merges (a prior layout was wider)
        sh.batch_update({"requests": [{"unmergeCells": {"range": {"sheetId": gid,
            "startRowIndex": 0, "endRowIndex": ws.row_count,
            "startColumnIndex": 0, "endColumnIndex": ws.col_count}}}]})
    except Exception:
        pass
    gid_of = {t: (_ws(sh, t).id if _ws(sh, t) else None) for t in SPEC}
    SUB = ["Column", "Who fills it", "Meaning", "Example value"]
    rows, heads, subs = [], [], []             # heads/subs = 0-based row indices to format
    rows.append(["DICTIONARY — what every tab + column means.  GREEN = human input (you fill "
                 "it; the AI reads & clears it). The Holicay Brand tab is entirely yours; the "
                 "Connectors Notes column is yours.", "", "", ""])
    rows.append([f'=HYPERLINK("{BLUEPRINT_URL}","START HERE  →  the full Project Ana 2.0 system '
                 '(frameworks · engine · data model · workflow · how to run it) — on GitHub")',
                 "", "", ""])
    rows.append(["", "", "", ""])
    for tab, spec in SPEC.items():
        g = gid_of[tab]
        heads.append(len(rows))
        rows.append([f'=HYPERLINK("#gid={g}","{tab}")' if g is not None else tab, "", "", ""])
        subs.append(len(rows))
        rows.append(SUB[:])
        for ci, c in enumerate(spec["columns"]):
            name = (f'=HYPERLINK("#gid={g}&range={_a1col(ci)}2","{c["name"]}")'
                    if g is not None else c["name"])
            rows.append([name, c["who"], c["desc"], c["example"]])
        rows.append(["", "", "", ""])          # spacer between groups
    # mention the Dashboard (a derived analytics view, not in SPEC)
    dw = _ws(sh, DASH_TAB)
    dg = dw.id if dw else None
    heads.append(len(rows))
    rows.append([f'=HYPERLINK("#gid={dg}","{DASH_TAB}")' if dg is not None else DASH_TAB, "", "", ""])
    subs.append(len(rows))
    rows.append(SUB[:])
    rows.append([DASH_TAB, "AI", "Live formulas only (no data of its own): per-character pipeline "
                 "state + performance analytics over the fact tabs. Rebuilt by `dashboard-init`.", ""])
    rows.append(["", "", "", ""])
    end = _a1col(NCOL - 1)
    ws.batch_update([{"range": f"A1:{end}{len(rows)}", "values": rows}],
                    value_input_option="USER_ENTERED")    # USER_ENTERED so HYPERLINK evaluates

    def band(r, bg, white, merge):
        out = []
        if merge:
            out.append({"mergeCells": {"range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
                "startColumnIndex": 0, "endColumnIndex": NCOL}, "mergeType": "MERGE_ALL"}})
        tf = {"bold": True}
        if white:
            tf["foregroundColor"] = WHITE
        out.append({"repeatCell": {"range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
            "startColumnIndex": 0, "endColumnIndex": NCOL},
            "cell": {"userEnteredFormat": {"backgroundColor": bg, "wrapStrategy": "WRAP", "textFormat": tf}},
            "fields": "userEnteredFormat(backgroundColor,wrapStrategy,textFormat)"}})
        return out
    reqs = band(0, GREEN, True, True)
    reqs += band(1, T_GREEN, False, True)      # START HERE -> blueprint pointer (clickable)
    for r in heads:
        reqs += band(r, NAVY, True, True)      # clickable tab heading spanning the row
    for r in subs:
        reqs += band(r, T_NAVY, False, False)
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": gid,
        "gridProperties": {"frozenRowCount": 2}}, "fields": "gridProperties.frozenRowCount"}})
    for i, w in enumerate((210, 130, 460, 300)):
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": gid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    sh.batch_update({"requests": reqs})
    print(f"[sheets] Dictionary rebuilt ({len(heads)} tab sections)")


# ── commands: posts (per-character fact tables) ──────────────────────────────
def _char_ws(sh, char):
    return _ws(sh, char["tab"]) or _ensure_tab(sh, char["tab"])


def cmd_post_upsert(a):
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    headers = HEADERS[char["tab"]]
    fields = {"ID": a.id, "Country": a.country or "", "Framework": a.framework or "",
              "Variant": a.variant or "", "Copy Iteration": a.iteration or "",
              "Title": a.title or "", "Output Folder": a.folder or "", "Caption": a.caption or "",
              "Notes": a.notes or "", "Metadata": a.metadata or ""}
    row = _row_for_id(ws, a.id)
    if row is None:
        fields["Date Created"] = _today()
        ws.append_row([fields.get(h, "") for h in headers],
                      value_input_option="USER_ENTERED", table_range="A2")
        print(f"[sheets] inserted {a.id}")
    else:
        ups = [{"range": f"{_a1col(headers.index(h))}{row}", "values": [[v]]}
               for h, v in fields.items() if v != ""]
        if ups:
            ws.batch_update(ups, value_input_option="USER_ENTERED")
        print(f"[sheets] updated {a.id} (row {row})")


def cmd_post_set(a):
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    headers = HEADERS[char["tab"]]
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no {char['name']} row for {a.id}; post-upsert it first")
    pairs = {}
    for arg, col in [("title", "Title"), ("folder", "Output Folder"), ("caption", "Caption"),
                     ("country", "Country"), ("framework", "Framework"), ("variant", "Variant"),
                     ("iteration", "Copy Iteration"), ("notes", "Notes"), ("metadata", "Metadata"),
                     ("post_link", "Post Link"), ("posting_date", "Posting Date"),
                     ("views", "Views"), ("likes", "Likes"), ("comments", "Comments"),
                     ("share", "Share"), ("save", "Save")]:
        v = getattr(a, arg, None)
        if v is not None:
            pairs[col] = _today() if v == "today" else v
    if any(k in pairs for k in ("Views", "Likes", "Comments", "Share", "Save")):
        pairs["Stats Last Updated"] = _now()
    ws.batch_update([{"range": f"{_a1col(headers.index(h))}{row}", "values": [[v]]}
                     for h, v in pairs.items()], value_input_option="USER_ENTERED")
    print(f"[sheets] set {a.id}: {list(pairs)}")


# ── rotation logic (pure — offline-testable) ─────────────────────────────────
def _other_variant(v):
    return "nohuman" if v == "human" else "human"


def compute_next_slot(char_rows, all_rows, country):
    """PURE rotation math (no I/O) — the durable 2.0 spec, mirrored by the Dashboard formula.

    char_rows : list of row-dicts for THIS character's fact tab (marker/1.0 rows included; they
                carry an EMPTY Framework so they are ignored here).
    all_rows  : list of row-dicts across ALL character fact tabs (for the cross-character copy count).
    country   : the resolved content country (override or the registry default).

    Returns {framework, variant, copy_iteration}. (id + country are decided by the caller.)
      framework      = FRAMEWORKS[len(my framework-bearing rows) % 4]
      variant        = default(framework) if that framework's prior count is even, else the other
                       (defaults: A/B/C1 -> human, C2 -> nohuman)
      copy_iteration = count of (framework, country) rows across ALL fact tabs + 1
    """
    mine = [r for r in char_rows if (r.get("Framework") or "").strip()]
    framework = FRAMEWORKS[len(mine) % 4]
    prior = sum(1 for r in mine if (r.get("Framework") or "").strip() == framework)
    default = VARIANT_DEFAULT[framework]
    variant = default if prior % 2 == 0 else _other_variant(default)
    ci = 1 + sum(1 for r in all_rows
                 if (r.get("Framework") or "").strip() == framework
                 and (r.get("Country") or "").strip() == country)
    return {"framework": framework, "variant": variant, "copy_iteration": ci}


def cmd_next_slot(a):
    """The next framework/variant slot for a character, DERIVED from the Sheet (never a local
    counter). Prints JSON {id, framework, variant, country, copy_iteration, reserved}.

    --reserve appends a stub row that atomically CLAIMS the slot on the shared Sheet (ID, Country,
    Framework, Variant, Copy Iteration, Title="(building)", Date Created, Metadata="reserved <ts>"),
    so a teammate running this a moment later sees the claim and rotates past it. Delivery
    (post-upsert, same id) fills the row in. An ABORTED build leaves the stub — clean it with
    `post-delete --character <k> --id <id>` so the number + rotation slot free up again."""
    char = _char_for(a.character)
    sh = _open()
    char_rows, all_rows = [], []
    for c in _characters().values():
        rows = _read_rows(sh, c["tab"])
        all_rows += rows
        if c["key"] == char["key"]:
            char_rows = rows
    country = a.country or char["country"]
    slot = compute_next_slot(char_rows, all_rows, country)
    ws = _char_ws(sh, char)
    pid, _nn = _next_post_id(ws, char["id_prefix"])
    out = {"id": pid, "framework": slot["framework"], "variant": slot["variant"],
           "country": country, "copy_iteration": slot["copy_iteration"], "reserved": False}
    if getattr(a, "reserve", False) and _row_for_id(ws, pid) is None:
        headers = HEADERS[char["tab"]]
        stub = {"ID": pid, "Country": country, "Framework": slot["framework"],
                "Variant": slot["variant"], "Copy Iteration": slot["copy_iteration"],
                "Title": "(building)", "Date Created": _today(),
                "Metadata": f"reserved {_iso_ts()}"}
        ws.append_row([stub.get(h, "") for h in headers],
                      value_input_option="USER_ENTERED", table_range="A2")
        out["reserved"] = True
    print(json.dumps(out))


def cmd_next_number(a):
    """Just the next post NUMBER for a character (lower-level than next-slot), derived from the
    Sheet: scans the fact tab col A for `<prefix>-NN` and returns max+1. Prints JSON. For framework
    posts prefer `next-slot` (it also picks framework + variant + copy iteration).

    --reserve appends a minimal stub claiming the id (no Framework, so it does NOT consume a
    rotation slot — use next-slot --reserve for that). Idempotent: skips the append if the id exists."""
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    pid, nn = _next_post_id(ws, char["id_prefix"])
    reserved = False
    if getattr(a, "reserve", False) and _row_for_id(ws, pid) is None:
        headers = HEADERS[char["tab"]]
        rowvals = {"ID": pid, "Title": a.title or "(building)",
                   "Date Created": _today(), "Metadata": f"reserved {_iso_ts()}"}
        ws.append_row([rowvals.get(h, "") for h in headers],
                      value_input_option="USER_ENTERED", table_range="A2")
        reserved = True
    print(json.dumps({"character": char["key"], "name": char["name"],
                      "prefix": char["id_prefix"], "nn": nn, "nn_padded": f"{nn:02d}",
                      "id": pid, "reserved": reserved}))


def cmd_post_delete(a):
    """Delete a post's row from its character tab (e.g. removing a duplicate or an aborted stub).
    Does NOT touch Drive or local files. Frees the number + rotation slot."""
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no {char['name']} row for {a.id}")
    ws.delete_rows(row)
    print(f"[sheets] deleted {a.id} (was row {row}) from tab {char['tab']}")


def cmd_deliver_missing(a):
    """Drive-canonical safety net: deliver every post that has a local build but no Drive link on
    its Sheet row yet (shelling out to drive_sync.py --post), then record the returned link. Posts
    live at outputs/<char-key>/<Title>/ — the Title column bridges the Sheet row to the folder (it
    equals the local folder basename AND the Drive folder). Sweeps all characters (or one via
    --character). --dry-run lists what it would deliver."""
    sh = _open()
    root = _root()
    ds = os.path.join(root, "engine", "drive", "drive_sync.py")
    chars = [_char_for(a.character)] if a.character else list(_characters().values())
    dry = getattr(a, "dry_run", False)
    delivered = already = 0
    for char in chars:
        ws = _char_ws(sh, char)
        headers = HEADERS[char["tab"]]
        char_out = os.path.join(root, "outputs", char["key"])   # per-character subdir
        grid = ws.get_all_values()
        for ridx, row in enumerate(grid[HEADER_ROWS:], start=HEADER_ROWS + 1):
            rec = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            pid = (rec.get("ID") or "").strip()
            title = (rec.get("Title") or "").strip()
            folder = (rec.get("Output Folder") or "").strip()
            local = os.path.join(char_out, title)
            if not pid or not title or not os.path.isdir(os.path.join(local, "final")):
                continue                                   # no id / no local build for this row
            if folder:
                already += 1; continue                     # already on Drive (has a link)
            if dry:
                print(f"[deliver-missing] WOULD deliver {pid}  {title}  ({char['name']})"); delivered += 1; continue
            print(f"[deliver-missing] {pid}  {title} -> Drive ({char['name']})")
            p = subprocess.run([sys.executable, ds, "--post", local, "--character", char["key"], "--platform", "Tiktok"],
                               capture_output=True, text=True)
            sys.stdout.write(p.stdout)
            if p.returncode != 0:
                print(f"  [warn] delivery failed for {pid}: {p.stderr.strip()}", file=sys.stderr); continue
            url = next((ln.split("-> ", 1)[-1].strip() for ln in p.stdout.splitlines()
                        if "drive.google.com/drive/folders/" in ln), "")
            if url:
                ws.batch_update([{"range": f"{_a1col(headers.index('Output Folder'))}{ridx}", "values": [[url]]}],
                                value_input_option="USER_ENTERED")
            delivered += 1
    print(f"[deliver-missing] done — {'would deliver' if dry else 'delivered'} {delivered}, {already} already on Drive")


# ── commands: brand ──────────────────────────────────────────────────────────
def cmd_brand_list(_):
    print(json.dumps(_read_rows(_open(), BRAND_TAB), ensure_ascii=False, indent=2))


def cmd_brand_add(a):
    sh = _open()
    ws = _ws(sh, BRAND_TAB) or _ensure_tab(sh, BRAND_TAB)
    bid = a.id or _next_id(ws, "B")
    row = {"ID": bid, "Brand Feature": a.feature or "", "Use Case": a.use_case or "",
           "Description": a.desc or "", "Media Asset Link": a.asset or "",
           "Funnel Fit": a.funnel_fit or "", "Notes": a.notes or ""}
    ws.append_row([row.get(h, "") for h in HEADERS[BRAND_TAB]], value_input_option="USER_ENTERED")
    print(f"[sheets] brand {bid} added")


# ── commands: connectors register ────────────────────────────────────────────
# EXACT seed set (upsert by Connector name; Status seeded, Notes left GREEN/empty for the human).
# Owner account for the Google surfaces: creators@holicay.com.
CONNECTOR_SEED = [
    ("Pexels", "photo search", "keys.env PEXELS", "Pexels API account",
     "pexels.com/api", "free", "legacy · optional"),
    ("Unsplash", "photo search", "keys.env UNSPLASH", "Unsplash developer account",
     "unsplash.com/developers", "free", "legacy · optional"),
    ("SerpAPI", "Google Images sourcing (brightdata.py gimg)", "keys.env SERP", "SerpAPI account",
     "serpapi.com", "paid per-search", "ACTIVE"),
    ("Google Places", "user photos + Maps Embed route shots", "keys.env PLACES",
     "creators@holicay.com (Google Cloud project of that key)", "console.cloud.google.com",
     "billed to the Google Cloud project of that key", "ACTIVE — primary UGC source"),
    ("scrape.do", "proxy fallback", "keys.env SCRAPE_TOKEN", "scrape.do account",
     "scrape.do", "free tier", "legacy · optional"),
    ("Bright Data", "greviews backend", "keys.env BRIGHTDATA", "Bright Data account",
     "brightdata.com", "pay-as-you-go", "PARTIAL — Google-reviews flaky, Instagram KYC-blocked"),
    ("Apify", "Instagram UGC (brightdata.py ig)", "keys.env APIFY", "Apify account",
     "console.apify.com", "FREE plan $5/mo credit", "ACTIVE — the working IG backend"),
    ("Google service account", "Sheets read/write + Drive reads", "holicay-*.json at repo root",
     "holicay-message-machine@holicay-402208.iam.gserviceaccount.com (GCP project holicay-402208)",
     "console.cloud.google.com", "free", "ACTIVE — share the new Sheet/Drive with this email"),
    ("Google OAuth Drive client", "Drive uploads/creation as creators@holicay.com",
     "client_secret*.json + per-user drive_token.json",
     "creators@holicay.com (GCP project masquerade-2 — a DIFFERENT project than the SA)",
     "console.cloud.google.com", "free", "ACTIVE"),
    ("ChatGPT", "character/cover image gen via logged-in browser (NO API key)",
     "~/.masquerade_chrome CDP profile", "that ChatGPT account", "chatgpt.com",
     "per that ChatGPT account's plan", "ACTIVE — re-login in the masquerade Chrome when gens fail"),
    ("TikTok", "stats scraping via logged-in browser session (same profile)",
     "~/.masquerade_chrome CDP profile", "@solo.with.ana / @chloe.belletravel", "tiktok.com",
     "free", "ACTIVE — views are login-gated; re-auth with engine/scrape/tiktok_login.js --open"),
    ("GitHub", "code home", "gh CLI", "Davenkoh", "github.com/Davenkoh/Project-Ana-2",
     "free", "ACTIVE"),
    ("iTunes Search API", "real app icons", "keyless", "—", "—", "free", "ACTIVE"),
]


def _seed_connectors(sh):
    ws = _ws(sh, CONN_TAB) or _ensure_tab(sh, CONN_TAB)
    headers = HEADERS[CONN_TAB]
    grid = ws.get_all_values()
    existing = {}
    for ridx, r in enumerate(grid[HEADER_ROWS:], start=HEADER_ROWS + 1):
        if r and r[0].strip():
            existing[r[0].strip()] = ridx
    added = updated = 0
    REF_COLS = ["Purpose", "Auth (env var / credential file)", "Account / identity",
                "Console URL", "Plan & cost"]      # refreshed on re-run; Status + Notes preserved
    for (name, purpose, auth, acct, url, plan, status) in CONNECTOR_SEED:
        vals = {"Connector": name, "Purpose": purpose, "Auth (env var / credential file)": auth,
                "Account / identity": acct, "Console URL": url, "Plan & cost": plan,
                "Status": status, "Notes": ""}
        if name in existing:
            row = existing[name]
            ups = [{"range": f"{_a1col(headers.index(h))}{row}", "values": [[vals[h]]]} for h in REF_COLS]
            ws.batch_update(ups, value_input_option="USER_ENTERED")
            updated += 1
        else:
            ws.append_row([vals.get(h, "") for h in headers],
                          value_input_option="USER_ENTERED", table_range="A2")
            added += 1
    print(f"[sheets] connectors seeded ({added} added, {updated} refreshed; Status/Notes preserved on re-run)")


def cmd_connectors_init(_):
    _seed_connectors(_open())


# ── commands: human feedback (every GREEN cell) ──────────────────────────────
# GREEN feedback channels: each fact tab's "Human Feedback" column, the Connectors "Notes"
# column, and the Holicay Brand "Notes" column. _feedback_col picks the right one per tab.
FEEDBACK_TABS = {**{c["key"]: c["tab"] for c in _characters().values()},
                 "brand": BRAND_TAB, "connectors": CONN_TAB}


def _feedback_col(tab):
    headers = HEADERS[tab]
    return "Human Feedback" if "Human Feedback" in headers else "Notes"


def cmd_feedback_poll(_):
    sh = _open()
    out = []
    for key, tab in FEEDBACK_TABS.items():
        headers = HEADERS[tab]
        col = _feedback_col(tab)
        if col not in headers:
            continue
        fi = headers.index(col)
        ws = _ws(sh, tab)
        if ws is None:
            continue
        for r in ws.get_all_values()[HEADER_ROWS:]:
            if len(r) > fi and r[fi].strip():
                out.append({"tab": key, "tab_name": tab, "column": col,
                            "id": r[0] if r else "", "feedback": r[fi].strip()})
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_feedback_clear(a):
    sh = _open()
    key = (a.tab or _default_char_key()).lower()
    if key not in FEEDBACK_TABS:
        sys.exit(f"[sheets] feedback-clear --tab must be one of {list(FEEDBACK_TABS)}")
    tab = FEEDBACK_TABS[key]
    headers = HEADERS[tab]
    col = _feedback_col(tab)
    ws = _ws(sh, tab) or _ensure_tab(sh, tab)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no {a.id} in {tab}")
    ups = [{"range": f"{_a1col(headers.index(col))}{row}", "values": [[""]]}]
    stamp = (f": {a.note}" if a.note else "")
    if "Metadata" in headers:        # fact tabs carry Metadata; stamp when feedback was processed
        prev = ws.cell(row, headers.index("Metadata") + 1).value or ""
        meta = (prev + "\n" if prev else "") + f"[{_now()}] feedback processed{stamp}"
        ups.append({"range": f"{_a1col(headers.index('Metadata'))}{row}", "values": [[meta]]})
    ws.batch_update(ups, value_input_option="USER_ENTERED")
    print(f"[sheets] feedback cleared for {a.id} in {tab} ({col})")


# ── commands: stats scraping ─────────────────────────────────────────────────
def _scrape_stats(url):
    script = os.path.join(_root(), "engine", "scrape", "tiktok_stats.js")
    if not os.path.exists(script):
        sys.exit(f"[sheets] scraper missing: {script}")
    res = subprocess.run(["node", script, url], capture_output=True, text=True, timeout=180)
    for line in reversed((res.stdout or "").strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
    sys.exit(f"[sheets] scrape failed for {url}\n{res.stderr.strip()[:500]}")


def _apply_stats(ws, headers, row, s):
    cmap = {"views": "Views", "likes": "Likes", "comments": "Comments",
            "share": "Share", "save": "Save", "posting_date": "Posting Date"}
    ups = []
    for k, col in cmap.items():
        if s.get(k) not in (None, "") and col in headers:
            ups.append({"range": f"{_a1col(headers.index(col))}{row}", "values": [[s[k]]]})
    if "Stats Last Updated" in headers:
        ups.append({"range": f"{_a1col(headers.index('Stats Last Updated'))}{row}", "values": [[_now()]]})
    if ups:
        ws.batch_update(ups, value_input_option="USER_ENTERED")
    return {k: s.get(k) for k in cmap}


def cmd_post_stats(a):
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    headers = HEADERS[char["tab"]]
    li = headers.index("Post Link")
    grid = ws.get_all_values()[HEADER_ROWS:]
    targets = []
    for i, r in enumerate(grid, start=HEADER_ROWS + 1):
        if a.all:
            if len(r) > li and r[li].strip():
                targets.append((i, r[0], r[li].strip()))
        elif r and r[0] == a.id:
            link = r[li].strip() if len(r) > li else ""
            if not link:
                sys.exit(f"[sheets] {a.id} has no Post Link to scrape")
            targets.append((i, r[0], link))
    if not a.all and not targets:
        sys.exit(f"[sheets] no {char['name']} row {a.id}")
    no_views = []
    for (row, pid, link) in targets:
        s = _scrape_stats(link)
        got = _apply_stats(ws, headers, row, s)
        flag = ""
        if s.get("loggedIn") is False or s.get("views") in (None, ""):
            flag = "  ⚠ no views (logged out?)"; no_views.append(pid)
        print(f"[sheets] {pid}: {got}{flag}")
    if no_views:
        print(f"[sheets] WARNING: {len(no_views)} post(s) returned no views — TikTok photo posts need a "
              f"logged-in session: {', '.join(no_views)}", file=sys.stderr)
        print("[sheets]   re-auth the masquerade Chrome:  node engine/scrape/tiktok_login.js --open", file=sys.stderr)


# ── commands: dashboard (live formulas over the fact tabs) ────────────────────
def _stack_range(tabs, letter):
    """A vertically-stacked array literal of one column across all fact tabs, e.g.
    {'Ana'!C3:C1000;'Chloe'!C3:C1000;'Hannah'!C3:C1000} — safe inside SUMPRODUCT."""
    return "{" + ";".join(f"'{t}'!{letter}3:{letter}1000" for t in tabs) + "}"


def _stack_all(tabs):
    """The full A3:T stack across all fact tabs — for QUERY (Col1..Col20)."""
    return "{" + ";".join(f"'{t}'!A3:T1000" for t in tabs) + "}"


def _build_dashboard(sh):
    """(Re)build the Dashboard tab as LIVE formulas (USER_ENTERED). No data of its own; every
    number recomputes from the fact tabs. Tab names are read from state.json, so re-running after a
    character is added extends it. Columns on a fact tab: A=ID B=Country C=Framework D=Variant
    E=Copy Iteration F=Title G=Output Folder H=Caption I=Date Created J=Notes K=Post Link
    L=Posting Date M=Views N=Likes O=Comments P=Share Q=Save R=Stats Last Updated S=Human
    Feedback T=Metadata."""
    tabs = _fact_tabs()
    ws = _ws(sh, DASH_TAB)
    if ws is None:
        ws = sh.add_worksheet(title=DASH_TAB, rows=200, cols=8)
    ws.clear()
    gid = ws.id
    NCOL = 6
    C_ = _stack_range(tabs, "C"); D_ = _stack_range(tabs, "D"); B_ = _stack_range(tabs, "B")
    M_ = _stack_range(tabs, "M"); O_ = _stack_range(tabs, "O"); Q_ = _stack_range(tabs, "Q")
    STACK = _stack_all(tabs)

    def cnt(cond):   return f'=SUMPRODUCT(({cond})*({M_}>0))'
    def avgv(cond):  return f'=IFERROR(SUMPRODUCT(({cond})*({M_}>0)*{M_})/SUMPRODUCT(({cond})*({M_}>0)),"")'
    def srate(cond): return f'=IFERROR(SUMPRODUCT(({cond})*({M_}>0)*{Q_})/SUMPRODUCT(({cond})*({M_}>0)*{M_}),"")'
    def crate(cond): return f'=IFERROR(SUMPRODUCT(({cond})*({M_}>0)*{O_})/SUMPRODUCT(({cond})*({M_}>0)*{M_}),"")'

    rows = []          # each row = list of up to NCOL cell strings
    titles, headers_idx, rate_cells = [], [], []   # 0-based row indices / (row,col) for formatting

    def pad(r):
        return (r + [""] * NCOL)[:NCOL]

    def add(r):
        rows.append(pad(r))

    def title(text):
        titles.append(len(rows)); add([text])

    def header(cells):
        headers_idx.append(len(rows)); add(cells)

    def metric_row(label, cond, extra=None):
        # label [| extra] | count | avg views | save-rate | comment-rate
        base = [label] if extra is None else [label, extra]
        rate_c = len(base) + 2                       # save-rate column index (0-based)
        r = base + [cnt(cond), avgv(cond), srate(cond), crate(cond)]
        rate_cells.append((len(rows), rate_c)); rate_cells.append((len(rows), rate_c + 1))
        add(r)

    add([f"PROJECT ANA 2.0 — DASHBOARD   (live; rebuilt by dashboard-init on {_today()})"])
    add(["Every number recomputes from the character fact tabs. Performance rows count only posts with Views > 0."])
    add([])

    # ── Block 1: per-character pipeline ───────────────────────────────────────
    title("PIPELINE  ·  per character")
    header(["Character", "Total 2.0 posts", "Posted", "Last built", "Next framework"])
    for t in tabs:
        q = f"'{t}'"
        total = f'=COUNTIF({q}!C3:C1000,"<>")'
        posted = f'=COUNTIF({q}!K3:K1000,"<>")'
        last = f'=IF(COUNT({q}!I3:I1000)=0,"",TEXT(MAX({q}!I3:I1000),"yyyy-mm-dd"))'
        nextfw = f'=INDEX({{"A";"B";"C1";"C2"}},MOD(COUNTIF({q}!C3:C1000,"<>"),4)+1)'
        add([t, total, posted, last, nextfw])
    add([])

    # ── Block 2: performance ──────────────────────────────────────────────────
    title("PERFORMANCE  ·  by framework")
    header(["Framework", "Posts (views>0)", "Avg views", "Save-rate", "Comment-rate"])
    for fw in FRAMEWORKS:
        metric_row(fw, f'{C_}="{fw}"')
    add([])

    title("PERFORMANCE  ·  by variant")
    header(["Variant", "Posts (views>0)", "Avg views", "Save-rate", "Comment-rate"])
    for v in VARIANTS:
        metric_row(v, f'{D_}="{v}"')
    add([])

    title("PERFORMANCE  ·  framework × variant")
    header(["Framework", "Variant", "Posts (views>0)", "Avg views", "Save-rate", "Comment-rate"])
    for fw in FRAMEWORKS:
        for v in VARIANTS:
            metric_row(fw, f'({C_}="{fw}")*({D_}="{v}")', extra=v)
    add([])

    # by country — enumerate the roster's distinct content countries (robust default)
    countries = []
    for c in _characters().values():
        if c["country"] and c["country"] not in countries:
            countries.append(c["country"])
    title("PERFORMANCE  ·  by country")
    header(["Country", "Posts (views>0)", "Avg views", "Save-rate", "Comment-rate"])
    for ct in countries:
        metric_row(ct, f'{B_}="{ct}"')
    add([])

    # by character — per-tab (not stacked)
    title("PERFORMANCE  ·  by character")
    header(["Character", "Posts (views>0)", "Avg views", "Save-rate", "Comment-rate"])
    for t in tabs:
        q = f"'{t}'"
        c_cnt = f'=SUMPRODUCT(({q}!M3:M1000>0)*1)'
        c_avg = f'=IFERROR(SUMPRODUCT(({q}!M3:M1000>0)*{q}!M3:M1000)/SUMPRODUCT(({q}!M3:M1000>0)*1),"")'
        c_sr  = f'=IFERROR(SUMPRODUCT(({q}!M3:M1000>0)*{q}!Q3:Q1000)/SUMPRODUCT(({q}!M3:M1000>0)*{q}!M3:M1000),"")'
        c_cr  = f'=IFERROR(SUMPRODUCT(({q}!M3:M1000>0)*{q}!O3:O1000)/SUMPRODUCT(({q}!M3:M1000>0)*{q}!M3:M1000),"")'
        rate_cells.append((len(rows), 3)); rate_cells.append((len(rows), 4))
        add([t, c_cnt, c_avg, c_sr, c_cr])
    add([])

    # ── Block 3: top-10 posts by save-rate ────────────────────────────────────
    title("TOP 10 POSTS  ·  by save-rate (across all characters, views>0)")
    header(["Title", "Framework", "Variant", "Views", "Save-rate"])
    top = (f'=IFERROR(SORTN({{'
           f'QUERY({STACK},"select Col6,Col3,Col4,Col13 where Col13>0",0),'
           f'ARRAYFORMULA(IFERROR('
           f'QUERY({STACK},"select Col17 where Col13>0",0)/'
           f'QUERY({STACK},"select Col13 where Col13>0",0),0))'
           f'}},10,0,5,FALSE),"")')
    r0 = len(rows)
    add([top])
    for k in range(10):                              # the spill fills 5 cols; format save-rate col
        rate_cells.append((r0 + k, 4))

    # write everything at once (USER_ENTERED so formulas evaluate)
    end = _a1col(NCOL - 1)
    ws.batch_update([{"range": f"A1:{end}{len(rows)}", "values": rows}],
                    value_input_option="USER_ENTERED")

    # formatting
    reqs = []

    def band(r, bg, white, bold, merge):
        out = []
        if merge:
            out.append({"mergeCells": {"range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
                "startColumnIndex": 0, "endColumnIndex": NCOL}, "mergeType": "MERGE_ALL"}})
        tf = {"bold": bold}
        if white:
            tf["foregroundColor"] = WHITE
        out.append({"repeatCell": {"range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
            "startColumnIndex": 0, "endColumnIndex": NCOL},
            "cell": {"userEnteredFormat": {"backgroundColor": bg, "wrapStrategy": "WRAP", "textFormat": tf}},
            "fields": "userEnteredFormat(backgroundColor,wrapStrategy,textFormat)"}})
        return out

    reqs += band(0, NAVY, True, True, True)          # page title
    for r in titles:
        reqs += band(r, CORAL, True, True, True)     # section titles (coral banners)
    for r in headers_idx:
        reqs += band(r, T_NAVY, False, True, False)  # column headers
    for (r, c) in rate_cells:                        # rate cells -> percentage
        reqs.append({"repeatCell": {"range": {"sheetId": gid, "startRowIndex": r, "endRowIndex": r + 1,
            "startColumnIndex": c, "endColumnIndex": c + 1},
            "cell": {"userEnteredFormat": {"numberFormat": {"type": "PERCENT", "pattern": "0.00%"}}},
            "fields": "userEnteredFormat.numberFormat"}})
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": gid,
        "gridProperties": {"frozenRowCount": 1}}, "fields": "gridProperties.frozenRowCount"}})
    for i, w in enumerate((230, 150, 120, 110, 110, 110)):
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": gid, "dimension": "COLUMNS", "startIndex": i, "endIndex": i + 1},
            "properties": {"pixelSize": w}, "fields": "pixelSize"}})
    try:
        sh.batch_update({"requests": reqs})
    except Exception as e:
        print(f"[sheets] dashboard formatting partial: {e}", file=sys.stderr)
    print(f"[sheets] Dashboard rebuilt ({len(tabs)} character tab(s), {len(titles)} sections)")


def cmd_dashboard_init(_):
    _build_dashboard(_open())


# ── commands: stats-summary (client-side rollups for the analyze skill) ──────
def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None


def _summarize(rows):
    """Group fact rows (dicts) by framework / variant / framework×variant / country / character and
    compute count, sum/avg views, avg save-rate, avg comment-rate (per-row rates), plus aggregate
    save-/comment-rate (sum/sum). Only rows with Views > 0 are counted."""
    def blank():
        return {"count": 0, "sum_views": 0.0, "_srates": [], "_crates": [],
                "_sum_save": 0.0, "_sum_comments": 0.0}
    groups = {"by_framework": {}, "by_variant": {}, "by_framework_variant": {},
              "by_country": {}, "by_character": {}}

    def bump(bucket, key, views, save, comments):
        d = bucket.setdefault(key, blank())
        d["count"] += 1
        d["sum_views"] += views
        d["_sum_save"] += save
        d["_sum_comments"] += comments
        d["_srates"].append(save / views)
        d["_crates"].append(comments / views)

    for r in rows:
        views = _num(r.get("Views"))
        if not views or views <= 0:
            continue
        save = _num(r.get("Save")) or 0.0
        comments = _num(r.get("Comments")) or 0.0
        fw = (r.get("Framework") or "").strip()
        var = (r.get("Variant") or "").strip()
        country = (r.get("Country") or "").strip()
        char = (r.get("_character") or "").strip()
        if fw:
            bump(groups["by_framework"], fw, views, save, comments)
        if var:
            bump(groups["by_variant"], var, views, save, comments)
        if fw and var:
            bump(groups["by_framework_variant"], f"{fw} / {var}", views, save, comments)
        if country:
            bump(groups["by_country"], country, views, save, comments)
        if char:
            bump(groups["by_character"], char, views, save, comments)

    def finish(d):
        n = d["count"]
        return {
            "count": n,
            "sum_views": round(d["sum_views"], 2),
            "avg_views": round(d["sum_views"] / n, 2) if n else None,
            "avg_save_rate": round(sum(d["_srates"]) / n, 6) if n else None,
            "avg_comment_rate": round(sum(d["_crates"]) / n, 6) if n else None,
            "agg_save_rate": round(d["_sum_save"] / d["sum_views"], 6) if d["sum_views"] else None,
            "agg_comment_rate": round(d["_sum_comments"] / d["sum_views"], 6) if d["sum_views"] else None,
        }
    return {dim: {k: finish(v) for k, v in sorted(bucket.items())}
            for dim, bucket in groups.items()}


def cmd_stats_summary(a):
    sh = _open()
    rows = []
    for c in _characters().values():
        for r in _read_rows(sh, c["tab"]):
            r = dict(r); r["_character"] = c["name"]
            rows.append(r)
    summary = _summarize(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=(None if getattr(a, "json", False) else 2)))


# ── commands: read / dictionary ──────────────────────────────────────────────
def cmd_read(a):
    sh = _open()
    if a.tab in SPEC:
        print(json.dumps(_read_rows(sh, a.tab), ensure_ascii=False, indent=2)); return
    ws = _ws(sh, a.tab)
    if ws is None:
        sys.exit(f"[sheets] no tab named {a.tab!r}")
    try:
        print(json.dumps(ws.get_all_records(), ensure_ascii=False, indent=2))
    except Exception:
        print(json.dumps(ws.get_all_values(), ensure_ascii=False, indent=2))


def cmd_dictionary(_):
    _build_dictionary(_open())


def main():
    p = argparse.ArgumentParser(description="Project Ana 2.0 Google Sheet (spec-driven front-end)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("migrate-schema").set_defaults(fn=cmd_migrate_schema)
    sub.add_parser("dictionary").set_defaults(fn=cmd_dictionary)
    sub.add_parser("dashboard-init").set_defaults(fn=cmd_dashboard_init)
    sub.add_parser("connectors-init").set_defaults(fn=cmd_connectors_init)

    u = sub.add_parser("post-upsert"); u.set_defaults(fn=cmd_post_upsert)
    u.add_argument("--character"); u.add_argument("--id", required=True)
    for f in ("title", "folder", "caption", "country", "framework", "variant",
              "iteration", "notes", "metadata"):
        u.add_argument(f"--{f}")

    s = sub.add_parser("post-set"); s.set_defaults(fn=cmd_post_set)
    s.add_argument("--character"); s.add_argument("--id", required=True)
    for f in ("title", "folder", "caption", "country", "framework", "variant", "iteration",
              "notes", "metadata", "post-link", "posting-date", "views", "likes",
              "comments", "share", "save"):
        s.add_argument(f"--{f}")

    asx = sub.add_parser("post-stats"); asx.set_defaults(fn=cmd_post_stats)
    asx.add_argument("--character"); asx.add_argument("--id"); asx.add_argument("--all", action="store_true")

    ns = sub.add_parser("next-slot"); ns.set_defaults(fn=cmd_next_slot)
    ns.add_argument("--character"); ns.add_argument("--country")
    ns.add_argument("--reserve", action="store_true",
                    help="atomically claim the slot by appending a stub row (visible to the team)")

    nn = sub.add_parser("next-number"); nn.set_defaults(fn=cmd_next_number)
    nn.add_argument("--character"); nn.add_argument("--title")
    nn.add_argument("--reserve", action="store_true",
                    help="claim the id now by appending a stub row (no framework — use next-slot for a rotation slot)")

    dm = sub.add_parser("deliver-missing"); dm.set_defaults(fn=cmd_deliver_missing)
    dm.add_argument("--character"); dm.add_argument("--dry-run", action="store_true")

    pdel = sub.add_parser("post-delete"); pdel.set_defaults(fn=cmd_post_delete)
    pdel.add_argument("--character"); pdel.add_argument("--id", required=True)

    ss = sub.add_parser("stats-summary"); ss.set_defaults(fn=cmd_stats_summary)
    ss.add_argument("--json", action="store_true", help="compact single-line JSON")

    sub.add_parser("brand-list").set_defaults(fn=cmd_brand_list)
    ba = sub.add_parser("brand-add"); ba.set_defaults(fn=cmd_brand_add)
    for f in ("id", "feature", "use-case", "desc", "asset", "funnel-fit", "notes"):
        ba.add_argument(f"--{f}")

    sub.add_parser("feedback-poll").set_defaults(fn=cmd_feedback_poll)
    fc = sub.add_parser("feedback-clear"); fc.set_defaults(fn=cmd_feedback_clear)
    fc.add_argument("--tab", required=True, help="ana | chloe | hannah | brand | connectors")
    fc.add_argument("--id", required=True); fc.add_argument("--note")

    r = sub.add_parser("read"); r.set_defaults(fn=cmd_read); r.add_argument("--tab", required=True)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
