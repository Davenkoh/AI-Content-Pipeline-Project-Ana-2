---
name: analyze
description: The periodic learning pass. Mine the Sheet's post stats + the agent's own artifacts for what actually wins by framework / variant / country / copy angle, rewrite knowledge/tuning/06_performance.md, and PROPOSE (never silently apply) any CONTRACT / frameworks edits. Use when the user says "what's working", "analyze performance", "mine the data", "should we do more human or nohuman", or on a cadence. This is WORKFLOW §Analyze in detail.
---

# Analyze (corpus-wide performance pass)

`propagate-feedback` reacts to one GREEN cell at a time. This skill steps back and reads the **whole
recorded brain** — the Sheet's post stats + the agent's own artifacts — to find what the numbers say to
double down on or back off. It **rewrites `knowledge/tuning/06_performance.md`** (the data-backed memory
`generate-post` reads before writing copy) and **PROPOSES** any spec change; it never silently edits
`CONTRACT.md` or the frameworks doc.

> **`WORKFLOW.md §Analyze` is canonical** for the commands. Run `scrape-stats` first so the numbers are
> current, and `propagate-feedback` first so the GREEN inbox is empty.

## Touches
- **Reads — the Sheet:** each character fact tab (`read --tab <Ana|Chloe|Hannah>`) for every post's
  framework / variant / country / copy_iteration + its STATS (views · likes · comments · shares · saves) +
  Human-Feedback notes; the **Dashboard** + `stats-summary --json` for the rollup.
- **Reads — the agent's artifacts:** each post's `outputs/*/flags.md` + `sources.md` + `caption.txt`, the
  `copy_bank/<country>/<OPT>.md` used-angle history, and `knowledge/tuning/propagation-log.md`.
- **Writes:** `knowledge/tuning/06_performance.md` (directly — it is the results skeleton). **Proposes only**
  for `CONTRACT.md` / `content_frameworks.md` / any other governing doc.

## Steps

**1 · Refresh + gather.** Run `scrape-stats` if the numbers are stale, then:
```bash
python3 engine/sheets/sheets.py stats-summary --json
python3 engine/sheets/sheets.py read --tab Ana
python3 engine/sheets/sheets.py read --tab Chloe
python3 engine/sheets/sheets.py read --tab Hannah
```
Read the `outputs/*` artifacts + `copy_bank` + `propagation-log`.

**2 · Join stats to the levers**, in order:
- **By framework (A / B / C1 / C2)** — median views + saves each. Which blueprint earns saves?
- **By variant (human / nohuman)** — **the human-vs-nohuman A/B test readout.** Same accounts post both
  (the rotation alternates per framework), so compare within-account where you can. This verdict is the
  headline of the run.
- **By country** — does a country over/under-index on a framework?
- **Copy angles that outperformed** — hook titles, plug variants, and per-slide angles that beat the
  median, each with the **post IDs** as evidence.

**3 · Rewrite `knowledge/tuning/06_performance.md`** — fill its by-framework / by-variant / by-country
tables and the "copy angles that outperformed" list, every claim backed by post IDs. This is a direct
write (the doc is the auto-written results skeleton); do not hand-invent numbers.

**4 · Propose, don't patch, for anything structural.** If the data suggests a spec change (retire a weak
plug variant, re-order a slide map, shift the variant default), emit a review list — one item each:
```
- Finding: <the pattern>
- Evidence: <the Sheet metrics + which post IDs>
- Target: <CONTRACT.md / content_frameworks.md / a copy_bank file>
- Proposed edit: <the exact change, in that target's style>
```
The **human approves**; approved items are written via `propagate-feedback`'s discipline and logged in
`propagation-log.md` (mark `source: analyze`). Rejected items are dropped.

## Boundary vs propagate-feedback
- **propagate-feedback** = the live GREEN inbox: per-item, write-through, clears the cell.
- **analyze** = the periodic corpus pass: stats + performance across posts. Rewrites `06_performance.md`
  directly; **proposes** governing-doc edits; does NOT clear GREEN cells.

## Output
An updated `knowledge/tuning/06_performance.md` (by framework / variant / country + winning copy angles,
with post-ID evidence), a stated **human-vs-nohuman verdict**, and a short human-reviewable proposal list
for any CONTRACT / frameworks change. Nothing structural is written without approval.
