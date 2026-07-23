# Project Ana 2.0 — The Workflow

The canonical operating manual. One continuous loop turns a **country + a rotation slot** into a
**finished framework carousel** (A / B / C1 / C2 per `CONTRACT.md`), delivered to Google Drive and
logged on the Google Sheet. Any AI coding agent with shell + vision drives it; the **Sheet + Drive
folder are the front-end** (where the human watches, feeds back, and owns the brand).

> **This is the command reference. Read it top to bottom the first time; after that jump to the stage
> you need — every stage is independently runnable, so a regen re-enters mid-flow.** The `generate-post`
> skill *sequences* these stages; it never restates their commands. `CONTRACT.md` +
> `knowledge/frameworks/content_frameworks.md` own the output spec; this doc owns how you produce it.

Every stage lists **inputs · command(s) · output · tuning doc**. The `generate-post` skill's stages 0–10
map onto §1–§11 here one-for-one.

## The shape

| Phase | Stages | What happens |
|---|---|---|
| **Set up** | §1–§3 | preflight, claim a rotation slot, make sure a `human`-variant deck has its scene photos |
| **Compose** | §4–§5 | write pre-broken copy + fact-checked caption, source + curate real UGC photos |
| **Build** | §6–§9 | render 1080×1920, assemble the chosen variant, vision-review, hard QC gate |
| **Ship** | §10–§11 | deliver to Drive, log the Sheet row, report the link to the human |
| **Learn** | §Stats · §Feedback · §Analyze | scrape stats back, propagate GREEN feedback, mine performance |

`SE/...` = `engine/...`. All commands run **from the repo root**.

---

## 1 · Preflight

- **Inputs:** a working clone (see `SETUP.md`).
- **Command:**
  ```bash
  bash engine/qc/preflight.sh
  ```
- **Output:** `== preflight OK ==`. It checks `keys.env`, the Google service-account key, the CDP Chrome
  on `:9222` (launches the `~/.masquerade_chrome` profile if it is down), the Playwright install, and the
  bundled TikTok Sans fonts. **Abort on any `[FAIL]`.**
- **Tuning:** none — this is the environment gate. Missing pieces → `SETUP.md`.

## 2 · Claim the rotation slot

- **Inputs:** the character key (`ana` · `chloe` · `hannah`) + optional `--country` override.
- **Command:**
  ```bash
  python3 engine/sheets/sheets.py next-slot --character <key> [--country <Country>] --reserve
  ```
- **Output:** one line of JSON —
  `{"id": "<prefix-NN>", "framework": "A|B|C1|C2", "variant": "human|nohuman", "country": "...", "copy_iteration": N, "reserved": true}`.
  Everything downstream keys off these five fields.
- **How the slot is derived (never stored — computed live from the Sheet):**
  - `framework` cycles **A → B → C1 → C2** by the count of this character's framework-bearing rows.
  - `variant` alternates **per (account, framework)** from the framework default (**A/B/C1 → human,
    C2 → nohuman**): even prior count → the default, odd → the other. This is the **human-vs-nohuman A/B
    test** — the same account posts both over time.
  - `copy_iteration` = the number of prior (framework, country) packs across all accounts + 1 (drives the
    `copy_bank` freshness rule in §4). Iteration 0 in `copy_bank` is the unposted fixtures; the first real
    pack is iteration 1.
- `--reserve` appends an atomic **`(building)`** stub row so a teammate running `next-slot` a moment later
  rotates *past* your slot. **An aborted build leaves that stub** — free the number + slot again with:
  ```bash
  python3 engine/sheets/sheets.py post-delete --character <key> --id <prefix-NN>
  ```
- **Tuning:** the rotation is the durable 2.0 spec (`content_frameworks.md`); do not add a local counter.

## 3 · Human-variant prerequisite (scene photos)

