// Standalone framework slide renderer (SANDBOX — sandbox/frameworks-test only).
//
// Renders the content-framework carousels (Options A / B / C1 / C2) from a per-option
// copy JSON into 1080x1920 PNGs. Playwright HTML->PNG, mirroring engine/design/build.js's
// proven pattern (file:// HTML, Google-Fonts @import + networkidle + small wait, esc(),
// screenshot clip) but self-contained — it imports nothing from engine/ and writes nothing
// outside this sandbox.
//
// Design authority: knowledge/frameworks/content_frameworks.md.  Interface: ./CONTRACT.md.
//
// CLI:
//   node build.js --copy <copy/X.json> --out <dir> [--only NN] [--contact]
//     * reads the copy JSON (schema in CONTRACT.md), renders every slide -> <dir>/NN_<role>.png
//     * cover/save slides render TWICE: _human (char_photo) and _nohuman (scenic_photo)
//     * --only NN   renders just the slide at deck position NN (e.g. --only 02)
//     * --contact   also writes <dir>/_contact.png — a labelled grid montage of the deck
//
// Playwright is not installed at repo root; require it from the engine by absolute path.
const PLAYWRIGHT = '/Users/daven/Documents/Holicay Workflows/Project Ana/engine/node_modules/playwright';
const { chromium } = require(PLAYWRIGHT);
const fs = require('fs');
const path = require('path');

const ROOT   = __dirname;                       // sandbox/frameworks-test
const GRADED = path.join(ROOT, 'media', 'graded');
const CHARS  = path.join(ROOT, 'chars');
const W = 1080, H = 1920;

// ---- shared helpers (esc lifted from engine/design/build.js) ----
function fileUrl(p) { return 'file://' + encodeURI(p); }
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function toLines(x) { return Array.isArray(x) ? x : (x == null ? [] : [x]); }

// slug -> media/graded/<slug>.(jpg|png|jpeg) ; char name -> chars/<name>(.png|.jpg)
function resolveIn(dir, name, exts) {
  if (/\.(jpg|jpeg|png)$/i.test(name)) return path.join(dir, name);
  for (const e of exts) { const p = path.join(dir, name + '.' + e); if (fs.existsSync(p)) return p; }
  return path.join(dir, name + '.' + exts[0]);
}
function photo(slug) { return fileUrl(resolveIn(GRADED, slug, ['jpg', 'png', 'jpeg'])); }
function charPhoto(name) { return fileUrl(resolveIn(CHARS, name, ['png', 'jpg', 'jpeg'])); }

// ---- type system ----
const MONT_IMPORT   = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800;900&display=swap';
const NUNITO_IMPORT = 'https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&family=Poppins:wght@700;800;900&display=swap';
// TikTok Sans (TikTok's real typeface, SIL OFL, via Google Fonts) is bundled locally in
// assets/fonts/ so renders don't depend on the network; Montserrat stays as the online fallback.
const TTS_FACES = fs.readFileSync(path.join(__dirname, 'assets', 'fonts', 'tiktok-sans.css'), 'utf8');
const TIKTOK = "'TikTok Sans','Montserrat','Apple Color Emoji',-apple-system,Arial,sans-serif";
const NUNITO = "'Nunito','Poppins','Apple Color Emoji',-apple-system,Arial,sans-serif";
// A / B / C1 = bold TikTok Sans (the actual TikTok face; Montserrat was its stand-in) ;
// C2 = rounded bold Nunito (Poppins fallback) per the doc's C2 design block
function fontFor(option) {
  return option === 'C2'
    ? { fam: NUNITO, head: `@import url('${NUNITO_IMPORT}');` }
    : { fam: TIKTOK, head: `@import url('${MONT_IMPORT}');\n${TTS_FACES}` };
}

// ---- the CORE COMPONENT: the fused paragraph "sticker" (v3 — MEASURED OUTLINE PATH) ----
// One PARAGRAPH = ONE connected white shape, drawn TikTok's own way. Each line still hugs
// its own width; the lines stack flush; and a single crisp SVG <path> is drawn around the
// whole stack. Mechanism (in-page, after fonts load — see STICKER_SCRIPT): measure every
// rendered line's box (hugged width incl. padding, its top/height), build the rectilinear
// silhouette of the stack, then round every corner — CONVEX outer corners at radius R, small
// CONCAVE quarter-arc fillets at radius F where a shorter line meets a longer one (both capped
// so tiny steps stay smooth), dead-flat straight edges everywhere else. Pure-white fill, NO
// filter / NO blur / NO gray fringe — razor-sharp antialiased edges only. The SVG sits behind
// a pixel-crisp text layer; the filter never touches glyphs. `stickerOf` only emits the two
// layers + an empty <svg> placeholder — all shape geometry is computed at render time.
const STK_R = 15;         // convex outer-corner radius (px)
const STK_F = 12;         // concave step-fillet radius (px)
const MAXW  = W - 120;    // 960px — auto-fit cap: no rendered line may be wider than this
const VPAD  = 40;         // frame-edge safe margin used by the vertical auto-fit guard

