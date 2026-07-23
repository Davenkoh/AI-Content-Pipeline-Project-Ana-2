#!/usr/bin/env python3
"""Sandboxed photo-sourcing CLI (frameworks-test) — Bright Data + SerpAPI + Apify.

STANDALONE: does not import engine/. Reads keys the same way the engine does
(keys.env at repo root, env var of the same name overrides). NEVER prints key
values — keys are referenced by env-var name only (BRIGHTDATA / PLACES / SERP / APIFY).

READ-ONLY against the Bright Data account: this tool only *probes* (get_active_zones)
and makes *request-usage* calls through existing zones. It never creates, edits, or
deletes zones / datasets / settings. If a product is missing it says what a human
must click, it does not provision it.

Subcommands
  probe                          authenticate, list active zones, classify usable products
  places  --query Q --subject S --category C [--n 8] [--download K] [--hl en --gl jp]
                                 Google Places user-review photos (predominantly visitor-uploaded
                                 = real UGC framing). Works TODAY with the PLACES key, zero Bright
                                 Data setup. Text Search -> place_id -> Details(photos) -> media 1600px.
  gimg    --query Q --subject S --category C [--n 8] [--download K] [--hl en --gl us]
  greviews --place P --subject S --category C [--n 6]
  fetch   --url U --subject S --category C --query Q [--source-url SU] [--author A]
          [--platform google_images] [--license ugc-unlicensed]
  ig      --query Q --subject S --category C [--n 12] [--download K] [--mode M] [--url U] [--frames 2]
                                 Instagram post photos via Apify public actors (api.apify.com/v2).
                                 THE Instagram backend (real people's posts = primary UGC). --query is
                                 a #hashtag / single token / venue name -> hashtag search; --mode
                                 url|user routes profile/post URLs through the general scraper.
  ig-bd   --query Q             [alt] Instagram via Bright Data's Web Scraper dataset — KYC-gated on
                                 this account (HTTP 400 "Customer is not active"); kept for when the
                                 social-data compliance unlock is approved.

Downloads land in  media/library/<subject-slug>/<id>.jpg  and every saved byte
appends an entry to  media/manifest.json  (id = first 8 hex of sha256). Images
smaller than 700px on the short side are skipped; duplicates (by sha256) are skipped.
"""
import os, sys, io, re, json, ssl, time, hashlib, argparse, datetime, urllib.parse
import requests
from requests.adapters import HTTPAdapter
try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass
from PIL import Image

# ------------------------------------------------------------------ paths
HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo_root(start):
    """Walk UP from `start` until a dir carries the .gitignore sentinel (same trick as
    engine/lib/keys.py's keys.env discovery); that dir is the repo root."""
    d = start
    while True:
        if os.path.exists(os.path.join(d, ".gitignore")):
            return d
        parent = os.path.dirname(d)
        if parent == d:            # reached filesystem root without a sentinel
            return start
        d = parent


REPO = _find_repo_root(HERE)                       # repo root (holds media/, keys.env, engine/)
MEDIA = os.path.join(REPO, "media")
LIBRARY = os.path.join(MEDIA, "library")
GRADED = os.path.join(MEDIA, "graded")
MANIFEST = os.path.join(MEDIA, "manifest.json")
MIN_SHORT_SIDE = 700

BD_API = "https://api.brightdata.com"
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

# ------------------------------------------------------------------ keys (standalone copy of engine/lib/keys.py behaviour)
_KEYS = None


