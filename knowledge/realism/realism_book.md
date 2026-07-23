# BOOK 2 — REALISM / BELIEVABILITY  (v5)

Defines **how believable** the output is. Identity-agnostic — applies to any subject.
Believability layer. Character identity comes from the **locked Base References** (the signature look
is baked into the images); to create/lock a character see the `new-character` skill ([`.claude/skills/new-character/SKILL.md`](../../.claude/skills/new-character/SKILL.md)).

Scope: **not just static studio stills.** Reusable for image *and* video — how the character looks, lights, moves, and reacts across conditions. v5 adds an explicit layer for **social / UGC phone-snapshot** content, where the believability bar is *lower fidelity*, not higher.

Core principle: remove the **plastic/wax sheen** — do NOT add flaws. Realism means environment-driven detail, not random damage or uglification.
Mental model: *editorial beauty realism* for hero/portrait work; *camera-roll realism* for social/UGC. Real models in unretouched shots still have pores, texture, weight, expression, wardrobe intention, and motion. Real phone snaps additionally have imperfect exposure, messy context, and lower image quality.

**Realism is a SYSTEM, and smoothness is NOT the tell.** A face can be smooth, clear, even symmetric and STILL read fully real — the actual AI tells are **sheen + perfectly uniform tone + impossible hyper-4K crispness**, not smoothness itself. Kill those three (matte finish, non-linear tone, believable lower resolution/softness) and "perfect" skin passes. So there are **four independent ways to defeat the skin/feature tell, and a shot only needs ENOUGH of them, not all:** (1) **add imperfection** — subtle blemishes/asymmetry/texture (D1), most needed when the face is BRIGHT, close and detailed because nothing else hides it; (2) **hide detail with distance** — zoom out to full/three-quarter (D6); (3) **hide detail with low light / degradation** — a dim, warm, noisy, soft, low-res frame the sensor genuinely struggled with (D2 low-light lesson); (4) **occlude the features** — sunglasses/specs, or a raised phone in a mirror selfie (D5 / §5). When 2–4 already carry a shot, do NOT force facial imperfection — the environment does the work, and over-adding flaws can look wrong. **Matte skin + non-linear tone are the near-universal minimums; the rest is situational.**

### What changed in v5 (read this if you used v4)
- New **§5 SOCIAL / UGC PHONE-REALISM**: deliberate quality degradation, studio-vs-real photo selection, the source hierarchy, reference images for generation, OODA-on-generated-output, and watermark handling. These are the lessons from a Vietnam drinks carousel where v4-grade output still read as "too studio."
- Key reframe: for social content, *picture-perfect is the failure*. A clean background, even lighting, and high sharpness read as stock/AI. The fix is BOTH better selection (messy, contextual frames) AND post degrade (lower the quality on purpose).
- v4 is archived at `Archive/02_REALISM_book_v4.md`. v5 supersedes it.

---

## 0. CONTRACT (shared — see the `new-character` skill ([`.claude/skills/new-character/SKILL.md`](../../.claude/skills/new-character/SKILL.md)))

- AGE guardrail absolute · Precedence: `AGE > R1 (real) > R3 (consistent) > R2 (attract)`
- This book owns **R1 — Realistic.**
- OODA every stage: OBSERVE → ORIENT → DECIDE (PASS/REGEN/STOP) → ACT + log. This applies to sourced photos and generated images, not only to character renders.

---

## 1. Domains (apply per scene — not all always-on)

