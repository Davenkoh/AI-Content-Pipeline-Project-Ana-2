# copy_bank — used copy angles per country × framework

The memory of **what copy we have already shipped** for each country × framework, so the next post
does not repeat itself. `generate-post` reads the matching file before it writes copy, and appends a
new entry after. This tracks the **angles and places** — the hook title, the per-slide topics/places,
the caption angle — not the full verbatim copy (the design + copy spec lives in
`../frameworks/content_frameworks.md` + `../../CONTRACT.md`; the shipped copy lives in the post's
`outputs/<char-key>/<ID - Title>/` folder).

## Layout

- **One file per country per framework:** `<country-slug>/<OPT>.md` — e.g. `japan/A.md`,
  `vietnam/C1.md`. `<OPT>` is one of `A`, `B`, `C1`, `C2`.
- Within each file, **one entry per copy iteration**, newest at the bottom.

## Iteration numbering (matches the Sheet)

- **Iteration 0** = the four `japan/{A,B,C1,C2}.md` entries are **sandbox-calibration fixtures**
  (the decks in `fixtures/` + `outputs/` used to lock the design). They were **never posted**, so
  they do not consume a real slot — they are marked `iteration 0 (fixture ...)`.
- **Iteration 1 = the first REAL posted pack** for that country × framework. This is why
  `sheets.py next-slot --character chloe` reports `copy_iteration: 1` for Japan A even though a
  fixture entry already exists here: the Sheet counts posted rows, not fixtures. Keep the two in
  step — the first shipped Japan A post appends the `iteration 1` entry below the fixture.

## Entry format

```
## <YYYY-MM-DD> · <character> · <post ID>
- Hook title: <the exact hook title used>
- Slides (angle / place per slide):
  - <slide topic or place>
  - ...
- Caption angle: <one line — the caption's through-line>
- Source: fixture | generated
- Posted: yes | no
```

## Rules

- **Freshness.** The next iteration for the same country + framework **must use new angles / places**
  than every prior entry in that file — *unless the run explicitly asks for "same"* (a deliberate
  re-run). This is the doc-level version of the frameworks' "resonance first, don't clone" rule: a
  second Japan A post picks different mistakes; a second Japan C1 picks different cities / venues.
- **Paraphrase by default across accounts.** When the same pack is reused across accounts / characters
  (e.g. a Japan C1 run for both Chloe and another character), **paraphrase** — same places, reworded
  lines and caption — rather than shipping identical text twice. Verbatim reuse happens only when a
  run explicitly asks for "same".
- **Append, never rewrite** a past entry — it is the used-angles history.
