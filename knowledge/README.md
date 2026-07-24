# knowledge/ — the agent's brains (frameworks + craft + tuning)

These docs are the agent's strategy, voice, realism, and brand judgment for building framework posts.
The **spine is the repo-root [`CREATIVE.md`](../CREATIVE.md) (content wheel) + [`DESIGN.md`](../DESIGN.md)
(visual/build spec)** — together they own the A/B/C/D blueprints and the durable output spec. Everything else here is supporting craft the build
stages load as needed. The human's review feedback tunes these docs through the `propagate-feedback`
skill; the `dream-cycle` skill mines the agent's own artifacts for more.

| Doc / dir | What it owns |
|---|---|
| [`../CREATIVE.md`](../CREATIVE.md) *(repo root)* | **the content spine** — the A/B/C/D carousel blueprints: hook titles, slide maps, the Holicay plug copy, the hashtag + essay-caption formula, voice + photo direction. Visual / type / plug authority = [`../DESIGN.md`](../DESIGN.md) |
| [`frameworks/photo_sourcing.md`](frameworks/photo_sourcing.md) | the **design rationale** for the real-UGC body photos — library keying, manifest schema, rights posture. Implementation = `engine/source/brightdata.py` (+ `engine/source/SOURCING_STATUS.md` for live status) |
| ~~copy-bank~~ *(retired)* | the old per-country copy-angle files are gone — freshness now comes from scanning past posts' own `copy.json` under `outputs/<char>/*/` |
| [`realism/`](realism/) | the **character-in-photo craft** — `realism_book.md` (believability rules), `persona_gen_prompt_reference.md` (the proven gen recipe), `winning_prompts.md` (verbatim winning prompts) |
| [`voice/humanizer.md`](voice/humanizer.md) | anti-AI-tell **voice rules** — short, story-first, real specifics, straight quotes, no em/en dashes |
| [`brand/holicay_brand.md`](brand/holicay_brand.md) | what Holicay is + how to name a use case — **the standing brand reference** (human-maintained; no Sheet tab feeds it) |
| [`platform/tiktok_style.md`](platform/tiktok_style.md) | **platform voice + strategy only** (trimmed) — `CREATIVE.md` + `DESIGN.md` own design; this keeps the "real person's phone" snapshot + the subject / logo / facts / research notes that still apply |
| [`tuning/01_analysis.md`](tuning/01_analysis.md) … [`05_realism.md`](tuning/05_realism.md) | **per-stage lessons** the feedback loop writes — analysis · copywriting · sourcing · realism (no `04`; on-slide design is owned by `CREATIVE.md` + `DESIGN.md`) |
| [`tuning/06_performance.md`](tuning/06_performance.md) | **performance memory** — auto-written by the `analyze` skill from Sheet stats, read by `generate-post` before it writes copy |
| [`tuning/propagation-log.md`](tuning/propagation-log.md) | **append-only audit** — every feedback item, its classification, the doc it propagated to. Newest at the bottom; never rewrite history |

**One source of truth per lesson.** A lesson lives in exactly ONE of these docs — cross-reference it,
never duplicate it. When you learn something durable, sharpen the existing bullet rather than appending
a near-twin. That is the same DRY discipline the frameworks apply to the design spec.

**Where feedback goes.** The `propagate-feedback` skill routes each GREEN cell on the Sheet into the
single governing doc that controls all future posts, logs the edit in `tuning/propagation-log.md`, and
clears the cell. `dream-cycle` mines the agent's artifacts for recurring, performance-backed lessons
and proposes edits for human approval.
