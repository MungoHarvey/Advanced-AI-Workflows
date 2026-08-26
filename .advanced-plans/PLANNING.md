# Planning State

current_phase: 5
phase_name: "Superpowers Behavioural Port"
plan_file: .advanced-plans/phases/phase-5/plan.md
loops_file: .advanced-plans/phases/phase-5/loops.md
status: not started — phase 4 CLOSED on 2026-08-26 (gate PASSED, attempt 2, unanimous across codex and both in-house reviewers, zero critical findings, one criterion waived by human decision)
current_loop: null
gate_status: pending
loops_total: 2
todos_total: 0
todos_done: 0
todos_pending: 0
previous_phase: 4 — gate PASSED attempt 2, closed and compacted 2026-08-26
last_updated: 2026-08-26

programme: "AAW v0.2 — Herdr-managed multi-runtime orchestration"
design_spec: .advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md
baseline: .advanced-plans/evidence/2026-08-26-baseline-audit.md
controller_checkout: C:\Users\mharvey2\Coding\Advanced-AI-Workflows
controller_branch: docs/herdr-v0.2-import

resolved_decisions:
  - "HOME split fix: BOTH — machine-wide user override plus the scoped launcher and doctor assertion (2026-08-26)"
  - "Cursor runtime: install cursor-agent — already bundled by the Cursor IDE, shimmed onto PATH (2026-08-26)"
  - "External-write gate: approved — docs/herdr-v0.2-import and v0.1.0 pushed (2026-08-26)"
  - "Phase-4 gate, attempt 1: the gstack upstream-suite criterion is WAIVED (2026-08-26). All 7 failures were re-run in isolation and attributed - 3 to a missing jq, 2 to Windows Developer Mode being off, 1 to a Git Bash fork() flake, 1 to an upstream gstack defect predating the sync. None is attributable to the sync, so no retry can close it. Recorded inline in phases/phase-4/plan.md."
  - "Phase-4 gate, attempt 1: the second failing criterion - no global installer path resolves through ~ or HOME - was fixed rather than waived, in 3b19a49 on feat/aaw-packaging-repair (2026-08-26)."

blocking_decisions:
  - "none open"

