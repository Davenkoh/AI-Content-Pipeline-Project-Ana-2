#!/usr/bin/env python3
"""
sheets.py — Project Ana's Google Sheet, the human-facing FRONT-END.

One spreadsheet, spec-driven. SPEC (below) is the SINGLE SOURCE OF TRUTH for every
tab and column: it generates the banded headers, the colours, the cell-notes, the
dropdowns, the hyperlinked back-links, AND the self-documenting Dictionary tab. Change
a column in SPEC and everything else follows.

Reading conventions baked into the sheet
  • Each tab is split into visually-banded SECTIONS so the "meat" is obvious vs the
    stats / metadata: meat=coral, stats/metadata=navy, AI-metadata=grey, and
    HUMAN INPUT = GREEN. Anything GREEN (a column or the whole Holicay Brand tab) is
    yours to fill; the AI only reads + clears it when you ask.
  • Star schema: each character (Ana, Chloe, …) has its OWN fact table (one row per post;
    carries Hook ID / CTA ID / Funnel ID / Inspo ID foreign keys + the post's own stats).
    Hooks / CTA / Funnels + Inspo are SHARED across characters (niche-agnostic technique
    atoms). They link to each other with clickable HYPERLINK back-links
    (run `relink`). There is no auto "status": reuse is judged from each technique's
    Posts Used (and the metrics on those posts).

Tabs
  Ana, Chloe, …          one row per post, per character (the per-character fact tables).
  TikTok Inspo Analysis  one row per scraped inspiration (+ that post's own stats).
  TikTok Hooks           agnostic hook library (the open).
  TikTok CTA             agnostic CTA library (the ask) — funnel-tagged + placement.
  TikTok Funnels         the strategy spine (F1-F6, seeded).
  Holicay Brand          GREEN — you own this; the AI reads it.
  Dictionary             auto-generated reference for every tab + column.

Common commands
  python3 sheets.py init                       # build/format every tab + seed funnels + dictionary
  python3 sheets.py migrate-schema             # realign existing rows to the new spec (run BEFORE init)
  python3 sheets.py relink                      # (re)build the clickable back-links
  python3 sheets.py post-upsert --character ana --id tt-16 --title "..." --hook "..." --hook-id H003 \
        --cta "..." --cta-id C002 --funnel F3 --inspo I001 --script "..." --folder "<link>"
  python3 sheets.py post-stats --character ana --id tt-16   # scrape the live post's metrics (needs Post Link)
  python3 sheets.py post-stats --character ana --all
  python3 sheets.py hook-add --pattern "..." --type "..." --example "..." --creator AI --origin I001
  python3 sheets.py cta-add  --pattern "..." --funnel F3 --placement close --mechanism "..." --origin I001
  python3 sheets.py funnel-list / funnel-add / funnel-append-lesson
  python3 sheets.py inspo-add --url "<url>" --hook "..." --funnel F3 ...
  python3 sheets.py inspo-stats --id I001      # scrape the inspiration's own metrics
  python3 sheets.py read --tab "TikTok Hooks"  # -> JSON rows
  python3 sheets.py brand-list / brand-add
  python3 sheets.py feedback-poll              # every GREEN Human Feedback cell with content
  python3 sheets.py feedback-clear --tab hook --id H003 --note "applied: using less"
"""
import argparse, glob, json, os, subprocess, sys, datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# ── tab names (shared, character-agnostic) ────────────────────────────────────
INSPO_TAB  = "TikTok Inspo Analysis"
HOOKS_TAB  = "TikTok Hooks"
CTA_TAB    = "TikTok CTA"
FUNNEL_TAB = "TikTok Funnels"
BRAND_TAB  = "Holicay Brand"
DICT_TAB   = "Dictionary"

# Repo doc the Dictionary tab points newcomers to (the full system blueprint, on GitHub).
BLUEPRINT_URL = "https://github.com/Davenkoh/Project-Ana/blob/main/BLUEPRINT.md"


