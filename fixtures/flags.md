# Copy extraction flags — Options A / B / C / D (Japan, Chloe)

For the human + a future fact-check pass. Everything quoted as "doc" = `../CREATIVE.md` (the content wheel).
Everything quoted as a post number ("09", "01", "08", "05", "02", "10") = that post's shipped, already-approved
copy under `outputs/`. Verbatim requirements (the Option A essay, both plug blocks, the C keyword plug, the D
favorites table) were checked programmatically word-for-word against the doc source — all match exactly.

**Follow-up pass (same session):** the coordinator asked for three edits after the first draft shipped — (1) fill
every C Kyoto/Nara/Hakone/Osaka `[needs copy — no mined source]` placeholder with drafted stand-in copy
(explicitly unapproved — see the loud section below), (2) append an optional save/ending slide to D.json so the
human can A/B it, and (3) normalize every `char_photo` slug to `chloe_cover`/`chloe_ending`. All three are done;
details inline below plus a dedicated DRAFT FILLS section. No `scenic_photo` values were touched, per instruction.

---

## A.json — fear of making mistakes

**Body copy = my condensation of the doc's own Caption essay example (Option A, Japan) into the 4-part
❌/✅ split formula.** Every number, name, and fact below is lifted unchanged from the essay; only the sentence
shape was compressed to fit the split template. Slide 2 (Narita/Haneda) is the one exception — the task asked
for the doc's worked-example **lines**, not just the wording, so I preserved its exact line breaks even though
two of them (`and $15 to $20 just to reach the city` = 38 chars) run past the ~34-char body-line guideline. Every
other split slide was freely re-broken to fit budget.

