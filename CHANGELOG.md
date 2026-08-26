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
- `tools/herdr-env.sh` and `tools/herdr-env.ps1` — launchers that pin `HOME`, `HOMEDRIVE` and
  `HOMEPATH` from `USERPROFILE` for the child process, plus an `--assert` doctor check scoped to
  the four target runtimes. Proven in both directions, including a deliberate-drift negative test.
- `%USERPROFILE%\.local\bin\cursor-agent.cmd` (outside the repository) — a shim onto the
  `cursor-agent` CLI the Cursor IDE already bundles but does not expose on `PATH`. It resolves the
  newest version directory at run time, so a Cursor upgrade cannot leave it stale.
- `.advanced-plans/phases/phase-3` … `phase-9` — the v0.2 implementation plan. Phases 3 to 5 are
  decomposed into ralph loops; 6 to 9 are planned at phase level only.
- `.advanced-plans/evidence/2026-08-26-phase-3-loop-001-environment-pin.md` — loop 001 evidence.
- `.advanced-plans/evidence/2026-08-26-phase-3-loop-002-herdr-pilot.md` — the disposable Herdr
  pilot report covering all ten kickoff Step 4 items. Verdict: Herdr is fit to be the execution
  layer, with four qualifying findings.
- `%USERPROFILE%\.local\bin\cursor-agent` (outside the repository) — an extensionless POSIX wrapper
  beside the `.cmd` shim, because Git Bash does not consider `.cmd` when resolving a bare command
  name and this project's agents shell out through Bash.
- `docs/programme-git-policy.md` — branch and tag naming for every repository in the programme, the
  per-repository check command, commit authorship for agent-written work, and the three human gates
  (push, pull request, tag push).
- `docs/worktree-ownership.md` — one owner per checkout, the controller-sole-writer rule with the
  forbidden-path list, safe removal without `--force`, and the pilot finding that a Herdr worktree
  bounds the working directory and nothing else.
- `.gitattributes` — `*.sh` pinned to LF, `*.ps1` / `*.cmd` / `*.bat` to CRLF. Without it
  `core.autocrlf=true` checks shell scripts out with CRLF and Git Bash fails on them.
- `.advanced-plans/evidence/2026-08-26-fork-divergence-reaudit.md` — fresh gstack and Superpowers
  fork audits; both reproduce the baseline exactly.
- `.advanced-plans/evidence/2026-08-26-phase-4-loop-001-gstack-sync.md` — the gstack sync record:
  refs, backup tag, build, suite, per-failure attribution, Windows install smoke, the control run,
  the cross-model review, and the worktree teardown.

### Changed

- **Plannotator is deprecated as a component of this project.** The human review gate
  moves to a cross-model gate reviewer (a reviewer running on a different model from
  the implementer, with findings resolved or explicitly waived by a human). See
  [`docs/plannotator-deprecation.md`](docs/plannotator-deprecation.md).
  The four-tool stack becomes a three-tool stack: gstack + advanced-planning +
  superpowers.
- ROADMAP restated for the Herdr execution runtime and the four target agent
  runtimes (Claude Code, Codex, OpenCode, Cursor). Gemini CLI is no longer a target.
- Corrected the baseline audit's HOME diagnosis. Herdr does not ignore `USERPROFILE`; it prefers
  `HOME` when set and falls back to `USERPROFILE` otherwise, which makes the `M:\` failure
  shell-specific rather than machine-wide. `docs/herdr-windows-operations.md` §1.1 now documents
  the launcher as the supported way to invoke Herdr.
- `docs/upstream-sync-playbook.md` and `docs/herdr-windows-operations.md` now carry resolved
  checkout paths instead of `C:\src\...` placeholders.
- `docs/worktree-ownership.md` section 4 gains two rules from phase 4 loop 001: attempt
  `herdr worktree remove` *before* closing panes (closing the last pane of a workspace destroys
  the workspace and loses the Herdr-managed removal path entirely), and check the content diff
  before treating a worktree as dirty, since `core.autocrlf=true` can leave a file stat-dirty
  with identical content.

### Phase 3 — Safety Baseline and Herdr Pilot: complete

All three loops complete; evidence in
[`loop 001 — environment pin`](.advanced-plans/evidence/2026-08-26-phase-3-loop-001-environment-pin.md)
and
[`loop 002 — Herdr pilot`](.advanced-plans/evidence/2026-08-26-phase-3-loop-002-herdr-pilot.md).

**Exit gate: PASS with one open item.** Herdr reliably creates worktrees, including on paths
containing a space; detects the chosen agents; and reports `working` / `idle` / `done` / `blocked`
accurately. Cross-model review is demonstrated end to end — codex `gpt-5.6-terra` implemented,
opencode `Qwen3.5-397B` reviewed. A clean worktree was removed without `--force`. The open item is
ACC-10: Herdr 0.8.2 exposes no CLI detach, so detach-and-reattach could not be exercised without
killing or seizing the controller's own session. It is recorded as a testability gap and closes
with one manual `Ctrl+B`, `Q` and reattach by the operator.

### Phase 4 loop 001 — gstack upstream sync: complete

Evidence:
[`loop 001 — gstack sync`](.advanced-plans/evidence/2026-08-26-phase-4-loop-001-gstack-sync.md).

`sync/upstream-2026-08-26` created in a Herdr worktree from freshly fetched `upstream/main`
(`ad840054`), identical to it. Annotated backup tag `pre-upstream-sync-2026-08-26` at the pre-sync
fork head `a5dc03bd`. **Both are local only and neither has been pushed.**

`bun install` and `bun run build` exit 0. The Windows install smoke exits 0 into an isolated
`HOME`, leaving the live profile skills directory identical (245 entries, same hash, nothing
touched).

**`bun run test:windows` exits 1 with 7 failing tests, and that is recorded as a failure.** Each
was re-run in isolation and attributed: 3 need `jq` (not installed), 2 need Windows symlink
privilege (Developer Mode off), 1 is a Git Bash `fork()` flake, and 1 is a genuine upstream bug —
`browse/test/build.test.ts:16` interpolates an unquoted path into `execSync`, so it breaks on any
checkout path containing a space. **None is attributable to the sync**, which the empty net tree
patch makes structural rather than a judgement call.

Independent cross-model review (ACC-18): implementer Claude Opus 5, reviewer
`Qwen/Qwen3.5-397B-A17B-FP8` via opencode. **Verdict PASS**, and every factual claim in it was
re-derived by the controller before being accepted.


### Known issues

- `.claude/skills/gstack-to-plans/SKILL.md` is documented and installed but not tracked
  in this repository — `.gitignore` whitelists only `setup-with-claude/`. The Quick Start
  is therefore not a verified fresh-install route at this head. Repaired in v0.2
  Workstream 1B.
- Global path resolution must use `USERPROFILE`, never `HOME` / `HOMEDRIVE` / `~`.
  On this machine those disagree (`M:\` vs `C:\Users\mharvey2`), which silently hides
  installed tooling. See §1.2 and §7 of the baseline audit.
- The gstack suite has never been observed green on this machine. `jq` is not installed and
  Windows Developer Mode is off, so five test failures are environmental and mask anything real.
  Fix both before proposing a PR on the sync branch.

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
