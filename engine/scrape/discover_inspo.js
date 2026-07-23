#!/usr/bin/env node
/**
 * discover_inspo.js — seed-based inspo discovery, RANKED BY PERFORMANCE.
 *
 * Reads discovery_seeds.json (curated creators + hashtags/searches), drives the project's CDP
 * Chrome to each seed page, collects recent photo-carousel URLs *with their view counts*, dedupes
 * against what's already in inspo/, and reports the NEW candidates **ranked by views** so the loop
 * studies WINNERS, not whatever was posted. With --pull N it pulls the top N.
 *
 * A seed creator is not an endorsement of every post: the metric ranking here + the analysis gate
 * in the ideate skill (read the slides, why it worked, funnel fit, replicability) decide what's worth it.
 *
 * Usage:
 *   node discover_inspo.js --carousels                   # ranked carousels from all seeds
 *   node discover_inspo.js --carousels --min-views 200K  # gate out low performers
 *   node discover_inspo.js --carousels --pull 3          # pull the top 3 by views
 */
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');
const { connect, context } = require('../lib/cdp');

const HERE = __dirname;
const SEEDS = path.join(HERE, 'discovery_seeds.json');
const INSPO = path.resolve(HERE, '..', '..', 'inspo');

function parseViews(s) {
  if (!s) return 0;
  const m = String(s).trim().replace(/,/g, '').match(/([\d.]+)\s*([KMB万亿]?)/i);
  if (!m) return 0;
  const n = parseFloat(m[1]); const u = (m[2] || '').toUpperCase();
  const mult = u === 'B' ? 1e9 : u === 'M' ? 1e6 : u === 'K' ? 1e3 : u === '万' ? 1e4 : u === '亿' ? 1e8 : 1;
  return Math.round(n * mult);
}
function fmtViews(n) { return n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? Math.round(n / 1e3) + 'K' : n ? String(n) : '?'; }

function parseArgs(argv) {
  const a = { pull: 0, carousels: false, min: 0, graph: false, harvest: false };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--pull') a.pull = parseInt(argv[++i], 10) || 0;
    else if (argv[i] === '--carousels') a.carousels = true;
    else if (argv[i] === '--min-views') a.min = parseViews(argv[++i]);
    else if (argv[i] === '--graph') a.graph = true;     // creator-agnostic: crawl the self-grown tag pool
    else if (argv[i] === '--harvest') a.harvest = true; // grow the pool from existing pulls, no scan
  }
  return a;
}

function postId(url) {
  const m = url.match(/\/(?:video|photo)\/(\d+)/);
  if (m) return 'tt:' + m[1];
  return url.split('?')[0];
}

function seenIds() {
  const ids = new Set();
  if (!fs.existsSync(INSPO)) return ids;
  for (const n of fs.readdirSync(INSPO)) {
    const sp = path.join(INSPO, n, 'source.txt');
    if (!fs.existsSync(sp)) continue;
    for (const line of fs.readFileSync(sp, 'utf8').split('\n')) {
      const m = line.match(/^(?:url|input_url):\s*(\S+)/);
      if (m) ids.add(postId(m[1]));
    }
  }
  return ids;
}