// items: [{t, size, weight}] = the lines of ONE paragraph (uniform size in practice, but
// per-line sizing is supported). Returns the sticker: an empty <svg> the in-page script fills
// with the measured outline, behind a crisp black-glyph text layer. `gap` is the inter-line
// margin (slightly negative pulls neighbours snug; flush fusion is guaranteed by the path,
// which snaps every line boundary to the midpoint of the two boxes so there are no seams).
function stickerOf(items, opts = {}) {
  const { px = 28, py = 10, gap = -3, lh = 1.12, cls = '' } = opts;
  const vars = `--px:${px}px;--py:${py}px;--g:${gap}px;--lh:${lh}`;
  const rows = items.map(it =>
    `<div class="sln" style="font-size:${it.size}px;font-weight:${it.weight}">${esc(it.t)}</div>`).join('');
  return `<div class="stk ${cls}" style="${vars}">`
       + `<svg class="stk-bg" preserveAspectRatio="none" aria-hidden="true"></svg>`
       + `<div class="stk-txt">${rows}</div></div>`;
}
// convenience: one paragraph, uniform size/weight
function sticker(lines, size, weight, opts = {}) {
  return stickerOf(toLines(lines).map(t => ({ t, size, weight })), opts);
}

// ---- in-page sticker builder — injected into every emitted doc, runs after document.fonts.ready.
// It (1) AUTO-FITS each sticker: if any line is wider than MAXW, or the cluster is taller than the
// safe frame band, it scales THAT sticker's font down uniformly (never re-wraps); then (2) MEASURES
// the (possibly rescaled) lines and injects one razor-sharp outline <path> per sticker. When done it
// sets <html data-stickers-done> so the screenshot driver knows measurement + injection has settled.
const STICKER_SCRIPT = `<script>
(function(){
  var R=${STK_R}, F=${STK_F}, MAXW=${MAXW}, VPAD=${VPAD}, FRAMEH=${H};
  function lens(stk){
    var slns=stk.querySelectorAll('.stk-txt .sln'), sb=stk.getBoundingClientRect(), a=[];
    for(var i=0;i<slns.length;i++){
      var r=slns[i].getBoundingClientRect();
      a.push({L:r.left-sb.left, R:r.right-sb.left, T:r.top-sb.top, B:r.bottom-sb.top, w:r.width});
    }
    return {lines:a, box:sb};
  }
  function fit(stk){
    var m=lens(stk); if(!m.lines.length) return;
    var slns=stk.querySelectorAll('.stk-txt .sln');
    // the side padding (--px) is fixed & uniform across lines, so scale only the TEXT part:
    // solving textW*s + padX <= MAXW keeps the whole white box inside the safe band (not just
    // the glyphs), so a scaled sticker never creeps past the frame margin the way font*=MAXW/boxW would.
    var cs=getComputedStyle(slns[0]), padX=parseFloat(cs.paddingLeft)+parseFloat(cs.paddingRight);
    var maxW=0; for(var i=0;i<m.lines.length;i++){ if(m.lines[i].w>maxW) maxW=m.lines[i].w; }
    var s=1;
    if(maxW>MAXW){ var tw=maxW-padX; if(tw>0) s=Math.min(s, (MAXW-padX)/tw); }
    var availH=FRAMEH-2*VPAD;
    if(m.box.height>availH) s=Math.min(s, availH/m.box.height);
    if(s<1){
      for(var j=0;j<slns.length;j++){
        var fs=parseFloat(getComputedStyle(slns[j]).fontSize);
        slns[j].style.fontSize=(fs*s)+'px';
      }
    }
  }
  function dedupe(v){
    var out=[], n=v.length;
    for(var i=0;i<n;i++){
      var p=v[i];
      if(out.length){ var q=out[out.length-1]; if(Math.abs(p[0]-q[0])<0.02 && Math.abs(p[1]-q[1])<0.02) continue; }
      out.push(p);
    }
    if(out.length>1){ var a=out[0], b=out[out.length-1]; if(Math.abs(a[0]-b[0])<0.02 && Math.abs(a[1]-b[1])<0.02) out.pop(); }
    var res=[], m=out.length;
    for(var i=0;i<m;i++){
      var pr=out[(i-1+m)%m], cu=out[i], nx=out[(i+1)%m];
      var ix=cu[0]-pr[0], iy=cu[1]-pr[1], ox=nx[0]-cu[0], oy=nx[1]-cu[1];
      if(Math.abs(ix*oy-iy*ox)<0.02 && (ix*ox+iy*oy)>0) continue; // collinear pass-through
      res.push(cu);
    }
    return res;
  }
  function ring(lines){
    var n=lines.length, tops=[], bots=[], Ls=[], Rs=[];
    for(var i=0;i<n;i++){ tops[i]=lines[i].T; bots[i]=lines[i].B; Ls[i]=lines[i].L; Rs[i]=lines[i].R; }
    for(var i=0;i<n-1;i++){ var mid=(bots[i]+tops[i+1])/2; bots[i]=mid; tops[i+1]=mid; } // flush seams
    var v=[];
    v.push([Ls[0],tops[0]]); v.push([Rs[0],tops[0]]);               // top edge (line 0)
    for(var i=0;i<n;i++){ v.push([Rs[i],bots[i]]); if(i<n-1) v.push([Rs[i+1],bots[i]]); } // right, stepping
    v.push([Ls[n-1],bots[n-1]]);                                    // bottom edge (last line)
    for(var i=n-1;i>=1;i--){ v.push([Ls[i],tops[i]]); v.push([Ls[i-1],tops[i]]); }        // left, stepping up
    return dedupe(v);
  }
  function pathFor(lines){
    var v=ring(lines), m=v.length; if(m<3) return '';
    var A=[], B=[], SW=[], Rr=[];
    for(var i=0;i<m;i++){
      var pr=v[(i-1+m)%m], cu=v[i], nx=v[(i+1)%m];
      var ix=cu[0]-pr[0], iy=cu[1]-pr[1], ox=nx[0]-cu[0], oy=nx[1]-cu[1];
      var iL=Math.sqrt(ix*ix+iy*iy), oL=Math.sqrt(ox*ox+oy*oy);
      var cross=ix*oy-iy*ox;                     // >0 convex, <0 concave (clockwise ring, y-down)
      var r=Math.min(cross>0?R:F, iL/2, oL/2);   // cap so neighbouring arcs never overlap
      Rr[i]=r; SW[i]=cross>0?1:0;
      var iux=iL>0?ix/iL:0, iuy=iL>0?iy/iL:0, oux=oL>0?ox/oL:0, ouy=oL>0?oy/oL:0;
      A[i]=[cu[0]-iux*r, cu[1]-iuy*r];           // enter corner r before the vertex
      B[i]=[cu[0]+oux*r, cu[1]+ouy*r];           // leave corner r after the vertex
    }
    var d='M '+A[0][0].toFixed(2)+' '+A[0][1].toFixed(2);
    for(var i=0;i<m;i++){
      d+=' A '+Rr[i].toFixed(2)+' '+Rr[i].toFixed(2)+' 0 0 '+SW[i]+' '+B[i][0].toFixed(2)+' '+B[i][1].toFixed(2);
      var ni=(i+1)%m;
      d+=' L '+A[ni][0].toFixed(2)+' '+A[ni][1].toFixed(2);
    }
    return d+' Z';
  }
  function draw(stk){
    var m=lens(stk); if(!m.lines.length) return;
    var w=m.box.width, h=m.box.height, svg=stk.querySelector('.stk-bg'); if(!svg) return;
    svg.setAttribute('width', w); svg.setAttribute('height', h);
    svg.setAttribute('viewBox', '0 0 '+w+' '+h);
    svg.innerHTML='<path d="'+pathFor(m.lines)+'" fill="#ffffff"/>';
  }
  function run(){
    var stks=document.querySelectorAll('.stk');
    for(var i=0;i<stks.length;i++) fit(stks[i]);   // pass 1: scale down any overflowing sticker
    for(var i=0;i<stks.length;i++) draw(stks[i]);  // pass 2: measure (post-scale) + inject path
    document.documentElement.setAttribute('data-stickers-done','1');
  }
  if(document.fonts && document.fonts.ready){ document.fonts.ready.then(run); } else { run(); }
})();
</script>`;

