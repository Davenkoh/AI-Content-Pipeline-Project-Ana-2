#!/usr/bin/env python3
"""Populate a post's _work/cover/to_upload/ with the persona IDENTITY references that gpt_prep.js
attaches to the ChatGPT cover prompt.

gpt_prep.js expects exactly three files in cover/to_upload/ named 1_<Persona>_hero_front.png,
2_<Persona>_face_closeup.png, 3_<Persona>_half_front.png. This copies them from
character/<Persona>/Base References/ (matched by keyword, tolerant of filename quirks like a
trailing space or the numbering prefix), so a fresh teammate's cover gen does not fail with a
missing-file error.

The persona's Base References must be present locally first. git clone gives the persona .md;
`bootstrap` (or `drive_sync.py --pull character --to character`) fills in the images from Drive.

Run from anywhere:
  python3 engine/design/prep_cover_refs.py "outputs/NN - Title/_work/cover" [--persona Ana]
"""
import argparse, glob, os, shutil, sys

# keyword in the Base-Reference filename -> (slot index, role used in the to_upload name).
# Match is lenient (normalized, case/space/dash-insensitive, substring), so casual names like
# "Hero shot.png", "close up.png", or "Ana_07_SOLO_half-front.png" all resolve to the right slot.
SLOTS = [("hero", 1, "hero_front"),
         ("closeup", 2, "face_closeup")]
# Optional anchors: staged + attached ONLY if present (gpt_prep attaches every staged ref). "half" is a
# half-body front — the SAME framing as the hero — so it's OPTIONAL now (drop it when it just duplicates
# the hero, as for Chloe). "vary" is a 3/4-angles + expression sheet (side-view + smiling coverage so
# varied covers stay on-identity). Both keywords are distinct from Ana's "angles"/"expressions"/"sheet"
# filenames, so a character without a dedicated ref is never silently changed. Required = hero + closeup.
OPT_SLOTS = [("half", 3, "half_front"),
             ("vary", 4, "vary_angles_expr")]
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def _norm(s):
    return s.lower().replace("-", "").replace(" ", "")


def find_ref(base_dir, keyword):
    needle = _norm(keyword)
    hits = [f for f in glob.glob(os.path.join(base_dir, "*"))
            if f.lower().endswith(IMG_EXT) and needle in _norm(os.path.basename(f))]
    return sorted(hits)[0] if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cover_dir", help="the post's _work/cover directory")
    ap.add_argument("--persona", default="Ana")
    a = ap.parse_args()
    base = os.path.join(_root(), "character", a.persona, "Base References")
    if not os.path.isdir(base):
        sys.exit(f"[prep_cover_refs] no 'Base References' for persona {a.persona!r} at:\n  {base}\n"
                 f"  pull them first:  python3 engine/drive/drive_sync.py --pull character --to character")
    up = os.path.join(a.cover_dir, "to_upload")
    os.makedirs(up, exist_ok=True)
    missing = []
    n = 0
    for keyword, idx, role in SLOTS:
        src = find_ref(base, keyword)
        if not src:
            missing.append(keyword)
            continue
        dst = os.path.join(up, f"{idx}_{a.persona}_{role}.png")
        shutil.copy2(src, dst)
        n += 1
        print(f"  {os.path.basename(src)}  ->  {os.path.relpath(dst, _root())}")
    if missing:
        sys.exit(f"[prep_cover_refs] could not find a Base Reference for: {missing}\n  in {base}")
    for keyword, idx, role in OPT_SLOTS:                       # optional extras — stage only if present
        src = find_ref(base, keyword)
        if src:
            dst = os.path.join(up, f"{idx}_{a.persona}_{role}.png")
            shutil.copy2(src, dst)
            n += 1
            print(f"  (optional) {os.path.basename(src)}  ->  {os.path.relpath(dst, _root())}")
    print(f"[prep_cover_refs] {a.persona}: {n} identity refs ready in {os.path.relpath(up, _root())}")


if __name__ == "__main__":
    main()