def _find_env(start):
    d = start
    while True:
        p = os.path.join(d, "keys.env")
        if os.path.exists(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def keys(name):
    """env var first, then keys.env (walked up from here). Raises if missing."""
    global _KEYS
    v = os.environ.get(name)
    if v:
        return v
    if _KEYS is None:
        _KEYS = {}
        p = _find_env(HERE)
        if p:
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, val = line.split("=", 1)
                    _KEYS[k.strip()] = val.strip().strip('"').strip("'")
    v = _KEYS.get(name)
    if not v:
        raise KeyError("key %s not found (add to keys.env at repo root or export %s)" % (name, name))
    return v


def has_key(name):
    try:
        keys(name)
        return True
    except Exception:
        return False


# ------------------------------------------------------------------ http session
_S = requests.Session()
_S.mount("https://", HTTPAdapter(max_retries=1))
_S.mount("http://", HTTPAdapter(max_retries=1))


def _bd_headers():
    # Authorization built here and never logged.
    return {"Authorization": "Bearer " + keys("BRIGHTDATA"), "Content-Type": "application/json"}


def slugify(s):
    s = (s or "").lower().strip()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
        elif ch in " /_-.":
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "misc"


def domain_of(url):
    try:
        return urllib.parse.urlparse(url).netloc or ""
    except Exception:
        return ""


# ================================================================== Bright Data: zone discovery
def get_active_zones():
    """GET /zone/get_active_zones -> list of {name, type, ...}. Raises on auth/HTTP error."""
    r = _S.get(BD_API + "/zone/get_active_zones", headers=_bd_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    # API historically returns a bare list; tolerate {"zones":[...]} too.
    if isinstance(data, dict):
        data = data.get("zones") or data.get("data") or []
    return data if isinstance(data, list) else []


def _classify_zone(z):
    t = (z.get("type") or z.get("plan", {}).get("type") if isinstance(z.get("plan"), dict) else z.get("type")) or ""
    t = str(t).lower()
    if "serp" in t:
        return "serp"
    if "unblock" in t or "unlock" in t:
        return "unlocker"
    if "res" in t:
        return "residential"
    if t in ("dc", "static", "isp", "datacenter"):
        return "datacenter"
    if "scrap" in t or "browser" in t:
        return "browser"
    return t or "unknown"


_ZONES_CACHE = None


def discover_zones():
    """Return {'serp': name|None, 'unlocker': name|None, 'all': [(name,type,kind)], 'error': str|None}."""
    global _ZONES_CACHE
    if _ZONES_CACHE is not None:
        return _ZONES_CACHE
    out = {"serp": None, "unlocker": None, "all": [], "error": None}
    try:
        zones = get_active_zones()
    except requests.HTTPError as e:
        out["error"] = "HTTP %s from get_active_zones" % (e.response.status_code if e.response is not None else "?")
        _ZONES_CACHE = out
        return out
    except Exception as e:
        out["error"] = "%s: %s" % (type(e).__name__, e)
        _ZONES_CACHE = out
        return out
    for z in zones:
        name = z.get("name") or z.get("zone") or ""
        rawt = z.get("type") or ""
        kind = _classify_zone(z)
        out["all"].append((name, rawt, kind))
        if kind == "serp" and not out["serp"]:
            out["serp"] = name
        if kind == "unlocker" and not out["unlocker"]:
            out["unlocker"] = name
    _ZONES_CACHE = out
    return out


def bd_status():
    """GET /status -> {status, customer, can_make_requests, auth_fail_reason, ip}. (dict, err)."""
    try:
        r = _S.get(BD_API + "/status", headers=_bd_headers(), timeout=20)
        if r.status_code == 200:
            return r.json(), None
        return None, "HTTP %s" % r.status_code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)


def list_catalog():
    """GET /datasets/list -> the Web Scraper API *marketplace catalog* (NOT owned/triggerable
    by this account without billing). Entries are {id, name, size}. Returns (list, err)."""
    try:
        r = _S.get(BD_API + "/datasets/list", headers=_bd_headers(), timeout=30)
        if r.status_code == 200:
            j = r.json()
            if isinstance(j, dict):
                j = j.get("datasets") or j.get("data") or []
            return (j if isinstance(j, list) else []), None
        return None, "HTTP %s" % r.status_code
    except Exception as e:
        return None, "%s: %s" % (type(e).__name__, e)


def catalog_find(cat, *keywords):
    """Case-insensitive AND-match of keywords against a catalog entry's name."""
    out = []
    for d in cat or []:
        name = (d.get("name") or "").lower()
        if all(k in name for k in keywords):
            out.append(d)
    return out


# ------------------------------------------------------------------ Web Scraper API (v3) datasets
# Confirmed dataset ids (from /datasets/list on this account, 2026-07-22):
DATASET_IG_POSTS = "gd_lk5ns7kz21pck8jpis"       # "Instagram - Posts"
DATASET_GMAPS_REVIEWS = "gd_luzfs1dn2oa0teb81"   # "Google maps reviews"
# NOTE: there is NO /datasets/v3/list endpoint (404). The catalog list is GET /datasets/list.
# Collection is the v3 lifecycle: trigger -> progress(poll) -> snapshot(fetch).


def bd_trigger(dataset_id, inputs, extra_qs=""):
    """POST /datasets/v3/trigger -> (snapshot_id|None, http_status, err_body_verbatim).
    `inputs` is a list of input dicts. Rejection bodies are captured verbatim (never the token)."""
    url = BD_API + "/datasets/v3/trigger?dataset_id=%s&include_errors=true%s" % (dataset_id, extra_qs)
    r = _S.post(url, headers=_bd_headers(), json=inputs, timeout=60)
    if r.status_code == 200:
        try:
            return (r.json() or {}).get("snapshot_id"), 200, None
        except Exception:
            return None, 200, "200 but no snapshot_id in body"
    return None, r.status_code, (r.text or "").strip()[:600]


def bd_poll(snapshot_id, budget_s=240, interval=15):
    """Poll /datasets/v3/progress until ready/failed/error or budget. Returns (status, elapsed_s)."""
    t0 = time.time()
    status = None
    while time.time() - t0 < budget_s:
        try:
            r = _S.get(BD_API + "/datasets/v3/progress/%s" % snapshot_id, headers=_bd_headers(), timeout=30)
            status = (r.json() or {}).get("status")
        except Exception:
            status = None
        if status in ("ready", "failed", "error"):
            break
        time.sleep(interval)
    return status, int(time.time() - t0)


def bd_snapshot(snapshot_id):
    """GET /datasets/v3/snapshot?format=json -> (records_list, err)."""
    r = _S.get(BD_API + "/datasets/v3/snapshot/%s?format=json" % snapshot_id,
               headers=_bd_headers(), timeout=90)
    if r.status_code != 200:
        return None, "HTTP %s: %s" % (r.status_code, (r.text or "")[:200])
    try:
        d = r.json()
    except Exception:
        return None, "non-json snapshot body"
    return (d if isinstance(d, list) else [d]), None


def _first(rec, *keys):
    """First present, non-empty value among keys (supports dotted 'a.b')."""
    for k in keys:
        cur, ok = rec, True
        for part in k.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                ok = False
                break
        if ok and cur not in (None, "", [], {}):
            return cur
    return None


def _collect_image_urls(value):
    """Normalize a photo field (str | [str] | [{url|image|src|link}]) into a flat [str] list."""
    out = []
    if isinstance(value, str):
        if value.startswith("http"):
            out.append(value)
    elif isinstance(value, list):
        for it in value:
            if isinstance(it, str) and it.startswith("http"):
                out.append(it)
            elif isinstance(it, dict):
                u = it.get("url") or it.get("image") or it.get("src") or it.get("link") or it.get("photo_url")
                if isinstance(u, str) and u.startswith("http"):
                    out.append(u)
    return out


def extract_review_images(rec):
    """One Google-Maps-review record -> [(image_url, author, source_url)]. Broad field fallbacks
    so it survives schema drift (confirmed field names are tried first)."""
    author = _first(rec, "reviewer_name", "author_name", "user_name", "name") or ""
    src = _first(rec, "review_url", "url", "review_link", "link", "place_url") or ""
    photos = _first(rec, "review_photos", "photos", "review_image_urls", "images",
                    "photos_urls", "review_images", "photo_url", "image")
    return [(u, author, src) for u in _collect_image_urls(photos)]


def extract_ig_images(rec):
    """One Instagram-Posts record -> [(image_url, @handle, post_url)]. Broad fallbacks."""
    handle = _first(rec, "user_posted", "username", "owner_username", "profile_name", "ownerUsername") or ""
    if handle and not handle.startswith("@"):
        handle = "@" + handle
    src = _first(rec, "url", "post_url", "link", "permalink") or ""
    photos = _first(rec, "photos", "display_url", "image_url", "images", "thumbnail", "photo",
                    "display_resources", "image_urls")
    return [(u, handle, src) for u in _collect_image_urls(photos)]


# ================================================================== Apify (Instagram UGC backend)
# THE Instagram backend. Bright Data's IG scraper is KYC-gated on our account (see cmd_ig_bd), so
# Instagram posts are sourced via Apify's public actors (https://api.apify.com/v2). Verified working
# 2026-07-22 on a FREE-plan token: the HASHTAG scraper returns real posts+images; the general scraper
# returns posts for profile/post `directUrls`. IG *location* scraping returns venue metadata only
# (empty `posts`) on this actor version, so a venue name is matched via its #hashtag (see _ig_plan).
# Auth is a Bearer header built from the APIFY key and NEVER logged.
APIFY_API = "https://api.apify.com/v2"
ACTOR_IG_HASHTAG = "apify~instagram-hashtag-scraper"   # input: {hashtags:[..], resultsType, resultsLimit}
ACTOR_IG_SCRAPER = "apify~instagram-scraper"           # input: {directUrls:[..], resultsType, resultsLimit}


def _apify_headers():
    # Bearer built here and NEVER logged (token referenced by env-var name APIFY only).
    return {"Authorization": "Bearer " + keys("APIFY"), "Content-Type": "application/json"}


def apify_usage_usd():
    """Current billing-cycle usage in USD (for an approximate per-run cost delta). float | None."""
    try:
        r = _S.get(APIFY_API + "/users/me/limits", headers=_apify_headers(), timeout=20)
        if r.status_code == 200:
            cur = ((r.json() or {}).get("data") or {}).get("current") or {}
            return float(cur.get("monthlyUsageUsd") or 0.0)
    except Exception:
        pass
    return None


def apify_run_sync_items(actor, inp, budget_s=240, max_items=None):
    """POST /acts/{actor}/run-sync-get-dataset-items — run synchronously and return dataset items.
    Preferred path (one call, no polling). Returns (items|None, meta) where
    meta = {status, http, path, detail?}. A 4xx rejection body is captured verbatim (never the token)."""
    qs = "?timeout=%d&format=json" % budget_s
    if max_items:
        qs += "&maxItems=%d" % max_items
    url = APIFY_API + "/acts/%s/run-sync-get-dataset-items%s" % (actor, qs)
    try:
        r = _S.post(url, headers=_apify_headers(), json=inp, timeout=budget_s + 30)
    except requests.Timeout:
        return None, {"status": "timeout", "http": None, "path": "run-sync", "detail": "client timeout"}
    except Exception as e:
        return None, {"status": "error", "http": None, "path": "run-sync",
                      "detail": "%s: %s" % (type(e).__name__, e)}
    if r.status_code in (200, 201):
        try:
            items = r.json()
        except Exception:
            return None, {"status": "error", "http": r.status_code, "path": "run-sync",
                          "detail": "non-json body"}
        return (items if isinstance(items, list) else [items]), {"status": "ok", "http": r.status_code, "path": "run-sync"}
    return None, {"status": "http-error", "http": r.status_code, "path": "run-sync",
                  "detail": (r.text or "").strip()[:500]}


def apify_run_async(actor, inp, budget_s=240, interval=6, max_items=None):
    """Fallback: POST /acts/{actor}/runs, poll /actor-runs/{id} to a terminal state, then fetch the
    dataset. Used when run-sync times out or 5xx's. Returns (items|None, meta) with run cost if seen."""
    try:
        r = _S.post(APIFY_API + "/acts/%s/runs" % actor, headers=_apify_headers(), json=inp, timeout=60)
    except Exception as e:
        return None, {"status": "error", "path": "async", "detail": "%s: %s" % (type(e).__name__, e)}
    if r.status_code not in (200, 201):
        return None, {"status": "http-error", "http": r.status_code, "path": "async",
                      "detail": (r.text or "").strip()[:500]}
    run = ((r.json() or {}).get("data")) or {}
    run_id, ds_id = run.get("id"), run.get("defaultDatasetId")
    if not run_id:
        return None, {"status": "error", "path": "async", "detail": "no run id in response"}
    t0, final = time.time(), run
    while time.time() - t0 < budget_s:
        try:
            rr = _S.get(APIFY_API + "/actor-runs/%s" % run_id, headers=_apify_headers(), timeout=30)
            final = ((rr.json() or {}).get("data")) or final
            ds_id = final.get("defaultDatasetId") or ds_id
        except Exception:
            pass
        if final.get("status") in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT", "TIMED_OUT"):
            break
        time.sleep(interval)
    status = final.get("status")
    if status != "SUCCEEDED":
        return None, {"status": "run-%s" % str(status or "unknown").lower(), "path": "async",
                      "run_id": run_id, "cost_usd": final.get("usageTotalUsd")}
    dsq = "?clean=true&format=json" + (("&limit=%d" % max_items) if max_items else "")
    try:
        di = _S.get(APIFY_API + "/datasets/%s/items%s" % (ds_id, dsq), headers=_apify_headers(), timeout=90)
        items = di.json()
    except Exception as e:
        return None, {"status": "error", "path": "async", "detail": "dataset fetch: %s" % e}
    return (items if isinstance(items, list) else [items]), {"status": "ok", "path": "async",
            "run_id": run_id, "cost_usd": final.get("usageTotalUsd")}


def apify_collect(actor, inp, budget_s=240, max_items=None):
    """run-sync first (preferred); on client timeout / 408 / 5xx fall back to run+poll. A real 4xx
    rejection is surfaced as-is (no retry). Returns (items|None, meta)."""
    items, meta = apify_run_sync_items(actor, inp, budget_s=budget_s, max_items=max_items)
    if items is not None:
        return items, meta
    http = meta.get("http")
    transient = meta.get("status") == "timeout" or (isinstance(http, int) and (http == 408 or http >= 500))
    if transient:
        items2, meta2 = apify_run_async(actor, inp, budget_s=budget_s, max_items=max_items)
        meta2["fell_back_from"] = {k: meta.get(k) for k in ("status", "http")}
        return items2, meta2
    return None, meta


def extract_apify_ig(rec, frames=2):
    """One Apify Instagram post record -> [(image_url, @handle, post_url)]. IMAGES ONLY:
      * top-level Video posts (reels) are skipped entirely;
      * a Sidecar/carousel yields its first `frames` IMAGE child frames (video children skipped);
      * a single Image yields its displayUrl.
    Field names follow the apify/instagram-* output schema, with lower_snake fallbacks."""
    if not isinstance(rec, dict):
        return []
    owner = rec.get("ownerUsername") or rec.get("owner_username") or ""
    handle = ("@" + str(owner)) if owner and not str(owner).startswith("@") else (owner or "")
    src = rec.get("url") or rec.get("inputUrl") or rec.get("postUrl") or ""
    t = str(rec.get("type") or "").lower()
    is_video = (t == "video") or bool(rec.get("videoUrl")) or (rec.get("productType") == "clips")
    cap = max(1, int(frames or 1))
    urls = []
    if t == "sidecar":
        for c in (rec.get("childPosts") or []):
            if len(urls) >= cap:
                break
            if not isinstance(c, dict):
                continue
            if str(c.get("type") or "").lower() == "video" or c.get("videoUrl"):
                continue  # skip video frames inside a carousel
            u = c.get("displayUrl") or c.get("display_url")
            if isinstance(u, str) and u.startswith("http"):
                urls.append(u)
        if not urls:  # childPosts detail absent -> fall back to the flat images[] strings
            for u in (rec.get("images") or [])[:cap]:
                if isinstance(u, str) and u.startswith("http"):
                    urls.append(u)
        if not urls:  # last resort: the cover frame
            u = rec.get("displayUrl")
            if isinstance(u, str) and u.startswith("http"):
                urls.append(u)
    elif is_video:
        return []  # reel / single video -> images only, skip
    else:  # single Image (or unknown non-video)
        u = rec.get("displayUrl") or rec.get("display_url")
        if isinstance(u, str) and u.startswith("http"):
            urls.append(u)
    return [(u, handle, src) for u in urls]


def _hashtagify(s):
    """'Shibuya Sky' -> 'shibuyasky' (alnum only, lowercased; leading # stripped)."""
    return "".join(ch for ch in (s or "").lstrip("#").lower() if ch.isalnum())


def _ig_plan(a):
    """Decide (mode, actor, input_dict|None, note) from --query / --mode / --url. Never touches the
    token. resultsLimit is capped at 50 for cost safety.  Mapping:
      #tag / single token            -> hashtag  (apify/instagram-hashtag-scraper)
      multi-word venue name          -> place    (hashtag-ified -> same hashtag scraper)
      --mode url / http --query      -> url      (apify/instagram-scraper directUrls: posts/profiles)
      --mode user                    -> user     (apify/instagram-scraper directUrls: profile page)"""
    q = (a.query or "").strip()
    mode = (getattr(a, "mode", "") or "").strip().lower() or None
    raw_urls = [u.strip() for u in (a.url or "").split(",") if u.strip()] if getattr(a, "url", None) else []
    if q.startswith("http"):
        raw_urls = raw_urls or [q]
    n = min(max(int(a.n or 0), int(a.download or 0), 3), 50)  # cost guard
    if raw_urls and mode in (None, "url"):
        mode = "url"
    if not mode:
        mode = "hashtag" if (q.startswith("#") or (q and not any(ch.isspace() for ch in q))) else "place"
    if mode == "url":
        if not raw_urls:
            return "url", ACTOR_IG_SCRAPER, None, "url mode needs --url <instagram url(s)> or an http --query"
        return "url", ACTOR_IG_SCRAPER, {"directUrls": raw_urls, "resultsType": "posts", "resultsLimit": n}, \
            "directUrls x%d (posts/profiles)" % len(raw_urls)
    if mode == "user":
        user = q.lstrip("@").strip("/") or (raw_urls[0] if raw_urls else "")
        if not user:
            return "user", ACTOR_IG_SCRAPER, None, "user mode needs a --query username"
        url = user if user.startswith("http") else "https://www.instagram.com/%s/" % user
        return "user", ACTOR_IG_SCRAPER, {"directUrls": [url], "resultsType": "posts", "resultsLimit": n}, \
            "profile %s" % url
    # hashtag / place -> hashtag scraper (a venue is matched by its hashtag; IG location scraping is
    # metadata-only on this actor, so the venue string is hashtag-ified)
    tag = _hashtagify(q)
    if not tag:
        return (mode or "hashtag"), ACTOR_IG_HASHTAG, None, "empty query -> nothing to search"
    note = ("#%s" % tag) if mode == "hashtag" else ("#%s (venue %r matched by hashtag)" % (tag, q))
    return (mode or "hashtag"), ACTOR_IG_HASHTAG, \
        {"hashtags": [tag], "resultsType": "posts", "resultsLimit": n}, note


# ================================================================== Bright Data: SERP request
def _unwrap_serp_json(text):
    try:
        j = json.loads(text)
    except Exception:
        return None
    if isinstance(j, dict) and isinstance(j.get("body"), str):
        try:
            j = json.loads(j["body"])
        except Exception:
            pass
    return j


def bd_serp_gimg(query, n, zone, hl="en", gl="us"):
    """Google Images via a Bright Data SERP zone (brd_json parsed output)."""
    target = "https://www.google.com/search?" + urllib.parse.urlencode(
        {"q": query, "tbm": "isch", "brd_json": "1", "hl": hl, "gl": gl})
    body = {"zone": zone, "url": target, "format": "raw"}
    r = _S.post(BD_API + "/request", headers=_bd_headers(), json=body, timeout=90)
    r.raise_for_status()
    j = _unwrap_serp_json(r.text)
    if not isinstance(j, dict):
        return []
    items = j.get("images") or j.get("images_results") or j.get("image_results") or []
    return [c for c in (_serp_item_to_cand(it) for it in items) if c][:n]


def _serp_item_to_cand(it):
    if not isinstance(it, dict):
        return None
    full = (it.get("image") or it.get("original") or it.get("image_url")
            or it.get("src") or it.get("link_image"))
    if isinstance(full, dict):
        w = full.get("width") or 0
        h = full.get("height") or 0
        full = full.get("src") or full.get("url")
    else:
        w = it.get("width") or it.get("original_width") or 0
        h = it.get("height") or it.get("original_height") or 0
    if not full or not str(full).startswith("http"):
        return None
    page = it.get("link") or it.get("source_url") or it.get("source") or ""
    src = it.get("source") or domain_of(page) or domain_of(full)
    thumb = it.get("thumbnail") or it.get("thumb") or full
    return {"thumb": thumb, "full": full, "w": int(w or 0), "h": int(h or 0),
            "source_url": page or full, "author": src, "source": src}


# ================================================================== SerpAPI fallback
def serpapi_gimg(query, n, hl="en", gl="us"):
    params = {"engine": "google_images", "q": query, "api_key": keys("SERP"), "hl": hl, "gl": gl}
    r = _S.get("https://serpapi.com/search.json?" + urllib.parse.urlencode(params), timeout=60)
    r.raise_for_status()
    d = r.json()
    out = []
    for it in d.get("images_results", [])[:n * 2]:
        full = it.get("original")
        if not full:
            continue
        page = it.get("link") or it.get("source")
        src = it.get("source") or domain_of(page or full)
        out.append({"thumb": it.get("thumbnail"), "full": full,
                    "w": int(it.get("original_width") or 0), "h": int(it.get("original_height") or 0),
                    "source_url": page or full, "author": src, "source": src})
        if len(out) >= n:
            break
    return out


def gather_gimg(query, n, hl, gl):
    """Return (candidates, backend_used, note). BD SERP first if a zone exists, else SerpAPI."""
    zi = discover_zones()
    if zi.get("serp"):
        try:
            cands = bd_serp_gimg(query, n, zi["serp"], hl, gl)
            if cands:
                return cands, "brightdata-serp", "zone=%s" % zi["serp"]
            note_bd = "BD SERP returned 0 rows; fell back to SerpAPI"
        except Exception as e:
            note_bd = "BD SERP error (%s); fell back to SerpAPI" % type(e).__name__
    else:
        note_bd = "no BD SERP zone; used SerpAPI"
    cands = serpapi_gimg(query, n, hl, gl)
    return cands, "serpapi-gimg", note_bd


# ================================================================== byte fetch (direct -> unlocker)
def fetch_bytes(url):
    """Robust image byte fetch. Order: browser UA + SSL verify, then verify off, then BD Web Unlocker.
    Returns (bytes, how) or raises."""
    # host-aware Referer: Instagram/Facebook CDNs 403 a google referer; everything else keeps google.
    _host = domain_of(url)
    _ref = ("https://www.instagram.com/"
            if _host.endswith("cdninstagram.com") or _host.endswith("fbcdn.net")
            else "https://www.google.com/")
    hdr = {"User-Agent": BROWSER_UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
           "Referer": _ref}
    # 1) direct, SSL verify on (the standing Pexels/Unsplash lesson)
    try:
        r = _S.get(url, headers=hdr, timeout=30, verify=True)
        if r.ok and r.content and len(r.content) > 1024:
            return r.content, "direct-ssl"
    except Exception:
        pass
    # 2) direct, SSL verify off (some hosts have broken chains)
    try:
        r = _S.get(url, headers=hdr, timeout=30, verify=False)
        if r.ok and r.content and len(r.content) > 1024:
            return r.content, "direct-nossl"
    except Exception:
        pass
    # 3) Bright Data Web Unlocker zone, if one exists
    zi = discover_zones()
    if zi.get("unlocker"):
        try:
            body = {"zone": zi["unlocker"], "url": url, "format": "raw"}
            r = _S.post(BD_API + "/request", headers=_bd_headers(), json=body, timeout=90)
            if r.ok and r.content and len(r.content) > 1024:
                return r.content, "bd-unlocker:%s" % zi["unlocker"]
        except Exception:
            pass
    raise RuntimeError("all fetch strategies failed for %s" % url)


# ================================================================== manifest + download
def load_manifest():
    if os.path.exists(MANIFEST):
        try:
            with open(MANIFEST, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return []
    return []


def save_manifest(m):
    os.makedirs(MEDIA, exist_ok=True)
    tmp = MANIFEST + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, MANIFEST)


def save_bytes(data, subject, category, query, source_url=None, author=None,
               platform="google_images", license="ugc-unlicensed"):
    """Validate (decodable + >=700 short side), dedupe by sha256, save jpg, append manifest.
    Takes already-fetched image *bytes* (used by the Places backend, which fetches with an API
    key we must never route through fetch_bytes/logs). Returns (status, detail) where status in
    {ok, dup, too_small, undecodable, error}."""
    sha = hashlib.sha256(data).hexdigest()
    manifest = load_manifest()
    for e in manifest:
        if e.get("sha256") == sha:
            return "dup", "sha256 already in library as %s" % e.get("id")
    # decode + size
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        w, h = im.size
    except Exception as e:
        return "undecodable", "PIL could not decode (%s)" % type(e).__name__
    if min(w, h) < MIN_SHORT_SIDE:
        return "too_small", "%dx%d (short side < %d)" % (w, h, MIN_SHORT_SIDE)
    _id = sha[:8]
    slug = slugify(subject)
    dest_dir = os.path.join(LIBRARY, slug)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, _id + ".jpg")
    try:
        im.convert("RGB").save(dest, "JPEG", quality=92)
    except Exception as e:
        return "error", "save failed: %s" % e
    entry = {
        "id": _id,
        "subject": subject,
        "category": category,
        "query": query,
        "platform": platform,
        "source_url": source_url or "",
        "author": author or "",
        "license": license,
        "sha256": sha,
        "w": w, "h": h,
        "local_path": os.path.relpath(dest, REPO),
        "scraped_at": datetime.date.today().isoformat(),
        "used_in": [],
    }
    manifest.append(entry)
    save_manifest(manifest)
    return "ok", entry


