# Phase 3: Safety Baseline and Herdr Pilot

Workstream 0 of the v0.2 design. First phase of the v0.2 programme.

## Objective

Prove that Herdr can be trusted as the execution layer before any real sync or repair work
touches a component repository: that agent state is observable and honest, that worktrees are
created and removed safely on native Windows, that the controller/worker boundary holds, and
that the branch/tag/push policy is written down rather than improvised.

## Scope

### Included

- Pin the split-brain `HOME` fix so `herdr integration status` reports the truth (baseline audit §1.1, §7).
- Resolve the Cursor runtime question: install `cursor-agent`, or drop Cursor from the v0.2 target set.
- Run the Step 4 disposable Herdr pilot end to end and write a pilot report.
- Record the branch naming, backup-tag, check-command, and push policy for the whole programme.
- Establish the controller/worker ownership rules in an executable form (a checked-in policy file).

### Explicitly NOT included

- Any edit to gstack, Superpowers, or Advanced Planning. The pilot uses a disposable branch of AAW only.
- A machine-wide `HOME` change. The recommendation in baseline audit §7.5 is a scoped fix; a
  machine-wide change is a separate decision with GPO risk.
- The `aaw` CLI, the registry, or the run state machine. Those are Phase 8.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Scoped HOME fix | PowerShell launcher + doctor assertion | `tools/herdr-env.ps1`, documented in `docs/herdr-windows-operations.md` |
| Cursor decision record | Markdown | `.advanced-plans/evidence/2026-08-26-cursor-runtime-decision.md` |
| Pilot report | Markdown | `.advanced-plans/evidence/<date>-herdr-pilot-report.md` |
| Programme Git policy | Markdown | `docs/programme-git-policy.md` |
| Ownership policy | Markdown | `docs/worktree-ownership.md` |

## Success Criteria

- ✓ `herdr integration status` invoked through the documented launcher reports `current` for every
  runtime in the final v0.2 target set, from a shell where `HOME` was previously `M:\`.
- ✓ The Cursor question is closed by a written decision, not left implicit. If Cursor is dropped,
  every document that names four runtimes is updated in the same commit.
- ✓ The pilot observed and recorded `working`, then `idle`/`done`, for a real agent — with the
  transition evidenced by Herdr output, not by the agent's own prose.
- ✓ The pilot exercised `blocked` on at least one provider that supports it, or recorded explicitly
  which providers cannot produce it and why.
- ✓ A Herdr worktree containing a committed trivial edit was removed **without** `--force`.
- ✓ Detach and reattach to the named Herdr session preserved the pane and the agent.
- ✓ A second provider independently reviewed the trivial edit and its verdict is recorded.
- ✓ `docs/programme-git-policy.md` states branch names, backup-tag names, per-repository check
  commands, and that push/PR/merge are human gates.

## Dependencies

### Must complete before this phase

- Baseline audit (`.advanced-plans/evidence/2026-08-26-baseline-audit.md`) — complete, `c9abdad`.

### Blocked by

- **The HOME fix decision.** The investigation is complete (§7) and a recommendation is written,
  but the choice between the scoped fix and a machine-wide change is the repository owner's.
  Loop 001 cannot start until it is made.
- **The Cursor decision.** `cursor-agent` is not installed. Either it is installed (a new tool on
  the machine, so a decision gate) or Cursor leaves the v0.2 target set (a design amendment).

### Optional

- PowerShell 7. The machine has Windows PowerShell 5.1; nothing in this phase requires 7, but the
  pilot should record which shell produced each observation.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| A GPO reasserts `HOMEDRIVE=M:` and silently reverts a machine-wide fix | Medium | High | Prefer the scoped launcher fix; add a `doctor` assertion that fails loudly rather than resolving silently |
| Herdr reports `idle` for an agent that has actually failed | Medium | High | This is exactly what the pilot tests. Treat `idle` as "look at the evidence", never as success — ACC-12 |
| A worktree cannot be removed without `--force` | Low | High | Stop the phase. This is an exit-gate failure, not something to work around; report it upstream |
| Paths containing spaces break a Herdr command | Medium | Medium | The pilot deliberately uses a path with a space; failures are recorded rather than avoided |
| Installing `cursor-agent` pulls unexpected dependencies | Low | Medium | Decision gate before install; record what was installed and its version |

## Assumptions

- `Herdr 0.8.2 is the version under test` — recorded in the baseline; re-record if it self-updates.
- `All four integrations are already installed` — validated in baseline audit §1.1 under corrected HOME.
- `The controller checkout is the sole writer of .advanced-plans/` — asserted, and made checkable
  by the ownership policy this phase produces.

## Notes / Design Decisions

- The pilot is **disposable by construction**: a throwaway branch of AAW, in a path containing a
  space, removed at the end. Nothing it produces is merged.
- `idle`, `done`, and terminal silence are not completion evidence. The pilot's whole purpose is to
  find out what Herdr's states actually mean before the programme depends on them.

## Ralph Loops (3)

| Loop | Name | Type | Key Outputs |
|------|------|------|-------------|
| 001 | environment-pin | Implementation | Scoped HOME fix, doctor assertion, Cursor decision record, target-runtime set finalised |
| 002 | herdr-pilot | Investigation | Ten-step disposable pilot executed and evidenced; pilot report written |
| 003 | policy-record | Documentation | Programme Git policy and worktree ownership policy committed |