// ---- OUTLINE TEXT (the dial) — NO box. White fill + a thin OUTER black stroke + soft
// shadow. Layered duplicate: a black -webkit-text-stroke copy underneath, a clean white
// fill copy on top; the fill covers the stroke's inner half so the stroke reads only
// OUTSIDE the glyphs (a centre stroke that eats the letterforms is not acceptable).
function outlineText(lines, size, weight, opts = {}) {
  const { stroke = 6, gap = 8, lh = 1.14, cls = '' } = opts;
  const rows = toLines(lines).map(t => {
    const e = esc(t);
    return `<div class="oln" style="font-size:${size}px;font-weight:${weight};line-height:${lh};margin-bottom:${gap}px">`
         + `<span class="ol-s" style="-webkit-text-stroke:${stroke}px #000">${e}</span>`
         + `<span class="ol-f">${e}</span></div>`;
  }).join('');
  return `<div class="otl ${cls}">${rows}</div>`;
}

// ---- shared component CSS (injected into every doc) ----
const STICKER_CSS = `
.stk{position:relative;display:flex;flex-direction:column;align-items:center}
.stk-bg{position:absolute;left:0;top:0;width:100%;height:100%;z-index:1;overflow:visible;pointer-events:none}
.stk-txt{position:relative;z-index:2;display:flex;flex-direction:column;align-items:center}
.sln{display:inline-block;padding:var(--py) var(--px);line-height:var(--lh);
  white-space:nowrap;margin-bottom:var(--g);color:#141414}
.sln:last-child{margin-bottom:0}`;
const OUTLINE_CSS = `
.otl{display:flex;flex-direction:column;align-items:center;text-align:center}
.oln{position:relative;display:inline-block;white-space:nowrap}
.oln:last-child{margin-bottom:0 !important}
.ol-s,.ol-f{white-space:nowrap}
.ol-s{position:absolute;left:0;top:0;color:#000;
  text-shadow:0 4px 13px rgba(0,0,0,.5),0 2px 5px rgba(0,0,0,.45)}
.ol-f{position:relative;color:#fff}`;

