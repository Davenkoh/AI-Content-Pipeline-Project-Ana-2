// Generate ONE base-reference image over CDP: open a fresh ChatGPT chat, attach reference image(s),
// type a prompt, send, wait for the finished image, download it. For topping up an EXISTING
// character's Base References (e.g. Chloe's missing half-front) without the full new-character flow.
// Mirrors the cover pipeline (gpt_prep -> gpt_send -> gpt_grab) but single-ref + arbitrary prompt/out.
//
// Usage:
//   node gen_base_ref.js --attach <img> [--attach <img2> ...] (--prompt "..." | --prompt-file f.txt) --out <png>
const { connect, page: findPage } = require('../lib/cdp');
const fs = require('fs');
const path = require('path');

function arg(name, def) { const i = process.argv.indexOf(name); return i >= 0 ? process.argv[i + 1] : def; }
function args(name) { const out = []; process.argv.forEach((a, i) => { if (a === name) out.push(process.argv[i + 1]); }); return out; }

(async () => {
  const attach = args('--attach');
  const out = arg('--out');
  let prompt = arg('--prompt');
  const pf = arg('--prompt-file');
  if (!prompt && pf) prompt = fs.readFileSync(pf, 'utf8').trim();
  if (!attach.length || !out || !prompt) {
    console.log('usage: --attach <img> [--attach ...] (--prompt "..." | --prompt-file f) --out <png>');
    process.exit(1);
  }

  const b = await connect();
  const page = await findPage(b, 'chatgpt.com', { create: true, gotoUrl: 'https://chatgpt.com/' });
  await page.bringToFront();
  await page.goto('https://chatgpt.com/', { waitUntil: 'domcontentloaded' }).catch(() => {}); // fresh chat
  await page.waitForTimeout(1800);

  // 1) attach reference image(s)
  let inputs = await page.$$('input[type=file]');
  if (inputs.length === 0) {
    const plus = await page.$('[data-testid="composer-plus-btn"], button[aria-label*="Add" i], button[aria-label*="attach" i]');
    if (plus) { await plus.click(); await page.waitForTimeout(900); }
    inputs = await page.$$('input[type=file]');
  }
  if (inputs.length === 0) { console.log('!! no file input — aborting'); await b.close(); process.exit(2); }
  await inputs[0].setInputFiles(attach.map(p => path.resolve(p)));
  console.log('attached', attach.length, 'ref(s); waiting for upload…');
  for (let i = 0; i < 40; i++) {
    const n = await page.evaluate(() => document.querySelectorAll('img[alt*="Uploaded" i], img[alt*="preview" i], [data-testid*="attachment"] img, form img').length);
    if (n >= attach.length) break;
    await page.waitForTimeout(700);
  }

  // 2) type the prompt (use the SPECIFIC composer id — a bare `textarea` selector can match a
  //    hidden element and fail the click; mirror gpt_prep.js)
  await page.waitForTimeout(1500);                       // let the upload settle
  const ta = await page.$('#prompt-textarea');
  if (!ta) { console.log('!! no #prompt-textarea composer'); await b.close(); process.exit(2); }
  await ta.click();
  await page.keyboard.insertText(prompt);
  await page.waitForTimeout(600);

  // 3) send
  let send = await page.$('[data-testid="send-button"]');
  if (!send) send = await page.$('button[aria-label*="Send" i]');
  if (send) { await send.click(); console.log('clicked send'); }
  else { await page.keyboard.press('Enter'); console.log('pressed Enter'); }

  // 4) poll for the finished image = the LARGEST-RENDERED image on the page. The generated result
  //    displays wide; attachments (even the copy re-shown inside the sent user message) stay small
  //    ~256px thumbnails. So require the pick to render wide (rw>=320) — excludes those thumbs during
  //    the wait — and hold stable for 3 polls. Ignore the 'streaming' flag: a reasoning UI ("Thought
  //    for 2m") keeps the stop-button visible long after the image is done.
  const findBig = async () => page.evaluate(() => {
    let best = null;
    document.querySelectorAll('img').forEach(im => {
      const src = im.currentSrc || im.src;
      if (!src || src.startsWith('data:')) return;
      const w = im.naturalWidth || 0, rw = Math.round(im.getBoundingClientRect().width);
      if (w >= 700 && rw >= 320 && (!best || rw > best.rw)) best = { src, w, h: im.naturalHeight || 0, rw };
    });
    return best;
  });
  let prev = null, stable = 0, done = null;
  for (let i = 0; i < 120; i++) {                // up to ~120*3s = ~360s
    await page.waitForTimeout(3000);
    let best;
    try { best = await findBig(); } catch (e) { continue; }
    console.log(`t+${(i + 1) * 3}s  big-img=${best ? best.w + 'x' + best.h + ' rw' + best.rw : 'none'}`);
    if (best) { if (prev === best.src) stable++; else stable = 1; prev = best.src; if (stable >= 3) { done = best; break; } }
    else stable = 0;
  }
  if (!done) { console.log('!! no finished image in time'); await b.close(); process.exit(3); }
  console.log('FINAL image', done.w + 'x' + done.h);

  // 5) download via in-page fetch (handles blob: and authed oaiusercontent URLs)
  const dataUrl = await page.evaluate(async (src) => {
    const r = await fetch(src); const blob = await r.blob();
    return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(blob); });
  }, done.src);
  fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
  fs.writeFileSync(path.resolve(out), Buffer.from(dataUrl.split(',')[1], 'base64'));
  console.log('saved', out, fs.statSync(path.resolve(out)).size, 'bytes');
  await b.close();
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
