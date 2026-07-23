// Grab the largest generated image on the ChatGPT page and save it.
// Runs copied into _work/scripts/ (cdp.js is its flat sibling there — see WORKFLOW §8 scaffold).
const { connect, page: findPage } = require('./cdp');
const fs = require('fs');
const path = require('path');

(async () => {
  const ROOT = path.resolve(__dirname, '..');
  const COVER = path.join(ROOT, 'cover');
  const b = await connect();
  const page = await findPage(b, 'chatgpt.com');
  if (!page) { console.log('!! no chatgpt page'); await b.close(); return; }

  const cands = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('img').forEach(im => {
      out.push({ src: im.currentSrc || im.src, w: im.naturalWidth || 0, h: im.naturalHeight || 0,
                 rw: Math.round(im.getBoundingClientRect().width) });
    });
    return out.filter(c => c.src && !c.src.startsWith('data:')).sort((a, b) => (b.w * b.h) - (a.w * a.h));
  });
  console.log('image candidates (top 6):');
  cands.slice(0, 6).forEach(c => console.log(`  ${c.w}x${c.h} render=${c.rw}  ${c.src.slice(0, 80)}`));
  // the generated image DISPLAYS big; reference thumbnails display small — pick the largest
  // on-screen render (rw) among full-size images. Robust to the gen's aspect ratio (3:4, 9:16, …),
  // unlike sorting by pixel area which can grab a 2:3 reference photo.
  const pick = cands.filter(c => c.w >= 700).sort((a, b) => b.rw - a.rw)[0] || cands[0];
  if (!pick) { console.log('!! no image'); await b.close(); return; }
  console.log('PICK', pick.w + 'x' + pick.h, pick.src.slice(0, 90));

  const dataUrl = await page.evaluate(async (src) => {
    const r = await fetch(src); const blob = await r.blob();
    return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result); fr.readAsDataURL(blob); });
  }, pick.src);
  const out = path.join(COVER, `${(process.env.MASQ_PERSONA || 'Ana').toLowerCase()}_cover_raw.png`);
  fs.writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
  console.log('saved', out, fs.statSync(out).size, 'bytes');
  await b.close();
})();
