#!/usr/bin/env python3
"""provision.py — ONE-TIME cloud provisioning for Project Ana 2.0 (OAuth-first).

Stands up the cloud side of a fresh 2.0 repo: the shared My-Drive root "Project Ana 2.0", its whole
folder subtree, the tracker spreadsheet (created INSIDE the root and shared with the service
account), the _setup secrets bundle, and the sheet_id + drive_setup_url pointers written back into
state.json. Then `seed-markers` anchors 2.0's post numbering to where 1.0 left off.

Reuses engine/drive/drive_sync.py (OAuth Drive service + folder/upload helpers) and
engine/sheets/sheets.py (gspread client + roster + headers) by IMPORT, so there is no drift.

  python3 engine/setup/provision.py create [--secrets-src DIR] [--dry-run]
  python3 engine/setup/provision.py seed-markers [--old-sheet-id ID]

create        find-or-create the Drive root + subtree + spreadsheet, share with the SA, upload the
              _setup secrets, and write sheet_id + drive_setup_url into state.json. Idempotent:
              re-running finds existing pieces and fills gaps. --dry-run prints the plan, no network.
seed-markers  via the SA, read the 1.0 Sheet's Ana/Chloe/Hannah col A, find each character's max
              <prefix>-NN, and append ONE marker row per fact tab in the NEW sheet (Framework EMPTY,
              so rotation ignores it) — so 2.0 ids continue from 1.0. Run AFTER `sheets.py init`.

Uploads/creation use the per-user OAuth token (drive_token.json); run drive_auth.py first if needed.
On any OAuth/Drive failure this prints a manual fallback (do it by hand in the Drive UI).
"""
import argparse, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.dirname(HERE)
# import the engine helpers (no module-level network in either) — prefer import over copy to avoid drift
sys.path.insert(0, os.path.join(ENGINE, "drive"))
sys.path.insert(0, os.path.join(ENGINE, "sheets"))
import drive_sync as D            # noqa: E402  (OAuth service + ensure_folder/_q/upload_file/_find_creds/_root)
import sheets as S               # noqa: E402  (gspread _client/_open + _characters/HEADERS/_ws/_row_for_id/_today)

# The 1.0 Sheet — READ-ONLY source for the id markers (the 1.0 repo/Sheet stay untouched as the archive).
OLD_SHEET_ID = "1z5t_VrN0ytFqJkw4n1mxELcJZYOwXaTwt4lz8HaechQ"

# Secret files placed in Drive _setup/ (NEVER drive_token.json — that is per-user).
SECRET_PATTERNS = ("keys.env", "holicay-*.json", "client_secret*.json")
SECRET_NEVER = ("drive_token.json",)


def _root_name():
    return (S._state() or {}).get("drive_root_name") or "Project Ana 2.0"


def _sa_email():
    """The service-account client_email (to share the Sheet/Drive with). None if no SA json present."""
    try:
        return (json.load(open(D._find_creds())) or {}).get("client_email")
    except SystemExit:
        return None
    except Exception:
        return None


def _subtree():
    """The relative folder paths to create under the root (roster-driven)."""
    paths = ["_setup",
             "_reference/decks/A", "_reference/decks/B", "_reference/decks/C1", "_reference/decks/C2"]
    for c in S._characters().values():
        n = c["name"]
        paths += [f"{n}/Base References", f"{n}/Profile Pictures", f"{n}/Tiktok"]
    paths += ["_shared/Wardrobe References", "chars", "media/graded", "media/brand", "Holicay Brand"]
    return paths


def _secret_files(src):
    """Absolute paths of the secret files present in src (excludes drive_token.json)."""
    out = []
    for pat in SECRET_PATTERNS:
        for f in sorted(glob.glob(os.path.join(src, pat))):
            if os.path.basename(f) in SECRET_NEVER:
                continue
            if f not in out:
                out.append(f)
    return out


