#!/usr/bin/env python3
"""File the images a human dropped in inbox/ into their PERMANENT home (wardrobe by default),
auto-numbered, then push to Drive — so a dropped outfit becomes a filed, numbered, synced wardrobe
reference instead of being archived to _used. This is what WORKFLOW §7 runs after the user drops an
outfit you asked for. Drive stays canonical: the push uses `--prune`, so the Drive folder ends up
an EXACT mirror of the local one (numbering + deletions included).

  python3 engine/qc/file_inbox.py                 # file all inbox images -> Wardrobe References/, numbered, push to Drive
  python3 engine/qc/file_inbox.py --to brand      # file into media/brand/logos/ instead
  python3 engine/qc/file_inbox.py --renumber      # also renumber existing non-numeric files in the target (normalize)
  python3 engine/qc/file_inbox.py --no-push       # file locally only; skip the Drive mirror+prune
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

# name -> (local target dir = also the mirror source, Drive nested dest under the shared root)
TARGETS = {
    "wardrobe": ("character/_shared/Wardrobe References", "_shared/Wardrobe References"),
    "brand":    ("media/brand/logos", "media/brand/logos"),
}
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def _num(name):
    m = re.match(r"(\d+)\.", name)
    return int(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", default="wardrobe", help="wardrobe | brand | <relpath under the repo>")
    ap.add_argument("--renumber", action="store_true", help="also renumber existing non-numeric files in the target")
    ap.add_argument("--no-push", action="store_true", help="file locally only; skip the Drive mirror+prune")
    a = ap.parse_args()
    root = _root()
    tgt_rel, dest = TARGETS.get(a.to, (a.to, os.path.basename(a.to.rstrip("/"))))
    tgt = os.path.join(root, tgt_rel)
    os.makedirs(tgt, exist_ok=True)
    inbox = os.path.join(root, "inbox")
    drops = ([f for f in sorted(os.listdir(inbox)) if f.lower().endswith(IMG_EXT)]
             if os.path.isdir(inbox) else [])

    nums = [n for n in (_num(f) for f in os.listdir(tgt)) if n is not None]
    nxt = (max(nums) + 1) if nums else 1
    moved = 0

    if a.renumber:                                        # normalize existing hash/screenshot names -> numbers
        loose = sorted(f for f in os.listdir(tgt)
                       if f.lower().endswith(IMG_EXT) and _num(f) is None)
        for f in loose:
            ext = os.path.splitext(f)[1].lower()
            os.rename(os.path.join(tgt, f), os.path.join(tgt, f"{nxt}{ext}"))
            print(f"  renumber: {f}  ->  {nxt}{ext}")
            nxt += 1
            moved += 1

    for f in drops:                                       # file the inbox drops
        ext = os.path.splitext(f)[1].lower()
        shutil.move(os.path.join(inbox, f), os.path.join(tgt, f"{nxt}{ext}"))
        print(f"  filed: inbox/{f}  ->  {tgt_rel}/{nxt}{ext}")
        nxt += 1
        moved += 1

    if not moved:
        print("[file-inbox] nothing to file")
        return
    print(f"[file-inbox] {moved} file(s) -> {tgt_rel}/")

    if not a.no_push:
        ds = os.path.join(root, "engine", "drive", "drive_sync.py")
        print(f"[file-inbox] pushing {dest}/ to Drive (mirror + prune → exact match)…")
        subprocess.run([sys.executable, ds, "--mirror", tgt, "--dest", dest, "--prune"])


if __name__ == "__main__":
    main()