### D1 — Surface texture (static, always-on)
- **Keep:** fine pores, real skin texture, subtle asymmetry, natural freckles/beauty marks already belonging to the identity, slight under-eye/cheek texture, realistic high-point sheen, loose flyaways + baby hairs, natural fabric folds.
- **Skin realism — imperfection is perfection (strongest on close / portrait / profile):** avoid glowing-perfect, poreless, or waxy skin; do not over-smooth. **Picture-perfect skin is the AI tell** — a real face carries a few subtle, believable imperfections, and losing them is what makes an otherwise good render read fake. Give pore-level texture and uneven micro-reflection, PLUS (scene-scaled) one or two small subtle blemishes/spots, faint under-eye texture, slight natural redness around the nose/cheeks, and a light sweat sheen at the hairline/temples when heat, sun, humidity, exertion, or travel justifies it. Keep every imperfection SUBTLE and non-identity-changing — she still reads attractive; the skin just stops reading airbrushed. Scale it: heaviest on candid/close social shots (profile pics, covers, derived scene gens) where skin fills the frame; lightest on the grey-bg editorial base library (which already carries texture + a beauty mark or two).
- **Face/expression realism — super-micro-expression:** expression must react to the environment AND carry a real, tiny candid micro-expression — a slight squint/scrunch around the eyes and nose-bridge, one brow marginally higher, a small asymmetric almost-smile, a natural unposed gaze fixation — **never a blank, symmetric, posed-perfect pretty face** (a dead-neutral symmetric expression is itself an AI tell). In sun, lean into the squint/scrunch. Mouth shape should fit the moment: relaxed closed mouth is fine, but teeth smiles are allowed where the scene, pose, and emotion make them believable.
- **Hair-realism (mandatory on back/profile):** individual strand separation, fine flyaways + baby hairs, soft natural shine — not a uniform CG sheet; slight irregular waves. Only add wind-lifted strands when the environment demands it; otherwise keep hair natural, softly separated, slightly imperfect, and still flattering.
- **Nails (hand-visible):** natural short neutral manicured.
- **Avoid — the over-flaw failure, NOT subtlety:** heavy acne, scarring, prominent or multiple blemishes, rough/unhealthy skin, or anything that dents beauty or changes identity. The ban is on DEGREE, not on imperfection itself: one or two SUBTLE spots read human; "give her blemished/bad skin" reads ugly. Add texture and a couple of faint imperfections — never uglify.
- **Feature asymmetry + the beauty-filter tell (case studies):** real faces are not perfectly symmetric — the two eyes differ slightly in size/shape, one brow sits a touch higher or differently shaped, one side of the nose reads a little different, and makeup is uneven side-to-side (crisper on one side, heavier/lighter in patches) rather than flawless and linear. Some days the eye-bags/eyes look heavier. Bodies carry small variation too — uneven colour, skin texture, natural shape. Above all avoid the **Mei Tu Xiu Xiu (美图秀秀) beauty-filter look**: whitened, poreless, uniformly smoothed skin under a soft global sheen laid over the whole subject. That skin-smoothing glow (distinct from the wet/glossy "global material sheen" in D2) is a top AI/filter tell — kill it and let real texture, redness, and asymmetry show. Still beautiful, just not a flawless supermodel. (A *good* case-study trait to keep: slightly different eye shape/size reads as real.)
- **Base-reference check — patch forward, don't go back:** some existing Base References were baked before these lessons and read too perfect. We do NOT regenerate old base refs — instead, at gen time, check whether the attached reference looks too perfect (airbrushed/whitened) and dial the imperfection back in (texture, asymmetry, scene-appropriate skin) integrated with the environment she's in. Future base-ref generation will bake these lessons in from the start.
- **Matte finish + non-linear skin tone, incl. HANDS (case study — this holds even when the face is "perfect"):** the near-universal minimum is a **matte** skin finish (no glossy/dewy/waxy sheen) and skin tone that is **not one flat even colour** — it varies region to region and pools darker at the joints. **Hands are the clearest test:** knuckles and finger joints read darker and the shine varies finger to finger; a hand (or any limb) rendered in one uniform tone with a dewy sheen is a tell. Same for elbows/knees and the transitions between lit and shadowed skin. This is what lets *smooth, symmetric* skin still pass — smoothness is not the tell; **sheen + uniform tone + hyper-4K crispness** are (see the top-of-book "realism is a system" note).
- **Warm PEACH undertone + hold skin brightness DOWN (case study — human steer 2026-07-10, Chloe sakura profile pic):** the whitening tell has two halves people miss — not only smoothness but a **pale white cast** and an **over-bright, luminous** face. Real skin (especially East-Asian travel/UGC) reads a warm **peach / lightly sun-kissed** tone, NOT porcelain-white, and it is **exposed slightly UNDER — the face is not the brightest thing in the frame, no glow or bloom on the skin.** A bright, evenly-pale, glowing face is a filter tell *even when pores are present*. Warm scene light (golden hour) tempts the model to wash the face bright and white — counter it explicitly: peach undertone, drop the skin exposure a touch, keep it matte. Corollary: soft/overcast light renders skin more matte and natural than a bright golden wash (see D2), so prefer a softer-lit background when a gen keeps coming back too white. **LOCKED (2026-07-10 win — do NOT lose this):** apply "expose under" FRAME-WIDE — the whole photo a touch darker, not just her skin — with warm, slightly-**muted (non-punchy) colour**. The human confirmed this same dim/natural grade is what also made the **background** read real (random ground detail + realistic muted colours), not just the face. So the default persona-gen look = **dim + peach + matte skin + a slightly-under, muted whole-frame grade + random uncontrolled ground/floor detail** (see the D2 imperfect-background lesson); a bright / punchy / whitened / evenly-lit frame is a REGEN, in gen AND in QC.
- Clause: `natural skin with fine pores and realistic texture, a matte finish (no glossy/dewy sheen), non-linear skin tone that varies region to region and pools slightly darker at the knuckles/joints (hands especially), a warm peach/sun-kissed undertone (not a pale white/porcelain cast), skin exposed slightly under (not the brightest point in the frame, no glow/bloom), subtle natural asymmetry (eyes clearly different in size/shape — e.g. one eye a touch larger, one brow marginally higher, one side of the nose a touch different, makeup uneven side-to-side), identity-consistent freckles, one or two small subtle blemishes with faint under-eye/nose redness (kept subtle, still attractive), a light hairline sweat sheen where the scene's heat justifies it, a real candid micro-expression (slight eye/nose scrunch, small asymmetric almost-smile — not a blank neutral), realistic high-point sheen without glow, a few loose flyaways, no airbrushing, no whitening beauty-filter sheen, no plastic sheen.`
- **Emergency de-AI dial:** append `candid, shot on phone, slightly soft, subtle grain, imperfect exposure`.

### D2 — Light & environment
Light is where most AI tells live once texture is fixed.
- **Sources:** full sun · overcast · golden hour · dim / low-key · mixed/practical · indoor window.
- **Shadows:** edge hardness matches source (hard sun / soft overcast); direction consistent with the light; contact + occlusion shadows present (no floating).
- **Skin under light:** subsurface scatter; sheen on high points (nose, cheekbone, forehead) vs matte elsewhere; warm tone in sun, cool in shade. The skin is warm because of lighting and white balance, not because the avatar was repainted.
- **Expression under light:** eyes, brow, cheeks, and nose react to real light direction. For low sun or glare, add a small natural squint/scrunch and matching catchlights instead of wide, studio-perfect eyes.
- **Catchlights:** shape, height, and direction match the actual light source.
- **Hair:** rim light + edge translucency; warm backlight can glow through loose strands, especially in wind.
- **Environment integration:** wardrobe color, fabric weight, skin sheen, hair movement, shadows, and posture must all match the actual location, weather, altitude, season, and time of day.
- **Tone constancy:** locked `skin_tone` must read the same identity across lighting — corrected by white balance, not re-pigmented. (interlocks with the locked Base References)

### D2 addendum — Material finish must be scene-local, not globally stylized
Realism breaks when an image has a single global finish applied across every surface. Avoid treating the whole frame as glossy, wet, cinematic, dewy, polished, or high-contrast by default.
- Read each material separately: skin, hair, fabric, wood, metal, glass, stone, painted walls, pavement, foliage.
- Each surface should reflect light according to its own material properties, not according to a global aesthetic filter.
- Skin can have a natural satin response on high points, while fabric remains matte, hair has controlled strand shine, and walls/floors stay dull or textured.
- Do not let "cinematic," "film," "rain," "neon," or "beauty lighting" create a uniform shine layer over the subject and environment.
- Highlights must be motivated by actual light direction, surface angle, and material reflectivity.
- Shadows and contrast should come from the scene's light sources, not from artificial beauty lighting imposed on top.
- Preserve ordinary camera imperfections when appropriate: uneven exposure, limited dynamic range, soft ambient shadows, slight noise, and non-perfect white balance.