# ── character registry ────────────────────────────────────────────────────────
# state.json is the single source of truth for the roster. Each character has its OWN
# fact-table tab (named after it) + post-id prefix; the technique libraries + inspo are
# SHARED. Convention: tab name == character name, EXCEPT a faceless character's tab is
# suffixed " (Faceless)" so she's identifiable at a glance on the Sheet; only id_prefix /
# country / faceless need storing.
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
    """key -> {key, name, tab, faceless, id_prefix, country}. Falls back to a lone 'ana' if unset."""
    raw = _state().get("characters") or {"ana": {"name": "Ana", "id_prefix": "tt"}}
    out = {}
    for key, c in raw.items():
        c = c or {}
        name = c.get("name") or key.capitalize()
        faceless = bool(c.get("faceless"))
        # a faceless character has no persona; suffix her tab so she's identifiable on the front end
        tab = f"{name} (Faceless)" if faceless else name
        out[key] = {"key": key, "name": name, "tab": tab, "faceless": faceless,
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
CORAL  = {"red": 0.949, "green": 0.318, "blue": 0.259}   # meat
NAVY   = {"red": 0.075, "green": 0.227, "blue": 0.290}   # stats / metadata
GRAY   = {"red": 0.45,  "green": 0.45,  "blue": 0.45}     # ai metadata
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

# ── dropdown options ──────────────────────────────────────────────────────────
CREATOR_OPTS   = ["AI", "AI + Human Feedback", "Human"]
PLACEMENT_OPTS = ["cover", "body", "close", "caption"]
DROPDOWNS = {("TikTok Hooks", "Creator"): CREATOR_OPTS,
             ("TikTok CTA", "Creator"): CREATOR_OPTS,
             ("TikTok Funnels", "Creator"): CREATOR_OPTS,
             ("TikTok CTA", "Placement"): PLACEMENT_OPTS}


# ── SPEC: the single source of truth ─────────────────────────────────────────
# C(name, section, who, desc, example, link)
#   section: meat | stats | meta | human | ai
#   who    : "AI" | "Human" | "AI + Human"   (shown in the Dictionary)
#   link   : None | hooks | cta | funnels | inspo | auto | post_multi | funnels_multi
def C(name, section, who, desc, example, link=None):
    return {"name": name, "section": section, "who": who,
            "desc": desc, "example": example, "link": link}

def _fact_spec():
    """The per-character fact table (one row per post). Same schema for every character."""
    return {
        "sections": {"meat": "POST CREATION (the post)", "stats": "STATS (this post's performance)",
                     "human": "HUMAN INPUT", "ai": "AI METADATA"},
        "columns": [
            C("ID", "meat", "AI", "Unique post id. Presence here = a planned/built post.", "tt-16"),
            C("Platform", "meat", "AI", "Which channel the post is for.", "tiktok"),
            C("Title", "meat", "AI", "Post title / the output folder name.", "16 - Things to Do in Vietnam"),
            C("Output Folder", "meat", "AI", "Drive link to the built carousel.", "https://drive.google.com/drive/folders/..."),
            C("Caption", "meat", "AI", "The caption posted with the carousel.", "saving you the research for vietnam ..."),
            C("Hook", "meat", "AI", "The concrete opener used in THIS post.", "top things to do in vietnam (even if it's not your first time)"),
            C("Hook ID", "meat", "AI", "Which Hook-library pattern this used. Click to open it.", "H003", "hooks"),
            C("CTA", "meat", "AI", "The concrete ask used in THIS post.", "comment 'vietnam' and i'll dm the itinerary"),
            C("CTA ID", "meat", "AI", "Which CTA-library pattern this used. Click to open it.", "C002", "cta"),
            C("Funnel ID", "meat", "AI", "Which funnel strategy this post ran. Click to open it.", "F3", "funnels"),
            C("Script", "meat", "AI", "The body copy / slide-by-slide text.", "slide1: ... slide2: ..."),
            C("Inspo ID", "meat", "AI", "The inspiration this post was derived from. Click to open it.", "I001", "inspo"),
            C("Date Created", "meat", "AI", "When the post was built.", "2026-06-19"),
            C("Notes", "meat", "AI", "Plain-English context the HUMAN should read about this post.", "first end-to-end test run"),
            C("Post Link", "stats", "AI + Human", "The live TikTok URL once posted. Drop it here; presence = 'posted'. Feeds the stats scraper.", "https://www.tiktok.com/@user/photo/123"),
            C("Posting Date", "stats", "AI", "When it went live (scraped).", "2026-06-20"),
            C("Views", "stats", "AI", "Views (scraped).", "12000"),
            C("Likes", "stats", "AI", "Likes (scraped).", "800"),
            C("Comments", "stats", "AI", "Comments (scraped).", "40"),
            C("Share", "stats", "AI", "Shares (scraped).", "25"),
            C("Save", "stats", "AI", "Saves / bookmarks (scraped).", "300"),
            C("Stats Last Updated", "stats", "AI", "When the stats above were last refreshed.", "2026-06-22 18:00"),
            C("Human Feedback", "human", "Human", "YOUR steer on this post. The AI reads it when you ask, acts, and clears it.", "hook felt weak, try a confession opener"),
            C("Metadata", "ai", "AI", "AI-only bookkeeping (e.g. when feedback was processed).", "feedback processed 2026-06-20"),
        ],
    }


SHARED_SPEC = {
    INSPO_TAB: {
        "sections": {"meat": "ANALYSIS (what we learned)", "stats": "INSPIRATION STATS (how the original did)",
                     "human": "HUMAN INPUT"},
        "columns": [
            C("Inspo ID", "meat", "AI", "Unique id for this analyzed inspiration.", "I001"),
            C("URL", "meat", "AI", "The original TikTok post.", "https://www.tiktok.com/@user/photo/123"),
            C("Date Analyzed", "meat", "AI", "When we analyzed it (not when it was posted).", "2026-06-18"),
            C("Slides", "meat", "AI", "Drive link to the saved slides (inspo-sync fills it; the local inspo/NN folder is disposable scratch).", "https://drive.google.com/drive/folders/..."),
            C("Format", "meat", "AI", "The post's structure.", "listicle / storytime / notes-app"),
            C("Storytelling / Copy", "meat", "AI", "How the body copy / story works.", "personal anecdote then a payoff list"),
            C("Design notes (+image refs)", "meat", "AI", "Font / casing / placement + links to slide refs.", "Montserrat white centered; inspo/01/2.jpg"),
            C("Hook", "meat", "AI", "The opener observed in the post.", "everyone gets the iced coffee and stops there"),
            C("Hook ID", "meat", "AI", "Maps to a Hook-library row. Click to open it.", "H003", "hooks"),
            C("CTA / Funnel", "meat", "AI", "The ask + mechanism observed (free text).", "comment for the guide"),
            C("CTA ID", "meat", "AI", "Maps to a CTA-library row. Click to open it.", "C002", "cta"),
            C("Funnel ID", "meat", "AI", "Which funnel the inspiration ran. Click to open it.", "F3", "funnels"),
            C("Hypothesis on Why it Worked", "meat", "AI", "The AI's analysis of WHY this post performed.", "curiosity gap + a genuinely save-worthy list"),
            C("Possible Holicay Content", "meat", "AI", "AI synthesis: how to turn this (format+hook+story+design+cta+funnel, wrapped around the why) into a Holicay post.", "F3 DM-magnet listicle of hidden cafes, withhold the map"),
            C("Posting Date", "stats", "AI", "When the inspiration was originally posted (scraped).", "2026-05-30"),
            C("Views", "stats", "AI", "The inspiration's views (scraped).", "250000"),
            C("Likes", "stats", "AI", "The inspiration's likes (scraped).", "18000"),
            C("Comments", "stats", "AI", "The inspiration's comments (scraped).", "600"),
            C("Share", "stats", "AI", "The inspiration's shares (scraped).", "1200"),
            C("Save", "stats", "AI", "The inspiration's saves (scraped).", "9000"),
            C("Stats Last Updated", "stats", "AI", "When the stats above were last refreshed.", "2026-06-22"),
            C("Human Feedback", "human", "Human", "YOUR notes on this inspiration. The AI reads it when you ask, acts, and clears it.", "great F5 example, replicate the reveal"),
        ],
    },
    HOOKS_TAB: {
        "sections": {"meat": "THE HOOK", "meta": "TRACKING / METADATA", "human": "HUMAN INPUT"},
        "columns": [
            C("Hook ID", "meat", "AI", "Unique id.", "H001"),
            C("Hook Pattern (general)", "meat", "AI", "The agnostic mechanism, topic-free (dress onto any subject).", "top [N] things to do in [place]"),
            C("Type", "meat", "AI", "Category of hook.", "listicle / curiosity gap / confession"),
            C("Funnel Affinity", "meat", "AI", "Funnels this hook tends to open well (soft, comma-separated). Click to open.", "F1, F5", "funnels_multi"),
            C("Example", "meat", "AI", "A concrete instance of the pattern.", "top 7 cafes in Hoi An"),
            C("Creator", "meta", "AI", "Where this technique came from.", "AI"),
            C("Origin Ref", "meta", "AI", "Back-link to the inspo / post / feedback that birthed it. Click to open.", "I001", "auto"),
            C("Lessons", "meta", "AI", "Dated learnings accumulated as the hook gets reused.", "- [2026-06-20] lands harder with a specific number"),
            C("Posts Used", "meta", "AI", "Posts that used this hook (comma-separated). Click any to open it. Higher count = leaned on more.", "tt-01, tt-09", "post_multi"),
            C("Last Updated", "meta", "AI", "When this row last changed.", "2026-06-20"),
            C("Human Feedback", "human", "Human", "YOUR steer (e.g. 'tired, use less' / 'great, push it'). The AI reads, acts, clears.", "feels overused, vary it"),
        ],
    },
    CTA_TAB: {
        "sections": {"meat": "THE CTA", "meta": "TRACKING / METADATA", "human": "HUMAN INPUT"},
        "columns": [
            C("CTA ID", "meat", "AI", "Unique id.", "C001"),
            C("Pattern (general)", "meat", "AI", "The agnostic ask phrasing, topic-free.", "comment [keyword] for the [resource]"),
            C("Funnel ID", "meat", "AI", "The ONE funnel this CTA executes. Click to open.", "F3", "funnels"),
            C("Placement", "meat", "AI", "Where the ask sits in the post (a subtle in-body mention is still a CTA).", "close"),
            C("Mechanism", "meat", "AI", "How the ask actually works.", "comment keyword -> auto-DM the plan"),
            C("Example", "meat", "AI", "A concrete instance.", "comment 'vietnam' and i'll dm the itinerary"),
            C("Creator", "meta", "AI", "Where this technique came from.", "AI"),
            C("Origin Ref", "meta", "AI", "Back-link to the inspo / post / feedback that birthed it. Click to open.", "I001", "auto"),
            C("Lessons", "meta", "AI", "Dated learnings accumulated as the CTA gets reused.", "- [2026-06-20] keyword in the cover doubles comments"),
            C("Posts Used", "meta", "AI", "Posts that used this CTA (comma-separated). Click any to open it.", "tt-16", "post_multi"),
            C("Last Updated", "meta", "AI", "When this row last changed.", "2026-06-20"),
            C("Human Feedback", "human", "Human", "YOUR steer on this CTA. The AI reads, acts, clears.", "stop using the hard close, too salesy"),
        ],
    },
    FUNNEL_TAB: {
        "sections": {"meat": "THE FUNNEL (strategy)", "meta": "TRACKING / METADATA", "human": "HUMAN INPUT"},
        "columns": [
            C("Funnel ID", "meat", "AI + Human", "The funnel id (F1-F6 + any candidates).", "F3"),
            C("Name", "meat", "AI + Human", "Short name.", "DM Magnet"),
            C("Trigger / When to use", "meat", "AI + Human", "The condition that selects this funnel.", "high-value guide that can withhold the full plan"),
            C("Canonical Ask", "meat", "AI + Human", "The funnel's signature action.", "comment a keyword -> auto-DM"),
            C("Primary KPI", "meat", "AI + Human", "The metric to judge it on (never grade it on another).", "comments / DMs (leads)"),
            C("Creator", "meta", "AI", "Where this funnel came from.", "Human"),
            C("Origin Ref", "meta", "AI", "Back-link to its source. Click to open.", "funnel_skill.md"),
            C("Lessons", "meta", "AI", "Dated learnings accumulated as the funnel gets used.", "- [2026-06-20] keyword posts out-save plain lists"),
            C("Posts Used", "meta", "AI", "Posts that ran this funnel (comma-separated). Click any to open it. Higher count = leaned on more.", "tt-16", "post_multi"),
            C("Last Updated", "meta", "AI", "When this row last changed.", "2026-06-20"),
            C("Human Feedback", "human", "Human", "YOUR steer on this funnel. The AI reads, acts, clears.", "run F3 more this month"),
        ],
    },
    BRAND_TAB: {
        # whole tab is human-owned -> every section is "human" (all green)
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
    },
}

# Build SPEC: one fact tab per character (roster order), then the shared library/inspo/brand tabs.
SPEC = {c["tab"]: _fact_spec() for c in _characters().values()}
SPEC.update(SHARED_SPEC)

# derived: HEADERS[tab] = ordered column names; HEADER_ROWS = 2 for all SPEC tabs
HEADERS = {tab: [c["name"] for c in s["columns"]] for tab, s in SPEC.items()}
HEADER_ROWS = 2

# link target tab per (single-value) link-key
LINK_TAB = {"hooks": HOOKS_TAB, "cta": CTA_TAB, "funnels": FUNNEL_TAB, "inspo": INSPO_TAB}

# Seed funnels (F1-F6) lifted from knowledge/funnels/funnel_skill.md §3.
FUNNEL_SEED = [
    ("F1", "Trust Builder", "default; pure value; no honest app fit; growing the account",
     "Follow (+ save) = audience capture", "follows, saves, reach"),
    ("F2", "Honest Mention", "a value post naturally lists tools or raises a planning pain",
     "Brand recall (assist, not a click) - app named flat among real tools", "profile taps (assist)"),
    ("F3", "DM Magnet", "high-value guide OR strong story that can withhold the full plan",
     "Comment a keyword -> auto-DM a real itinerary", "comments / DMs (leads)"),
    ("F4", "Soft Demo", "audience = overwhelmed planners; teachable 'how I do it'",
     "Save + use the app her way (app shown in use)", "saves, app opens"),
    ("F5", "Decoy Reveal", "high-intent searchers; can disguise the post as the listicle",
     "Make their own / save (app revealed at the back)", "app opens, saves"),
    ("F6", "Before/After", "a relatable before->after transformation; app = the turning point",
     "Want the after -> use app / save", "saves, shares, app opens"),
]


# ── plumbing ─────────────────────────────────────────────────────────────────
def _sheet_id():
    env = os.environ.get("MASQUERADE_SHEET_ID")
    if env:
        return env
    sp = os.path.join(_root(), "state.json")
    if os.path.exists(sp):
        sid = (json.load(open(sp)) or {}).get("sheet_id")
        if sid:
            return sid
    sys.exit("[sheets] no sheet id — set sheet_id in state.json or $MASQUERADE_SHEET_ID")


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
    sys.exit("[sheets] no service-account JSON found at repo root (set $HOLICAY_SA_JSON)")


def _client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError as e:
        sys.exit(f"[sheets] missing dependency: {e}. Run: python3 -m pip install gspread")
    creds = Credentials.from_service_account_file(_find_creds(), scopes=SCOPES)
    return gspread.authorize(creds)


def _open():
    return _client().open_by_key(_sheet_id())


def _today():
    return datetime.date.today().isoformat()


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


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
    """Largest prefix+NNN in column A, +1. Skips banner/header (non prefix+digits)."""
    n = 0
    for v in ws.col_values(1):
        if v.startswith(prefix) and v[len(prefix):].isdigit():
            n = max(n, int(v[len(prefix):]))
    return f"{prefix}{n + 1:03d}"


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
    # a faceless character's tab gets a distinct slate colour — instant visual ID on the front end
    if tab.endswith("(Faceless)"):
        reqs.append({"updateSheetProperties": {"properties": {"sheetId": gid,
            "tabColor": {"red": 0.26, "green": 0.26, "blue": 0.28}}, "fields": "tabColor"}})
    try:
        sh.batch_update({"requests": reqs})
    except Exception as e:
        print(f"[sheets] {tab}: formatting partial: {e}", file=sys.stderr)


def _width(c):
    long_text = {"Caption", "Script", "Storytelling / Copy", "Design notes (+image refs)",
                 "Hypothesis on Why it Worked", "Possible Holicay Content", "Lessons",
                 "Human Feedback", "Notes", "Metadata", "Mechanism", "Description",
                 "Trigger / When to use", "Hook Pattern (general)", "Pattern (general)",
                 "Hook", "CTA", "CTA / Funnel", "Use Case"}
    ids = {"ID", "Hook ID", "CTA ID", "Funnel ID", "Inspo ID", "Platform"}
    if c["name"] in ids or c["link"] in ("hooks", "cta", "funnels", "inspo"):
        return 80
    if c["name"] in long_text:
        return 300
    if c["name"] in ("URL", "Output Folder", "Post Link", "Media Asset Link", "Slides"):
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


# ── commands: build / migrate / dictionary / relink ──────────────────────────
def cmd_init(_):
    sh = _open()
    for old, new in TAB_RENAMES.items():          # legacy whole-tab renames (idempotent; preserves gid + rows)
        if _ws(sh, old) and not _ws(sh, new):
            _ws(sh, old).update_title(new); print(f"[init] renamed worksheet {old!r} -> {new!r}")
    for old in ("Pipeline", "Feedback Log"):
        w = _ws(sh, old)
        if w and not _ws(sh, f"{old} (archived)"):
            try:
                w.update_title(f"{old} (archived)")
                sh.batch_update({"requests": [{"updateSheetProperties": {
                    "properties": {"sheetId": w.id, "hidden": True}, "fields": "hidden"}}]})
            except Exception as e:
                print(f"[sheets] could not archive '{old}': {e}", file=sys.stderr)
    for tab in SPEC:
        _ensure_tab(sh, tab)
    _seed_funnels(_ws(sh, FUNNEL_TAB))
    _build_dictionary(sh)
    _relink(sh)
    print("[sheets] init OK — tabs: " + ", ".join(list(SPEC) + [DICT_TAB]))
    print(f"  https://docs.google.com/spreadsheets/d/{_sheet_id()}/edit")


def _seed_funnels(ws):
    have = set(ws.col_values(1)[HEADER_ROWS:])
    added = 0
    for fid, name, trigger, ask, kpi in FUNNEL_SEED:
        if fid in have:
            continue
        row = {"Funnel ID": fid, "Name": name, "Trigger / When to use": trigger,
               "Canonical Ask": ask, "Primary KPI": kpi, "Creator": "Human",
               "Origin Ref": "funnel_skill.md", "Last Updated": _today()}
        ws.append_row([row.get(h, "") for h in HEADERS[FUNNEL_TAB]], value_input_option="USER_ENTERED")
        added += 1
    if added:
        print(f"[sheets] seeded {added} funnel row(s)")


# legacy WHOLE-WORKSHEET renames (old title -> new title); applied first by migrate-schema so the
# column realign finds the renamed tab. update_title preserves the tab's gid + rows.
TAB_RENAMES = {"Ashley": "Ana", "Mia": "Mia (Faceless)"}  # Mia is faceless -> tab suffixed for front-end ID
# old-name -> new-name for migrating a populated sheet onto the current SPEC (per fact tab + shared).
_FACT_RENAMES = {"Funnel": "Funnel ID", "Inspo URL": "Inspo ID", "Feedback": "Human Feedback"}
_FACT_DROPS = {"Follows", "Link Clicks"}
RENAMES = {
    INSPO_TAB:  {"Date": "Date Analyzed", "Funnel": "Funnel ID",
                 "Why it worked / metrics": "Hypothesis on Why it Worked",
                 "Verdict": "Possible Holicay Content", "Notes": "Human Feedback"},
    HOOKS_TAB:  {"Source": "Creator", "Posts": "Posts Used", "Steer": "Human Feedback"},
    CTA_TAB:    {"Funnel": "Funnel ID", "Source": "Creator", "Posts": "Posts Used", "Steer": "Human Feedback"},
    FUNNEL_TAB: {"Source": "Creator", "Posts": "Posts Used", "Steer": "Human Feedback"},
    BRAND_TAB:  {},
}
# old Source vocabulary -> new Creator dropdown vocabulary
CREATOR_NORM = {"inspo": "AI", "feedback": "AI + Human Feedback", "manual": "Human",
                "ai": "AI", "human": "Human", "ai + human feedback": "AI + Human Feedback", "": "AI"}
# columns intentionally dropped during migration (their data is discarded)
DROPS = {
    INSPO_TAB:  {"Author"},
    HOOKS_TAB:  {"Times Used", "Success / Perf", "Status"},
    CTA_TAB:    {"Times Used", "Success / Perf", "Status"},
    FUNNEL_TAB: {"Success / Perf", "Status"},
    BRAND_TAB:  {"Status"},
}
for _c in _characters().values():            # every character fact tab shares the fact renames/drops
    RENAMES.setdefault(_c["tab"], _FACT_RENAMES)
    DROPS.setdefault(_c["tab"], _FACT_DROPS)


def cmd_migrate_schema(_):
    """Realign existing rows to the current SPEC by column NAME, honouring RENAMES/DROPS,
    and converting every tab to the 2-row banded layout. Run BEFORE `init`. Idempotent."""
    sh = _open()
    # 0) legacy whole-worksheet renames first (preserve gid + rows) so the column realign below
    #    finds the renamed tab instead of `init` creating an empty one beside the orphan.
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
        # detect the real header row by its first cell (the first header name is rename-stable):
        # flat tabs have it on row 1; banded tabs (a banner above) have it on row 2.
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
            if "Creator" in new_headers:        # normalize old Source vocab -> Creator dropdown
                g["Creator"] = CREATOR_NORM.get((g.get("Creator", "") or "").strip().lower(),
                                                g.get("Creator", "").strip() or "AI")
            out.append([g.get(h, "") for h in new_headers])
        ws.clear()
        _ensure_tab(sh, tab)            # writes banner + headers + formatting
        if out:
            end = _a1col(len(new_headers) - 1)
            ws.batch_update([{"range": f"A3:{end}{2 + len(out)}", "values": out}],
                            value_input_option="USER_ENTERED")
        print(f"[migrate-schema] {tab}: {len(out)} row(s) -> {len(new_headers)} cols (banded)")
    print("[migrate-schema] done. Run `init` to seed funnels + build the Dictionary + relink.")


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
                 "it; the AI reads & clears it). The Holicay Brand tab is entirely yours.",
                 "", "", ""])
    rows.append([f'=HYPERLINK("{BLUEPRINT_URL}","START HERE  →  the full system blueprint '
                 '(architecture · engines · data model · workflow · how to run it) — on GitHub")',
                 "", "", ""])
    rows.append(["", "", "", ""])
    for tab, spec in SPEC.items():
        g = gid_of[tab]
        heads.append(len(rows))
        rows.append([f'=HYPERLINK("#gid={g}","{tab}")' if g is not None else tab, "", "", ""])
        subs.append(len(rows))
        rows.append(SUB[:])
        for ci, c in enumerate(spec["columns"]):
            # link the column name to its actual header cell (row 2) in the tab
            name = (f'=HYPERLINK("#gid={g}&range={_a1col(ci)}2","{c["name"]}")'
                    if g is not None else c["name"])
            rows.append([name, c["who"], c["desc"], c["example"]])
        rows.append(["", "", "", ""])          # spacer between groups
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