def _manual_fallback(reason=""):
    email = _sa_email() or "the service-account email (holicay-message-machine@holicay-402208.iam.gserviceaccount.com)"
    print("\n[provision] MANUAL FALLBACK (OAuth/Drive could not run here):", file=sys.stderr)
    if reason:
        print(f"            reason: {reason}", file=sys.stderr)
    print(f"  1. In the Drive UI (as creators@holicay.com) create a My-Drive folder \"{_root_name()}\".", file=sys.stderr)
    print("  2. Inside it create a blank Google Sheet (any name, e.g. \"Project Ana 2.0\").", file=sys.stderr)
    print(f"  3. Share BOTH the folder and the Sheet (Editor) with {email}.", file=sys.stderr)
    print("  4. Inside the folder create a \"_setup\" subfolder and upload keys.env + the holicay-*.json", file=sys.stderr)
    print("     SA key + client_secret*.json into it (NOT drive_token.json).", file=sys.stderr)
    print("  5. Paste the Sheet id into state.json \"sheet_id\", and the _setup folder link into", file=sys.stderr)
    print("     \"drive_setup_url\".", file=sys.stderr)
    print("  6. Run: python3 engine/sheets/sheets.py init", file=sys.stderr)
    print("     Then: python3 engine/setup/provision.py seed-markers", file=sys.stderr)


# ── create ────────────────────────────────────────────────────────────────────
def _plan_text():
    lines = [f'Root (My Drive, find-or-create):  "{_root_name()}"', "Subtree under root:"]
    for p in _subtree():
        lines.append(f"    {p}/")
    lines.append(f'Spreadsheet (find-or-create INSIDE root):  "{_root_name()}"')
    email = _sa_email()
    lines.append(f"  -> shared (Editor) with SA: {email or '(no SA json found at repo root)'}")
    lines.append(f"  -> root folder also shared (Editor) with the SA")
    src = os.path.join(D._root())
    lines.append("Secrets uploaded to _setup/ (drive_token.json EXCLUDED):")
    found = _secret_files(src)
    if found:
        for f in found:
            lines.append(f"    {os.path.basename(f)}")
    else:
        lines.append(f"    (none found in {src} — copy 1.0's secrets there first, or pass --secrets-src)")
    lines.append("state.json writes:  sheet_id=<new sheet id>,  drive_setup_url=<_setup folder link>")
    return "\n".join(lines)


def _find_or_create_root(svc):
    """Find-or-create the My-Drive root folder by name. Fails loudly on >=2 same-name roots."""
    name = _root_name()
    hits = [f for f in D._q(svc, f"mimeType='{D.FOLDER_MIME}' and trashed=false")
            if f.get("name") == name]
    if len(hits) > 1:
        sys.exit(f"[provision] {len(hits)} Drive folders named {name!r} already exist — "
                 f"resolve the ambiguity (trash the extras) and re-run:\n" +
                 "\n".join(f"    {h['id']}" for h in hits))
    if hits:
        print(f"[provision] root exists: {name}  ({hits[0]['id']})")
        return hits[0]["id"]
    fid = svc.files().create(body={"name": name, "mimeType": D.FOLDER_MIME},
                             fields="id", supportsAllDrives=True).execute()["id"]
    print(f"[provision] created root: {name}  ({fid})")
    return fid


def _ensure_subtree(svc, root_id):
    """Create every subtree folder (idempotent), returning {relpath: id}."""
    cache = {"": root_id}

    def ensure(rel):
        if rel in cache:
            return cache[rel]
        parent = ensure(os.path.dirname(rel)) if os.path.dirname(rel) else root_id
        before = {f["name"] for f in D._q(svc, f"mimeType='{D.FOLDER_MIME}' and '{parent}' in parents and trashed=false")}
        cache[rel] = D.ensure_folder(svc, os.path.basename(rel), parent)
        print(f"  {'exists' if os.path.basename(rel) in before else 'created'}: {rel}/")
        return cache[rel]

    for p in _subtree():
        ensure(p)
    return cache