#### Lantern / night-market exposure lesson
When the scene is lit by lanterns, shop windows, neon, candles, or other practical lights, realism improves when the image does **not** look like a globally polished beauty ad. Let the practical lights clip, bloom, or fall off unevenly where the camera would naturally struggle. Keep skin and fabric below the lanterns less glossy than the glowing light sources; avoid turning satin/silk, skin, pavement, and wood into the same wet reflective surface. Use mild exposure imperfection: slightly hot lantern cores, darker pockets in the street, uneven face illumination, mixed color temperature, soft noise/grain, and small areas of under/overexposure.

Clause:
`scene-local material response: skin, hair, fabric, metal, glass, walls, ground, and props each keep their own realistic matte/satin/gloss level; no global gloss filter, no universal beauty sheen, highlights only where motivated by light source, angle, and material; allow practical-light exposure imperfection with slightly clipped lanterns, darker falloff, mixed white balance, and subtle grain where scene-appropriate.`

#### Imperfect-background & non-uniform-exposure lesson (case-study batch)
A too-clean, too-even background is the #1 reason an otherwise good render reads as AI. **Imperfect background is perfection.**
- **Populate + "dirty" the scene.** Real places have life the photographer can't control: other people and cars *near* the subject (not only far off), scattered clouds, an unremarkable/"ugly" sun, an uneven/worn street, a rogue passer-by, a rogue parked car, some run-down buildings beside newer ones, one odd building that stands out. A background with *no one near her* and *nothing out of place* is a tell. (AI also renders far-off people/cars with *some* detail that never resolves into what they actually are — another tell.) **Litter the GROUND/FLOOR with random uncontrolled detail** — scattered petals/leaves, dirt patches, worn/uneven grass, cracks, pebbles, small debris, a stray shadow — a clean, even, tidy floor is a tell. (Human called out this "so much random detail on the floor" as a big part of what sold the 2026-07-10 sakura pfp — LOCKED, prompt for it every persona gen.)
- **Non-uniform exposure & colour across the frame.** A real phone lens does not expose every element equally: some highlights glare/clip and bloom, some elements sit brighter, and brightness/saturation/hue vary element-to-element. A background whose buildings, cars, sky, and traffic lights all share one brightness, one saturation, and one hue — a "linear" look — reads AI. The **sky especially** must not be a flawless linear gradient; break it with clouds and uneven light. This is the environment-scale version of the D2-addendum "no global finish" rule. **Grade the WHOLE frame a touch DARKER with slightly-muted, warmer colours — not bright, not punchy, not saturated.** A slightly-under-exposed, natural, de-saturated grade across the whole photo (subject + background together) is what makes both skin and background read real; a bright, punchy, high-saturation frame reads AI/HDR. **LOCKED from the 2026-07-10 sakura pfp win** — pair it with the D1 peach/expose-under skin bullet; the two are one recipe.
- **Fix path by source:** for a **sourced/stock** photo, re-source a genuinely real one (§5.2–5.3 tools) rather than trying to rescue a too-perfect frame; for a **generated** image, ground it on a real location reference and prompt explicitly for an imperfect, populated background.
- **Ground the subject in it:** the subject's own light must be read from the same imperfect scene — e.g. a face in dappled shade carrying uneven shadow (some from a cap brim, some from tree leaves) with real specks of light between them, and shadow directions that match the sun you can already see on the background. Do NOT light her as if the background were a studio backdrop (the studio-lit subject on a clearly-not-studio street is a classic fail).

#### Camera exposure & dynamic range lesson (backlight — the impossible-exposure tell)
**Render the shot the way a real phone camera would actually EXPOSE that specific light — a camera meters for ONE thing and has limited dynamic range; it cannot hold both a bright sky and a bright face.** One of the most-missed tells (human steer 2026-07-09 on a rooftop-sunset profile pic: an evenly-bright face against a perfectly-exposed glaring sun — physically impossible).
- **Backlit / shooting toward the sun or a bright sky → the subject goes DARK on the front (shadowed, rim-lit on hair/shoulders only, often with flare/haze), OR the bright sky/sun blows out to white. Pick one — never both.** An evenly-lit bright face in front of a bright, richly-detailed sunset/sky is the #1 HDR/AI tell.
- **Front-lit** (sun in front of her, camera aimed away from the sun) → she's lit and the sky reads a normal, un-blown colour: the safe way to get warm even light without the tell.
- **Harsh direct sun → commit to it:** hard, sharp-edged shadows ON her (under the nose, from a brow / cap / sunglasses), high contrast, a hot sheen on lit planes with genuinely dark shadow planes, a natural squint — NOT an even wash.
- **Flattering + safe defaults:** open shade, overcast, or soft blue-hour ambient give even, believable light with a consistent exposure (and let skin read matte). Reach for these instead of forcing a dramatic backlit sky the model will render impossibly.
- **Expose the subject slightly UNDER, not glowing**, and make the scene's light physically interact with her — one side a touch darker, scene colour spilling onto skin, warm practicals spilling at night. She is lit BY the scene, never a bright cutout on a backdrop. Per shot, reason: "where is the light, what would the camera meter for, what goes dark, what clips."

