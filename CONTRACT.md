# Frameworks design sandbox — build contract

> **SANDBOX.** This directory is an isolated test bed for the self-governing content frameworks
> (`knowledge/frameworks/content_frameworks.md` — THE authority for every design decision here).
> Nothing in here touches the current system: **no edits to `engine/`**, no writes into `outputs/`,
> no Sheet logging, no Drive delivery, no `sync_media.py`. Reading/reusing existing repo assets
> (engine patterns, graded photos, Chloe images, shipped copy JSONs) is allowed and encouraged.
> If the test graduates, code moves out deliberately (photo sourcing → `engine/source/` per
> `knowledge/frameworks/photo_sourcing.md`).

## Test definition (from the human)

- Character for the human-in-post test: **Chloe** (Japan). Content country: **Japan**.
- For **each option (A, B, C1, C2)**: render the **cover and the ending slide in TWO variants** —
  `human` (Chloe in scene) and `nohuman` (pure scenic, same text treatment). Body slides render
  once (no person on body slides anyway).
  - For A/B/C1 the framework default is *human on first + last* → `nohuman` is the test variant.
  - For C2 the framework default is *faceless* → `human` is the test variant (the doc itself allows
    "swap that scenic hero for a character-in-scene cover instead").
- **The Holicay plug slide now has a real design (human steer 2026-07-23) — two treatments:**
  - **C1 plug (`mockup`) = the ✅ solution:** a framed phone screenshot of the **Holicay app**
    (rounded corners + white border + soft shadow), sized LARGE (~1162px tall, ~64% frame height)
    and centered on a **dark-tinted picturesque country scenic** (`bg_photo` + a ~0.45–0.62 black
    gradient tint so the white phone and text read on top with clear hierarchy). The plug's first
    paragraph is a sticker pulled in just above the phone and the comment-CTA sticker just below it
    (tight grouping, small gaps — not floating far in empty space). The app screenshot is a
    first-party brand asset (`media/brand/`); a flat coral gradient is only the fallback when no
    `bg_photo` is given.
  - **A / B / C2 plug (`bg_photo`) = the ❌ problem framing:** a **full-bleed picturesque country
    scenic** (decorative brand backdrop, EXEMPT from the UGC-framing gate — postcard shots are fine
    here) + a dark scrim, with the plug's `❌ i regret using… / ✅ HOLICAY.COM …game changer` sticker
    cluster centered over it. Pick a scenic distinct from that deck's cover/save photos.
  - Flat `#f2f2f2` is now only a fallback; nothing uses it.

## Directory map

```
sandbox/frameworks-test/
  CONTRACT.md          this file
  build.js             standalone renderer (playwright HTML→PNG), ALL templates
  copy/                A.json B.json C1.json C2.json places.json flags.md
  media/library/       sourced UGC, keyed by place:  <subject-slug>/<id>.jpg
  media/manifest.json  attribution index (shape below)
  media/graded/        render-ready picks (slug.jpg) referenced by copy JSONs
  chars/               chosen Chloe photos for covers/endings (copied from repo, clean/no text)
  tools/               brightdata.py (sourcing CLI), app_icons.py
  fixtures/            tiny per-template fixture JSONs used while building
  out/<OPT>/           rendered slides + _contact.png per option
```

## Canvas + naming

- **1080×1920 (9:16)** exactly — viewport AND screenshot clip. This overrides the engine's 1080×1440.
- Slide files: `NN_<role>.png` (`01_cover_human.png`, `01_cover_nohuman.png`, `02_body.png`, …,
  `10_save_human.png`, `10_save_nohuman.png`). NN = position in the deck, zero-padded.
- Every option dir also gets `_contact.png` — a labeled grid montage of the whole deck for review.

## Type system (from the doc — binding)

- **A / B / C1 text = bold TikTok Sans** — the real TikTok typeface (SIL OFL), bundled locally at
  `assets/fonts/` (`tiktok-sans.css` + the two woff2 subsets); Montserrat is only the network
  fallback in the stack.
- **C2 text = rounded bold sans — Nunito (Poppins fallback)**, its black step pills + white boxes.
- **Paragraph sticker (core component, v3 — human steers 2026-07-22/23):** the lines of ONE
  paragraph share ONE connected white shape — each line hugs its own width, lines stack flush.
  **Mechanism = TikTok's own:** measure each rendered line's width, then draw a single crisp
  outline path around the stack — convex corners ~15px, small CONCAVE fillets (~12px, capped at
  half the width step) where a shorter line meets a longer one, dead-flat edges everywhere else.
  NO blur/goo blobs, NO gray fringe — pure white, razor edges (calibrate against the human's
  pasted TikTok references). Clear gap (~16–24px) BETWEEN paragraphs; never one big rectangle;
  never separated floating per-line boxes within a paragraph. Black bold text.
- **Cover flag (v3):** `slide.flag` renders as a BARE drop-shadowed emoji overlapping the title
  sticker's top-left corner (peeking half above the box, per the kylie.nbt reference) — never
  boxed, never its own white chip, never inside the sticker layers.
- **Type scale (v3):** ~15% up from v2 — cover title ≈68 / subtitle ≈40, split title ≈58 / why
  ≈46, plug ≈46, save ≈84/42, C2 headline ≈58 / body ≈52 / tip ≈44. Auto-fit guard: a sticker
  that would overflow its zone (line wider than 1080−120, or cluster taller than its band)
  scales its font down uniformly — lines are NEVER re-wrapped.
