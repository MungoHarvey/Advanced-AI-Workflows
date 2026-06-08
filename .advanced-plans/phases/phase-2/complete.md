---
phase: 2
title: "v0.1 Smoke-Findings Fix-Pack"
status: passed
gate_verdict_ref: .advanced-plans/gate-verdicts/phase-2-attempt-2-phase-goals-agent.json
anchor_sha: 382a843
end_sha: 3557bfa
commit_count: 12
loop_count: 3
created: 2026-06-08T10:05:00Z
---

## Goals met
- Global `setup-with-claude` is the 4-tool version at the REAL Claude home — `C:/Users/mharvey2/.claude/skills/setup-with-claude/SKILL.md` (--uninstall ×5, integrations.json ×17, aaw-routing ×10; corrective deploy in 3557bfa).
- Runtime `phase-goals-agent` declares `Write` — `C:/Users/mharvey2/.claude/agents/phase-goals-agent.md` (loop-003; agent wrote its own gate verdict at attempt 2).
- `--refresh` extended to re-fetch canonical skill + re-run sub-package installers + print change report — SKILL.md Steps R2/R3/R5 (fe6d28e).
- `--uninstall` removes globally-installed glue (Step U7) and deletes an emptied CLAUDE.md with a non-empty guard (Step U3) — SKILL.md (fe6d28e).
- Hook session-restart caveat documented — SKILL.md Step 8 + SETUP.md (fe6d28e).
- Fix 1 (STRUCTURE.md) fast-forward merged into `MungoHarvey/advanced-planning` main at `fa799d3` (loop-002).
- Smoke-report findings #1–#5 marked resolved/documented referencing phase-2 — `tests/v0.1-smoke-report.md` (da54eb8, corrected 3557bfa).

## Deferred
- (none) — all planned work landed; public-upstream promotion was explicitly out-of-scope, not deferred-within-phase.

## Opened
- Environment gotcha: Bash tool `~`/`$HOME` resolves to `/m/`, not the real Claude home — use absolute paths for global installs (memory: project-bash-home-mismatch; gate caught the silent miss at attempt 1).
- Worker over-reach: "refresh all copies of X" caused edits to 4 unrelated projects/plugins; reverted (memory: feedback-worker-refresh-scope).
- Session restart still required for THIS running session to load the refreshed global skill + agent (they load at startup).
- git identity is auto-derived (mharvey2@ed.ac.uk) across commits — user may want mungo@the-harveys.org.
