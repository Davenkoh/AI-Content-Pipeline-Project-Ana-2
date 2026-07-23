#!/usr/bin/env node
/**
 * tiktok_stats.js — scrape one TikTok post's metrics and print them as JSON.
 *
 * Drives the project's CDP Chrome (localhost:9222, same channel as the carousel scraper),
 * loads the post, and reads exact counts + posting date via extract_stats.js. Used by
 * sheets.py for BOTH the inspiration's stats (TikTok Inspo Analysis) and a posted character's
 * post's stats (the character's fact tab). TikTok gates this data behind a real browser, hence CDP.
 *
 * Usage: node tiktok_stats.js "<tiktok_url>"
 * Output (stdout, last line): {"views":..,"likes":..,"comments":..,"share":..,"save":..,
 *                              "posting_date":"YYYY-MM-DD","author":"..","source":"json|dom|none"}
 */
const { extractStats, attachItemCapture } = require('./extract_stats');
const { connect, context } = require('../lib/cdp');

(async () => {
  const url = process.argv[2];
  if (!url) { console.error('usage: node tiktok_stats.js "<tiktok_url>"'); process.exit(1); }
  const browser = await connect();
  const ctx = await context(browser);
  const page = await ctx.newPage();
  const cap = attachItemCapture(page);   // must be attached BEFORE navigation
  try {
    await page.goto(url, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
    // wait for either the hydrated JSON or a rendered counter
    await page.waitForFunction(
      () => document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__') ||
            document.getElementById('SIGI_STATE') ||
            document.querySelector('[data-e2e="like-count"],[data-e2e="browse-like-count"]'),
      { timeout: 30000 }).catch(() => {});
    await cap.wait(9000);                 // let the /api/item/detail/ XHR arrive (carries views)
    const stats = await extractStats(page, { apiItem: cap.item() });
    console.error(`[stats] @${stats.author || '?'} login=${stats.loggedIn} src=${stats.source} ` +
      `views=${stats.views} likes=${stats.likes} comments=${stats.comments} ` +
      `share=${stats.share} save=${stats.save} posted=${stats.posting_date}`);
    if (stats.source === 'none') console.error('[stats] WARN: no counts found (login wall / markup change / private post)');
    else if (stats.loggedIn === false || stats.views === '')
      console.error('[stats] WARN: not logged into TikTok — views/posting-date unavailable for photo posts. ' +
        'Re-auth: node engine/scrape/tiktok_login.js --open');
    console.log(JSON.stringify(stats));
  } finally {
    await page.close().catch(() => {});
    await browser.close().catch(() => {}); // detaches CDP; leaves Chrome running
  }
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
