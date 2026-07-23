# Winning gen prompts — the proven-exemplar library

Append-only library of the **actual, verbatim** image-gen prompts that produced a human-approved
"very good" output. This is the concrete companion to
[`persona_gen_prompt_reference.md`](persona_gen_prompt_reference.md): that doc holds the distilled
*rules* (the LOCKED recipe + QC gate); **this doc holds the real prompts that worked**, so a future gen
can start from a proven exemplar instead of a blank page. Reusing a winner is how we hold realism
**consistent** run-to-run instead of re-discovering it each time.

## The practice — how this grows (do this every time)
When the human calls a gen output very good / super-realistic (or you otherwise confirm a clear win):
1. **Copy the FULL prompt that produced it, verbatim** — every block, no trimming, no paraphrase.
2. Add an entry at the **top** using the template below: date · character · deliverable · why it won · output link · the prompt.
3. **Never rewrite a past prompt's text** — it's the record of what actually worked; only fix metadata around it.
4. Do **not** distill the rule here — sharpening the reusable *rule* is
   [`persona_gen_prompt_reference.md`](persona_gen_prompt_reference.md)'s job (and it routes through
   `propagate-feedback`). This file keeps the **raw winners**; that file keeps the **rules**. One concern each.

## How to reuse one
Match the **deliverable** (profile pic / cover / wardrobe-swap / scene) and **character**, paste the
closest winning prompt, then swap only what changes — character refs, wardrobe ref, the REAL background
ref, the location words. Keep the **SKIN / EXPOSURE / COMPOSITION** blocks intact: those are *why* it read
real, not decoration. Then still run the QC gate in `persona_gen_prompt_reference.md` before ship.

## Entry template
```
### NN — <deliverable> · <character> · <YYYY-MM-DD>
- **Character:** …
- **Deliverable:** … (e.g. square 1:1 profile picture, waist-up)
- **Refs used:** … (e.g. rungen_bg 5-slot — identity 1/2/4 · wardrobe 3 · REAL background 5)
- **Why it won:** … (the human's words / what it nails)
- **Output:** <link or path>

​```text
<full verbatim prompt — every block, untrimmed>
​```
```

---

### 01 — Square 1:1 profile picture (sakura park) · Chloe (Japan) · 2026-07-11
- **Character:** Chloe — Japan (@chloe.belletravel)
- **Deliverable:** SQUARE 1:1 social **profile picture**, waist-up, cherry-blossom park
- **Refs used:** rungen_bg 5-slot — identity refs 1/2/4 · wardrobe ref 3 (white off-shoulder ruffle top) · **REAL background ref 5** (open sakura park with grassy foreground + path + distant people)
- **Why it won:** human called it realistic — the peach / expose-under skin **and** the real sourced background both read real (random floor detail, darker + muted colour). This is the "sakura v2" regen the **LOCKED recipe** in [`persona_gen_prompt_reference.md`](persona_gen_prompt_reference.md) was distilled from — the canonical starting point for any character's outdoor pfp.

```text
A candid SQUARE 1:1 phone photo of a young woman under cherry blossoms in a Japanese park, framed as her social-media PROFILE PICTURE, taken by a friend a step away. It must look like a real photo from someone's camera roll, NOT a studio shoot, NOT a polished model render. SKIN & FACE — THIS IS THE #1 PRIORITY, MAKE IT REAL, NOT A BEAUTY FILTER. Her skin must NOT read white, bright, smooth or perfect: - TONE: a warm natural PEACH / lightly sun-kissed undertone — NOT a pale porcelain-white cast. A whitened, evenly-pale face is the #1 filter tell. Keep it a natural warm medium tone. - BRIGHTNESS: expose her skin slightly UNDER — her face is NOT the brightest thing in the frame, no glow, no bloom, no luminous sheen on the skin. Dimmer and matte, not radiant. - PORES & TEXTURE: clearly visible pores and real skin texture across the cheeks, nose, forehead, chin and chest. A fully MATTE finish (no dewy/glossy/waxy sheen). - IMPERFECTIONS: a couple of small but visible blemishes/spots, slight redness around the nose and cheeks, a faint under-eye shadow — subtle, still attractive, never airbrushed away. - FEATURE ASYMMETRY: her two eyes are noticeably a little different — ONE EYE slightly larger / a slightly different shape than the other, one brow set a touch higher, the mouth/almost-smile a little uneven side-to-side. NOT a flawless symmetric doll face. - KILL the Mei Tu / beauty-filter look entirely: no whitening, no smoothing, no uniform glow, no plastic sheen. - Emergency realism: candid, shot on a phone, slightly soft, subtle grain, imperfect exposure — like a friend's camera roll. IDENTITY: keep the same PERSON as reference images 1, 2 and 4 — same face shape, same eyes, same long straight dark hair (she must clearly read as the same individual) — but apply the real-skin notes above; do NOT beautify, whiten, brighten or slim her. If the reference looks too perfect/airbrushed, dial the imperfection and peach tone back in. WARDROBE: dress her in the outfit shown in reference image 3 and match its styling closely — a white off-shoulder top with soft ruffle/tie detail that bares the shoulders and collarbone, delicate jewelry. Pretty, feminine spring travel style. The off-shoulder neckline tastefully shows her neck, collarbone and shoulders. BACKGROUND — USE THE REAL REFERENCE, DO NOT INVENT: reference image 5 is a REAL photo of the exact place — an open cherry-blossom park with pink sakura trees, an open grassy foreground and a path with a couple of distant people. Reproduce THAT background faithfully (same location, structures, colours, time of day, perspective, depth); do NOT invent, replace, or stylise it. Place her naturally INTO it, set a little back so the blossoms and park read around and behind her, her lighting coming FROM that scene with matching shadows, perspective and a natural phone depth-of-field. Never a cut-out pasted onto a backdrop. COMPOSITION (profile-picture crop): a SQUARE frame, zoomed to roughly the WAIST UP — she is the clear subject in the centre of the square but still set a little back, with the real sakura park filling the frame around and above her. A little headroom. Her face is clearly readable in the upper-centre. NOT a tight face crop and NOT a full-body shot. POSE + EXPRESSION: candid and relaxed, NEVER a centered studio stare. Turned slightly, glancing softly just off to the side (not a hard dead-on stare), a small natural asymmetric almost-smile, one brow a touch higher, a hand loose near her hair or shoulder. Caught mid-moment. CAMERA EXPOSURE & LIGHT — GET THIS PHYSICALLY RIGHT: the warm late-afternoon sun sits behind / to the side and only RIMS her hair and shoulders — her FACE sits in the softer, cooler open shade. Do NOT let the sun wash her face bright or white. Expose her about a stop UNDER so her skin reads matte, dim and peachy, not glowing. One side of her face a touch darker. No blown highlights on the skin. There is no bright blown-white sky directly behind her face. BACKGROUND — MUST BE NON-UNIFORM: petals, branches, grass, path and distant people all at DIFFERENT brightness, hue and saturation; some highlights catch the sun and bloom, some areas fall into soft shadow; real depth and a couple of real distant visitors. Not a clean even postcard. No text, captions, logos, or watermarks anywhere. Five fingers per hand, no distortion.
```
