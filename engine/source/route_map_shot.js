// Screenshot a REAL pinned Google Maps route (Tokyo -> Hakone -> Kyoto -> Osaka) at 1080x1920
// for the D "Route & Days" slide. Uses the Maps Embed API (free) with the PLACES key from
// keys.env; falls back to the public maps directions page if the embed errors.
// Usage: node engine/source/route_map_shot.js [--out media/graded/route_map.png]
const path = require('path');
const fs = require('fs');

// Repo root = walk UP from here until the .gitignore sentinel (same trick as engine/lib/keys.py);
// playwright lives in engine/node_modules, and keys.env + media/graded hang off the repo root.
function findRepoRoot(start) {
  let d = start;
  for (;;) {
    if (fs.existsSync(path.join(d, '.gitignore'))) return d;
    const parent = path.dirname(d);
    if (parent === d) return start;
    d = parent;
  }
}
const REPO = findRepoRoot(__dirname);
const { chromium } = require(path.join(REPO, 'engine', 'node_modules', 'playwright'));

function keyFromEnvFile(name) {
  if (process.env[name]) return process.env[name];
  const envPath = path.join(REPO, 'keys.env');
  if (!fs.existsSync(envPath)) return null;
  const txt = fs.readFileSync(envPath, 'utf8');
  const m = txt.match(new RegExp('^' + name + '=(.+)$', 'm'));
  return m ? m[1].trim() : null;
}

(async () => {
  const outIdx = process.argv.indexOf('--out');
  const out = path.resolve(REPO, outIdx > -1 ? process.argv[outIdx + 1] : 'media/graded/route_map.png');
  const key = keyFromEnvFile('PLACES');
  if (!key) { console.error('no PLACES key found'); process.exit(1); }

  const embed = 'https://www.google.com/maps/embed/v1/directions'
    + '?key=' + encodeURIComponent(key)
    + '&origin=' + encodeURIComponent('Tokyo Station, Japan')
    + '&destination=' + encodeURIComponent('Osaka Station, Japan')
    + '&waypoints=' + encodeURIComponent('Hakone, Japan|Kyoto Station, Japan')
    + '&mode=driving&language=en'
    + '&center=35.1,137.6&zoom=8'; // whole Tokyo->Osaka corridor + endpoint pins inside a 1080-wide portrait frame

  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0}html,body{width:1080px;height:1920px;overflow:hidden}
iframe{width:1080px;height:1920px;border:0}
</style></head><body><iframe src="${embed}" allowfullscreen></iframe></body></html>`;
  const hp = path.join(__dirname, '_route_map.html');
  fs.writeFileSync(hp, html);

  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + encodeURI(hp), { waitUntil: 'networkidle' });
  await page.waitForTimeout(4500); // let tiles + route polyline finish drawing
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1920 } });
  await browser.close();
  fs.unlinkSync(hp);
  console.log('wrote', out);
})();
