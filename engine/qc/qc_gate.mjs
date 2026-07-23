#!/usr/bin/env node
/**
 * qc_gate.mjs — deterministic pre-delivery QC for one framework post folder (Project Ana 2.0).
 *
 * Mechanical, dependency-free gate that hard-blocks a draft whose deliverables don't match its
 * copy.json. Vision checks (legibility, cover identity, batch-graded look, watermark corners)
 * are NOT here — those are the routine's job via Read on the PNGs.
 *
 * Usage:  node qc_gate.mjs "<post folder>" [--framework A|B|C1|C2]
 * Output: JSON { pass, ok[], warn[], issues[] } then human-readable lines.
 *         exit 0 = pass · 1 = fail · 2 = bad usage.
 *
 * What it checks (all against the 1080x1920 framework spec in CONTRACT.md):
 *   1. copy.json exists + parses; if --framework given, copy.option must equal it.
 *   2. final/ exists; names ^NN_role.png^ (variant suffix stripped); numbering contiguous from
 *      01; 01_cover.png present; role sequence + count EXACTLY equal to copy.json's slides
 *      (role = the renderer's role name: split->body, everything else->its own type); no strays.
 *   3. every final/ PNG is exactly 1080x1920 (IHDR bytes, no deps).
 *   4. caption.txt non-empty and free of em/en dashes.
 *   5. flags.md present + non-empty (the fact-check flag sheet).
 *   6. every photo slug a slide references resolves under media/graded (mockup: graded OR brand)
 *      and has an attribution row in media/manifest.json; char_photo resolves under chars/.
 *      Brand / app-icon / route-map assets are first-party -> exempt from the manifest row.
 *   7. WARN-only: _work/render/ retains both _human and _nohuman cover+save renders.
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ---- repo root (holds media/, chars/): walk UP until the .gitignore sentinel (same trick as
// engine/lib/keys.py's keys.env discovery). media/graded, media/brand, chars, manifest hang off it.
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
const GRADED = path.join(REPO, 'media', 'graded');
const BRAND = path.join(REPO, 'media', 'brand');
const CHARS = path.join(REPO, 'chars');
const MANIFEST = path.join(REPO, 'media', 'manifest.json');

// ---- args ----
const argv = process.argv.slice(2);
let dir = null, framework = null;
for (let i = 0; i < argv.length; i++) {
  const x = argv[i];
  if (x === '--framework' || x === '-f') framework = argv[++i];
  else if (!dir) dir = x;
}
if (!dir) { console.error('usage: node qc_gate.mjs "<post folder>" [--framework A|B|C1|C2]'); process.exit(2); }

const issues = [];
const ok = [];
const warn = [];
const before = () => issues.length;               // mark, to add an ok line only when a section is clean
const cleanSince = (n, msg) => { if (issues.length === n) ok.push(msg); };

// role naming mirrors the renderer's ROLE map (build.js): split -> body, else the type itself.
const ROLE = { cover: 'cover', split: 'body', plug: 'plug', save: 'save',
               divider: 'divider', notes: 'notes', step: 'step', favorites: 'favorites' };
const NAME_RE = /^\d{2}_[a-z0-9]+\.png$/;         // suffix-stripped: 01_cover.png, not 01_cover_human.png
const DASH = /[—–]/;                              // em — / en –
const EXTS = ['jpg', 'png', 'jpeg'];

function pngSize(file) {
  const fd = fs.openSync(file, 'r');
  const buf = Buffer.alloc(24);
  fs.readSync(fd, buf, 0, 24, 0);
  fs.closeSync(fd);
  if (buf.toString('ascii', 1, 4) !== 'PNG') return null;
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}
function resolvesIn(base, slug) {
  if (/\.(jpg|jpeg|png)$/i.test(slug)) return fs.existsSync(path.join(base, slug));
  return EXTS.some(e => fs.existsSync(path.join(base, slug + '.' + e)));
}
// first-party assets are produced by our own tools (app_icons.py -> app_*, route_map_shot.js ->
// route_map, brand app mockups under media/brand) — real, but not part of the sourced-UGC manifest.
function isFirstParty(slug, isMockup) {
  return isMockup || slug === 'route_map' || /^app[_-]/.test(slug);
}
// every photo-bearing field on a slide -> [slug, field, isMockup]
function photoSlugs(slide) {
  const out = [];
  for (const f of ['scenic_photo', 'top_photo', 'bottom_photo', 'bg_photo', 'photo']) {
    if (slide[f]) out.push([slide[f], f, false]);
  }
  if (slide.mockup) out.push([slide.mockup, 'mockup', true]);
  for (const c of slide.cells || []) out.push([c, 'cells', false]);
  for (const ic of slide.icons || []) if (ic && ic.slug) out.push([ic.slug, 'icons', false]);
  return out;
}

// ---- 1. copy.json ----
const copyPath = path.join(dir, 'copy.json');
let copy = null;
if (!fs.existsSync(copyPath)) {
  issues.push('copy.json missing at post root');
} else {
  try { copy = JSON.parse(fs.readFileSync(copyPath, 'utf8')); ok.push('copy.json parses'); }
  catch (e) { issues.push('copy.json does not parse: ' + e.message); }
}
if (copy) {
  if (framework && copy.option !== framework) {
    issues.push(`copy.option is ${JSON.stringify(copy.option)} but --framework ${framework} was requested`);
  } else if (framework) {
    ok.push(`copy.option matches --framework ${framework}`);
  }
  if (!Array.isArray(copy.slides)) issues.push('copy.json has no slides array');
}

// ---- 2. final/ names + sequence, 3. dimensions ----
const finalDir = path.join(dir, 'final');
if (!fs.existsSync(finalDir)) {
  issues.push('final/ folder missing');
} else {
  const mark = before();
  const entries = fs.readdirSync(finalDir);
  const pngs = [];
  for (const f of entries) {
    if (f.toLowerCase().endsWith('.png')) pngs.push(f);
    else issues.push(`stray non-PNG file in final/: ${f} (deliver clean)`);
  }
  for (const f of pngs) {
    if (!NAME_RE.test(f)) issues.push(`malformed name in final/: ${f} (expected NN_role.png, variant suffix stripped)`);
  }
  const actual = pngs.filter(f => NAME_RE.test(f)).sort();

  if (copy && Array.isArray(copy.slides)) {
    const expected = copy.slides.map((s, i) => `${String(i + 1).padStart(2, '0')}_${ROLE[s.type] || s.type}.png`);
    if (!pngs.includes('01_cover.png')) issues.push('final/01_cover.png missing');
    expected.forEach((e, i) => { if (!actual.includes(e)) issues.push(`final/${e} missing (expected from copy.json slide ${i + 1})`); });
    for (const f of actual) if (!expected.includes(f)) issues.push(`unexpected file in final/: ${f} (not in the copy.json slide sequence)`);
    const nums = actual.map(f => parseInt(f.slice(0, 2), 10));
    for (let i = 0; i < nums.length; i++) {
      if (nums[i] !== i + 1) { issues.push(`final/ numbering not contiguous from 01 (positions present: ${nums.join(', ') || 'none'})`); break; }
    }
    cleanSince(mark, `final/ has ${actual.length} PNG(s) matching the ${copy.option || '?'} slide sequence`);
  }

  // dimensions — every PNG, regardless of name validity
  const dmark = before();
  for (const f of pngs) {
    const s = pngSize(path.join(finalDir, f));
    if (!s) issues.push(`${f}: not a valid PNG (no IHDR)`);
    else if (s.w !== 1080 || s.h !== 1920) issues.push(`${f}: ${s.w}x${s.h}, expected 1080x1920`);
  }
  cleanSince(dmark, `all ${pngs.length} final/ PNG(s) are 1080x1920`);
}

// ---- 4. caption.txt ----
const captionPath = path.join(dir, 'caption.txt');
if (!fs.existsSync(captionPath)) {
  issues.push('caption.txt missing at post root');
} else {
  const caption = fs.readFileSync(captionPath, 'utf8');
  if (!caption.trim()) issues.push('caption.txt is empty');
  else ok.push('caption.txt present and non-empty');
  if (DASH.test(caption)) issues.push('caption.txt contains an em/en dash (instant AI tell)');
}

// ---- 5. flags.md ----
const flagsPath = path.join(dir, 'flags.md');
if (!fs.existsSync(flagsPath)) issues.push('flags.md missing at post root');
else if (!fs.readFileSync(flagsPath, 'utf8').trim()) issues.push('flags.md is empty');
else ok.push('flags.md present and non-empty');

// ---- 6. photo slugs resolve + attributed ----
let manifest = [];
if (fs.existsSync(MANIFEST)) { try { manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8')); } catch { manifest = []; } }
if (!Array.isArray(manifest)) manifest = [];
const manIds = new Set(manifest.map(e => e && e.id).filter(Boolean));
const manBase = new Set(manifest.map(e => e && e.local_path && path.basename(e.local_path).replace(/\.[^.]+$/, '')).filter(Boolean));
const inManifest = slug => manIds.has(slug) || manBase.has(slug);

if (copy && Array.isArray(copy.slides)) {
  const mark = before();
  copy.slides.forEach((slide, idx) => {
    const n = idx + 1;
    if (slide.char_photo && !resolvesIn(CHARS, slide.char_photo)) {
      issues.push(`slide ${n} char_photo "${slide.char_photo}" not found in chars/`);
    }
    for (const [slug, field, isMockup] of photoSlugs(slide)) {
      const inGraded = resolvesIn(GRADED, slug);
      const inBrand = resolvesIn(BRAND, slug);
      if (isMockup) {
        if (!inGraded && !inBrand) issues.push(`slide ${n} ${field} "${slug}" not found in media/graded/ or media/brand/`);
      } else if (!inGraded && !inBrand) {
        issues.push(`slide ${n} ${field} "${slug}" not found in media/graded/`);
      }
      if (!isFirstParty(slug, isMockup) && !inManifest(slug)) {
        issues.push(`slide ${n} ${field} "${slug}" has no attribution row in media/manifest.json`);
      }
    }
  });
  cleanSince(mark, 'every photo slug resolves and is attributed (or first-party exempt)');
}

// ---- 7. WARN-only: _work/render/ human+nohuman cover+save ----
const workRender = path.join(dir, '_work', 'render');
if (fs.existsSync(workRender)) {
  const rf = fs.readdirSync(workRender);
  const has = (role, variant) => rf.some(f => f.includes(role) && f.includes(variant));
  if (has('cover', '_human') && has('cover', '_nohuman') && has('save', '_human') && has('save', '_nohuman')) {
    ok.push('_work/render/ retains both _human and _nohuman cover+save renders');
  } else {
    warn.push('_work/render/ present but missing some _human/_nohuman cover+save renders');
  }
} else {
  warn.push('_work/render/ not retained (human/nohuman cover+save renders not kept for review)');
}

// ---- output ----
const uniq = a => [...new Set(a)];
const out = { pass: issues.length === 0, ok: uniq(ok), warn: uniq(warn), issues: uniq(issues) };
console.log(JSON.stringify(out, null, 2));
for (const o of out.ok) console.log('  ok    ' + o);
for (const w of out.warn) console.log('  warn  ' + w);
for (const it of out.issues) console.log('  FAIL  ' + it);
console.log(out.pass ? 'QC PASS' : 'QC FAIL');
process.exit(out.pass ? 0 : 1);
