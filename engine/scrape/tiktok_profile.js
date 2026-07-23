#!/usr/bin/env node
/**
 * tiktok_profile.js — list every post on a TikTok profile (id, url, caption, stats, date).
 *
 * Drives the project's CDP Chrome (same profile/session as the other scrapers), opens the
 * profile, and harvests posts from the `/api/post/item_list/` feed (intercepted) while
 * scrolling to paginate. Each post's caption + stats come straight from that itemStruct, so
 * this is the backfill source for "what did we post that isn't linked in the Sheet yet".
 * Needs the masquerade Chrome logged into TikTok (see tiktok_login.js).
 *
 * Usage:  node tiktok_profile.js "@handle" | "<profile_url>" | <character key, e.g. ana>  (key -> @handle via state.json)
 * Output (stdout, last line): {"author":"..","count":N,"posts":[
 *   {id,url,type,desc,views,likes,comments,share,save,posting_date}, ... ]}  (newest first)
 */
const { connect, context } = require('../lib/cdp');
const { parseCount, postingDate } = require('./extract_stats');
const fs = require('fs');
const path = require('path');

// Resolve a character key/name ("ana", "Chloe") to its @handle from state.json, so discovery can
// run per-character (`node tiktok_profile.js ana`) without hard-coding handles. @handle / URL pass through.
function resolveHandle(a) {
  if (!a || a.startsWith('@') || a.startsWith('http')) return a;
  try {
    let p = __dirname;
    while (p !== path.dirname(p)) {
      const sj = path.join(p, 'state.json');
      if (fs.existsSync(sj)) {
        const chars = JSON.parse(fs.readFileSync(sj, 'utf8')).characters || {};
        const key = a.toLowerCase();
        for (const [k, c] of Object.entries(chars))
          if ((k.toLowerCase() === key || String((c && c.name) || '').toLowerCase() === key) && c && c.tiktok)
            return c.tiktok;
        break;
      }
      p = path.dirname(p);
    }
  } catch (_) {}
  return a;
}

// Deep-collect post items (a digit id + a desc + an author) from any item_list JSON, keyed by id.
function collectItems(root, into) {
  const stack = [root]; let hops = 0;
  while (stack.length && hops < 400000) {
    const cur = stack.pop(); hops++;
    if (cur && typeof cur === 'object') {
      if (typeof cur.id === 'string' && /^\d{6,}$/.test(cur.id) &&
          typeof cur.desc === 'string' && cur.author) {
        into.set(cur.id, cur);
      }
      for (const k in cur) { const v = cur[k]; if (v && typeof v === 'object') stack.push(v); }
    }
  }
}

(async () => {
  const arg = process.argv[2];
  if (!arg) { console.error('usage: node tiktok_profile.js "@handle" | "<profile_url>" | <character key e.g. ana>'); process.exit(1); }
  const resolved = resolveHandle(arg);
  const handle = resolved.replace(/^https?:\/\/[^/]+\//, '').replace(/^@/, '').split(/[/?]/)[0];
  const url = resolved.startsWith('http') ? resolved : `https://www.tiktok.com/@${handle}`;

  const browser = await connect();
  const ctx = await context(browser);
  const page = await ctx.newPage();
  const items = new Map();
  page.on('response', async (resp) => {
    if (!/\/api\/post\/item_list/.test(resp.url())) return;
    try { collectItems(JSON.parse(await resp.text()), items); } catch (_) {}
  });

  await page.goto(url, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(3000);
  // also seed from the server-rendered hydration JSON (first page may not be an XHR)
  try {
    const hydration = await page.evaluate(() => {
      const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__') || document.getElementById('SIGI_STATE');
      return el ? el.textContent : null;
    });
    if (hydration) collectItems(JSON.parse(hydration), items);
  } catch (_) {}

  // scroll to paginate until the count stops growing (or a hard cap)
  let last = items.size, stable = 0;
  for (let i = 0; i < 60 && stable < 4; i++) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);
    if (items.size === last) stable++; else { stable = 0; last = items.size; }
  }

  const author = [...items.values()][0]?.author?.uniqueId || handle;
  const posts = [...items.values()].map((it) => {
    const st = Object.assign({}, it.stats || {}, it.statsV2 || {});
    const type = it.imagePost ? 'photo' : 'video';
    const a = (it.author && it.author.uniqueId) || author;
    return {
      id: it.id,
      url: `https://www.tiktok.com/@${a}/${type}/${it.id}`,
      type,
      desc: it.desc || '',
      views: parseCount(st.playCount),
      likes: parseCount(st.diggCount),
      comments: parseCount(st.commentCount),
      share: parseCount(st.shareCount),
      save: parseCount(st.collectCount),
      posting_date: postingDate(it.createTime),
    };
  }).sort((x, y) => (x.posting_date < y.posting_date ? 1 : x.posting_date > y.posting_date ? -1 : 0));

  console.error(`[profile] @${author}: ${posts.length} posts harvested`);
  console.log(JSON.stringify({ author, count: posts.length, posts }));
  await page.close().catch(() => {});
  await browser.close().catch(() => {});
})().catch((e) => { console.error('FATAL', e.message); process.exit(1); });
