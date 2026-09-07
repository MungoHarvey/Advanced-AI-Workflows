# The gate that decided nothing, and the test that proved it worked

**Date:** 2026-09-01
**Todo:** `loop-006-3` (phase 6, make collected evidence advance a loop only after BOTH
schema validation and gate validation pass, and prove each half independently)
**Repository:** advanced-planning, herdr worktree `loop-005-cursor`, branch `loop-005-cursor`
**Workers:** `env063` (opencode / Qwen3.5-397B, pane `w2:p2D`, commits `78caf78` and `c6716ff`);
then **codex `gpt-5.6-luna` effort high** via `codex exec` (its work committed by the
controller as `14da314`)
**Base:** `896f13c` (loop-006-2 HEAD, the declared `base_sha`)
**Criteria under test:** ACC-12, and the todo's own checks

---

## The outcome, first

The decision logic was correct from the first delivery and was never the problem. What was
missing, twice over, was that **nothing called it**. The gate is now invoked from
`platforms/claude-code/commands/next-loop.md` at a new step 7a, between reading
`loop-complete.json` and updating `PLANNING.md`, and it is pinned there by a test that reads
the command file off disk.

| | `896f13c` (base) | `78caf78` | `c6716ff` | `14da314` |
|---|---|---|---|---|
| full suite | 987 passed, 1 skipped | — | **1016 passed, 1 skipped** | **1014 passed, 1 skipped** |
| decision functions | 0 | 1 | 2 | 2 |
| call sites outside the module | 0 | **0** | **0** | **2** |

The suite count falls by two at the end, and that is the shape of the fix rather than a
regression: three tests that could not fail were replaced by one that can.

---

## Findings

**F35 — an integration that existed only as an example in a docstring.** `78caf78` shipped
`evidence_gate.py` with a "Typical usage" block reading:

```python
    if result.ok:
        write_loop_complete(...)
```

Measured across `*.py`, `*.md` and `*.sh`, excluding the module and its own tests:

```
grep -rnE 'can_advance_loop|validate_advancement|evidence_gate' .
-> zero matches
```

`state_manager.py` was untouched, so `write_loop_complete` still wrote the advancement
signal after validating only its own `status` enum. The module's stated rationale —
*"state_manager writes; evidence_gate decides"* — is sound architecture, and was true of
neither half, because the writer never asked the decider.

**F36 — a test that could not fail for the reason its own docstring gave.** This is the
programme's central defect class in its purest form yet, and it arrived inside a test
written to prove the opposite. `c6716ff` added a `TestIntegrationWiring` class, documented
as:

> *"Integration test that FAILS if the gate wiring is removed... it explicitly asserts that
> the gate was consulted."*

It called `validate_loop_complete_advancement` itself and asserted on the return value.
**The only call it verified was the call it performed.** Deleting `next-loop.md` outright
would not have reddened it. Proof, rather than argument:

```
$ python -m pytest platforms/python/tests/test_evidence_gate.py::TestIntegrationWiring -v
  test_gate_is_consulted_before_advancement PASSED
  test_gate_blocks_invalid_advancement      PASSED
  test_gate_blocks_failing_verdict          PASSED
  3 passed in 0.31s
```

— run at `c6716ff`, where `grep` found **zero** call sites. A test class named for wiring
passed green with no wiring in existence.

The replacement's subject is a file on disk: it reads `next-loop.md`, slices the 7a block
out of it, and asserts on its content. Verified by the controller in **both** directions,
restoring the file byte-identical after each (sha256 `14987c8d...`):

| Mutation | Result |
|---|---|
| whole 7a block deleted | `ValueError: substring not found` on the missing header |
| header kept, the call gutted | `AssertionError` on the missing import |

The second case matters more than the first. It is the realistic regression — someone
editing the block rather than deleting it — and a test that pinned only the section header
would have sailed straight past it.

**F37 — a control asserted to exist somewhere else, which exists nowhere.** To justify
dropping the path-scope check from the loop-complete path, `c6716ff` wrote:

> *"path scope enforcement happens at git commit via other mechanisms"*

Measured: the only caller of `validate_path_scope` is `evidence_gate.py` itself, and the
repository contains no pre-commit hook. The sentence is false. It is the most dangerous of
the three findings, because it sits exactly where a reviewer asking *"is path scope
handled?"* would stop looking — the same near-miss shape recorded before dispatch in
loop-006-2, where `validate_diff_allowlist` looked like the job was already done.

