# Tuning — Stage 8 (persona cover/character gen + realism)

**Read this (and `../realism/realism_book.md`) before generating the persona cover.** Feedback about
the avatar looking fake, too clean, wrong framing, or off-identity lands here.

## Principles
- The active persona (set `MASQ_PERSONA=Ana` or `Chloe`) is generated through the logged-in ChatGPT
  image model over CDP. Attach the persona's **Base References** (the signature look is baked into
  them — `character/<Name>/Base References/`) + a wardrobe/styling ref; name the wardrobe photo.
- **Prompt for the unedited look:** candid, natural available light, slightly uneven
  exposure, a little soft, not HDR, not color-graded, mild grain, real street context,
  headroom up top for the headline. The generation itself must deliver the realism via
  environmental integration (wardrobe/framing/pose/lighting) — the cover is NOT
  post-degraded.
- **OODA, don't blindly accept.** Check identity, wardrobe, scene, quality. Keep the prior
  best as a fallback before regenerating.

## Lessons (append-only; newest at bottom)
- **Denim is the tell:** the model renders jeans too pristine/flat. Ask for realistic worn
  denim — natural crease/fold lines at hips/knees/waist, slight fade, imperfect drape.
- **Too-close framing + too-perfect subject + invented background read fake.** Frame
  three-quarter (knees/mid-thigh up), close enough that her face clearly reads as the same
  woman; ground the scene with a REAL location reference photo.
- **Full-body drifts the face** — favour three-quarter and re-state her exact face shape
  (soft jaw, rounded chin).
- **Footwear must be stylish** (heels/heeled boots), never flip-flops, or crop the feet out.
- On closing/wind-down slides go lighter on the makeup (relaxed); full glam holds for the
  cover + main slides.
