# Charlotte — Base Reference gen prompts (Canada) · 2026-07-26

The verbatim prompts that produce her locked visual identity. Per
`.claude/skills/new-character/SKILL.md` §2 the house aesthetic (K-idol clean-glam makeup · natural B-cup ·
long sleek dark hair · dainty gold jewelry · white ribbed tank · grey seamless studio · 85mm) is
**constant across the roster** — the only things that vary are her `[LOOK]` and her beauty marks.

- **`[LOOK]` = White North-American (Canadian).** Registry: `charlotte` · `id_prefix: ttch` · country **Canada**.
- **Her lane (do not drop this — it is what keeps the roster from reading as one girl):** The soft, warm, approachable one — rounded features, no hard angles anywhere.
- **Age: 22.** The template's stock age line is 25/"mid-20s"; this roster was commissioned at **22**, so
  every prompt below says *22-year-old · clearly an adult woman in her early twenties with mature adult
  facial proportions, never reads younger, never a teenager*. The 21+ kill-switch still governs.
- **Hair:** the house constant is *long sleek dark hair*; for her European colouring it is written as **dark chocolate-brown** so the tone reads natural on her. Length, sleekness, centre part and face-framing strands are unchanged.

**Order:** run **1 (HERO) first and lock it**, then attach the locked hero file to 2 / 3.
**Minimum to run the pipeline = a hero + a closeup** (`prep_cover_refs.py` matches on the keywords
`hero` · `closeup` · `half`).

**Gate (OODA, strictest in the system):** score in this order `AGE (reads 22+) → REAL (no AI/plastic
tell) → ATTRACTIVE`. **Age is a kill-switch** — if a candidate reads under 21, regen; never "try
younger". Do not re-roll the face after locking.

---

## 1 · HERO — locks the identity (do FIRST, solo, full-res)
Save as `Charlotte_01_hero-front.png`.

```text
Editorial agency test-shot, full-resolution studio portrait of a stunning, conventionally attractive
22-year-old White North-American (Canadian) woman — clearly an adult woman in her early twenties with mature adult facial
proportions, never reads younger, never a teenager. Fair neutral-warm skin with a light natural flush across the cheeks. Soft rounded features: a heart-shaped face with a gently rounded, softly tapered jaw and a small chin, softly rounded cheekbones, wide-set warm hazel-green eyes with a slight upward tilt at the outer corners, a small straight nose with a softly rounded tip, and a fuller lower lip under a gently defined cupid's bow.
Healthy radiant glow, a slim well-proportioned figure with a natural B-cup bust subtly accentuated with a light push-up look (tasteful, body-conscious fit). Long sleek dark chocolate-brown hair, center part with soft face-framing
strands. Front-on, neutral straight-to-camera pose, shoulders square, relaxed confident soft gaze.
Wardrobe: a fitted white ribbed tank top with thin straps, natural fabric folds, plus a dainty thin gold
layered necklace. Plain neutral seamless grey studio background. 85mm portrait lens, soft beauty lighting
with soft catchlights.
Signature makeup — K-idol clean-glam, worn-but-effortless: dewy glowy "glass" skin with real texture
still visible (not a mask), a soft rosy "drunk blush" high under the eyes and across the cheeks and nose,
soft straight groomed brows, soft neutral-brown eyeshadow with a subtle slightly down-turned "puppy"
liner, brightened inner corners and a gentle aegyo-sal under-eye, defined natural-length lashes, and a
glossy nude-rosy / soft-coral lip. Cohesive, fresh, pretty — clearly makeup, but it looks effortless.
Skin realism: natural skin with fine pores and real texture, subtle asymmetry, two small identity-defining beauty marks — one on her left cheek just below the cheekbone and one on the right side of her neck, realistic
high-point sheen without glow, loose flyaways and baby hairs; hair shows strand separation and soft real
shine, not a CG sheet. No airbrushing, no waxy or plastic sheen, no over-smoothing. Photorealistic
editorial realism — a real unretouched agency test shot, not AI.
```