// ---- document skeleton ----
function doc({ font, frameBg, css, body }) {
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>
${font.head}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px}
.frame{position:relative;width:${W}px;height:${H}px;overflow:hidden;
  font-family:${font.fam};-webkit-font-smoothing:antialiased;${frameBg ? `background:${frameBg};` : ''}}
/* photo layers carry the subtle whole-frame grade; text layers never do */
.photo{position:absolute;inset:0;background-size:cover;background-position:center;
  filter:brightness(.92) saturate(.88) contrast(.98)}
${STICKER_CSS}
${OUTLINE_CSS}
${css || ''}
</style></head><body><div class="frame">${body}</div>${STICKER_SCRIPT}</body></html>`;
}

// ================= TEMPLATES =================
// Each returns a full HTML doc for one rendered PNG. `v` is the render variant (human|nohuman|null).
const TEMPLATES = {

  // ---- 2. cover — full-bleed photo, gentle scrim, title stack upper-middle + subtitle just under ----
  cover(slide, option, v) {
    const font = fontFor(option);
    const img = v === 'human' ? charPhoto(slide.char_photo) : photo(slide.scenic_photo);
    // flag = a BARE drop-shadowed emoji (NO box, never inside the sticker layers) peeking
    // half-above the title sticker's top-left corner — kylie.nbt cover geometry. Cover only.
    const flag = slide.flag ? `<span class="flag">${esc(slide.flag)}</span>` : '';
    const title = sticker(slide.title_lines, 68, 800);
    const sub = slide.subtitle_lines && slide.subtitle_lines.length
      ? `<div class="cover-sub">${slide.subtitle_style === 'outline'
          ? outlineText(slide.subtitle_lines, 40, 700)
          : sticker(slide.subtitle_lines, 40, 700)}</div>` : '';
    const css = `
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.20),rgba(0,0,0,0) 24%,rgba(0,0,0,0) 68%,rgba(0,0,0,.24))}
.cover-block{position:absolute;left:60px;right:60px;top:470px;display:flex;flex-direction:column;align-items:center}
.titlewrap{position:relative}
.flag{position:absolute;top:-46px;left:22px;z-index:5;font-size:70px;line-height:1;
  filter:drop-shadow(0 3px 6px rgba(0,0,0,.38))}
.cover-sub{margin-top:30px}`;
    const body = `<div class="photo" style="background-image:url('${img}')"></div>
<div class="scrim"></div>
<div class="cover-block">
  <div class="titlewrap">${flag}${title}</div>
  ${sub}
</div>`;
    return doc({ font, css, body });
  },

  // ---- 5. save — like cover but dead-center vertical middle ----
  save(slide, option, v) {
    const font = fontFor(option);
    const img = v === 'human' ? charPhoto(slide.char_photo) : photo(slide.scenic_photo);
    const title = slide.title_style === 'outline'
      ? outlineText(toLines(slide.title || 'SAVE THIS'), 84, 900)
      : sticker(toLines(slide.title || 'SAVE THIS'), 84, 900);
    const sub = slide.subtitle
      ? `<div class="save-sub">${sticker(toLines(slide.subtitle), 42, 700)}</div>` : '';
    const css = `
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.24),rgba(0,0,0,.10) 34%,rgba(0,0,0,.10) 66%,rgba(0,0,0,.28))}
.save-block{position:absolute;left:60px;right:60px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;align-items:center}
.save-sub{margin-top:26px}`;
    const body = `<div class="photo" style="background-image:url('${img}')"></div>
<div class="scrim"></div>
<div class="save-block">${title}${sub}</div>`;
    return doc({ font, css, body });
  },

  // ---- 3. split — A/B body. Top half = ❌ photo, bottom half = ✅ photo. Cluster on the seam. ----
  split(slide, option) {
    const font = fontFor(option);
    const top = photo(slide.top_photo), bot = photo(slide.bottom_photo);
    // four separate fused stickers (❌ title / ❌ why / ✅ title / ✅ why), clustered on the seam
    const groups = [
      [slide.x_title_lines, 58, 800], [slide.x_why_lines, 46, 700],
      [slide.check_title_lines, 58, 800], [slide.check_why_lines, 46, 700],
    ];
    const stk = groups.filter(g => toLines(g[0]).length)
      .map(([l, s, w]) => sticker(l, s, w)).join('');
    const css = `
.split{position:absolute;inset:0}
.half{position:absolute;left:0;right:0;height:960px;background-size:cover;background-position:center;
  filter:brightness(.90) saturate(.88) contrast(.98)}
.half.top{top:0}
.half.bottom{top:960px}
/* seam-local scrim so the white boxes pop over both photos */
.seam{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);height:640px;
  background:radial-gradient(120% 62% at 50% 50%,rgba(0,0,0,.40),rgba(0,0,0,.12) 58%,rgba(0,0,0,0))}
.split-cluster{position:absolute;left:50px;right:50px;top:50%;transform:translateY(-50%);
  display:flex;flex-direction:column;align-items:center;gap:22px}`;
    const body = `<div class="split">
  <div class="half top" style="background-image:url('${top}')"></div>
  <div class="half bottom" style="background-image:url('${bot}')"></div>