const DYN = path.join(HERE, 'dynamic_hashtags.json');
function loadDyn() { try { return JSON.parse(fs.readFileSync(DYN, 'utf8')); } catch { return { relevance_keywords: [], hashtags: {} }; } }
function saveDyn(d) { fs.writeFileSync(DYN, JSON.stringify(d, null, 2) + '\n'); }
function isRelevant(tag, kws) { const t = tag.toLowerCase(); return kws.some(k => t.includes(k.replace(/\s+/g, ''))); }
// harvest the hashtags from every pulled post's source.txt; add travel-relevant NEW ones to the pool
function harvest() {
  const d = loadDyn(); const kws = d.relevance_keywords || []; const added = [];
  if (fs.existsSync(INSPO)) {
    for (const n of fs.readdirSync(INSPO)) {
      const sp = path.join(INSPO, n, 'source.txt');
      if (!fs.existsSync(sp)) continue;
      const tags = (fs.readFileSync(sp, 'utf8').match(/#[\p{L}\p{N}_]+/gu) || []).map(t => t.slice(1).toLowerCase());
      for (const t of tags) if (!d.hashtags[t] && isRelevant(t, kws)) { d.hashtags[t] = { source: 'harvested:' + n, added: new Date().toISOString().slice(0, 10) }; added.push(t); }
    }
  }
  if (added.length) saveDyn(d);
  return { added, total: Object.keys(d.hashtags).length };
}

// collect {url, views} for every post link on the page, grabbing the view-count shown on each thumb
async function candidatesFrom(page, url) {
  await page.goto(url, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(3500);
  for (let i = 0; i < 3; i++) { await page.mouse.wheel(0, 1600).catch(() => {}); await page.waitForTimeout(900); }
  return await page.evaluate(() => {
    const re = /\/@[\w.-]+\/(video|photo)\/\d+/;
    const out = []; const seen = new Set();
    document.querySelectorAll('a[href]').forEach(a => {
      const h = (a.href || '').split('?')[0];
      if (!re.test(h) || seen.has(h)) return; seen.add(h);
      // view count lives inside the post <a> (confirmed: strong[data-e2e="video-views"])
      const cont = a.closest('[data-e2e="user-post-item"]') || a;
      const vc = a.querySelector('strong[data-e2e="video-views"]') || cont.querySelector('strong[data-e2e="video-views"]');
      out.push({ url: h, views: vc ? vc.textContent.trim() : '' });
    });
    return out;
  });
}

(async () => {
  const a = parseArgs(process.argv);
  if (a.harvest && !a.pull && !a.graph) {  // standalone: grow the pool from existing pulls, no browser
    const h = harvest();
    console.log(`harvested ${h.added.length} new travel hashtag(s): ${h.added.map(t => '#' + t).join(' ') || '(none)'}\npool now ${h.total} tags`);
    return;
  }
  if (!fs.existsSync(SEEDS)) { console.error('missing discovery_seeds.json'); process.exit(1); }
  const seeds = JSON.parse(fs.readFileSync(SEEDS, 'utf8'));
  const seen = seenIds();
  console.log(`already pulled: ${seen.size} posts on record${a.min ? ` | min views: ${fmtViews(a.min)}` : ''}\n`);

  const browser = await connect();
  const ctx = await context(browser);
  const page = await ctx.newPage();
  const found = new Map(); // id -> {url, views:number}

  try {
    const cfg = seeds.tiktok || {};
    let urls = [...(cfg.creators || []), ...(cfg.hashtags || []), ...(cfg.searches || [])];
    if (a.graph) {                                   // creator-agnostic: also crawl the self-grown pool
      urls = [...new Set([...urls, ...Object.keys(loadDyn().hashtags).map(h => `https://www.tiktok.com/tag/${h}`)])];
    }
    for (const seedUrl of urls) {
      process.stdout.write(`scanning ${seedUrl} ... `);
      let cands = [];
      try { cands = await candidatesFrom(page, seedUrl); } catch (e) { console.log('err', e.message); continue; }
      let fresh = 0;
      for (const c of cands) {
        const id = postId(c.url);
        if (seen.has(id) || found.has(id)) continue;
        if (a.carousels && !/\/photo\//.test(c.url)) continue;   // static carousels only
        const v = parseViews(c.views);
        if (a.min && v < a.min) continue;                        // performance gate
        found.set(id, { url: c.url, views: v }); fresh++;
      }
      console.log(`${cands.length} posts, ${fresh} new`);
    }
  } finally {
    await page.close().catch(() => {});
    await browser.close().catch(() => {});
  }

  const list = [...found.values()].sort((x, y) => y.views - x.views);   // WINNERS first
  console.log(`\n=== ${list.length} NEW candidate carousel(s), ranked by views ===`);
  list.forEach((c, i) => console.log(`  [${i + 1}] ${fmtViews(c.views).padStart(6)}  ${/\/photo\//.test(c.url) ? 'carousel' : 'video   '}  ${c.url}`));
  if (a.pull && list.length) {
    for (const c of list.slice(0, a.pull)) {
      console.log(`\n-> pulling (${fmtViews(c.views)} views) ${c.url}`);
      const r = spawnSync('node', [path.join(HERE, 'tiktok_carousel.js'), c.url], { stdio: 'inherit' });
      if (r.status === 2) console.log('   (not a photo carousel, skipped)');
    }
  }
  if (a.pull) {  // every pull widens the graph
    const h = harvest();
    console.log(`\n[graph] harvested ${h.added.length} new hashtag(s) -> pool now ${h.total}${h.added.length ? ': ' + h.added.map(t => '#' + t).join(' ') : ''}`);
  }
  if (!a.pull) console.log('\n(ranked by views; --graph crawls the self-grown tag pool, --pull N pulls + harvests, --harvest grows the pool from existing pulls)');
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
