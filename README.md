# Advanced AI Workflows

**Retired as a product on 2026-09-07. What it was for now lives in six habits, not in code.**

This repository set out to integrate three planning frameworks — gstack, advanced-planning
and superpowers — behind a component manifest, a detector, and a routing block that every
project's `CLAUDE.md` would carry. Three independent model reviews, run in parallel on
different vendors, each concluded on its own that the machinery was compensating for weaker
models and for the absence of an orchestrator, and that neither condition still holds. Their
reports are in [`docs/research/`](docs/research/):

- [agy / Gemini](docs/research/aaw-value-review-agy.md)
- [cursor / Grok](docs/research/aaw-value-review-cursor.md)
- [opencode / Qwen](docs/research/aaw-value-review-qwen.md)

Three numbers decided it. Of 249 commits, 170 touched only `.advanced-plans/`. No pull
request was ever opened against this repository. Nothing was ever merged to `main` until the
commit that closed the effort.

## What survived

Six standing habits, kept at
[`herdr-ops/WORKING-AGREEMENT.md`](https://github.com/MungoHarvey/herdr-ops) and summarised
in this repo's [`CLAUDE.md`](CLAUDE.md). They need no installer, no manifest and no Python.
herdr is the orchestrator; the Matt Pocock skills in [`.agents/skills/`](.agents/skills/) are
the planning path; GitHub Issues holds the state that `.advanced-plans/` used to.

## What was removed

`.advanced-plans/`, `.aaw/` and its detector, `tools/`, `tests/`, the
`setup-with-claude` and `gstack-to-plans` skills, and the architecture, roadmap, rationale
and setup documents that described them. All of it is in git history; nothing is lost, and
nothing is maintained.

## What is still here

| Path | Why it stayed |
|---|---|
| [`.agents/skills/`](.agents/skills/) | The Matt Pocock skill set, pinned by `skills-lock.json`. The planning path itself. |
| [`CONTEXT.md`](CONTEXT.md) | The domain glossary. |
| [`docs/agents/`](docs/agents/) | Issue tracker conventions, triage labels, worker attribution. |
| [`docs/research/`](docs/research/) | The measurements this decision rests on, including the reviews above. |

The wayfinder map on issue #1 records the route and its close.

## Licence

[MIT](LICENSE)
