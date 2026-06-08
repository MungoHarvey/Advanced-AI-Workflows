---
phase: 2
title: "v0.1 Smoke-Findings Fix-Pack"
status: passed
gate: attempt-2 PASS (code-review-agent 0.97, phase-goals-agent 0.97)
commits: 382a843..3557bfa
generated: 2026-06-08
note: written by hand (no platforms/python/handoff_digest.py in this repo)
---

## What this phase did
Resolved all 5 v0.1 smoke-test findings + landed held Fix 1, fork-first (each fix in its source repo, then redeployed). 3 loops, 14 todos.

## State now
- Meta-project `main` @ `3557bfa`, pushed to `MungoHarvey/Advanced-AI-Workflows` (HTTPS-via-GCM; SSH auth still down).
- advanced-planning fork `main` @ `fa799d3`, pushed (Fix 1 ff-merged).
- Phase-2 gate PASSED (attempt 2). Phase-1 complete (smoke PASS). No phase-3 planned.

## Key decisions / context
- Approach A for anti-drift: extended `setup-with-claude --refresh` (no symlink/version-stamp). Steps R2/R3/R5 in SKILL.md.
- `--uninstall` now removes global glue (U7) + deletes emptied CLAUDE.md guarded (U3).
- Fork-first: never push sub-package fixes to public upstream without explicit instruction.

## Errors & issues encountered
- **Wrong-HOME deploy (gate-caught):** loop-003-1's `cp ~/.claude/...` wrote to Bash `$HOME`=/m/, not real `C:/Users/mharvey2/.claude/`. Gate attempt-1 FAILED; fixed with absolute-path copy; attempt-2 PASS. → memory `project-bash-home-mismatch`. ALWAYS use absolute paths for global installs.
- **Worker over-reach:** loop-003 refreshed phase-goals-agent.md in 4 unrelated locations (eddie plugin, outlook-agent, skills_repo); reverted. → memory `feedback-worker-refresh-scope`.

## Open threads (not blocking)
- **Restart Claude Code** for this session to load the refreshed global skill + agent (load at startup).
- git identity auto-derived `mharvey2@ed.ac.uk`; user may want `mungo@the-harveys.org`.
- v0.2+ deferred: public-upstream promotion, multi-runtime, fixture/CI tests (see ROADMAP).

## Resume seed
Phase-2 done and gate-passed. Next natural steps: restart for live effect, optional `/progress-report` or `/run-closeout`, or begin new work. No pending loop.
