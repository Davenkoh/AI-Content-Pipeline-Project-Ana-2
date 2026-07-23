#!/usr/bin/env python3
"""Grade photos to look like an UNEDITED, slightly low-quality phone snapshot — NOT punchy HDR.
Camera-roll realism: imperfect per-shot exposure + white-balance cast (kills 'too consistent'
lighting across the set), muted-not-punchy color, mild softness, sensor grain + a little chroma
speckle, faint chromatic aberration, and JPEG compression. `strength` scales how dirty it goes
(higher for too-clean studio shots). Reproducible: jitter derived from the slug.

CANONICAL TEMPLATE — copied into each post's _work/scripts/. Canvas is 3:4 (1080x1440).
Replace JOBS per post: slug -> (crop_ax, crop_ay, strength). 0.5 = centered crop anchor.
Usage: python3 grade.py [slug ...]"""
import os, math, sys, hashlib
from PIL import Image, ImageEnhance, ImageChops, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHOSEN = os.path.join(ROOT, "raw", "chosen_candid")
GRADED = os.path.join(ROOT, "graded")
os.makedirs(GRADED, exist_ok=True)
W, H = 1080, 1440                       # 3:4 TikTok carousel

# slug -> (crop_ax, crop_ay, strength). EXAMPLE — replace per post.
JOBS = {
    "01_example": (0.50, 0.50, 0.45),
    "02_example": (0.50, 0.50, 0.50),
}

def jitter(slug):
    h = hashlib.md5(slug.encode()).digest()
    ev  = h[0] / 255.0 - 0.5     # exposure offset
    wbR = h[1] / 255.0 - 0.5     # warm/cool
    wbG = h[2] / 255.0 - 0.5     # green/magenta
    return ev, wbR, wbG

def cover(im, ax, ay):
    w, h = im.size
    s = max(W / w, H / h)
    nw, nh = math.ceil(w * s), math.ceil(h * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - W) * ax); y = int((nh - H) * ay)
    return im.crop((x, y, x + W, y + H))

def clampLUT(mult):
    return [max(0, min(255, int(i * mult))) for i in range(256)]

def chroma_ab(im, shift=1):
    r, g, b = im.split()
    r = ImageChops.offset(r, -shift, 0)
    b = ImageChops.offset(b, shift, 0)
    return Image.merge("RGB", (r, g, b))

def add_grain(im, amount):
    mono = Image.effect_noise((W, H), 22).convert("L")
    lum = Image.merge("RGB", (mono, mono, mono))
    im = Image.blend(im, ImageChops.overlay(im, lum), amount)
    ch = Image.merge("RGB", (Image.effect_noise((W, H), 16).convert("L"),
                             Image.effect_noise((W, H), 16).convert("L"),
                             Image.effect_noise((W, H), 16).convert("L")))
    im = Image.blend(im, ImageChops.overlay(im, ch), amount * 0.22)
    return im

def real_grade(im, slug, strength):
    ev, wbR, wbG = jitter(slug)
    # 1) imperfect exposure (some shots a touch dark / bright, never auto-perfect)
    im = ImageEnhance.Brightness(im).enhance(1.0 + ev * 0.12 * (0.5 + strength))
    # 2) imperfect white balance — a slight cast, different per shot
    warm = wbR * 0.05 * strength
    grn = wbG * 0.04 * strength
    r, g, b = im.split()
    im = Image.merge("RGB", (r.point(clampLUT(1 + warm)), g.point(clampLUT(1 + grn)), b.point(clampLUT(1 - warm))))
    # 3) pull BACK the pop — unedited is flatter, not HDR-punchy
    im = ImageEnhance.Color(im).enhance(1.0 - 0.12 * strength)
    im = ImageEnhance.Contrast(im).enhance(1.0 - 0.05 * strength)
    # 4) lower the resolution feel for the cleanest shots, then a touch of softness
    if strength >= 0.6:
        f = 0.74
        im = im.resize((int(W * f), int(H * f)), Image.LANCZOS).resize((W, H), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(0.3 + 0.45 * strength))
    # 5) faint chromatic aberration (cheap phone lens)
    if strength >= 0.4:
        im = chroma_ab(im, shift=1)
    # 6) sensor grain + a little chroma speckle
    im = add_grain(im, amount=0.06 + 0.12 * strength)
    # 7) NO vignette — a darkened corner falloff dulls the photo and reads as an added
    #    "effect", not a real phone snap (human steer 2026-07-07, on a too-dark-edged slide).
    #    Realism already comes from steps 1-6 (imperfect exposure/WB, muted colour, soft grain,
    #    faint chroma). Keep the frame bright + clear to the corners.
    return im

def save_jpeg_lowish(im, path, strength):
    q = int(round(86 - 16 * strength))     # ~73 (dirty) .. 86 (light)
    im.save(path, quality=q)
    if strength >= 0.7:                    # double-compress the cleanest ones for real artifacts
        Image.open(path).convert("RGB").save(path, quality=q - 3)

def main(only=None):
    for slug, (ax, ay, strength) in JOBS.items():
        if only and slug not in only:
            continue
        p = os.path.join(CHOSEN, slug + ".jpg")
        if not os.path.exists(p):
            print("  missing", p); continue
        im = Image.open(p).convert("RGB")
        im = real_grade(cover(im, ax, ay), slug, strength)
        out = os.path.join(GRADED, slug + ".jpg")
        save_jpeg_lowish(im, out, strength)
        print(f"graded {slug}  strength={strength}  size={im.size}")

if __name__ == "__main__":
    main(sys.argv[1:] or None)
