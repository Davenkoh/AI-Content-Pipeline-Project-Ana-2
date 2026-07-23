#!/usr/bin/env python3
"""Central API-key loader for the Masquerade / Holicay sourcing pipeline.

Single source of truth = `keys.env` (KEY=VALUE lines), found by walking UP from
this file's location until it's found — so it works whether this loader runs from
`Pipeline Engine/` or from any post's `_work/scripts/`. Environment variables of the
same name take precedence over the file. This module holds NO secrets, so it is safe
to duplicate next to every script (the secrets live only in keys.env).

Usage:
    from keys import get as _keys
    PEXELS = _keys("PEXELS")
or simply:
    import keys
    keys.PEXELS            # also works (lazy module attribute)
"""
import os

_CANON = ("PEXELS", "UNSPLASH", "SERP", "PLACES", "SCRAPE_TOKEN", "BRIGHTDATA", "APIFY")
_cache = None


def _find_env():
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        p = os.path.join(d, "keys.env")
        if os.path.exists(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:          # reached filesystem root
            return None
        d = parent


def _load():
    global _cache
    if _cache is not None:
        return _cache
    _cache = {}
    p = _find_env()
    if p:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                _cache[k.strip()] = v.strip().strip('"').strip("'")
    return _cache


def get(name):
    """Return the key `name`, env var first, then keys.env. Raises if missing."""
    v = os.environ.get(name)
    if v:
        return v
    v = _load().get(name)
    if not v:
        raise KeyError(
            f"API key '{name}' not found. Add it to keys.env at the repo root "
            f"(or export {name}=...). Looked up starting from {os.path.abspath(__file__)}."
        )
    return v


def __getattr__(name):          # lets `keys.PEXELS` / `from keys import PEXELS` work too
    if name in _CANON:
        return get(name)
    raise AttributeError(name)
