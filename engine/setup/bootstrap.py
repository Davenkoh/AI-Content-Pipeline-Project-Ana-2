#!/usr/bin/env python3
"""One-command onboarding for a fresh clone.

  1. installs Python deps (engine/requirements.txt) and Node deps (engine/package.json)
  2. places the shared `_setup/` secrets bundle (keys.env + the *.json creds) at the repo root.
     The folder is PRIVATELY shared, so this is normally a MANUAL step (SETUP.md step 1); bootstrap
     only attempts an automated gdown pull if drive_setup_url is set, and falls back gracefully.
  3. with the secrets present, pulls the gitignored build media from Drive — character refs, _shared,
     knowledge/brand, chars, media/graded, media/brand (add --full to also pull media/library scratch)
  4. runs preflight

The Drive folder link comes from state.json -> "drive_setup_url". Idempotent; safe to re-run.
Run from anywhere:  python3 engine/setup/bootstrap.py   (or: bash setup.sh)
"""
import glob
import json
import os
import shutil
import subprocess
import sys

# secret/credential filenames we recognize and place at the repo root
SECRET_PATTERNS = ("keys.env", "holicay-*.json",
                   "*service_account*.json", "client_secret*.json", "oauth_client*.json")


def repo_root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


R = repo_root()


def run(cmd):
    print(f"\n$ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=R)


def have_secrets():
    return os.path.exists(os.path.join(R, "keys.env")) and any(
        glob.glob(os.path.join(R, p)) for p in ("holicay-*.json", "*service_account*.json"))


def install_deps():
    req = os.path.join(R, "engine", "requirements.txt")
    if os.path.exists(req):
        run([sys.executable, "-m", "pip", "install", "-r", req])
    if os.path.exists(os.path.join(R, "engine", "package.json")) and shutil.which("npm"):
        run(["npm", "install", "--prefix", "engine"])
    else:
        print("[bootstrap] npm not found — install Node.js, then: npm install --prefix engine")


def pull_setup_bundle():
    if have_secrets():
        print("\n[bootstrap] secrets already present at repo root — skipping Drive pull.")
        return
    url = (json.load(open(os.path.join(R, "state.json"))) or {}).get("drive_setup_url", "")
    if not url or "PASTE" in url:
        print("\n[bootstrap] state.json has no usable 'drive_setup_url' yet.")
        print("            → Set it to the shared '_setup' Drive folder link, OR copy keys.env +")
        print("              the *.json creds from that folder into the repo root manually.")
        return
    try:
        import gdown
    except ImportError:
        run([sys.executable, "-m", "pip", "install", "gdown"])
        import gdown
    tmp = os.path.join(R, ".setup_download")
    print(f"\n[bootstrap] attempting an automated _setup/ pull from Drive → repo root")
    try:
        gdown.download_folder(url=url, output=tmp, quiet=False, use_cookies=False)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  [info] automated pull failed ({type(e).__name__}) — the _setup/ folder is privately")
        print("         shared (not link-public), so this is expected. Download keys.env + the *.json")
        print("         creds from Drive _setup/ into the repo ROOT by hand (SETUP.md step 1), then re-run.")
        return
    placed = 0
    for pat in SECRET_PATTERNS:
        for f in glob.glob(os.path.join(tmp, "**", pat), recursive=True):
            dest = os.path.join(R, os.path.basename(f))
            shutil.copy2(f, dest)
            placed += 1
            print("  placed", os.path.basename(f))
    shutil.rmtree(tmp, ignore_errors=True)
    if not placed:
        print("  [warn] no secret files found via the automated pull (the _setup/ folder is privately shared).")
        print("         Download them from Drive _setup/ into the repo ROOT by hand (SETUP.md step 1), then re-run.")


def pull_media_assets(full=False):
    """Fill in the gitignored, build-critical media from the shared Drive, using the creds that
    pull_setup_bundle just placed: each character's persona references (so the cover gen has a face
    to work from), the shared wardrobe/pfp refs (_shared), the Holicay brand assets, the chosen
    character photos (chars/), and the sourced/first-party media picks (media/graded, media/brand).
    Skips files already present, so it is safe to re-run. The finished-post libraries (Ana/Tiktok, …)
    are NOT pulled here (browse on Drive, or pull on demand with e.g.
    python3 engine/drive/drive_sync.py --fetch-post "28 - Title" --character ana). media/library is
    LOCAL SCRATCH and is pulled only with --full."""
    if not have_secrets():
        print("\n[bootstrap] secrets not present yet — skipping the Drive media pull.")
        print("            Place keys.env + the *.json credential files from Drive _setup/ into the repo ROOT (SETUP.md step 1), then re-run.")
        return
    state = json.load(open(os.path.join(R, "state.json"))) if os.path.exists(os.path.join(R, "state.json")) else {}
    root_name = state.get("drive_root_name", "Project Ana 2.0")
    ds = os.path.join(R, "engine", "drive", "drive_sync.py")
    # one folder per character on Drive (refs + posts); pull each character's refs + the shared refs.
    # the ref pull skips the finished-post library (Tiktok) — those are browsed/pulled on demand.
    # (drive_name, local_dir) — drive_name may be a NESTED Drive path (drive_sync --pull walks it).
    targets = []
    for key, c in (state.get("characters") or {}).items():
        name = (c or {}).get("name") or key.capitalize()
        targets.append((name, f"character/{name}"))
    targets.append(("_shared", "character/_shared"))
    targets.append(("Holicay Brand", "knowledge/brand"))
    targets.append(("chars", "chars"))
    targets.append(("media/graded", "media/graded"))
    targets.append(("media/brand", "media/brand"))
    if full:
        targets.append(("media/library", "media/library"))   # local scratch — opt-in only
    for drive_name, local in targets:
        print(f"\n[bootstrap] pulling Drive '{drive_name}' -> {local}/ (gitignored media)")
        run([sys.executable, ds, "--pull", drive_name, "--to", local, "--root-name", root_name])


def preflight():
    pf = os.path.join(R, "engine", "qc", "preflight.sh")
    if os.path.exists(pf):
        run(["bash", pf])


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Project Ana 2.0 one-command onboarding for a fresh clone.")
    ap.add_argument("--full", action="store_true",
                    help="also pull media/library (local scratch) — off by default")
    args = ap.parse_args()

    print("== Project Ana 2.0 bootstrap ==")
    install_deps()
    pull_setup_bundle()
    pull_media_assets(full=args.full)
    preflight()
    print("\n[bootstrap] done. Remaining one-time steps:")
    st = {}
    try:
        st = json.load(open(os.path.join(R, "state.json"))) or {}
    except Exception:
        pass
    if not (st.get("sheet_id") or "").strip():
        print("  0. python3 engine/setup/provision.py create   # provision the Drive root + Sheet (fills state.json)")
        print("     then: python3 engine/setup/provision.py seed-markers   # seed the 1.0-era id markers")
    print("  1. Launch the masquerade Chrome profile and LOG IN to ChatGPT + TikTok")
    print("     (cover-gen + stats scraping use that logged-in profile; there is no API key).")
    print("  2. python3 engine/drive/drive_auth.py   # one-time Drive OAuth consent (writes drive_token.json)")
    print("  3. bash engine/qc/preflight.sh          # re-check the environment")
    print("  Then follow the workflow docs.")


if __name__ == "__main__":
    main()