- **Slide 5 (no public trash cans → carry a small bag) is the one doc-sanctioned fill**, not from the essay —
  it's the shared-rules section's own resonance example ("having to carry your trash around in a plastic bag in
  Japan"). Flagged per the task brief's own instruction to flag it.
- **Slide 8 (hotels)** — essay names three alternative neighborhoods (Ikebukuro, Nippori, Kinshicho); the ✅
  title only fits two ("Try Ikebukuro or Nippori") for line-length reasons, Kinshicho is dropped from the
  *title* but the *why* line still says "Nippori or Kinshicho." Not contradictory, just compressed.
- **Photo gap**: slide 8's bottom_photo reuses the generic `neighbourhoods` asset as a stand-in for all three
  named neighborhoods (no single real photo can be all three). See places.json.
- Cover `title_lines` drops the leading ❌ (only `caption.title_line` keeps it) — see "Schema conventions" below.

## B.json — controversial takes

**Which take came from which shipped post** (task explicitly asked for this):

| Take | ❌ place | ✅ place | Source |
|---|---|---|---|
| 1 (slide 2) | Shibuya Sky | Tokyo Gov Building | **Doc's own verbatim worked example** (not a shipped post) |
| 2 (slide 3) | Shibuya Crossing | Shimokitazawa | ❌ from posts **09 + 01** (near-identical wording in both). ✅ **self-paired** — post 01 rates Shimokitazawa "WORTH IT" but never pairs it against the crossing in the source. |
| 3 (slide 5) | Takeshita Street | Cat Street | **Shipped-paired** — both posts **09 and 01** explicitly name Cat Street as Takeshita's alternative in their own captions. Cleanest take of the five. |
| 4 (slide 6) | Tokyo Skytree | Roppongi Hills / Mori Tower | ❌ from posts **09 + 01**. ✅ from post **05**'s day-4 Roppongi list — **but that shipped line compares Mori Tower against Shibuya Sky, not Skytree.** I substituted Skytree as the ❌ (also literally "OVERRATED" in both 09 and 01) so Take 4 wouldn't repeat Take 1's Gov Building payoff. **Flag for fact-check**: the "easier ticket, cheaper, less packed, closer view of Tokyo Tower" claim was shipped about Shibuya Sky vs Mori Tower, not Skytree vs Mori Tower. |
| 5 (slide 7) | 2hr Ichiran queue | Omoide Yokocho | ❌ from post **09** (which never names its own alternative — "i'll tell you where" is never paid off in the source). ✅ **self-paired** from post **05**'s day-2 Shinjuku list (yakitori, 150–300 yen/skewer). |

- Cover subtitle intentionally empty (doc's title-1 option has no subtitle).
- Slide 8 ("am I right? 🤷🏻‍♀️") subtitle intentionally empty — task brief says "no subtitle." (The sandbox's own
  test fixture invented "drop your take below" here; that's fixture test data, not sourced copy — not used.)
- Plug slide: restored the doc's deliberate misspellings **"alot"** and **"revisted"** exactly — the sandbox
  fixture had silently "corrected" both (and dropped "alot" entirely). Confirmed byte-verbatim against the doc.

## C.json — full-trip dump (Kyoto / Nara / Osaka / Hakone gap — NOW FILLED WITH DRAFTS, see loud section below)

**All five mining-source posts (09, 01, 08, 05, 02+10) are Tokyo-only, except post 10 which covers Osaka
shopping.** None of them mention Kyoto, Nara, or Hakone at all. The doc's D favorites-row table (reused here
per the task's explicit instruction to mine it) is the *only* sanctioned source for those three places, and it
gives just 3 terse place names each, with zero eat/matcha/nature/onsen content:

- Kyoto: Arashiyama, Fushimi Inari, Botanical Gardens
- Nara: deer park, Todaiji, Wakakusayama
- Hakone: shrine, Owakudani, glass museum

**Original pass (first draft):** per the task's "fill it ONLY from the mining sources... log every fill" rule, I
did not invent restaurant names, matcha cafes, nature spots, or onsen ryokans beyond those doc-given names — the
7 affected sections shipped as explicit `[needs copy — no mined source]` placeholders rather than fabricated
content.

**This follow-up pass:** the coordinator explicitly authorized drafting stand-in copy for those same 7 sections
(Kyoto eat + matcha, Osaka eat, Nara eat + nature, Hakone eat + onsen/nature) using real, well-known, first-timer-
recognizable picks, for design-density purposes. **Every single item this pass added is general knowledge, not
mined from any shipped post or the doc, and is explicitly unapproved** — see the loud DRAFT FILLS section
immediately below for the full per-city list and the fact-check flags on individual items. The placeholder text
is gone from C.json; nothing in the file reads `[needs copy]` anymore, but none of the new content should be
read as "sourced" the way the rest of this doc's flagged items are.

Other flags (unchanged from the original pass):
- **Osaka's third category = 🛍️ shop, not street food** — my call per the task's "your call from mined lists"
  instruction, made because post 10's `shop.json` has real, named Osaka store data (BIOTOP, Shinsaibashi PARCO,
  LUCUA Osaka, RAGTAG, KINJI BIGSTEP, Kindal Minamisenba, @cosme OSAKA, AINZ&TULPE) while no mined source names
  any Osaka street food.
- **Plug lands at slide 5, not slide 4** — Tokyo's listicle is rich enough (5 mined posts touch Tokyo) to spill
  across two notes slides (`contd:true`), which per the doc's own text ("keep the plug front/middle, ~slide 4,
  right after the first place's list, **even if that first list spilled**") pushes the plug to slide 5. Doc-
  sanctioned, not an error. Deck is 14 slides vs. the task brief's "~13" estimate for the same reason.
- **Tokyo's lists are curated, not exhaustive** — trimmed from a much larger mined pool (posts 02, 05, 08, 09,
  01 all touch Tokyo) to fit the ~10–12-line-per-slide budget. Left out: Yanaka, Daikanyama, Koenji, Nakano,
  Kagurazaka, Zojo-ji, Hie Shrine, Nezu Shrine, Kinokuniya, Aoyama Flower Market, Loft, BookOff, Flamingo,
  Chicago, Kindal, the full "day trips" list, and the free-viewpoints list beyond the Gov Building. All still
  available in the mining-source JSONs if a denser Tokyo slide is wanted later.
- Minor low-risk clarifications: "Nara deer park" (doc says just "deer park"); "the glass museum" for Hakone
  kept generic/unnamed in the copy itself per the doc's own terse wording (I inferred the likely real name,
  Hakone Glass no Mori, only for the *photo query* in places.json, not in the slide copy); "Universal Studios
  Japan" expands the doc's bare "Universal."

---

# ⚠️ DRAFT FILLS (UNAPPROVED, NEEDS HUMAN SIGN-OFF + FACT-CHECK) ⚠️

