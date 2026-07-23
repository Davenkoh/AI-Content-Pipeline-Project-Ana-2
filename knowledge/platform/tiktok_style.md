# TikTok Post Skill

How to make a character static carousel for **TikTok** (Ana or Chloe — the active character selects the persona refs + subject). The shared build engine is the repo-root `../../WORKFLOW.md` (read it for the full end-to-end pipeline). This skill holds what is **TikTok-specific**: platform snapshot, the lazy "Classic" visual style, content types/formats, and strategy. The **shared mechanics** (canvas + safe zone, photo sourcing, grade=degrade, ChatGPT cover gen over CDP, the HTML→PNG render engine, character/wardrobe identity, file hygiene, OODA checkpoints) live in `../../WORKFLOW.md` — don't duplicate them here.

---

## 1. Platform snapshot

- The whole point: it reads as a **real person's phone, not a brand.** Two rules above everything: pick **messy real frames**, and **never let anything look polished or designed.** When in doubt, make it rougher.
- A TikTok carousel = swipeable static images; the **cover hook + first slide** carry the swipe. Caption is short and casual.
- The active character sets the subject default: **Ana** is based in Vietnam (subject defaults to **Vietnam**); **Chloe** is based in Japan (subject defaults to **Japan**). The character is a general digital influencer — content can be anything that works for the format; the **country** (from `state.json` → `characters`) is only the default subject.

## 2. Inputs

- **Inspo**: `inspo/<n>/` — the reference post(s) the user points at. Copy THAT post's text style + energy; do not invent a "tasteful" version. Pull a fresh one from a TikTok link: `node "engine/scrape/tiktok_carousel.js" "<url>"` (drives the CDP Chrome, files the slides to the next free `inspo/<N>/`; playbook §0.5).
- **Wardrobe + character refs**: `character/<Name>/Base References/` (per character) + the shared `character/_shared/Wardrobe References/` per the playbook. Identity comes from the reference photos, never from demographic words in a prompt (playbook §4).

## 3. Visual style — lazy TikTok "Classic"

- **Font**: TikTok "Classic" ≈ Proxima Nova → we use **Montserrat** (Google Fonts). White fill, **subtle soft drop shadow only** — no box, no band, no gradient bar, no wordmark, no slide counter. Weights ~700 slides / ~800 cover.
- **Lazy lowercase = the creator's voice**; local names typed fast with **no diacritics**. Casing is voice, layout is the inspo (copy the inspo's font/alignment/weight/placement, but keep the words in her voice).
- It must look **"typed in the TikTok app," not designed.** This is the single most-corrected thing here — err plainer and rougher.
## 4. Content types / formats (re-derive from the inspo every time)

TikTok references are different *kinds* of carousel. Read the cover + 2-3 body slides, then build to match:
- **item / street-food list** — each slide = one item: `N) name` + a tiny English gloss. Cover = ALL-CAPS headline at top.
- **travel-tips paragraph** — each slide = a bold headline + an explanatory paragraph, centered white over a backdrop photo + soft scrim. Cover = sentence headline mid-frame + a parenthetical sub.
- **multi-city itinerary** — scenic-quote cover → per-city 2x2 photo-collage divider → notes-app text-list slides.
- **overrated / underrated hot-takes** — GPT street-selfie cover + per-place verdict over the place photo.
- **first-person storytime** — lowercase hook cover → narrative beats → comment-for-itinerary CTA.
- **chaos-compilation / culture-shock storytime** — a "things that shocked me when i moved to [place]" or "everything that went wrong" oversharing listicle (mirrors @lunapigeonk, Inspo/10): character cover with a black-text-on-white-box hook + a lighter italic sub → each body slide is a SEPARATE candid graded photo + ONE **short, COMPLETE, humanized one-paragraph** beat. Keep beats **realistic with a wow factor but nothing too crazy** — relatable culture-shock (the auntie who walks you across the street, the $2 meal, what fits on one motorbike) beats a shocking-crime reel (the user rejected a sensational scam cut as "obviously fake, not complete"). Ground them in real common experiences; place text over a calm/dark zone or use a `grad` top wash on bright daytime shots. Optional comment-to-DM list close (cat 5). `build_story.js`.
- **recommendations guide** — character cover + category-header slides with a short venue list under each.
- **card-format guide** — frosted real-icon app grid + white info cards (regions / islands / tips) + a Holicay feature slide.
- **IG-stories photo-dump** — "my IG stories in [place]" cover → 3x3 IG "stories archive" grids → comment-to-DM closing.
- **things-you-must-do experiences guide** — a candid character cover with a HUGE place-name headline ("things you must do in [place]") → per-experience photo collages (flush 2x2 or 1+2 cells, `build_collage.js`), each with a 📍 + lowercase action label + a parenthetical personal rec centered on the middle seam over a soft wash → optional comment-to-DM closing. Research the real venues (parallel subagents) so each pick is specific + save-worthy; pick a calm/dark center where the cells meet so the white label reads.

