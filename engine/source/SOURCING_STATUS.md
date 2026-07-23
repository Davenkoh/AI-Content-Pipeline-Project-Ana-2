# Photo sourcing — what works now, and the exact clicks Bright Data still needs

*Plain-language status for the 2.0 photo-sourcing backends. Last checked: 2026-07-22 (in the 1.0
sandbox; the backends are unchanged).*
*All commands run from the repo root. Photos land in `media/library/<place>/` (note: a `/` in
`--subject` flattens to `-` in the folder name) and every download is logged (author + source link)
in `media/manifest.json` automatically. Downloads enforce a **≥700px short-side floor** — on Google
Images expect a decent share of candidates to bounce (`too_small` / `undecodable` / hotlink-blocked);
a subject that yields 0 usable frames usually needs an alternate query or the `places`/`ig` backend.
Promote a pick to a render slug with `install` (see WORKFLOW §5).*

---

## TL;DR

| Source | Status | Needs a human? |
|---|---|---|
| **Google Places user photos** | ✅ **Works now** — best "real visitor took this" framing | No |
| **Instagram posts (Apify)** | ✅ **Works now** — real people's posts by #hashtag/venue; net-new UGC source | No |
| **Google Images (SerpAPI)** | ✅ **Works now** — good for specific/messy searches | No |
| **Bright Data — Google Maps reviews** | 🟡 Account is **already enabled** & code is wired; the crawler is currently flaky (Google sign-in wall) | No unlock — just reliability tuning |
| Instagram posts — Bright Data | ⚪ **Optional alternative** to Apify — code is wired (`ig-bd`) but BD gates social data behind KYC | Only if you want BD instead of Apify |
| Bright Data — SERP / Web Unlocker "zones" | ⚪ Not set up (optional; SerpAPI already covers Google Images) | Optional |

**Two sources give the "real visitor took this" look with zero human setup: Google Places user photos
and Instagram posts (via Apify).** Places photos are predominantly uploaded by real visitors (handheld,
eye-level, imperfect — the opposite of the "professional drone shot" look we rejected). Instagram adds
real people's *posts* for a place or vibe — but IG mixes in influencer-polished shots, business promo
graphics and collages, so IG results **must** be curated against QC gate 9 (see the honest read below).

---

## 1. What works RIGHT NOW

### A. Google Places user-review photos  ← use this first
Real photos that visitors uploaded to a place's Google listing. No Bright Data needed.

```
python3 engine/source/brightdata.py places --query "Shibuya Sky" --subject japan/tokyo --category visit --download 4 --gl jp
```

- `--query` = the venue name, `--subject` = the library folder (country/city), `--download` = how many to save.
- It finds the place, pulls its visitor photos at 1600px, skips obvious owner/official shots, and saves the
  rest with the uploader's name + profile link recorded for attribution.
- Verified 2026-07-22 on **Shibuya Sky** and **Ichiran ramen Shibuya**: downloaded real user shots — an
  observation-deck view with the deck floor & safety net in frame, a ramen bowl with the diner's own Coke
  can, glasses and earbuds on the counter. Exactly the UGC look we want.
- One known limit: an owner photo whose uploader name is in a different script than the place name (e.g. a
  Japanese store name vs the romanized place) can slip through. The uploader name is saved in the manifest,
  so it's easy to spot and swap.

### B. Google Images (via SerpAPI — your existing SERP key)
Best when you need a very specific or "messy" shot that isn't tied to one venue.

```
python3 engine/source/brightdata.py gimg --query "omoide yokocho yakitori alley night" --subject japan/tokyo --download 3
```

### C. Instagram posts (via Apify)  ← net-new "real people's posts" UGC
Real Instagram posts for a place or a vibe. Uses **Apify** public actors (not Bright Data — see §2 for
why). Works today on our Apify token; no verification step.

```
python3 engine/source/brightdata.py ig --query "shibuyasky" --subject japan/tokyo --category visit --download 5
```

