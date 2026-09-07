# loop-009-3 — criteria 3 and 4, and three rounds to get a guard that could fail

Date: 2026-09-07
Repository: `advanced-planning`, worktree `loop-009-gatewiring` (based on `loop-009-envelope`)
Commits: `def4e5c`, `f5b60b5`, `88ec3e8` — all opencode/Qwen worker `gatewiring-fix`
Closes: phase 6 success criteria 3 and 4, both of which Codex failed and the in-house
agents passed at attempt 3

## The two defects

Both were the programme's central defect class: a gate answering a question using a
value the caller supplied rather than a fact read off the machine.

**Criterion 4.** `validate_advancement` gate 2 ended in an `else` branch that set
`gate_result = {"result": "pass", "conflicts": [], "missing": []}` under the comment
*"No gate review requested — policy gate passes by default"*. `--no-verdicts-requested`
is documented and shipped on both subcommands, so the shipped route reached that
literal. "No policy gate ran" and "the policy gate passed" are different facts and the
gate reported the second when the first was true.

**Criterion 3.** Gate 3 read `changed_paths` from `evidence.git.changed_paths` — a
document written by the worker being audited. The worker chose the input to the check
that policed it. The sibling `validate_loop_complete_advancement` already did this
correctly, deriving paths from git via `--baseline`.

## Round 1 fixed the half nothing calls

`def4e5c` added four tests, and the suite was green at 1112. It still closed neither
criterion, which only driving the shipped command showed.

The worker made `--baseline` *optional* and left the evidence read in place behind a
comment reading *"DEFECT B: This is the vulnerable path... Kept for backward
compatibility but flagged."* A comment is not a guard. Running the exact form documented
at `SKILL.md:222`, against evidence naming one changed path while git reported two, the
second forbidden by the envelope:

| invocation | exit |
|---|---|
| `collected-evidence ev env --no-verdicts-requested` (as documented) | **0** |
| the same, plus `--baseline loop-009-envelope` | 1, `path_scope: ... (forbidden)` |

Neither documented invocation passes `--baseline`, so nothing changed in the product.
Criterion 4 had the same shape: fixed at `validate_advancement`, untouched at
`validate_loop_complete_advancement`, which is the route `SKILL.md` documents twice.

### The guard had the defect it was written to catch, for the fourth loop running

`test_worker_omission_caught_when_baseline_provided` asserted `result.ok is True`. Both
planted files were in scope, so it passed whether or not git was consulted. Disabling
the derivation outright (`if baseline is not None:` → `if False:`) left it passing while
only its sibling went red. Its docstring said *"RED half (before fix): This test would
FAIL."* It would not.

## Round 2 fixed the mechanism and left the suite red

`f5b60b5` did all four things asked, and the controller confirmed each: the evidence
read deleted outright rather than flagged, `--baseline` required on `collected-evidence`,
`not_requested` applied at both routes, git failures returning 2 under a `git:` prefix
per the module's own documented contract, and the derivation extracted to
`_derive_changed_paths_from_git` and called from both sites instead of duplicated.

It also stopped mid-task. **Nine tests failed at `f5b60b5` with nothing mutated** — the
tests that had been relying on the hole. The worker did not claim otherwise: its own
todo list still read `[•] Update existing tests to provide baseline` and `[ ] Run full
test suite`. Stopping short, not a false report, which is a better failure than the
three before it.

## Round 3 finished it

`88ec3e8` changed `test_evidence_gate.py` only — `git diff f5b60b5..88ec3e8 --
platforms/python/evidence_gate.py` is empty, so no gate was weakened to make a test
pass, which was the one prohibition the envelope carried.

## The mutation matrix, re-run after the test rewrite

A 405-line test rewrite can neuter a guard, so all three mutations were run again
against the final tree rather than carried over from round 2.

| mutation | result |
|---|---|
| `not_requested` → `pass` at `validate_advancement:309` | 1 failed |
| `not_requested` → `pass` at `validate_loop_complete_advancement:570` | 3 failed |
| `_derive_changed_paths_from_git` returns a fixed in-scope list | 9 failed |
| unmutated | 54 passed, `PYTEST_EXIT=0` |

And the shipped form that previously exited 0 on a lie now refuses to run:

```
A) SHIPPED FORM, exactly as SKILL.md:222 documents it (no --baseline):  exit = 2
   Error: collected-evidence requires --baseline <git-ref>. Changed paths must be
   derived from git, not from worker self-report.
B) same evidence, with --baseline loop-009-envelope:                    exit = 1
```

## The suite

```
1111 passed, 1 skipped in 509.51s (0:08:29)
PYTEST_EXIT=0
```

1112 before, minus the one test that could not fail and was deleted. The number
reconciles rather than merely looking acceptable.

## A breaking change, taken deliberately

`--baseline` is now **required** on `collected-evidence`. That breaks a documented
command, and `SKILL.md:216` and `:222` were rewritten to match. The operator approved
this explicitly rather than it being chosen by the worker or the controller. The
alternative considered and rejected was keeping the fallback with a loud warning, which
would have left criterion 3 failing by its own words while looking addressed.

## Controller error, disclosed

While checking round 2 the controller ran `pytest ... | tail -12; echo EXIT=$?` and
reported `EXIT=0` over `9 failed`. That was the pipeline's exit code, not pytest's — the
same trap this programme has already recorded once. The failure count was read from the
summary line instead, and every later run captured the exit code before piping.

## What this loop did not do

- Criterion 1 remains contested and is the operator's call.
- The three `loop-009-*` branches are still unconsolidated; nothing is pushed.
- Phase 6 has not been re-gated. This closes two of the three criteria that blocked it.
- Six `fence_byte_identity` failures appear in the worker's shell and not the
  controller's, because the worker's `bash` resolves to WSL rather than Git Bash. No
  product code was changed for them and none should be.

## Attribution

All three commits carry `Co-Authored-By: opencode (Qwen) via herdr worker gatewiring-fix`
and `Loop: loop-009-3`, present at creation because the envelope stated them verbatim at
every round — the enforcement point named in `docs/agents/worker-attribution.md`.
