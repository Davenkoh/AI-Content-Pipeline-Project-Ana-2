#!/usr/bin/env node
/**
 * tiktok_login.js — check / restore the masquerade Chrome's TikTok login.
 *
 * TikTok only hydrates a PHOTO post's full stats (views, posting date, author, saves)
 * when the browser is logged IN. The cover-gen + scraping share the `~/.masquerade_chrome`
 * profile on CDP :9222; when its TikTok session expires, `post-stats` silently loses views.
 * This is the one place to verify + re-auth that session.
 *
 *   node tiktok_login.js            # report login state; exit 0 = logged in, 2 = logged out
 *   node tiktok_login.js --open     # open TikTok's login page in the CDP Chrome, then wait
 *                                   # (polls for the session cookie) until you finish logging in
 *
 * Leaves Chrome running (detaches CDP) so the next scrape reuses the session.
 */
const { connect, context } = require('../lib/cdp');

const LOGIN_URL = 'https://www.tiktok.com/login';
const SESSION_COOKIES = ['sessionid', 'sessionid_ss'];

async function isLoggedIn(ctx) {
  const cookies = await ctx.cookies('https://www.tiktok.com');
  return cookies.some(c => SESSION_COOKIES.includes(c.name) && c.value);
}

(async () => {
  const open = process.argv.includes('--open');
  const browser = await connect();
  const ctx = await context(browser);

  if (!open) {
    const ok = await isLoggedIn(ctx);
    console.log(ok ? '[login] TikTok: LOGGED IN ✓' : '[login] TikTok: LOGGED OUT ✗  (run: node tiktok_login.js --open)');
    await browser.close().catch(() => {});
    process.exit(ok ? 0 : 2);
  }

  if (await isLoggedIn(ctx)) {
    console.log('[login] already logged in ✓ — nothing to do');
    await browser.close().catch(() => {});
    process.exit(0);
  }

  const page = (await ctx.pages())[0] || await ctx.newPage();
  await page.goto(LOGIN_URL, { waitUntil: 'load', timeout: 60000 }).catch(() => {});
  await page.bringToFront().catch(() => {});
  console.log('[login] Opened TikTok login in the masquerade Chrome window.');
  console.log('[login] → Switch to that Chrome window and log in as the Ana account (@solo.with.ana).');
  console.log('[login] Waiting for the session (up to 5 min)…');

  const deadline = Date.now() + 5 * 60 * 1000;
  while (Date.now() < deadline) {
    await page.waitForTimeout(3000);
    if (await isLoggedIn(ctx)) {
      console.log('[login] TikTok login detected ✓ — session saved to the profile.');
      await browser.close().catch(() => {});
      process.exit(0);
    }
  }
  console.error('[login] timed out — still not logged in. Re-run when ready: node tiktok_login.js --open');
  await browser.close().catch(() => {});
  process.exit(2);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