- `--query` is a **#hashtag / single word** (e.g. `shibuyasky`, `ichiran`) or a **venue name** (e.g.
  `"Shibuya Sky"`). A single word or `#tag` → hashtag search; a multi-word venue → the same hashtag
  search on the venue's squished name (`Shibuya Sky` → `#shibuyasky`). Override with
  `--mode hashtag|place|url|user`.
- `--mode url --url "https://www.instagram.com/p/XXXX/"` pulls specific **post(s)**; `--mode user
  --query <handle>` pulls a **profile's** recent posts.
- It saves the post's photo(s) into `media/library/<subject>/`, recording the poster's **@handle** and
  the **post URL** for attribution — same as every other source. **Images only** (Reels/videos are
  skipped); carousels contribute their first 1–2 frames (`--frames`, default 2).
- `--n` caps how many posts to scrape (default 12, hard-capped at 50 for cost); `--download K` saves
  the first K usable images.

**Honest read on IG framing (curate against QC gate 9).** Verified 2026-07-22 across three queries,
5 downloads each:
- **`ichiran`** — cleanest. All 5 were genuine diner POV/overhead ramen shots (branded bowl, chopsticks,
  the counter's order card) — textbook food UGC. A specific dish/venue hashtag gives the best signal.
- **`shibuyasky`** — 3/5 candid (a family on the deck ×2, the classic look-straight-down-at-Shibuya-
  Crossing POV through the glass); 2/5 were influencer-polished posed portraits of the same creator.
- **`shimokitazawa`** — messiest. 2 clean (foodie-polished) ramen bowls, 1 excellent candid café scene
  (matcha waffle + iced drinks + K-pop photocards), but **1 event-promo poster** (a business account)
  and **1 picture-in-picture collage** — both must be rejected. A broad neighborhood hashtag drags in
  promo graphics and collages.
- **Takeaway:** IG is a strong *venue/vibe* photo source **alongside** Places, but it is NOT
  pre-filtered — the scraper returns raw hashtag posts. Prefer specific venue/dish hashtags over broad
  area names, and always run the results through gate 9 (reject influencer-staged shots, promo graphics,
  and collages). The manifest records the @handle so pro/business posters are easy to spot.

---

## 2. Bright Data — exactly what to click

**What I found when I tested the Bright Data account on 2026-07-22** (token read from `keys.env`, never
printed):

- The account is **active and can already run "collection" jobs** — I triggered a **Google Maps reviews**
  job and it ran to completion (no billing/verification error).
- **Instagram is blocked on Bright Data.** Triggering BD's Instagram scraper returns, word for word:
  > `HTTP 400  —  Customer is not active`
  Google Maps reviews works but Instagram doesn't, on the same account at the same moment. That pattern is
  Bright Data's **compliance / KYC gate for social-media data** (Instagram, Facebook, TikTok, LinkedIn are
  gated; business data like Google Maps is not). **This is why Instagram is sourced via Apify (§1C)
  instead** — Apify has no such gate, so IG works today with zero setup.
- There are **no "zones"** configured (the account status literally says `zone_not_found`). Zones are only
  needed for Bright Data's *own* Google Images (SERP) and proxy fetching — we don't need those because
  SerpAPI already covers Google Images. So this is optional.

### ➤ (Optional) Bright Data Instagram — only if you'd rather use BD than Apify

**You don't need this.** Instagram now works today via **Apify** (§1C) with no verification. Keep this
path only if you specifically want Bright Data's Instagram dataset instead. The code is still wired as the
**`ig-bd`** subcommand. To unlock it on this BD account:

1. Go to **brightdata.com** and log in.
2. Make sure a **payment method** is on file: left sidebar → **Billing** → **Payment methods** → add a card.
   (Collection is billed per record — see costs below.)
3. Complete **KYC / compliance verification**: look for a **"Complete verification"**, **"Compliance"**, or
   **"KYC"** prompt — usually in the top-right account menu or under **Account settings → Compliance**.
   Bright Data requires this specifically to allow **social-media** datasets. Fill in the business details and
   the use-case it asks for.
4. **Submit and wait for approval.** This is a manual review by Bright Data (typically a few hours to a couple
   of business days) — it is not instant.