- **Plug paragraph grammar (v3):** para 1 = the "i regret using…" hook line · ❌ mess statement =
  own para · "✅ HOLICAY.COM …game changer" = own short para · the how-it-works detail = own
  para · any CTA/aside ("(you should try it with this tiktok 😉)") = own para.
- **C2 tip slot:** only genuine "Tip:" insider notes ride the lower tip position; every other
  line is a body block in the mid cluster.
- **Outline text (the dial, v2):** `subtitle_style` / `title_style` = `"outline"` renders that text
  with NO box — bold TikTok Sans, white fill, thin black border (~3px stroke) + a soft shadow for
  legibility. Used at the orchestrator's discretion on cover subtitles and the B "am I right?"
  ending slide.
- Line breaks arrive **pre-broken** in the copy JSONs (`lines: [...]`) — the renderer must never
  re-wrap. Emoji render via native Apple Color Emoji.
- **Slide-copy rules (v2):** no sentence-final periods on slide text (C2's numbered pill prefixes
  like `1.` keep their dot); the brand is always written **HOLICAY.COM** on slides.
- **Text sits in the vertical middle** of the frame (safe from TikTok chrome). Exception: covers —
  title boxes **upper-middle** (≈22–30% down), subtitle box just under (see `inspo/29/1.jpg`).
- Body photos get a **subtle grade** in-template (slightly darker + desaturated, non-punchy): e.g.
  `filter: brightness(.92) saturate(.88) contrast(.98)` — tune by eye against inspo/29.

## copy JSON schema

Top level per option: `{option, hook:{title,subtitle}, hashtags:[...], caption:{title_line, body_draft}, slides:[...]}`.
`photo`/`cells` values are slugs resolving to `media/graded/<slug>.jpg`; `char_photo` resolves to `chars/<name>`.

Slide objects by `type`:

```
cover      {type, title_lines[], subtitle_lines[], char_photo, scenic_photo}       # render both variants
split      {type, x_title_lines[], x_why_lines[], check_title_lines[], check_why_lines[], top_photo, bottom_photo}   # A/B body
plug       {type, paragraphs[[lines],...], mockup?:<app-slug>, bg_photo?:<scenic-slug>}   # mockup=C1 app frame · bg_photo=A/B/C2 scenic · neither=flat fallback
save       {type, title:"SAVE THIS", subtitle:"just incase you need it ❤️", char_photo, scenic_photo}   # both variants
divider    {type, label, cells:[4 slugs]}                                           # C1: 2×2, lowercase white name on the seam
notes      {type, place, contd:bool, sections:[{emoji, header, items:[{text, gloss?}]}]}   # C1 listicle, Montserrat, Notes-look
step       {type, pill, layout:"photo"|"grid4"|"map"|"icons", photo|cells, blocks:[{lines[], size:"headline"|"body"|"tip"}], cell_labels?[{title_lines[], note_lines[]}]]}   # C2
favorites  {type, title_lines[], photo, cities:[{pill, lines[]}]}                   # C2 slide 5
```

## media/manifest.json (attribution — per photo_sourcing.md)

Array of: `{id, subject, category, query, platform, source_url, author, license, sha256, w, h,
local_path, scraped_at, used_in:[...]}`. Every sourced byte gets an entry — UGC is posted as-is
but attribution is always stored. `license: ugc-unlicensed | unsplash | pexels | places-tos | repo-graded`.
Photos reused from prior posts' `_work/graded/` pools get `platform:"repo-graded"` +
`source_url` pointing at the post dir.

**Media hygiene (human steer 2026-07-23): keep only what the final decks render.** Download
candidates into `media/library/<subject>/` while sourcing, but AFTER picks are approved, prune the
library — delete every candidate that is not the installed pick. The durable footprint is exactly:
`media/graded/<used slugs>` + `chars/<used>` + `media/brand/<first-party>`, with `manifest.json`
holding one attribution row per kept asset. `media/library/` is scratch, not an archive; do not
hoard unused downloads.

## QC gates (renderer + assembly must self-check against these before handing back)

1. Canvas exactly 1080×1920; text cluster centered vertically (covers: upper-middle).
2. Per-line hugging boxes — no full-width bars, no box wider than its line + padding.
3. No awkward orphan-word boxes (line breaks are content, but flag any that render badly).
4. C1 divider name legible on the seam (soft drop shadow; curation picks calm-center cells).
5. C2 pills top-center, body boxes mid-frame; rounded font everywhere on C2.
6. Split slides: ❌ pair reads over the TOP photo, ✅ pair over the BOTTOM, cluster on the seam.
7. Plug slides stay bare (placeholder rule above).
8. Emoji actually rendered (not tofu). Fonts actually loaded (not fallback serif).
9. **UGC-framing gate (human steer 2026-07-22):** every body photo must read as taken by a real
   visitor on a phone — eye-level or handheld, imperfect timing/composition welcome. REJECT:
   drone/aerial views, tripod long-exposures, editorial symmetry or perfectly-timed shots, HDR
   postcard grades, anything that looks professionally staged. **Google Images (SerpAPI) is a fine
   source when the shot makes sense** — a genuinely candid frame, or when no good UGC exists; UGC
   (Google Places user uploads / Instagram) is **prioritized, not mandatory**. Prefer a UGC frame
   over a Google-Images one when both pass, but a sensible Google-Images pick beats a weak UGC one.

> **These rules are the durable output spec.** Future framework posts must reproduce this exact
> system — templates, sticker mechanism, type scale, flag treatment, plug grammar, photo gates —
> with ONLY the copy content (and its sourced photos) changing per post.
