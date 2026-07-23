---
name: new-character
description: Stand up a new digital-influencer character end to end — registry entry, locked visual identity (Base References), Sheet tab + Drive folder, and her framework scene photos (chars/<key>_cover.png + <key>_ending.png). Use when the user says "create a new character/profile/persona" (e.g. "create a new profile, call it Priya, India content"). After this, generate-post can post as her.
---

# Create a New Character

Stands up a new character end to end; after this the `generate-post` pipeline can post as her.

A character in 2.0 is **four things** — no personality or makeup text files:
1. a **registry entry** in `state.json` (name + country + id prefix + TikTok @handle),
2. a locked **visual identity** = a few reference images with her signature look **baked in**
   (`character/<Name>/Base References/`),
3. a **Sheet tab** + **Drive folder** (created from the registry), and
4. her **framework scene photos** — `chars/<key>_cover.png` + `chars/<key>_ending.png` — the clean
   character-in-scene shots the renderer lays cover/ending text over (**new in 2.0** — the human-variant
   decks need these).

She is a **general digital influencer**; the country is only her *default subject*. The look lives in the
images, so once the hero is locked you never describe her again.

> Example trigger: *"create a new profile, call it Priya, India content."* → run this top to bottom.

## Touches
- **Knowledge:** `knowledge/realism/realism_book.md` (the image-gen realism layer, D1–D6 + §5.9 real
  background), `knowledge/realism/persona_gen_prompt_reference.md` (the locked recipe),
  `knowledge/realism/winning_prompts.md` (reuse the closest banked winner).
- **Engine:** `engine/setup/provision.py create` (idempotent Drive subfolders), `engine/drive/drive_sync.py
  --mirror` (push refs), `engine/sheets/sheets.py init` + `dashboard-init`, the persona-gen chain
  (`prep_cover_refs.py` → `gpt_prep.js` → `gpt_send.js` → `gpt_grab.js` / `gen_base_ref.js`).
- **State:** a `characters` entry in `state.json` (no counter to seed — `next-slot` derives her numbering).

## Input
- **Name** (e.g. `Priya`) + **default content country** (e.g. `India`) + a short unambiguous **id_prefix**.
- **TikTok @handle** if the account exists yet (else leave `""` — like Hannah — and register it later).
- **Look direction** — the one creative choice: her ethnicity / aesthetic (optionally drop a couple of
  reference images of the vibe). Everything else stays open.

## 1 · Register the character (`state.json`)
Add a `characters` entry (no counter to seed — `next-slot` derives her rotation + numbering from her tab):
```jsonc
"characters": {
  ...
  "priya": { "name": "Priya", "id_prefix": "ttp", "country": "India", "tiktok": "" }
}
```
- **`id_prefix`** — short, signals tiktok + the character, unambiguous from the others (Ana `tt`, Chloe
  `ttc`, Hannah `tth`). Post ids become `<prefix>-NN`; the trailing `-` keeps `tt`/`ttc`/`tth` apart.
- **`country`** — her default subject. **`tiktok`** — her @handle (used by `scrape-stats`); `""` until the
  account exists.

`sheets.py` / `drive_sync.py` / `provision.py` / the cover scripts / the skills all read this registry —
nothing else needs editing to introduce her.

## 2 · Generate her locked visual identity → `character/<Name>/Base References/`
Goal: a few reference images with her face **and signature makeup BAKED IN**, so every downstream gen
inherits the look automatically.

**Capture convention (every base shot):** front-on agency test-shot, plain neutral **grey** background,
fitted **white ribbed tank**, **85mm** soft beauty light, **editorial realism — NOT phone-degraded**. Keep
skin real: pores, texture, **no waxy/plastic sheen**.

**House aesthetic (the default EVERY character inherits — keep it consistent)** so the whole roster reads
as one brand of influencer:
- **Makeup — K-idol clean-glam:** dewy glowy "glass" skin (real texture still visible, not a mask), a soft
  rosy **"drunk blush"** high under the eyes and across the cheeks/nose, soft straight groomed brows, soft
  neutral-brown eyeshadow with a subtle slightly **down-turned "puppy" liner**, brightened inner corners +
  a gentle **aegyo-sal**, defined natural lashes, and a **glossy nude-rosy / soft-coral lip**. Fresh,
  pretty, effortless — not heavy, not matte.
- **Body + bust:** slim, healthy, well-proportioned; a natural **~B-cup** bust, subtly accentuated with a
  light push-up look (tasteful, body-conscious fit).
- **Hair + accessories:** long, sleek, dark hair, center part with soft face-framing strands; dainty
  **gold jewelry** (fine layered necklace, small earrings).
- **What varies per character:** only her **face / ethnicity** (the `[LOOK]`) + name + country. The makeup,
  body, bust, hair, and glam level stay constant.

### a · HERO — locks the identity (do FIRST; strictest gate)
The house aesthetic is already baked into the template — normally you change only `[LOOK]`:
```
Editorial agency test-shot, full-resolution studio portrait of a stunning, conventionally attractive
25-year-old [LOOK — e.g. "East-Asian, K-pop-idol aesthetic"] woman — clearly an adult in her mid-20s,
never reads younger. Refined symmetric-leaning idol features, big expressive soft eyes, healthy radiant
glow, a slim well-proportioned figure with a natural B-cup bust subtly accentuated with a light push-up
look (tasteful, body-conscious fit). Long sleek dark hair, center part with soft face-framing strands.
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
identity-defining beauty marks, realistic high-point sheen without glow, loose flyaways and baby hairs;
hair shows strand separation and soft real shine, not a CG sheet. No airbrushing, no waxy or plastic
sheen, no over-smoothing. Photorealistic editorial realism — a real unretouched agency test shot, not AI.
```
**Gate it (OODA — the strictest gate in the system).** Generate ~4 candidates; score each **in this
order**: `AGE (reads 21+) → REAL (no AI/plastic tell) → ATTRACTIVE`. Pick the best and **LOCK** it. Age is
a kill-switch: if any reads under 21, regen — **never "try younger."** Do not re-roll the face after locking.

