// Send the prepared composer, wait for the GPT image to finish, download it.
// Runs copied into _work/scripts/ (cdp.js is its flat sibling there — see WORKFLOW §8 scaffold).
const { connect, page: findPage } = require('./cdp');
const fs = require('fs');
const path = require('path');

(async () => {
  const ROOT = path.resolve(__dirname, '..');
  const COVER = path.join(ROOT, 'cover');
  const SHOTS = path.join(COVER, '_shots');
  fs.mkdirSync(SHOTS, { recursive: true });

  const b = await connect();
  const page = await findPage(b, 'chatgpt.com');
  if (!page) { console.log('!! no chatgpt page'); await b.close(); return; }
  await page.bringToFront();

  // send
  let send = await page.$('[data-testid="send-button"]');
  if (!send) send = await page.$('button[aria-label*="Send" i]');
  if (send) { await send.click(); console.log('clicked send'); }
  else { await page.click('#prompt-textarea'); await page.keyboard.press('Enter'); console.log('pressed Enter'); }

  // poll for a finished assistant image
  const findImg = async () => page.evaluate(() => {
    const turns = document.querySelectorAll('[data-message-author-role="assistant"]');
    let best = null;
    turns.forEach(t => t.querySelectorAll('img').forEach(im => {
      const w = im.naturalWidth || 0;
      if (w > 400 && (!best || w > best.w)) best = { src: im.src, w, h: im.naturalHeight || 0 };
    }));
    const streaming = !!document.querySelector('[data-testid="stop-button"], button[aria-label*="Stop" i]');
    return { best, streaming };
  });

  let prev = null, stable = 0, done = null;
  for (let i = 0; i < 80; i++) {           // up to ~80*4s = ~320s
    await page.waitForTimeout(4000);
    let st;
    try { st = await findImg(); } catch (e) { continue; }
    if (i % 4 === 0) {
      try { await page.screenshot({ path: path.join(SHOTS, `gen_${String(i).padStart(2, '0')}.png`) }); } catch {}
    }
    const tag = st.best ? `${st.best.w}x${st.best.h}` : 'none';
    console.log(`t+${(i + 1) * 4}s  img=${tag}  streaming=${st.streaming}`);
    if (st.best && !st.streaming) {
      if (prev && st.best.src === prev) stable++; else stable = 1;
      prev = st.best.src;
      if (stable >= 2) { done = st.best; break; }
    } else { stable = 0; }
  }

  if (!done) { console.log('!! no finished image in time'); await page.screenshot({ path: path.join(SHOTS, 'gen_timeout.png') }); await b.close(); return; }
  console.log('FINAL image', done.w + 'x' + done.h);

  // download via in-page fetch (handles blob: and authed oaiusercontent URLs)
  const dataUrl = await page.evaluate(async (src) => {
    const r = await fetch(src); const blob = await r.blob();
    return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(blob); });
  }, done.src);
  const b64 = dataUrl.split(',')[1];
  const out = path.join(COVER, `${(process.env.MASQ_PERSONA || 'Ana').toLowerCase()}_cover_raw.png`);
  fs.writeFileSync(out, Buffer.from(b64, 'base64'));
  console.log('saved', out, fs.statSync(out).size, 'bytes');
  await page.screenshot({ path: path.join(SHOTS, 'gen_final.png') });
  await b.close();
})();