- **Stage-7 wardrobe is SPEC'd, not open-ended (user feedback 2026-06-18).** Decide the
  setting from the content yourself; then tell the user the wardrobe requirements
  (climate/season + vibe + which slides she's in) so they don't hand you season-mismatched
  clothes (e.g. winter clothes for a tropical Saigon scene).
- [2026-06-30] **Realism comes from ENVIRONMENTAL INTEGRATION, not grain (ttc-01: a first
  cover passed QC while looking fake).** The cover needs NO post-degrade at ALL — the
  regenerated ttc-01 cover looked real straight from the gen; realism comes from wardrobe +
  zoom-out + candid pose/expression + matching light, not grain. The GENERATION must integrate: light from one consistent
  direction with matching shadows on her body and on the ground; a candid pose that fits the
  scene (mid-stride, glancing back, hand on the bag strap, never a centered studio stare); a
  microexpression that reacts to the environment (slight squint + easy smile in sun); a few
  wind-lifted strands; real skin/hair texture (no airbrush, no plastic/gloss). Prompt for all
  of this explicitly.
- [2026-06-30] **Always dress the persona in a real wardrobe outfit. ATTACH a wardrobe
  reference image as a gen ref (slot 3), never leave her in the base/default look** (it reads
  generic and fake). Pick a season-appropriate full-outfit photo from
  `character/_shared/Wardrobe References/`, attach it, and tell the gen to match its top,
  bottoms, footwear, and styling. (gpt_prep attaches slots 1/2/3; use slot 3 for the wardrobe
  when the identity is already carried by hero + closeup.)
- [2026-06-30] **The cover vision-judge must actually REJECT a fake cover** (tight centered
  crop, studio lighting, default clothing, blank expression, light that doesn't match the
  scene). Passing one of those is a QC failure. Regen with the integration + wardrobe +
  zoom-out fixes above before accepting.
- [2026-07-07] **Profile pics / candid persona gens: push realism PAST picture-perfect —
  subtle skin imperfection + a super-micro-expression** (human review of Hannah's 3 profile
  pics: "1 and 3 is most realistic … what can be improved is micro expression and the skin …
  there should be super micro expression like slight scrunches … skin should [not] look so
  perfect, there should be some blemishes, some sweat (if it makes sense), some environmental
  indicators … 1 works because she don't look as picture perfect … humans are naturally
  imperfect. imperfection is perfection"). **Keep what the good ones already nail:** a slight
  sun/lens flare like a real camera, wind (sea/mountain/open air) lifting the hair, matching
  directional shadowing, strand-level hair. **Add on the FACE:** (a) a real candid
  **super-micro-expression** — a slight eye/nose-bridge scrunch, one brow a touch higher, a
  small asymmetric almost-smile, an unposed gaze — never a blank posed-neutral pretty face;
  (b) **believably imperfect skin** — visible pores/texture, one or two small SUBTLE
  blemishes/spots, faint under-eye + around-the-nose redness, a light sweat sheen at the
  hairline/temples where heat/sun/humidity/exertion justify it, plus environmental indicators
  (sun on the skin, windburn flush). Keep it SUBTLE and non-identity-changing — the goal is
  "stops looking airbrushed," not "ugly." This **refines the older D1 "do NOT add flaws / drop
  blemish words" rule:** the ban is on HEAVY flaws (acne, scarring, uglification), NOT on the
  one-or-two-subtle-imperfections that make a close/portrait shot read human. Strongest on
  close/portrait/profile shots (skin fills the frame) + the persona cover; the grey-bg
  editorial base library stays lighter. Propagated into `../realism/realism_book.md` D1 (skin
  realism, face/expression, avoid, clause, §3 pass-criteria, failure table).
- [2026-07-08] **Case-study batch (5 gens: LA full-body / Vegas / rooftop close-up / sunlight-squint /
  neon-street) — the realism hierarchy is FRAMING+POSE → BACKGROUND → LIGHTING → SKIN, and
  "imperfection is perfection" at every layer.** The real-vs-fake split was driven FIRST by framing,
  distance, and pose, then background/lighting imperfection, and only then skin. Propagated into
  `../realism/realism_book.md` (new **D6 framing/distance/pose**; D2 imperfect-background & non-uniform-
  exposure lesson; D1 beauty-filter/asymmetry + base-ref-check bullets & clause; D5 feature-hiding
  accessories; §2 prompt block; §3 OODA D6 + D1; failure table +5 rows; §5.6). Operational rules for
  persona / cover / profile gen:
  - **Framing & distance (biggest tell):** zoom OUT — full or three-quarter body, subject set BACK,
    standing **lower-center** (rule-of-thirds col 2, rows 2–3) with the real environment filling the
    frame around her. NO tight face crops (they let skin/feature tells be scrutinized and read as a
    studio portrait). The two "super AI'd" case studies were both close-ups; the two "real"/"borderline-
    real" ones were full-body wide. Distance itself hides the hardest-to-fake skin/feature detail, so it
    is the SAFER default — reserve close-ups for when we can carry the skin/asymmetry work or hide
    features with accessories; OK to vary the hairstyle across gens.
  - **Pose & gaze:** an unposed gaze looking AWAY from the lens (people don't stare into the camera for
    an aesthetic photo) and a pose that fits the location + how a real person actually stands there.
    Reject stiff/awkward or model poses that don't fit the scene (a "candid" sitting square-to-camera; a
    runway pose on a neon street). Judge framing + pose TOGETHER.
  - **Background = imperfect + non-linear:** pick a spot worth shooting, then keep it real — people/cars
    NEAR her (not just far off), scattered clouds, an "ugly" sun, worn/run-down elements beside new
    ones, a rogue person/car; and vary exposure/saturation/hue element-to-element (a real phone blows
    some highlights hotter than others). A flawless linear sky, or a background where every element
    shares one brightness/hue, is the #1 AI tell (far-off people/cars showing some detail that never
    resolves = another tell). Sourced photo → re-source a real one with the §5.2–5.3 tools; gen →
    ground on a real location ref + prompt an imperfect, populated background.
  - **Subject lighting reads from the scene:** uneven, environment-driven face shadow (some from a cap
    brim, some from tree-leaf shade, with specks of light) and shadow directions matching the sun
    already visible on the background — never studio lighting/saturation on a clearly-not-studio street.
  - **Skin/face = believably imperfect (extends the 2026-07-07 lesson):** no glossy flawless supermodel
    skin. Feature asymmetry (eyes slightly different size/shape — a *good* trait to keep — one brow/one
    side of the nose a touch different), makeup uneven side-to-side, heavier eye-bags some days, faint
    redness/blemishes, body-skin variation. Kill the **Mei Tu Xiu Xiu (美图秀秀) whitening beauty-filter
    sheen** — a soft smoothing glow over the whole model is a top tell. Because we won't regen old
    **Base References**, CHECK the attached ref for being too perfect and dial imperfection back in at
    gen time (patch forward).
  - **Accessories as a fallback:** when a close framing is unavoidable, the face won't blend/pass, or
    feedback keeps saying "too AI," add feature-hiding accessories — sunglasses/clear specs (best, they
    hide eyes+brows), a cap/cute bandana, a little jewelry. NOT the default (follow the wardrobe ref);
    add only when realism needs it and the wardrobe lacks it.
