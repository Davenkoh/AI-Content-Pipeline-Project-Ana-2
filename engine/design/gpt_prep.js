// Prepare ChatGPT composer over CDP: attach 3 persona refs + type the cover prompt. Does NOT send.
// Persona is selected by the MASQ_PERSONA env var (default Ana); refs come from prep_cover_refs.py.
// Runs copied into _work/scripts/ (so cdp.js is its flat sibling there — see WORKFLOW §8 scaffold).
const { connect, page: findPage } = require('./cdp');
const fs = require('fs');
const path = require('path');

(async () => {
  const ROOT = path.resolve(__dirname, '..');
  const COVER = path.join(ROOT, 'cover');
  const SHOTS = path.join(COVER, '_shots');
  fs.mkdirSync(SHOTS, { recursive: true });
  const UP = path.join(COVER, 'to_upload');
  const PERSONA = process.env.MASQ_PERSONA || 'Ana';
  // attach every ref prep_cover_refs staged (1_/2_/3_ required + any optional 4_… variation sheet),
  // sorted so the hero leads. Backward-compatible: a character with only the 3 required still works.
  const refs = fs.readdirSync(UP)
    .filter(f => /\.(png|jpe?g|webp)$/i.test(f))
    .sort()
    .map(f => path.join(UP, f));

  let prompt = fs.readFileSync(path.join(COVER, 'gpt_image_prompt.txt'), 'utf8');
  prompt = prompt.split('\n').filter(l => !l.trim().startsWith('[Attach')).join('\n').trim();

  const b = await connect();
  const page = await findPage(b, 'chatgpt.com', { create: true, gotoUrl: 'https://chatgpt.com/' });
  await page.bringToFront();
  await page.waitForTimeout(500);

  // 1) attach reference images
  let inputs = await page.$$('input[type=file]');
  console.log('file inputs found:', inputs.length);
  if (inputs.length === 0) {
    // open the "+" menu to reveal the file input
    const plus = await page.$('[data-testid="composer-plus-btn"], button[aria-label*="Add" i], button[aria-label*="attach" i]');
    if (plus) { await plus.click(); await page.waitForTimeout(900); }
    inputs = await page.$$('input[type=file]');
    console.log('after +menu, file inputs:', inputs.length);
  }
  if (inputs.length === 0) { console.log('!! no file input — aborting'); await b.close(); return; }
  await inputs[0].setInputFiles(refs);
  console.log('attached', refs.length, 'refs; waiting for upload…');

  // 2) wait for 3 attachment thumbnails to render
  for (let i = 0; i < 40; i++) {
    const n = await page.evaluate(() => {
      const imgs = document.querySelectorAll('img[alt*="Uploaded" i], img[alt*="preview" i], [data-testid*="attachment"] img, form img');
      return imgs.length;
    });
    if (n >= refs.length) { console.log('thumbnails:', n); break; }
    await page.waitForTimeout(500);
  }
  await page.waitForTimeout(1500);

  // 3) type the prompt into the composer
  const ta = await page.$('#prompt-textarea');
  if (!ta) { console.log('!! no #prompt-textarea'); await page.screenshot({ path: path.join(SHOTS, 'prep_noinput.png') }); await b.close(); return; }
  await ta.click();
  await page.keyboard.insertText(prompt);
  await page.waitForTimeout(800);

  const val = await page.evaluate(() => document.querySelector('#prompt-textarea')?.innerText || '');
  console.log('composer chars:', val.length);
  await page.screenshot({ path: path.join(SHOTS, 'prep.png') });
  console.log('prep screenshot saved');
  await b.close();
})();