def _id_row_maps(sh):
    """{tab: {id: rownum}} for building back-links."""
    maps = {}
    for tab in (HOOKS_TAB, CTA_TAB, FUNNEL_TAB, INSPO_TAB,
                *[c["tab"] for c in _characters().values()]):
        ws = _ws(sh, tab)
        m = {}
        if ws:
            for i, v in enumerate(ws.col_values(1)[HEADER_ROWS:], start=HEADER_ROWS + 1):
                if v:
                    m[v] = i
        maps[tab] = (ws.id if ws else None, m)
    return maps


def _link_tab_for(value):
    if value.startswith("I") and value[1:].isdigit():
        return INSPO_TAB
    # post ids route to their character's fact tab by id_prefix (tt- -> Ana, ttc- -> Chloe).
    # longest prefix first so "ttc-" wins over "tt-" (the trailing "-" already disambiguates).
    for c in sorted(_characters().values(), key=lambda c: -len(c["id_prefix"])):
        if value.startswith(c["id_prefix"] + "-"):
            return c["tab"]
    if value.startswith("H") and value[1:].isdigit():
        return HOOKS_TAB
    if value.startswith("C") and value[1:].isdigit():
        return CTA_TAB
    if value.startswith("F") and value[1:].isdigit():
        return FUNNEL_TAB
    return None


