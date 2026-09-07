# Phase 8: AAW Run Registry and Dispatcher

Workstream 4 of the v0.2 design.

> **Planned, not decomposed — and explicitly not to be started early.** The kickoff prompt is
> direct: "do not implement the AAW registry/CLI yet". Loops are written when Phase 7 passes.

## Objective

Give the controller a durable, inspectable record of every dispatched run, so that a run's state
survives interruption, an idle agent is never mistaken for a successful one, and cleanup refuses
to destroy work.

## Scope

### Included

- A zero-dependency Python package with an `aaw` entry point.
- SQLite storage with migration and versioning.
- A Herdr CLI adapter with structured error handling.
- A run state machine with legal-transition tests.
- Immutable envelope and result writers.
- Commands: `doctor`, `dispatch`, `list`, `inspect`, `prompt`, `attach`, `collect`, `review`,
  `stop`, `resume`, `clean`.
- Redaction rules and a local retention policy.

### Explicitly NOT included

- Any network service, hosted dashboard, or remote registry. Local only.
- Replacing Herdr. The adapter drives Herdr's existing CLI; it does not reimplement a multiplexer.
- New production dependencies without a decision gate. "Zero-dependency" is a requirement.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| `aaw` package | Python, zero-dependency | `src/aaw/` |
| Registry | SQLite + migrations | `.aaw/registry.db` |
| Herdr adapter | Python | `src/aaw/herdr/` |
| Run state machine | Python + tests | `src/aaw/runs/` |
| Redaction and retention | Policy + implementation | `src/aaw/`, `docs/` |

## Success Criteria

- ✓ Process interruption does not corrupt the registry — tested by killing mid-write, not by review.
- ✓ A restored Herdr or native session can be rebound to its AAW run — ACC-10.
- ✓ `blocked` surfaces clearly and preserves the question text — ACC-09.
- ✓ The collector catches a changed path outside `allowed_paths` and blocks completion, naming the
  offending path — ACC-13.
- ✓ An idle agent with a failing test is marked review or failed, never completed — ACC-12.
- ✓ A Herdr server restart never produces a false `completed`; the run becomes explicitly
  `interrupted` — ACC-11.
- ✓ `clean` refuses a dirty or non-terminal worktree and attempts no force deletion — ACC-17.
- ✓ No command accepts an unresolved `~` as a destructive target.
- ✓ Two concurrent writing tasks get distinct branches and worktrees with one declared owner each — ACC-07.

## Dependencies

### Must complete before this phase

- Phase 6 — the task envelope and evidence schemas the registry stores.
- Phase 7 — the routing and project config the dispatcher reads.

### Blocked by

- The Phase 3 pilot's findings about what Herdr's states actually mean. The state machine's whole
  correctness depends on the mapping between Herdr states and AAW run states being observed rather
  than assumed.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Herdr state is mapped to AAW state on assumption | Medium | **High** | The Phase 3 pilot exists to produce the real mapping; cite it, do not infer it |
| `idle` is treated as success somewhere in the state machine | Medium | **High** | ACC-12 is a required test. The design principle is explicit: idle is not success |
| A cleanup command destroys uncommitted work | Low | **High** | `clean` refuses dirty and non-terminal worktrees; no code path may pass `--force` |
| The zero-dependency constraint erodes | Medium | Medium | Any new dependency is a decision gate, not an implementation detail |
| SQLite corruption on an interrupted write | Medium | High | WAL mode plus a kill-during-write test in CI |

## Notes / Design Decisions

- This is the largest single phase and the one with the most acceptance scenarios attached to it
  (ACC-07, 09, 10, 11, 12, 13, 17). Decompose it into more, smaller loops than the earlier phases.
- The registry is the component that makes "idle is not completion evidence" enforceable rather
  than merely stated.

## Ralph Loops

To be decomposed after the Phase 7 gate passes.
