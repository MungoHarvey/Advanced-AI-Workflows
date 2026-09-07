# loop-008-7 - the gate now reads the policy block it is handed

**Date:** 2026-09-02
**Worker:** opencode / Qwen3.5-397B, herdr agent `gate-impl`, pane `w23:p1`
**Worktree:** `~/.herdr/worktrees/advanced-planning/loop-008-gate`,
branch `loop-008-gate` based on `loop-007-integration` at `9fd6796`
**Commit:** `e0f7104`, +270 lines across two files
**Envelope:** delivered inline in the `agent prompt` text, because opencode gates
directory access outside its own worktree.

## What was wrong

A `collected-evidence` document could record `policy.independent_review_passed: false`,
stay schema-valid, and be advanced. `core/state/collected-evidence.schema.json` requires
all three policy booleans to be *present* - it guards against **absent**, which is right,
and says nothing about **false**, which is a value a worker must be able to report
honestly. `evidence_gate.py` then never read the block: every hit for
`independent_review_passed`, `tests_passed` and `path_scope_passed` was a docstring, and
every executable `policy` reference concerned verdict FILES.

This is the **third** silent pass recorded in this loop, and the one that mattered most to
sequencing: it sits inside the very function 008-2 was about to expose as a CLI. Shipping
the CLI first would have wired in a known-broken gate, and 008-4's tests would then have
pinned the wrong behaviour as correct.

## Verified by the controller, not reported by the worker

The worker's own summary was not accepted as evidence. Every line below was measured here.

| check | result |
|---|---|
| commit count, tree state | one commit, clean tree, only the two allowed paths touched |
| production diff | read in full; a new Gate 2b block after Gate 2 in `validate_advancement` |
| shipped fixture `evidence-review-complete.json` | `ok=False`, reasons `[('policy_self_review', 'Worker self-review failed: independent_review_passed=false')]` - was `ok=True, reasons=[]` |
| positive control, all three booleans true | `ok=True`, `reasons=[]` - so the check is not simply refusing everything |
| a policy key ABSENT rather than false | caught earlier by the schema gate: `/policy: Missing required property: 'independent_review_passed'` |
| `loop-complete.schema.json` | carries no policy block, so scoping the change to `validate_advancement` alone was correct rather than an omission |
| `ok = len(reasons) == 0` | line 288 - a new reason genuinely blocks |
| `test_evidence_gate.py` | 37 passed in 0.63s |
| whole test directory | **1073 passed, 1 skipped in 387s**, RC=0 |

The reason name `policy_self_review` is deliberately distinct from `policy_gates`, which
means verdict files. `test_policy_self_review_distinct_from_policy_gates` proves the
distinction rather than asserting it: a **passing** verdict file alongside a failing
self-review, asserting `policy_self_review` fires and `policy_gates` does not.

## One unreachable branch, recorded rather than papered over

The worker also added a missing-policy-block branch as defence in depth. **It is
unreachable in production.** `validate_document` is called unconditionally at
`evidence_gate.py:207` and there is no flag that skips it, so the schema gate always fires
first; the only way to reach the branch is the `unittest.mock.patch` the existing
disable-schema tests use.

Two things make this worth leaving in place rather than treating as a finding. The worker
labelled it "defense in depth" in its own comment rather than claiming coverage it does not
have, and its test asserts `schema` - the true behaviour - instead of forcing its own branch
to be the one that fires. That is the honest version. It becomes live if the schema is ever
relaxed.

It is still an unreachable branch inside the loop about unreachable code, and saying so here
costs less than rediscovering it.

## A stale citation, fixed in the same commit

008-7 inserted 35 lines into `evidence_gate.py`, moving the second `# Gate 2` comment from
line 400 to 435 (`can_advance_loop` stays at 113; `validate_loop_complete_advancement` moved
314 to 349). 008-2's todo cited "evidence_gate.py 219 and 400" as forward-looking
instruction to a worker who will read the *post*-008-7 tree, so that number was wrong the
moment this landed. It is now cited without line numbers.

The 008-5 evidence file keeps both numbers, and should: it records a measurement taken
against `9fd6796` and is pinned to that commit. A dated measurement does not go stale; an
instruction does.

The 008-2 envelope's three other citations were re-checked and all still hold -
`TestPolicySelfReview` was appended at line 777, leaving `TestIntegrationWiring` (720),
`test_next_loop_gate_does_not_read_the_envelope_that_nobody_writes` (734) and
`test_next_loop_gate_tells_the_three_failures_apart` (757) unmoved, and
`next-loop.md:397` is still exactly `allowed_paths, forbidden_paths = default_worker_scope('.')`.

## The controller's own before-measurement for 008-2

Taken now, at the post-008-7 HEAD, so the worker's before/after proof for Part B can be
checked against an independent reading rather than believed:

```
module=evidence_gate    rc=0    stdout='' stderr=''
module=state_validate   rc=2    stdout='' stderr="RuntimeWarning: ...state_validate..."
```

A module with no `__main__` dispatches through the launcher, prints nothing, and reports
success. That is the whole of the defect 008-2 Part B must close.

## An instrument error worth recording

The first attempt at that measurement piped through `head` and read `echo "EXIT=$?"`, which
reports the exit status of `head`, not of python - it printed `EXIT=0` for both modules and
would have shown the two cases as identical. Caught and redone without the pipe. This is the
programme's own rule biting on the programme: **check your instrument before your subject.**

A second, milder one: the full-directory suite was called a hang after eight minutes of
empty output. It was not. The output was empty because `| tail -20` flushes only at exit,
and the suite genuinely takes 6m27s.