- **Inputs:** the `variant` from §2. **Only when `variant == human`.** A `nohuman` slot skips this stage.
- **What is required:** the chosen character's clean scene photos at **`chars/<key>_cover.png`** and
  **`chars/<key>_ending.png`** (no text — the renderer lays text over them). Status today:
  - **Chloe** — present (`chars/chloe_cover.png`, `chars/chloe_ending.png`). Ready.
  - **Ana · Hannah** — **pending.** Their `character/<Name>/Base References/` (the locked identity) exist,
    but their `chars/` scene photos do not yet. A `human` slot for Ana or Hannah is **blocked** until you
    generate them.
- **Command (generate the missing scene photos — persona-gen chain, one bash call so the Stop hook does
  not quit Chrome mid-run):** follow the `new-character` skill's final step and
  `knowledge/realism/persona_gen_prompt_reference.md` (the locked recipe) + `winning_prompts.md` (reuse the
  closest banked winner). Stage the Base References, attach a real sourced background, generate a
  candid cover scene + ending scene, QC against `realism_book.md` D1–D6, save to `chars/<key>_cover.png` /
  `chars/<key>_ending.png`, then sync:
  ```bash
  python3 engine/qc/sync_media.py
  ```
- **Output:** `chars/<key>_cover.png` + `chars/<key>_ending.png` on disk and mirrored to Drive.
- **Tuning:** `knowledge/realism/*` (realism_book D1–D6, the locked recipe, the winners bank).

## 4 · Copy + caption + fact-check

- **Inputs:** the slot (§2). **Load before writing:** `CONTRACT.md` (§copy JSON schema + type system),
  `knowledge/frameworks/content_frameworks.md` (the option spec for this framework — hook titles, slide
  map, verbatim plug copy, hashtag + caption formula), `knowledge/copy_bank/<country>/<OPT>.md` (used
  angles — obey the freshness rule), `knowledge/tuning/06_performance.md` (what is winning),
  `knowledge/tuning/02_copywriting.md`, `knowledge/voice/humanizer.md`, and the live brand tab:
  ```bash
  python3 engine/sheets/sheets.py read --tab "Holicay Brand"
  ```
- **Write** `outputs/<key>/<ID - Title>/copy.json` — the schema is `CONTRACT.md §copy JSON schema`.
  **Lines arrive PRE-BROKEN** in every `lines[]` / `*_lines[]` / `paragraphs[]` array; the renderer
  **never re-wraps**, so break on natural phrase boundaries yourself.
- **Caption** → `caption.txt`: line 1 = the **hook title verbatim**, then an essay **one paragraph per
  slide**, then the hashtag formula `#{country}travel #{country}tips #travel{country} #{country}trip
  #{country}`. **C1 exception:** the comment-keyword CTA (`comment "{COUNTRY}" and i'll send you the full
  itinerary`) is the **first body line**, under the title.