**None of the items below came from a mined post, the doc, or any other approved source. They are my own general
knowledge, drafted this follow-up pass specifically to make C's four thin places render at a believable design
density, per the coordinator's explicit request.** Every price, hour, "still operating," and exact-name claim in
here is **unverified** per the doc's own fact-check framework (§Sourcing the copy) — treat this whole block as
Step 1 (Draft) only, with Step 2 (Verify facts) not yet done. Do not ship any of it without a human pass. Items
are ordered exactly as they lead each section (3 most-famous-first, then up to 3 more), per the coordinator's
"resonance-first" instruction.

**Kyoto — 🍜 where to eat** (4 items, all drafted): Nishiki Market ("kyoto's kitchen, street food stalls") ·
Pontocho Alley ("riverside dining near gion") · a kaiseki dinner ("kyoto's multi course specialty") · yudofu in
Arashiyama ("simmered tofu, a kyoto classic").

**Kyoto — 🍵 where to matcha** (4 items, all drafted): Uji ("the matcha region, day trip from kyoto") · %
Arabica, Higashiyama ("the river view everyone posts") · Tsujiri, Gion ("matcha parfaits, expect a queue") ·
Nakamura Tokichi ("uji's famous matcha house"). *Fact-check flag:* confirm the Higashiyama %Arabica location and
the Tsujiri Gion branch are still operating before ship — cafe locations/openings turn over.

**Osaka — 🍜 where to eat** (4 items, all drafted): takoyaki on Dotonbori ("osaka's signature street food") ·
okonomiyaki ("the savory pancake, osaka style") · Kuromon Ichiba Market ("osaka's kitchen, stall hopping") ·
kushikatsu in Shinsekai ("fried skewers, no double dipping"). Lower risk than most of this block — these are
dish/area-level picks, not single named restaurants that could close.

**Nara — 🍜 where to eat** (4 items, all drafted): Nakatanidou mochi ("the rapid mochi pounding show") ·
kakinoha-zushi ("persimmon leaf wrapped sushi") · Naramachi ("the old merchant quarter, cafes and lunch") ·
Nara-zuke pickles ("sake lees pickled vegetables, a local souvenir"). *Fact-check flag:* Nakatanidou is a single
named shop (viral mochi-pounding performance) — confirm it's still operating and still doing the show before
ship; it's led the section because it's the most recognizable via social virality, ahead of the arguably more
"authentically Nara" kakinoha-zushi.

**Nara — 🏞️ nature** (3 items, all drafted): Kasugayama Primeval Forest ("untouched forest behind kasuga
taisha") · Yoshikien Garden ("a quiet traditional garden, often free") · Isuien Garden ("borrowed scenery of
todaiji in the background"). *Note:* inherently a deeper-cut section — Nara's headline nature draws (the deer,
Wakakusayama) are already claimed by the doc-sourced "places to visit" section, so these three are genuinely
lesser-known picks, not resonance-first in the way the other sections are. Flag for the human: consider whether
a deer-adjacent nature pick would resonate better even if it overlaps "places to visit."