def _find_or_create_sheet(svc, root_id):
    """Find-or-create the tracker spreadsheet INSIDE the root."""
    name = _root_name()
    hits = [f for f in D._q(svc, f"mimeType='application/vnd.google-apps.spreadsheet' and "
                                 f"name='{name}' and '{root_id}' in parents and trashed=false")]
    if hits:
        print(f"[provision] spreadsheet exists: {name}  ({hits[0]['id']})")
        return hits[0]["id"]
    sid = svc.files().create(body={"name": name,
                                   "mimeType": "application/vnd.google-apps.spreadsheet",
                                   "parents": [root_id]},
                             fields="id", supportsAllDrives=True).execute()["id"]
    print(f"[provision] created spreadsheet: {name}  ({sid})")
    return sid


def _share_with_sa(svc, file_id, label):
    email = _sa_email()
    if not email:
        print(f"  [warn] no SA json at repo root — cannot auto-share {label} (share it by hand)", file=sys.stderr)
        return
    try:
        svc.permissions().create(fileId=file_id,
                                 body={"type": "user", "role": "writer", "emailAddress": email},
                                 sendNotificationEmail=False, supportsAllDrives=True).execute()
        print(f"  shared {label} (Editor) with {email}")
    except Exception as e:
        # already-shared or benign — report and continue
        print(f"  [info] share {label} with {email}: {type(e).__name__} (may already have access)", file=sys.stderr)


