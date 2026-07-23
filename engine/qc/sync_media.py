#!/usr/bin/env python3
"""Sync local media -> Drive, JUST IN TIME (the clone-model auto-push).

  python3 engine/qc/sync_media.py --if-changed   # cheap: fingerprint media; push ONLY if it changed
  python3 engine/qc/sync_media.py                 # always push

`--if-changed` is wired to the Claude **Stop hook** (.claude/settings.local.json), so any session that
touches the media files auto-syncs to Drive as each turn finishes — no daemon, no watcher. On a turn
that didn't touch media it's a sub-second no-op. Fails SOFT: a push error prints a warning and exits 0,
so it never breaks the turn. For a FULL reconcile (media + posts + inspo) run `./sync.sh`.
"""
import hashlib
import os
import subprocess
import sys

WATCH_DIRS = ["character/_shared", "knowledge/brand", "inspo"]
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


ROOT = _root()
STATE = os.path.join(ROOT, ".sync_state")


def _dirs():
    out = [os.path.join(ROOT, w) for w in WATCH_DIRS]
    ch = os.path.join(ROOT, "character")
    if os.path.isdir(ch):
        for name in os.listdir(ch):
            for sub in ("Base References", "Profile Pictures"):
                out.append(os.path.join(ch, name, sub))
    return [p for p in out if os.path.isdir(p)]


def _fingerprint():
    sig = []
    for d in _dirs():
        for cur, _sub, files in os.walk(d):
            for f in files:
                if f.lower().endswith(IMG_EXT):
                    try:
                        st = os.stat(os.path.join(cur, f))
                        sig.append(f"{os.path.join(cur, f)}|{int(st.st_mtime)}|{st.st_size}")
                    except OSError:
                        pass
    h = hashlib.md5()
    for line in sorted(sig):
        h.update(line.encode())
    return h.hexdigest()


def main():
    fp = _fingerprint()
    if "--if-changed" in sys.argv:
        try:
            if open(STATE).read().strip() == fp:
                return                                  # nothing changed since last sync — fast no-op
        except OSError:
            pass
    print("[sync-media] media changed -> syncing to Drive…", flush=True)
    try:
        subprocess.run([sys.executable, os.path.join(ROOT, "engine", "drive", "drive_sync.py"),
                        "--mirror-all", "--prune"], check=True)
        with open(STATE, "w") as f:
            f.write(fp)
        print("[sync-media] synced. Drive mirrors local.", flush=True)
    except Exception as e:
        print(f"[sync-media] WARNING: sync failed ({e}) — run ./sync.sh when back online.", file=sys.stderr)


if __name__ == "__main__":
    main()