#### Low-light / dim-scene exposure lesson (case-study batch)
When the scene is genuinely dim (night street, bar, night bedroom, dusk indoors), realism comes from two things **together**: the subject is exposed **as part of the dark scene** (not lit separately), AND the phone is allowed to **struggle** the way a real small sensor does. The struggle is one of the strongest levers because it also HIDES skin/feature tells (a smooth, symmetric face passes when the light is low enough) — but it only works if she isn't glowing in the first place. Per shot, reason: *where is the one light, how much of it reaches her, what stays dark.*
- **The subject is IN the dark — her exposure cannot exceed the scene's (the #1 dark-scene tell).** A fully, evenly bright model standing in a dim scene reads as a separately-lit portrait dropped onto a dark background — the night version of the "bright cutout on a backdrop" fail. A phone meters for the *scene*: if the scene is dark, she is dark too — under-exposed, muddy, losing detail in her own shadows — UNLESS a real, visible light source is physically falling on her. Even then, only the part the light reaches lifts; the rest of her stays as dim as her surroundings. Never leave a well-lit, glowing model in a dark frame: dim her down to the scene, or motivate a source that would actually light her.
- **One dominant source → directional falloff across her body, not a flat wash.** Find THE brightest source in the frame and light her FROM it: only the planes facing it catch light; everything turned away falls into shadow, and brightness drops off steeply with distance (a small night source obeys inverse-square, so the far side goes genuinely dark). A lamp / window / shopfront / neon sign / streetlight in the **top-left** means her upper-left is brightest — left temple and cheek, left shoulder, left arm, the left of her chest — grading down to a shadowed right side, a darker front turned away from it, and legs darkest of all (farthest from the light, usually below it). Model that gradient explicitly, match the source's colour (warm tungsten, cool blue neon) and its shadow direction, and let the side away from it fall toward black. A subject lit evenly on every side in a single-source night scene has no motivated light and reads AI.
- **Crushed, EMPTY shadows.** Backgrounds fall to near-black with NO recoverable detail. A real phone cannot lift those shadows; AI's instinct to render detail everywhere is the tell. Let the dark be dark.
- **Lower effective resolution — "1080p, not 4K."** Low light forces the sensor down: softer, less micro-detail, not razor-crisp, with slight handheld motion blur. Impossible hyper-4K clarity in a dim room is fake — the darker the scene, the lower the quality the phone can hold.
- **Sensor noise where light is scarce.** Luminance grain + faint chroma speckle in the shadows and midtones; heavier the darker the scene.
- **Warm ambient white balance** (tungsten/lamp/neon), consistent across skin; **limited dynamic range** so only whatever the light actually reaches sits near correct exposure and everything else — including the parts of HER turned away from the source — falls off into shadow.
- **No flash blowout.** Available light, slightly UNDER-exposed — not a hard, evenly-lit flash frame.
- **Exposure-dependent degradation:** match grain/softness/low-res to the light level — bright scenes stay cleaner, dark scenes get noticeably noisier and softer. A glossy fabric (satin/silk) is tamed to near-matte by the dark, reading soft with only restrained highlights instead of a wet global sheen.

Clause:
`dim low-light phone capture: the subject exposed no brighter than the scene (dark scene → she is dark too, under-exposed and losing detail unless a real source physically lights her), lit directionally from the single dominant source so only the planes facing it catch light while everything turned away falls into shadow with steep falloff, warm ambient white balance matching that source, crushed empty shadows with no lifted detail, limited dynamic range, visible sensor noise in the shadows, softer lower-effective-resolution (1080p-not-4K) with slight handheld softness, available light with no flash blowout, glossy fabrics tamed to near-matte — grain and softness scaled up with how dark the scene is.`

### D3 — Motion (video)
- **Micro-movement:** natural blink cadence, breathing rise/fall, micro weight shifts — never frozen.
- **Gaze:** saccades + natural fixation, not robotic tracking.
- **Body:** weight transfer, natural arm swing, settle — no glide/float.
- **Gesture:** hands lead then settle naturally.
- **Dynamics:** hair + fabric carry momentum, follow-through, settle — no rigid CG.
- **Expression:** smiles build and fade — onset/decay, not snap-on.
- **Temporal identity:** face stable frame-to-frame — no morph. Re-anchor to FACE ANCHOR across frames.

### D4 — Condition micro-detail (scene-scaled)
- **Heat:** sweat sheen, flush, damp hairline. · **Cold:** goosebumps, flushed nose/cheeks, breath vapor. · **Wind:** hair lift, uneven flyaways, fabric flutter, natural squint. · **Exertion:** chest rise, color change, light sweat where plausible. · **Sun / glare:** slight eye scrunch, nose/cheek highlight, small sweat sheen, not glossy skin. · **Wet/dry skin states.**
- Scale to the scene — never default-on. The detail should explain the environment, not decorate the avatar.

### D5 — Wardrobe, styling & accessories (scene-scaled, flattering)
- **Wardrobe must belong to the environment:** travel, weather, terrain, and local activity drive the outfit before fashion fantasy. Avoid gowns, studio outfits, or random glamour unless the scene specifically calls for them.
- **Always flatter the avatar's body:** choose fit, waistline, neckline, layers, and fabric drape that enhance silhouette and proportions while staying tasteful, age-appropriate, and practical for the scene.
- **Show upper-body skin at the neckline by default (when the wardrobe allows).** On character/persona gens, prefer cuts and necklines that expose the **neck, collarbone, shoulders, and a tasteful amount of cleavage** — scoop/V-neck, cami/spaghetti straps, off-shoulder, an open or unbuttoned collar. Among believable outfit options, pick the one that shows more of that upper-body skin, and lean toward wardrobe reference photos with these necklines. Conditional — "if the wardrobe allows": tasteful, age-appropriate, and scene-plausible always win (AGE + R1 are absolute), so don't force it against a genuinely covered look (turtleneck, coat, cold-weather or modesty scene). This is the attract/R2 default and composes with "always flatter the body"; it is NOT a license for lingerie/swimwear (those stay request-only, per below).
- **Revealing vs practical:** when a more revealing look is requested, use believable travel/editorial styling (fitted ribbed tank, cropped knit, open overshirt, fitted trousers, high-waist pants, rolled sleeves). Do not default to lingerie, swimwear, or implausible exposure unless explicitly requested and scene-appropriate.
- **Accessories:** small plausible accessories (subtle earrings, bracelet, necklace, watch, sunglasses, small travel bag, scarf, jacket). Accessories should catch the same light and support the story, not distract from identity.
- **Accessories as a realism aid (feature-hiding).** When a close/zoom-in framing is unavoidable, when the face is hard to blend into the scene or pass as human, or after repeated "looks unreal / too AI" feedback, add face- and skin-covering accessories to hide the hardest-to-fake features: sunglasses or clear specs (best — they cover the eyes and brows), a cap or a cute bandana, plus a little jewelry. Covering skin and features with worn items is a reliable way to push a shot past the uncanny line. This is NOT the default — the default is to follow the wardrobe reference — but if the wardrobe doesn't already include eyewear (etc.) and realism needs it, add one.
- **Fabric realism:** folds, tension points, translucency/opacity, wind behavior, and contact with the body must match the pose and weather.
- Clause: `scene-appropriate flattering wardrobe, tasteful body-conscious fit with a neckline that shows the neck/collarbone/shoulders and a tasteful hint of cleavage where the outfit allows, practical travel styling, subtle accessories, natural fabric folds and wind movement.`

