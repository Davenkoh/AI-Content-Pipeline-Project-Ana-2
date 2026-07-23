#!/usr/bin/env python3
"""Clear ONE-OFF leftovers from inbox/ after a run (success OR failure).

REUSABLE drops — an outfit, a brand asset — should be FILED to their permanent home first via
`engine/qc/file_inbox.py` (which numbers them + pushes to Drive so Drive stays canonical). This only
sweeps whatever genuinely one-off scratch is left, so nothing piles up.

Why this exists: the pipeline only ever *fills* inbox/ (WORKFLOW §7), and the cover gen consumes a
drop by LOOKING at it (vision) rather than moving it, so nothing ever leaves the folder on its own.
This is the explicit sweep.

Filename-agnostic on purpose: it clears EVERYTHING except README.txt (and dotfiles / the _used
archive). The macOS screenshot gotcha — a U+202F narrow no-break space before AM/PM — means a literal
"... PM.png" glob would silently miss exactly those files; matching by "not README" sidesteps it.

Default: MOVE cleared items into inbox/_used/<timestamp>/ (gitignored, recoverable). Pass --delete to
remove them outright.

Run:  python3 engine/qc/clear_inbox.py [--delete]
"""
import datetime
import os
import shutil
import sys

KEEP = {"README.txt", "_used"}


def _root():
    p = os.path.dirname(os.path.abspath(__file__))
    while p != os.path.dirname(p):
        if os.path.exists(os.path.join(p, ".gitignore")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()


def main():
    delete = "--delete" in sys.argv
    inbox = os.path.join(_root(), "inbox")
    if not os.path.isdir(inbox):
        print("[clear-inbox] no inbox/ — nothing to do")
        return
    items = [n for n in os.listdir(inbox) if n not in KEEP and not n.startswith(".")]
    if not items:
        print("[clear-inbox] inbox already clean")
        return
    dest = None
    if not delete:
        dest = os.path.join(inbox, "_used", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(dest, exist_ok=True)
    n = 0
    for name in items:
        src = os.path.join(inbox, name)
        if delete:
            shutil.rmtree(src) if os.path.isdir(src) else os.remove(src)
        else:
            shutil.move(src, os.path.join(dest, name))
        n += 1
    where = "deleted" if delete else f"archived -> inbox/_used/{os.path.basename(dest)}/"
    print(f"[clear-inbox] cleared {n} item(s) ({where})")


if __name__ == "__main__":
    main()