def download(url, subject, category, query, source_url=None, author=None,
             platform="google_images", license="ugc-unlicensed"):
    """Fetch bytes from a public image URL, then save_bytes(). Returns (status, detail)."""
    try:
        data, how = fetch_bytes(url)
    except Exception as e:
        return "error", "fetch failed: %s" % e
    return save_bytes(data, subject, category, query,
                      source_url=source_url or url, author=author,
                      platform=platform, license=license)


# ================================================================== Google Places (user-review photos)
# The Places photo pool is *predominantly visitor-uploaded* review shots — real handheld, eye-level,
# imperfectly-timed framing = the UGC look the human wants, with ZERO Bright Data account setup.
# Chain (legacy Places API, the variant this PLACES key is enabled for, same as engine/source):
#   Text Search -> place_id -> Place Details(fields=photos) -> Photo media(maxwidth=1600) -> bytes.
# The API key rides in the request URL only; it is NEVER printed and NEVER stored (source_url is the
# uploader's public contributor link from html_attributions, not the keyed media URL).
GMAPS_API = "https://maps.googleapis.com/maps/api"
_ATTR_RE = re.compile(r'href="([^"]+)"[^>]*>([^<]+)</a>')


def _places_key():
    return keys("PLACES")


def places_text_search(query, hl="en", gl=""):
    """Legacy Text Search -> (place_id, name, status, err). Top result only."""
    params = {"query": query, "key": _places_key()}
    if hl:
        params["language"] = hl
    if gl:
        params["region"] = gl
    r = _S.get(GMAPS_API + "/place/textsearch/json?" + urllib.parse.urlencode(params), timeout=30)
    r.raise_for_status()
    d = r.json()
    status = d.get("status")
    if status != "OK":
        return None, None, status, d.get("error_message")
    res = d.get("results") or []
    if not res:
        return None, None, "ZERO_RESULTS", None
    top = res[0]
    return top.get("place_id"), top.get("name"), status, None