Always re-derive the model from the actual inspo before coding; don't assume a format.

## 5. Strategy

- **Subject defaults to the active character's country** (Ana → Vietnam, Chloe → Japan) — localize a foreign-country inspo to that country (content, backdrops, app list) unless the user explicitly asks for another country. Speak as a local ("from someone who lives here").
- **Holicay** only when a funnel genuinely fits, subtle, surrounded by real value — funnels in `knowledge/funnels/funnel_skill.md` (F1 Trust Builder / F2 Honest Mention / F3 DM Magnet / F4 Soft Demo / F5 Decoy Reveal). One light touch per post (F4 and F5 are the exceptions — the app is the earned payoff).
- **Real brand/app logos**, never emoji stand-ins (iTunes Search API; `fetch_app_icons.py`; eyeball the verify sheet, a keyword miss grabs the wrong app).
- **Don't assert unverifiable facts** in copy (no invented posting cadence, prices, or dates).
- **Research list content with parallel subagents** (**Reddit-primary** = the source of truth; blog/Google confirm-only; flag traps + tourist-trap-vs-better swaps) — that consensus is what makes a guide save-worthy.
- Run **all** copy through `Humanizer.md`: no em/en dashes anywhere, straight quotes, a short sweet caption.

## 6. Build + deliver

- Build through the playbook engine: source → grade (degrade) → patch watermarks → overlay text → character cover via CDP → assemble + QC → caption → deliver.
- **Output**: `outputs/NN - Title Case Name/` with `_work/` + `final/` + `caption.txt`; **local folder names match Drive.** Deliver to Drive `…/<Character>/Tiktok/NN - Title Case Name/` flat (sequential `00_cover.png` … + `caption.txt`). **Drop the `(Filler)` suffix** when a post promotes Holicay or is a hero storytime. The canonical Playwright install lives at `engine/node_modules`.
- Canvas **1080×1440 (3:4)**, centered text, a light ~80px edge buffer (no heavy margins) so TikTok's UI chrome doesn't clip the copy. Re-derive exact sizing from the reference post.

## 7. Lessons (append-only)

The cross-format lessons now live in the per-stage tuning files `../tuning/` (`01_analysis` … `05_realism`) — Vietnam/subject defaults, real logos, full-bleed covers, two-gen end-slides, Holicay discipline, research-with-subagents, Humanizer-on-every-slide, no-unverifiable-facts, deliver-clean. Add new lessons there (the feedback loop writes to them).

## 8. Status

TikTok posts **01-13** delivered in `outputs/` (local + Drive). Post 11 ("How I Plan a Trip") is the first **cat 4 process / soft-demo** post (community-itineraries). Post 13 ("How I Plan With AI") is the first **cat 6 decoy guide funnel**: a decoy "best places in [place]" cover (real creator + the searched-for listicle) → 1-2 value collage slides → reveal Holi-AI (guided form + canvas) → soft close. It NAMES Holi-AI/Holicay at the reveal, and is country / content / character agnostic. Post 12 ("Things That Shocked Me in Vietnam") is the first **culture-shock storytime** + first **cat 5 storytime → soft list DM funnel** (short, complete, realistic culture-shock beats — an American who moved to Saigon and *looks* local but isn't; closing keyword "saigon"). NOTE: a first sensational scam-beat cut was rejected by the user as fake/incomplete and as wrongly calling Ana Vietnamese — storytime beats must be short, complete, humanized, realistic (wow but not crazy), and Ana is American-born, not a fluent local. This skill plus the playbook are canonical for new TikTok posts.
