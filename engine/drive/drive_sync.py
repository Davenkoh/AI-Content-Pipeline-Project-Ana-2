#!/usr/bin/env python3
"""Push a finished post's deliverables to Google Drive via the service account.
Creates <shared root>/<Character>/<Platform>/<NN - Title>/ and uploads final/*.png + caption.txt + _review.md.

Requires: Drive API enabled on project holicay-402208 (390823350744) AND the target Drive
folder shared with holicay-message-machine@holicay-402208.iam.gserviceaccount.com (edit access).
Deps: google-api-python-client (installed).

Usage:
  python3 drive_sync.py --list-shared                       # see folders the SA can access
  python3 drive_sync.py --post "<local post folder>" --character Ana --platform Tiktok [--root-id ID | --root-name NAME]
  python3 drive_sync.py --inspo "inspo/NN"                   # upload an inspo folder, print a shareable link
  python3 drive_sync.py --mirror character/Ana --dest Ana    # UP: upload a character's gitignored refs to <root>/Ana/
  python3 drive_sync.py --pull Ana --to character/Ana        # DOWN: fill in a character's gitignored refs (skips post libraries + files present)
  python3 drive_sync.py --fetch-post "NN - Title" --character Ana  # DOWN: reconstitute one finished post into outputs/ (local can stay disposable)

Default shared root is "Project Ana" (auto-resolved by name); override with --root-id/--root-name.
"""
import argparse, os, sys, glob, json, mimetypes, hashlib

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_MIME = "application/vnd.google-apps.folder"
OAUTH_CLIENT = "oauth_client.json"   # Desktop OAuth client downloaded from the GCP console
OAUTH_TOKEN = "drive_token.json"     # cached after the one-time browser consent (gitignored)


def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.path.dirname(os.path.abspath(__file__))


def _char_name(arg):
    """Resolve --character (registry key or display name) to its Drive folder name. Defaults to
    state.json's default_character; title-cases an unknown arg as a best-effort folder name."""
    st = {}
    try:
        st = json.load(open(os.path.join(_root(), "state.json"))) or {}
    except Exception:
        pass
    chars = st.get("characters") or {}
    if not arg:
        arg = st.get("default_character") or (next(iter(chars)) if chars else "Ana")
    a = str(arg).strip().lower()
    for key, c in chars.items():
        c = c or {}
        if a in (key.lower(), (c.get("name") or key).lower()):
            return c.get("name") or key.capitalize()
    return str(arg).strip().capitalize()


def _find_creds():
    """Service-account JSON (fallback path only): $HOLICAY_SA_JSON, else the first
    *.json with type=service_account walking up to the repo root."""
    override = os.environ.get("HOLICAY_SA_JSON")
    if override and os.path.exists(override):
        return override
    p = os.path.dirname(os.path.abspath(__file__))
    while True:
        for f in sorted(glob.glob(os.path.join(p, "*.json"))):
            try:
                if json.load(open(f)).get("type") == "service_account":
                    return f
            except Exception:
                pass
        parent = os.path.dirname(p)
        if parent == p:
            break
        p = parent
    sys.exit("[drive_sync] no service-account JSON found (set $HOLICAY_SA_JSON)")


