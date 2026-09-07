# loop-008-8 — five gate defects closed, and a sixth that only the combination revealed

Date: 2026-09-03
Repository: advanced-planning
Branch: `loop-008-gate` (base `loop-008-3` at `f209e54`)
Worktree: `~/.herdr/worktrees/advanced-planning/loop-008-gate`
Provider: opencode / Qwen3.5 397B, herdr worker `gate-fix` in `w2:p2F`
Discharges: criterion 4

## What landed

| commit | author | change |
|---|---|---|
| `6497c87` | worker | F1–F5: the two silent passes, the unreadable failure, the cwd dependency, and the third advancement path |
| `8cf17b5` | worker | the residual the controller measured between F1 and F4 |

Three files across the two commits: `platforms/python/evidence_gate.py`,
`platforms/python/tests/test_evidence_gate.py`, and
`platforms/shared/agent-skills/advanced-planning/SKILL.md`. Nothing in
`.advanced-plans/` or `core/` was touched by either commit, and the tree is
clean at `8cf17b5`.

## How it was checked

Interventionally, not by reading the diff. Two throwaway **installed** projects
were built from `git archive` exports — one from the pre-fix commit `f209e54`,
one from the fix — and the same 13-scenario script was run against each. The
script is byte-identical between runs; its `pre|post` argument changes only the
**expected** column, never what executes. Every loop-complete scenario carries a
real committed in-scope change and prints its committed set, so the VACUOUS
guard cannot fire and be mistaken for the fix.

| scenario | on `f209e54` | on the fix |
|---|---|---|
| F1 positive control — one in-scope commit | rc=0 | rc=0 |
| F1 mixed — untracked forbidden + committed in-scope | rc=0 **silent** | rc=1 names `loop-ready.json` |
| F1 mixed — staged forbidden + committed in-scope | rc=0 **silent** | rc=1 names `history.jsonl` |
| F1 regression guard — tracked, modified, unstaged | rc=1 | rc=1 names `.claude/settings.json` |
| F4 in-scope change from the project root | rc=0 | rc=0 |
| F4 the same change from `src/` | rc=1 **spurious** | rc=0 |
| F1×F4 untracked forbidden, from `src/` | rc=1 **wrong reason** | rc=1 names `loop-ready.json` |
| F4 second arm — forbidden path from `src/` | rc=1 | rc=1 names `.claude/settings.json` |
| F2 control A — in-scope path, envelope permits `src/` | rc=0 | rc=0 |
| F2 control B — same path, envelope permits nothing | rc=1 | rc=1 names `src/app.py` |
| F2 the defect — empty `changed_paths`, envelope permits nothing | rc=0 **silent** | rc=1 |
| F3 collected-evidence arm | bare count | names `run_id` |
| F3 loop-complete arm | bare count | names `todos_done` |

13/13 after round two. The controls matter as much as the defects: a gate that
had simply started refusing everything would pass six of these rows and fail the
other seven.

## The sixth defect: a fix that moved a defect rather than closing it

The F1×F4 row is the finding, and neither fix's own test could see it.

`git diff` reports repository-relative paths whatever the process cwd, but
`git ls-files --others --exclude-standard` is scoped to the cwd's own subtree
and prints paths relative to it. So closing F1's untracked hole and closing F4's
cwd dependency, each correct alone, combined into a gate that was blind to an
untracked forbidden file whenever it ran from a subdirectory — **precisely the
case F4 existed to make safe**. F4's fix removed a spurious refusal that had
been accidentally masking F1's hole.

The pre-fix column reads `rc=1` on that row and is not a pass. It named
`src/app.py (not_allowed)` — the F4 bug — while the actual forbidden file was
invisible. A refusal for the wrong reason is not a refusal, and only a run that
reads the stderr text rather than the exit code can tell the two apart. The
fixed gate names `.advanced-plans/state/loop-ready.json (forbidden)`.

It was isolated rather than guessed: in the same post-fix run a **committed**
forbidden write was still caught from `src/`, which is what proves `git diff` is
repo-wide and pins `git ls-files` as the cwd-dependent call. `8cf17b5` moves the
`git rev-parse --show-toplevel` resolution above all three git subprocesses and
runs each with `cwd=repo_root`, so no input the gate collects depends on where
the operator stood. No `os.chdir` in the library.

## Mutation, done by reversion

Round one reported *"Mutation verification: Not performed"*, on the grounds that
the tests were written green-first against fixed code. That does not reach the
question. Green-first says the test passes now; the requirement is that it would
**fail** if the fix were removed, because a test that passes either way cannot
protect the fix from a future edit.

Done controller-side, by reverting the whole production file rather than
mutating one line — a stronger intervention, since it removes every part of the
fix at once:

| new test class | own gate | pre-fix gate |
|---|---|---|
| `TestF1StagedForbiddenDetection` (2 tests) | pass | **fail** |
| `TestF2EmptyChangedPathsInValidateAdvancement` | pass | **fail** |
| `TestF3SchemaErrorsToStderr` (2 tests) | pass | **fail** |
| `TestF4RepositoryRootResolution` | pass | **fail** |
| `TestF1F4UntrackedForbiddenFromSubdirectory` | pass | **1 failed, 1 passed** |

Six of six round-one tests fail on `f209e54`'s gate. None is dead weight.