5. When it's approved, test it:
   ```
   python3 engine/source/brightdata.py ig-bd --url "https://www.instagram.com/p/XXXXXXX/" --subject japan/tokyo --download 3
   ```
   - If it prints image-download lines → **unlocked**.
   - If it still says `Customer is not active` → verification isn't approved yet; wait and retry.

   *(I couldn't see the exact verification screen through the API, so the menu wording in step 3 may differ
   slightly — look for anything named verification / compliance / KYC.)*

### ➤ Google Maps reviews (already runs — only reliability to tune)

- **No unlock needed.** The job triggers and runs on the current account today. The backend is wired
  (`greviews` command below).
- **Current snag:** the Google Maps crawler intermittently hits a Google **"Sign in"** wall that hides the
  reviews. The exact error I captured was:
  > `Crawler error: Sign in modal hides the Reviews`

  Some runs also come back with no reviews. Retrying, or feeding a cleaner Google Maps place URL, usually
  gets past it. If it stays flaky, **Google Places user photos (section 1A) already covers the same need.**
- Command (resolves the venue automatically, then collects):
  ```
  python3 engine/source/brightdata.py greviews --place "Shibuya Sky" --subject japan/tokyo --download 3
  ```

### ➤ (Optional) SERP + Web Unlocker zones

Only if you ever want Bright Data's own Google Images or proxy byte-fetch (we don't, today):
brightdata.com → left sidebar **Proxies & Scraping Infrastructure** → **Add zone** → pick **SERP API**
and/or **Web Unlocker** → save. Then re-run `python3 engine/source/brightdata.py probe`.

---

## 3. Roughly what it costs

- **Apify Instagram (§1C — our IG source):** the actors (`apify/instagram-hashtag-scraper`,
  `apify/instagram-scraper`) are **pay-per-result**, Apify's published rate ≈ **$2.30 per 1,000 posts**
  scraped (≈ $0.0023/post). **Measured 2026-07-22:** the three 5-download test runs (scraping ~8 posts each)
  cost about **$0.02 each**; the whole build+test session — every probe, all three downloads, plus the
  url/place checks — came to **≈ $0.08 total**. Our token is on Apify's **FREE plan: $5 of free credits
  per month** (usage capped at $30), so light sourcing is effectively free. `--n` is hard-capped at 50
  posts/run to keep any single job cheap. Downloading the image bytes from Instagram's CDN is free.
- **Bright Data Web Scraper (`ig-bd`, Google Maps reviews):** Bright Data's published pay-as-you-go
  price is about **$1–$1.50 per 1,000 records** (≈ $0.0015 per photo/review), and cheaper at volume. Confirm
  the exact number on your dashboard's pricing page — it depends on your plan.
- **Google Places photos (section 1A):** billed by Google, not Bright Data — Text Search ≈ $32 / 1,000,
  Place Details ≈ $17 / 1,000, Photos ≈ $7 / 1,000 — **but Google includes a large monthly free credit**, so
  light sourcing is effectively free.
- **SerpAPI Google Images:** whatever your existing SerpAPI plan charges per search.

Because photos are saved to a reusable library keyed by place, you pay **once per place** and reuse it across
every post about that place.

---

## 4. Where each source stands now

- **Instagram (`ig`, via Apify): working today** — no unlock, no verification. Returns real people's posts
  by hashtag/venue/profile. It is a strong primary **venue/vibe** photo source alongside `places`, but its
  results are **not pre-filtered** — always curate against QC gate 9 (reject influencer-staged shots, promo
  graphics, collages). Prefer specific venue/dish hashtags (e.g. `#ichiran`) over broad area names.
- **Bright Data Instagram (`ig-bd`): optional.** Only needed if you'd rather use BD than Apify; still gated
  behind BD's KYC (§2). The code is wired and will start returning photos the moment that flag flips.
- **Google Maps reviews (`greviews`)** already runs and is wired; only crawl-reliability remains to tune.
- **Google Places (`places`)** and **Google Images (`gimg`)** work today with zero setup (§1A, §1B).
