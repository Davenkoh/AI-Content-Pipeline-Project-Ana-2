# CONNECTORS — the credential + billing registry

Every external service Project Ana 2.0 touches: what it does, how it authenticates, whose account it is,
its console, its cost, its status, and how to rotate or fix it. This **mirrors the Sheet's Connectors
tab** (seeded by `python3 engine/sheets/sheets.py connectors-init`) — that tab is the live copy, and its
**Notes column is the human's GREEN channel** for connector issues (poll + clear it via
`propagate-feedback`). Re-running `connectors-init` refreshes the reference columns but **preserves
Status + Notes**.

## The registry (13 connectors)

| Connector | Purpose | Auth (env var / file) | Account / identity | Console | Plan & cost | Status |
|---|---|---|---|---|---|---|
| **Pexels** | photo search | `keys.env` `PEXELS` | Pexels API account | pexels.com/api | free | legacy · optional |
| **Unsplash** | photo search | `keys.env` `UNSPLASH` | Unsplash developer account | unsplash.com/developers | free | legacy · optional |
| **SerpAPI** | Google Images (`brightdata.py gimg`) | `keys.env` `SERP` | SerpAPI account | serpapi.com | paid per-search | ACTIVE |
| **Google Places** | user photos + Maps Embed route shots | `keys.env` `PLACES` | `creators@holicay.com` (the GCP project of that key) | console.cloud.google.com | billed to that key's GCP project | ACTIVE — primary UGC source |
| **scrape.do** | proxy fallback | `keys.env` `SCRAPE_TOKEN` | scrape.do account | scrape.do | free tier | legacy · optional |
| **Bright Data** | `greviews` backend | `keys.env` `BRIGHTDATA` | Bright Data account | brightdata.com | pay-as-you-go | PARTIAL — Google-reviews flaky, Instagram KYC-blocked |
| **Apify** | Instagram UGC (`brightdata.py ig`) | `keys.env` `APIFY` | Apify account | console.apify.com | FREE plan, $5/mo credit | ACTIVE — the working IG backend |
| **Google service account** | Sheets read/write + Drive reads | `holicay-*.json` at repo root | `holicay-message-machine@holicay-402208.iam.gserviceaccount.com` (GCP **holicay-402208**) | console.cloud.google.com | free | ACTIVE — share the Sheet/Drive with this email |
| **Google OAuth Drive client** | Drive uploads/creation as `creators@holicay.com` | `client_secret*.json` + per-user `drive_token.json` | `creators@holicay.com` (GCP **masquerade-2** — a DIFFERENT project than the SA) | console.cloud.google.com | free | ACTIVE |
| **ChatGPT** | character/cover image gen via logged-in browser (**NO API key**) | `~/.masquerade_chrome` CDP profile | that ChatGPT account | chatgpt.com | per that account's plan | ACTIVE — re-login in the masquerade Chrome when gens fail |
| **TikTok** | stats scraping via logged-in browser (same profile) | `~/.masquerade_chrome` CDP profile | @solo.with.ana / @chloe.belletravel | tiktok.com | free | ACTIVE — views login-gated; re-auth `tiktok_login.js --open`. **Per-account logins/VPN/Gmail live on the Sheet's Accounts tab.** |
| **GitHub** | code home | `gh` CLI | Davenkoh | github.com/Davenkoh/Project-Ana-2 | free | ACTIVE |
| **iTunes Search API** | real app icons (`app_icons.py`) | keyless | — | — | free | ACTIVE |

## Things to know (the traps)

- **TWO separate Google Cloud projects.** The **service account** (Sheets + Drive reads) is in project
  **holicay-402208**; the **OAuth Drive client** (uploads as `creators@holicay.com`) is in project
  **masquerade-2** — legacy, but working. They are not interchangeable; a new machine needs *both* the SA
  key (`holicay-402208-*.json`) and the OAuth client (`client_secret*.json` → mint `drive_token.json`).
- **ChatGPT + TikTok are BROWSER LOGINS, not API keys.** They live in the `~/.masquerade_chrome` CDP
  profile — there is nothing in `keys.env` for them. If image gen or stats fail, the fix is usually to
  re-login in that Chrome (`bash engine/qc/preflight.sh` launches it; `tiktok_login.js --open` re-auths TikTok).
- **`keys.env` at the repo root holds the 7 API keys:** `PEXELS UNSPLASH SERP PLACES SCRAPE_TOKEN
  BRIGHTDATA APIFY`. It is gitignored; it is distributed via Drive `_setup/`.
- **Apify is on the FREE plan — $5/mo of credit** (usage capped). Light IG sourcing is effectively free
  (measured ~$0.02 per 5-download run), but a heavy run could exhaust it; `--n` is hard-capped at 50 posts/run.
- **Bright Data Instagram needs KYC** (compliance verification for social-media datasets) and is currently
  blocked ("Customer is not active"). **Apify covers Instagram**, so you do not need to unlock it. Bright
  Data's Google-reviews backend runs but is flaky (Google sign-in wall); Google Places (`places`) covers
  the same need. Full status + the exact unlock clicks: `engine/source/SOURCING_STATUS.md`.
- **Secrets distribution = Drive `_setup/`** (privately shared, manual download — never scripted, never
  "anyone with the link"). See `SETUP.md` step 2.
- **The Connectors tab Notes column is GREEN** — the human writes connector problems there; the agent polls
  them via `feedback-poll`, acts, and clears them (route to this file), per `propagate-feedback`.

## Rotate / fix

- **An API key (Pexels/Unsplash/SerpAPI/Places/scrape.do/BrightData/Apify):** regenerate it in that
  service's console (above), update `keys.env` at the repo root, and re-upload `keys.env` to Drive `_setup/`.
- **The service-account key:** rotate in the GCP console (project holicay-402208) → download the new
  `holicay-*.json` → replace at repo root → re-upload to `_setup/`. The SA email (and thus the Sheet/Drive
  shares) stays the same.
- **The OAuth Drive token:** delete your local `drive_token.json` and re-run `python3
  engine/drive/drive_auth.py` (per-user; not shared, not in `_setup/`).
- **ChatGPT / TikTok:** re-login in the `~/.masquerade_chrome` Chrome (`bash engine/qc/preflight.sh` to
  launch it; `node engine/scrape/tiktok_login.js --open` for TikTok). Nothing to rotate in `keys.env`.
- **Over-shared `_setup/`:** rotate the SA key + all 7 API keys, then re-publish `_setup/` (SETUP.md Security note).
