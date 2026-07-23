# Project Ana 2.0

- **Read [`AGENTS.md`](AGENTS.md) first** — it is the front-door resolver (capability → the one canonical home).
- **Skills live in [`.claude/skills/`](.claude/skills/)** — `generate-post`, `scrape-stats`, `propagate-feedback`, `analyze`, `new-character`. They sequence the workflow; they never fork its commands.
- **[`WORKFLOW.md`](WORKFLOW.md) is the command reference** (stages §1–§11 + Stats / Feedback / Analyze + the one Guardrails block). `CONTRACT.md` + `knowledge/frameworks/content_frameworks.md` are the output spec.