**Hakone — 🍜 where to eat** (3 items, all drafted): kuro tamago at Owakudani ("the black eggs, said to add 7
years to your life") · soba noodles ("a hakone specialty, mountain buckwheat") · a ryokan kaiseki dinner ("multi
course, usually included with your stay"). The "adds 7 years" line is a well-known bit of Japan-travel trivia,
not a claim of fact — reads fine as voice, but flagging since it's a specific number.

**Hakone — ♨️ onsen + nature** (3 items, all drafted): Lake Ashi ("the pirate ship cruise, mount fuji views") ·
an onsen ryokan ("book one with a private outdoor bath") · the Hakone Ropeway ("volcanic steam vents from
above"). Lake Ashi and the Ropeway both revisit Owakudani/the lake conceptually already touched by "places to
visit" — expected overlap for a compact place like Hakone, not treated as a duplication problem.

**Total: 25 drafted line-items across 7 sections, 4 places.** All are real, genuinely well-known things (not
invented venues) — the flag is that their *inclusion, current operating status, and exact framing* have not been
verified against a primary source, per the doc's own two-step draft-then-verify rule.

## D.json — first-timers planning guide

- **⚠️ Slide 11 (save/ending) is OPTIONAL and NOT part of the doc's D table — appended this follow-up pass on
  the coordinator's explicit request.** The doc's D table is exactly 10 rows (cover + 9 content rows) ending at
  "7. Mobile data," with no save/ending slide defined anywhere in the D spec. It's rendered here purely so the
  human can A/B the ending-with-human-photo/nohuman-scenic-photo treatment consistently across all four options
  in this design test — **drop or adopt is entirely the human's call, this is not a recommendation to add a
  permanent ending to D.** Copy is a plain reuse: `title: "SAVE THIS"`, `subtitle: "just incase you need it
  ❤️"`, `char_photo: "chloe_ending"`, `scenic_photo: "fuji_lake"` — all four values copied exactly from A.json's
  save slide, per instruction. D.json is now 11 slides, not the doc's 10; every other D flag below still
  applies to slides 1–10 unchanged. (Original context, still true of slides 1–10: DESIGN.md's general
  test-definition line "render the cover and the ending slide in two variants... for each option" is written
  across all four options generically, but the renderer's actual dual-variant mechanism (`build.js`'s
  `TWO_VARIANT` set) is type-driven — only `cover`/`save` slides get rendered twice — which is why D had zero
  save-type slides before this pass.)
- **Step 2 (route)**: doc's literal string "tokyo 4 days · hakone 1 night · kyoto 3 · osaka 2" trimmed to
  "tokyo 4 · hakone 1 night · kyoto 3 · osaka 2" (dropped "days") to fit the line budget — matches the sandbox's
  own D fixture convention for this exact line. Meaning unchanged.
- **Step 2's route order/logic** ("loop west, never backtrack: tokyo → hakone → kyoto → osaka, nara = a day trip
  from kyoto") **is my construction**, not literally stated anywhere — the doc gives day-*counts* only, not the
  order. Built from standard Japan geography (matches the sandbox's own D fixture, which makes the same
  "Hakone & Nara = day trips" call). Flag for a geography sanity check before ship.
- **Step 1 (seasons)** month ranges ("Mar - May" etc.) are not from any mined source or the doc — added as
  standard Northern Hemisphere calendar quartiles (low-risk, objectively checkable), matching the sandbox
  fixture's own convention for this slide.
- **All 7 step pill labels** ("1. When to Go," "2. Route & Days," etc.) are my invented structural labels — the
  doc specifies each step's *content purpose*, never literal pill copy.
- **Step 4 (activities)** uses the doc's own literal example — Ghibli Park as the sell-out attraction, "miss the
  Shibuya Sky sunset slot, the night slots are still great" as the tip — per the task's explicit instruction to
  use "the Ghibli Park example." This diverges from the mined posts, which name teamLab (not Ghibli Park) as
  Tokyo's sell-out attraction; intentional per the task brief, not an error. `teamlab.jpg` already exists in the
  graded pool as an easy swap-back if the human prefers teamLab; `ghibli_park` needs fresh sourcing.
- **Step 7 (mobile data)** reuses the existing `golden_gai` asset as an approximate "neon street at night"
  backdrop per the doc's visual spec — thematically a stretch (a bar alley isn't really about eSIMs) but the
  only existing night-street shot in the pool. Flagged as a placeholder pick.
- **Favorites slide's 6 city groups** (Tokyo/Osaka/Kyoto/Nara/Nagoya/Hakone) are copied verbatim from the doc's
  own D table favorites row, per the task's explicit instruction. Nagoya appears here even though it's not one
  of C's five places — that's correct, the doc's table includes Nagoya specifically for D's favorites slide.
- Per the doc's "Note on the insert," no "see next slide" teaser was written into the activities slide (nothing
  to soften — none was drafted in the first place, since the plug now sits before favorites, not after
  activities).

---

## Captions — B, C, D body_draft are DRAFTS, not approved copy

Only **A's `caption.body_draft`** is approved copy — it's the doc's own Caption essay example, verified
word-for-word verbatim against the source. **B, C, and D's `caption.body_draft` are fresh copywriting I wrote
for this pass**, one paragraph per major beat, in the same register as the A essay. Per the task brief these are
explicitly secondary to the design round — flagging clearly so they aren't mistaken for pre-approved copy the
way the slide/plug text is. C's caption additionally follows the doc's stated exception: the keyword CTA
(`comment "JAPAN" and i'll send you the full itinerary`) is the literal first line of the body, ahead of the
essay, per the doc's C caption-exception rule.

## Schema conventions inferred from the sandbox's fixtures/build.js (not spelled out in DESIGN.md itself)

