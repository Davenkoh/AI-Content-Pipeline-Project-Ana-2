# Tuning — Stage 8 (photo sourcing)

**Read this before sourcing photos.** Feedback about wrong/ugly/too-clean frames,
wrong subjects, or watermarks lands here.

## Principles
- **Target = composed-candid:** the subject is the attractively-framed hero AND the
  background is genuine, uncontrolled real life. Reject all three failure shapes:
  studio-clean, random-ugly, and fake-prop staged.
- **Hierarchy (framework body photos, per `DESIGN.md` Gate 9):** Google Places user photos
  (prioritized) → Instagram via Apify → SerpAPI Google Images (native-language + context
  modifiers); Pexels/Unsplash only when the shot genuinely reads candid. Tool:
  `engine/source/brightdata.py`. (Persona BACKGROUNDS invert — Pexels/Unsplash first; see
  `../realism/realism_book.md` §5.9.)
- **Build contact sheets, then pick the most *contextual* frame, not the prettiest.**
  High quality is not always good — a clean stock photo is worse than a real phone snap.
- **Verify the subject is literally correct** — right dish/drink/place, no competitor
  branding, no baked-in on-photo text or banners.
- **Source by real venue name** for "things to do / must-eat" posts (e.g. the specific
  café/restaurant), so you get real customer/UGC photos, not generic stock.
- **Real app/brand logos via the iTunes Search API**, never emoji stand-ins; eyeball the
  verify sheet (a keyword miss grabs the wrong app).

## Lessons (append-only; newest at bottom)
- For text-backdrop slides the photo is a backdrop (subject can sit lower, top stays calm
  for text) — resolution matters less, but pick bright/inviting over dark/moody when the
  copy is meant to entice.
- Patch baked-in watermarks AFTER grading (grade regenerates from source and wipes patches).
