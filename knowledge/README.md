# knowledge/ — the agent's brains (frameworks + craft + tuning)

These docs are the agent's strategy, voice, realism, and brand judgment for building framework posts.
The **spine is `frameworks/` + the repo-root [`CONTRACT.md`](../CONTRACT.md)** — together they own the
A/B/C1/C2 blueprints and the durable output spec. Everything else here is supporting craft the build
stages load as needed. The human's review feedback tunes these docs through the `propagate-feedback`
skill; the `dream-cycle` skill mines the agent's own artifacts for more.

| Doc / dir | What it owns |
|---|---|
| [`frameworks/content_frameworks.md`](frameworks/content_frameworks.md) | **the spine** — the A/B/C1/C2 carousel blueprints: hook titles, slide maps, the Holicay plug copy, the hashtag + essay-caption formula, and the on-slide design. Design / type / plug authority = [`../CONTRACT.md`](../CONTRACT.md) |
| [`frameworks/photo_sourcing.md`](frameworks/photo_sourcing.md) | the **design rationale** for the real-UGC body photos — library keying, manifest schema, rights posture. Implementation = `engine/source/brightdata.py` (+ `engine/source/SOURCING_STATUS.md` for live status) |
| [`copy_bank/`](copy_bank/) | **used copy angles per country × framework** — which hooks / places / angles have shipped, so the next post stays fresh. One file per `<country>/<OPT>.md`; see its README |
| [`realism/`](realism/) | the **character-in-photo craft** — `realism_book.md` (believability rules), `persona_gen_prompt_reference.md` (the proven gen recipe), `winning_prompts.md` (verbatim winning prompts) |
| [`voice/humanizer.md`](voice/humanizer.md) | anti-AI-tell **voice rules** — short, story-first, real specifics, straight quotes, no em/en dashes |
| [`brand/holicay_brand.md`](brand/holicay_brand.md) | what Holicay is + how to name a use case — a cache; the Sheet's Holicay Brand tab is the truth |
| [`platform/tiktok_style.md`](platform/tiktok_style.md) | **platform voice + strategy only** (trimmed) — the framework docs + CONTRACT own design; this keeps the "real person's phone" snapshot + the subject / logo / facts / research notes that still apply |
| [`tuning/01_analysis.md`](tuning/01_analysis.md) … [`05_realism.md`](tuning/05_realism.md) | **per-stage lessons** the feedback loop writes — analysis · copywriting · sourcing · realism (no `04`; on-slide design is owned by the frameworks + CONTRACT) |
| [`tuning/06_performance.md`](tuning/06_performance.md) | **performance memory** — auto-written by the `analyze` skill from Sheet stats, read by `generate-post` before it writes copy |
| [`tuning/propagation-log.md`](tuning/propagation-log.md) | **append-only audit** — every feedback item, its classification, the doc it propagated to. Newest at the bottom; never rewrite history |

**One source of truth per lesson.** A lesson lives in exactly ONE of these docs — cross-reference it,
never duplicate it. When you learn something durable, sharpen the existing bullet rather than appending
a near-twin. That is the same DRY discipline the frameworks apply to the design spec.

**Where feedback goes.** The `propagate-feedback` skill routes each GREEN cell on the Sheet into the
single governing doc that controls all future posts, logs the edit in `tuning/propagation-log.md`, and
clears the cell. `dream-cycle` mines the agent's artifacts for recurring, performance-backed lessons
and proposes edits for human approval.
