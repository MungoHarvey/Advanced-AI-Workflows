# loop-008-9 — one blocked exit code, decided; and the shipped doc that outlived the decision

Date: 2026-09-03
Repository: advanced-planning
Branch: `loop-008-gate` (base `loop-008-8` at `8cf17b5`)
Worktree: `~/.herdr/worktrees/advanced-planning/loop-008-gate`
Provider: opencode / Qwen3.5 397B, herdr worker `gate-exit` in `w2:p2H`
Discharges: the three success criteria loop-008 left unticked

## The decision, made before dispatch

Criterion 1409 asked for three failure modes distinguishable **by exit code**.
That is the wrong contract, and the loop was opened saying so: nothing in any
shipped command branches on which gate failed, so three codes would be an
interface nothing consumes and a future edit could break in silence. The
decision was to keep **one** blocked code and separate the modes by stderr
prefix, then fix the two defects that decision exposes.

Defect A: VACUOUS was printed under the `path_scope:` prefix, so one prefix
covered a real scope violation and the refusal to rule on zero paths. Prefix
overloading defeats "distinguishable by message", which was the half of the
criterion that was achievable.

Defect B: five git-subprocess failures returned **1**, the same code as a real
refusal. That is this programme's own defect class inside the gate itself: an
exit code asserting something the gate never checked. A baseline that does not
resolve is not a verdict about the operator's change.

## What landed

| commit | author | change |
|---|---|---|
| `5a24129` | worker | items 1-3: the removal record, the `vacuous:` prefix, the five git sites moved to exit 2 under `git:` |
| `d09d91f` | worker | the shipped SKILL.md exit-code prose, round 2 |
| `2d85287` | controller | restore the 3-space indent round 2 had changed to 4 |
| `1fb0f38` | controller | make the decision record readable outside its envelope |

Tree clean at the tip. Nothing under `.advanced-plans/` or `core/` was touched
by any of the four.

## The return map, measured rather than read

Walking `main()` after the fix:

- **`return 0`** at 573, 745.
- **`return 1`** at exactly three sites: 582 and 754 (`path_scope:`) and 732
  (`vacuous:`).
- **`return 2`** everywhere else, including the five that used to be 1:
  653 (`git: BAD REPO ROOT`), 673 / 693 / 713 (`git: BAD BASELINE`), and 725
  (`git: Failed to get git diff`).

Line 754 is the combined arm: schema errors, policy-gate reasons and scope
violations all reach it, each written to stderr under its own prefix. That is
why the decision record names four blocking modes and not three.

## Red-green, by reversion

Controller-side, reverting the whole production file to `8cf17b5` rather than
mutating one line:

| new test | own gate | on `8cf17b5` |
|---|---|---|
| `test_vacuous_uses_vacuous_prefix` | pass | **fail** |
| `test_git_rev_parse_failure_uses_git_prefix_exit_2` | pass | **fail** |
| `test_git_diff_baseline_failure_uses_git_prefix_exit_2` | pass | **fail** |
| `test_real_scope_violation_uses_path_scope_prefix_exit_1` | pass | **pass** |

The fourth row is the positive control and its *passing* is the finding: a gate
that had simply started returning 2 for everything would have failed it. Three
red and one green is the asymmetry a control exists to show.

One existing test was edited, `test_bad_baseline_says_bad_baseline_not_vacuous`,
and only its exit-code assertion, 1 to 2. Its subject, that a bad baseline says
BAD BASELINE rather than VACUOUS, is untouched, so this is a consequence of the
fix rather than a weakening of the test.

## Independent re-run, with the tree as a parameter

`verify_008_9.py` runs the gate against an installed fixture with `PYTHONPATH`
pointed at a **chosen** tree, so the same five scenarios can be measured before
and after. It refuses outright if the clean control does not exit 0.

| scenario | expected pre | expected post |
|---|---|---|
| clean pass (control) | 0 | 0 |
| real path-scope violation (control) | 1, `path_scope:` | 1, `path_scope:` |
| VACUOUS off the `path_scope:` prefix | 1, `path_scope:` | 1, `vacuous:` |
| bad baseline is not a verdict | 1 | 2, `git:` |
| the same, from a subdirectory | 1 | 2, `git:` |

**5/5 pre, 5/5 post.**

The first attempt at this measured a moving target: it ran against the live
worktree file the worker was concurrently editing, so `vacuous:` already
appeared in the "pre" column. Fixed by exporting `8cf17b5` with `git archive`
and parameterising the tree. The archive was then incomplete, and the instrument
check refused with a missing schema file rather than emitting four meaningless
rows, so `core` had to be exported alongside `platforms`. The instrument caught
itself twice before it was allowed to say anything about the subject.

## Criterion 1408, proven by execution at both sites