</div>
<div class="seam"></div>
<div class="split-cluster">${stk}</div>`;
    return doc({ font, css, body });
  },

  // ---- 4. plug — two treatments (human steer 2026-07-23):
  //   * slide.mockup   (C1): the Holicay app shown as a framed phone on brand coral — the ✅ SOLUTION.
  //   * slide.bg_photo (A/B/C2): a full-bleed picturesque country scenic + scrim — the plug copy's
  //                    ❌ problem / ✅ HOLICAY.COM fix rides on top. (was: flat #f2f2f2 placeholder.)
  plug(slide, option) {
    const font = fontFor(option);

    // C1 — framed phone mockup of the Holicay app on a DARK-TINTED picturesque country scenic
    // (human steer 2026-07-23: bigger phone, text pulled in toward it, scenic+tint for hierarchy).
    if (slide.mockup) {
      const shot = photo(slide.mockup);
      const paras = slide.paragraphs || [];
      const top = paras[0] ? sticker(paras[0], 46, 700) : '';
      const bot = paras[1] ? sticker(paras[1], 46, 700) : '';
      const bgLayer = slide.bg_photo
        ? `<div class="photo" style="background-image:url('${photo(slide.bg_photo)}')"></div><div class="plug-tint"></div>`
        : `<div class="plug-bg"></div>`;                 // coral fallback if no scenic given
      const css = `
.plug-bg{position:absolute;inset:0;background:linear-gradient(158deg,#F5836A 0%,#E8604E 52%,#CE4433 100%)}
/* dark tint over the scenic so the white phone + text sit on top with clear hierarchy */
.plug-tint{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.62),rgba(0,0,0,.44) 26%,rgba(0,0,0,.44) 74%,rgba(0,0,0,.64))}
.plug-top{position:absolute;left:56px;right:56px;top:208px;display:flex;justify-content:center}
.phone{position:absolute;left:50%;top:484px;transform:translateX(-50%);height:1010px;width:auto;
  border-radius:44px;border:9px solid #fff;box-shadow:0 24px 66px rgba(0,0,0,.5)}
.plug-bot{position:absolute;left:56px;right:56px;top:1538px;display:flex;justify-content:center}`;
      const body = `${bgLayer}
<div class="plug-top">${top}</div>
<img class="phone" src="${shot}">
<div class="plug-bot">${bot}</div>`;
      return doc({ font, css, body });
    }

    // A / B / C2 — full-bleed picturesque country scenic behind the plug sticker cluster
    if (slide.bg_photo) {
      const img = photo(slide.bg_photo);
      const paras = (slide.paragraphs || []).map(
        p => `<div class="para">${sticker(p, 46, 700)}</div>`).join('');
      const css = `
.pscrim{position:absolute;inset:0;background:
  linear-gradient(180deg,rgba(8,10,14,.46),rgba(8,10,14,.30) 50%,rgba(8,10,14,.5)),
  radial-gradient(86% 50% at 50% 50%,rgba(0,0,0,.5),rgba(0,0,0,.14) 72%,rgba(0,0,0,0))}
.plug-block{position:absolute;left:70px;right:70px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;align-items:center}
.para{margin-bottom:34px}
.para:last-child{margin-bottom:0}`;
      const body = `<div class="photo" style="background-image:url('${img}')"></div>
<div class="pscrim"></div>
<div class="plug-block">${paras}</div>`;
      return doc({ font, css, body });
    }

    // fallback — flat placeholder (nothing uses this now, kept as a safety net)
    const paras = (slide.paragraphs || []).map(
      p => `<div class="para">${sticker(p, 46, 700)}</div>`).join('');
    const css = `
.plug-block{position:absolute;left:70px;right:70px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;align-items:center}
.para{margin-bottom:34px}
.para:last-child{margin-bottom:0}`;
    const body = `<div class="plug-block">${paras}</div>`;
    return doc({ font, frameBg: '#f2f2f2', css, body });
  },

  // ---- 6. divider (C1) — 2x2 collage, soft center wash, lowercase white name on the seam ----
  divider(slide, option) {
    const font = fontFor(option);           // C1 = Montserrat
    const c = (slide.cells || []).map(photo);
    const css = `
.grid2{position:absolute;inset:0;display:grid;grid-template-columns:540px 540px;grid-template-rows:960px 960px}
.cell{background-size:cover;background-position:center;filter:brightness(.90) saturate(.86) contrast(.98)}
.wash{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);height:360px;
  background:radial-gradient(58% 100% at 50% 50%,rgba(0,0,0,.46),rgba(0,0,0,.18) 55%,rgba(0,0,0,0))}
.dlabel{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;
  font-weight:800;font-size:108px;letter-spacing:1px;color:#fff;text-transform:lowercase;
  text-shadow:0 3px 9px rgba(0,0,0,.6),0 5px 30px rgba(0,0,0,.5)}`;
    const body = `<div class="grid2">
  <div class="cell" style="background-image:url('${c[0]}')"></div>
  <div class="cell" style="background-image:url('${c[1]}')"></div>
  <div class="cell" style="background-image:url('${c[2]}')"></div>
  <div class="cell" style="background-image:url('${c[3]}')"></div>