def _relink(sh):
    """(Re)write clickable HYPERLINK back-links for every link column. Idempotent."""
    maps = _id_row_maps(sh)
    sid = _sheet_id()
    total = 0
    for tab, spec in SPEC.items():
        ws = _ws(sh, tab)
        if ws is None:
            continue
        headers = HEADERS[tab]
        grid = ws.get_all_values()
        data = grid[HEADER_ROWS:]
        if not data:
            continue
        link_cols = [(i, c) for i, c in enumerate(spec["columns"]) if c["link"]]
        if not link_cols:
            continue
        updates = []
        rich = []      # (row, col, plain, [(start,end,uri)])
        for ridx, row in enumerate(data):
            row = row + [""] * (len(headers) - len(row))
            for ci, c in link_cols:
                raw = row[ci].strip()
                if not raw or raw.startswith("="):
                    continue
                kind = c["link"]
                if kind in ("hooks", "cta", "funnels", "inspo"):
                    target = LINK_TAB[kind]
                    gid, m = maps[target]
                    if raw in m and gid is not None:
                        updates.append((ridx + HEADER_ROWS + 1, ci,
                                        f'=HYPERLINK("#gid={gid}&range=A{m[raw]}","{raw}")'))
                elif kind == "auto":
                    target = _link_tab_for(raw)
                    if target:
                        gid, m = maps[target]
                        if raw in m and gid is not None:
                            updates.append((ridx + HEADER_ROWS + 1, ci,
                                            f'=HYPERLINK("#gid={gid}&range=A{m[raw]}","{raw}")'))
                elif kind in ("post_multi", "funnels_multi"):
                    # a Posts Used cell can mix characters (tt-19, ttc-01) -> resolve EACH id's
                    # tab by prefix; funnels_multi always points at the Funnels tab.
                    parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
                    plain = ", ".join(parts)
                    runs, cur = [], 0
                    for p in parts:
                        st, en = cur, cur + len(p)
                        tgt = FUNNEL_TAB if kind == "funnels_multi" else _link_tab_for(p)
                        gid, m = maps.get(tgt, (None, {})) if tgt else (None, {})
                        if gid is not None and p in m:
                            uri = f"https://docs.google.com/spreadsheets/d/{sid}/edit#gid={gid}&range=A{m[p]}"
                            runs.append((st, en, uri))
                        cur = en + 2    # ", "
                    if runs:
                        rich.append((ridx + HEADER_ROWS + 1, ci, plain, runs))
        if updates:
            ws.batch_update([{"range": f"{_a1col(ci)}{r}", "values": [[f]]} for (r, ci, f) in updates],
                            value_input_option="USER_ENTERED")
            total += len(updates)
        for (r, ci, plain, runs) in rich:
            try:
                _set_rich_links(sh, ws.id, r - 1, ci, plain, runs)
                total += 1
            except Exception as e:
                print(f"[relink] {tab} r{r}: rich-link skipped: {e}", file=sys.stderr)
    print(f"[sheets] relink: {total} cell(s) linked")


