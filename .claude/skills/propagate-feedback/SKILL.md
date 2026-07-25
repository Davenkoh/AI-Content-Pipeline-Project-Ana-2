---
name: propagate-feedback
description: Turn each piece of human review feedback (the GREEN cells on the Sheet) into a global lesson — edit the ONE governing doc that controls all future posts, log where it went, and clear the cell. Use when the user says "process the feedback", "propagate feedback", or after a review pass leaves green cells. This is WORKFLOW §Feedback in detail.
---

# Propagate Feedback (the leverage loop)

Turns each **GREEN cell** on the Sheet into a **global lesson**: edit the one governing doc that controls
all *future* framework posts, log where it went, and clear the cell. `WORKFLOW.md §Feedback` is canonical
for the commands.

The point is leverage: a regen fixes one deck; a governing-doc edit fixes the whole factory.

## Touches
- **Knowledge / spec:** `CREATIVE.md` (content wheel), `DESIGN.md` (visual/build spec),
  `knowledge/brand/holicay_brand.md`, `knowledge/tuning/02_copywriting.md · 03_sourcing.md`,
  `knowledge/realism/*`, `knowledge/voice/humanizer.md`, `CONNECTORS.md`,
  `knowledge/tuning/propagation-log.md` (the append-only audit).
- **Engine:** `engine/sheets/sheets.py feedback-poll` / `feedback-clear`.

## The rule (never violate)
- **Propagate, don't patch.** Every item must change a *governing* doc so the lesson applies to all future
  posts. If feedback can ONLY be satisfied by re-generating this one deck (no reusable rule), that is a
  build action — re-run the affected `generate-post` stage for that post id, note it in the log as a
  regen, and do not invent a fake "lesson."
- **Feedback is quoted verbatim** in the log. Never paraphrase the human's words.
- **No em/en dashes** in anything you write into post-facing copy specs.
- **Don't duplicate a lesson.** Sharpen the existing bullet rather than appending a near-twin (one source
  of truth per lesson — `knowledge/README.md`).
- **GREEN belongs to the human** — read and clear only.

## Steps (per item)

**1 · Poll.**
```bash
python3 engine/sheets/sheets.py feedback-poll        # every GREEN cell with content (JSON), all tabs
```
Empty → nothing to do.

**2 · Classify** the verbatim feedback: a **reusable lesson** (almost all review feedback → step 3), a
**one-off build fix** (regen the affected stage for that post id; log it as a regen, no fake lesson), or a
**connector/account issue** (route to `CONNECTORS.md` + the Connectors tab).

**3 · Route + edit** the single governing doc (table below) in its established style.

**4 · Log it** — append to `knowledge/tuning/propagation-log.md` (**newest at the BOTTOM**):
```
## <id> (YYYY-MM-DD)
- Feedback: <verbatim from the Sheet>
- Theme: <theme>
- Propagated to: <file path(s) + section edited>   (or: Regen — re-ran <stage> for <id>)
- Change: <one line on what changed>
```

**5 · Clear** the cell:
```bash
python3 engine/sheets/sheets.py feedback-clear --tab <any registry character key|connectors> --id <id> --note "what I changed"
```

## Routing table (theme → the one doc that controls future posts)

| Feedback is about | Edit |
| --- | --- |
| content / copy / caption / hook direction — framework structure, slide map, copy slots, verbatim plug copy, caption formula, copy angles, which places, freshness | `CREATIVE.md` (+ `knowledge/tuning/02_copywriting.md` for a durable craft lesson) |
| on-slide visual / design / type / sticker mechanism / flag / plug visual / QC gates | `DESIGN.md` |
| photo direction / sourcing — what shots read as real UGC, stock-vs-UGC, wrong subject, which backend | `CREATIVE.md` §Photo direction + the technical gate in `DESIGN.md` Gate 9 + `knowledge/tuning/03_sourcing.md` |
| realism / "looks fake" / persona / cover-polish / skin / framing | `knowledge/realism/*` (realism_book, persona_gen_prompt_reference, winning_prompts) |
| caption voice / wording / em dashes / anti-AI-tell | `knowledge/voice/humanizer.md` |
| a connector / account / billing / credential issue | `CONNECTORS.md` + the Sheet **Connectors** tab (its Notes column is the GREEN channel) |
| what Holicay is / how to name a use case (brand facts) | `knowledge/brand/holicay_brand.md` (the standing brand reference) |

When an item spans two themes, edit the doc future *builds* actually read at the moment the mistake
happens, and cross-reference the other in the log line.

## Output
Every pending item is propagated (a governing doc edited, logged, the cell cleared), handed back as a
regen, or routed to the connector registry. `feedback-poll` returns to empty. The same mistake should not
recur on the next post.

---
> **Companion:** this skill is the live GREEN inbox — poll, propagate, **clear**. The `analyze` skill is
> the periodic corpus pass (stats + performance) that PROPOSES bigger-picture edits. Run this first (empty
> the inbox), then `analyze`.
