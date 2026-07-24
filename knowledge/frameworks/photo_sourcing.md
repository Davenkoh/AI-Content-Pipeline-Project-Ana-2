# Photo sourcing + reusable media library (Bright Data)

> **Status: IMPLEMENTED.** The operative truth is the standalone CLI `engine/source/brightdata.py`,
> with [`engine/source/SOURCING_STATUS.md`](../../engine/source/SOURCING_STATUS.md) tracking live
> backend status (which sources work today, which need a human unlock). This doc is the **design
> rationale** behind the frameworks' real-UGC body-slide photos
> ([CREATIVE.md](../../CREATIVE.md) §Photo direction + [DESIGN.md](../../DESIGN.md) Gate 9): the library keying, the manifest schema,
> and the rights posture. A `BRIGHTDATA` token in `keys.env` unlocks the Bright Data backends (the
> account/token is the human's to create); Google Places / Google Images / Instagram work today
> without it (see SOURCING_STATUS.md).

## Why

The frameworks want body-slide photos that look like **a real person took them**, not stock. Licensed
stock alone (Pexels / Unsplash) and generic Bing results don't carry that "real visitor" look, and
re-sourcing every post from scratch is wasteful. `engine/source/brightdata.py` adds the **UGC sources**
(Instagram, Google Images, Google Maps reviews, and Google Places user photos), and a **reusable,
place-keyed library** makes it cheap and consistent — you pay once per place, then reuse.

## 1. The sourcing backends (standalone `brightdata.py`)

`engine/source/brightdata.py` is a **standalone sourcing CLI** — a per-source dispatcher
(`brightdata.py <backend> --query … --subject … --download N`), not a set of backends bolted onto an
older sourcer. Each backend returns `[{thumb, full, w, h, source, source_url, author, license}]`:

| Backend key | Bright Data product | Fills |
|---|---|---|
| `ig` | Instagram Scraper (by hashtag / location / profile) | **real UGC — the net-new source** |
| `gimg` | SERP API (Google Images) | Google Images the engine can't reach today |
| `greviews` | Google Maps reviews scraper | real diner / visitor photos per venue (vs `places`' official shots) |
| (bytes) | Web Unlocker / residential proxy | robust image-byte fetch past 403 / hotlink |

- **Token:** `BRIGHTDATA` in `keys.env`, read via `_keys("BRIGHTDATA")` (same pattern as `PEXELS` / `SERP`).
- **Return shape:** add **`source_url`, `author`, `license`** on top of the existing fields — the library + attribution need them.
- **Cost:** Bright Data bills per record / request, so the library (below) is what keeps it economical — you pay **once per place**, then reuse.

## 2. The reusable library (place-keyed, shared)

Photos are keyed by **place, not post** — a Hanoi egg-coffee shot is reused by every Hanoi post.
Shared and character-agnostic (a place photo isn't Ana's or Chloe's). **Bytes live in Drive
(canonical) + local mirror** per the media policy — **not committed to git**; the **manifest is a
small git-tracked JSON index** (portability: a teammate pulls the repo, gets the whole index, and
resolves the bytes from Drive).

**Manifest entry:**

```json
{
  "id": "a1b2c3d4",
  "subject": "vietnam/hanoi",            // country/city (or venue)
  "category": "eat",                     // visit | eat | shop | matcha | nature | ...
  "query": "cafe giang egg coffee hanoi",
  "platform": "instagram",               // instagram|google_images|google_reviews|bing|pexels|unsplash|places
  "source_url": "https://...",
  "author": "@handle",                   // stored for attribution
  "license": "ugc-unlicensed",           // ugc-unlicensed | unsplash | pexels | places-tos
  "sha256": "...", "phash": "...",        // dedupe across re-encodes
  "w": 1440, "h": 1080,
  "drive_id": "...", "local_path": "...",
  "scraped_at": "2026-07-19",
  "used_in": ["ana/tt-21"]               // rotation: don't reuse the same frame across posts
}
```

**Cache-first flow (in `brightdata.py`):**

1. normalize `subject` + `category` → look up the manifest
2. **hit** → return those candidates (free, instant, zero Bright Data spend); prefer frames **not** in `used_in` (rotation, so two posts about the same place don't clone each other)
3. **miss** → run the backends (Bright Data etc.) → OODA-pick as today → **bank** the picks into the library + Drive + manifest
4. append the post code to the chosen assets' `used_in`

Dedupe on `sha256` + `phash` so the same photo pulled from IG and from Google doesn't double-store.

## 3. Rights posture — DECIDED: direct repost, attributed

**(2026-07-19)** Body-slide UGC is **posted as-is** for maximum authenticity. The library **records
`author` + `source_url` + `license` on every asset** so you can attribute, swap, or answer a takedown
later — but there is **no gating step and no pre-post approval**; the sourcer banks and uses UGC
automatically. This knowingly accepts the (common-in-travel-TikTok) rights exposure as a deliberate
call. Licensed sources (Unsplash / Pexels / Places) stay in the `order` as free, rights-clean
options, but UGC is **not** down-ranked for rights reasons.

## 4. Build checklist

The standalone CLI (`engine/source/brightdata.py`) is built; **`engine/source/SOURCING_STATUS.md`
holds the live status** of each backend (which run today, which need a human unlock). The design's
full intent:

- [ ] `BRIGHTDATA` token in `keys.env` (+ Drive `_setup` so the team gets it) — for the Bright Data backends only
- [ ] `engine/source/brightdata.py` — `ig()`, `gimg()`, `greviews()`, `unlock_fetch()`
- [ ] expose `ig` / `gimg` / `greviews` / `places` as `brightdata.py` subcommands; every backend returns `source_url` / `author` / `license`
- [ ] `engine/source/library.py` — manifest read/write, `sha256` + `phash` dedupe, cache-first lookup, `used_in` rotation
- [ ] Drive `Project Ana/Media Library/` + local mirror wired into the existing `sync_media.py` → `mirror-all`
- [ ] manifest JSON git-tracked; image bytes git-ignored (Drive-only)
