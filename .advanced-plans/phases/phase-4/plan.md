# Phase 4: gstack Sync and AAW Packaging Repair

Workstream 1A (gstack half) and Workstream 1B of the v0.2 design. These run in parallel because
they touch different repositories.

## Objective

Bring the gstack fork current with upstream, and repair the AAW packaging defect that makes the
documented Quick Start unverifiable at the current head. After this phase a fresh clone of AAW
contains every source artefact the documentation tells a user to install.

## Scope

### Included

**gstack (Workstream 1A, gstack half)**

- Create `sync/upstream-<date>` from freshly fetched `upstream/main` in a Herdr worktree.
- Re-confirm at execution time that the three fork-only commits still carry no net tree patch.
- Run the upstream test/build suite and a Windows install smoke test.

**AAW packaging (Workstream 1B)**

- Restore and track `.claude/skills/gstack-to-plans/SKILL.md`, and fix the `.gitignore` whitelist
  that made it untrackable.
- Add a packaging test that fails when any documented install source is missing.
- Replace stale-`.advanced-plans/` detection with a real installation marker.
- Make audit deterministic and non-interactive so it can run in CI.
- Resolve global paths to absolute native Windows paths.
- Prove install / refresh / uninstall idempotency in a temporary project.

### Explicitly NOT included

- Any AAW-specific product change to gstack. The sync branch is a pure upstream sync.
- The Superpowers port. That is Phase 5, deliberately a separate and higher-risk review lane.
- The multi-runtime adapters, the `AGENTS.md` routing block, or the `aaw` CLI. Phases 6, 7, 8.
- Pushing anything. Every branch in this phase stays local until the external-write gate.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| gstack sync branch | Git branch | `gstack-fork`: `sync/upstream-<date>` |
| gstack sync evidence | Markdown | `.advanced-plans/evidence/<date>-gstack-sync.md` |
| Restored glue skill | Markdown, tracked | `.claude/skills/gstack-to-plans/SKILL.md` |
| Fixed ignore whitelist | gitignore | `.gitignore` |
| Packaging test | Script | `tests/packaging/` |
| Installation manifest | JSON | `.aaw/installed.json` (schema + writer) |
| Idempotency evidence | Markdown | `.advanced-plans/evidence/<date>-packaging-repair.md` |

## Success Criteria

**gstack**

- ✓ `sync/upstream-<date>` is created from a freshly fetched `upstream/main`, not from the fork tree.
- ✓ The empty-net-patch claim is re-verified at execution time with
  `git diff <merge-base> origin/main`, not with `git diff upstream/main origin/main` — the latter
  measures how far behind the fork is and will look alarming while proving nothing.
- ✓ The upstream suite passes, with the exact command and exit code recorded.

  > **WAIVED at the phase-4 gate on 2026-08-26, by human decision.** The suite does not pass on
  > this machine: `bun run test:windows` -> `exit=1`, 7 failing tests, recorded in full at
  > `.advanced-plans/evidence/2026-08-26-phase-4-loop-001-gstack-sync.md:117-186`. Every one of
  > the seven was re-run in isolation and attributed: 3 need `jq` on PATH, 2 need Windows
  > Developer Mode (symlink privilege), 1 is a Git Bash `fork()` flake, and 1 is a genuine
  > upstream defect at `browse/test/build.test.ts:16` that pre-dates the sync. None is
  > attributable to the sync - the branch carries no net patch - so re-running loop 001 in this
  > environment reproduces the same result, which is why `loops_to_revert` was left empty by
  > every reviewer who looked at it.
  >
  > The waiver covers the *passing* half of this criterion only. The recording half was met, and
  > the Risk Assessment below anticipated exactly this case and required an honest record rather
  > than a claimed pass. Closing the criterion properly needs environment remediation (`jq`,
  > Developer Mode) and an upstream fix; both are tracked as open items in `PLANNING.md`.
  >
  > This note is a record of a decision already taken, not an instruction to a reviewer. A
  > reviewer should still evaluate the criterion and report what it finds; the waiver governs
  > what the controller does with that finding, not what the finding is.
- ✓ A Windows install smoke test passes from the synced tree.
- ✓ The branch contains zero AAW-specific changes.

**AAW packaging**

- ✓ `git ls-files .claude/skills/gstack-to-plans/SKILL.md` returns the path — the file is tracked,
  not merely present.
- ✓ A fresh `git clone` of the branch into a temporary directory contains every install source
  named in README, SETUP, and the setup skill.
- ✓ The packaging test fails when any one of those sources is deleted, and passes when restored.
- ✓ A directory containing only a stale `.advanced-plans/` is reported as *data present, Advanced
  Planning absent* — ACC-02.
- ✓ Running refresh twice produces no change on the second run — ACC-16.
- ✓ Uninstall removes only AAW-owned fenced blocks and files, and preserves user content.
- ✓ No global path in the installer resolves through `~` or `HOME`.

## Dependencies

### Must complete before this phase

- Phase 3. The pilot must have shown Herdr can create and remove worktrees safely, or this phase
  has no execution layer.

### Blocked by

- Nothing external. Both repositories are local, clean, and at verified heads.

### Optional

- The `gstack-to-plans` contract can be recovered from the deployed copy at
  `C:\Users\mharvey2\.claude\skills\gstack-to-plans\SKILL.md` (90 lines, verified intact in the
  baseline audit §3). Rewriting from the documented contract is the fallback, not the first choice.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| The deployed `gstack-to-plans` copy has drifted from what the docs describe | Low | Medium | Diff it against README/SETUP/ROADMAP claims before committing; record any discrepancy rather than silently accepting the file |
| Widening the `.gitignore` whitelist accidentally tracks unrelated local skills | Medium | Medium | Whitelist by explicit skill directory, never by removing the `.claude/skills/*` exclusion wholesale; verify with `git status` before committing |
| gstack upstream has moved since the baseline | Medium | Low | Re-fetch and re-record at execution time; the baseline is a snapshot, not a guarantee |
| The upstream gstack suite does not run on native Windows | Medium | Medium | Record the failure honestly as a platform limitation; do not claim a passing suite that was not run |
| Idempotency testing pollutes the real profile | Medium | High | All install/refresh/uninstall testing happens in a temporary project directory with global paths redirected, never against the live profile |

## Assumptions

- `The .gitignore whitelist is the sole cause of the untracked skill` — validated in baseline audit
  §3; re-verify with `git check-ignore -v` before changing it.
- `gstack's fork-only commits are merges with no net patch` — validated against the fresh clone;
  re-verify at execution time because the fork could have moved.
- `An installation manifest is sufficient to replace path probing` — to be proven by ACC-02, not
  assumed.

## Notes / Design Decisions

- **gstack and packaging run in parallel** in separate worktrees with separate owners. They share
  no files and no repository.
- **The packaging repair stays independently reviewable.** It must not expand into the multi-runtime
  adapter work; that would make the one branch a reviewer can actually check into one they cannot.
- **The net-patch test is stated explicitly in this plan** because getting it wrong once already
  produced a false alarm during the baseline audit.

## Ralph Loops (3)

| Loop | Name | Type | Key Outputs |
|------|------|------|-------------|
| 001 | gstack-sync | Migration | `sync/upstream-<date>` created from fresh upstream, suite + install smoke run, evidence recorded |
| 002 | packaging-restore | Implementation | Glue skill tracked, `.gitignore` fixed, packaging test added and proven to fail on a missing source |
| 003 | packaging-determinism | Implementation | Installation manifest replaces path probing, audit made non-interactive, idempotency proven in a temporary project |
