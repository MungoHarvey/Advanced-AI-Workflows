# Plans Index

| Phase | Name | Status | Plan |
|-------|------|--------|------|
| 1 | Four-Tool Integration v0.1 | complete (smoke PASS 2026-06-05) | [phases/phase-1/plan.md](phases/phase-1/plan.md) |
| 2 | v0.1 Smoke-Findings Fix-Pack | passed (gate 2026-06-08, attempt 2) | [phases/phase-2/complete.md](phases/phase-2/complete.md) |
| 3 | Safety Baseline and Herdr Pilot | passed with one open item (2026-08-26) | [phases/phase-3/complete.md](phases/phase-3/complete.md) |
| 4 | gstack Sync and AAW Packaging Repair | in progress (loops 001-003 complete; loop-003-5 awaiting its human gate) | [phases/phase-4/plan.md](phases/phase-4/plan.md) |
| 5 | Superpowers Behavioural Port | planned | [phases/phase-5/plan.md](phases/phase-5/plan.md) |
| 6 | Advanced Planning Multi-Runtime Adapters | planned (loops deferred) | [phases/phase-6/plan.md](phases/phase-6/plan.md) |
| 7 | AAW Multi-Host Routing and Installer | planned (loops deferred) | [phases/phase-7/plan.md](phases/phase-7/plan.md) |
| 8 | AAW Run Registry and Dispatcher | planned (loops deferred) | [phases/phase-8/plan.md](phases/phase-8/plan.md) |
| 9 | Cross-Host E2E and Release | planned (loops deferred) | [phases/phase-9/plan.md](phases/phase-9/plan.md) |

---

## Programme: AAW v0.2 — Herdr-managed multi-runtime orchestration

- Design spec: [specs/2026-08-26-herdr-multi-runtime-orchestration-design.md](specs/2026-08-26-herdr-multi-runtime-orchestration-design.md)
- Amendment: [docs/plannotator-deprecation.md](../docs/plannotator-deprecation.md) — supersedes §7.4
- Baseline: [evidence/2026-08-26-baseline-audit.md](evidence/2026-08-26-baseline-audit.md)
- Controller prompt: [docs/herdr-kickoff-prompt.md](../docs/herdr-kickoff-prompt.md)
- Release procedure: [docs/releasing.md](../docs/releasing.md)
- Git policy: [docs/programme-git-policy.md](../docs/programme-git-policy.md)
- Worktree ownership: [docs/worktree-ownership.md](../docs/worktree-ownership.md)
- Herdr pilot report: [evidence/2026-08-26-phase-3-loop-002-herdr-pilot.md](evidence/2026-08-26-phase-3-loop-002-herdr-pilot.md)
- Fork divergence re-audit: [evidence/2026-08-26-fork-divergence-reaudit.md](evidence/2026-08-26-fork-divergence-reaudit.md)
- gstack sync record (phase 4 loop 001): [evidence/2026-08-26-phase-4-loop-001-gstack-sync.md](evidence/2026-08-26-phase-4-loop-001-gstack-sync.md)
- packaging repair record (phase 4 loop 002): [evidence/2026-08-26-phase-4-loop-002-packaging-repair.md](evidence/2026-08-26-phase-4-loop-002-packaging-repair.md)
- installation state record (phase 4 loop 003): [evidence/2026-08-26-phase-4-loop-003-installation-state.md](evidence/2026-08-26-phase-4-loop-003-installation-state.md)

### Workstream to phase mapping

| Design workstream | Phase |
|---|---|
| 0 — Safety baseline and Herdr pilot | 3 |
| 1A (gstack) + 1B — sync and packaging repair | 4 |
| 1A (Superpowers) — behavioural port | 5 |
| 2 — Advanced Planning multi-runtime adapters | 6 |
| 3 — AAW multi-host routing and installer | 7 |
| 4 — AAW registry and dispatcher | 8 |
| 5 — Cross-host E2E and release | 9 |

Workstream 1A's Plannotator fast-forward is **withdrawn** — deprecated 2026-08-26.

---

## Phase 2 — manifest entry

- phase: 2
  title: "v0.1 Smoke-Findings Fix-Pack"
  status: passed
  commits: 382a843..3557bfa
  detail: .advanced-plans/phases/phase-2/complete.md
  highlights:
    - All 5 smoke findings + Fix 1 landed; durable `--refresh` anti-drift added (fe6d28e, fa799d3).
    - Gate caught a wrong-HOME global deploy (Bash ~ = /m/); fixed via absolute path, attempt-2 PASS (3557bfa).

## Ralph Loops (Phase 2)

| Loop | Name | Status |
|------|------|--------|
| 001 | meta-source-fixes (--refresh, --uninstall, hook-restart doc) | completed |
| 002 | land-fix-1 (advanced-planning STRUCTURE.md ff-merge) | completed |
| 003 | redeploy-and-verify (+ close smoke findings) | completed |

## Ralph Loops (Phase 3)

| Loop | Name | Status |
|------|------|--------|
| 001 | environment-pin (HOME fix, orphan copy, Cursor decision) | completed |
| 002 | herdr-pilot (ten-step disposable pilot) | completed |
| 003 | policy-record (Git policy, worktree ownership) | completed |

## Ralph Loops (Phase 4)

| Loop | Name | Status |
|------|------|--------|
| 001 | gstack-sync | **completed** (5/5 todos; cross-model review PASS; suite exit 1, all failures attributed) — [evidence](evidence/2026-08-26-phase-4-loop-001-gstack-sync.md) |
| 002 | packaging-restore | **completed** (5/5 todos; cross-model review FAIL then PASS, one finding accepted and fixed; packaging test proven in four directions) — [evidence](evidence/2026-08-26-phase-4-loop-002-packaging-repair.md) |
| 003 | packaging-determinism | **completed** (5/5 todos; manifest, detection, audit and a 43-check idempotency test; cross-model review FAIL x3 then PASS over four passes, every finding re-derived and every fix proven to fire; two caveats recorded) — [evidence](evidence/2026-08-26-phase-4-loop-003-installation-state.md) |

## Ralph Loops (Phase 5)

| Loop | Name | Status |
|------|------|--------|
| 001 | behaviour-matrix | pending (net-patch re-derivation done) |
| 002 | routing-port | pending |

## Source of truth

- v0.2 design doc: `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md`
- v0.1 design doc (CEO+ENG cleared): `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-design-20260521-144453.md`
- v0.1 test plan (REG-1..REG-7): `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-eng-review-test-plan-20260521-152241.md`
- v0.1 CEO plan: `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\ceo-plans\2026-05-21-four-tool-integration.md`
