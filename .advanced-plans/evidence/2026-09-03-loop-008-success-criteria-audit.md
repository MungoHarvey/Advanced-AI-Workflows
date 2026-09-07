# loop-008 success criteria — audited against the code, not the narrative

Date: 2026-09-03
Subject: `.advanced-plans/phases/phase-6/loops.md`, the loop-008 success criteria block (lines 1385-1392)
Repository under test: advanced-planning, branch `loop-008-gate` at `8cf17b5`

All eight loop-008 sub-loops closed, but the block's seven checkboxes had never been
checked against anything. Ticking them because the loops finished would be the
defect this programme exists to remove, so each was measured. Four are ticked.
**Three are not, and this note records why**, so the next reader does not mistake
an unticked box for an unexamined one.

| # | criterion | verdict |
|---|---|---|
| 1386 | launcher can no longer exit 0 having checked nothing | **met** |
| 1387 | the router runs the gate at BOTH sites before the advancement is logged | **not met as worded** |
| 1388 | the three failure modes distinguishable by exit code and message | **not met on the exit-code half** |
| 1389 | a module lacking `__main__` fails a test derived from the shipped commands | **met** |
| 1390 | `validate_advancement` / `can_advance_loop` exposed or deleted, decisions recorded | **half met** |
| 1391 | the gate reads the policy block it is handed | met, under loop-008-7 |
| 1392 | criterion 4 measured pass and fail on a non-Claude host | met, under loop-008-6 |

## 1386 — met

Six invocations of `ap_launcher`, each exit code captured **before** any pipe:

| invocation | rc |
|---|---|
| no subcommand | 2 |
| bogus subcommand | 2 |
| a module with no `__main__` | 3 |
| a nonexistent module | 3 |
| gate without `--baseline` | 2 |
| gate without the verdicts flag | 2 |

None is 0. The pre-fix failure — dispatch succeeds, nothing runs, exit 0 — is
unreachable through any of these.

## 1389 — met

`platforms/python/tests/test_dispatchable_modules.py` derives the invocation list
from the shipped command text rather than from a hand-written list, and carries a
negative control: `assert has_main_block("scope_policy") is False`. Without that
control the test would pass on a `has_main_block` that returned `True`
unconditionally. Ran: 4 passed.

## 1387 — not met, and the reason is a decision rather than an omission

The criterion asks the router to **run the gate** at both sites. The F5 fix in
loop-008-8 chose the opposite for the `resume` site: it refuses to finalize and
hands the operator the command to run with a baseline they supply. The block says
why — after a crash the step-6 baseline SHA is gone, because it lived in the
session and was never persisted, so the gate cannot run there and running it on a
guessed baseline would make it meaningless.

That is the better behaviour and the criterion is the thing that is now wrong. It
was written before the difficulty was understood. Two consequences carry forward:

- the `resume` branch no longer validates `loop-ready.json` at all, since the two
  `state_validate` lines were removed with the finalize path;
- any future "both sites" wording must say *runs or refuses with the reason*, not
  *runs*.

## 1388 — not met on the exit-code half

loops.md line 1272 names which three modes are meant: *"a path-scope violation, a
VACUOUS measurement, and a schema failure."* Measured against the shipped gate:

| mode | source line | rc |
|---|---|---|
| VACUOUS — empty changed set | `evidence_gate.py:719` | 1 |
| path scope | `evidence_gate.py:741` | 1 |
| schema invalid | `evidence_gate.py:571` / `743` | 1 |
| clean control | | 0 |

All three are exit 1. So they are distinguishable by **message only**. The messages
do carry the information the criterion wanted — `path_scope: <path> (<reason>)`
prints every violating path, VACUOUS names the baseline as the thing to check, and
F3 made the schema arm name the offending field rather than print a bare count —
but an operator branching on `$?` cannot tell them apart.

Worth noting the exit space is not empty: `2` is reserved for malformed invocation
and is used at fifteen sites, and the launcher adds `3`. Three distinct codes for
the three modes were available and were not taken. Four git-subprocess failures
also return 1, which is a fourth class sharing the code.

Not fixed here. Whether to split the codes is a design decision with a real
argument on both sides — a single "blocked" code is easier to script against than
three — and it belongs to whoever next opens the module, not to a checkbox audit.

## 1390 — half met

- `validate_advancement` is exposed: `__all__` at `evidence_gate.py:81-87`.
- `can_advance_loop` is deleted: absent from the entire source tree. The only
  remaining hit is a stale `.pyc`, which is not a reference.

So both names are settled, which is the first half. The second half — *"the
decisions are recorded in the module"* — is not done. Nothing in
`evidence_gate.py` says `can_advance_loop` was removed or why, and a reader
arriving from an older call site finds silence rather than an answer. Grepping the
module for `removed`, `deleted`, `no longer exported` returns nothing.

That is the whole of the shortfall, and it is a two-line comment's worth of work.
It is left undone deliberately rather than slipped in: this branch is finished and
unpushed, and an edit made outside a loop is an edit nothing measured.