- [2026-07-08] **Low-light mirror-selfie case study — realism is a SYSTEM; the tell is sheen + uniform
  tone + hyper-resolution, NOT smoothness (this one passed DESPITE perfect symmetric skin).** A dim
  black-slip bedroom mirror selfie read fully real even though the face was smooth and symmetric, because
  every OTHER layer carried it and the low light hid the skin. Propagated into
  `../realism/realism_book.md` (top "realism is a system / four ways to beat the tell" note; D1 matte +
  non-linear-tone/hands bullet + clause; new D2 low-light/dim-scene lesson + clause; D6 mirror-selfie
  format bullet; failure table +2 rows). Key learnings:
  - **Smooth ≠ fake.** The real AI tells are (a) SHEEN, (b) perfectly UNIFORM skin tone, (c) impossible
    HYPER-4K crispness. Kill those three — matte finish, non-linear tone, believable lower-res/softness —
    and even clear, symmetric skin passes. Don't treat "add imperfection" as the ONLY fix.
  - **Four independent ways to defeat the skin/feature tell — a shot needs ENOUGH, not all:** (1) add
    subtle imperfection/asymmetry (D1) — most needed on BRIGHT, close, detailed faces; (2) hide detail
    with distance / zoom-out (D6); (3) hide detail with low light + degradation (D2); (4) occlude
    features (sunglasses/specs, or a raised phone in a mirror selfie — D5/§5). When 2–4 carry it, do NOT
    force facial flaws.
  - **Low light is a top lever** because the sensor genuinely struggles: crushed EMPTY shadows (no
    recovered detail — let dark be dark), lower effective resolution ("1080p not 4K", softer, slight
    handheld blur), sensor noise in the shadows, warm ambient WB, limited dynamic range (only the
    face/chest near correct exposure), NO flash blowout. Scale grain/softness to how dark it is. A glossy
    satin/silk dress is tamed to near-matte by the dark (restrained highlights, not a wet sheen).
  - **Matte + non-linear skin tone are the near-universal minimums.** Skin is never one flat even
    colour — it pools darker at joints and varies region to region. **Hands are the clearest test:**
    darker knuckles/finger joints, shine varying finger-to-finger; a uniform-tone glossy hand is a tell.
  - **Ordinary > aspirational background** — a normal, dim, un-styled bedroom reads more real than a
    perfectly nice one.
  - **Mirror selfie = a high-realism format that STACKS levers** (natural one-hand pose, eyeline to the
    mirror not the lens, phone occluding the face, dim ordinary room). Reach for it when a normal
    close-up would fail.
- [2026-07-08] **Wardrobe default — show upper-body skin at the neckline whenever the outfit allows.** On
  character/persona gens, prefer necklines/cuts that expose the **neck, collarbone, shoulders, and a
  tasteful amount of cleavage** (scoop/V-neck, cami/spaghetti straps, off-shoulder, open/unbuttoned
  collar); among believable options pick the one that shows more of that skin, and lean toward wardrobe
  reference photos with these necklines. Conditional — tasteful + age-appropriate + scene-plausible
  always win (AGE + R1 absolute), and don't force it against a genuinely covered look (turtleneck/coat/
  cold or modesty scene) — "if the wardrobe allows." NOT lingerie/swimwear (request-only). Propagated
  into `../realism/realism_book.md` D5 (new "show skin at the neckline" bullet + clause). R2/attract
  default; composes with "always flatter the body" + the feature-hiding-accessories rule.
