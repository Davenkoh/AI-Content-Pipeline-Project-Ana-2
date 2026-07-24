# SETUP — run Project Ana 2.0 on your machine

Project Ana 2.0 is **AI-agent-agnostic**: the engine is plain `bash` / `python3` / `node`, and the
workflow is markdown your agent reads and executes. Drive it with **any** capable AI coding agent (Claude
Code, Codex, Cursor, …) or by hand. GitHub is the single code entry point; one command pulls the media and
you place the secrets from the shared Google Drive.

---

## The shared infrastructure (what you connect to)

Three shared resources, **all owned by `creators@holicay.com`**:

| Resource | Link | Holds |
|---|---|---|
| **GitHub repo** | https://github.com/Davenkoh/Project-Ana-2 | All code, `knowledge/`, `.claude/skills/`, docs, `AGENTS.md`, `state.json`. **No secrets, no media.** |
| **Google Drive** — "Project Ana 2.0" | in `creators@holicay.com` My Drive · `_setup/` = [secrets folder](https://drive.google.com/drive/folders/19pUGwusqcvf5cdJuyx6AQKysVleiNHv5) | The `_setup/` secrets bundle, one folder per character (`Ana/`, `Chloe/`, `Hannah/`) + `_shared/`, brand assets, the media library, and every delivered post. |
| **Google Sheet** — "Project Ana 2.0" | https://docs.google.com/spreadsheets/d/1Wskn2YPWwu3cEBJVTwyYpgM7XXVjJwODLjZVqLgAqWo/edit | The human front-end: a fact tab per character + Dashboard + Connectors + Accounts + Holicay Brand + Dictionary. GREEN cells = your feedback channel. |

### How the agent controls the Sheet + Drive — two Google credentials
- **A service account** — `holicay-message-machine@holicay-402208.iam.gserviceaccount.com` (GCP project
  **holicay-402208**) — is shared (Editor) into the Sheet + Drive. `sheets.py` uses it to read/write the
  **Sheet**; `drive_sync.py` uses it to **read** Drive media. Its key file is `holicay-402208-*.json` at the repo root.
- **An OAuth Drive client** (GCP project **masquerade-2**, a *different* project — legacy but working)
  mints your **own** `drive_token.json` so **uploads** land with a storage-quota owner. That is step 4.

Full connector inventory + billing: [`CONNECTORS.md`](CONNECTORS.md).

## Prerequisites (install once)
- **git** + the **`gh`** CLI (GitHub access)
- **Node.js** ≥ 18 and **npm**
- **Python** 3.9+
- **Google Chrome** (the scrapers + cover-gen drive a real Chrome over CDP). Non-macOS: set `CHROME_BIN`.
- **Access from the owner** (`creators@holicay.com`): ask to be shared (Editor) on the Drive folder + the Sheet.

---

## 1. Clone + bootstrap
```bash
git clone https://github.com/Davenkoh/Project-Ana-2.git "Project Ana 2.0" && cd "Project Ana 2.0"
bash setup.sh          # wraps engine/setup/bootstrap.py ; add --full to also pull media/library scratch
```
Bootstrap installs the Python + Node deps, checks the secrets, and — once they are present — pulls the
gitignored build media from Drive (character refs, `_shared`, `chars/`, `media/graded`, `media/brand`) and
runs preflight. It skips anything already present, so it is safe to re-run.

> **Never nest this repo inside another git repo.** The engine finds the repo root by walking up to the
> `.gitignore` sentinel; a parent repo would break `keys.env` + Playwright resolution.

## 2. Place the secrets (one manual step — the folder is privately shared)
Open Drive **`_setup/`** ([link](https://drive.google.com/drive/folders/19pUGwusqcvf5cdJuyx6AQKysVleiNHv5))
and download these **3 files** into the repo **root**:
- `keys.env` — the 7 sourcing API keys (Pexels · Unsplash · SerpAPI · Google Places · scrape.do · Bright Data · Apify)
- `holicay-402208-*.json` — the **service-account key** (Sheet + Drive-read auth)
- `client_secret*.json` — the Drive **OAuth client** secret (used by step 4)

Then re-run `bash setup.sh` — with the creds present it pulls the media too. The **4th** credential the
machine needs, **`drive_token.json`, is NOT in the bundle** — you mint it per-person in step 4.

## 3. Log in once (Chrome profile) — per person, cannot be shared
Cover/scene gen has **no API key**; it drives a logged-in ChatGPT in the `~/.masquerade_chrome` Chrome
profile, and stats scraping uses the same profile for TikTok. Launch it and sign in:
```bash
bash engine/qc/preflight.sh         # launches the masquerade Chrome profile if it's down
```
In the window it opens, **log into ChatGPT and TikTok.** The logins persist in the profile. (TikTok views
are login-gated; if they later go blank, re-auth with `node engine/scrape/tiktok_login.js --open`.)

## 4. Authorize Drive uploads (per person, one time)
```bash
python3 engine/drive/drive_auth.py  # browser consent → writes your own drive_token.json
```
Uploads are then owned by your account but land in the shared folder.

## 5. Add the hooks (Claude Code) — media auto-sync + Chrome cleanup
Create **`.claude/settings.local.json`** (gitignored, per-machine) with exactly this hooks block — a
`SessionStart` + `Stop` media sync and a `Stop` Chrome quit:
```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [
        { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engine/qc/sync_media.py\" --if-changed", "timeout": 180, "statusMessage": "Sync check: media -> Drive (if changed)" }
      ] }
    ],
    "Stop": [
      { "hooks": [
        { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/engine/lib/quit_chrome.sh\"", "timeout": 10, "statusMessage": "Quitting the masquerade Chrome" },
        { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/engine/qc/sync_media.py\" --if-changed", "timeout": 180, "statusMessage": "Syncing media to Drive (if changed)" }
      ] }
    ]
  }
}
```
> **Non-Claude orchestrators** don't run these hooks. Do the same two things by hand **at the end of each
> session**: `bash engine/lib/quit_chrome.sh` and `python3 engine/qc/sync_media.py --if-changed` (or just
> `bash sync.sh`).

## 6. Confirm + run
```bash
bash engine/qc/preflight.sh                                   # expect: == preflight OK ==
python3 engine/sheets/sheets.py next-slot --character ana     # expect: {"id": "tt-20", "framework": "A", ...}
```
Then point your agent at [`AGENTS.md`](AGENTS.md) → [`WORKFLOW.md`](WORKFLOW.md), or just say
"generate a post for chloe" (the `generate-post` skill).

> **Verify a fresh handoff.** To adversarially check a blind teammate can run this from GitHub + Drive, run
> the `verify-portability` workflow.

---

## Where things live (the GitHub / Drive / local split)
- **GitHub** — `engine/`, `knowledge/` (`.md`), `.claude/skills/`, the docs, `AGENTS.md`, `state.json`,
  `media/manifest.json` (the attribution index), `fixtures/reference/*.png` (the render regression spec).
- **Drive "Project Ana 2.0"** — the gitignored media + secrets: `_setup/` (secrets), `Ana/` `Chloe/`
  `Hannah/` (per-character images + `Tiktok/<post>`), `_shared/`, the brand assets, the media library, and
  every delivered post.
- **Local only** (gitignored, regenerated) — `node_modules/`, `outputs/**/_work/`, `drive_token.json`, the
  `~/.masquerade_chrome` profile, `.claude/settings.local.json`.

The rule: **git carries code + text; Drive carries media + secrets.**

## Owner: publishing media to Drive (`creators@holicay.com`)
When you add or refresh gitignored media, push it up so teammates' bootstrap can pull it:
```bash
python3 engine/drive/drive_sync.py --mirror-all              # ALL char refs + _shared + brand + chars + media -> Drive
python3 engine/drive/drive_sync.py --mirror-all --prune      # + TRASH Drive files you deleted locally (exact mirror)
bash sync.sh                                                 # the "git push" for media: mirror-all --prune + deliver-missing
```
`--mirror-all` is idempotent + md5-skips unchanged bytes. The **secrets** are the one exception — drop them
into Drive `_setup/` by hand via the Drive UI (never scripted).

## Security note
The service-account key + the API keys live in Drive `_setup/`. Keep the **whole "Project Ana 2.0" folder
shared only with trusted teammates** (never "anyone with the link"). The service account can only touch
what it was shared into (this project's Sheet + Drive), so the blast radius is contained. If the folder is
ever over-shared, rotate the SA key + the API keys (their consoles are in `CONNECTORS.md`) and re-publish `_setup/`.
