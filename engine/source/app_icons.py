#!/usr/bin/env python3
"""Fetch real App Store icons for named apps (frameworks-test sandbox).

Uses the public iTunes Search API (no key): itunes.apple.com/search?term=..&entity=software,
takes the best name-matched result's artworkUrl512, and saves a real PNG to
  media/graded/app_<slug>.png
These are fixed brand assets (App Store artwork), not place-keyed UGC, so they do NOT get a
media/manifest.json entry — the manifest is the sourced-UGC library index.

Usage:
  python3 engine/source/app_icons.py "DeepL" "Google Translate"
  python3 engine/source/app_icons.py --country us "Notion"
"""
import os, io, sys, argparse, difflib, urllib.parse
import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root(start):
    """Walk UP from `start` to the dir carrying the .gitignore sentinel (repo root),
    same trick as engine/lib/keys.py's keys.env discovery."""
    d = start
    while True:
        if os.path.exists(os.path.join(d, ".gitignore")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return start
        d = parent


REPO = _find_repo_root(HERE)
GRADED = os.path.join(REPO, "media", "graded")
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")


def slugify(s):
    out = []
    for ch in (s or "").lower().strip():
        out.append(ch if ch.isalnum() else "-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "app"


def lookup(term, country="us", limit=8):
    params = {"term": term, "entity": "software", "limit": limit, "country": country}
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(params)
    r = requests.get(url, headers={"User-Agent": BROWSER_UA}, timeout=30)
    r.raise_for_status()
    return r.json().get("results", [])


def best_match(results, term):
    """Prefer exact (case-insensitive) trackName, else best fuzzy ratio, else first."""
    if not results:
        return None
    tl = term.lower()
    for res in results:
        if (res.get("trackName") or "").lower() == tl:
            return res
    scored = sorted(results, key=lambda r: difflib.SequenceMatcher(
        None, tl, (r.get("trackName") or "").lower()).ratio(), reverse=True)
    return scored[0]


def art_url(res):
    return res.get("artworkUrl512") or res.get("artworkUrl100") or res.get("artworkUrl60")


def fetch_icon(term, country="us"):
    results = lookup(term, country)
    res = best_match(results, term)
    if not res:
        return {"term": term, "status": "no-result"}
    url = art_url(res)
    if not url:
        return {"term": term, "status": "no-artwork", "matched": res.get("trackName")}
    r = requests.get(url, headers={"User-Agent": BROWSER_UA}, timeout=30, verify=True)
    r.raise_for_status()
    try:
        im = Image.open(io.BytesIO(r.content))
        im.load()
    except Exception as e:
        return {"term": term, "status": "undecodable", "err": type(e).__name__}
    slug = slugify(term)
    os.makedirs(GRADED, exist_ok=True)
    dest = os.path.join(GRADED, "app_%s.png" % slug)
    im.convert("RGBA").save(dest, "PNG")
    return {"term": term, "status": "ok", "matched": res.get("trackName"),
            "bundle": res.get("bundleId"), "w": im.size[0], "h": im.size[1],
            "path": os.path.relpath(dest, REPO), "art": url}


def main():
    ap = argparse.ArgumentParser(prog="app_icons.py")
    ap.add_argument("apps", nargs="+", help="app names, e.g. DeepL \"Google Translate\"")
    ap.add_argument("--country", default="us")
    a = ap.parse_args()
    ok = 0
    for term in a.apps:
        try:
            res = fetch_icon(term, a.country)
        except Exception as e:
            res = {"term": term, "status": "error", "err": "%s: %s" % (type(e).__name__, e)}
        if res.get("status") == "ok":
            ok += 1
            print("ok   %-18s -> %s  %dx%d  match=%r bundle=%s"
                  % (term, res["path"], res["w"], res["h"], res["matched"], res["bundle"]))
        else:
            print("FAIL %-18s -> %s  %s" % (term, res.get("status"), res.get("err", res.get("matched", ""))))
    print("done: %d/%d icons saved -> media/graded/" % (ok, len(a.apps)))


if __name__ == "__main__":
    main()
