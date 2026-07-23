# Feedback Propagation Log

Append-only audit of every piece of review feedback and **where it propagated** —
which governing doc/config was edited so the lesson applies to all future posts.
Newest at the bottom.

Written by **Stage 11** of `WORKFLOW.md` (poll the Sheet's Feedback column → classify →
propagate → clear the cell). Each lesson is appended to the matching per-stage tuning file
(`01_analysis` … `05_realism`) and/or a canonical knowledge doc, logged here, then the
Sheet's Feedback cell is cleared and the row's Metadata stamped. Format per entry:

```
## <output id> (YYYY-MM-DD)
- Feedback: <verbatim from the Sheet>
- Theme: voice | cover-polish | funnel | identity | platform | sourcing | realism | other
- Propagated to: <file path(s) + section edited>
- Change: <one line on what changed>
```

---

<!-- entries below -->

## tt-014 (2026-06-10)
- Feedback: jeans/denim looks a bit too perfect, reads fake (AI tell)
- Theme: realism / cover-polish
- Propagated to: CAROUSEL_WORKFLOW_PLAYBOOK.md §7 (after-gen OODA) + §8 (lessons)
- Change: character-gen prompts must request realistic worn denim (creasing, fades, soft drape); OODA now checks fabric isn't too perfect

## tt-014 closing (2026-06-12)
- Feedback: closing shot too close to camera, subject too perfect, background looks fake; use a real-place reference; lighter makeup on the ending page
- Theme: realism / framing / makeup
- Propagated to: CAROUSEL_WORKFLOW_PLAYBOOK.md §7 + §8; [[ana-look-y2k-abg]] memory
- Change: gens attach a REAL location photo to ground the background; medium/fuller framing (don't crowd the camera); closing / wind-down slides use lighter natural makeup. Re-genning tt-014 06_close with these.

## tt-014 closing v2 (2026-06-12)
- Feedback: face shape drifted (looks different), jeans too perfect around the waist (shadow/lighting), and flip-flops read sloppy/not sexy
- Theme: identity / realism / styling
- Propagated to: CAROUSEL_WORKFLOW_PLAYBOOK.md §8; [[ana-look-y2k-abg]] memory
- Change: full-body distance drifts the face, so frame three-quarter (knees up) + re-state her exact soft-oval face; denim needs real shadow + fit creases at the waist/waistband; footwear must be stylish (heeled boots), never flip-flops. Re-genning 06_close.

## discovery + ideation discipline (2026-06-12)
- Feedback: scrape only metric-WINNERS; analyze each post VISUALLY (read the slides, not the caption keyword); judge funnel-fit by content + replicability; discard non-fits even from trusted seed creators. Example: #14 "PLAN A" was a dating meme that I keyword-matched to F4 travel-planning.
- Theme: discovery / ideation discipline
- Propagated to: `ideation.md` (analysis gate), `discover_inspo.js` (view-ranking + `--min-views`), [[automation-content-loop]] memory
- Change: discovery now ranks candidates by views; ideation requires a per-post analysis card (what it is / why it worked / funnel fit / replicable) before queueing; never keyword-match.

## tt-015 review (2026-06-12)
- Feedback: (1) overlay line breaks placed anyhow, hard to read, must be lazily typed with deliberate breaks + respect margins; (2) cover looks green-screened, needs real iphone exposure coherence + imperfect windblown hair (less perfect); (3) slide 2 map must be a real google map; (4) inspo had weak metrics and was copied too 1:1, analyze what works and recreate it in own flavour
- Theme: realism/cover · overlay/text · map/format · discovery/inspo
- Propagated to: CAROUSEL_WORKFLOW_PLAYBOOK.md §7 + §8 (green-screen/exposure + environment hair; deliberate line breaks within margins; map = real Google Maps); `Automation Node/routines/ideation.md` hard rules (metrics floor ≥10k views / ≥1k likes + re-verify at selection; don't clone 1:1, recreate the working element in own flavour); tt-015 `_review.md` regen checklist; [[automation-content-loop]] memory
- Change: lessons captured for the loop; tt-015 itself NOT regenned (user will regen another time) — the regen checklist on the row/_review.md guides that rebuild.

## tt-16 wardrobe-spec (2026-06-18)
- Feedback: don't ask me for the setting + wardrobe generically — YOU pick the setting from the content, and TELL me what wardrobe to pick (climate/vibe) so I don't hand over winter clothes for a summer setting.
- Theme: realism / asset-request (Stage 7)
- Propagated to: WORKFLOW.md §7 (persona-needed bullet), knowledge/tuning/05_realism.md
- Change: Stage 7 now decides the setting itself and SPECS the wardrobe (climate/season + vibe + which slides she's in) for the user to pick.

## tt-17 humanized-copy + hot-take receipts (2026-06-23)
- Feedback: "don't use —"; "use humanized language, you can reference the human way it was typed from where you got these information from (im guessing reddit)" (given while composing the Vietnam overrated/underrated post tt-17).
- Theme: copywriting / voice (Stage 6)
- Propagated to: knowledge/tuning/02_copywriting.md Lessons (echo real source phrasing; never em/en dashes, reinforced; hot-takes need a real receipt + pre-empt the "well actually").
- Change: tt-17 caps rewritten to carry real traveler register ("eurodisney", basalt = "giant's causeway", "a half built hotel blocks the valley view"); all em dashes removed; the close slide was also dropped per user (deck ends on the F5 reveal).

## tt-18 placement-steer (2026-06-23)
- Feedback: "move planning it to earlier in the slides, maybe the third one, remember this for all future posts, that people usually don't scroll to the end, so keep holicay placement around the middle or front" (given while composing the Vietnam first-timer guide tt-18).
- Theme: copywriting / funnel placement (Stage 5/6)
- Propagated to: knowledge/tuning/02_copywriting.md Lessons; CTA C005 + C004 lessons (Sheet); [[holicay-placement-front-middle]] memory
- Change: the Holicay/app slide moves to front-middle (around slide 3), never the back; tt-18 reordered so the planning slide is 02 (right after where-to-go). F5 decoy reveal also moves its reveal front-middle going forward (caption still carries it for non-swipers).

## ttc-01 cover + Holicay-slide design (2026-06-30)
- Feedback: (given on Chloe's debut ttc-01) the cover persona looked fake/studio in default clothing with a pose/lighting that didn't match the scene; the cover text was too high + too small + not exciting; the human should be zoomed out + in the lower half; the Holicay slide had a blank background and unnatural copy ("i don't zigzag tokyo") with a stray dangling word; the logo was too small. Meta: "why did you not learn from the tiktok inspos what their designs was... so shitty and deterministic."
- Theme: design (Stage 8) + realism / persona cover (Stage 8) + Holicay-slide copy.
- Propagated to: knowledge/tuning/04_design.md Lessons (reference inspo + winning covers, don't ship a template; cover headline bigger/exciting/emoji in the upper area with breathing room; persona zoomed-out + lower-half; Holicay slide gets a darkened photo bg + natural feature copy + sizable logo) and knowledge/tuning/05_realism.md Lessons (realism via environmental integration not grain; ALWAYS attach a real wardrobe ref, never the default look; the cover vision-judge must reject a fake/studio cover).
- Change: ttc-01 cover regenned with a wardrobe ref (Summer Outfit 4), zoomed-out lower-half full-body candid pose, environmental lighting/shadows/microexpression, a light degrade (0.32) [superseded by the next entry, which removes cover degrade entirely]; headline enlarged (~82px) + 🗼 emoji + moved to the upper-third. Holicay slide rebuilt on a darkened black-tinted Tokyo-night skyline with "how i plan my trip" + "i pin everything on a canvas, map my route with ai, and see the weather all in one place" and a bigger white wordmark. Re-delivered to Drive.

## ttc-01 cover realism = gen, not degrade (2026-06-30)
- Feedback: (given on the regenerated Chloe ttc-01 cover) the cover looked real straight from the generation — so the persona cover no longer needs any post-degrade. Its realism comes from everything else: the wardrobe reference, the zoomed-out lower-half framing, a candid pose + microexpression matching the scene, matching lighting/shadows, and real (not airbrushed) skin/hair.
- Theme: realism / persona cover (Stage 8)
- Propagated to: engine/design/cover_finish.py (degrade removed, size-only), knowledge/tuning/05_realism.md, knowledge/realism/realism_book.md §5.6, WORKFLOW.md §8, BLUEPRINT.md, .claude/skills/new-post + new-character SKILLs.
- Change: cover_finish no longer degrades the cover — the generation itself carries realism (wardrobe ref, zoom-out lower-half framing, candid pose + expression, matching lighting/shadows, real skin/hair). Sourced-photo degrade (grade.py) is unchanged and still applies to stock/real photos.

## ttc-02 text-overlap QC (2026-07-01)
- Feedback: (on the ttc-02 Holicay slide) "do you not see the text overlapping each other? can you ensure these type of issues are fixed during qc". The headline "how i actually plan tokyo 🗺️" was too wide for one line, so the map emoji wrapped onto a 2nd line that overlapped the sub-headline.
- Theme: design / QC (Stage 8 + 8q vision gate)
- Propagated to: knowledge/tuning/04_design.md Lessons (text-overlap = hard vision fail; qc_gate can't see it, so Read every PNG; prevention = white-space:nowrap + font sized to fit the container incl. emoji + >=40px gap between headline's lowest line and the sub); WORKFLOW.md §8q + .claude/skills/new-post/SKILL.md 8q (added "no text element overlapping another" as an explicit vision-QC line item, "Read every finished PNG").
- Change: ttc-02 Holicay slide rebuilt (headline 56px one-line white-space:nowrap, sub pushed to a clear gap below), re-delivered to Drive. Note: this is inherently a VISION check, not something the deterministic qc_gate.mjs can catch (it has no render/OCR); the durable fix is making the vision pass mandatory + explicit and the layout non-wrapping, not a new gate rule.

## design: follow whatever the post is derived from, not one baked-in template (2026-07-02)
- Feedback: (mid-batch on the Chloe 5-post run) "i want you to follow the design style of the inspo instead of having the same one which is baked in, over and over. do it from this post on." Refined same day: "not just follow inspo, follow what it should — if it referenced a previous post let's say ana tt-03 then follow the design from there; if it's from inspo then follow from there."
- Theme: design (Stage 8 overlay)
- Propagated to: knowledge/tuning/04_design.md Lessons (a post's on-slide design must follow whatever it's DERIVED FROM — mirror the Inspo row's design when built from an inspiration, or the referenced PRIOR POST's design when modeled on one, e.g. "make another like ana tt-03"; match font/casing/box-or-pill treatment/colours/placement/number of text blocks via a custom per-post build.js template or per-slide HTML through render.js; the engine templates are starting points, not the mandated look); memory design-mirror-the-inspo.md.
- Change: applied from ttc-03 onward in this batch — ttc-03 = inspo3's translucent grey rounded pills + casual system font + yellow-star authority cover; ttc-06 = inspo4's white-box cover/close + white centered numbered tips; ttc-07 = inspo5's bold white "DAY N / Area" dividers + white-card close. ttc-01/02 were already delivered before the steer, so they keep the earlier template look (not retro-fitted).

## design: no vignette on sourced photos (2026-07-07)
- Feedback: (on Hannah's LA slide tth-02 01_car "you kinda need a car") "the slides should stop having this dark overlay look around the edges of the photo, it makes it look so dull and unclear. no need regen, just write into playbook for future gens"
- Theme: design / realism (sourced-photo grade)
- Propagated to: engine/design/grade.py (removed the step-7 corner vignette in the canonical grade template, which is copied into every post's `_work/scripts/`); knowledge/tuning/04_design.md Lessons
- Change: the sourced-photo degrade no longer multiplies a corner-darkening vignette onto stock/real photos — they now stay bright + clear to the edges. The other camera-roll cues (imperfect exposure/WB, muted colour, soft grain, faint chroma, JPEG) are unchanged. Applies to all FUTURE posts; existing posts were NOT regenned, per the user.

## profile-pic realism: micro-expression + subtle skin imperfection (2026-07-07)
- Feedback: (human review of Hannah's 3 profile pictures) "1 and 3 is most realistic … what can be improved is micro expression and the skin … there should be super micro expression like slight scrunches. for skin, it should [not] look so perfect, there should be some blemishes, some sweat (if it makes sense), some environmental indicators … 1 works because she don't look as picture perfect, her skin, her, should be imperfect, humans are naturally imperfect … imperfection is perfection." (The sun flare, wind, shadowing, and hair were praised as already good for realism.)
- Theme: realism (persona / profile-pic gen)
- Propagated to: knowledge/realism/realism_book.md D1 (skin-realism, face/expression, avoid, clause) + §3 D1 pass-criteria + the failure-mode table (refined "Over-flawed", added "Picture-perfect"); knowledge/tuning/05_realism.md Lessons.
- Change: realism now REQUIRES a candid super-micro-expression (slight eye/nose scrunch, asymmetric almost-smile) and subtle, scene-scaled skin imperfection (one or two small blemishes, faint redness, hairline sweat, environmental indicators) on close/candid/profile shots — reframing the old "drop blemish words / do NOT add flaws" rule as a ban on HEAVY flaws (acne/scarring/uglification) only, not on subtle believable imperfection. Applied immediately by regenerating Chloe's 3 profile pics (1:1, same centered lower-two-thirds framing, real Tokyo background) with the new realism.

## tth-02 pills design: reproduce TikTok's native text faithfully (2026-07-08)
- Feedback: (on Hannah's LA pills post tth-02 02_area "pick ONE area per day") "i already commented in another thread on the dark tint especially around the edge, it being ugly and to stop doing that. but also this design is really ugly, because it grey, dull and boring. yes there's a lazy typing style, but that must be tiktok font and tiktok style of typing, this is neither tiktok style nor a nice style. you should follow the inspo or nice designs from past posts that worked. this looks like you tried to create one yourself. no need regen just note feedback be better in the next gen"
- Theme: design (Stage 8 overlay) — follow-the-source fidelity
- Propagated to: knowledge/tuning/04_design.md Lessons (reproduce a TikTok-native-text inspo faithfully — TikTok font + per-line hugging near-black pill with notched corners + scattered box rhythm; never a flat muddy-grey rounded box in a system font); this log.
- Change: NO regen (per user). Root cause: `pills` is NOT a canonical engine template (the engine ships only `lists`/`tips`/`hottakes`/`dividers`); it was hand-authored per-post for tth-02 to mirror inspo I007 (@babytaiyaki, `inspo/24/`) — the real TikTok text tool — but approximated it with a generic system-font grey slab (`-apple-system` sans + one flat `rgba(58,58,61,.5)` rounded rect) instead of the actual TikTok font + per-line hugging pill. Future TikTok-native-text mirrors must reproduce the specific treatment element-by-element. The dark-edge tint the user re-flagged is the corner vignette already removed 2026-07-07 in engine/design/grade.py; tth-02 was built Jul 3 (pre-fix) so its rendered slides still show it — not re-propagated.

## realism case-study batch: framing/pose > background > lighting > skin (2026-07-08)
- Feedback: (human graded 5 persona gens — LA full-body, Vegas "worth the hype", rooftop close-up, sunlight-squint, neon-street) with verdicts + reasons. 10/10 real (LA): full-body natural self-shot framing (3×3 col 2 rows 2–3), gaze away, imperfect real street (weeds, normal), sun direction readable + dappled uneven face shadow with light specks, natural outfit creases, flyaway strands catching light, not-close-up hides skin detail. Borderline-AI (Vegas): character/pose/framing right but background too perfect (no one/cars near her, far people/cars unresolvable, linear sky, all elements same brightness/saturation/hue). Super-AI'd (rooftop): studio lighting on a non-studio scene, too zoomed-in, awkward pose no one would strike, too-perfect skin + a Mei Tu Xiu Xiu beauty-filter sheen. Borderline-real (squint): great imperfect background+light, natural squint + forehead sweat + messy hair shadow, just make skin less perfect. Super-unreal (neon): environment not accounted for, unnatural pose for the context, too zoomed-in, too-perfect skin/face/body, linear lighting (only the eye-size asymmetry read real). Plus the general rule: use accessories (sunglasses/specs/cap/bandana/jewelry) to hide features when close-ups / the face won't pass; base refs are too perfect but we patch forward, not backward.
- Theme: realism (persona / cover / profile gen) + framing/pose + sourcing (imperfect background)
- Propagated to: knowledge/realism/realism_book.md (new **D6** framing/distance/pose; D2 imperfect-background & non-uniform-exposure lesson; D1 feature-asymmetry + Mei Tu beauty-filter tell + base-ref-check bullets & clause; D5 feature-hiding accessories; §2 prompt block; §3 OODA D6 + D1; failure table +5 rows; §5.6 base-ref check + D6); knowledge/tuning/05_realism.md Lessons (2026-07-08 full hierarchy + operational rules); knowledge/tuning/04_design.md Lessons (3×3-grid / zoom-out / gaze-away cover-framing cross-ref); memory realism-camera-native-framing.md (new) + realism-imperfection-microexpression.md (extended).
- Change: realism now leads with **framing + distance + pose** (zoom out; full/three-quarter; subject lower-center on the 3×3 grid; gaze away; pose fits the scene — no tight studio-portrait crops), then **imperfect non-linear background** (populate + dirty the scene, vary exposure/colour element-to-element; sourced → re-source, gen → ground + prompt), then **environment-driven subject lighting**, then **believably imperfect skin** (asymmetry, no Mei Tu whitening sheen, check base ref & patch forward). Accessories added as a feature-hiding fallback for unavoidable close-ups. Applies to all FUTURE gens; existing posts/base-refs NOT regenned (patch forward).

## realism case study: low-light mirror selfie — realism is a system, the tell is sheen not smoothness (2026-07-08)
- Feedback: (human graded a dim black-slip bedroom mirror selfie as real DESPITE perfect skin + symmetry) what carries it — lack of sheen / matte skin; "1080p not 4K" because a phone struggles in low light; pose natural for the mirror-selfie context; an ordinary (not perfectly-nice) bedroom; hand skin non-linear in colour (darker at the joints, variation in shine). "analyze what else you can ... this is despite perfect skin and symmetry."
- Theme: realism (persona / low-light / mirror-selfie) — light/exposure + skin finish + format
- Propagated to: knowledge/realism/realism_book.md (top "realism is a system / four ways to beat the skin-feature tell / smooth≠fake" note; D1 matte + non-linear-tone-incl-hands bullet + clause; new D2 "Low-light / dim-scene exposure lesson" + clause; D6 mirror-selfie high-realism-format bullet; failure table +2 rows [Over-clean low-light; Flat-tone/glossy skin & hands]); knowledge/tuning/05_realism.md Lessons (2026-07-08 low-light mirror-selfie); memory realism-imperfection-microexpression.md + realism-camera-native-framing.md (extended).
- Change: adds low-light degradation (crushed empty shadows, sensor noise, 1080p-not-4K softness, warm WB, no flash, exposure-dependent grain) as a top realism lever; reframes the skin tell as SHEEN + UNIFORM TONE + HYPER-RESOLUTION rather than smoothness (so clear/symmetric skin can pass); sets matte + non-linear tone (hands darker at joints) as near-universal minimums; codifies the four ways to defeat the skin/feature tell (imperfection / zoom-out / low-light / occlusion — need ENOUGH, not all); adds the mirror selfie as a lever-stacking format. Applies to future gens; nothing regenned.

## wardrobe: show neck/collarbone/shoulder/cleavage skin by default (2026-07-08)
- Feedback: "whenever character is gen, if possible with the wardrobe, showoff clevage with and shoulder, collarbone and neck skin."
- Theme: realism / wardrobe & styling (D5) — attract (R2)
- Propagated to: knowledge/realism/realism_book.md D5 (new "show upper-body skin at the neckline by default" bullet + clause); knowledge/tuning/05_realism.md Lessons; memory wardrobe-show-neckline-skin.md (new).
- Change: character/persona gens now DEFAULT to necklines/cuts that expose the neck, collarbone, shoulders, and a tasteful amount of cleavage when the outfit + scene allow (scoop/V-neck, cami straps, off-shoulder, open collar); pick the more skin-revealing believable option and favour wardrobe refs with these necklines. Stays tasteful/age-appropriate/scene-plausible (AGE + R1 absolute); NOT lingerie/swimwear (request-only); don't force against a genuinely covered look. Applies to future gens.

## realism dark-scene: subject exposed IN the dark + single-source directional falloff (2026-07-10)
- Feedback: (on a dark-scene character gen) "improve, not regen, the realism for darker scene generation. This looks ai because the scene is dark, but the model still looks so bright. secondly you need to take into account the light source … there's one bright light source in the top left corner of the photo, so the model should only have her left top side light up, the rest of her should be shadowed and abit darker. a iphone camera would also struggle to take photos in dark, so quality will be lower. this should not have passed qc."
- Theme: realism (persona / cover / dark-scene gen) — light & exposure (D2)
- Propagated to: knowledge/realism/realism_book.md D2 "Low-light / dim-scene exposure lesson" (two new leading bullets — subject-exposed-no-brighter-than-scene + one-dominant-source directional falloff; fixed the "brightest area near correct exposure" bullet to "whatever the light actually reaches"; extended the Clause) + §3 D2 pass criterion + failure table (new "Over-bright / flat-lit model in a dark scene" row); knowledge/tuning/05_realism.md Lessons [2026-07-10]; memory realism-imperfection-microexpression.md (low-light lever refinement) + qc-character-gen-before-ship.md (exposure bullet).
- Change: dark-scene realism now REQUIRES (1) the subject exposed no brighter than the scene — dark scene → she is dark too unless a real source physically lights her (kills the over-bright-model-on-dark-background tell), and (2) directional lighting from the single dominant source — only the planes facing it are lit, the rest fall into shadow with steep falloff (top-left source → upper-left lit, right side / front / legs shadowed), matching the source colour + shadow direction; reinforced that iPhone low-light quality loss (noise / softness / 1080p-not-4K) scales with how dark the scene is. Flagged as a must-QC play. Applies to FUTURE gens; the flagged output was NOT regenned (lesson only, per the user — "improve, not regen").

## realism skin: peach undertone + hold brightness down (not just "less smooth") (2026-07-10)
- Feedback: (on the Chloe sakura 1:1 profile pic) "the skin is too white and perfect, did i not write in the playbook to make her skin less smooth and perfect, have some blemishes, and the facial features not be super perfect, maybe one eye slight bigger, some asymmetry, and lastly i notice slightly more natural more peach (less white) and less brightness skin tone helps with realism. the pores also."
- Theme: realism (persona / profile-pic / derived gen) — surface texture + skin tone (D1); also a QC-discipline miss.
- Propagated to: knowledge/realism/realism_book.md D1 (new **Warm PEACH undertone + hold skin brightness DOWN** bullet; peach-undertone + expose-under + concrete "one eye a touch larger" added to the D1 Clause; failure-table "Beauty-filter skin (Mei Tu)" row extended to name the pale/over-bright cast + peach/under-expose fix); memory realism-imperfection-microexpression.md (peach/brightness lever) + qc-character-gen-before-ship.md (don't rationalize a flagged glow into a PASS).
- Change: the Mei-Tu/whitening tell has TWO halves the prompts were missing — a **pale white cast** and an **over-bright/luminous** face — on top of smoothness. Future gens now steer skin to a warm **peach/sun-kissed** undertone (not porcelain-white), **exposed slightly UNDER** (the face is not the brightest thing in the frame, no glow/bloom), with **clearly visible pores**, a couple of small blemishes, and **concrete feature asymmetry** (one eye slightly larger, one brow higher). Corollary added: a soft/overcast background renders skin more matte/natural than a bright golden wash, so prefer softer light when a gen keeps coming back too white. Process note: the sakura gen was FLAGGED as glowy in QC then shipped anyway — a flagged whitening tell is a REGEN, not a PASS. The sakura pfp was regenned; café + seaside kept (already matte/natural). Applies to future gens.

## realism LOCK-IN: the "dim + peach + muted whole-frame grade + random ground detail" recipe (2026-07-10)
- Feedback: (on the sakura v2 regen) "this new generation makes her look super realistic, lock this in make sure you dont miss it out again in next gen or in qc. it even makes the background look soso realistic theres so much detail thats random on the floor, the colours on the background also super super realistic, abit darker and all and whatever else you did please make sure we lock it in."
- Theme: realism (persona gen) — the "expose under" I applied for skin also fixed the BACKGROUND (whole-frame darker + muted colour + random ground detail). Lock the whole combination, not just the skin half.
- Propagated to: knowledge/realism/realism_book.md — D1 peach bullet (added **LOCKED**: apply expose-under FRAME-WIDE + muted non-punchy colour; it's what made the background read real too; bright/punchy/whitened frame = REGEN in gen AND QC); D2 imperfect-background lesson ("Populate + dirty" bullet → **random GROUND/FLOOR detail**; "Non-uniform exposure & colour" bullet → **grade the whole frame darker + muted, not punchy**); §2 pointer to the new reference. New file knowledge/realism/persona_gen_prompt_reference.md (exact proven SKIN + EXPOSURE/BACKGROUND blocks + QC gate). Memory: qc-character-gen-before-ship.md (+ whole-frame-under-expose + random-ground-detail + muted-colour QC checks), character-gen-real-sourced-background.md (+ ground-detail/muted-grade note), realism-imperfection-microexpression.md (frame-wide note).
- Change: the persona-gen DEFAULT look is now explicitly **dim + peach + matte skin + a slightly-under, muted (non-punchy) whole-frame grade + random uncontrolled ground/floor detail (scattered petals/leaves, dirt, worn grass, cracks, debris)** on top of the real sourced background she is lit BY. All three are QC gates; a flagged bright/punchy/whitened/clean-floor frame is a REGEN. Applies to all future gens.

## knowledge rule: Reddit = primary source of truth for guide content (2026-07-10)
- Feedback: "use reddit as primary source of truth (write this somewhere so future gen follows this)" (given while building the I011 shopping guides for Hannah / Ana / Mia).
- Theme: sourcing (content/venue research at Stage 6 — which venues/picks go in a guide; NOT photo sourcing)
- Propagated to: knowledge/tuning/02_copywriting.md (top principle rewritten so Reddit is the PRIMARY source of truth for factual list/guide content, blogs/Google/store-sites confirm-only; + dated Lessons entry); WORKFLOW.md §6 (research pointer strengthened to "Reddit first"); knowledge/platform/tiktok_style.md §5 (list-content research line → Reddit-primary); this log.
- Change: venue/list-content research is now Reddit-first by rule, **cross-checked with a second source** — pick the shops/venues/picks from real redditor opinion (authentic/controversial "netizens' real thoughts" + genuine gems + tourist-trap flags), then confirm each against a local guide + Google/Maps or the store's own site for existence + currency (Reddit alone has coverage/recency gaps). Carry over how people actually typed it (dovetails with the 2026-06-23 echo-the-phrasing lesson). Access note added: reddit.com is blocked to WebFetch, so use WebSearch + Reddit-aggregating guides or drive the CDP Chrome to raw threads. Refined 2026-07-10 after user clarified Reddit is wanted for real unfiltered opinion, mixed with a cross-check, not as a sole oracle. Applies to all future list/guide posts.

## practice: bank the VERBATIM winning gen prompts, not just the distilled rule (2026-07-11)
- Feedback: (on the Chloe sakura 1:1 pfp prompt, pasted in full) "can add this as a reference prompt for future generation. because this created something realistic. in the future, i want to save prompts written to image gen that generated very good outputs so it can be referenced. this is to help consistency."
- Theme: realism (persona / cover / derived gen) — process/consistency: keep a reusable library of proven full prompts, not only the abstracted recipe.
- Propagated to: NEW file knowledge/realism/winning_prompts.md (append-only library — the practice + reuse instructions + entry template + entry 01 = the Chloe sakura pfp prompt verbatim); knowledge/realism/persona_gen_prompt_reference.md (intro callout: rules here, verbatim winners there, bank every fresh win); knowledge/realism/realism_book.md §2 (pointer to the library beside the recipe); memory bank-winning-gen-prompts.md.
- Change: two-file split locked in — persona_gen_prompt_reference.md keeps the distilled **rules** (routed via propagate-feedback), winning_prompts.md keeps the **raw verbatim prompts that won** (append-only, newest on top, never rewrite a past prompt). New standing practice: whenever the human calls a gen output very good / super-realistic, copy the FULL prompt that produced it into winning_prompts.md; start future gens of the same deliverable/character from the closest banked winner and swap only refs/wardrobe/background/location, keeping the SKIN/EXPOSURE/COMPOSITION blocks intact. Seeded with the sakura pfp win. Applies going forward.

---

## ⎯⎯ ERA 2.0 — frameworks graduated (2026-07-23) ⎯⎯

The A/B/C1/C2 content frameworks graduated from the 1.0 `sandbox/frameworks-test/` into **the
production system** of this repo (Project Ana 2.0). This is an era divider, not a feedback item.

- **Everything ABOVE is 1.0-era historical context** — it records where past feedback propagated in
  the old system. Some of those target docs were **not ported to 2.0** (e.g. `04_design.md`,
  `funnels/funnel_skill.md`, and `WORKFLOW.md` stage numbers); the references stand as historical
  record. History is preserved, not rewritten.
- **New 2.0 feedback entries continue BELOW**, in the same entry format, newest at the bottom. The
  governing docs a 2.0 lesson can propagate to now live under `knowledge/` (frameworks/, realism/,
  voice/, brand/, platform/, tuning/) + `CONTRACT.md`.
