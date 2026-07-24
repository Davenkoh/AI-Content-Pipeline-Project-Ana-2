---
name: generate-post
description: Build one finished framework TikTok carousel (A/B/C/D) for a character, near-autonomously (WORKFLOW §1→§11). Use when the user says "make a post", "generate a post", "build the next post for chloe", "run the loop", or gives a character + country. Pass `all` to loop every registry character. Takes the vision gates (photo curation + contact-sheet review) itself.
---

# Generate One Post

Turns a **rotation slot** into a **review-ready framework deck**, near-autonomously: run `WORKFLOW.md`
(repo root) §1 → §11 end to end and take the vision gates (Gate-9 photo curation in §5, the
contact-sheet review in §8) with your own **vision**.

> **`WORKFLOW.md` is canonical** — it carries the exact command for every stage. This skill only
> sequences it. `CREATIVE.md` (content wheel) + `DESIGN.md` (visual/build spec) are the output spec. Read
> `WORKFLOW.md` first; do not restate its commands here.

## Touches
- **Knowledge (load at §4 copy):** `DESIGN.md`, `CREATIVE.md`,
  `knowledge/tuning/06_performance.md`, `knowledge/tuning/02_copywriting.md`, `knowledge/voice/humanizer.md`,
  `knowledge/brand/holicay_brand.md` (freshness: scan recent `outputs/<char>/*/copy.json`).
  **§5 sourcing:** `knowledge/tuning/03_sourcing.md`, `knowledge/frameworks/photo_sourcing.md`, `DESIGN.md`
  Gate 9. **§3 realism:** `knowledge/realism/*`.
- **Engine (capabilities; exact flags in WORKFLOW):** sheets · source · render · qc · drive.
- **State:** the slot comes from the **Sheet** — `sheets.py next-slot --character <key> --reserve` (no local counter).

## Input
- **Which character** — `ana` (Vietnam `tt-`) · `chloe` (Japan `ttc-`) · `hannah` (USA `tth-`), or **`all`**
  to loop every registry character sequentially (each gets its own slot).
- **`--country`** override (defaults to the character's registry country).
- **Copy dial** — `same` (verbatim reuse of a pack) | `similar` (paraphrase — same places, reworded) |
  `fresh` (new angles/places). **Default `fresh`** for a new iteration; **paraphrase** when reusing a pack
  across accounts. This drives the §4 freshness check (scan recent `outputs/<char>/*/copy.json`).

## Guardrails → `WORKFLOW.md` "Guardrails" (obey, never restate)
Posting is always manual (deliver + log auto-run; the human posts). Never skip `qc_gate.mjs`. No em/en
dashes in post copy. UGC Gate 9 on every body photo. Plug copy is verbatim. Lines arrive pre-broken.
GREEN is the human's. Quit Chrome after CDP work.

## Sequence (pointers into WORKFLOW — read it for the commands)
- **§1** preflight (`preflight.sh`) — abort on FAIL.
- **§2** `next-slot --character <key> [--country X] --reserve` → the slot JSON (id · framework · variant ·
  country · copy_iteration). Everything downstream keys off these.
- **§3 HUMAN-VARIANT PREREQ:** if `variant == human` and `chars/<key>_cover.png` **or**
  `chars/<key>_ending.png` is missing → **generate them first** (persona-gen chain per WORKFLOW §3 +
  `new-character` final step). **Chloe has hers; Ana + Hannah are pending** — a `human` slot for them is
  blocked until you gen the scene photos. A `nohuman` slot skips this stage.
- **§4** copy — load the `DESIGN.md` schema + this framework's `CREATIVE.md` block + `tuning/06` + `02` +
  `voice/humanizer` + `knowledge/brand/holicay_brand.md` (honor the copy dial; check freshness by scanning
  recent `outputs/<char>/*/copy.json`) → write `outputs/<key>/<ID - Title>/copy.json` (**pre-broken lines**) +
  `caption.txt` (title verbatim + one-para-per-slide essay + hashtag formula; **C: keyword CTA is the
  first body line**) → **fact-check** prices/hours/claims via WebSearch/WebFetch primary sources →
  `flags.md` (verbatim-vs-drafted + unverified).
- **§5** photos — plan slugs (`fixtures/places.json` shape) → source via `brightdata.py places`
  (prioritized) / `gimg` / `ig` (+ `app_icons.py` + `route_map_shot.js` for D) → **VISION-curate against
  Gate 9** → install picks to `media/graded/<slug>.jpg` → **prune `media/library/`** → write `sources.md`
  (`media/PHOTO_SOURCES.md` row pattern) + confirm manifest rows. Scenic cover/ending + plug `bg_photo` are
  postcard-exempt.
- **§6** render — `build.js --copy … --out …/_work/render --contact` (renders 1080×1920; cover+save render
  both `_human`/`_nohuman`; `_contact.png` montage).
- **§7** assemble — copy the **chosen variant** cover/save (suffix stripped) + bodies → `final/`; keep `caption.txt`.
- **§8 VISION GATE:** `Read` `_work/render/_contact.png` against **DESIGN.md gates 1–8**; fix + re-render on any miss.
- **§9** `qc_gate.mjs "<post folder>" --framework <OPT>` → **fix until exit 0**.
- **§10** deliver — `drive_sync --post` (prints the Drive link) → `sheets.py post-upsert` (all slot fields +
  Drive link + caption). The delivered `copy.json` is the freshness record for next time (no separate freshness file).
- **§11** report — Drive folder link + one-line summary. Silence = approved; feedback → regen +
  `propagate-feedback`.

## `all` mode
Run characters **sequentially**, each with its own `next-slot` claim and its own post folder. When the
same country × framework pack is reused across accounts, **paraphrase** (copy dial `similar`) rather than
shipping identical text. Report one Drive link per character.

## Unique notes this skill owns (not in WORKFLOW)
- **Persona-gen reliability (§3).** Warm + prep + send in **one bash call** — the Stop hook quits Chrome at
  end of turn. Sequential gens share one ChatGPT conversation, so grab the **LAST** big image. If a gen
  dies after the image rendered, recover it with `gpt_grab.js` rather than regenerating.
- **On failure.** Surface the error; note it on the row's `--notes`. **Do not deliver a partial deck.**
  Leave the `(building)` stub only if you intend to resume; otherwise `post-delete` it so the slot frees up.
- **Quit Chrome when done** — `bash engine/lib/quit_chrome.sh` (a Stop hook also runs it).

## Output
A review-ready post folder (`final/` + `caption.txt` + `copy.json` + `flags.md` + `sources.md`), delivered
to Drive, with a logged Sheet row (the delivered `copy.json` is the freshness record). The human reviews on the Sheet +
Drive, posts to TikTok, and leaves GREEN feedback — which becomes a global lesson via `propagate-feedback`,
never a one-off fix.