The last row is the most informative and was run against `6497c87` — the commit
immediately before the fix it pins. Reverting breaks the defect assertion while
leaving the positive control green. That asymmetry is what a control is for: it
shows the class is not passing merely because everything passes.

The worker performed its own mutation in round two, reverting `cwd=repo_root`
from the `ls-files` call and reporting a matching sha256 pair either side of the
restore. That is the right method, and it is also narrower than the reversion
above — which is why the controller ran its own.

## Two existing tests were edited, and the edits are legitimate

`TestLoadBearingSchema::test_disable_schema_check_case_a_advances` and
`TestPolicySelfReview::test_policy_all_true_advances` both changed
`"changed_paths": []` to `["platforms/python/test.py"]`. That is a consequence of
F2 rather than a weakening: an empty list is now correctly refused, and neither
test's actual subject — schema load-bearingness, policy self-review — depends on
the list being empty. Their comments were updated to say so rather than left
stale.

## F5: the decision, and the difficulty it names

The `resume` finalize branch now refuses to finalize and directs the operator to
run the gate manually with a supplied baseline. The block says why: after a
crash the baseline SHA recorded at step 6 is gone, because it lived in the
session and was never persisted, so running the gate is impossible and running
it with a guessed baseline is unsafe.

That is the harder of the two available answers and it states the real
difficulty rather than papering over it. One consequence to carry: the branch no
longer validates `loop-ready.json` at all, since the two `state_validate` lines
were removed with it.

## The harness caught its own defect first

The first pre-run printed `f1_staged`'s committed set as
`['.advanced-plans/state/loop-ready.json', 'src/app.py']` — the *previous*
scenario's untracked file. `git checkout -b` drops neither untracked nor staged
files, and `git add -A` then swept it into the commit, so the scenario would
have reported a refusal for the wrong reason. Fixed by committing only named
paths, unlinking an enumerated scratch list, and asserting
`git status --porcelain` is empty at the start of each scenario. No `git clean`
and no `git reset --hard` anywhere.

Checking the instrument before the subject is what kept a contaminated harness
from producing a confident wrong verdict about the worker.

## The dispatch failed twice, silently, in the programme's own defect class

Worth recording because it is the same failure the loop is about.

The round-two brief was sent as a 4016-byte multi-paragraph prompt and was
submitted only as far as its **first blank line**. That opening paragraph was
praise for round one, so the worker answered a question nobody asked —
*"Confirmed. All five defects (F1-F5) are fixed and verified in commit
6497c87"* — in 17.9s, and settled `done`. A second attempt broke on PowerShell's
native-argument quoting around the embedded double quotes, and delivered
nothing.

Both failures returned success. `agent prompt` replied `agent_prompted` each
time, and `--wait` returned immediately on the worker's pre-existing `idle`, so
the controller saw exit 0 and a JSON success for a prompt that was never
delivered. Taking that as evidence of dispatch would have been exactly the
defect this loop closed in the gate: **a check whose subject is a string it
supplied itself.** Delivery was established instead by reading the worker's
`agent_status` reach `working` on a moved `state_change_seq`, and by finding the
*tail* of the prompt on screen.

Recorded as a machine-level operating memory, since it is not specific to this
programme.

## The 008-3 harness needed a change, and it is an improvement

F5 added a second shipped block containing `evidence_gate loop-complete`, so
`run_008_3_scenarios_v2.py`'s uniqueness guard would have refused. Taking the
first by line order would have been a positional assumption. It now selects by
**structure**: site 1 is the gate whose own `state_validate` sits within 12
lines above it, and the `resume` site has none, because the F5 fix removed those
lines. The count is printed rather than assumed, so a third site appearing is
visible instead of silently absorbed.

Confirmed discriminating on both installs before use — 2 gate sites post-fix, 1
pre-fix, the same site 1 chosen in each, and the new `resume` site correctly
reading unpaired. The harness then re-ran 6/6 unchanged in substance, with the
invalid-document scenario now naming `/todos_done` rather than a bare count,
which is F3 visible through the shipped operator path.

## Controller-run suite

Run by the controller in the worktree at `8cf17b5`, not taken from the worker's
report:

```
python -m pytest platforms/python/tests temp -q -p no:cacheprovider
1102 passed, 1 skipped in 407.33s (0:06:47)
```

Exit 0, captured before any pipe. The comparable run at loop-008-4 was
`1080 passed, 1 skipped in 437s`, so the +22 are the new classes across the two
commits and nothing that previously passed has started failing or been removed.
The one skip is the same long-standing one.

## A stale docstring the fix left behind

Found while preparing loop-008-6, after this loop was recorded. The module
docstring of `platforms/python/evidence_gate.py` still says, of the
loop-complete path:

> Path scope is NOT validated because loop-complete.json does not contain
> changed_paths, so path scope cannot be checked from it. There is no
> commit-stage path-scope enforcement today.

That was true before F1 and is false after it. The `loop-complete` subcommand in
`main()` now derives the changed set from git and runs `validate_path_scope` over
it, which is the whole of what F1 added and what the thirteen scenarios above
measure. The code is right and the prose above it describes the code it
replaced.

Not fixed here, deliberately: this loop is closed and its branch is finished.
Recorded so the next loop that touches the module corrects the docstring rather
than trusting it. It is a documentation defect with a real cost — a reader
deciding whether the commit-stage gate exists gets the wrong answer from the
first thing they read.
