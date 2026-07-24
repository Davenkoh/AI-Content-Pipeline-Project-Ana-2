# Project Ana 2.0

**A framework-first TikTok carousel factory you drive with any AI coding agent.** Pick a character and a
country; it claims the next **rotation slot** (which of the four blueprints A / B / C1 / C2, in a human or
no-human variant), writes humanized story-first copy, sources real UGC photos, renders a **1080×1920**
carousel, QCs it, delivers it to Google Drive, and logs a Google Sheet row — then folds your feedback and
the scraped stats back in so the next post is better. Four locked blueprints; **only the copy + photos
change per post.**

Three parallel accounts, one per character. The carousels quietly drive viewers toward **Holicay** (a
travel itinerary-planner app). **You post to TikTok yourself** — nothing publishes without you.

## The loop at a glance

```
    country + character
            │
            ▼
   ┌──────────────────────┐   rotation is DERIVED from the Sheet (per account):
   │  next-slot (Sheet)   │   framework cycles A → B → C1 → C2;
   │  → framework+variant │   the human / no-human variant alternates per framework
   └──────────┬───────────┘   (the A/B test)
              ▼
   ┌──────────────────────┐   copy.json (pre-broken lines) + fact-checked caption
   │  copy + photos        │   real UGC photos, curated against the UGC gate
   │  per CONTRACT.md      │   → media/graded/<slug>.jpg
   └──────────┬───────────┘
              ▼
   ┌──────────────────────┐        ┌──────────────────┐
   │  render 1080×1920     │  ───▶  │  QC gate (hard)   │  ──▶ fix until green
   │  (build.js)           │        └──────────────────┘
   └──────────┬───────────┘
              ▼
   ┌──────────────────────┐
   │  Drive folder + Sheet │  ◀── the review surface (silence = approved)
   │  row (auto-delivered) │
   └──────────┬───────────┘
              ▼
      YOU download & post to TikTok  ──▶  leave GREEN feedback
              │                                    │
              ▼                                    ▼
     stats scraped back ──▶ Dashboard      propagate-feedback / analyze
              │                                    │
              └──────────────▶ next gen is better ◀┘
```

## The accounts

| Character | Prefix | Country | TikTok | Next id |
|---|---|---|---|---|
| **Ana** | `tt-` | Vietnam | @solo.with.ana | `tt-20` |
| **Chloe** | `ttc-` | Japan | @chloe.belletravel | `ttc-11` |
| **Hannah** | `tth-` | USA | *(handle pending)* | `tth-05` |

Numbering continues each account's 1.0 history. Chloe's character scene photos (`chars/chloe_*`) exist;
**Ana + Hannah need theirs generated before their first *human*-variant post** (`new-character` final step).

## The human-vs-no-human experiment

Every account posts each framework **both ways** over time — a **human** cover/ending (the character in
scene) and a **no-human** one (pure scenic, same text). The rotation alternates them per framework, so the
`analyze` skill can read which actually wins on views/saves. That verdict is the headline of each learning pass.

## The three homes (all owned by `creators@holicay.com`)

- **GitHub** — code, brains, skills: https://github.com/Davenkoh/Project-Ana-2
- **Google Sheet** — "Project Ana 2.0" (fact tabs + Dashboard + Connectors + Accounts + Holicay Brand + Dictionary; GREEN cells are yours): https://docs.google.com/spreadsheets/d/1Wskn2YPWwu3cEBJVTwyYpgM7XXVjJwODLjZVqLgAqWo/edit
- **Google Drive** — "Project Ana 2.0" (all media + delivered posts + `_setup/` secrets), in `creators@holicay.com` My Drive. Find the folder link with `python3 engine/drive/drive_sync.py --list-shared`.

## Quickstart

```bash
bash engine/qc/preflight.sh                                  # 1. confirm the environment is ready
python3 engine/sheets/sheets.py next-slot --character chloe  # 2. peek at the next slot (framework + variant)
# 3. tell your agent: "generate a post for chloe"  — it runs the generate-post skill (WORKFLOW §1-§11)
```

First time on this machine? [`SETUP.md`](SETUP.md) walks clone → bootstrap → secrets → logins.

## The repo in one screen

```
AGENTS.md         the front-door resolver: capability -> the one canonical home
CONTRACT.md       the durable OUTPUT SPEC (design · type · plug · QC gates) the renderer reproduces
WORKFLOW.md       the operating manual (stages §1-§11 + Stats/Feedback/Analyze + Guardrails)
SETUP.md          new-machine onboarding · CONNECTORS.md  the billing/troubleshooting registry
engine/           the deterministic tools (sheets · source · render · qc · drive · scrape · design · setup · lib)
knowledge/        the brains: frameworks (the spine) + copy_bank · realism · voice · tuning · brand
.claude/skills/   the agent's verbs (generate-post · scrape-stats · propagate-feedback · analyze · new-character)
fixtures/         the four framework copy exemplars + reference contact sheets (the render regression spec)
media/            graded/ (render-ready picks) · brand/ (first-party) · library/ (scratch) · manifest.json
chars/            character-in-scene cover/ending photos    character/  the persona registry images (on Drive)
state.json        the local registry + Sheet/Drive pointers (the rotation is derived from the Sheet)
outputs/<key>/    built decks (final/ -> Drive; _work/ is gitignored scratch)
```

## 1.0 is the archive

The original **Project Ana** (`/Project Ana`, repo `Davenkoh/Project-Ana`, its own Sheet + Drive) stays
**untouched** as the archive. 2.0 is a fresh repo + fresh cloud; nothing here writes back to 1.0.

## Safety / rollback

`main` is the live system; larger changes land on a branch. Finished posts live on Drive, so the
deliverables are safe regardless of local repo state. Media is Drive-canonical; code + docs are in git.