def _write_state(sheet_id, setup_url):
    """Write sheet_id + drive_setup_url (+ updated) into state.json, preserving its formatting."""
    sp = os.path.join(D._root(), "state.json")
    txt = open(sp, encoding="utf-8").read()
    orig = txt
    txt = re.sub(r'("sheet_id"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(sheet_id), txt, count=1)
    txt = re.sub(r'("drive_setup_url"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(setup_url), txt, count=1)
    txt = re.sub(r'("updated"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(S._today()), txt, count=1)
    try:
        json.loads(txt)                       # never write a corrupt state.json
    except Exception as e:
        sys.exit(f"[provision] refusing to write state.json (would be invalid JSON: {e}). "
                 f"Set sheet_id + drive_setup_url by hand.")
    if txt == orig:
        print("[provision] state.json already current (no change)")
        return
    with open(sp, "w", encoding="utf-8") as f:
        f.write(txt)
    print(f"[provision] state.json updated (sheet_id + drive_setup_url)")


def cmd_create(a):
    src = os.path.abspath(a.secrets_src) if a.secrets_src else D._root()
    if a.dry_run:
        print("== provision create — DRY RUN (no network calls) ==")
        print(f"secrets source: {src}")
        print(_plan_text())
        print("\n(dry-run) nothing was created. Re-run without --dry-run to provision.")
        return
    try:
        svc = D._service()
    except SystemExit as e:
        _manual_fallback(str(e)); sys.exit(1)
    except Exception as e:
        _manual_fallback(f"{type(e).__name__}: {e}"); sys.exit(1)
    try:
        root_id = _find_or_create_root(svc)
        print("[provision] ensuring subtree…")
        cache = _ensure_subtree(svc, root_id)
        setup_id = cache["_setup"]
        sheet_id = _find_or_create_sheet(svc, root_id)
        _share_with_sa(svc, sheet_id, "spreadsheet")
        _share_with_sa(svc, root_id, "root folder")
        # upload the secrets bundle into _setup/
        secrets = _secret_files(src)
        if not secrets:
            print(f"  [warn] no secret files found in {src} — copy keys.env + the *.json creds there, "
                  f"then re-run (or upload into _setup/ by hand)", file=sys.stderr)
        for p in secrets:
            print(f"  {D.upload_file(svc, p, setup_id)}: _setup/{os.path.basename(p)}")
        setup_url = f"https://drive.google.com/drive/folders/{setup_id}"
        _write_state(sheet_id, setup_url)
    except Exception as e:
        _manual_fallback(f"{type(e).__name__}: {e}"); sys.exit(1)
    print("\n[provision] create done. Next:")
    print("  1. python3 engine/sheets/sheets.py init         # build the tabs + Dashboard + Dictionary")
    print("  2. python3 engine/setup/provision.py seed-markers   # anchor 2.0 numbering to 1.0")
    print(f"  Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")


# ── seed-markers ──────────────────────────────────────────────────────────────
def cmd_seed_markers(a):
    old_id = a.old_sheet_id or OLD_SHEET_ID
    try:
        gc = S._client()                      # gspread authorized with the SA
    except SystemExit as e:
        sys.exit(str(e))
    try:
        old = gc.open_by_key(old_id)
    except Exception as e:
        sys.exit(f"[provision] cannot open the 1.0 Sheet {old_id} with the SA ({type(e).__name__}: {e}). "
                 f"Confirm the SA has read access to it.")
    new = S._open()                           # 2.0 sheet (errors cleanly if sheet_id is empty)
    added = missing = 0
    for key, c in S._characters().items():
        tab, prefix = c["tab"], c["id_prefix"]
        nws = S._ws(new, tab)
        if nws is None:
            print(f"[provision] new sheet has no {tab!r} tab — run `python3 engine/sheets/sheets.py init` first",
                  file=sys.stderr)
            missing += 1
            continue
        ows = S._ws(old, tab)
        if ows is None:
            print(f"[provision] (1.0 Sheet has no {tab!r} tab — no marker for {key})")
            continue
        pre = prefix + "-"
        mx, mx_str = -1, None
        for v in ows.col_values(1):
            v = (v or "").strip()
            if v.startswith(pre) and v[len(pre):].isdigit():
                n = int(v[len(pre):])
                if n >= mx:
                    mx, mx_str = n, v
        if mx_str is None:
            mx_str = f"{prefix}-00"            # 1.0 had none -> anchor so 2.0 starts at 01
        if S._row_for_id(nws, mx_str) is not None:
            print(f"[provision] {tab}: marker {mx_str} already present — skipping")
            continue
        headers = S.HEADERS[tab]
        note = f"IDs continue from the 1.0 Sheet: https://docs.google.com/spreadsheets/d/{old_id}"
        rowvals = {"ID": mx_str, "Title": "(1.0 era marker)", "Notes": note,
                   "Date Created": S._today()}   # Framework EMPTY -> ignored by rotation/next-slot
        nws.append_row([rowvals.get(h, "") for h in headers],
                       value_input_option="USER_ENTERED", table_range="A2")
        added += 1
        print(f"[provision] {tab}: seeded marker {mx_str}  (2.0 next id -> {prefix}-{mx + 1 if mx >= 0 else 1:02d})")
    if missing:
        sys.exit(f"[provision] {missing} fact tab(s) missing — run `sheets.py init`, then re-run seed-markers")
    print(f"[provision] seed-markers done — {added} marker row(s) added (source: {old_id})")


def main():
    p = argparse.ArgumentParser(description="Project Ana 2.0 one-time cloud provisioning")
    sub = p.add_subparsers(dest="cmd", required=True)

    cr = sub.add_parser("create", help="find-or-create the Drive root + subtree + Sheet + _setup secrets")
    cr.set_defaults(fn=cmd_create)
    cr.add_argument("--secrets-src", help="dir holding keys.env + the *.json creds (default: the repo root)")
    cr.add_argument("--dry-run", action="store_true", help="print the plan without any network calls")

    sm = sub.add_parser("seed-markers", help="anchor 2.0 numbering to the 1.0 Sheet's per-character maxes")
    sm.set_defaults(fn=cmd_seed_markers)
    sm.add_argument("--old-sheet-id", help=f"1.0 Sheet id to read (default: {OLD_SHEET_ID})")

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