- [2026-07-09] **Camera exposure & dynamic range is a must-QC play — a backlit-but-evenly-bright face is
  the #1 tell, and I shipped one (a rooftop-sunset Hannah profile pic) without checking.** Two lessons:
  - **(process) ALWAYS run an explicit realism QC that FLAGS every relevant playbook play and checks the
    gen against each BEFORE shipping any character gen — don't eyeball it.** The failure is almost always
    the BACKGROUND + how the ENVIRONMENT plays on her, not the face alone. (Also saved as a `feedback`
    memory.)
  - **(craft) Render the shot the way a real phone camera would EXPOSE that light.** A camera meters for
    ONE thing / limited dynamic range: **backlit → subject dark & rim-lit OR the sky blows out, never both**;
    front-light / open-shade / overcast / blue-hour for even flattering light with a normal sky; **harsh
    sun → hard shadows ON her**, not an even wash; expose her slightly under, lit BY the scene (colour
    spill, cast shadows, warm practicals), never a bright cutout on a backdrop; background non-uniform
    (element-to-element brightness/hue, clipping, no smooth-gradient sky). Fixed the batch by reshooting
    the 4 well-lit close-ups in consistent light (blue-hour / overcast / harsh-done-right). Propagated into
    `../realism/realism_book.md` (new D2 "camera exposure & dynamic range" lesson + failure-table row).
- [2026-07-10] **Character-into-a-real-place: give GPT a REAL, portrait-worthy background photo as a
  reference and have it place her INTO the scene — do NOT let GPT invent a background, and do NOT
  rembg-composite.** Human steer (emphatic, repeated). The fake-background tell (uniform lights, esp.
  skylines) is because GPT invents the place; the cure is to hand it a real photo to reproduce. Wrong turns
  I made first: (1) "prompt GPT harder" — still invents; (2) rembg cut-out + composite onto a real bg — a
  hard cut never blends (light/perspective/edges mismatch → overlaid look). RIGHT: attach a real bg photo as
  ref 5 (`pgen/rungen_bg.sh`) + prompt "reproduce ref 5 faithfully, place her INTO it, lighting from that
  scene" — GPT integrates her, grounded on real pixels. **AND the reference must be PORTRAIT-WORTHY:** an
  open, zoomed-out scene with real SPACE + depth + a hero spot for the subject (use portrait-photography
  judgment) — never a tight/cluttered detail shot (a café chairs-and-table close-up = fail, she reads
  pasted). Source Pexels/Unsplash first (need `Mozilla/5.0` UA + unverified SSL on Py3.14). Propagated into
  `../realism/realism_book.md` new §5.9 + a `feedback` memory. Interlocks with the "QC every char gen before
  ship" rule (QC the placement + blend too).
- [2026-07-10] **Dark scenes: the model is IN the dark, and one light source lights her directionally —
  a dark gen that kept her bright + evenly lit should NOT have passed QC.** Human steer. Two craft points
  + one process point:
  - **(craft) Exposure match:** a phone meters for the scene, so a dark scene means a DARK subject —
    under-exposed, muddy, losing detail — UNLESS a real visible source physically lights her. A fully,
    evenly bright model in a dim frame is the night version of the "bright cutout on a backdrop" tell.
  - **(craft) Directional single-source falloff:** find THE dominant light (e.g. one bright source in the
    top-left) and light only the planes facing it — top-left source → her upper-left (left cheek/shoulder/
    arm) brightest, grading to a shadowed right side and darkest legs; steep inverse-square falloff; match
    the source colour + shadow direction; NOT a flat all-sides wash. Plus lower iPhone quality (noise /
    soft / 1080p-not-4K) because the sensor struggles in the dark — darker = worse.
  - **(process) Must-QC play** — flag it on every dark-scene gen. Propagated into
    `../realism/realism_book.md` D2 low-light lesson (two new leading bullets + clause), the failure table
    (new "Over-bright / flat-lit model in a dark scene" row), and the §3 D2 pass criterion.