def _set_rich_links(sh, gid, row0, col0, text, runs):
    """One cell, multiple in-text hyperlinks via textFormatRuns."""
    tf_runs = []
    last = 0
    for (st, en, uri) in runs:
        if st > last:
            tf_runs.append({"startIndex": last, "format": {}})
        tf_runs.append({"startIndex": st, "format": {"link": {"uri": uri},
                        "foregroundColor": {"red": 0.06, "green": 0.4, "blue": 0.75},
                        "underline": True}})
        last = en
    cell = {"userEnteredValue": {"stringValue": text}, "textFormatRuns": tf_runs}
    req = {"updateCells": {"rows": [{"values": [cell]}],
                           "fields": "userEnteredValue,textFormatRuns",
                           "start": {"sheetId": gid, "rowIndex": row0, "columnIndex": col0}}}
    sh.batch_update({"requests": [req]})


# ── commands: posts (per-character fact tables) ──────────────────────────────
def _char_ws(sh, char):
    return _ws(sh, char["tab"]) or _ensure_tab(sh, char["tab"])


def cmd_post_upsert(a):
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    headers = HEADERS[char["tab"]]
    fields = {"ID": a.id, "Platform": a.platform or "tiktok", "Title": a.title or "",
              "Output Folder": a.folder or "", "Caption": a.caption or "", "Hook": a.hook or "",
              "Hook ID": a.hook_id or "", "CTA": a.cta or "", "CTA ID": a.cta_id or "",
              "Funnel ID": a.funnel or "", "Script": a.script or "", "Inspo ID": a.inspo or "",
              "Notes": a.notes or ""}
    row = _row_for_id(ws, a.id)
    if row is None:
        fields["Date Created"] = a.created or _today()
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
                     ("hook", "Hook"), ("hook_id", "Hook ID"), ("cta", "CTA"), ("cta_id", "CTA ID"),
                     ("funnel", "Funnel ID"), ("script", "Script"), ("inspo", "Inspo ID"),
                     ("notes", "Notes"), ("post_link", "Post Link"), ("posting_date", "Posting Date"),
                     ("views", "Views"), ("likes", "Likes"), ("comments", "Comments"),
                     ("share", "Share"), ("save", "Save"), ("metadata", "Metadata")]:
        v = getattr(a, arg, None)
        if v is not None:
            pairs[col] = _today() if v == "today" else v
    if any(k in pairs for k in ("Views", "Likes", "Comments", "Share", "Save")):
        pairs["Stats Last Updated"] = _now()
    ws.batch_update([{"range": f"{_a1col(headers.index(h))}{row}", "values": [[v]]}
                     for h, v in pairs.items()], value_input_option="USER_ENTERED")
    print(f"[sheets] set {a.id}: {list(pairs)}")


def cmd_next_number(a):
    """Next post number for a character, derived from the SHEET (the source of truth) — never a
    local counter. Scans the character's fact tab col A for <prefix>-NN ids and returns max+1
    (1 if none). Prints JSON {character, prefix, nn, nn_padded, id}.

    With --reserve, also appends a stub row claiming that id immediately, so a teammate running
    this a moment later sees the claim on the shared Sheet and gets the next number — this is what
    kills the old race (the claim used to live only in an uncommitted local state.json). Delivery
    (post-upsert, same id) later fills the row in. Idempotent claim: if the id somehow already
    exists, the stub append is skipped."""
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    pre = char["id_prefix"] + "-"
    n = 0
    for v in ws.col_values(1):
        v = (v or "").strip()
        if v.startswith(pre) and v[len(pre):].isdigit():
            n = max(n, int(v[len(pre):]))
    nn = n + 1
    pid = f"{char['id_prefix']}-{nn:02d}"
    reserved = False
    if getattr(a, "reserve", False) and _row_for_id(ws, pid) is None:
        headers = HEADERS[char["tab"]]
        rowvals = {"ID": pid, "Platform": "tiktok", "Title": a.title or "(building)",
                   "Date Created": _today(), "Metadata": f"reserved {_now()}"}
        ws.append_row([rowvals.get(h, "") for h in headers],
                      value_input_option="USER_ENTERED", table_range="A2")
        reserved = True
    print(json.dumps({"character": char["key"], "name": char["name"],
                      "prefix": char["id_prefix"], "nn": nn, "nn_padded": f"{nn:02d}",
                      "id": pid, "reserved": reserved}))


def cmd_post_delete(a):
    """Delete a post's row from its character tab (e.g. removing a duplicate). Does NOT touch Drive or
    local files — remove those separately. Frees the number: next-number will hand it out again."""
    char = _char_for(a.character)
    sh = _open()
    ws = _char_ws(sh, char)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no {char['name']} row for {a.id}")
    ws.delete_rows(row)
    print(f"[sheets] deleted {a.id} (was row {row}) from tab {char['tab']}")