</div>
<div class="wash"></div>
<div class="dlabel">${esc(slide.label)}</div>`;
    return doc({ font, css, body });
  },

  // ---- 7. notes (C1) — iPhone-Notes look but set entirely in Montserrat ----
  notes(slide, option) {
    const font = fontFor(option);           // C1 = Montserrat (doc: NOT literal SF Pro)
    const secs = (slide.sections || []).map(sec => {
      const header = esc(sec.header) + (slide.contd ? ' (contd)' : '');
      const items = (sec.items || []).map(it => {
        const bullet = it.emoji
          ? `<span class="bemoji">${esc(it.emoji)}</span>`
          : `<span class="bcircle"></span>`;
        const gloss = it.gloss ? ` <span class="gloss">(${esc(it.gloss)})</span>` : '';
        return `<div class="item">${bullet}<span class="itx">${esc(it.text)}${gloss}</span></div>`;
      }).join('');
      return `<div class="sec"><div class="sechd">${esc(sec.emoji)} ${header}</div>${items}</div>`;
    }).join('');
    const css = `
.page{position:absolute;inset:0;background:#fbfbf9}
.band{position:absolute;left:0;right:0;top:0;height:112px;background:#f2f2ee}
.nwrap{position:absolute;left:84px;right:84px;top:50%;transform:translateY(-50%)}
.sec{margin-bottom:46px}
.sec:last-child{margin-bottom:0}
.sechd{font-size:54px;font-weight:800;color:#20201e;letter-spacing:.2px;margin-bottom:16px}
.item{display:flex;align-items:flex-start;gap:20px;font-size:42px;line-height:1.30;
  font-weight:600;color:#33322f;padding:7px 0}
.bcircle{flex:0 0 auto;width:30px;height:30px;margin-top:11px;border:3px solid #c3c2bc;border-radius:50%}
.bemoji{flex:0 0 auto;font-size:38px;line-height:1.2}
.itx{flex:1}
.gloss{color:#9a988f;font-weight:600}`;
    const body = `<div class="page"></div><div class="band"></div><div class="nwrap">${secs}</div>`;
    return doc({ font, css, body });
  },

  // ---- 8. step (C2) — black pill top-center + white-box blocks, four layouts ----
  step(slide, option) {
    const font = fontFor(option);           // C2 = Nunito
    const layout = slide.layout || 'photo';
    const SIZE = { headline: 58, body: 52, tip: 44 }, WT = { headline: 800, body: 800, tip: 700 };

    const pillTop = layout === 'grid4' ? 60 : 240;
    const pill = `<div class="pill" style="top:${pillTop}px"><span>${esc(slide.pill)}</span></div>`;

    let scrim, layers;
    if (layout === 'grid4') {
      const c = (slide.cells || []).map(photo);
      const labels = slide.cell_labels || [];
      // top-row groups sit ~lower-third of the top cells; bottom-row groups ~lower-third of bottom cells
      const pos = [
        { left: 0,   top: 640 }, { left: 540, top: 640 },
        { left: 0,   top: 1500 }, { left: 540, top: 1500 },
      ];
      const cellText = labels.map((lb, i) => {
        const label = sticker(lb.title_lines, 44, 800);
        const note = lb.note_lines && lb.note_lines.length
          ? `<div style="margin-top:9px">${sticker(lb.note_lines, 34, 700)}</div>` : '';
        return `<div class="cg" style="left:${pos[i].left}px;top:${pos[i].top}px">${label}${note}</div>`;
      }).join('');
      const sub = slide.blocks && slide.blocks.length
        ? `<div class="grid-sub">${sticker(slide.blocks[0].lines, 44, 800)}</div>` : '';
      const css = `
.grid2{position:absolute;inset:0;display:grid;grid-template-columns:540px 540px;grid-template-rows:960px 960px}
.cell{background-size:cover;background-position:center;filter:brightness(.90) saturate(.88) contrast(.98)}
.pill{position:absolute;left:0;right:0;text-align:center}
.pill span{display:inline-block;background:#141414;color:#fff;border-radius:34px;padding:14px 40px;
  font-size:52px;font-weight:800;box-shadow:0 4px 14px rgba(0,0,0,.35)}
.grid-sub{position:absolute;left:60px;right:60px;top:196px}
.cg{position:absolute;width:540px;display:flex;flex-direction:column;align-items:center;transform:translateY(-50%)}`;
      const body = `<div class="grid2">
  <div class="cell" style="background-image:url('${c[0]}')"></div>
  <div class="cell" style="background-image:url('${c[1]}')"></div>
  <div class="cell" style="background-image:url('${c[2]}')"></div>
  <div class="cell" style="background-image:url('${c[3]}')"></div>
</div>${pill}${sub}${cellText}`;
      return doc({ font, css, body });
    }

    if (layout === 'icons') {
      const img = photo(slide.photo);
      const icons = (slide.icons || []).map(ic =>
        `<div class="app"><img src="${photo(ic.slug)}"><div class="nm">${esc(ic.name)}</div></div>`).join('');
      const above = (slide.blocks || []).filter(b => b.size !== 'tip')
        .map(b => sticker(b.lines, SIZE[b.size || 'body'], WT[b.size || 'body'])).join('<div style="height:14px"></div>');
      const below = (slide.blocks || []).filter(b => b.size === 'tip')
        .map(b => sticker(b.lines, SIZE.tip, WT.tip)).join('<div style="height:14px"></div>');
      const css = `
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.42),rgba(0,0,0,.12) 26%,rgba(0,0,0,.12) 66%,rgba(0,0,0,.34))}
.pill{position:absolute;left:0;right:0;text-align:center}
.pill span{display:inline-block;background:#141414;color:#fff;border-radius:34px;padding:14px 40px;
  font-size:50px;font-weight:800;box-shadow:0 4px 14px rgba(0,0,0,.35)}
.s-above{position:absolute;left:60px;right:60px;top:34%;transform:translateY(-50%)}
.frost{position:absolute;left:50%;top:56%;transform:translate(-50%,-50%);display:flex;gap:64px;
  background:rgba(255,255,255,.26);backdrop-filter:blur(22px) saturate(1.2);-webkit-backdrop-filter:blur(22px) saturate(1.2);
  border:1px solid rgba(255,255,255,.5);border-radius:40px;padding:44px 60px;box-shadow:0 10px 40px rgba(0,0,0,.3)}
.app{display:flex;flex-direction:column;align-items:center;gap:18px}
.app img{width:158px;height:158px;border-radius:36px;object-fit:cover;box-shadow:0 5px 16px rgba(0,0,0,.34)}
.app .nm{color:#fff;font-weight:800;font-size:34px;text-shadow:0 2px 7px rgba(0,0,0,.55)}
.s-below{position:absolute;left:60px;right:60px;top:78%;transform:translateY(-50%)}`;
      const body = `<div class="photo" style="background-image:url('${img}')"></div>
<div class="scrim"></div>${pill}
<div class="s-above">${above}</div>
<div class="frost">${icons}</div>
<div class="s-below">${below}</div>`;
      return doc({ font, css, body });
    }

    // layout === 'photo' || 'map'  (map backdrop is just a map-screenshot slug)
    const img = photo(slide.photo);
    const mid = (slide.blocks || []).filter(b => b.size !== 'tip')
      .map(b => sticker(b.lines, SIZE[b.size || 'body'], WT[b.size || 'body'])).join('<div style="height:16px"></div>');
    const tip = (slide.blocks || []).filter(b => b.size === 'tip')
      .map(b => sticker(b.lines, SIZE.tip, WT.tip)).join('<div style="height:16px"></div>');
    scrim = `<div class="scrim"></div>`;
    const css = `
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.40),rgba(0,0,0,.10) 24%,rgba(0,0,0,.10) 62%,rgba(0,0,0,.34))}
.pill{position:absolute;left:0;right:0;text-align:center}
.pill span{display:inline-block;background:#141414;color:#fff;border-radius:34px;padding:14px 40px;
  font-size:50px;font-weight:800;box-shadow:0 4px 14px rgba(0,0,0,.35)}
.s-mid{position:absolute;left:56px;right:56px;top:44%;transform:translateY(-50%)}
.s-tip{position:absolute;left:80px;right:80px;top:76%;transform:translateY(-50%)}`;
    layers = `<div class="photo" style="background-image:url('${img}')"></div>${scrim}${pill}
<div class="s-mid">${mid}</div>
${tip ? `<div class="s-tip">${tip}</div>` : ''}`;
    return doc({ font, css, body: layers });
  },

  // ---- 9. favorites (C2) — scenic photo, title stack upper-middle, 4-6 city rows in two columns ----
  favorites(slide, option) {
    const font = fontFor(option);           // C2 = Nunito
    const img = photo(slide.photo);
    const title = sticker(slide.title_lines, 52, 800);
    const cities = slide.cities || [];
    const cityHtml = c => {
      const spots = sticker(c.lines, 40, 800);
      return `<div class="city"><div class="cpill"><span>${esc(c.pill)}</span></div>${spots}</div>`;
    };
    const left = cities.filter((_, i) => i % 2 === 0).map(cityHtml).join('');
    const right = cities.filter((_, i) => i % 2 === 1).map(cityHtml).join('');
    const css = `
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.34),rgba(0,0,0,.10) 20%,rgba(0,0,0,.12) 70%,rgba(0,0,0,.30))}
.fav-title{position:absolute;left:60px;right:60px;top:150px}
.cols{position:absolute;left:40px;right:40px;top:430px;display:flex;gap:20px;align-items:flex-start}
.col{flex:1;display:flex;flex-direction:column;align-items:center}
.col.r{margin-top:70px}
.city{display:flex;flex-direction:column;align-items:center;margin-bottom:30px}
.city:last-child{margin-bottom:0}
.cpill{margin-bottom:9px}
.cpill span{display:inline-block;background:#141414;color:#fff;border-radius:26px;padding:8px 28px;
  font-size:40px;font-weight:800;box-shadow:0 3px 11px rgba(0,0,0,.34)}`;
    const body = `<div class="photo" style="background-image:url('${img}')"></div>
<div class="scrim"></div>
<div class="fav-title">${title}</div>
<div class="cols">
  <div class="col l">${left}</div>
  <div class="col r">${right}</div>
</div>`;
    return doc({ font, css, body });
  },
};

// ---- role naming (NN_<role>.png) ----
const ROLE = { cover: 'cover', split: 'body', plug: 'plug', save: 'save',
               divider: 'divider', notes: 'notes', step: 'step', favorites: 'favorites' };
const TWO_VARIANT = new Set(['cover', 'save']);   // render _human + _nohuman

// A render job = one output PNG.
function jobsForSlide(slide, idx) {
  const nn = String(idx + 1).padStart(2, '0');
  const role = ROLE[slide.type] || slide.type;
  if (TWO_VARIANT.has(slide.type)) {
    return [
      { nn, name: `${nn}_${role}_human`,   slide, variant: 'human' },
      { nn, name: `${nn}_${role}_nohuman`, slide, variant: 'nohuman' },
    ];
  }
  return [{ nn, name: `${nn}_${role}`, slide, variant: null }];
}

function parseArgs(argv) {
  const a = { copy: null, out: null, only: null, contact: false };
  for (let i = 2; i < argv.length; i++) {
    const x = argv[i];
    if (x === '--copy' || x === '-c') a.copy = argv[++i];
    else if (x === '--out' || x === '-o') a.out = argv[++i];
    else if (x === '--only') a.only = argv[++i];
    else if (x === '--contact') a.contact = true;
  }
  return a;
}

async function renderContact(page, outDir, files) {
  const cells = files.map(f => `
    <div class="cell">
      <img src="${fileUrl(path.join(outDir, f))}">
      <div class="cap">${esc(f)}</div>
    </div>`).join('');
  const cols = 4, cw = 244;
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1c1c1e;font-family:-apple-system,'SF Mono',Menlo,monospace;padding:22px}
.grid{display:grid;grid-template-columns:repeat(${cols},${cw}px);gap:20px 18px;justify-content:center}
.cell{width:${cw}px}
.cell img{width:${cw}px;height:${Math.round(cw * H / W)}px;object-fit:cover;border-radius:8px;
  display:block;box-shadow:0 3px 10px rgba(0,0,0,.5)}
.cap{color:#d7d7db;font-size:15px;margin-top:7px;text-align:center;word-break:break-all;line-height:1.25}
</style></head><body><div class="grid">${cells}</div></body></html>`;
  const hp = path.join(outDir, '_contact.html');
  fs.writeFileSync(hp, html);
  await page.setViewportSize({ width: cols * cw + 18 * (cols - 1) + 44, height: 1000 });
  await page.goto(fileUrl(hp), { waitUntil: 'networkidle' });
  await page.waitForTimeout(250);
  const op = path.join(outDir, '_contact.png');
  await page.screenshot({ path: op, fullPage: true });
  fs.unlinkSync(hp);
  console.log('rendered', op);
  return op;
}

if (require.main === module) (async () => {
  const a = parseArgs(process.argv);
  if (!a.copy) { console.error('usage: node build.js --copy <copy/X.json> --out <dir> [--only NN] [--contact]'); process.exit(1); }
  const copy = JSON.parse(fs.readFileSync(a.copy, 'utf8'));
  const option = copy.option || 'A';
  const outDir = path.resolve(a.out || path.join(ROOT, 'out', option));
  fs.mkdirSync(outDir, { recursive: true });
  const htmlDir = path.join(outDir, '_html');
  fs.mkdirSync(htmlDir, { recursive: true });

  let jobs = [];
  (copy.slides || []).forEach((slide, i) => { jobs.push(...jobsForSlide(slide, i)); });
  if (a.only) jobs = jobs.filter(j => j.nn === String(a.only).padStart(2, '0'));
  if (!jobs.length) { console.log('no slides to render'); return; }

  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const written = [];
  for (const j of jobs) {
    const tpl = TEMPLATES[j.slide.type];
    if (!tpl) { console.warn('!! no template for type', j.slide.type); continue; }
    const html = tpl(j.slide, option, j.variant);
    const hp = path.join(htmlDir, j.name + '.html');
    fs.writeFileSync(hp, html);
    await page.goto(fileUrl(hp), { waitUntil: 'networkidle' });
    try { await page.evaluate(() => document.fonts.ready); } catch (e) {}
    // the in-page STICKER_SCRIPT measures lines + injects the outline paths after fonts.ready,
    // then flags <html data-stickers-done>; wait for that so we never capture pre-measurement.
    try {
      await page.waitForFunction(() => document.documentElement.hasAttribute('data-stickers-done'), { timeout: 6000 });
    } catch (e) { console.warn('!! stickers-done wait timed out for', j.name); }
    await page.waitForTimeout(200);
    const op = path.join(outDir, j.name + '.png');
    await page.screenshot({ path: op, clip: { x: 0, y: 0, width: W, height: H } });
    written.push(j.name + '.png');
    console.log('rendered', op);
  }

  if (a.contact && !a.only) {
    // deck order for the montage = the PNGs we just wrote, in job order
    await renderContact(page, outDir, written);
  }
  await browser.close();
  // tidy scratch html
  try { fs.rmSync(htmlDir, { recursive: true, force: true }); } catch (e) {}
})();

module.exports = { TEMPLATES };
