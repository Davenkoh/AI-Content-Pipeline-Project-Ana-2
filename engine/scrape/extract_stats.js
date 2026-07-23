/**
 * extract_stats.js — pull a TikTok post's engagement metrics from a live page.
 *
 * Shared by tiktok_stats.js (standalone, for the Sheet) and tiktok_carousel.js (inline,
 * for source.txt). Source priority, richest first:
 *   1. api  — the /api/item/detail/ XHR response (the ONLY place a photo post's views /
 *             playCount now live; TikTok stopped embedding stats in the hydration JSON).
 *             Captured in the Playwright layer via attachItemCapture(page) BEFORE goto.
 *   2. json — the hydrated __UNIVERSAL_DATA_FOR_REHYDRATION__ / SIGI_STATE (still works for
 *             some video posts; carries exact counts + createTime).
 *   3. dom  — the rendered [data-e2e] counters (logged-out fallback: like/comment/share/save,
 *             but NO views for photo posts).
 *
 * Returns { views, likes, comments, share, save, posting_date, author, source, loggedIn }
 * where counts are integers (or "" when genuinely unavailable, e.g. logged-out photo views).
 */

// "1.2M" / "12.5K" / "1,234" / 1234 -> integer
function parseCount(v) {
  if (v === null || v === undefined || v === '') return '';
  if (typeof v === 'number') return Math.round(v);
  const s = String(v).trim().replace(/,/g, '');
  const mult = { k: 1e3, m: 1e6, b: 1e9 };
  const mm = s.match(/^([\d.]+)\s*([kmb])$/i);
  if (mm) return Math.round(parseFloat(mm[1]) * mult[mm[2].toLowerCase()]);
  const n = parseInt(s, 10);
  return Number.isFinite(n) ? n : '';
}

// runs inside page.evaluate — must be self-contained (no closures over node scope)
function pageExtract() {
  const out = { likes: '', comments: '', share: '', save: '', views: '', createTime: '', author: '', source: 'none', loggedIn: null };

  // login state — for PHOTO posts, views + createTime + collectCount only hydrate when
  // logged IN. Logged out, TikTok serves a reduced page (DOM counters only, no views).
  // Detect it so callers can warn instead of silently stamping stale views as fresh.
  const _profileIcon = document.querySelector('[data-e2e="profile-icon"]');
  const _loginBtn = document.querySelector('[data-e2e="top-login-button"], [data-e2e="login-button"]');
  out.loggedIn = _profileIcon ? true : (_loginBtn ? false : null);

  // 1) hydrated JSON: deep-search for the itemStruct (has stats{} + createTime)
  const jsonFrom = (id) => {
    const el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (_) { return null; }
  };
  // collect every object that looks like an item (has a stats{} with counts), then pick
  // the RICHEST one (some shells carry only digg/comment; the real itemStruct also has
  // createTime + collectCount + author).
  const findItem = (root) => {
    const stack = [root];
    let hops = 0;
    const cands = [];
    while (stack.length && hops < 200000) {
      const cur = stack.pop(); hops++;
      if (cur && typeof cur === 'object') {
        const st = cur.stats;
        if (st && typeof st === 'object' && ('diggCount' in st || 'commentCount' in st)) {
          const s2 = cur.statsV2 || {};
          let score = 0;
          if ('createTime' in cur) score += 2;
          if (cur.author) score += 1;
          if (st.collectCount != null || s2.collectCount != null) score += 1;
          if (st.playCount != null || s2.playCount != null) score += 1;
          cands.push([score, cur]);
        }
        for (const k in cur) { const v = cur[k]; if (v && typeof v === 'object') stack.push(v); }
      }
    }
    if (!cands.length) return null;
    cands.sort((a, b) => b[0] - a[0]);
    return cands[0][1];
  };
  const root = jsonFrom('__UNIVERSAL_DATA_FOR_REHYDRATION__') || jsonFrom('SIGI_STATE');
  if (root) {
    const item = findItem(root);
    if (item) {
      const st = Object.assign({}, item.stats || {}, item.statsV2 || {});
      out.likes = st.diggCount ?? '';
      out.comments = st.commentCount ?? '';
      out.share = st.shareCount ?? '';
      out.save = st.collectCount ?? '';
      out.views = st.playCount ?? '';
      out.createTime = item.createTime ?? '';
      out.author = (item.author && (item.author.uniqueId || item.author.id)) || '';
      out.source = 'json';
      return out;
    }
  }

  // 2) DOM fallback: the rendered counters. Logged out, photo posts expose
  //    like / comment / share / SAVE — but NOT views (play count is withheld).
  const txt = (sel) => { const e = document.querySelector(sel); return e ? (e.textContent || '').trim() : ''; };
  out.likes = txt('[data-e2e="like-count"], [data-e2e="browse-like-count"]');
  out.comments = txt('[data-e2e="comment-count"], [data-e2e="browse-comment-count"]');
  out.share = txt('[data-e2e="share-count"]');
  // saves: TikTok renamed this counter to "favorite-count" (was collect-/undefined-count).
  out.save = txt('[data-e2e="favorite-count"], [data-e2e="collect-count"], [data-e2e="undefined-count"]');
  // posting date sits next to the author handle, e.g. "· 2025-5-30" (other year) or "· 6-20"
  // (current year, month-day). The old nickname container selector is stale, so scan the
  // header region for the first date-shaped leaf text.
  const dateRe = /(?:^|·\s*)((?:\d{4}-)?\d{1,2}-\d{1,2})\s*$/;
  for (const el of document.querySelectorAll('span, div, time')) {
    if (el.childElementCount) continue;                 // leaf nodes only
    const t = (el.textContent || '').trim();
    if (t.length > 24) continue;
    const m = t.match(dateRe);
    if (m && el.getBoundingClientRect().top < 700) { out.dateText = m[1]; break; }
  }
  if (out.likes || out.comments || out.save) out.source = 'dom';
  return out;
}