### b · FACE-CLOSEUP (+ optional HALF-FRONT) — *attach the locked hero*
They inherit the face + makeup; don't re-describe the look.
```
[FACE-CLOSEUP] Same woman from the attached reference image — identical face and identity, same skin
tone. Macro beauty close-up of her face filling the frame, front-on. 100mm macro lens, soft even light.
Maximum skin/eye fidelity: visible pores, real texture, the same beauty marks, realistic catchlights,
eyelash + iris detail. Plain neutral grey background. No airbrushing, no waxy sheen, no over-smoothing.
Photorealistic editorial realism, real unretouched person, not AI.
```
Optionally add a **HALF-FRONT** (waist-up, same tank + jeans) and a few angles (3q-left / 3q-right / one
smile-with-teeth) by attaching the locked hero and **changing ONE thing per shot**. Batch angles as a 2×2
sheet to save gens; keep hero + closeup solo / full-res.

### Save (filename just needs the role keyword — matching is lenient)
`prep_cover_refs.py` picks files out of `Base References/` by the keywords **hero · closeup · half**, so
`Priya_01_hero-front.png`, `close up.png`, `half body.png` all work. **Minimum to run the pipeline = a
hero + a closeup.**

## 3 · Provision her Drive folders + push her references
`provision.py create` is **idempotent** and creates any missing character's `Base References /
Profile Pictures / Tiktok` subfolders under the Drive root (it iterates the registry), so a re-run picks
her up:
```bash
python3 engine/setup/provision.py create
python3 engine/drive/drive_sync.py --mirror "character/<Name>" --dest "<Name>"     # push her (gitignored) refs
```
(Per-leaf `--mirror` also works if you only want to push one folder.)

## 4 · Create her Sheet tab
```bash
python3 engine/sheets/sheets.py init             # idempotent — builds the <Name> fact tab from the registry
python3 engine/sheets/sheets.py dashboard-init   # re-run so the Dashboard picks up her new tab
```

## 5 · Generate her framework scene photos → `chars/<key>_cover.png` + `chars/<key>_ending.png` (NEW)
The **human-variant** A / B / C1 decks lay the hook title over a candid **cover** scene and the "SAVE THIS"
over a candid **ending** scene. Generate both **before her first human-variant post** (this is the
`generate-post` §3 blocker):
- Use the **§5.9 real-background method** (`realism_book.md`) — give GPT a **real sourced background**
  (Pexels/Unsplash first) of a spot that fits her country, and place her INTO it (do NOT invent, do NOT
  composite), lit BY that scene.
- Follow the **locked recipe** (`persona_gen_prompt_reference.md`): SKIN block first (peach undertone,
  expose under, matte, visible pores, asymmetry), whole-frame dim + muted grade, random ground detail;
  reuse the closest banked winner from `winning_prompts.md`.
- QC against `realism_book.md` D1–D6 (a FLAG is a REGEN, not a pass). Save clean (no text) as
  `chars/<key>_cover.png` and `chars/<key>_ending.png`, then `python3 engine/qc/sync_media.py`.
- **Persona-gen reliability:** warm + prep + send in ONE bash call (the Stop hook quits Chrome each turn);
  sequential gens share one ChatGPT conversation, so grab the LAST big image; `bash
  engine/lib/quit_chrome.sh` when done.

## Done
She is live. Build posts with `generate-post --character <key>` — the rotation derives her framework +
variant, the cover gen reads her Base References (`MASQ_PERSONA=<Name>`), and her `chars/` scene photos
carry the human-variant cover/ending.

---

## Faceless variant (no face)
**2.0 has no `"faceless": true` character flag** (that was a 1.0 feature — the engine here reads only
name / id_prefix / country / tiktok). In 2.0, "faceless" is a **framework property, not a character
property**: **C2 is faceless by spec**, and the **`nohuman` variant** of A / B / C1 shows no person on the
cover/ending either. So to run an account facelessly, register her (§1) + create her tab (§4), **skip §2
and §5** (no Base References, no `chars/` scene photos), and ship only her **`nohuman` / C2** slots — her
decks build from real location/food UGC + the render templates, never the persona/cover-gen path. Caveat:
the rotation still *proposes* `human` slots for her (A/B/C1 default human), and a `human` slot with no
`chars/<key>_cover.png` is blocked (`generate-post` §3) — so either treat her human slots as nohuman or
give her the scene photos after all. Flag this to the human rather than papering over it.

## The rules that keep her consistent
- **AGE 21+ is absolute** (kill-switch). Precedence when criteria conflict:
  `AGE > REAL > IDENTITY-CONSISTENT > ATTRACTIVE` — never trade realism or identity for beauty, never
  trade anything for age.
- **Lock the hero, then re-anchor to it** — every later shot references the *locked file*, never the
  previous output, or the face drifts.
- **One variable per gen** — change angle OR expression OR framing, never several.
- **Don't over-collect** — hero + closeup run the pipeline; add angles only for a real downstream need.
- **Realism guardrail** — dewy / "glass-skin" makeup is the fastest path back to the waxy-AI look; always
  keep `real texture, no over-smoothing` in the prompt. The base library is **editorial**.