## 2 · FACE-CLOSEUP — attach the LOCKED hero
Save as `Charlotte_02_face-closeup.png`. Solo, full-res.

```text
Same woman from the attached reference image — identical face and identity, same fair neutral-warm skin tone,
same beauty marks, same hair. Macro beauty close-up of her face filling the frame, front-on. 100mm macro
lens, soft even light. Maximum skin/eye fidelity: visible pores, real texture, the same beauty marks,
realistic catchlights, eyelash + iris detail. She still reads as a woman in her early twenties, never
younger. Plain neutral grey background. Same K-idol clean-glam makeup as the reference — do not restyle
it. No airbrushing, no waxy sheen, no over-smoothing. Photorealistic editorial realism, real unretouched
person, not AI.
```

## 3 · HALF-FRONT — attach the LOCKED hero
Save as `Charlotte_03_half-front.png`. Gives the scene-gen a body/proportion anchor.

```text
Same woman from the attached reference image — identical face, identity, hair and skin tone, same beauty
marks. Waist-up three-quarter-length studio shot, front-on, arms relaxed at her sides. Wardrobe: the same
fitted white ribbed tank top with thin straps plus straight-leg mid-blue jeans, natural fabric folds, the
same dainty thin gold layered necklace. Plain neutral seamless grey studio background. 85mm portrait
lens, soft beauty lighting. Same K-idol clean-glam makeup as the reference — do not restyle it. Natural
skin with visible pores and real texture, five correct fingers per hand, no distortion. No airbrushing,
no waxy sheen, no over-smoothing. Photorealistic editorial realism, real unretouched agency test shot,
not AI.
```

## 4 · ANGLE / EXPRESSION SHEET — attach the LOCKED hero
Save as `Charlotte_04_vary-angles.png`. Batched as one 2×2 sheet to save gens. `prep_cover_refs.py` picks
this up on the `vary` keyword and it rides along as an identity ref on scene / profile-picture gens
(the PFP recipe attaches identity refs 1/2/4 — hero, closeup and this sheet).

```text
Same woman from the attached reference image — identical face, identity, hair, makeup and skin tone, same
beauty marks, in all four frames. A 2x2 contact sheet of four separate head-and-shoulders studio portraits
of her, evenly divided, no text or labels or borders: (top-left) three-quarter turn to her left, neutral
soft expression; (top-right) three-quarter turn to her right, neutral soft expression; (bottom-left)
front-on, warm closed-lip smile; (bottom-right) front-on, natural open smile with teeth, eyes slightly
crinkled. Identical wardrobe (the same fitted white ribbed tank, the same dainty thin gold layered
necklace), identical plain neutral seamless grey studio background and identical 85mm soft beauty lighting
in every frame — only the angle and expression change. She reads as a woman in her early twenties in all
four, never younger. Natural skin with visible pores and real texture in all four. No airbrushing, no waxy
sheen, no over-smoothing. Photorealistic editorial realism, real unretouched agency test shots, not AI.
```

---

## Rules that keep her consistent (from the skill)
- **AGE is absolute.** Precedence when criteria conflict: `AGE > REAL > IDENTITY-CONSISTENT > ATTRACTIVE`.
- **Lock the hero, then re-anchor to it** — 2 / 3 each attach the *locked hero file*, never the previous
  output, or the face drifts.
- **One variable per gen** — angle OR expression OR framing, never several.
- **Realism guardrail** — the dewy "glass-skin" makeup is the fastest path back to the waxy-AI look; the
  `real texture, no over-smoothing` clauses are load-bearing, never trim them. This base library is
  **editorial** (studio). Her *scene* photos (`chars/charlotte_cover.png` / `_ending.png`) are a different
  recipe — matte, expose-under, real sourced background — see
  `knowledge/realism/persona_gen_prompt_reference.md` + `winning_prompts.md`.

## Next after these
```bash
python3 engine/setup/provision.py create
python3 engine/drive/drive_sync.py --mirror "character/Charlotte" --dest "Charlotte"
```
Then her framework scene photos (skill §5) before her first `human`-variant post.