def cmd_deliver_missing(a):
    """Drive-canonical safety net: deliver every post that has a local outputs/<Title>/final/ but no
    Drive link on its Sheet row yet (shelling out to drive_sync.py --post), then record the returned
    link. Ensures a built-but-undelivered post is never the only copy — so local can stay disposable.
    Sweeps all characters (or one via --character). --dry-run just lists what it would deliver.
    The Title column is the bridge: it equals both the local outputs/ folder name and the Drive folder."""
    import subprocess
    sh = _open()
    root = _root()
    ds = os.path.join(root, "engine", "drive", "drive_sync.py")
    out_dir = os.path.join(root, "outputs")
    chars = [_char_for(a.character)] if a.character else list(_characters().values())
    dry = getattr(a, "dry_run", False)
    delivered = already = 0
    for char in chars:
        ws = _char_ws(sh, char)
        headers = HEADERS[char["tab"]]
        grid = ws.get_all_values()
        for ridx, row in enumerate(grid[HEADER_ROWS:], start=HEADER_ROWS + 1):
            rec = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            pid, title, folder = (rec.get("ID") or "").strip(), (rec.get("Title") or "").strip(), (rec.get("Output Folder") or "").strip()
            if not pid or not title or not os.path.isdir(os.path.join(out_dir, title, "final")):
                continue                                   # no row id / no local build for this row
            if folder:
                already += 1; continue                     # already on Drive (has a link)
            local = os.path.join(out_dir, title)
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


# ── commands: inspo ──────────────────────────────────────────────────────────
def cmd_inspo_add(a):
    sh = _open()
    ws = _ws(sh, INSPO_TAB) or _ensure_tab(sh, INSPO_TAB)
    iid = a.id or _next_id(ws, "I")
    row = {"Inspo ID": iid, "URL": a.url or "", "Date Analyzed": _today(),
           "Slides": a.slides or "", "Format": a.format or "", "Hook": a.hook or "",
           "Hook ID": a.hook_id or "", "Storytelling / Copy": a.story or "",
           "Design notes (+image refs)": a.design or "", "CTA / Funnel": a.cta or "",
           "CTA ID": a.cta_id or "", "Funnel ID": a.funnel or "",
           "Hypothesis on Why it Worked": a.why or "", "Possible Holicay Content": a.idea or ""}
    ws.append_row([row.get(h, "") for h in HEADERS[INSPO_TAB]], value_input_option="USER_ENTERED")
    print(f"[sheets] inspo {iid} added")


def cmd_inspo_set(a):
    sh = _open()
    ws = _ws(sh, INSPO_TAB) or _ensure_tab(sh, INSPO_TAB)
    headers = HEADERS[INSPO_TAB]
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no inspo row {a.id}")
    pairs = {}
    for arg, col in [("url", "URL"), ("slides", "Slides"), ("format", "Format"),
                     ("story", "Storytelling / Copy"), ("design", "Design notes (+image refs)"),
                     ("hook", "Hook"), ("hook_id", "Hook ID"), ("cta", "CTA / Funnel"),
                     ("cta_id", "CTA ID"), ("funnel", "Funnel ID"),
                     ("why", "Hypothesis on Why it Worked"), ("idea", "Possible Holicay Content")]:
        v = getattr(a, arg, None)
        if v is not None:
            pairs[col] = v
    ws.batch_update([{"range": f"{_a1col(headers.index(h))}{row}", "values": [[v]]}
                     for h, v in pairs.items()], value_input_option="USER_ENTERED")
    print(f"[sheets] inspo set {a.id}: {list(pairs)}")


def cmd_inspo_sync(a):
    """Make inspo Drive-canonical: for every inspo row whose Slides isn't already a Drive link, push
    its local inspo/NN folder to Drive (via drive_sync.py --inspo) and store the returned link in
    Slides — Sheets auto-renders a URL as clickable. Backfills existing rows and enforces going
    forward (the Inspo ID is canonical; the local inspo/NN folder is disposable scratch). --dry-run
    previews; --id limits to one row."""
    import subprocess
    sh = _open()
    ws = _ws(sh, INSPO_TAB)
    if ws is None:
        sys.exit("[sheets] no inspo tab")
    headers = HEADERS[INSPO_TAB]
    ds = os.path.join(_root(), "engine", "drive", "drive_sync.py")
    dry = getattr(a, "dry_run", False)
    synced = already = 0
    for ridx, r in enumerate(ws.get_all_values()[HEADER_ROWS:], start=HEADER_ROWS + 1):
        rec = dict(zip(headers, r + [""] * (len(headers) - len(r))))
        iid, slides = (rec.get("Inspo ID") or "").strip(), (rec.get("Slides") or "").strip()
        if not iid or (a.id and iid != a.id):
            continue
        if slides.startswith("http"):
            already += 1; continue                          # already a Drive link
        folder = slides if slides.startswith("inspo/") else ""
        local = os.path.join(_root(), folder) if folder else ""
        if not folder or not os.path.isdir(local):
            print(f"  [warn] {iid}: no local folder for Slides={slides!r} — skipping", file=sys.stderr); continue
        if dry:
            print(f"[inspo-sync] WOULD push {folder} -> Drive, link {iid}"); synced += 1; continue
        print(f"[inspo-sync] {iid}: pushing {folder} -> Drive")
        p = subprocess.run([sys.executable, ds, "--inspo", local], capture_output=True, text=True)
        sys.stdout.write(p.stdout)
        if p.returncode != 0:
            print(f"  [warn] push failed for {iid}: {p.stderr.strip()}", file=sys.stderr); continue
        url = next((ln.split("-> ", 1)[-1].strip() for ln in p.stdout.splitlines()
                    if "drive.google.com/drive/folders/" in ln), "")
        if url:
            ws.batch_update([{"range": f"{_a1col(headers.index('Slides'))}{ridx}", "values": [[url]]}],
                            value_input_option="USER_ENTERED")
            synced += 1
    print(f"[inspo-sync] done — {'would sync' if dry else 'synced'} {synced}, {already} already linked")


# ── commands: technique libraries ────────────────────────────────────────────
def _lib_append_lesson(ws, headers, post_id, lesson, row):
    cur = ws.row_values(row)
    cur += [""] * (len(headers) - len(cur))
    g = {h: cur[i] for i, h in enumerate(headers)}
    new_lessons = g["Lessons"]
    if lesson:
        new_lessons = (g["Lessons"] + ("\n" if g["Lessons"] else "") + f"- [{_today()}] {lesson}")
    posts = g.get("Posts Used", "")
    if post_id and post_id not in posts:
        posts = (posts + ", " + post_id) if posts else post_id
    ws.batch_update([
        {"range": f"{_a1col(headers.index('Lessons'))}{row}", "values": [[new_lessons]]},
        {"range": f"{_a1col(headers.index('Posts Used'))}{row}", "values": [[posts]]},
        {"range": f"{_a1col(headers.index('Last Updated'))}{row}", "values": [[_today()]]},
    ], value_input_option="USER_ENTERED")