- **Fact-check** every price / hour / closure / transit rule against the **primary source** (the venue's
  or operator's own site) via `WebSearch` + `WebFetch` — never a listicle. Opinions ("overrated") are
  judgment calls, not fetched, but **anchor each to a verified fact**.
- **Flag** what you could not verify → `outputs/<key>/<ID - Title>/flags.md` (verbatim-vs-drafted +
  unverified items), following the `fixtures/flags.md` pattern. Nothing unverified is buried in the copy.
- **Freshness / paraphrase (copy_bank rule):** the next iteration for the same country × framework must
  use **new angles / places** unless the run explicitly says `same`; when reusing a pack across accounts,
  **paraphrase** (same places, reworded lines) rather than shipping identical text.
- **Output:** `copy.json` + `caption.txt` + `flags.md`.
- **Tuning:** `02_copywriting.md`, `voice/humanizer.md`, `content_frameworks.md §Sourcing the copy`.

## 5 · Source + curate photos

- **Inputs:** the `copy.json` photo slugs (`scenic_photo`, `top_photo`, `bottom_photo`, `photo`, `cells`,
  `icons`). **Plan the slugs first** in the `fixtures/places.json` shape (slug → subject, category, query,
  geometry).
- **Source** (Google Places user photos are the **prioritized** UGC source per `CONTRACT.md` Gate 9):
  ```bash
  python3 engine/source/brightdata.py places --query "<venue>" --subject <country/city> --category <visit|eat|shop|...> --download 4 --gl <cc>
  python3 engine/source/brightdata.py gimg   --query "<specific shot>" --subject <country/city> --download 3
  python3 engine/source/brightdata.py ig     --query "<hashtag|venue>" --subject <country/city> --category <cat> --download 5
  ```
  **C2-only** helper assets:
  ```bash
  python3 engine/source/app_icons.py "DeepL" "Google Translate"      # real app icons -> media/graded/app_<slug>.png
  node    engine/source/route_map_shot.js                            # the pinned route map -> media/graded/route_map.png
  ```
  Downloads land in `media/library/<subject>/` and auto-append attribution rows to `media/manifest.json`.
- **Curate by VISION against `CONTRACT.md` Gate 9 (UGC-framing):** every **body** photo must read as a
  real visitor's handheld phone shot. Reject drone/aerial, tripod long-exposure, editorial symmetry,
  HDR-postcard grades, anything staged. Prefer a UGC frame over a Google-Images one when both pass.
  **Postcard exemption:** the scenic **cover / ending** photos and the **A / B / C2 plug `bg_photo`
  scenic** are decorative brand backdrops — exempt from Gate 9.
- **Install each pick with the `install` verb** (copies the file to `media/graded/<slug>`, writes the
  slug-keyed manifest row with attribution carried over, records `used_in`, and deletes the library
  file + its raw row — the hygiene prune is built in):
  ```bash
  python3 engine/source/brightdata.py install --from "media/library/<subject>/<id>.jpg" --slug <slug> --used-in <post-id>
  ```
  Reusing an already-graded asset (e.g. a Gate-9-exempt scenic)? Record it:
  ```bash
  python3 engine/source/brightdata.py install --slug <slug> --used-in <post-id>
  ```
  After all picks are installed, delete any leftover unpicked files under `media/library/` **and their
  raw manifest rows** (the library is scratch, not an archive; a raw row whose file is gone must not
  linger). Then write the per-post **`outputs/<key>/<ID - Title>/sources.md`** in the
  `media/PHOTO_SOURCES.md` row format (`NN slug — KEPT|REPLACED — platform — author — source_url — note`).
  Gotchas: `--subject japan/tokyo` creates the folder `media/library/japan-tokyo/` (the `/` flattens to
  `-`); downloads enforce a **≥700px short-side floor** — expect a chunk of gimg candidates to be
  rejected (`too_small`/`undecodable`/fetch-failed); if a subject yields 0 usable frames, retry with an
  alternate query or fall back to `places` / `ig`.
- **Output:** `media/graded/<slug>.jpg` for every slug + `sources.md` + confirmed manifest rows.
- **Tuning:** `knowledge/tuning/03_sourcing.md`, `knowledge/frameworks/photo_sourcing.md`,
  `engine/source/SOURCING_STATUS.md` (live backend status), `CONTRACT.md` Gate 9.

## 6 · Render

- **Inputs:** `copy.json` (§4) + `media/graded/` (§5) + `chars/` (§3).
- **Command:**
  ```bash
  node engine/render/build.js --copy "outputs/<key>/<ID - Title>/copy.json" \
       --out "outputs/<key>/<ID - Title>/_work/render" --contact
  ```
  (`--media` / `--chars` default to `media/graded` + `chars/`; pass them only to override.)
- **Output:** every slide at **1080×1920** under `_work/render/`. Cover + save render **twice** —
  `NN_cover_human.png` / `NN_cover_nohuman.png` (and the save slide likewise); `--contact` also writes
  `_work/render/_contact.png`, the labeled review montage.
- **Tuning:** `CONTRACT.md §Type system` + the framework's own design block. Templates + type scale are
  **locked** — do not edit `build.js`.

## 7 · Assemble the chosen variant

- **Inputs:** `_work/render/` + the `variant` from §2.
- **Do:** copy the **chosen variant's** cover + save into `final/` with the **variant suffix stripped**,
  and copy every body slide across unchanged, so `final/` holds exactly one contiguous `NN_<role>.png`
  per `copy.json` slide (e.g. `variant=human` → `_work/render/01_cover_human.png` becomes
  `final/01_cover.png`). Keep `caption.txt` alongside.
- **Output:** `outputs/<key>/<ID - Title>/final/NN_<role>.png` (the deliverable) + `caption.txt`.
- **Tuning:** naming spec = `CONTRACT.md §Canvas + naming`.

## 8 · Vision-review the contact sheet

- **Inputs:** `_work/render/_contact.png`.
- **Do:** `Read` the contact sheet and check it against **`CONTRACT.md` QC gates 1–8** — canvas + centered
  text, per-line hugging boxes (no full-width bars), no broken orphan-word boxes, C1 divider name legible
  on the seam, C2 pills + rounded font, split ❌/✅ over the right halves, the plug's specced treatment,
  emoji + fonts actually loaded (no tofu / fallback serif). Fix copy or photos and re-render (§6) on any
  miss. This is the vision half QC that the mechanical gate cannot do.
- **Output:** a deck that passes gates 1–8 by eye.
- **Tuning:** `CONTRACT.md §QC gates`.

## 9 · Hard QC gate

- **Inputs:** the assembled post folder + its framework.
- **Command:**
  ```bash
  node engine/qc/qc_gate.mjs "outputs/<key>/<ID - Title>" --framework <A|B|C1|C2>
  ```
- **Output:** JSON `{pass, ok[], warn[], issues[]}` + human-readable lines. **Exit 0 = pass · 1 = fail ·
  2 = bad usage.** It checks copy.json parses + matches `--framework`, `final/` names + count + contiguity
  vs `copy.json`, every PNG exactly 1080×1920, `caption.txt` non-empty and **dash-free**, `flags.md`
  present, and that every slug resolves under `media/graded` (mockup: graded or brand) with a manifest row
  (char photos under `chars/`). **Never skip it; fix until exit 0.**
- **Tuning:** the gate encodes `CONTRACT.md §QC gates` — a failure means the deck, not the gate, is wrong.

## 10 · Deliver to Drive + log the Sheet

- **Inputs:** a green post folder.
- **Commands:**
  ```bash
  python3 engine/drive/drive_sync.py --post "outputs/<key>/<ID - Title>" --character <key> --platform Tiktok
  python3 engine/sheets/sheets.py post-upsert --character <key> --id <prefix-NN> \
    --title "<Title>" --folder "<Drive link>" --caption "<caption.txt contents>" \
    --country "<Country>" --framework <OPT> --variant <human|nohuman> --iteration <N> \
    [--notes "<context for the human>"]
  ```
  `drive_sync --post` uploads `final/*.png` + `caption.txt` + `copy.json` + `flags.md` + `sources.md` and
  **prints the Drive folder link** (paste it into `--folder`). Then **append the `iteration N` entry** to
  `knowledge/copy_bank/<country>/<OPT>.md` (newest at the bottom).
- **Output:** the post on Drive under `<Character>/Tiktok/<ID - Title>/`, the Sheet row filled (the
  `(building)` stub is upserted in place), and the copy_bank history advanced.
- **Note:** delivery + logging **auto-run on completion** (no manual go-ahead) — the Drive folder + Sheet
  are the review surface, and the human still posts to TikTok, so this is not auto-publishing. Sweep any
  built-but-undelivered post with `python3 engine/sheets/sheets.py deliver-missing`.

## 11 · Report to the human

- **Do:** hand back the **Drive folder link** + a one-line summary (id · framework · variant · country).
  **Silence = approved.** Feedback → regen from the affected stage **and** propagate the lesson
  (§Feedback). Then quit Chrome if any CDP work ran:
  ```bash
  bash engine/lib/quit_chrome.sh
  ```
- **Output:** the human reviews on the Sheet + Drive, posts to TikTok manually, and leaves GREEN feedback.

---

## Stats — scrape performance back

For a character **with a `tiktok` handle** in `state.json` (Ana, Chloe; Hannah pending):
```bash
node engine/scrape/tiktok_profile.js <key>                 # harvest the profile's post URLs + stats
node engine/scrape/tiktok_login.js --open                  # only if views come back blank (login-gated)
python3 engine/sheets/sheets.py post-stats --character <key> --all   # write scraped rows (needs Post Link)
node engine/scrape/tiktok_stats.js "<post url>"            # one post, one-line JSON
bash engine/lib/quit_chrome.sh                             # always, when CDP work is done
```
Match Sheet rows by **Post Link**; backfill a missing Post Link by caption match first. **Views are
login-gated** — TikTok only hydrates them via the `/api/item/detail/` XHR when the masquerade Chrome is
logged in. Anything the scraper can't reach → `post-set --character <key> --id <prefix-NN> --views ... `.
Then eyeball the Dashboard / `python3 engine/sheets/sheets.py stats-summary`. Full sequencing:
`scrape-stats` skill.

## Feedback — propagate the GREEN cells

GREEN cells are the human's review channel (each fact tab's **Human Feedback** column + the **Connectors**
and **Holicay Brand** Notes columns). Poll → classify → edit the ONE governing doc → log → clear:
```bash
python3 engine/sheets/sheets.py feedback-poll
python3 engine/sheets/sheets.py feedback-clear --tab <ana|chloe|hannah|brand|connectors> --id <id> --note "what I changed"
```
Route each item to its single home and append the verbatim item + destination to
`knowledge/tuning/propagation-log.md` (newest at the **bottom**). A one-off fix is a **regen** (re-run the
affected stage), not a fake lesson. Full routing table + discipline: `propagate-feedback` skill.