DESIGN.md's `copy JSON schema` section is abstract; `sandbox/frameworks-test/fixtures/*.json` and
`build.js`'s `TEMPLATES` show the concrete field shapes in practice, so those were treated as authoritative
whenever the two diverged in specificity (the fixtures' actual *wording*, however, was never trusted — see
"alot"/"revisted" above; only their *structure* was reused):

- The FLAG emoji never sits in `title_lines` — it is always the cover's separate `"flag"` field (bare
  peeking render). A leading **❌** is different: when the hook title itself starts with ❌ (A's option-1
  title), the ❌ IS part of `title_lines` (see `fixtures/A.json` slide 1) and `caption.title_line` carries
  it too. (Corrected 2026-07-23 — an earlier version of this bullet wrongly claimed ❌ never appears in
  `title_lines`.)
- `save.title` / `save.subtitle` and `divider.label` are plain strings, not line arrays (per DESIGN.md's own
  schema line and the fixtures).
- `notes` item objects are `{text, gloss?}` plain strings, **not** pre-broken `lines[]` — the FORMAT RULES
  "every text field is pre-broken into lines" instruction was applied only to fields that are arrays per the
  DESIGN.md schema (title_lines, why_lines, paragraphs, blocks[].lines, cities[].lines, etc.), not to the notes
  item text/gloss or to pill/label strings, matching how `build.js`'s `notes()` template actually consumes them.
- `TWO_VARIANT` (dual human/nohuman render) is driven by slide **type** (`cover`, `save`), not slide position —
  relevant to the D "no ending slide" note above.

If the human's mental model of the schema differs from the fixtures here, these are the first places a mismatch
would surface when `build.js` runs against these files.

## Line-break QC

Ran an automated ≤24-char-title / ≤34-char-body / no-orphan-single-word-line check across all four files.
Two genuine issues were fixed: B's "✅ Go to the Tokyo Gov Building" title reflowed to two lines; D's route
headline trimmed ("tokyo 4 days ·" → "tokyo 4 ·"). The checker also flagged several **false positives** that
were left as-is because they match the sandbox fixtures' own established pattern of one name/word per line in a
stacked list or an emphasis word getting its own line (not an accidental orphan): B's cover "UNDERRATED" alone
on a line, D's season names (Spring/Summer/Autumn/Winter) alone on their label line, and D's favorites-slide
venue names (Teamlab, Sensoji, Dotonbori, etc.) one per line.

## Char photo normalization (follow-up pass, item 3)

Checked every `char_photo` field across all four files against the coordinator's request (cover slides →
`chloe_cover`, save slides → `chloe_ending`, matching the final picks now in `chars/`). **Result: already
consistent from the original pass — zero fields needed changing.** All cover slides (A/B/C/D) already used
`"chloe_cover"`; all save slides (A/B/C, plus the new D slide 11 above) already used `"chloe_ending"`; nothing
anywhere referenced `chloe_fixture` (the renderer-test-only asset). Slugs are kept extension-less
(`"chloe_cover"`, not `"chloe_cover.png"`) to match every other photo reference in these files — `build.js`'s
`resolveIn()` appends the file extension itself, and writing it inline would be inconsistent with `fuji_lake`,
`tokyo_skyline`, and every other slug in the schema (it would still *work*, since `resolveIn` special-cases
strings that already end in an image extension, but it would be the only slug in the file written that way). No
`scenic_photo` value was touched anywhere, per instruction.

## Photo sourcing — see places.json for the full slot-by-slot plan

61 photo slots logged across all four decks. Headline numbers: **37 need fresh sourcing**, **2** (Shibuya Sky,
Tokyo Gov Building) just need an OODA-pick + grade from candidates already sitting in
`media/library/japan-tokyo/` (no fresh sourcing pass needed), **15** slots reuse assets already graded in the
sandbox pool, and **7** existing graded assets (`areas`, `coffee`, `cute_stores`, `thrift`, `teamlab`,
`icon_deepl`, `icon_gtrans`) ended up unused by this draft. **Kyoto, Nara, and Osaka have zero existing photo
coverage** in the sandbox pool (Hakone has 1 of its 4 divider cells covered by the existing `hakone.jpg`) — this
mirrors the copy-sourcing gap almost exactly: the same three-to-four places are thin on both text and photos,
for the same underlying reason (the five mining posts never went there).