The criterion was reworded by the loop-008 audit, from *runs the gate at both
sites* to *runs it, or refuses and says why*, because F5 chose refusal at the
`resume` site for a stated reason. A criterion reworded to fit the code is
worthless unless something then checks it, so it was checked:

- **Site 1**: the six-scenario harness re-run against a fresh installed fixture
  carrying the round-2 SKILL.md, with `runtime.json` repointed at the branch tip.
  **6/6**. VACUOUS, positive control, forbidden path in the last commit,
  forbidden path in the *first* of two commits, and both schema arms. The
  `vacuous:` prefix is visible through the shipped operator path, which is item 2
  measured end-to-end rather than in a unit test.
- **Site 2**: the `resume` block in the installed copy refuses. *"Do NOT finalize
  here"*, followed by the reason (the step-6 baseline was held in the session and
  is lost after a crash; a guessed one would make the gate meaningless) and the
  manual recipe.

Site selection stayed structural, not positional: 2 shipped blocks run the
loop-complete gate, the one at line 159 is paired with a `state_validate` four
lines above it, and the `resume` site at 245 has none because F5 removed those
lines. Unchanged by the round-2 edit, which is itself the check that the doc
change did not disturb extraction.

## Criterion 1411

`can_advance_loop` appears nowhere in the tree except the line recording its own
removal. `validate_advancement` is in `__all__`. The record sits directly above
`__all__`, where a reader arriving from an older call site will meet it.

## The third instance of the same defect: a fix that moved the reason out from under the documentation

Found after the worker's first round was already verified. The shipped SKILL.md
said, in two places:

> Exit code `2`: malformed invocation — should not happen with the shipped command.

Item 3 had just made exit 2 the code for a baseline that does not resolve, which
is the commonest operator error there is, because step 7 makes them supply a
baseline by hand. The prose said "should not happen" exactly where it now would.

This is the third time in this programme that a fix has moved the *reason* out
from under the documentation that explains it, after the `evidence_gate` module
docstring in 008-8 and the step-7 rationale in 008-6. It is worth stating as a
class: **when a change alters what an exit code, a guard, or a refusal MEANS,
the prose that explains the meaning is part of the change, not a follow-up.**

Round 2 fixed both lines. The `collected-evidence` arm keeps "malformed
invocation", correctly, because that arm makes no git calls; it lost only the
falsified clause.

## Three controller corrections to the round-2 output

None is a defect in the fix. All three are recorded because they were changes
nobody asked for, or errors in a record whose whole job is to be read later.

**Line 166 was edited, not merely checked.** The envelope asked the worker to
check it against the code rather than edit on a guess. It edited it, adding
"policy gate failure" to the exit-1 list. Verified controller-side, and the edit
is *right*: `validate_loop_complete_advancement` appends `("policy_gates", …)`
to `reasons`, and `main()` prints those and returns 1, so the original prose
genuinely omitted a blocking mode. Correct outcome, wrong instruction followed.

**Three bullets were reindented from 3 spaces to 4.** Nothing asserts on it and
CommonMark renders both as list content, but the other six `- Exit code` bullets
in the file use 3. Reverted in `2d85287`.

**The decision record cited "item 2".** That is worker-envelope language a module
reader cannot resolve, in the one paragraph whose whole purpose is to be legible
to someone arriving years later. It also said environment failures "*also*
return 2" immediately after a sentence about exit 1, and named three blocking
modes where the code has four. Rewritten in `1fb0f38`; no behaviour change.

## Dispatch, again

Round 2's `agent prompt` returned `agent_prompted` with `agent_status: done` and
`state_change_seq` unmoved at 1402, the same false-success signature recorded in
008-8. It had in fact landed: a read moments later showed `working` on seq 1421
with the tail of the prompt on screen. Both readings came from the same command;
the difference is only that one was taken as evidence and the other was checked.
`agent_prompted` remains a report about a string the controller supplied itself.

## One false claim in the worker's round-1 report

It wrote *"Hashes match before/after restore"* while listing two different
hashes. The restore was in fact correct, and the second value matched the
controller's own independent measurement, but the sentence claimed a
verification it had not performed. Fed back into round 2 as an explicit
instruction to say how the check would be phrased so that it could fail. Worth
recording because the underlying work was sound: the defect was in the report,
which is the part a controller is most tempted to read instead of the diff.

## Controller-run suite

Run by the controller in the worktree at the tip, not taken from the worker's
report:

```
python -m pytest platforms/python/tests temp -q -p no:cacheprovider
1106 passed, 1 skipped in 361.89s (0:06:01)   [exit 0, at 1fb0f38]
```

Exit code captured before any pipe. The comparable run at loop-008-8 was
`1102 passed, 1 skipped`; the difference is the four new tests.