### D6 — Camera framing, distance & pose (the "a real person actually took this" rule)
Across a batch of case studies the single biggest tell was **framing + distance + pose**, ahead of skin detail: a believable phone photo is composed the way a person shoots themselves for an aesthetic post, not the way a studio frames a model. (Scales strongest for the persona cover + any candid persona gen; interlocks with the §5 social bar.)
- **Distance — zoom OUT; full or three-quarter body, never a tight portrait.** Default to a full-body or knees/mid-thigh-up frame with the subject set back from the camera. A tight face crop invites pixel-level scrutiny of skin and features (where the AI tells live) and reads as a posed studio portrait — the worst case-study fails were all close-ups. Zooming out is itself a realism *tool*: minute skin/feature imperfections that are hard to fake simply cannot be scrutinized at full-body distance, which is partly why the wider shots read real.
- **The 3×3 grid rule (framing).** Picture the phone camera's rule-of-thirds grid. Place the subject in the **center column, occupying the middle and lower rows** (col 2, rows 2–3) — standing lower-center with the real environment filling the frame above and around her. This is exactly how people frame a self-shot aesthetic photo, and it doubles as headline headroom on a cover.
- **Gaze — look away, not into the lens.** People posing for an aesthetic photo usually do NOT stare into the camera; default to an unposed off-camera gaze (glancing away/aside/down). A centered dead-on stare reads posed/AI.
- **Pose must fit the context.** The pose has to make sense for where she is and how a real person would stand or move there (mid-stride on a street, a hand adjusting the cap, leaning on something). Reject poses no human would strike in that setting — e.g. sitting stiffly square-to-camera for a "candid" portrait, or a stiff model pose on a busy neon street. Framing and pose are judged *together*: right frame + wrong pose still fails.
- **Pick a background worth shooting.** A real person chooses a spot they genuinely want a photo at — a photogenic street, a nice corner. Choose a background with that pull, then keep it imperfect (see D2).
- **Lean on high-realism formats that stack the levers.** Some formats carry realism because they combine several cues at once — the **mirror selfie** is the strongest: a naturally-motivated one-hand phone-up pose, an eyeline to the mirror/screen (never the lens), a raised phone that occludes part of the face, and usually a dim, ordinary bedroom that hides detail. It stacks occlusion (§5/D5) + low-light (D2) + a genuinely-motivated pose, so it can carry a close/intimate shot that a normal straight-on close-up would fail. Reach for it there.
- Clause: `full-body or three-quarter framing, subject set back and standing lower-center (rule-of-thirds col 2, rows 2–3) with the real environment filling the frame around her, unposed gaze looking away from the lens, a natural pose that fits the location and how a real person would stand there — never a tight centered face-crop, never a dead-on studio stare.`

---

## 2. Prompt block emitted

`[D6 framing/distance/pose clause] [D1 texture/face-expression clause] (+ hair-realism on back/profile) [+ D2 light/shadow/environment integration spec] [+ D3 motion-naturalness per clip] [+ D4 condition detail per scene] [+ D5 wardrobe/styling/accessory clause] [+ §5 phone-snapshot clause for social/UGC]`

