# Planning State

current_phase: 5
phase_name: "Superpowers Behavioural Port"
plan_file: .advanced-plans/phases/phase-5/plan.md
loops_file: .advanced-plans/phases/phase-5/loops.md
status: in progress — ralph-loop-001 COMPLETE 2026-08-26 (behaviour matrix written, cross-model design gate PASSED after a BLOCKED verdict was resolved). feat/aaw-packaging-repair merged into this branch (5524580), so the installation manifest is available; ralph-loop-002 realigned against the matrix and ready to execute.
current_loop: ralph-loop-002
gate_status: loop-001 design gate PASSED 2026-08-26 (reviewer codex/GPT-5.6 Sol, author claude/Opus 5 — ACC-18 satisfied)
loops_total: 2
todos_total: 11
todos_done: 4
todos_pending: 7
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
  - "CORRECTED 2026-08-26: the install-layer divergence hazard was misdiagnosed, then fixed properly. The original finding - global ~/.claude ahead of advanced-planning source on 24 files - was measured against a local checkout 147 commits behind origin/main. Fetching moved origin/main from e199cca to 02b4b86 (v0.16.0), which already contained essentially all of the ~1590 lines the audit had credited to the global layer. The global layer was ahead of one stale clone, not of the framework. Caught before any push; nothing lost. The 29-file adoption commit 5722f58 and the three rewritten helper modules in 4f7a6a1 are therefore redundant and abandoned on wip/stale-clone-adoption-2026-08-26. Salvaged onto fix/install-audit-diverged-state (off origin/main, local, unpushed) as the three things upstream genuinely lacked: 0532f64 adds the DIVERGED verdict to install_audit (a content difference where the installed copy is same-age-or-newer is no longer reported as STALE, because /sync-install parses STALE into its source->installed copy list and would destroy it), adds core/agents as an audited surface with extra computed against the union of every source dir installing into the same directory, and fixes ralph-loop.schema.md documenting both file modes with the same path; 7fd906e retracts the audit report headline. 8 new tests, mutation-verified; suite matches the origin/main baseline exactly (391 passed, 9 environmental failures, 11 skipped). The global layer has been re-synced from origin/main: 8 files restored, and commands/new-phase.md + next-loop.md deliberately NOT overwritten - they hold real local branch-scoped-phase customisation for parallel research worktrees that upstream has no equivalent of, and are the live worked example of why DIVERGED exists. Backups: global-claude-backup-2026-08-26/ (pre-session) and global-claude-pre-resync-2026-08-26/ (pre-restore) in the session scratchpad."
  - "OPEN DECISION (evidence corrected 2026-08-26): the todo `complexity` field. Retained in the stale-clone work on the reasoning that a schema deletion contradicted by four sibling files in its own tree is an incomplete edit. That reasoning was briefly abandoned on a bad measurement - grepping only core/schemas/todo.schema.md at origin/main returns 0 occurrences, which looked like a settled deletion. Grepping the whole of origin/main v0.16.0 returns 159 occurrences across 30+ files, and they are not vestigial: core/skills/plan-todos/references/todo-schema.md and core/skills/ralph-loop-planner/references/todo-schema.md - the copies the planning skills actually load - both document complexity AND the field order id -> content -> skill -> agent -> outcome -> status -> complexity -> priority; upstream's own newest loop files emit it (phase-14: 15 todos, phase-15: 23, phase-16: 25, all written at v0.16.0); and worker.md, orchestrator.md, ralph-orchestrator.md, agents/README.md and the 103-line docs/model-tier-strategy.md all drive worker model-tier selection off it. core/schemas/todo.schema.md is the lone outlier. So the original retention was right and the field is live. Stripping the 87 call-sites in the five loop files here would make them non-conformant with the two reference schemas the skills read, and would break Haiku eligibility. The 87 are untouched pending an explicit call. The cheap fix in the other direction is to restore complexity to core/schemas/todo.schema.md upstream so its own tree stops disagreeing with itself."
  - "gstack test:windows does not pass on this machine: exit 1, 7 failing tests. 5 are environmental (jq missing, Windows Developer Mode off), 1 a Git Bash fork flake, 1 a genuine upstream bug. None attributable to the sync. Fix the environment before any PR so real failures stop being masked."
  - "browse/test/build.test.ts:16 interpolates an unquoted path into execSync and breaks on any checkout path containing a space. Upstream bug, worth reporting to garrytan/gstack."
  - "sync/upstream-2026-08-26 and pre-upstream-sync-2026-08-26 are local only and need a push gate."
  - "feat/aaw-packaging-repair (now at 360ab3c, not 3b19a49 as previously recorded) is merged into docs/herdr-v0.2-import LOCALLY as 5524580, and the README:7 and SETUP.md:9 edits were applied in that merge. main is still unfixed: it continues to ship an incomplete install set until this branch lands there. A pull request and a merge to main are each a separate authorisation and neither has been given. Its Herdr worktree (workspace wA) is still open and needs its own removal approval."
  - "RESOLVED 2026-08-26: ralph-loop-002 has been rewritten against the gate-approved behaviour matrix. SP-4a is now do-not-port and SP-3 is delivered through the fenced block rather than held in the fork, so the fork patch target is zero and loop-002-1 prepares a local mirror branch plus a backup tag instead of a port branch. loop-002-2 targets .claude/skills/setup-with-claude/references/ (the fenced-block source), not a skill file. loop-002-3 is now the idempotent-merge proof. loop-002-6 asserts an EMPTY tree diff against upstream/main rather than diffing only the router section. The three entry criteria are settled and written into the loop prompt: the manifest predicate is .aaw/installed.json components[advanced-planning].installed, precedence is additive-and-idempotent-never-authoritative, and acceptance is loop-002-4 plus loop-002-5. phases/phase-5/plan.md carries a dated amendment recording the same three reversals; where plan and amendment disagree, the amendment governs."
  - "Publishing the Superpowers mirror requires force-pushing origin/main in that fork, which docs/herdr-kickoff-prompt.md places outside the controller's authority (force-push and default-branch merge are both on the not-authorised list). Phase 5 therefore prepares and proves the mirror locally and stops at a human gate; loop-002-1 must write down the exact publish command rather than run it."
  - "Two clones of MungoHarvey/superpowers exist on this machine at different commits. C:/Users/mharvey2/Coding/superpowers is the programme checkout (main at fde9f97, has both origin and upstream remotes) and is the one loop-001 and loop-002 use. M:/Coding/planning/superpowers is on main at f2d65a6, has NO upstream remote, and is two commits behind the fork head - it predates b874847 and fde9f97. Nothing has been done to it. Decide whether to delete it, re-point it, or leave it; until then, any command run in the wrong one silently measures the wrong tree."
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