def _service():
    """Prefer OAuth-as-user: a service account has no storage quota and CANNOT upload files
    to a personal-Gmail My Drive. With your OAuth token the files are owned by you, so your
    quota is used. Falls back to the service account only if no OAuth client is present."""
    from googleapiclient.discovery import build
    root = _root()
    import glob as _glob
    _cands = sorted(_glob.glob(os.path.join(root, "oauth_client*.json")) +
                    _glob.glob(os.path.join(root, "client_secret*.json")))
    client = _cands[0] if _cands else os.path.join(root, OAUTH_CLIENT)
    token = os.path.join(root, OAUTH_TOKEN)
    if os.path.exists(client) or os.path.exists(token):
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials as UserCreds
        from google.auth.transport.requests import Request
        creds = UserCreds.from_authorized_user_file(token, SCOPES) if os.path.exists(token) else None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(client):
                    sys.exit(f"Place your OAuth client JSON at {client}")
                creds = InstalledAppFlow.from_client_secrets_file(client, SCOPES).run_local_server(port=0)
            with open(token, "w") as f:
                f.write(creds.to_json())
        return build("drive", "v3", credentials=creds, cache_discovery=False)
    from google.oauth2.service_account import Credentials  # fallback (can't upload to My Drive)
    creds = Credentials.from_service_account_file(_find_creds(), scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _q(svc, q):
    """Run a Drive query to completion (paginated) — never silently cap results."""
    out, tok = [], None
    while True:
        resp = svc.files().list(q=q, fields="nextPageToken, files(id,name,mimeType,parents,md5Checksum,size)",
            supportsAllDrives=True, includeItemsFromAllDrives=True, pageSize=1000, pageToken=tok).execute()
        out += resp.get("files", [])
        tok = resp.get("nextPageToken")
        if not tok:
            return out


def list_shared(svc):
    fs = _q(svc, f"mimeType='{FOLDER_MIME}' and trashed=false")
    print(f"{len(fs)} folder(s) visible to the service account:")
    for f in fs:
        print(f"  {f['id']}  {f['name']}  parents={f.get('parents')}")
    return fs


def _drive_root_name():
    """The canonical shared-root name from state.json (drive_root_name = 'Project Ana')."""
    try:
        return (json.load(open(os.path.join(_root(), "state.json"))) or {}).get("drive_root_name")
    except Exception:
        return None


def resolve_root(svc, root_id, root_name):
    if root_id:
        return root_id
    if not root_name:                      # default to the configured canonical root (state.json),
        root_name = _drive_root_name()     # so the SA's many other Holicay folders can't make this ambiguous
    fs = _q(svc, f"mimeType='{FOLDER_MIME}' and trashed=false")
    if root_name:
        for f in fs:
            if f["name"] == root_name:
                return f["id"]
        sys.exit(f"no shared folder named {root_name!r}; run --list-shared")
    prefer = [f for f in fs if f["name"].lower() in
              ("project masquerade 2.0", "masquerade", "ana", "holicay",
               "ai content workflow", "content")]
    if len(prefer) == 1:
        return prefer[0]["id"]
    if len(fs) == 1:
        return fs[0]["id"]
    print("Need an explicit root (--root-id or --root-name). Visible folders:")
    for f in fs:
        print(f"  {f['id']}  {f['name']}")
    sys.exit(2)


def ensure_folder(svc, name, parent_id):
    safe = name.replace("'", "\\'")
    hit = _q(svc, f"mimeType='{FOLDER_MIME}' and name='{safe}' and '{parent_id}' in parents and trashed=false")
    if hit:
        return hit[0]["id"]
    meta = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent_id]}
    return svc.files().create(body=meta, fields="id", supportsAllDrives=True).execute()["id"]


def upload_file(svc, path, parent_id):
    from googleapiclient.http import MediaFileUpload
    name = os.path.basename(path)
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    existing = _q(svc, f"name='{name}' and '{parent_id}' in parents and trashed=false")
    if existing and existing[0].get("md5Checksum"):       # skip the re-upload if Drive already has these bytes
        h = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        if existing[0]["md5Checksum"] == h.hexdigest():
            return "unchanged"
    media = MediaFileUpload(path, mimetype=mime, resumable=False)
    if existing:
        svc.files().update(fileId=existing[0]["id"], media_body=media, supportsAllDrives=True).execute()
        return "updated"
    svc.files().create(body={"name": name, "parents": [parent_id]}, media_body=media,
        fields="id", supportsAllDrives=True).execute()
    return "created"


# ── brand folder: the loop READS the user's Drive brand assets (and may push learned ones) ──
def find_folder_by_name(svc, name):
    hits = _q(svc, f"mimeType='{FOLDER_MIME}' and name='{name.replace(chr(39), chr(92) + chr(39))}' and trashed=false")
    return hits[0]["id"] if hits else None


