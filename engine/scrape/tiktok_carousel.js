#!/usr/bin/env node
/**
 * Download a TikTok photo-carousel (slideshow) and file it into Tiktok Inspo/<N>/.
 *
 * TikTok gates post data behind a real browser (guest/bot HTTP fetches — even via scrape.do or
 * yt-dlp — get an empty shell), so this drives the project's CDP Chrome (localhost:9222, the same
 * channel the cover step uses). It loads the post, reads the full-res `photomode` slide images
 * from the hydrated DOM in carousel order, downloads them, and files them as 1.jpg, 2.jpg, ...
 * into the next numbered folder under the repo-root `inspo/`, plus a `source.txt`.
 *
 * This is the automated version of the manual browser method in `manual_console.js`.
 *
 * Requires: Chrome reachable on :9222 (auto-launched with the masquerade profile if it isn't),
 * and Playwright (resolved via the node_modules symlink next to this file).
 *
 * Usage:
 *   node tiktok_carousel.js "<tiktok_url>"            # auto next folder
 *   node tiktok_carousel.js "<tiktok_url>" -f 8       # force folder number
 *   node tiktok_carousel.js "<tiktok_url>" --dry-run  # list slides, don't save
 */
const fs = require('fs');
const path = require('path');
const https = require('https');
const { extractStats, attachItemCapture } = require('./extract_stats');
const { connect, context } = require('../lib/cdp');

const DEST_DEFAULT = path.resolve(__dirname, '..', '..', 'inspo'); // repo-root inspo/
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

function parseArgs(argv) {
  const a = { url: null, folder: null, dest: DEST_DEFAULT, dry: false };
  for (let i = 2; i < argv.length; i++) {
    const x = argv[i];
    if (x === '--dry-run') a.dry = true;
    else if (x === '-f' || x === '--folder') a.folder = parseInt(argv[++i], 10);
    else if (x === '-d' || x === '--dest') a.dest = argv[++i];
    else if (!a.url) a.url = x;
  }
  return a;
}

// Slides render as <img> with `photomode` in the CDN path. The swiper loops, so the same slide
// appears multiple times (clones) -- dedupe by the stable hash before `~tplv`, and order by the
// swiper's own data-swiper-slide-index when present (robust to prepended clones).
async function extractSlides(page) {
  return await page.evaluate(() => {
    const imgs = [...document.querySelectorAll('img')].filter(i => ((i.currentSrc || i.src || '').includes('photomode')));
    const byIndex = new Map();
    const order = [];
    const seen = new Set();
    let usedIndex = false;
    for (const img of imgs) {
      const src = img.currentSrc || img.src;
      const key = src.split('~tplv')[0];
      const slideEl = img.closest('[class*="swiper-slide"]');
      const idxAttr = slideEl && slideEl.getAttribute('data-swiper-slide-index');
      if (idxAttr !== null && idxAttr !== undefined && idxAttr !== '') {
        usedIndex = true;
        const n = parseInt(idxAttr, 10);
        if (!byIndex.has(n)) byIndex.set(n, src);
      } else if (!seen.has(key)) {
        seen.add(key); order.push(src);
      }
    }
    const urls = usedIndex ? [...byIndex.entries()].sort((a, b) => a[0] - b[0]).map(e => e[1]) : order;
    return { urls, method: usedIndex ? 'swiper-index' : 'dom-order' };
  });
}

async function meta(page) {
  return await page.evaluate(() => {
    const og = p => (document.querySelector(`meta[property="${p}"]`) || {}).content || '';
    const mu = location.pathname.match(/@([^/]+)/);
    // hashtags the post actually uses (fuel for the self-expanding discovery graph)
    const tags = [...new Set([...document.querySelectorAll('a[href*="/tag/"]')]
      .map(a => ((a.getAttribute('href') || '').match(/\/tag\/([^/?#]+)/) || [])[1])
      .filter(Boolean).map(t => decodeURIComponent(t).toLowerCase()))];
    return { author: mu ? mu[1] : '', title: og('og:title') || document.title, desc: og('og:description'), hashtags: tags };
  });
}

function dl(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': UA, 'Referer': 'https://www.tiktok.com/' } }, r => {
      if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location && redirects < 5) {
        r.resume(); return dl(r.headers.location, redirects + 1).then(resolve, reject);
      }
      if (r.statusCode !== 200) { r.resume(); return reject(new Error('HTTP ' + r.statusCode)); }
      const chunks = []; r.on('data', c => chunks.push(c)); r.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

function nextFolder(dest) {
  fs.mkdirSync(dest, { recursive: true });
  const nums = fs.readdirSync(dest)
    .filter(n => /^\d+$/.test(n) && fs.statSync(path.join(dest, n)).isDirectory())
    .map(Number);
  return nums.length ? Math.max(...nums) + 1 : 1;
}

(async () => {
  const a = parseArgs(process.argv);
  if (!a.url) { console.error('usage: node tiktok_carousel.js "<url>" [-f N] [--dry-run]'); process.exit(1); }

  const browser = await connect();
  const ctx = await context(browser);
  const page = await ctx.newPage();
  const cap = attachItemCapture(page);   // capture /api/item/detail/ (views) before navigating
  try {
    await page.goto(a.url, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
    await page.waitForSelector('img[src*="photomode"]', { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(2500);

    const { urls, method } = await extractSlides(page);
    const info = await meta(page);
    await cap.wait(6000);
    const stats = await extractStats(page, { apiItem: cap.item() }).catch(() => null);
    const finalUrl = page.url();
    if (!urls.length) {
      console.error('!! no photomode slides found -- is this a photo post (not a video)?\n' +
                    '   If TikTok changed its markup, use the manual fallback in manual_console.js.');
      process.exit(2);
    }
    console.log(`found ${urls.length} slides (${method}) | @${info.author} | ${JSON.stringify((info.desc || info.title || '').slice(0, 80))}`);

    if (a.dry) {
      urls.forEach((u, i) => console.log(`  ${i + 1}. ${u.split('~tplv')[0].split('/').pop()}`));
      return;
    }

    const n = a.folder || nextFolder(a.dest);
    const out = path.join(a.dest, String(n));
    fs.mkdirSync(out, { recursive: true });
    for (let i = 0; i < urls.length; i++) {
      const buf = await dl(urls[i]);
      fs.writeFileSync(path.join(out, `${i + 1}.jpg`), buf);
      console.log(`  saved ${i + 1}.jpg (${Math.round(buf.length / 1024)} KB)`);
    }
    const now = new Date().toISOString().slice(0, 16).replace('T', ' ');
    const s = stats || {};
    fs.writeFileSync(path.join(out, 'source.txt'),
      `url: ${finalUrl}\ninput_url: ${a.url}\nauthor: @${info.author}\n` +
      `slides: ${urls.length}\ndownloaded: ${now}\ncaption: ${info.desc || info.title || ''}\n` +
      `hashtags: ${(info.hashtags || []).map(h => '#' + h).join(' ')}\n` +
      `posting_date: ${s.posting_date || ''}\nviews: ${s.views ?? ''}\nlikes: ${s.likes ?? ''}\n` +
      `comments: ${s.comments ?? ''}\nshare: ${s.share ?? ''}\nsave: ${s.save ?? ''}\n`);
    if (stats) console.log(`   stats: views=${s.views} likes=${s.likes} comments=${s.comments} share=${s.share} save=${s.save} (${s.source})`);
    console.log(`-> filed ${urls.length} slides into ${out}/`);
  } finally {
    await page.close().catch(() => {});
    await browser.close().catch(() => {}); // detaches CDP; leaves Chrome running
  }
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