def cmd_hook_add(a):
    sh = _open()
    ws = _ws(sh, HOOKS_TAB) or _ensure_tab(sh, HOOKS_TAB)
    hid = _next_id(ws, "H")
    row = {"Hook ID": hid, "Hook Pattern (general)": a.pattern or "", "Type": a.type or "",
           "Funnel Affinity": a.affinity or "", "Example": a.example or "",
           "Creator": a.creator or "AI", "Origin Ref": a.origin or "",
           "Lessons": (f"- [{_today()}] {a.lesson}" if a.lesson else ""),
           "Posts Used": a.post or "", "Last Updated": _today()}
    ws.append_row([row.get(h, "") for h in HEADERS[HOOKS_TAB]], value_input_option="USER_ENTERED")
    print(f"[sheets] hook {hid} added")


def cmd_hook_append_lesson(a):
    sh = _open()
    ws = _ws(sh, HOOKS_TAB) or _ensure_tab(sh, HOOKS_TAB)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no hook {a.id}")
    _lib_append_lesson(ws, HEADERS[HOOKS_TAB], a.post, a.lesson, row)
    print(f"[sheets] hook {a.id}: lesson appended")


def cmd_cta_add(a):
    sh = _open()
    ws = _ws(sh, CTA_TAB) or _ensure_tab(sh, CTA_TAB)
    cid = _next_id(ws, "C")
    row = {"CTA ID": cid, "Pattern (general)": a.pattern or "", "Funnel ID": a.funnel or "",
           "Placement": a.placement or "", "Mechanism": a.mechanism or "", "Example": a.example or "",
           "Creator": a.creator or "AI", "Origin Ref": a.origin or "",
           "Lessons": (f"- [{_today()}] {a.lesson}" if a.lesson else ""),
           "Posts Used": a.post or "", "Last Updated": _today()}
    ws.append_row([row.get(h, "") for h in HEADERS[CTA_TAB]], value_input_option="USER_ENTERED")
    print(f"[sheets] cta {cid} added")


def cmd_cta_append_lesson(a):
    sh = _open()
    ws = _ws(sh, CTA_TAB) or _ensure_tab(sh, CTA_TAB)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no cta {a.id}")
    _lib_append_lesson(ws, HEADERS[CTA_TAB], a.post, a.lesson, row)
    print(f"[sheets] cta {a.id}: lesson appended")


def cmd_funnel_list(_):
    print(json.dumps(_read_rows(_open(), FUNNEL_TAB), ensure_ascii=False, indent=2))


def cmd_funnel_add(a):
    sh = _open()
    ws = _ws(sh, FUNNEL_TAB) or _ensure_tab(sh, FUNNEL_TAB)
    fid = a.id or _next_id(ws, "F")
    row = {"Funnel ID": fid, "Name": a.name or "", "Trigger / When to use": a.trigger or "",
           "Canonical Ask": a.ask or "", "Primary KPI": a.kpi or "",
           "Creator": a.creator or "Human", "Origin Ref": a.origin or "",
           "Lessons": (f"- [{_today()}] {a.lesson}" if a.lesson else ""),
           "Posts Used": a.post or "", "Last Updated": _today()}
    ws.append_row([row.get(h, "") for h in HEADERS[FUNNEL_TAB]], value_input_option="USER_ENTERED")
    print(f"[sheets] funnel {fid} added")


def cmd_funnel_append_lesson(a):
    sh = _open()
    ws = _ws(sh, FUNNEL_TAB) or _ensure_tab(sh, FUNNEL_TAB)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no funnel {a.id}")
    _lib_append_lesson(ws, HEADERS[FUNNEL_TAB], a.post, a.lesson, row)
    print(f"[sheets] funnel {a.id}: lesson appended")


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


# ── commands: human feedback (every GREEN cell) ──────────────────────────────
# character keys (ana, chloe, …) -> their fact tab; the shared libraries keep their short keys.
FEEDBACK_TABS = {**{c["key"]: c["tab"] for c in _characters().values()},
                 "inspo": INSPO_TAB, "hook": HOOKS_TAB, "cta": CTA_TAB, "funnel": FUNNEL_TAB}


def cmd_feedback_poll(_):
    sh = _open()
    out = []
    for key, tab in FEEDBACK_TABS.items():
        headers = HEADERS[tab]
        if "Human Feedback" not in headers:
            continue
        fi = headers.index("Human Feedback")
        ws = _ws(sh, tab)
        if ws is None:
            continue
        for r in ws.get_all_values()[HEADER_ROWS:]:
            if len(r) > fi and r[fi].strip():
                out.append({"tab": key, "tab_name": tab, "id": r[0] if r else "",
                            "feedback": r[fi].strip()})
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_feedback_clear(a):
    sh = _open()
    key = (a.tab or _default_char_key()).lower()
    if key not in FEEDBACK_TABS:
        sys.exit(f"[sheets] feedback-clear --tab must be one of {list(FEEDBACK_TABS)}")
    tab = FEEDBACK_TABS[key]
    headers = HEADERS[tab]
    ws = _ws(sh, tab) or _ensure_tab(sh, tab)
    row = _row_for_id(ws, a.id)
    if row is None:
        sys.exit(f"[sheets] no {a.id} in {tab}")
    ups = [{"range": f"{_a1col(headers.index('Human Feedback'))}{row}", "values": [[""]]}]
    stamp = (f": {a.note}" if a.note else "")
    if "Metadata" in headers:        # fact tabs carry Metadata; the libraries use Lessons instead
        prev = ws.cell(row, headers.index("Metadata") + 1).value or ""
        meta = (prev + "\n" if prev else "") + f"[{_now()}] feedback processed{stamp}"
        ups.append({"range": f"{_a1col(headers.index('Metadata'))}{row}", "values": [[meta]]})
    else:
        cur = ws.row_values(row); cur += [""] * (len(headers) - len(cur))
        prev = cur[headers.index("Lessons")]
        new = prev + ("\n" if prev else "") + f"- [{_today()}] (your feedback) {a.note or 'applied'}"
        ups.append({"range": f"{_a1col(headers.index('Lessons'))}{row}", "values": [[new]]})
        ups.append({"range": f"{_a1col(headers.index('Last Updated'))}{row}", "values": [[_today()]]})
    ws.batch_update(ups, value_input_option="USER_ENTERED")
    print(f"[sheets] feedback cleared for {a.id} in {tab}")


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


def cmd_inspo_stats(a):
    sh = _open()
    ws = _ws(sh, INSPO_TAB) or _ensure_tab(sh, INSPO_TAB)
    headers = HEADERS[INSPO_TAB]
    ui = headers.index("URL")
    grid = ws.get_all_values()[HEADER_ROWS:]
    targets = []
    for i, r in enumerate(grid, start=HEADER_ROWS + 1):
        if a.all:
            if len(r) > ui and r[ui].strip():
                targets.append((i, r[0], r[ui].strip()))
        elif r and r[0] == a.id:
            url = r[ui].strip() if len(r) > ui else ""
            if not url:
                sys.exit(f"[sheets] {a.id} has no URL to scrape")
            targets.append((i, r[0], url))
    if not a.all and not targets:
        sys.exit(f"[sheets] no inspo row {a.id}")
    for (row, iid, url) in targets:
        s = _scrape_stats(url)
        got = _apply_stats(ws, headers, row, s)
        print(f"[sheets] {iid}: {got}")


# ── commands: read / relink / dictionary / migrate(outputs) ──────────────────
def cmd_read(a):
    sh = _open()
    if a.tab in SPEC:
        print(json.dumps(_read_rows(sh, a.tab), ensure_ascii=False, indent=2)); return
    ws = _ws(sh, a.tab)
    if ws is None:
        sys.exit(f"[sheets] no tab named {a.tab!r}")
    print(json.dumps(ws.get_all_records(), ensure_ascii=False, indent=2))