Assembly (with the character's Base References):
`[Base References — identity + signature look baked in] + [SHOT/SCENE SPEC] + [LOCATION/LIGHTING REFERENCE] + [D5 WARDROBE/STYLING] + [BOOK 2 realism per domain] + [TECH/lens or phone-capture spec]`

**Proven, human-approved prompt language for persona gens** — the LOCKED *dim + peach + matte skin + slightly-under muted whole-frame grade + random uncontrolled ground detail* recipe (from the 2026-07-10 sakura pfp win), ready to paste: [`persona_gen_prompt_reference.md`](persona_gen_prompt_reference.md). The **verbatim full prompts** that produced approved wins — start from the closest one, and add to it every time the human calls a gen very good — are banked in [`winning_prompts.md`](winning_prompts.md).

**TECH/lens:** headshots `85mm` · macro closeup `100mm` · full-length `50mm` · plain neutral grey for base library; scene-appropriate for derived gen. For social/UGC, replace the lens spec with a **phone-capture spec** (see §5).

---

## 3. Realism OODA gate

- OBSERVE — capture still / frame / short clip, OR the sourced/generated candidate image.
- ORIENT — score vs R1 + active-domain criteria below, AND the §5 social bar when the deliverable is social/UGC.
- DECIDE — PASS → store · REGEN → from anchor (never patch identity) · RE-SOURCE → pick a different photo (for stock/UGC) · STOP → escalate.
- ACT — log the decision and why.

Per-domain pass criteria:
- D6: framing is full/three-quarter (not a tight face crop), subject set back and lower-center (3×3 col 2, rows 2–3), gaze off-camera, pose fits the location; a close studio-portrait framing or a pose that doesn't fit the scene FAILS.
- D1: texture present, no wax sheen, skin not glowing-perfect (carries a couple of subtle imperfections — not airbrushed/poreless, no whitening beauty-filter sheen), face reacts to environment AND holds a candid super-micro-expression (not a blank posed-neutral), hair not a CG sheet.
- D2: shadow direction + hardness match source; tone constant under correction; plausible catchlights; subject lit by the same location light; **in a dark scene the subject is exposed no brighter than the scene and lit directionally from the single dominant source — never an evenly-bright, flat-lit model on a dark background.**
- D3: micro-movement present; weight grounded; no identity morph across frames.
- D4: condition detail matches scene intensity, not always-on.
- D5: wardrobe scene-plausible, body-flattering, tastefully styled, physically integrated.
- **§5 (social/UGC): the frame shows real-world context, the lighting/exposure is imperfect, the quality is believably low, and there is no third-party watermark or baked-in graphic. If it looks like clean stock or a studio product shot, it FAILS even when it is beautiful.**

---

## 4. REALISM failure modes

| Failure | Symptom | Fix |
|---|---|---|
| AI sheen | Waxy, glowing, too-perfect | D1 skin realism + de-AI dial (`candid, shot on phone, slightly soft, subtle grain`) |
| Global material sheen | Skin, clothing, floor, props, background share one glossy finish | Scene-local material response; matte/satin/gloss per material; highlights only where motivated |
| Over-polished night exposure | Practical-light scene looks evenly exposed / beauty-lit | Add clipped lantern cores, darker falloff, mixed white balance, mild noise, matte skin |
| Dead expression | Blank face, eyes too open in harsh sun | D1/D2 environment-reactive gaze, slight squint/scrunch in sun |
| Fake hair | Glossy uniform CG sheet | Hair-realism: strand separation + baby hairs |
| Hand errors | Extra/fused fingers, warped nails | Re-roll; "five fingers, no distortion" |
| Shadow mismatch | Wrong direction / floating | D2 shadows match source; add contact/occlusion |
| Tone drift under light | Skin tans/lightens between lights | Skin-tone lock + white-balance reasoning |
| Frozen / uncanny | Mannequin stillness, dead eyes | D3 micro-movement, blink, breath |
| Identity morph | Face shifts between frames | Temporal identity stability; re-anchor FACE ANCHOR |
| Always-on effects | Sweat/wind in calm scene | D4 scene-scaling |
| Wardrobe mismatch | Outfit looks studio/gown-like or impractical | D5 scene-plausible flattering travel wardrobe; give a wardrobe REFERENCE image (§5) |
| Over-flawed | Beauty dented by HEAVY flaws — acne, scarring, rough/unhealthy skin | Ban is on DEGREE: keep one or two SUBTLE spots + texture/asymmetry; drop acne/scarring words, not subtlety |
| Picture-perfect (AI tell) | Poreless/airbrushed skin + dead-symmetric neutral face — reads AI even when pretty | D1 skin realism: add pore texture + one or two subtle blemishes + faint redness + a candid super-micro-expression (slight eye/nose scrunch, asymmetric almost-smile); scene-scaled hairline sweat |
| **Too studio (social)** | **Clean/seamless background, even lighting, high sharpness, single hero object, no context — reads as stock/AI** | **§5: re-source a frame WITH real context (people, street, clutter) AND degrade quality. Degrade alone cannot fix a context-less composition.** |
| **Uniform set lighting** | **Every slide in a set has the same clean, consistent exposure/white balance** | **§5: per-shot exposure + white-balance jitter so the set looks shot at different moments on a phone, not graded as a batch** |
| **Baked-in watermark / graphic** | **Third-party handle, site logo, infographic text, or dominant brand logo on the subject** | **§5: clone-patch from adjacent clean texture (run patches AFTER grading); if it dominates or won't patch cleanly, re-source** |
| **Random-ugly candid** | **Over-corrected toward "rough": subject half-hidden/awkward, bad angle, cramped (drink in a bag on a bike) — reads as an accidental ugly snapshot** | **§5.8: keep real background but frame the subject as the attractive hero, the way an influencer would. Grade ≠ composition.** |
| **Fake-prop staged** | **Amateur product shot: fake flower + placemat against a blank wall, no real life around the subject** | **§5.8: re-source a genuine café/street composition with real uncontrolled background; reject fake-prop sets** |
| **Too-close / studio portrait** | **Tight face crop, subject square-on, staring into the lens — reads posed/AI and lets skin/feature tells be scrutinized** | **D6: zoom OUT to full/three-quarter, subject lower-center (3×3 col 2, rows 2–3), gaze off-camera, pose that fits the location** |
| **Pose doesn't fit the scene** | **Stiff/awkward or studio pose no one would strike in that real setting (sitting square for a "candid", model-posing on a neon street)** | **D6: pose must match the location and how a real person stands/moves there; judge framing + pose together** |
| **Linear / uniform background** | **Sky a flawless gradient; buildings/cars/lights all one brightness+saturation+hue; no one and nothing near the subject; far people/cars unresolvable** | **D2 imperfect-background lesson: populate + dirty the scene, vary exposure & colour element-to-element; sourced → re-source a real one (§5.2–5.3), gen → ground on a real location ref + prompt an imperfect background** |
| **Impossible backlit exposure** | **Evenly-bright, glowing face in front of a bright, fully-detailed sun/sunset/sky — a camera can't hold both; #1 HDR/AI tell** | **D2 exposure & dynamic-range lesson: backlit → subject dark/rim-lit OR sky blows out (pick one); else front-light her / use open-shade / overcast / blue-hour; harsh sun → hard shadows on her; expose her slightly under, lit BY the scene** |
| **Beauty-filter skin (Mei Tu)** | **Whitened/pale, poreless, uniformly smoothed AND over-bright/glowing skin under a soft global glow over the whole subject** | **D1: kill the skin-smoothing sheen; restore pores/texture, faint redness, feature asymmetry (one eye slightly larger); shift the tone to a warm peach/sun-kissed undertone (not white) and expose the skin slightly UNDER (face not the brightest thing in frame); check the base ref isn't too perfect and dial it back at gen time** |
| **Face won't pass at close range** | **Zoom-out impossible, or repeated "looks unreal" on the face** | **D5: add feature-hiding accessories — sunglasses/clear specs (hide eyes/brows), cap/bandana, jewelry; not the default, only when realism needs it** |
| **Over-clean low-light** | **Dim scene but shadows are full of recovered detail, no noise, razor-sharp 4K, or a hard flat flash look** | **D2 low-light lesson: crush shadows to empty black, add sensor noise, drop to a softer 1080p-not-4K render, warm WB, available light with no flash blowout — scale grain/softness to how dark it is** |
| **Over-bright / flat-lit model in a dark scene** | **Fully, evenly bright subject in a dim scene — outshines the ambient, no directional shadow; reads as a separately-lit portrait pasted onto a dark background** | **D2 low-light lesson: expose her no brighter than the scene (dark → she is dark unless a real source physically lights her); light her directionally from the single dominant source (planes facing it lit, the rest in shadow, steep falloff, matching source colour); add noise/softness for the low light** |
| **Flat-tone / glossy skin & hands** | **A limb or hand rendered in one uniform even colour with a dewy/glossy sheen** | **D1: matte finish + non-linear tone — darker at knuckles/joints, varied finger-to-finger; hands are the clearest test** |

---

## 5. SOCIAL / UGC PHONE-REALISM  (new in v5)

For TikTok/IG/UGC, the deliverable must look like a real person's camera roll, not a brand asset. *Picture-perfect is the failure mode.* Two levers, used together: **selection** (pick messy, contextual frames) and **degrade** (lower the quality on purpose). One without the other is not enough — a beautiful studio shot stays studio after grain, and a perfect grade on a great candid still benefits from imperfection.

### 5.1 What a real phone snap looks like (target)
- **Context, not isolation.** Real surroundings in frame: other people, motorbikes, buildings, signage, table clutter, stools, a hand, the subject set down on a bike seat. A clean or blurred-to-nothing background is a tell.
- **Imperfect light + exposure.** Slightly under/over, uneven across the frame, mixed white balance, a small color cast. Not balanced-to-perfect.
- **Lower quality.** A little soft (not razor-sharp), visible sensor grain, mild chromatic aberration, JPEG compression. Modern HDR "pop" (heavy local contrast/clarity, punchy saturation, crisp edges) reads as edited/AI.
- **Lazy framing.** Slightly off-center, casual, not composed like a product shot.

### 5.2 Selection — studio-vs-real decision tree
For every candidate, ask in order:
1. **Is there real-world context around the subject?** (people, street, clutter, venue) — if no, lean reject.
2. **Is the lighting imperfect / location-driven?** — if it's even studio light, lean reject.
3. **Is the background "dirty"/busy rather than clean/seamless?** — clean seamless → reject.
4. **Resolution sane for the crop?** Slightly low is fine (it helps realism), but avoid extreme upscales that turn into mush (roughly cap upscale around 2x of the cropped region).
5. **Any watermark / baked-in text / dominant brand logo?** — patchable corner mark is OK; dominant or central → reject.
PASS only if it reads "someone snapped this at the place." When the best candid option is lower-resolution than a studio option, prefer the candid one — quality can be degraded down but context cannot be added.

Two more checks: (1) **the subject must be literally correct** — the right dish/drink, the right brand (e.g. green Grab, not teal Xanh SM which is a competitor), no baked-in brand banner or competing on-photo text. (2) **Scenery, landscapes, and standalone objects** (a vista, a fan of cash, a market) are exempt from the studio-vs-candid test — they just need to be real, crisp enough, and, when the message is meant to entice, bright and inviting rather than dark/moody. The composed-candid rule is for a *subject in an environment*, not for backdrops.

### 5.3 Source hierarchy (licensed → contextual → broad)
1. **Pexels / Unsplash** — try first (licensed, clean rights). For niche *local* subjects (e.g. Vietnamese street drinks) they are usually studio/stock; check, then move on. Log that you checked.
2. **Google Places API** — Text Search the venue/dish + photos endpoint. These are real visitor uploads: excellent for storefronts, interiors, and genuine on-site context. Sometimes thin on tight drink/product closeups.
3. **SerpAPI google_images** — best for candid street/product frames. Use **native-language queries** with context modifiers. For Vietnam: add `vỉa hè` (sidewalk), `quán cóc` (street stall), `xe đẩy` (cart), `trên bàn` (on the table), and set `hl=vi&gl=vn`. This consistently surfaces real camera-roll shots over western stock.
4. **scrape.do (fallback when SerpAPI 429s / is monthly-capped)** — proxy/scraper. Two uses: scrape **Bing Images** (`bing.com/images/search?q=...`; the original URLs sit in `murl` in the HTML, easy to regex; Google Images 502s without JS render), and **download hotlink-protected images** (proxy the image URL through scrape.do to bypass 403). Reusable helper: `_work/scripts/scrape_do.py` (`bing_images(query)`, `fetch(url)`). Bing + native-language queries gives plenty of candidates when SerpAPI is exhausted.
Document at each step why you fell through, so the decision tree is auditable.

### 5.4 Degrade (post) — the "real-phone" grade
After selection, push quality DOWN, do not enhance UP:
- Per-shot **imperfect exposure** offset and a small **white-balance cast** (warm/cool + green/magenta), varied per image so a set does not share one consistent grade.
- **Pull back the pop:** reduce saturation and micro-contrast; do NOT apply large-radius clarity or heavy sharpening.
- **Soften** slightly; for the cleanest sources, downscale-then-upscale to kill crispness.
- Add **sensor grain** + a little chroma speckle; faint **chromatic aberration**; mild **vignette**.
- Save at **lowish JPEG quality** (and double-compress the cleanest ones) for real artifacts.
- Strength scales with how clean the source is: hero/cover and re-sourced studio frames need more; already-candid frames need less.
- Generation prompt clause (helps but is not sufficient alone): `casual snapshot on a phone, natural available light, slightly uneven exposure, a little soft, not sharpened, not HDR, not color-graded, mild grain, like a friend's camera roll.`

### 5.5 Generation references — give hair AND clothing, not just face
When generating a character image, attach **identity/face refs PLUS a hair-style reference PLUS a clothing/wardrobe reference** (a styling photo). Name the styling reference in the prompt and instruct the model to match outfit, collar, makeup, jewelry, and hairstyling to it. Describing wardrobe in words alone drifts; a reference image locks it. (Shared styling source: `character/_shared/Wardrobe References/`; each character's signature look is **baked into her Base References** (`character/<Name>/Base References/`).)

### 5.6 OODA the generated image — never blindly accept
Generation is the start of the loop, not the end. OBSERVE the result and score: identity match, styling/wardrobe match, scene plausibility, AND quality (is it too clean/glossy?). DECIDE: PASS, or REGEN from the anchor — including when the result reads too clean/fake, where the fix is to REGEN with better environmental integration (wardrobe ref, zoom-out to a lower-half full-body framing, a candid pose/microexpression, and lighting/shadows that match the scene), not to degrade. Apply **D6 framing/pose** here too — a tight centered portrait, a dead-on stare, or a pose that doesn't fit the scene is a REGEN even when the skin is good. And check the **Base References** you attached aren't themselves too perfect (airbrushed/whitened/beauty-filtered); if they are, dial imperfection back in at gen time rather than regenerating the base refs (patch forward). For the **generated persona cover**, realism comes from the generation itself; do NOT post-degrade the cover. Post-degrade (§5.4) is for **sourced/stock photos**, never the generated cover. Keep the previous best as a fallback before regenerating so you never trade down.

### 5.7 Watermark / baked-in graphic handling
Reject third-party watermarks, infographic text, and dominant brand logos. For a small corner watermark over fairly uniform texture, clone-patch from an adjacent clean region with a feathered, slightly blurred paste. Patches must run **after** grading (grading regenerates from source and would wipe a patch applied earlier) and be reproducible (fixed boxes in a patch step). If the mark sits over busy detail, dominates, or won't patch cleanly, re-source instead.

### 5.8 Composed-candid: real background, but NOT ugly or staged
"Looks like a human took it" means the *background* is genuine and uncontrolled (real café, street, people, plants, a city behind) — the stuff you can't control when you point a camera at your drink. It does NOT mean a badly angled, cramped, or random ugly shot. An influencer took the photo; she still frames the subject to show it off. Keep these two things separate: the **grade** makes it "shot on a phone," the **composition** makes it "a human shot it well." A rough grade cannot rescue a badly composed photo, and a nicely composed one should not be over-degraded into mush.

Three things to reject, two of them new:
1. **Too studio** — clean/seamless background, even lighting, single isolated hero. Too perfect. (covered in 5.2)
2. **Random-ugly / badly thought through** — the subject half-hidden or awkward (e.g. the drink shoved in a plastic bag hung on a motorbike), bad angle, cramped, the kind of accidental snapshot an influencer would never post. Too rough.
3. **Fake-prop staged** — arranged on a placemat with a fake flower against a blank wall, or any "amateur product photo" with no real life around it. Fake context, not candid.

The target sits in the middle: **subject clearly the hero and attractively framed, with a genuine uncontrolled background that has life in it.** Think the influencer's nice rooftop-table or café-table shot with the real city/café behind, a cup held up with a real street blurred behind, a drink on a wooden table with other cups and a phin around it. Not a studio sweep, not a bag on a bike, not a fake flower on a placemat.

Practical sourcing note: the queries that surface this are the ones locals use for nice-but-real café shots — `sống ảo` (instagrammable corner), `góc cafe`, `check in`, `trên bàn` (on the table). Google Places photos of real cafés also yield rooftop/table shots with genuine backgrounds. When a drink is inherently a café drink (no street-vendor version exists, e.g. egg coffee, yogurt coffee, salt coffee), a cozy real café-table composition is the right target, not a forced street shot.

OODA add-on for §3 (social/UGC): PASS only if (a) the subject is the clear, attractively-framed hero, (b) the background is real and uncontrolled but not distracting, (c) the shot reads intentional, not accidental/ugly, and (d) it is not a fake-prop styled set. Fail and re-source on any of: studio-clean, random-ugly, or fake-staged.

### 5.9 Putting a CHARACTER into a real place — give GPT a real background to reference (do NOT invent, do NOT composite)
The single biggest "this looks fake" tell on a persona/character gen is the BACKGROUND: asked to imagine a place (a city skyline, a bar), the image model **invents** one, and the invented background has tell-tale uniform lights / uniform hue-brightness-saturation / flat made-up structures. Two wrong fixes we tried and rejected (human steer 2026-07-09→10): (a) prompting GPT harder in words — it still invents; (b) generating the figure and **rembg-compositing** it onto a real photo — a hard cut never blends (lighting, perspective, and edges never match; the subject reads as pasted-on).

**The method that works: give GPT a REAL background PHOTO as a reference image and tell it to place the character INTO that exact real setting, reproducing the background faithfully.** GPT then does the hard part (integrating the person — light, shadow, perspective, depth) but is **grounded on real pixels**, so the background looks real instead of invented.
- **Source a real background** (Pexels/Unsplash first — watermark-free; `scrape_do`/Bing only as fallback, and reject tiled-watermark stock). This is the same source-it-real discipline as §5.2–5.3, now for the *scene the character stands in*.
- **Attach it as an extra reference** (an added slot beyond the identity + wardrobe refs) and prompt: *"reference image N is a REAL photo of the exact place — reproduce that background faithfully (same location, structures, colours, lighting, time of day, perspective, depth); do NOT invent, replace, or stylise it — and place her naturally INTO it, her lighting coming FROM that scene, with matching shadows, perspective, and a natural phone depth-of-field."*
- **Never hard-composite** a cut-out character onto a background for the final image.

**Choosing the reference background — it MUST be PORTRAIT-WORTHY (apply real portrait-photography judgment):**
- It has to make sense as a place someone would actually **take a portrait**, WITH open **space and framing** for a person to stand in naturally, and real **depth** — the background sits *behind* the subject at a distance so she separates from it and the environment reads around/behind her.
- Pick an **open, zoomed-OUT establishing shot** with a clear "hero spot" (foreground/midground room for the subject) and a nice background behind. **REJECT: tight / zoomed-in detail shots, cluttered scenes with objects right where the subject would stand, or a pure distant vista with no ground for her to stand on.** These leave no room for the character, so the render crams the scene right behind her and she reads as awkwardly overlaid. (Concrete fail from this batch: a close-up of café chairs + a table by a window — no space, subject looks pasted. Good version: an open café interior shot from further back, or a café storefront/patio, with the room/street receding behind her.)
- Good targets: an open beach with the ocean/pier behind; a scenic overlook with a railing + skyline + open foreground; a street receding behind the subject; a garden or park path; a rooftop with an open deck + skyline; a colourful wall with space in front. Judge it the way a portrait photographer scouts a location: *where would she stand, is there room, is the background nice and set back?*
- **QC the placement + blend** before shipping (per §3 + the character-gen QC): does she sit in the space believably, is her light the scene's light, does the background match the real reference and read real, is she NOT crammed against foreground clutter?
