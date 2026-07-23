# Project Ana 2.0 — Agent Front Door (the resolver)

> **First file any AI orchestrator reads** (Claude Code, Codex, Hermes, …). It resolves WHAT you can do →
> WHERE the ONE canonical instruction lives. It is an index, never a tutorial: every row points at a
> single home and restates nothing. **DRY + MECE** — one row per capability, no overlap.

Project Ana 2.0 is a **framework-first TikTok carousel machine.** Four locked blueprints — **A** (fear of
mistakes), **B** (hot takes), **C1** (full-trip dump), **C2** (plan-&-prep guide) — reproduced every post;
only the **copy + sourced photos** change. The rotation (which framework + human/nohuman variant is next)
is **derived live from the Google Sheet**, per account. `.claude/skills/` are plain markdown any agent can
read; the engine is plain CLI you shell out to.

## 1 · Skills — the user-facing verbs (what the agent DOES)
Auto-surfaced by description; invoke by name or `/slash`. Each `SKILL.md` sequences `WORKFLOW.md` — it
never forks the commands.

| When the user wants… | Skill | Sequences |
|---|---|---|
| build the next post (one character or `all`) | [`generate-post`](.claude/skills/generate-post/SKILL.md) | WORKFLOW §1–§11 |
| refresh post stats from TikTok | [`scrape-stats`](.claude/skills/scrape-stats/SKILL.md) | WORKFLOW §Stats |
| process the GREEN review feedback | [`propagate-feedback`](.claude/skills/propagate-feedback/SKILL.md) | WORKFLOW §Feedback |
| mine what's working (the learning pass) | [`analyze`](.claude/skills/analyze/SKILL.md) | WORKFLOW §Analyze |
| stand up a new character | [`new-character`](.claude/skills/new-character/SKILL.md) | its own steps + WORKFLOW §3 |

## 2 · Engine — the deterministic hands, by CAPABILITY (not by file)
Full flags live in `WORKFLOW.md`; this table is the map. **Do not edit `engine/`** — it is finished + verified.

| Capability | Command | Manual |
|---|---|---|
| claim a slot · log · stats · feedback | `python3 engine/sheets/sheets.py <verb> …` | WORKFLOW §2 · §10 · §Stats · §Feedback |
| source + curate photos | `python3 engine/source/brightdata.py <backend> …` (+ `app_icons.py`, `route_map_shot.js`) | WORKFLOW §5 |
| render the deck (1080×1920) | `node engine/render/build.js --copy … --out … --contact` | WORKFLOW §6 |
| hard QC gate + preflight | `node engine/qc/qc_gate.mjs "<post>" --framework <OPT>` · `bash engine/qc/preflight.sh` | WORKFLOW §9 · §1 |
| deliver to Drive | `python3 engine/drive/drive_sync.py --post … --character <key>` | WORKFLOW §10 |
| scrape TikTok stats/profile | `node engine/scrape/tiktok_profile.js <key>` · `tiktok_stats.js` · `tiktok_login.js` | WORKFLOW §Stats |
| persona / scene-photo gen (CDP Chrome) | `engine/design/prep_cover_refs.py` → `gpt_prep.js` → `gpt_send.js` → `gpt_grab.js` / `gen_base_ref.js` | WORKFLOW §3 · new-character |
| onboarding / provisioning | `bash setup.sh` · `python3 engine/setup/provision.py <create\|seed-markers>` | SETUP.md |
| quit the shared Chrome | `bash engine/lib/quit_chrome.sh` | WORKFLOW Guardrails |

> One generic tool per capability, driven by per-post DATA (`copy.json`, the `fixtures/places.json`-shaped
> slug plan). Add a backend/template, not a new file.

## 3 · Knowledge — the brains, loaded at the stage that needs it
Index: [`knowledge/README.md`](knowledge/README.md). The **spine is `CONTRACT.md` + `knowledge/frameworks/`**.

| Stage | Load |
|---|---|
| the output spec (design / type / plug / QC gates) | [`CONTRACT.md`](CONTRACT.md) |
| the framework blueprints (hooks · slide maps · plug copy · caption) | [`knowledge/frameworks/content_frameworks.md`](knowledge/frameworks/content_frameworks.md) |
| write the copy (§4) | `knowledge/copy_bank/<country>/<OPT>.md` + `knowledge/tuning/02_copywriting.md` + `knowledge/voice/humanizer.md` |
| source photos (§5) | `knowledge/frameworks/photo_sourcing.md` + `knowledge/tuning/03_sourcing.md` + `engine/source/SOURCING_STATUS.md` |
| character / scene realism (§3) | `knowledge/realism/*` (realism_book · persona_gen_prompt_reference · winning_prompts) |
| what's winning (read before copy) | `knowledge/tuning/06_performance.md` (written by `analyze`) |
| feedback audit trail | `knowledge/tuning/propagation-log.md` |
| what Holicay is | the Sheet **Holicay Brand** tab (truth); `knowledge/brand/holicay_brand.md` is a cache |

## 4 · The three homes — where state lives
| Home | Holds | Link |
|---|---|---|
| **GitHub** (this repo) | code + text brains + skills | https://github.com/Davenkoh/Project-Ana-2 |
| **Google Drive** — "Project Ana 2.0" | all media + finished posts + `_setup/` secrets | root in `creators@holicay.com` My Drive (find the folder link with `python3 engine/drive/drive_sync.py --list-shared`) |
| **Google Sheet** — "Project Ana 2.0" | per-character fact tabs + Dashboard + Connectors + Holicay Brand + Dictionary (GREEN cells = human feedback) | https://docs.google.com/spreadsheets/d/1Wskn2YPWwu3cEBJVTwyYpgM7XXVjJwODLjZVqLgAqWo/edit |

`state.json` is the small local **registry** (each character = name + id_prefix + country + TikTok @handle)
+ the Sheet/Drive pointers. The rotation slot + next number are **derived from the Sheet**, never stored.
**1.0** (`/Project Ana`, repo `Davenkoh/Project-Ana`) is the untouched archive.

## 5 · Operating order + guardrails
Run the loop per [`WORKFLOW.md`](WORKFLOW.md): **§1 preflight → §2 claim slot → §3 scene-photo prereq → §4
copy → §5 photos → §6 render → §7 assemble → §8 vision review → §9 QC → §10 deliver + log → §11 report.**
The **Guardrails** (posting always manual; never skip QC; no dashes in post copy; UGC Gate 9; plug copy
verbatim; pre-broken lines; GREEN is the human's; quit Chrome; Drive-canonical media) live once in
`WORKFLOW.md` "Guardrails" — obey them there, never restate them here.

New to the system? [`README.md`](README.md) (glance) → [`SETUP.md`](SETUP.md) (install) →
[`WORKFLOW.md`](WORKFLOW.md) (operate). Connector billing/troubleshooting: [`CONNECTORS.md`](CONNECTORS.md).

## 6 · Agent requirements
Any orchestrator that can **run shell** (`python3` ≥ 3.9, `node` ≥ 18), **has vision** (curate Gate-9
photos, review the contact sheet, QC persona gens), and can **fetch the web** (`WebSearch` / `WebFetch`
for the §4 fact-check). **Nothing here is Claude-specific** — `.claude/skills/*` are plain markdown, and
the Stop/SessionStart hooks (media sync + quit Chrome) are a convenience a non-Claude agent runs by hand
(SETUP.md).