def places_details_photos(place_id, hl="en"):
    """Legacy Place Details (fields=name,photos,url) -> (name, [photo dicts], status, err).
    Each photo dict: {photo_reference, width, height, html_attributions:[...]} (up to 10)."""
    params = {"place_id": place_id, "fields": "name,photos,url", "key": _places_key()}
    if hl:
        params["language"] = hl
    r = _S.get(GMAPS_API + "/place/details/json?" + urllib.parse.urlencode(params), timeout=30)
    r.raise_for_status()
    d = r.json()
    status = d.get("status")
    if status != "OK":
        return None, [], status, d.get("error_message")
    result = d.get("result") or {}
    return result.get("name"), (result.get("photos") or []), status, None


def parse_attribution(html_list):
    """html_attributions -> (author, contrib_url, is_user_upload).
    A real visitor upload attributes to a Google Maps *contributor* profile
    (href .../maps/contrib/<id>). Owner/official/stock shots have no such link (empty
    html_attributions or a non-contrib href) -> is_user_upload=False so we can skip them."""
    for h in html_list or []:
        m = _ATTR_RE.search(h or "")
        if m:
            url, name = m.group(1), m.group(2)
            return name.strip(), url, ("/maps/contrib/" in url)
    return "", "", False


def _norm_alnum(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def looks_like_owner(author, place_name):
    """Best-effort owner-upload catch. Neither Places API exposes an explicit owner boolean, so
    the tell is: the contributor is named after the venue itself (owner posting under the business
    name). Same-script only — a romanized place vs a CJK store name won't match (documented limit)."""
    a, p = _norm_alnum(author), _norm_alnum(place_name)
    if len(a) < 4 or len(p) < 4:
        return False
    return a in p or p in a


def places_photo_bytes(photo_reference, maxwidth=1600):
    """Fetch actual image bytes for a photo_reference. The keyed media URL is built locally,
    followed through its 302 to googleusercontent, and NEVER logged."""
    url = (GMAPS_API + "/place/photo?" + urllib.parse.urlencode(
        {"maxwidth": maxwidth, "photo_reference": photo_reference, "key": _places_key()}))
    r = _S.get(url, headers={"User-Agent": BROWSER_UA}, timeout=45)  # requests follows the redirect
    if r.ok and r.content and len(r.content) > 1024:
        return r.content
    raise RuntimeError("places photo media HTTP %s (len=%d)" % (r.status_code, len(r.content or b"")))


# ================================================================== subcommands
def cmd_probe(a):
    print("== Bright Data probe (read-only) ==")
    if not has_key("BRIGHTDATA"):
        print("  BRIGHTDATA key: MISSING (add to keys.env)")
        return
    print("  BRIGHTDATA key: present (value not shown)")
    st, sterr = bd_status()
    if st:
        print("  /status: account=%s status=%s can_make_requests=%s auth_fail_reason=%s"
              % (st.get("customer"), st.get("status"), st.get("can_make_requests"),
                 st.get("auth_fail_reason") or "-"))
    else:
        print("  /status: unavailable (%s)" % sterr)
    zi = discover_zones()
    if zi["error"]:
        print("  active zones: get_active_zones FAILED -> %s" % zi["error"])
    else:
        listed = ", ".join("%s[%s]" % (n, k) for n, _, k in zi["all"]) or "NONE"
        print("  active zones (%d): %s" % (len(zi["all"]), listed))
    print("  request-usage zones (needed for SERP/Unlocker /request calls):")
    print("    SERP zone (Google Images) : %s" % (zi["serp"] or "NONE  ->  create a SERP zone in dashboard"))
    print("    Web Unlocker (byte fetch) : %s" % (zi["unlocker"] or "NONE  ->  create a Web Unlocker zone in dashboard"))
    cat, caterr = list_catalog()
    if isinstance(cat, list):
        ig = catalog_find(cat, "instagram")
        mp = catalog_find(cat, "maps", "review")
        print("  Web Scraper API catalog: %d datasets visible (marketplace CATALOG, not owned)" % len(cat))
        if ig:
            print("    instagram dataset e.g. : %s (%s)" % (ig[0].get("id"), ig[0].get("name")))
        if mp:
            print("    maps-reviews dataset   : %s (%s)" % (mp[0].get("id"), mp[0].get("name")))
        print("    NOTE: triggering ANY dataset needs Web Scraper API billing + can_make_requests=true")
    else:
        print("  Web Scraper API catalog: unavailable (%s)" % caterr)
    can = bool(st and st.get("can_make_requests"))
    print("  === product readiness ===")
    print("    brightdata-serp      : %s" % ("READY zone=%s" % zi["serp"] if zi["serp"]
                                             else "NEEDS-HUMAN (no SERP zone; can_make_requests=%s)" % can))
    print("    brightdata-unlocker  : %s" % ("READY zone=%s" % zi["unlocker"] if zi["unlocker"]
                                             else "NEEDS-HUMAN (no Web Unlocker zone)"))
    print("    brightdata-ig        : NEEDS-HUMAN (Web Scraper API dataset collection; setup+billing)")
    print("    greviews             : NEEDS-HUMAN (maps-reviews dataset; setup+billing)")
    print("    serpapi-gimg (fallbk): %s" % ("READY" if has_key("SERP") else "MISSING SERP key"))
    print("  other fallbacks: Pexels=%s Unsplash=%s Places=%s"
          % (has_key("PEXELS"), has_key("UNSPLASH"), has_key("PLACES")))


def cmd_gimg(a):
    cands, backend, note = gather_gimg(a.query, a.n, a.hl, a.gl)
    print("== gimg  query=%r  backend=%s  (%s)  candidates=%d" % (a.query, backend, note, len(cands)))
    for i, c in enumerate(cands):
        print("  [%d] %dx%d  %s  <%s>" % (i, c.get("w") or 0, c.get("h") or 0,
                                          (c.get("source") or "")[:28], (c.get("full") or "")[:80]))
    result = {"backend": backend, "note": note, "candidates": cands, "downloaded": []}
    if a.download and a.download > 0:
        got = 0
        for c in cands:
            if got >= a.download:
                break
            status, detail = download(
                c["full"], a.subject, a.category, a.query,
                source_url=c.get("source_url"), author=c.get("author"),
                platform="google_images", license="ugc-unlicensed")
            tag = detail["id"] if status == "ok" else str(detail)[:60]
            print("    dl %-11s %s" % (status, tag))
            if status == "ok":
                got += 1
                result["downloaded"].append(detail)
        print("  downloaded %d/%d usable into media/library/%s/" % (got, a.download, slugify(a.subject)))
    if a.json:
        print("JSON " + json.dumps(result, ensure_ascii=False))
    return result


def cmd_places(a):
    """Google Places user-review photos -> library + manifest. Works today, no BD account setup."""
    print("== places  query=%r  subject=%r  n=%d  download=%d" % (a.query, a.subject, a.n, a.download))
    if not has_key("PLACES"):
        print("  PLACES key: MISSING (add to keys.env)")
        return {"status": "no-key"}
    try:
        pid, pname, status, err = places_text_search(a.query, a.hl, a.gl)
    except Exception as e:
        print("  text search FAILED: %s: %s" % (type(e).__name__, e))
        return {"status": "error", "stage": "text_search", "detail": str(e)}
    if not pid:
        print("  text search -> no place (status=%s%s)" % (status, (" / %s" % err) if err else ""))
        return {"status": "no-place", "detail": status}
    print("  place: %s  (place_id=%s)" % (pname, pid))
    try:
        dname, photos, dstatus, derr = places_details_photos(pid, a.hl)
    except Exception as e:
        print("  place details FAILED: %s: %s" % (type(e).__name__, e))
        return {"status": "error", "stage": "details", "detail": str(e)}
    if dstatus != "OK":
        print("  place details -> status=%s%s" % (dstatus, (" / %s" % derr) if derr else ""))
        return {"status": "no-details", "detail": dstatus}
    print("  details: %d photo(s) on the place record (status=%s)" % (len(photos), dstatus))
    result = {"status": "ok", "place": pname, "place_id": pid, "photos_total": len(photos),
              "backend": "google_places_user_photo", "downloaded": [], "skipped_owner": 0}
    got, listed = 0, 0
    for i, ph in enumerate(photos):
        if a.download and got >= a.download:
            break
        if (not a.download) and a.n and listed >= a.n:
            break
        ref = ph.get("photo_reference")
        if not ref:
            continue
        author, contrib, is_user = parse_attribution(ph.get("html_attributions"))
        if (not is_user) or looks_like_owner(author, dname or pname):
            result["skipped_owner"] += 1
            why = "no visitor-contributor attribution" if not is_user else "attribution matches venue name"
            print("  [%d] SKIP  %s (owner/official/stock: %s)" % (i, why, (author or "-")[:24]))
            continue
        listed += 1
        if a.download and a.download > 0:
            try:
                data = places_photo_bytes(ref, 1600)
            except Exception as e:
                print("  [%d] fetch failed: %s" % (i, e))
                continue
            st, detail = save_bytes(
                data, a.subject, a.category, a.query,
                source_url=contrib, author=author,
                platform="google_places_user_photo", license="places-tos")
            tag = detail["id"] + " %dx%d" % (detail["w"], detail["h"]) if st == "ok" else str(detail)[:56]
            print("  [%d] %-11s by %-24s %s" % (i, st, (author or "?")[:24], tag))
            if st == "ok":
                got += 1
                result["downloaded"].append(detail)
        else:
            print("  [%d] user photo by %-24s <%s>" % (i, (author or "?")[:24], contrib))
    if a.download:
        print("  downloaded %d/%d user photos -> media/library/%s/  (skipped %d owner/unattributed)"
              % (got, a.download, slugify(a.subject), result["skipped_owner"]))
    else:
        print("  listed %d user photo(s); pass --download K to save (skipped %d owner/unattributed)"
              % (listed, result["skipped_owner"]))
    if a.json:
        print("JSON " + json.dumps(result, ensure_ascii=False))
    return result


def _download_from_records(records, a, platform, extract_fn, license, query):
    """Shared: extract (image_url, author, source_url) tuples from Web Scraper records and download
    the top-K into library+manifest via the existing byte-fetch strategies."""
    out = {"status": "ok", "downloaded": [], "candidates": 0, "platform": platform}
    got = 0
    for rec in records:
        for img_url, author, src in extract_fn(rec):
            out["candidates"] += 1
            if a.download and got >= a.download:
                continue
            if a.download and a.download > 0:
                st, detail = download(img_url, a.subject, a.category, query,
                                      source_url=src or img_url, author=author,
                                      platform=platform, license=license)
                tag = (detail["id"] + " %dx%d" % (detail["w"], detail["h"])) if st == "ok" else str(detail)[:50]
                print("    dl %-11s by %-22s %s" % (st, (author or "?")[:22], tag))
                if st == "ok":
                    got += 1
                    out["downloaded"].append(detail)
            else:
                print("    img by %-22s <%s>" % ((author or "?")[:22], img_url[:66]))
    if a.download:
        print("  downloaded %d/%d -> media/library/%s/" % (got, a.download, slugify(a.subject)))
    else:
        print("  %d image candidate(s) found; pass --download K to save" % out["candidates"])
    return out


def _bd_collect(a, dataset_id, inputs, cap):
    """Trigger -> poll -> snapshot for a Web Scraper dataset. Honours a.snapshot (reuse an existing
    snapshot, zero new spend). Returns (records|None, meta) where meta carries status/http/body/snapshot.
    Captures the trigger rejection body verbatim (this is the human-facing 'unlock' signal)."""
    if getattr(a, "snapshot", None):
        print("  reusing snapshot %s (no new collection triggered)" % a.snapshot)
        recs, err = bd_snapshot(a.snapshot)
        if recs is None:
            return None, {"status": "error", "detail": err, "snapshot": a.snapshot}
        return recs, {"status": "ready", "snapshot": a.snapshot}
    sid, code, body = bd_trigger(dataset_id, inputs, extra_qs="&limit_per_input=%d" % cap)
    if not sid:
        print("  trigger -> HTTP %s   body(verbatim): %s" % (code, body))
        return None, {"status": "needs-human", "http": code, "body": body, "dataset_id": dataset_id}
    print("  trigger ok -> snapshot=%s ; polling (budget %ds)" % (sid, a.budget))
    status, elapsed = bd_poll(sid, budget_s=a.budget)
    print("  poll -> status=%s (%ds)" % (status, elapsed))
    if status != "ready":
        print("  not ready yet — re-fetch later with:  --snapshot %s" % sid)
        return None, {"status": "pending", "snapshot": sid, "last": status}
    recs, err = bd_snapshot(sid)
    if recs is None:
        return None, {"status": "error", "detail": err, "snapshot": sid}
    return recs, {"status": "ready", "snapshot": sid}


def _split_records(recs):
    good = [r for r in recs if not (isinstance(r, dict) and r.get("error"))]
    errs = [r for r in recs if isinstance(r, dict) and r.get("error")]
    return good, errs


def cmd_greviews(a):
    """Real visitor photos per venue via Bright Data's Google-Maps-reviews Web Scraper dataset.
    VERIFIED 2026-07-22: this account triggers + runs this dataset today (no zone/billing/KYC gate).
    Resolves the venue -> place_id (Places API) -> canonical maps URL, then trigger->poll->download.
    Crawl caveat: a per-URL Google sign-in modal can intermittently hide reviews (retry / better URL)."""
    venue = a.place
    print("== greviews  place=%r  subject=%r  download=%d" % (venue, a.subject, a.download))
    if not has_key("BRIGHTDATA"):
        print("  BRIGHTDATA key: MISSING"); return {"status": "no-key"}
    inputs = None
    if not getattr(a, "snapshot", None):
        maps_url = getattr(a, "url", None)
        if not maps_url:
            if not has_key("PLACES"):
                print("  need --url <maps place url> or a PLACES key to resolve the venue")
                return {"status": "error", "detail": "no venue url"}
            pid, pname, stt, err = places_text_search(venue, a.hl, a.gl)
            if not pid:
                print("  venue resolve failed (status=%s)" % stt)
                return {"status": "no-place", "detail": stt}
            maps_url = "https://www.google.com/maps/place/?q=place_id:%s&hl=%s" % (pid, a.hl or "en")
            print("  venue: %s  ->  %s" % (pname, maps_url))
        inputs = [{"url": maps_url, "sort_by": a.sort}]
    cap = max(a.n, a.download, 5)
    recs, meta = _bd_collect(a, DATASET_GMAPS_REVIEWS, inputs, cap)
    if recs is None:
        print("  status: %s" % meta.get("status"))
        return meta
    good, errs = _split_records(recs)
    if errs and not good:
        print("  all %d record(s) errored, e.g.: %s" % (len(errs), errs[0].get("error")))
        return {"status": "crawl-error", "detail": errs[0].get("error"), "snapshot": meta.get("snapshot")}
    print("  %d review record(s) usable (%d crawl-errored)" % (len(good), len(errs)))
    res = _download_from_records(good, a, "google_reviews", extract_review_images, "ugc-unlicensed", venue)
    res["snapshot"] = meta.get("snapshot")
    if a.json:
        print("JSON " + json.dumps(res, ensure_ascii=False))
    return res


def cmd_ig(a):
    """Instagram post photos via Apify public actors (https://api.apify.com/v2) — THE Instagram UGC
    backend. Bright Data's IG scraper is KYC-gated on our account (see `ig-bd`). Maps --query to a
    hashtag search (single token / #tag / venue name -> apify/instagram-hashtag-scraper) or, via
    --mode url|user, routes post/profile URLs through apify/instagram-scraper's directUrls. Images
    only (reels/videos skipped); carousels contribute their first --frames image frames. Every saved
    byte gets a CONTRACT manifest row (platform 'instagram', license 'ugc-unlicensed', author @owner,
    source_url = post url)."""
    print("== ig (apify)  query=%r  subject=%r  n=%d  download=%d" % (a.query, a.subject, a.n, a.download))
    if not has_key("APIFY"):
        print("  APIFY key: MISSING (add to keys.env at repo root, or export APIFY)")
        return {"status": "no-key"}
    mode, actor, inp, note = _ig_plan(a)
    print("  mode=%s  actor=%s  input: %s" % (mode, actor.replace("~", "/"), note))
    if inp is None:
        print("  status: needs-input")
        return {"status": "needs-input", "detail": note, "mode": mode}
    rl = inp.get("resultsLimit", 0)
    print("  resultsLimit=%d  frames/carousel=%d ; collecting (run-sync, budget %ds)…" % (rl, a.frames, a.budget))
    u0 = apify_usage_usd()
    items, meta = apify_collect(actor, inp, budget_s=a.budget, max_items=rl)
    if items is None:
        print("  collect FAILED via %s: status=%s http=%s" % (meta.get("path"), meta.get("status"), meta.get("http")))
        if meta.get("detail"):
            print("  detail(verbatim): %s" % meta.get("detail"))
        return {"status": meta.get("status", "error"), "meta": meta, "mode": mode}
    good = [r for r in items if isinstance(r, dict) and not r.get("error")]
    errs = [r for r in items if isinstance(r, dict) and r.get("error")]
    print("  collected %d record(s) via %s (%d errored/empty)" % (len(good), meta.get("path"), len(errs)))
    if not good:
        if errs:
            print("  first record note(verbatim): %s" % str(errs[0].get("error") or errs[0])[:200])
        return {"status": "empty", "mode": mode, "meta": meta}
    res = _download_from_records(good, a, "instagram",
                                 lambda r: extract_apify_ig(r, frames=a.frames),
                                 "ugc-unlicensed", a.query)
    res["mode"], res["actor"] = mode, actor.replace("~", "/")
    u1 = apify_usage_usd()
    if u0 is not None and u1 is not None:
        res["cost_usd_delta"] = round(max(0.0, u1 - u0), 5)
        print("  approx apify spend this run: $%.5f (cumulative cycle $%.5f)" % (res["cost_usd_delta"], u1))
    if a.json:
        print("JSON " + json.dumps(res, ensure_ascii=False))
    return res


def cmd_ig_bd(a):
    """[alt backend] Instagram posts via Bright Data's 'Instagram - Posts' Web Scraper dataset (gd_lk5ns7kz21pck8jpis).
    Same trigger->poll->download mechanism as greviews (proven working there). On THIS account the IG
    trigger is gated: HTTP 400 'Customer is not active' = Bright Data's social-media compliance/KYC gate.
    Wired end-to-end; pass --url <post_url> to attempt a real pull (captures the gate verbatim, or
    collects once KYC is approved)."""
    print("== ig  query=%r  subject=%r  download=%d" % (a.query, a.subject, a.download))
    if not has_key("BRIGHTDATA"):
        print("  BRIGHTDATA key: MISSING"); return {"status": "no-key"}
    # investigate line (always useful)
    cat, _ = list_catalog()
    igsets = catalog_find(cat, "instagram", "post") if isinstance(cat, list) else []
    print("  dataset: %s (Instagram - Posts)" % DATASET_IG_POSTS)
    inputs = None
    if not getattr(a, "snapshot", None):
        urls = []
        if getattr(a, "url", None):
            urls = [u.strip() for u in a.url.split(",") if u.strip()]
        elif (a.query or "").startswith("http"):
            urls = [a.query.strip()]
        if not urls:
            print("  The 'Instagram - Posts' dataset collects by POST URL. Pass --url <instagram post url>")
            print("  (hashtag/profile discovery is a different dataset id). Nothing triggered.")
            print("  status: needs-input")
            return {"status": "needs-input", "detail": "pass --url <instagram post url>", "dataset_id": DATASET_IG_POSTS}
        inputs = [{"url": u} for u in urls]
    cap = max(a.download, len(inputs) if inputs else 1, 1)
    recs, meta = _bd_collect(a, DATASET_IG_POSTS, inputs, cap)
    if recs is None:
        if meta.get("status") == "needs-human":
            print("  status: needs-human — the verbatim body above IS the IG unlock gate.")
        else:
            print("  status: %s" % meta.get("status"))
        return meta
    good, errs = _split_records(recs)
    if errs and not good:
        print("  all %d record(s) errored, e.g.: %s" % (len(errs), errs[0].get("error")))
        return {"status": "crawl-error", "detail": errs[0].get("error"), "snapshot": meta.get("snapshot")}
    print("  %d post record(s) usable (%d errored)" % (len(good), len(errs)))
    res = _download_from_records(good, a, "instagram", extract_ig_images, "ugc-unlicensed", a.query)
    res["snapshot"] = meta.get("snapshot")
    if a.json:
        print("JSON " + json.dumps(res, ensure_ascii=False))
    return res


def cmd_fetch(a):
    status, detail = download(
        a.url, a.subject, a.category, a.query,
        source_url=a.source_url, author=a.author,
        platform=a.platform, license=a.license)
    if status == "ok":
        print("ok  id=%s  %dx%d  -> %s" % (detail["id"], detail["w"], detail["h"], detail["local_path"]))
    else:
        print("%s  %s" % (status, detail))
    return {"status": status, "detail": detail}


# ================================================================== argparse
def build_parser():
    p = argparse.ArgumentParser(prog="brightdata.py", description="sandboxed BD/SerpAPI photo sourcer")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("probe", help="authenticate + list zones (read-only)")
    sp.set_defaults(fn=cmd_probe)

    sg = sub.add_parser("gimg", help="Google Images (BD SERP -> SerpAPI fallback)")
    sg.add_argument("--query", required=True)
    sg.add_argument("--subject", required=True, help="country/city or venue, e.g. japan/tokyo")
    sg.add_argument("--category", default="visit")
    sg.add_argument("--n", type=int, default=8)
    sg.add_argument("--download", type=int, default=0, help="download top-K usable into library+manifest")
    sg.add_argument("--hl", default="en")
    sg.add_argument("--gl", default="us")
    sg.add_argument("--json", action="store_true")
    sg.set_defaults(fn=cmd_gimg)

    spl = sub.add_parser("places", help="Google Places user-review photos (works today, no BD setup)")
    spl.add_argument("--query", required=True, help="venue/place, e.g. 'Shibuya Sky' or 'Ichiran ramen Shibuya'")
    spl.add_argument("--subject", required=True, help="country/city library key, e.g. japan/tokyo")
    spl.add_argument("--category", default="visit")
    spl.add_argument("--n", type=int, default=8, help="max user photos to list when not downloading")
    spl.add_argument("--download", type=int, default=0, help="download top-K user photos into library+manifest")
    spl.add_argument("--hl", default="en", help="Places language code")
    spl.add_argument("--gl", default="", help="Places region bias (ccTLD, e.g. jp); blank = unbiased")
    spl.add_argument("--json", action="store_true")
    spl.set_defaults(fn=cmd_places)

    sr = sub.add_parser("greviews", help="visitor photos per venue via BD Google-Maps-reviews (works today)")
    sr.add_argument("--place", required=True, help="venue, e.g. 'Shibuya Sky' (resolved via Places)")
    sr.add_argument("--subject", required=True, help="country/city library key, e.g. japan/tokyo")
    sr.add_argument("--category", default="visit")
    sr.add_argument("--n", type=int, default=6, help="reviews to request (limit_per_input cap)")
    sr.add_argument("--download", type=int, default=0, help="download top-K review photos into library+manifest")
    sr.add_argument("--url", default=None, help="explicit Google Maps place URL (skip Places resolution)")
    sr.add_argument("--snapshot", default=None, help="reuse an existing snapshot id (no new collection/spend)")
    sr.add_argument("--sort", default="Newest", help="review sort (Newest|'Most relevant'|Highest|Lowest)")
    sr.add_argument("--budget", type=int, default=240, help="max seconds to poll the snapshot")
    sr.add_argument("--hl", default="en")
    sr.add_argument("--gl", default="")
    sr.add_argument("--json", action="store_true")
    sr.set_defaults(fn=cmd_greviews)

    si = sub.add_parser("ig", help="Instagram post photos via Apify (hashtag / venue / profile) — default IG backend")
    si.add_argument("--query", default="", help="#hashtag, single token, or venue/place name (venue -> its hashtag)")
    si.add_argument("--subject", default="misc", help="country/city library key, e.g. japan/tokyo")
    si.add_argument("--category", default="visit")
    si.add_argument("--n", type=int, default=12, help="posts to scrape (resultsLimit; capped at 50 for cost)")
    si.add_argument("--download", type=int, default=0, help="download top-K post images into library+manifest")
    si.add_argument("--mode", default="", choices=["", "hashtag", "place", "url", "user"],
                    help="override query->actor mapping (blank=auto: #/single-token->hashtag, multi-word->place)")
    si.add_argument("--url", default=None, help="explicit Instagram url(s), comma-separated (forces url mode; posts/profiles)")
    si.add_argument("--frames", type=int, default=2, help="max image frames to take per carousel/sidecar post")
    si.add_argument("--budget", type=int, default=240, help="max seconds for the actor run")
    si.add_argument("--json", action="store_true")
    si.set_defaults(fn=cmd_ig)

    sib = sub.add_parser("ig-bd", help="[alt] Instagram via Bright Data dataset (KYC-gated on this account)")
    sib.add_argument("--query", default="", help="a post URL, or free text (then pass --url)")
    sib.add_argument("--subject", default="misc", help="country/city library key")
    sib.add_argument("--category", default="visit")
    sib.add_argument("--download", type=int, default=0, help="download top-K post images into library+manifest")
    sib.add_argument("--url", default=None, help="Instagram POST url(s), comma-separated (Posts dataset input)")
    sib.add_argument("--snapshot", default=None, help="reuse an existing snapshot id (no new collection/spend)")
    sib.add_argument("--budget", type=int, default=240, help="max seconds to poll the snapshot")
    sib.add_argument("--json", action="store_true")
    sib.set_defaults(fn=cmd_ig_bd)

    sf = sub.add_parser("fetch", help="download one image url into library+manifest")
    sf.add_argument("--url", required=True)
    sf.add_argument("--subject", required=True)
    sf.add_argument("--category", default="visit")
    sf.add_argument("--query", default="")
    sf.add_argument("--source-url", dest="source_url", default=None)
    sf.add_argument("--author", default=None)
    sf.add_argument("--platform", default="google_images")
    sf.add_argument("--license", default="ugc-unlicensed")
    sf.set_defaults(fn=cmd_fetch)
    return p


def main():
    a = build_parser().parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
