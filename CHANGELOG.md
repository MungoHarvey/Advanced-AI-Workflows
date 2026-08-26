# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Release procedure: [docs/releasing.md](docs/releasing.md).

---

## [Unreleased]

Work towards v0.2.0 — Herdr-managed multi-runtime orchestration.
Design: [`.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md`](.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md).

### Added

- `docs/herdr-windows-operations.md`, `docs/upstream-sync-playbook.md`,
  `docs/herdr-kickoff-prompt.md` and `references/upstream-baseline-2026-08-26.json` —
  the v0.2 operating documentation set.
- `.advanced-plans/evidence/2026-08-26-baseline-audit.md` — controller baseline audit
  recording the environment, all five repository heads at full SHA, and the deltas
  from the design snapshot.
- Versioning: this changelog, a `VERSION` file, and `docs/releasing.md`.

### Changed

- **Plannotator is deprecated as a component of this project.** The human review gate
  moves to a cross-model gate reviewer (a reviewer running on a different model from
  the implementer, with findings resolved or explicitly waived by a human). See
  [`docs/plannotator-deprecation.md`](docs/plannotator-deprecation.md).
  The four-tool stack becomes a three-tool stack: gstack + advanced-planning +
  superpowers.
- ROADMAP restated for the Herdr execution runtime and the four target agent
  runtimes (Claude Code, Codex, OpenCode, Cursor). Gemini CLI is no longer a target.

### Known issues

- `.claude/skills/gstack-to-plans/SKILL.md` is documented and installed but not tracked
  in this repository — `.gitignore` whitelists only `setup-with-claude/`. The Quick Start
  is therefore not a verified fresh-install route at this head. Repaired in v0.2
  Workstream 1B.
- Global path resolution must use `USERPROFILE`, never `HOME` / `HOMEDRIVE` / `~`.
  On this machine those disagree (`M:\` vs `C:\Users\mharvey2`), which silently hides
  installed tooling. See §1.2 and §7 of the baseline audit.

---

## [0.1.0] - 2026-06-08

First tagged release. Four-tool integration for Claude Code:
gstack + advanced-planning + superpowers + plannotator.

Tagged retrospectively on 2026-08-26 at `3422a8c`, the closeout commit for phases 1–2.
Smoke-tested 2026-06-05 (PASS); gate passed 2026-06-08 on attempt 2.

### Added

- **`gstack-to-plans` glue skill** — pure-markdown `SKILL.md`, no executable helpers.
  Copies gstack design docs from `~/.gstack/projects/{slug}/` into `.advanced-plans/specs/`,
  with ask-when-unsure semantics at every ambiguous branch (multiple source matches,
  destination exists, unexpected filename pattern).
- **PostToolUse auto-trigger hook** — `PostToolUse Write` matcher scoped strictly to
  `~/.gstack/projects/`, surfacing a `/gstack-to-plans` suggestion on the next turn.
  Falls back to the manual command plus a CLAUDE.md closing instruction.
- **CLAUDE.md routing template** — four-tool front-door rules with superpowers preference
  overrides, in fenced begin/end markers for clean install and uninstall.
- **`setup-with-claude` skill** — rewritten as instructions Claude reads and executes
  interactively: detect, install, wire routing, grant permissions, install glue, write
  `integrations.json`, verify. Supports `--uninstall` and `--refresh`.
- Repository documentation set: README, ARCHITECTURE, DESIGN-RATIONALE, SETUP, ROADMAP.
- `tests/v0.1-smoke-report.md` and `tests/v0.1-smoke-test-runbook.html`.

### Fixed

- **advanced-planning `STRUCTURE.md`** — corrected stale path references
  (`plans/`, `.claude/plans/`, `PLANS-INDEX.md` → `.advanced-plans/`). Documentation only.
- **superpowers brainstorming default path** — Advanced-Planning-detected default moved
  from `.claude/plans/` to `.advanced-plans/specs/`. Two lines, behavioural.
- **Wrong-HOME global deploy** — caught by the phase-2 gate on attempt 2 (`3557bfa`).
  Git Bash `~` resolved to `/m/` rather than `%USERPROFILE%`, deploying artefacts to the
  wrong root. Fixed by resolving absolute paths.
- Durable `--refresh` anti-drift behaviour added to the setup skill (`fe6d28e`, `fa799d3`).

[Unreleased]: https://github.com/MungoHarvey/Advanced-AI-Workflows/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/MungoHarvey/Advanced-AI-Workflows/releases/tag/v0.1.0