// ── node-side helpers (run in the Playwright process, not the page) ───────────
// Deep-search any JSON for the richest item object (one carrying stats.playCount/diggCount).
function deepFindItem(root) {
  const stack = [root]; let hops = 0; const cands = [];
  while (stack.length && hops < 300000) {
    const cur = stack.pop(); hops++;
    if (cur && typeof cur === 'object') {
      const merged = Object.assign({}, cur.stats || {}, cur.statsV2 || {});
      if ('diggCount' in merged || 'playCount' in merged) {
        let score = 0;
        if ('createTime' in cur) score += 2;
        if (cur.author) score += 1;
        if (merged.collectCount != null) score += 1;
        if (merged.playCount != null) score += 1;
        cands.push([score, cur]);
      }
      for (const k in cur) { const v = cur[k]; if (v && typeof v === 'object') stack.push(v); }
    }
  }
  if (!cands.length) return null;
  cands.sort((a, b) => b[0] - a[0]);
  return cands[0][1];
}

// Capture the post's stats from the /api/item/detail/ XHR — the only place a photo post's
// views (playCount) now live. Attach BEFORE page.goto(); await cap.wait(ms) after load;
// then read cap.item() and hand it to extractStats({ apiItem }).
function attachItemCapture(page) {
  let item = null, resolve;
  const done = new Promise((r) => { resolve = r; });
  page.on('response', async (resp) => {
    if (item) return;
    if (!/\/api\/item\/detail\/?(\?|$)/.test(resp.url())) return;
    try {
      const body = await resp.text();
      if (!/playCount|diggCount/.test(body)) return;
      const found = deepFindItem(JSON.parse(body));
      if (found) { item = found; resolve(); }
    } catch (_) { /* body gone / not json */ }
  });
  return { item: () => item, wait: (ms) => Promise.race([done, page.waitForTimeout(ms)]) };
}

// createTime (unix secs) OR a DOM "M-D" / "YYYY-M-D" string -> "YYYY-MM-DD"
function postingDate(createTime, dateText) {
  if (createTime) {
    const t = parseInt(createTime, 10);
    if (Number.isFinite(t) && t > 0) return new Date(t * 1000).toISOString().slice(0, 10);
  }
  if (dateText) {
    let md = dateText.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
    if (md) return `${md[1]}-${md[2].padStart(2, '0')}-${md[3].padStart(2, '0')}`;
    if ((md = dateText.match(/^(\d{1,2})-(\d{1,2})$/))) {   // month-day ⇒ current year (or last)
      const now = new Date(); let y = now.getFullYear();
      if (new Date(`${y}-${md[1].padStart(2, '0')}-${md[2].padStart(2, '0')}T00:00:00`) > now) y -= 1;
      return `${y}-${md[1].padStart(2, '0')}-${md[2].padStart(2, '0')}`;
    }
  }
  return '';
}

async function extractStats(page, opts = {}) {
  // 1) preferred: the captured /api/item/detail/ itemStruct (the one place views still live)
  const api = opts.apiItem;
  if (api && (api.stats || api.statsV2)) {
    const st = Object.assign({}, api.stats || {}, api.statsV2 || {});
    if (st.playCount != null || st.diggCount != null) {
      return {
        views: parseCount(st.playCount),
        likes: parseCount(st.diggCount),
        comments: parseCount(st.commentCount),
        share: parseCount(st.shareCount),
        save: parseCount(st.collectCount),
        posting_date: postingDate(api.createTime),
        author: (api.author && (api.author.uniqueId || api.author.id)) || '',
        source: 'api',
        loggedIn: true,                 // item/detail only returns full stats to a session
      };
    }
  }
  // 2) hydration JSON, then 3) DOM counters — both via the page-side extractor
  const r = await page.evaluate(pageExtract);
  return {
    views: parseCount(r.views),
    likes: parseCount(r.likes),
    comments: parseCount(r.comments),
    share: parseCount(r.share),
    save: parseCount(r.save),
    posting_date: postingDate(r.createTime, r.dateText),
    author: r.author || '',
    source: r.source,
    loggedIn: r.loggedIn,
  };
}

module.exports = { extractStats, parseCount, attachItemCapture, deepFindItem, postingDate };
