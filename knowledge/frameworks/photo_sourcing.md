# Photo sourcing + reusable media library (Bright Data)

> **Status: SPEC — not built yet.** Needs a Bright Data account + a `BRIGHTDATA` token in `keys.env`
> (the account/token is the human's to create). This is the **"how"** behind the frameworks'
> real-UGC body-slide photos ([content_frameworks.md](content_frameworks.md) §Design). It **extends**
> the existing sourcer, it does not replace it.

## Why

The frameworks want body-slide photos that look like **a real person took them**, not stock. The
current sourcer ([`engine/source/source.py`](../../engine/source/source.py)) already does
Pexels / Unsplash / Bing / Google-Places / SerpAPI, but it has **no Instagram**, **can't do Google
Images** (returns 502 without a JS render, so it falls back to Bing), and **re-sources every post
from scratch** (nothing is reused). Bright Data fills the source gaps; a **reusable library** makes
it cheap and consistent.

## 1. Bright Data = new backends (not a rewrite)

`source.py` already dispatches per-slug backends from an `order` list, each a
`from_X(query, n) -> [{thumb, full, w, h, source}]`. Add a `brightdata.py` (sibling of
[`scrape_do.py`](../../engine/source/scrape_do.py)) and wire in new backend keys:

| Backend key | Bright Data product | Fills |
|---|---|---|
| `ig` | Instagram Scraper (by hashtag / location / profile) | **real UGC — the net-new source** |
| `gimg` | SERP API (Google Images) | Google Images the engine can't reach today |
| `greviews` | Google Maps reviews scraper | real diner / visitor photos per venue (vs `places`' official shots) |
| (bytes) | Web Unlocker / residential proxy | robust image-byte fetch past 403 / hotlink (better than scrape.do's `fetch`) |

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

**Cache-first flow (inside `source.py`):**

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

- [ ] `BRIGHTDATA` token in `keys.env` (+ Drive `_setup` so the team gets it)
- [ ] `engine/source/brightdata.py` — `ig()`, `gimg()`, `greviews()`, `unlock_fetch()`
- [ ] wire `ig` / `gimg` / `greviews` into `source.py` dispatch + default `order`; add `source_url` / `author` / `license` to **every** backend's return
- [ ] `engine/source/library.py` — manifest read/write, `sha256` + `phash` dedupe, cache-first lookup, `used_in` rotation
- [ ] Drive `Project Ana/Media Library/` + local mirror wired into the existing `sync_media.py` → `mirror-all`
- [ ] manifest JSON git-tracked; image bytes git-ignored (Drive-only)