def cmd_relink(_):
    _relink(_open())


def cmd_dictionary(_):
    _build_dictionary(_open())


def cmd_migrate(a):
    """Seed a character's fact tab from the built posts in outputs/ (one row each)."""
    char = _char_for(getattr(a, "character", None))
    sh = _open()
    ws = _char_ws(sh, char)
    headers = HEADERS[char["tab"]]
    out_dir = os.path.join(_root(), "outputs")
    if not os.path.isdir(out_dir):
        sys.exit("[sheets] no outputs/ dir")
    existing = set(ws.col_values(1)[HEADER_ROWS:])
    added = 0
    for name in sorted(os.listdir(out_dir)):
        d = os.path.join(out_dir, name)
        if not os.path.isdir(d):
            continue
        num = name.split(" ", 1)[0].split("-")[0].strip()
        pid = f"{char['id_prefix']}-{num.zfill(2)}" if num.isdigit() else f"{char['id_prefix']}-{name[:6]}"
        if pid in existing:
            continue
        cap = ""
        cp = os.path.join(d, "caption.txt")
        if os.path.exists(cp):
            cap = open(cp, encoding="utf-8").read().strip()
        try:
            created = datetime.date.fromtimestamp(os.path.getmtime(d)).isoformat()
        except Exception:
            created = _today()
        rowvals = {"ID": pid, "Platform": "tiktok", "Title": name, "Caption": cap,
                   "Date Created": created, "Notes": "migrated from outputs/",
                   "Metadata": f"migrated {_today()}"}
        ws.append_row([rowvals.get(h, "") for h in headers],
                      value_input_option="USER_ENTERED", table_range="A2")
        added += 1
        print(f"  + {pid}  {name}")
    print(f"[sheets] migrate done — {added} new row(s)")


def main():
    p = argparse.ArgumentParser(description="Project Ana Google Sheet (spec-driven front-end)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(fn=cmd_init)
    mig = sub.add_parser("migrate"); mig.set_defaults(fn=cmd_migrate); mig.add_argument("--character")
    sub.add_parser("migrate-schema").set_defaults(fn=cmd_migrate_schema)
    sub.add_parser("relink").set_defaults(fn=cmd_relink)
    sub.add_parser("dictionary").set_defaults(fn=cmd_dictionary)

    u = sub.add_parser("post-upsert"); u.set_defaults(fn=cmd_post_upsert)
    u.add_argument("--character"); u.add_argument("--id", required=True)
    for f in ("platform", "title", "folder", "caption", "hook", "hook-id", "cta", "cta-id",
              "funnel", "script", "inspo", "notes", "created"):
        u.add_argument(f"--{f}")

    s = sub.add_parser("post-set"); s.set_defaults(fn=cmd_post_set)
    s.add_argument("--character"); s.add_argument("--id", required=True)
    for f in ("title", "folder", "caption", "hook", "hook-id", "cta", "cta-id", "funnel",
              "script", "inspo", "notes", "post-link", "posting-date", "views", "likes",
              "comments", "share", "save", "metadata"):
        s.add_argument(f"--{f}")

    asx = sub.add_parser("post-stats"); asx.set_defaults(fn=cmd_post_stats)
    asx.add_argument("--character"); asx.add_argument("--id"); asx.add_argument("--all", action="store_true")

    nn = sub.add_parser("next-number"); nn.set_defaults(fn=cmd_next_number)
    nn.add_argument("--character"); nn.add_argument("--title")
    nn.add_argument("--reserve", action="store_true",
                    help="also claim the id now by appending a stub row (visible to the team)")

    dm = sub.add_parser("deliver-missing"); dm.set_defaults(fn=cmd_deliver_missing)
    dm.add_argument("--character"); dm.add_argument("--dry-run", action="store_true")

    pdel = sub.add_parser("post-delete"); pdel.set_defaults(fn=cmd_post_delete)
    pdel.add_argument("--character"); pdel.add_argument("--id", required=True)

    ia = sub.add_parser("inspo-add"); ia.set_defaults(fn=cmd_inspo_add)
    for f in ("id", "url", "slides", "format", "hook", "hook-id", "story", "design",
              "cta", "cta-id", "funnel", "why", "idea"):
        ia.add_argument(f"--{f}")
    isx = sub.add_parser("inspo-stats"); isx.set_defaults(fn=cmd_inspo_stats)
    isx.add_argument("--id"); isx.add_argument("--all", action="store_true")
    iss = sub.add_parser("inspo-set"); iss.set_defaults(fn=cmd_inspo_set)
    iss.add_argument("--id", required=True)
    for f in ("url", "slides", "format", "story", "design", "hook", "hook-id",
              "cta", "cta-id", "funnel", "why", "idea"):
        iss.add_argument(f"--{f}")
    isy = sub.add_parser("inspo-sync"); isy.set_defaults(fn=cmd_inspo_sync)
    isy.add_argument("--id"); isy.add_argument("--dry-run", action="store_true")

    ha = sub.add_parser("hook-add"); ha.set_defaults(fn=cmd_hook_add)
    for f in ("pattern", "type", "affinity", "example", "creator", "origin", "lesson", "post"):
        ha.add_argument(f"--{f}")
    hl = sub.add_parser("hook-append-lesson"); hl.set_defaults(fn=cmd_hook_append_lesson)
    hl.add_argument("--id", required=True); hl.add_argument("--lesson", required=True); hl.add_argument("--post")

    ca = sub.add_parser("cta-add"); ca.set_defaults(fn=cmd_cta_add)
    for f in ("pattern", "funnel", "placement", "mechanism", "example", "creator", "origin", "lesson", "post"):
        ca.add_argument(f"--{f}")
    cl = sub.add_parser("cta-append-lesson"); cl.set_defaults(fn=cmd_cta_append_lesson)
    cl.add_argument("--id", required=True); cl.add_argument("--lesson", required=True); cl.add_argument("--post")

    sub.add_parser("funnel-list").set_defaults(fn=cmd_funnel_list)
    fa = sub.add_parser("funnel-add"); fa.set_defaults(fn=cmd_funnel_add)
    for f in ("id", "name", "trigger", "ask", "kpi", "creator", "origin", "lesson", "post"):
        fa.add_argument(f"--{f}")
    fl = sub.add_parser("funnel-append-lesson"); fl.set_defaults(fn=cmd_funnel_append_lesson)
    fl.add_argument("--id", required=True); fl.add_argument("--lesson", required=True); fl.add_argument("--post")

    sub.add_parser("brand-list").set_defaults(fn=cmd_brand_list)
    ba = sub.add_parser("brand-add"); ba.set_defaults(fn=cmd_brand_add)
    for f in ("id", "feature", "use-case", "desc", "asset", "funnel-fit", "notes"):
        ba.add_argument(f"--{f}")

    sub.add_parser("feedback-poll").set_defaults(fn=cmd_feedback_poll)
    fc = sub.add_parser("feedback-clear"); fc.set_defaults(fn=cmd_feedback_clear)
    fc.add_argument("--tab", required=True, help="ana | chloe | inspo | hook | cta | funnel")
    fc.add_argument("--id", required=True); fc.add_argument("--note")

    r = sub.add_parser("read"); r.set_defaults(fn=cmd_read); r.add_argument("--tab", required=True)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