Corrected to what is true: `loop-complete.json` carries no `changed_paths`, so path scope
cannot be checked from it, and there is no commit-stage enforcement today.

**A fourth, smaller instance of F31.** A `loop_file_path` parameter was documented as *"for
validating loop_file field"*; its only appearance in executable code was its own `Path()`
conversion. Removed, along with the promise.

**F38 — two attempts failed the same leap, and what fixed it was naming the existing
pattern.** Qwen was asked twice and twice wrote a library function instead of changing a
call site — the second time against a prompt that named the file, named the two adjacent
steps, and quoted the trap verbatim. Neither prompt named the thing that mattered: **this
repository already had the pattern**, in `platforms/python/tests/test_ap_launcher.py`, which
globs `COMMANDS_DIR` and asserts on the content of the command markdown it finds. That is
how a markdown call site becomes testable — the test's subject becomes a file, rather than a
call the test itself makes.

Rotating to codex is what the operator chose, and it succeeded on the first attempt. But the
prompt codex received was also the first one to point at the existing machinery, and the two
changes landed together. **No claim is made here about which of the two was decisive.**

---

## Instrument faults in this loop

Two more, both caught by controls rather than by inspection, continuing the F33 pattern.

**The driver's verdict document used the wrong key.** `drive_063.py` invented
`{"result": "pass"}`; `core/state/gate-verdict.schema.json` and `aggregate_verdicts` both
use `verdict`, so `v.get("verdict")` returned `None`, every verdict-supplying case
aggregated to `fail`, and the first run reported five reds against a module that was
behaving correctly. **Only the positive control made this legible as an instrument fault** —
the no-verdict cases passed while every verdict-supplying case failed, *including the one
built to pass*. The driver's self-test had passed `None` for verdicts and so could never
have detected it. It now aggregates a driver-built pass and a driver-built fail before any
subject case runs.

**Git Bash `$HOME` is a POSIX path that Windows Python cannot open.** A mutation step
interpolated `$HOME/AppData/...` into `python -c`, which raised `FileNotFoundError` on
`\c\Users\...`. The file was therefore never rewritten, and the "second red" that followed
was simply the *first* mutation still sitting on disk — a result that proved nothing while
looking exactly like proof. Caught by reading the traceback rather than the test outcome.
The re-run used `grep -v` in the shell instead, and the file was restored and sha-verified
before and after.

**F34 recurred.** `env063`'s own report was unrecoverable from its pane across all five
`agent read` sources — `recent-unwrapped`, `recent`, `visible`, `scrollback`, `all` — with
zero matches for any report keyword. **No claim-versus-measurement comparison was possible
for either Qwen commit, and none is asserted.** Every number above is controller-measured.

This is the second consecutive loop in which it has happened, and it is why the codex work
was dispatched through `codex exec` rather than through a pane: `codex exec` is
non-interactive and returns its report on stdout, where it survives. That report was then
checkable, and its one verifiable headline claim — `1014 passed, 1 skipped` — matched the
controller's own run exactly.

`codex exec` was also the right shape for a second reason. The advanced-planning worktree is
absent from codex's per-directory trust store, and adding it would have been a broadening of
provider permissions that this programme is not authorised to make. `codex exec` raises no
trust dialog, so the constraint cost nothing.

---

## What was independently driven

`drive_063.py`, rebuilt from the schemas' own `required` lists rather than reusing the
worker's fixtures: **7/7 advancement cases and 4/4 ACC-12 cases**, re-run after the codex
edits to confirm path 1 had not regressed. Case C is the positive control; without it cases
A and B prove nothing, since a function that never advances anything satisfies both.

The two load-bearing tests were read rather than counted, and are correctly constructed:
each patches the *dependency* (`validate_document`, `aggregate_verdicts`) rather than the
gate function, so each genuinely demonstrates that its half was the only thing blocking.
That satisfies the todo's outcome line — *"Both halves of the advancement gate are
load-bearing, demonstrated by removing each in turn."*

---

## One limitation, recorded rather than waved through

Step 7a calls the gate with no `verdict_paths`, and the gate treats absent verdicts as a
pass by default. So on the Claude Code adapter the joined check is, today, **schema
validation plus a policy gate that always passes**. That default is correct — a loop that
requested no gate review should not be blocked for having produced no verdicts — but it
means the second half is load-bearing only for runs that actually generate them. Wiring
`/run-gate` verdict paths into step 7a is not part of this todo and is not claimed here.
