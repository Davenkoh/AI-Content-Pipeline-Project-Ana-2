// engine/lib/cdp.js — the one home for the CDP Chrome connection.
//
// Two patterns lived copy-pasted across scrape/ and design/:
//   - scrape/*  connect-or-launch the shared profile on :9222, then open a fresh page.
//   - design/*  connect to an already-running :9222 and find the ChatGPT tab.
// Both now route through here.
//
// `~/.masquerade_chrome` is an intentional technical identifier kept across the
// Project Ana rename (the shared profile logged into ChatGPT + each character's
// TikTok) — do not "fix" the name.
const { chromium } = require('playwright');
const path = require('path');
const { spawn } = require('child_process');

const CDP = process.env.MASQ_CDP || 'http://localhost:9222';
const CHROME = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PROFILE = path.join(process.env.HOME, '.masquerade_chrome');

// Connect to the CDP Chrome on :9222, launching it with the masquerade profile if it's down.
async function connect() {
  try { return await chromium.connectOverCDP(CDP); } catch (_) {}
  console.error('[no CDP on :9222 -> launching Chrome with the masquerade profile]');
  spawn(CHROME, [`--remote-debugging-port=9222`, `--user-data-dir=${PROFILE}`],
        { detached: true, stdio: 'ignore' }).unref();
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 1000));
    try { return await chromium.connectOverCDP(CDP); } catch (_) {}
  }
  throw new Error('could not reach Chrome CDP on :9222');
}

// The browser's first existing context, or a fresh one.
async function context(browser) {
  return browser.contexts()[0] || (await browser.newContext());
}

// Find an open page whose URL contains `urlIncludes`. Options:
//   create:true + gotoUrl  -> open a new tab there if none matched
//   fallbackFirst:true     -> return the first open page if none matched
async function page(browser, urlIncludes, opts = {}) {
  const ctx = await context(browser);
  let pg = ctx.pages().find(p => p.url().includes(urlIncludes));
  if (!pg && opts.create) {
    pg = await ctx.newPage();
    if (opts.gotoUrl) await pg.goto(opts.gotoUrl);
  }
  if (!pg && opts.fallbackFirst) pg = ctx.pages()[0];
  return pg;
}

module.exports = { connect, context, page, CDP, CHROME, PROFILE };
