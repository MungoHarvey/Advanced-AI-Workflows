# Phase 2 — Ralph Loops

Source phase plan: `.advanced-plans/phases/phase-2/plan.md`
Design spec: `.advanced-plans/specs/2026-06-05-smoke-findings-fixpack-design.md`

---

```yaml
---
name: "ralph-loop-001"
task_name: "Meta-source fixes (--refresh, --uninstall, hook-restart doc)"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: "Extended --refresh (re-fetch + re-run installers + change report), fixed --uninstall for global glue and empty CLAUDE.md, added hook-restart caveat to SKILL.md and SETUP.md; all committed and pushed to meta main."
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Extend the --refresh section of setup-with-claude/SKILL.md to re-fetch the canonical skill and re-run each detected sub-package installer, reporting what changed"
    skill: "NA"
    agent: "NA"
    outcome: ".claude/skills/setup-with-claude/SKILL.md --refresh section instructs (a) re-fetching the canonical setup-with-claude, (b) re-running each detected sub-package installer, (c) printing a change report"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-2"
    content: "Fix the --uninstall procedure to detect and offer removal of the globally-installed glue, not just project-local"
    skill: "NA"
    agent: "NA"
    outcome: "The --uninstall section includes a step that checks ~/.claude for globally-installed glue (setup-with-claude / gstack-to-plans) and offers to remove it"
    status: completed
    complexity: low
    priority: high
  - id: "loop-001-3"
    content: "Fix the --uninstall procedure to delete CLAUDE.md when removing the routing block leaves it empty, with a guard against deleting a non-empty file"
    skill: "NA"
    agent: "NA"
    outcome: "The --uninstall section instructs deleting CLAUDE.md only when it is empty or whitespace-only after block removal; non-empty CLAUDE.md is preserved"
    status: completed
    complexity: low
    priority: high
  - id: "loop-001-4"
    content: "Add the PostToolUse hook session-restart caveat to the setup post-install message and SETUP.md"
    skill: "NA"
    agent: "NA"
    outcome: "Both the setup-with-claude post-install message and SETUP.md state that the PostToolUse hook registers at session startup and a restart is needed after first-time settings.json creation"
    status: completed
    complexity: low
    priority: medium
  - id: "loop-001-5"
    content: "Commit the meta-source edits and push to meta-project main"
    skill: "NA"
    agent: "NA"
    outcome: "A commit containing the loop-001 edits is on main and pushed to origin (HTTPS path); git status clean"
    status: completed
    complexity: low
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Land all meta-project source edits for the fix-pack: extend --refresh, fix --uninstall (global glue + empty CLAUDE.md), and document the hook-restart caveat.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-001"

  ## Success criteria
  - [ ] setup-with-claude/SKILL.md --refresh re-fetches canonical skill + re-runs sub-package installers + reports changes
  - [ ] --uninstall offers to remove globally-installed glue
  - [ ] --uninstall deletes an emptied CLAUDE.md (guarded against non-empty)
  - [ ] hook-restart caveat present in post-install message and SETUP.md
  - [ ] edits committed and pushed to meta main

  ## Required skills
  - None — direct markdown edits to instruction files

  ## Inputs
  - Design spec: .advanced-plans/specs/2026-06-05-smoke-findings-fixpack-design.md
  - Target: .claude/skills/setup-with-claude/SKILL.md (~lines 315-405 for --uninstall), SETUP.md

  ## Expected outputs
  - Edited .claude/skills/setup-with-claude/SKILL.md
  - Edited SETUP.md
  - Commit on meta main, pushed

  ## Constraints
  - Fork-first: meta-project repo only this loop; no sub-package or upstream changes
  - Preserve the existing fenced begin/end marker design for routing block install/uninstall
  - CLAUDE.md deletion must be guarded: only when empty/whitespace-only after block removal
  - Push protocol (SSH auth is down in this env — use explicit HTTPS URL via GCM):
    `git push https://github.com/MungoHarvey/Advanced-AI-Workflows.git main`
    then sync the stale tracking ref: `git update-ref refs/remotes/origin/main HEAD`
    Do NOT change the origin remote (it stays SSH).

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-001 — meta-source fixes (refresh/uninstall/hook doc)"
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---
```

## Overview
Land every meta-project source edit for the fix-pack in one coherent change: the durable `--refresh` extension (1c), the two `--uninstall` fixes (2a, 2b), and the hook-restart documentation (#5).

## Success Criteria
- ✓ `--refresh` section documents re-fetch + re-run installers + change report: read the section
- ✓ `--uninstall` removes global glue and deletes emptied CLAUDE.md: read the section
- ✓ Hook-restart caveat in post-install message + SETUP.md: `grep -i restart`
- ✓ Edits committed and pushed: `git log origin/main..HEAD` empty after push

## Skills Required
### Broad (from phase plan):
- `markdown-editing`: editing instruction files
### Specific (refined for this loop):
- None — direct edits
### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Design spec | .advanced-plans/specs/2026-06-05-smoke-findings-fixpack-design.md | Markdown |
| Setup skill | .claude/skills/setup-with-claude/SKILL.md | Markdown |
| Setup guide | SETUP.md | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Edited setup skill | .claude/skills/setup-with-claude/SKILL.md | Markdown |
| Edited setup guide | SETUP.md | Markdown |

## Dependencies
### Must Complete Before
- Nothing — first loop; source-of-truth is current
### Blocked By
- Nothing
### Parallelisable
- ralph-loop-002 (different repo)

## Complexity
**Scope**: Low-Medium — focused edits to two instruction files
**Estimated effort**: 1 hour
**Key challenges**:
1. Keeping the `--refresh` instructions within the "Claude reads instructions" model (no new executable)
2. Correct guard logic for the CLAUDE.md deletion

## Rationale
Source edits land first so the loop-003 redeploy carries the new logic. All changes touch the meta-project only, keeping the change atomic and fork-clean.

---

```yaml
---
name: "ralph-loop-002"
task_name: "Land held Fix 1 (advanced-planning STRUCTURE.md)"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: "Fast-forward merged meta-project/fix-structure-md-stale-paths into advanced-planning main (fa799d3) and pushed to MungoHarvey/advanced-planning via HTTPS; origin/main tracking ref synced."
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Verify the meta-project/fix-structure-md-stale-paths branch is fast-forwardable into advanced-planning main"
    skill: "NA"
    agent: "NA"
    outcome: "git merge-base --is-ancestor main meta-project/fix-structure-md-stale-paths succeeds (main is an ancestor; ff is clean)"
    status: completed
    complexity: low
    priority: high
  - id: "loop-002-2"
    content: "Fast-forward merge the branch into advanced-planning main"
    skill: "NA"
    agent: "NA"
    outcome: "advanced-planning main HEAD is fa799d3 (the STRUCTURE.md fix commit); merge was fast-forward, no merge commit"
    status: completed
    complexity: low
    priority: high
  - id: "loop-002-3"
    content: "Push advanced-planning main to its origin"
    skill: "NA"
    agent: "NA"
    outcome: "origin/main of MungoHarvey/advanced-planning contains fa799d3; git status shows main up to date with origin"
    status: completed
    complexity: low
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Land the held STRUCTURE.md docs fix into advanced-planning fork main via fast-forward merge and push.

  ## Git checkpoint (run first)
  (Operates in the advanced-planning repo, not the meta-project. No meta checkpoint needed; confirm clean tree in the fork first.)

  ## Success criteria
  - [ ] ff is confirmed clean before merging
  - [ ] advanced-planning main = fa799d3 (fast-forward, no merge commit)
  - [ ] pushed to origin

  ## Required skills
  - None — git operations

  ## Inputs
  - Repo: C:/Users/mharvey2/Documents/Coding/advanced-planning
  - Branch: meta-project/fix-structure-md-stale-paths @ fa799d3

  ## Expected outputs
  - advanced-planning main advanced to fa799d3, pushed

  ## Constraints
  - Fork-internal only: target is MungoHarvey/advanced-planning main; NEVER a public upstream
    (the repo has NO upstream remote configured — origin is the only remote, so this is structurally safe)
  - Fast-forward only; if not fast-forwardable, escalate (do not force or create a merge commit)
  - Do not touch the meta-project repo in this loop
  - Push protocol (SSH auth is down in this env — use explicit HTTPS URL via GCM):
    `git push https://github.com/MungoHarvey/advanced-planning.git main`
    then sync the stale tracking ref: `git update-ref refs/remotes/origin/main HEAD`
    Do NOT change the origin remote (it stays SSH).

  ## On completion
  1. (in advanced-planning) confirm main pushed; optionally delete the merged feature branch
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---
```

## Overview
Merge the already-prepared, smoke-validated STRUCTURE.md docs branch into the advanced-planning fork's main and push. Independent of the meta-project loops.

## Success Criteria
- ✓ Fast-forward confirmed before merge: `git merge-base --is-ancestor`
- ✓ main = fa799d3, no merge commit: `git log -1 --oneline` + `git log --merges`
- ✓ Pushed: `git status` shows up to date with origin

## Skills Required
### Broad (from phase plan):
- `git-operations`: ff-merge + push in the fork
### Specific (refined for this loop):
- None
### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Fork repo | C:/Users/mharvey2/Documents/Coding/advanced-planning | git |
| Fix branch | meta-project/fix-structure-md-stale-paths @ fa799d3 | git ref |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Merged main | MungoHarvey/advanced-planning main | git |

## Dependencies
### Must Complete Before
- Nothing — independent of loop-001
### Blocked By
- Nothing (fork remote auth is its own configured remote)
### Parallelisable
- ralph-loop-001 (different repo)

## Complexity
**Scope**: Low — a fast-forward merge and push
**Estimated effort**: 15 minutes
**Key challenges**:
1. Confirming fast-forward cleanliness before merging
2. Ensuring the push targets the fork, never an upstream parent

## Rationale
The branch is one docs commit ahead of a recent main; the smoke test surfaced no new STRUCTURE.md issues, so it is clear to land. Fork-internal, no PR ceremony per the fork-first feedback memory.

---

```yaml
---
name: "ralph-loop-003"
task_name: "Redeploy global installs + verify + close findings"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-003-1"
    content: "Copy the refreshed setup-with-claude SKILL.md from the meta-project to the global install path"
    skill: "NA"
    agent: "NA"
    outcome: "~/.claude/skills/setup-with-claude/SKILL.md is byte-identical to the meta-project copy; grep -c returns >=1 for each of --uninstall, integrations.json, aaw-routing; header no longer says 'Three tools'"
    status: pending
    complexity: low
    priority: high
  - id: "loop-003-2"
    content: "Locate where the runtime phase-goals-agent is registered for this environment"
    skill: "NA"
    agent: "general-purpose"
    outcome: "The file path Claude Code loads phase-goals-agent from is identified and printed (search ~/.claude, plugins, project .claude/agents, and any advanced-planning --global target)"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-3"
    content: "Refresh the located phase-goals-agent copy from advanced-planning main so its tools line includes Write"
    skill: "NA"
    agent: "NA"
    outcome: "The deployed phase-goals-agent.md tools line reads 'Read, Glob, Grep, Write'; matches advanced-planning main canonical source"
    status: pending
    complexity: low
    priority: high
  - id: "loop-003-4"
    content: "Verify all Group A success criteria with explicit checks and log the results"
    skill: "NA"
    agent: "NA"
    outcome: "A verification block confirms global setup-with-claude markers present and phase-goals-agent has Write; all checks pass"
    status: pending
    complexity: low
    priority: high
  - id: "loop-003-5"
    content: "Update tests/v0.1-smoke-report.md to mark findings #1-#5 resolved/documented, referencing phase-2"
    skill: "NA"
    agent: "NA"
    outcome: "The report's findings section records resolution for #1-#4 and documentation for #5, with a pointer to phase-2"
    status: pending
    complexity: low
    priority: medium
  - id: "loop-003-6"
    content: "Commit the report update and push to meta main"
    skill: "NA"
    agent: "NA"
    outcome: "Report update committed on main and pushed; git status clean"
    status: pending
    complexity: low
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Redeploy the now-current global installs (setup-with-claude + phase-goals-agent), verify the Group A success criteria, and close out the smoke-report findings.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-003"

  ## Success criteria
  - [ ] global setup-with-claude is the 4-tool version (grep markers pass)
  - [ ] runtime phase-goals-agent has Write in its tools line
  - [ ] verification block logged, all checks pass
  - [ ] smoke report findings marked resolved/documented, referencing phase-2
  - [ ] report committed and pushed

  ## Required skills
  - None — file copy, search, verification, markdown edit

  ## Inputs
  - Refreshed source: .claude/skills/setup-with-claude/SKILL.md (from loop-001)
  - Agent source: advanced-planning main platforms/claude-code/agents/phase-goals-agent.md
  - Report: tests/v0.1-smoke-report.md

  ## Expected outputs
  - Refreshed ~/.claude/skills/setup-with-claude/SKILL.md
  - Refreshed phase-goals-agent.md at its runtime path
  - Updated tests/v0.1-smoke-report.md, committed + pushed

  ## Constraints
  - Must run AFTER loop-001 so the redeployed global skill carries the new --refresh/--uninstall logic
  - Do not modify the advanced-planning source in this loop — only copy from it
  - If the phase-goals-agent runtime path cannot be found, escalate with the search paths tried
  - Push protocol (SSH auth is down in this env — use explicit HTTPS URL via GCM):
    `git push https://github.com/MungoHarvey/Advanced-AI-Workflows.git main`
    then sync the stale tracking ref: `git update-ref refs/remotes/origin/main HEAD`
    Do NOT change the origin remote (it stays SSH).

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-003 — redeploy + verify + close findings"
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---
```

## Overview
Redeploy the refreshed global `setup-with-claude` and the `phase-goals-agent` copy, verify Group A is actually fixed, and mark the smoke-report findings resolved. Final loop of the phase.

## Success Criteria
- ✓ Global setup-with-claude markers present: `grep -c` for `--uninstall`/`integrations.json`/`aaw-routing` ≥1 each
- ✓ phase-goals-agent runtime tools line includes `Write`: `grep '^tools:'`
- ✓ Report findings section updated: read the section
- ✓ Report committed + pushed: `git log origin/main..HEAD` empty

## Skills Required
### Broad (from phase plan):
- `shell/deploy`: copy + verify install refresh
### Specific (refined for this loop):
- None
### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Refreshed setup skill | .claude/skills/setup-with-claude/SKILL.md | Markdown |
| Agent canonical source | advanced-planning main | Markdown |
| Smoke report | tests/v0.1-smoke-report.md | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Global setup skill | ~/.claude/skills/setup-with-claude/SKILL.md | Markdown |
| Refreshed agent | runtime registration path (located in loop) | Markdown |
| Closed findings | tests/v0.1-smoke-report.md | Markdown |

## Dependencies
### Must Complete Before
- ralph-loop-001: the global setup-with-claude refresh must carry the new --refresh/--uninstall logic
### Blocked By
- Nothing else (agent refresh source — advanced-planning main — already has Write independent of loop-002)
### Parallelisable
- None — final, integrative loop

## Complexity
**Scope**: Low-Medium — deploy + locate + verify
**Estimated effort**: 45 minutes
**Key challenges**:
1. Locating the runtime phase-goals-agent registration path (not in the obvious dirs)
2. Verifying the redeploy actually took effect for the running environment

## Rationale
Deploying after loop-001 guarantees the refreshed global skill includes the new logic. Closing the smoke-report findings here gives a single, auditable record that the fix-pack is complete.
