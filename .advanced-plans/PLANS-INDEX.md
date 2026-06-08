# Plans Index

| Phase | Name | Status | Plan |
|-------|------|--------|------|
| 1 | Four-Tool Integration v0.1 | complete (smoke PASS 2026-06-05) | [phases/phase-1/plan.md](phases/phase-1/plan.md) |
| 2 | v0.1 Smoke-Findings Fix-Pack | passed (gate 2026-06-08, attempt 2) | [phases/phase-2/complete.md](phases/phase-2/complete.md) |

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

## Source of truth

- Design doc (CEO+ENG cleared): `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-design-20260521-144453.md`
- Test plan (REG-1..REG-7): `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-eng-review-test-plan-20260521-152241.md`
- CEO plan: `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\ceo-plans\2026-05-21-four-tool-integration.md`