def brand_list(svc, folder_name):
    """List the user-owned Drive brand folder (one level of subfolders), for knowledge refresh."""
    fid = find_folder_by_name(svc, folder_name)
    if not fid:
        print(f"(no Drive folder named {folder_name!r} visible to this account)"); return
    items = _q(svc, f"'{fid}' in parents and trashed=false")
    print(f"{folder_name}  ({fid})  — {len(items)} item(s):")
    for it in sorted(items, key=lambda x: x["name"].lower()):
        if it["mimeType"] == FOLDER_MIME:
            print(f"  [dir]  {it['id']}  {it['name']}/")
            for sub in sorted(_q(svc, f"'{it['id']}' in parents and trashed=false"), key=lambda x: x["name"].lower()):
                print(f"         {sub['id']}  {it['name']}/{sub['name']}")
        else:
            print(f"  [file] {it['id']}  {it['name']}")


def brand_get(svc, file_id, out):
    """Download one brand asset by file id (so the loop can actually use it in a design)."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    req = svc.files().get_media(fileId=file_id)
    fh = io.FileIO(out, "wb")
    dl = MediaIoBaseDownload(fh, req)
    done = False
    while not done:
        _, done = dl.next_chunk()
    print("downloaded ->", out)


def brand_put(svc, path, folder_name):
    """Push a learned/reusable brand asset back into the Drive brand folder (persist for future runs)."""
    fid = find_folder_by_name(svc, folder_name)
    if not fid:
        sys.exit(f"no Drive folder named {folder_name!r}; create it or share it first")
    print(f"  {upload_file(svc, path, fid)}: {os.path.basename(path)} -> {folder_name}/")


# ── two-way folder mirror (the gitignored media — persona refs, brand assets — lives on Drive) ──
SKIP_NAMES = {"_work", "node_modules", ".git", "__pycache__", ".DS_Store"}
# each character's Drive folder also holds its finished-post library (Ana/Tiktok, …). The ref pull
# (bootstrap) skips these: posts are large and browsed on Drive / pulled on demand, not at setup.
POST_LIBS = {"Tiktok"}


def _git_tracked_abs(local_dir):
    """Abspaths of files git TRACKS under local_dir. The .gitignore is the source/Drive boundary:
    git owns the tracked text/code; Drive owns only what git ignores (the media). So mirror skips
    these — it never duplicates a .md / source.txt that already lives in the repo."""
    import subprocess
    try:
        root = _root()
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, text=True)
        base = os.path.abspath(local_dir)
        keep = set()
        for p in out.stdout.split("\0"):
            if not p:
                continue
            ap = os.path.abspath(os.path.join(root, p))
            if ap == base or ap.startswith(base + os.sep):
                keep.add(ap)
        return keep
    except Exception:
        return set()


def mirror_up(svc, local_dir, dest_name, root_id, prune=False):
    """Recursively upload the git-IGNORED media under local_dir to <root>/<dest_name>/.
    Skips anything git tracks (git owns text/code; Drive owns media), so it never duplicates a
    repo-tracked .md / source.txt onto Drive. Idempotent (re-runs only update changed files)."""
    local_dir = local_dir.rstrip("/")
    if not os.path.isdir(local_dir):
        sys.exit(f"[mirror] no such local dir: {local_dir}")
    tracked = _git_tracked_abs(local_dir)
    fid = {"": ensure_folder(svc, dest_name, root_id)}

    def ensure_path(rel):                                # lazily create the folder chain (no empty dirs)
        if rel in fid:
            return fid[rel]
        parent = ensure_path(os.path.dirname(rel)) if os.path.dirname(rel) else fid[""]
        fid[rel] = ensure_folder(svc, os.path.basename(rel), parent)
        return fid[rel]

    created = updated = skipped = unchanged = 0
    want = set()                                          # gitignored media rel-paths that SHOULD be on Drive
    for cur, dirs, files in os.walk(local_dir):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_NAMES)
        rel = os.path.relpath(cur, local_dir)
        rel = "" if rel == "." else rel
        for fn in sorted(files):
            if fn in SKIP_NAMES:
                continue
            path = os.path.join(cur, fn)
            if os.path.abspath(path) in tracked:          # git owns it — stays in the repo, not Drive
                skipped += 1
                continue
            want.add(os.path.join(rel, fn) if rel else fn)
            r = upload_file(svc, path, ensure_path(rel))
            created += r == "created"; updated += r == "updated"; unchanged += r == "unchanged"
            if r != "unchanged":
                print(f"  {r}: {dest_name}/{os.path.join(rel, fn)}")
    pruned = 0
    if prune:                                             # make Drive EXACTLY match local: trash Drive-only extras
        def _trash(it, label):
            nonlocal pruned
            try:
                svc.files().update(fileId=it["id"], body={"trashed": True}, supportsAllDrives=True).execute()
                pruned += 1
                print(f"  pruned{label}")
            except Exception as e:                        # e.g. a file owned by someone else — skip, don't abort
                print(f"  [prune skip]{label} ({type(e).__name__})", file=sys.stderr)
        def _prune(folder_id, relbase):
            for it in _q(svc, f"'{folder_id}' in parents and trashed=false"):
                r = os.path.join(relbase, it["name"]) if relbase else it["name"]
                if it["mimeType"] == FOLDER_MIME:
                    _prune(it["id"], r)
                    if not any(w == r or w.startswith(r + "/") for w in want):   # no local file under this dir
                        _trash(it, f" dir: {dest_name}/{r}/")
                elif r not in want:
                    _trash(it, f": {dest_name}/{r}")
        _prune(fid[""], "")
    print(f"[mirror] {local_dir} -> {dest_name}/  ({created} created, {updated} updated, {unchanged} unchanged, "
          f"{skipped} git-tracked skipped{', ' + str(pruned) + ' pruned (trashed on Drive)' if prune else ''})")
    return fid[""]


def pull_down(svc, dest_name, local_dir, root_id, overwrite=False):
    """Recursively download Drive <root>/<dest_name>/ into local_dir. By default SKIPS files that
    already exist locally, so it fills in gitignored media (persona refs, brand assets) without
    clobbering git-tracked text. Authenticated (works on a privately-shared folder)."""
    src = next((f["id"] for f in _q(svc, f"mimeType='{FOLDER_MIME}' and '{root_id}' in parents "
                                         f"and trashed=false") if f["name"] == dest_name), None)
    if not src:
        print(f"[pull] (no Drive folder {dest_name!r} under root — skipping)")
        return
    got = skipped = 0

    def rec(folder_id, path):
        nonlocal got, skipped
        os.makedirs(path, exist_ok=True)
        for it in _q(svc, f"'{folder_id}' in parents and trashed=false"):
            if it["name"] in SKIP_NAMES or it["name"] in POST_LIBS:
                continue
            dest = os.path.join(path, it["name"])
            if it["mimeType"] == FOLDER_MIME:
                rec(it["id"], dest)
            elif os.path.exists(dest) and not overwrite:
                skipped += 1
            else:
                brand_get(svc, it["id"], dest)           # reuse the chunked downloader
                got += 1

    rec(src, local_dir)
    print(f"[pull] {dest_name}/ -> {local_dir}  ({got} downloaded, {skipped} already present)")


def mirror_all(svc, root_id, prune=False):
    """Push EVERY local character-media store up to Drive in one shot — Drive-canonical for ALL media,
    not just posts/inspo. Mirrors each character/<Name>/ -> <Name>/ (refs + profile pics),
    character/_shared -> _shared, and knowledge/brand -> Holicay Brand. Idempotent (updates only
    changed files; skips git-tracked). Posts sync via `sheets.py deliver-missing`, inspo via
    `sheets.py inspo-sync` — run all three to fully reconcile local -> Drive."""
    root = _root()
    st = {}
    try:
        st = json.load(open(os.path.join(root, "state.json"))) or {}
    except Exception:
        pass
    # Target the media LEAF folders, NOT the character roots — so --prune makes each an exact mirror
    # WITHOUT ever touching the Drive-only post libraries (<Char>/Tiktok/, which don't exist under
    # character/). Posts sync via deliver-missing; pruning a char root would trash them.
    targets = []                                          # (local_dir, nested Drive dest under root)
    for key, c in (st.get("characters") or {}).items():
        name = (c or {}).get("name") or key.capitalize()
        for sub in ("Base References", "Profile Pictures"):
            targets.append((os.path.join(root, "character", name, sub), f"{name}/{sub}"))
    shared = os.path.join(root, "character", "_shared")
    if os.path.isdir(shared):
        for sub in sorted(os.listdir(shared)):
            if os.path.isdir(os.path.join(shared, sub)):
                targets.append((os.path.join(shared, sub), f"_shared/{sub}"))
    targets.append((os.path.join(root, "knowledge", "brand"), "Holicay Brand"))
    for local, dest in targets:
        if not os.path.isdir(local):
            print(f"[mirror-all] (skip — no local {os.path.relpath(local, root)})")
            continue
        parent = root_id
        for seg in dest.split("/")[:-1]:                  # resolve the nested dest chain under root
            parent = ensure_folder(svc, seg, parent)
        mirror_up(svc, local, dest.split("/")[-1], parent, prune)
    print("[mirror-all] done. (posts: `sheets.py deliver-missing` · inspo: `sheets.py inspo-sync`)")


def fetch_post(svc, title, char_name, platform, local_dir, root_id, overwrite=False):
    """DOWN (the inverse of --post): reconstitute ONE finished post by downloading
    <root>/<char_name>/<platform>/<title>/ into local_dir. This is what lets local stay disposable —
    any post can be pulled back from Drive (the canonical store). bootstrap's ref pull still skips the
    post libraries (they're large); this is the explicit, on-demand way to get a single post.
    Skips files already present unless overwrite."""
    def child(parent, name):
        safe = name.replace("'", "\\'")
        hit = _q(svc, f"mimeType='{FOLDER_MIME}' and name='{safe}' and '{parent}' in parents and trashed=false")
        return hit[0]["id"] if hit else None
    cid = child(root_id, char_name)
    pid = child(cid, platform) if cid else None
    tid = child(pid, title) if pid else None
    if not tid:
        sys.exit(f"[fetch] no post {char_name}/{platform}/{title!r} on Drive")
    got = skipped = 0

    def rec(folder_id, path):
        nonlocal got, skipped
        os.makedirs(path, exist_ok=True)
        for it in _q(svc, f"'{folder_id}' in parents and trashed=false"):
            if it["name"] in SKIP_NAMES:
                continue
            dest = os.path.join(path, it["name"])
            if it["mimeType"] == FOLDER_MIME:
                rec(it["id"], dest)
            elif os.path.exists(dest) and not overwrite:
                skipped += 1
            else:
                brand_get(svc, it["id"], dest)
                got += 1

    rec(tid, local_dir)
    print(f"[fetch] {char_name}/{platform}/{title} -> {local_dir}  ({got} downloaded, {skipped} already present)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post")
    ap.add_argument("--character", help="which character's Drive folder to deliver under (registry key or name; default from state.json)")
    ap.add_argument("--inspo", help="local inspo folder to upload to <root>/inspo/<name>/ (prints a shareable link)")
    ap.add_argument("--platform", default="Tiktok")
    ap.add_argument("--root-id")
    ap.add_argument("--root-name")
    ap.add_argument("--list-shared", action="store_true")
    ap.add_argument("--brand-list", action="store_true", help="list the Drive brand folder")
    ap.add_argument("--brand-folder", default="Holicay Brand", help="name of the Drive brand folder")
    ap.add_argument("--brand-get", help="file id to download")
    ap.add_argument("--brand-put", help="local asset to push into the brand folder")
    ap.add_argument("--out", help="output path for --brand-get")
    ap.add_argument("--mirror", help="local folder to recursively UPLOAD to <root>/<dest>/ (media -> Drive)")
    ap.add_argument("--dest", help="Drive folder name under root for --mirror (default: the folder's basename)")
    ap.add_argument("--mirror-all", action="store_true", help="push ALL local character/_shared/brand media up to Drive (Drive-canonical)")
    ap.add_argument("--prune", action="store_true", help="with --mirror/--mirror-all: also TRASH Drive files/folders not present locally (make Drive an exact mirror)")
    ap.add_argument("--pull", help="Drive folder name under root to recursively DOWNLOAD into --to")
    ap.add_argument("--fetch-post", help="post folder name (NN - Title) to DOWNLOAD from <root>/<char>/<platform>/ into outputs/ (or --to)")
    ap.add_argument("--to", help="local dir for --pull / --fetch-post (default: the Drive folder name / outputs/<title>)")
    ap.add_argument("--overwrite", action="store_true", help="for --pull: overwrite existing local files")
    a = ap.parse_args()
    svc = _service()
    if a.list_shared:
        list_shared(svc); return
    if a.mirror:
        root = resolve_root(svc, a.root_id, a.root_name)
        dest = a.dest or os.path.basename(a.mirror.rstrip("/"))
        parent = root
        for seg in dest.split("/")[:-1]:                  # allow a nested dest like "_shared/Wardrobe References"
            parent = ensure_folder(svc, seg, parent)
        mirror_up(svc, a.mirror, dest.split("/")[-1], parent, a.prune); return
    if a.mirror_all:
        root = resolve_root(svc, a.root_id, a.root_name)
        mirror_all(svc, root, a.prune); return
    if a.pull:
        root = resolve_root(svc, a.root_id, a.root_name)
        pull_down(svc, a.pull, a.to or a.pull, root, a.overwrite); return
    if a.fetch_post:
        root = resolve_root(svc, a.root_id, a.root_name)
        dest = a.to or os.path.join(_root(), "outputs", a.fetch_post)
        fetch_post(svc, a.fetch_post, _char_name(a.character), a.platform, dest, root, a.overwrite); return
    if a.brand_list:
        brand_list(svc, a.brand_folder); return
    if a.brand_get:
        brand_get(svc, a.brand_get, a.out or os.path.basename(a.brand_get)); return
    if a.brand_put:
        brand_put(svc, a.brand_put, a.brand_folder); return
    if a.inspo:
        src = a.inspo.rstrip("/")
        if not os.path.isdir(src):
            sys.exit(f"[drive_sync] no such inspo folder: {src}")
        root = resolve_root(svc, a.root_id, a.root_name)
        folder = ensure_folder(svc, os.path.basename(src), ensure_folder(svc, "inspo", root))
        imgs = sorted(os.path.join(src, f) for f in os.listdir(src)
                      if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        if not imgs:
            print(f"[drive_sync] (no images in {src})")
        for p in imgs:
            print(f"  {upload_file(svc, p, folder)}: {os.path.basename(p)}")
        print(f"-> https://drive.google.com/drive/folders/{folder}")
        return
    if not a.post:
        sys.exit("--post <local post folder> required")
    post_dir = a.post.rstrip("/")
    title = os.path.basename(post_dir)
    final_dir = os.path.join(post_dir, "final")
    caption = os.path.join(post_dir, "caption.txt")
    review = os.path.join(post_dir, "_review.md")
    if not os.path.isdir(final_dir):
        sys.exit(f"no final/ in {post_dir}")
    root = resolve_root(svc, a.root_id, a.root_name)
    char_name = _char_name(a.character)
    folder = ensure_folder(svc, title, ensure_folder(svc, a.platform, ensure_folder(svc, char_name, root)))
    files = sorted(os.path.join(final_dir, f) for f in os.listdir(final_dir) if f.lower().endswith(".png"))
    if os.path.exists(caption):
        files.append(caption)
    if os.path.exists(review):                       # ship the rationale too, so reviewers on Drive see the "why"
        files.append(review)
    for p in files:
        print(f"  {upload_file(svc, p, folder)}: {os.path.basename(p)}")
    print(f"-> https://drive.google.com/drive/folders/{folder}")


if __name__ == "__main__":
    main()