## Analyze — the periodic learning pass

Read-only over the data; **proposes**, never silently writes:
```bash
python3 engine/sheets/sheets.py stats-summary --json
python3 engine/sheets/sheets.py read --tab <Ana|Chloe|Hannah>
```
Join stats to frameworks / variants / countries / copy angles, rewrite
`knowledge/tuning/06_performance.md` (evidence = post IDs), and PROPOSE any `CONTRACT` / frameworks edits
to the human. The **human-vs-nohuman verdict** lives here. Full method: `analyze` skill.

---

## Guardrails (the single source of truth — never violate)

- **Posting is ALWAYS manual.** Never automate TikTok posting. Delivery to Drive + logging the Sheet
  auto-run on completion (the review surface); the human posts to TikTok. **Silence = approval.**
- **Never skip `qc_gate.mjs`.** A draft ships only at exit 0.
- **No em/en dashes anywhere** in captions or on slides. (Docs may use them; post copy never does.)
- **UGC Gate 9 on every body photo** — real-visitor handheld framing; reject drone / tripod / editorial /
  HDR-postcard / staged. Scenic covers, endings, and the A/B/C2 plug `bg_photo` are the only exemptions.
- **Plug copy is verbatim** from `content_frameworks.md` — the lowercase, emoji, and casual misspellings
  ("alot", "revisted") are the voice; never clean them up.
- **Lines arrive pre-broken** in `copy.json`; the renderer never re-wraps. Break on phrase boundaries.
- **GREEN cells belong to the human** — read and clear only; never write into them.
- **Always `bash engine/lib/quit_chrome.sh`** after any CDP work (cover gen / scraping). A Stop hook runs
  it every turn as a safety net; non-Claude agents run it by hand.
- **Abandoned `(building)` reserve rows → `post-delete`** so the number + rotation slot free up.
- **Media hygiene:** prune `media/library/` after picks — the `install` verb does file + manifest row
  together; if you ever prune by hand, delete the orphaned raw manifest rows too. **Drive is canonical
  for media; git for code + docs.** The durable footprint is `media/graded/` + `chars/` +
  `media/brand/` + `manifest.json` (one slug-keyed row per kept asset).
- **Never nest this repo inside another git repo** — credential discovery walks up to the `.gitignore`
  sentinel, so a parent repo would break `keys.env` / Playwright resolution.
- **Don't edit `engine/`** (finished + verified) or the locked `CONTRACT.md` / `content_frameworks.md`
  design spec as a side effect of a post — those change only through `propagate-feedback` / `analyze` with
  human sign-off.