open_items:
  - "ACC-10: detach/reattach unproven — Herdr 0.8.2 has no CLI detach. One manual Ctrl+B, Q by the operator closes it."
  - "Machine-wide HOME override unverified until next logon; the launcher makes it moot either way."
  - "Phase 3 has no gate verdict — the phase-4 boundary was the first real /run-gate run (attempt 1: FAIL, unanimous across codex, code-review-agent and phase-goals-agent)."
  - "The three helper modules /run-gate calls are WRITTEN (advanced-planning 4f7a6a1 on branch feat/gate-tooling-modules, local only, 109 new tests, 179 total passing). codex_gate reproduces the phase-4 attempt-1 FAIL and attempt-2 PASS unaided. Not yet adopted: the branch is unmerged and unpushed, and /run-gate's own snippets use sys.path.insert(0, '.') which will not find them from a consuming project - PYTHONPATH=<advanced-planning root> is the working invocation, documented in platforms/python/README.md."
  - "HAZARD, unresolved: the global ~/.claude layer is AHEAD of the advanced-planning source on 24 files and holds 13 files source has never seen. AUDITED per-file 2026-08-26 - the report is advanced-planning docs/install-layer-divergence-2026-08-26.md (commit 9fb8e85 on feat/gate-tooling-modules, local only). Findings: in every one of the 24 the global copy is ahead and no source file holds a change the installed copy lacks. Tier A = 10 files, ~76 lines, purely the plans/ -> .advanced-plans/ layout migration (4 stray lines missed, named in the report). Tier B = 12 files, ~1,590 lines of real design: Codex gate preflight and parallel execution, bounded remediation with SHA-256-frozen success criteria, branch scoping, mid-loop resume detection, incident-derived hard contracts, re-gate isolation. Tier C = 2 files where the GLOBAL copy regressed and must NOT be adopted: todo.schema.md deletes the complexity field (used 87 times across all five live loop files here) and ralph-loop.schema.md collapsed its two path modes into one identical line. Of the 13 orphans, 6 are framework (phase-compact, sync-plans, sync-install, decompose-phase, codex-reviewer, schemas/README) and 7 belong to other projects (eddie x2, paper-shred-refiner, code-reviewer, plannotator x3 - the plannotator ones are deprecated leftovers in the user global layer). Adoption means copying installed -> source by hand, per file, respecting the tiers; /sync-install cannot do it and documents that direction as unsupported. DO NOT RUN /sync-install until this is reconciled. Backup of the global layer (40 files) is in the session scratchpad at global-claude-backup-2026-08-26/."
  - "gstack test:windows does not pass on this machine: exit 1, 7 failing tests. 5 are environmental (jq missing, Windows Developer Mode off), 1 a Git Bash fork flake, 1 a genuine upstream bug. None attributable to the sync. Fix the environment before any PR so real failures stop being masked."
  - "browse/test/build.test.ts:16 interpolates an unquoted path into execSync and breaks on any checkout path containing a space. Upstream bug, worth reporting to garrytan/gstack."
  - "sync/upstream-2026-08-26 and pre-upstream-sync-2026-08-26 are local only and need a push gate."
  - "feat/aaw-packaging-repair is pushed (origin, 3b19a49) but not merged. Until it lands, main still ships an incomplete install set, and README:7 and SETUP.md:9 need one further edit when it does. A pull request and a merge are each a separate authorisation and neither has been given."
  - "The gstack-to-plans glue skill has zero AskUserQuestion callouts although phase 1 accepted it on having them at three ambiguous branches. Committed verbatim to preserve provenance; the packaging test checks presence, not correctness, so it cannot catch this."
  - "An agent self-reported model id is not evidence — a codex reviewer named a model that contradicted its own pane footer, then retracted it. ACC-18 checks must use the started --kind and the observable pane, not the agent word."
  - "Phase-4 Key Deliverables names two evidence files that were produced under different names (<date>-gstack-sync.md and <date>-packaging-repair.md against the actual ...-phase-4-loop-001-gstack-sync.md and ...-phase-4-loop-003-installation-state.md). Both gate attempts flagged it at info level. The plan was left as gated and the reconciliation is recorded in phases/phase-4/complete.md instead of editing an artefact the reviewers had already seen."
  - "references/install-gstack.md:16 gives only a ~-based install command with no Windows PowerShell variant, unlike its sibling reference files. Found at the phase-4 gate, pre-existing, non-blocking - it is a user-run command, so it does not breach the no-global-~ criterion."

## Phases

| Phase | Name | Status | Plan |
|-------|------|--------|------|
| 1 | Four-Tool Integration v0.1 | complete (smoke PASS 2026-06-05) | [phases/phase-1/plan.md](phases/phase-1/plan.md) |
| 2 | v0.1 Smoke-Findings Fix-Pack | complete (2026-06-08) | [phases/phase-2/plan.md](phases/phase-2/plan.md) |
| 3 | Safety Baseline and Herdr Pilot | passed with one open item (2026-08-26) | [phases/phase-3/complete.md](phases/phase-3/complete.md) |
| 4 | gstack Sync and AAW Packaging Repair | complete — gate PASSED attempt 2 (2026-08-26), one criterion waived | [phases/phase-4/complete.md](phases/phase-4/complete.md) |
| 5 | Superpowers Behavioural Port | current (2 loops decomposed, not started) | [phases/phase-5/plan.md](phases/phase-5/plan.md) |
| 6 | Advanced Planning Multi-Runtime Adapters | planned (loops deferred) | [phases/phase-6/plan.md](phases/phase-6/plan.md) |
| 7 | AAW Multi-Host Routing and Installer | planned (loops deferred) | [phases/phase-7/plan.md](phases/phase-7/plan.md) |
| 8 | AAW Run Registry and Dispatcher | planned (loops deferred) | [phases/phase-8/plan.md](phases/phase-8/plan.md) |
| 9 | Cross-Host E2E and Release | planned (loops deferred) | [phases/phase-9/plan.md](phases/phase-9/plan.md) |

## Execution scope authorised so far

Per `docs/herdr-kickoff-prompt.md`: execute Workstream 0 and the local branch portion of
Workstreams 1A and 1B — that is **phases 3, 4, and 5**. Phases 6 to 9 are planned at phase level
and deliberately not decomposed into loops yet. The registry and CLI (phase 8) are explicitly not
to be implemented at this stage.

## Controller ownership

This checkout is the sole writer of `.advanced-plans/state/`, this file, `PLANS-INDEX.md`,
`phases/*/complete.md`, `gate-verdicts/`, and `evidence/`. Worker worktrees never write them.
