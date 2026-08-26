# Planning State

current_phase: 3
phase_name: "Safety Baseline and Herdr Pilot"
plan_file: .advanced-plans/phases/phase-3/plan.md
loops_file: .advanced-plans/phases/phase-3/loops.md
status: planned — awaiting human review of the phase plan and two blocking decisions
current_loop: (none started)
loops_total: 3
todos_total: 15
todos_done: 0
todos_pending: 15
last_updated: 2026-08-26

programme: "AAW v0.2 — Herdr-managed multi-runtime orchestration"
design_spec: .advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md
baseline: .advanced-plans/evidence/2026-08-26-baseline-audit.md
controller_checkout: C:\Users\mharvey2\Coding\Advanced-AI-Workflows
controller_branch: docs/herdr-v0.2-import

blocking_decisions:
  - "HOME split fix: scoped launcher (recommended, baseline audit §7.5) vs machine-wide change"
  - "Cursor runtime: install cursor-agent, or drop Cursor from the v0.2 target set"
  - "External-write gate: push docs/herdr-v0.2-import and the local v0.1.0 tag"

## Phases

| Phase | Name | Status | Plan |
|-------|------|--------|------|
| 1 | Four-Tool Integration v0.1 | complete (smoke PASS 2026-06-05) | [phases/phase-1/plan.md](phases/phase-1/plan.md) |
| 2 | v0.1 Smoke-Findings Fix-Pack | complete (2026-06-08) | [phases/phase-2/plan.md](phases/phase-2/plan.md) |
| 3 | Safety Baseline and Herdr Pilot | planned (3 loops decomposed) | [phases/phase-3/plan.md](phases/phase-3/plan.md) |
| 4 | gstack Sync and AAW Packaging Repair | planned (3 loops decomposed) | [phases/phase-4/plan.md](phases/phase-4/plan.md) |
| 5 | Superpowers Behavioural Port | planned (2 loops decomposed) | [phases/phase-5/plan.md](phases/phase-5/plan.md) |
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
