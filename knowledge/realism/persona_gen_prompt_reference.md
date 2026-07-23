# Persona-gen prompt reference — the LOCKED realism recipe

Canonical, human-approved prompt language for character/persona image gens (profile pics, covers, derived
scene shots). Distilled from the **2026-07-10 Chloe sakura 1:1 profile-pic win** — the human called this
"super realistic" (skin AND background). Do not lose these blocks; they encode the same rules as
[`realism_book.md`](realism_book.md) D1 (peach undertone + expose-under) and D2 (imperfect background:
random ground detail + slightly-under muted colour). Pair with the sourced-background pipeline
(`pgen/rungen_bg.sh`: identity refs 1/2/4 + wardrobe ref 3 + REAL background ref 5).

> **This doc = the distilled RULES. The actual verbatim prompts that won live in
> [`winning_prompts.md`](winning_prompts.md)** — start a gen from the closest proven exemplar there, then
> swap only the refs/wardrobe/background/location. And whenever the human calls a fresh gen very good /
> super-realistic, **append that full prompt to `winning_prompts.md`** (raw winners there; sharpen the rule
> here). Reusing + banking winners is how realism stays consistent run-to-run.

## The recipe in one line
**dim + peach + matte skin + a slightly-under, muted (non-punchy) WHOLE-FRAME grade + random uncontrolled
ground/floor detail + real sourced background she is lit BY.** A bright / punchy / whitened / evenly-lit
frame is a REGEN — in gen *and* in QC.

## SKIN & FACE block (make it the #1 line of the prompt)
```
SKIN & FACE — #1 PRIORITY, MAKE IT REAL, NOT A BEAUTY FILTER. Her skin must NOT read white, bright, smooth or perfect:
- TONE: a warm natural PEACH / lightly sun-kissed undertone — NOT a pale porcelain-white cast. A whitened, evenly-pale face is the #1 filter tell.
- BRIGHTNESS: expose her skin slightly UNDER — her face is NOT the brightest thing in the frame, no glow, no bloom, no luminous sheen. Dim and matte, not radiant.
- PORES & TEXTURE: clearly visible pores and real skin texture across cheeks, nose, forehead, chin and chest. A fully MATTE finish (no dewy/glossy/waxy sheen).
- IMPERFECTIONS: one or two small but visible blemishes/spots, slight redness around the nose and cheeks, a faint under-eye shadow — subtle, still attractive, never airbrushed.
- FEATURE ASYMMETRY: her two eyes are a little different — ONE EYE slightly larger / a slightly different shape, one brow a touch higher, the almost-smile a little uneven side-to-side. NOT a symmetric doll face.
- KILL the Mei Tu / beauty-filter look: no whitening, no smoothing, no uniform glow, no plastic sheen.
- Emergency realism: candid, shot on a phone, slightly soft, subtle grain, imperfect exposure — like a friend's camera roll.
```

## EXPOSURE + BACKGROUND block (whole-frame dark/muted + random ground detail)
```
CAMERA EXPOSURE & LIGHT: expose the WHOLE frame slightly UNDER — a touch darker overall, warm, with slightly-muted (non-punchy, not saturated) colour. She is lit BY the scene's real light (not a studio cutout); one side of her a touch darker; no blown highlights on skin; no bright blown-white sky behind her face.
BACKGROUND — REAL + IMPERFECT: reproduce the real reference background faithfully (do NOT invent); populate + "dirty" it (people/objects near her, uneven wear); LITTER THE GROUND/FLOOR with random uncontrolled detail — scattered petals/leaves, dirt patches, worn uneven grass, cracks, pebbles, small debris, stray shadow. Non-uniform brightness/hue/saturation element-to-element; sky broken with uneven cloud, never a linear gradient.
```

## Also always include (unchanged from the proven prompt)
- **Identity:** keep the same PERSON as refs 1/2/4 but apply the real-skin notes; if the ref looks too perfect/airbrushed, dial imperfection + peach tone back in (patch forward).
- **Wardrobe (D5):** match ref 3; neckline shows neck/collarbone/shoulders (+ tasteful cleavage) where the outfit allows.
- **Composition:** square 1:1 for a profile pic, waist-up, subject set back with the real environment filling the frame, face readable upper-centre — never a tight face crop or dead-on studio stare (D6).
- **Pose/gaze:** candid, gaze off-lens, pose fits the location.
- **Tail:** no text/logos/watermarks; five fingers per hand, no distortion.

## QC gate (check every one before ship — a FLAG is a REGEN, not a pass)
1. Skin: peach not white, exposed UNDER (face not brightest thing), matte, visible pores, a couple of blemishes, eyes/brows asymmetric.
2. Whole-frame grade: slightly dark + muted, NOT bright/punchy/saturated.
3. Ground/floor: random uncontrolled detail present, not a clean even floor.
4. Background: real, populated, non-uniform exposure/colour; she is lit BY it.
5. D6 framing/pose/gaze; D5 wardrobe/neckline; hands; identity; no watermark.
