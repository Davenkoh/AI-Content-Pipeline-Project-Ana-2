# Evelyn — Base Reference gen prompts (2026-07-26)

The verbatim prompts that produce her locked visual identity. Per `.claude/skills/new-character/SKILL.md`
§2: the house aesthetic (K-idol clean-glam makeup · natural B-cup · long sleek dark hair · dainty gold
jewelry · white ribbed tank · grey seamless studio · 85mm) is **constant across the roster** — the only
thing that varies is her `[LOOK]`.

- **`[LOOK]` = East-Asian / Korean-idol.**
- **Differentiation from Chloe** (same East-Asian lane, so this matters): Evelyn is the *warm honey /
  peach-undertone, sculpted* one — longer oval face, high sculpted cheekbones, a cleanly defined tapered
  jaw and pointed chin, a straight high nose bridge, deeper crisp double-eyelid crease, fuller lips.
  Chloe is cooler/porcelain with a softer rounded jaw. That contrast is written into the hero prompt
  below; do not drop it or the two accounts read as twins.

**Order:** run **1 (HERO) first and lock it**, then attach the locked hero file to 2 / 3 / 4.
**Minimum to run the pipeline = a hero + a closeup** (`prep_cover_refs.py` matches on the keywords
`hero` · `closeup` · `half`).

**Gate (OODA, strictest in the system):** generate ~4 hero candidates, score in this order
`AGE (reads 21+) → REAL (no AI/plastic tell) → ATTRACTIVE`. **Age is a kill-switch** — if any candidate
reads under 21, regen; never "try younger". Do not re-roll the face after locking.

---

## 1 · HERO — locks the identity (do FIRST, solo, full-res)
Save as `Evelyn_01_hero-front.png`.

```text
Editorial agency test-shot, full-resolution studio portrait of a stunning, conventionally attractive
25-year-old East-Asian (Korean, K-pop-idol aesthetic) woman — clearly an adult in her mid-20s, never
reads younger. Warm honey / light peach skin undertone (not porcelain-white). Refined symmetric-leaning
idol features with a distinctly sculpted structure: a longer oval face, high defined cheekbones, a
cleanly tapered jawline and softly pointed chin, a straight high nose bridge, big expressive soft eyes
with a crisp deep double-eyelid crease, and full well-defined lips. Healthy radiant glow, a slim
well-proportioned figure with a natural B-cup bust subtly accentuated with a light push-up look
(tasteful, body-conscious fit). Long sleek dark hair, center part with soft face-framing strands.
Front-on, neutral straight-to-camera pose, shoulders square, relaxed confident soft gaze. Wardrobe: a
fitted white ribbed tank top with thin straps, natural fabric folds, plus a dainty thin gold layered
necklace. Plain neutral seamless grey studio background. 85mm portrait lens, soft beauty lighting with
soft catchlights.
Signature makeup — K-idol clean-glam, worn-but-effortless: dewy glowy "glass" skin with real texture
still visible (not a mask), a soft rosy "drunk blush" high under the eyes and across the cheeks and nose,
soft straight groomed brows, soft neutral-brown eyeshadow with a subtle slightly down-turned "puppy"
liner, brightened inner corners and a gentle aegyo-sal under-eye, defined natural-length lashes, and a
glossy nude-rosy / soft-coral lip. Cohesive, fresh, pretty — clearly makeup, but it looks effortless.
Skin realism: natural skin with fine pores and real texture, subtle asymmetry, one or two small
identity-defining beauty marks — one just below the outer corner of her left eye and one small one on
the right side of her collarbone — realistic high-point sheen without glow, loose flyaways and baby
hairs; hair shows strand separation and soft real shine, not a CG sheet. No airbrushing, no waxy or
plastic sheen, no over-smoothing. Photorealistic editorial realism — a real unretouched agency test
shot, not AI.
```

## 2 · FACE-CLOSEUP — attach the LOCKED hero
Save as `Evelyn_02_face-closeup.png`. Solo, full-res.

```text
Same woman from the attached reference image — identical face and identity, same warm honey skin tone,
same beauty marks. Macro beauty close-up of her face filling the frame, front-on. 100mm macro lens, soft
even light. Maximum skin/eye fidelity: visible pores, real texture, the same beauty marks, realistic
catchlights, eyelash + iris detail. Plain neutral grey background. No airbrushing, no waxy sheen, no
over-smoothing. Photorealistic editorial realism, real unretouched person, not AI.
```

## 3 · HALF-FRONT (optional but recommended) — attach the LOCKED hero
Save as `Evelyn_03_half-front.png`. Gives the scene-gen a body/proportion anchor.

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

## 4 · ANGLE / EXPRESSION SHEET (optional) — attach the LOCKED hero
Save as `Evelyn_04_vary-angles.png`. Batched as one 2×2 sheet to save gens.

```text
Same woman from the attached reference image — identical face, identity, hair, makeup and skin tone,
same beauty marks, in all four frames. A 2x2 contact sheet of four separate head-and-shoulders studio
portraits of her, evenly divided, no text or labels or borders: (top-left) three-quarter turn to her
left, neutral soft expression; (top-right) three-quarter turn to her right, neutral soft expression;
(bottom-left) front-on, warm closed-lip smile; (bottom-right) front-on, natural open smile with teeth,
eyes slightly crinkled. Identical wardrobe (fitted white ribbed tank, thin gold layered necklace),
identical plain neutral grey studio background and identical 85mm soft beauty lighting in every frame —
only the angle and expression change. Natural skin with visible pores and real texture in all four. No
airbrushing, no waxy sheen, no over-smoothing. Photorealistic editorial realism, real unretouched agency
test shots, not AI.
```

---

## Rules that keep her consistent (from the skill)
- **AGE 21+ is absolute.** Precedence when criteria conflict: `AGE > REAL > IDENTITY-CONSISTENT > ATTRACTIVE`.
- **Lock the hero, then re-anchor to it** — 2 / 3 / 4 each attach the *locked hero file*, never the
  previous output, or the face drifts.
- **One variable per gen** — angle OR expression OR framing, never several.
- **Don't over-collect** — hero + closeup run the pipeline; add 3 / 4 only for a real downstream need.
- **Realism guardrail** — the dewy "glass-skin" makeup here is the fastest path back to the waxy-AI look;
  the `real texture, no over-smoothing` clauses are load-bearing, never trim them. This base library is
  **editorial** (studio). Her *scene* photos (`chars/evelyn_cover.png` / `_ending.png`) are a different
  recipe — matte, expose-under, real sourced background — see
  `knowledge/realism/persona_gen_prompt_reference.md` + `winning_prompts.md`.

## Next after these
```bash
python3 engine/setup/provision.py create
python3 engine/drive/drive_sync.py --mirror "character/Evelyn" --dest "Evelyn"
```
Then her framework scene photos (skill §5) before her first `human`-variant post.
