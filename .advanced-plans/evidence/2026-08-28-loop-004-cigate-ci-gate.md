# loop-004-cigate (unplanned) — making the adapter suite a gate that can fail

- **Date:** 2026-08-28
- **Repository:** `advanced-planning` (LOCAL ONLY — no push has ever been approved)
- **Branch:** `loop-004-cigate`, based on `loop-004-opencode` (`b458a51`)
- **Worker:** `cigate`, opencode / Qwen3.5 397B via the ELM proxy, pane `wW:p1`
- **Commits:** `05918a5` (worker), controller tidy on top
- **Status:** complete

## Why this was inserted

loop-004-3 closed having found **three separate checking instruments reporting
green over ground they never examined** — a `grep` in single quotes searching a
literal that cannot occur, five fixtures seeding a sibling adapter as their own
"foreign" owner, and a path audit whose scanned-root list omitted the 1,755-line
directory it was cited as approving.

All three were found by hand. **Nothing in CI could have failed on any of them.**

Worse, the obvious remedy — "wire the adapter suite into CI" — would not have
worked, because of a fourth instance of the same defect sitting inside the
remedy itself.

## The trap, measured before anything was changed

`test_adapter_lifecycle.py` has 74 cases (37 × 2 adapters). Every one begins
`_skip_if_no_sh() if lang == "sh" else _skip_if_no_pwsh()`, and those helpers
called `pytest.skip(...)` when the interpreter was absent. So on a runner missing
an interpreter, the cases evaporate and the job exits 0.

Two baselines were taken **on the pre-change tree**, so they cannot have been
tuned to whatever the worker produced:

| Baseline | Command | Result |
|---|---|---|
| **A** | `.advanced-.advanced-` violation planted under `setup/claude-code/`, then `path_audit` | **exit 0 — not caught** |
| **B** | adapter suite with `pwsh` stripped from `PATH` | **32 passed, 42 skipped, exit 0** |

Baseline B is the decisive one: **42 of 74 cases vanish and the job still reports
success.** That is the "before" half of every discrimination below.

## What the worker did, and what it honestly did not

Three files, all in scope, tree clean: one line into `DEFAULT_SCANNED_ROOTS`, an
`AP_REQUIRE_ADAPTER_INTERPRETERS` escalation in both skip helpers, and two `ci.yml`
steps (a `command -v` assertion, and the env var on the pytest invocation).

It reported that **proofs 3 and 4 were beyond it** — it could not strip `pwsh`
from its own `PATH` mid-session — and did not claim them. That is the second
consecutive worker on this branch to decline a proof it could not run rather than
manufacture a pass, and it is the envelope working as intended.

Every escalation proof below is therefore controller-side.

## Controller verification

`verify-cigate.sh`, six groups, run against the two baselines.

**1. `ci.yml` parses, and the gate is in the parsed structure.** Asserted against
the object returned by `yaml.safe_load`, never against raw file text — a worker on
this repository previously left `ci.yml` as invalid YAML having run its Python four
times without once parsing the file it had edited. Four jobs parse; the assert step
exists, **precedes** the pytest step, and the env var is on the same command line
as `pytest`. No other job runs the adapter suite unguarded.

**2. `setup/claude-code/` is now load-bearing.** Planted violation → **exit 1**,
naming `setup\claude-code\install.sh:543 [doubled-prefix]`. Reverted → **exit 0**,
`PASSED WITH 7 SUPPRESSED`, tree clean. Against Baseline A's exit 0, the one-line
addition is proven to be doing work rather than decorating a list.

**3. Escalation on.** `AP_REQUIRE_ADAPTER_INTERPRETERS=1` with `pwsh` stripped:
**8 failed, 32 passed, 34 errors, exit 1**, and the message
`AP_REQUIRE_ADAPTER_INTERPRETERS=1 but 'pwsh' interpreter not found` appears 84
times. The 8 failures plus 34 errors are exactly the **42** cases that Baseline B
had silently skipped — the split is only whether the helper is reached from a
fixture or a test body. Nothing was recovered or lost in the conversion.

**4. Escalation off by default.** Same stripped `PATH`, variable unset:
**32 passed, 42 skipped, exit 0** — byte-identical to Baseline B. The developer
without PowerShell can still run the suite, which was the regression most worth
avoiding.

**5. Both helpers escalate.** `/usr/bin` cannot be stripped from `PATH` without
destroying the shell, so the `sh` side was exercised by driving `shutil.which`
directly. All four combinations behave: `sh` and `pwsh` each raise under the
variable and skip without it.

**6. Nothing else changed.** Both interpreters present, variable set: **74 passed,
0 skipped, exit 0.** The skip count is now zero rather than 42 — which is the whole
point, stated as a number.

## The fifth instance of this loop's defect class, and it was mine

Proof 2 first reported `FAIL — audit output names the offending file: not named`,
against an audit that had named it perfectly. `path_audit` prints an **absolute
path with the platform separator**:

```
C:\Users\...\loop-004-cigate\setup\claude-code\install.sh:543: [doubled-prefix (.advanced-.advanced-)]
```

My check grepped for `setup/claude-code/install.sh` — forward slashes, a literal
that cannot occur on Windows. Repaired to a separator-agnostic pattern and proven
by two-way discrimination:

| | clean tree | planted violation |
|---|---|---|
| repaired check | 0 | **1** |
| original check | 0 | **0** ← could not fail either way |

This is the same defect as the single-quoted `$ADAPTER`, the `parts[i-1]` count
parse, and the hard-coded sibling seed: **a check whose subject is a string it
interpolated, rather than a fact it read from disk or the process.** Four rounds of
stating that rule did not stop me writing it a fifth time. It was caught only
because the check was run in both directions rather than once.

## Controller tidy on the worker's code

`import os` had been added twice — once above the guard in `_skip_if_no_sh`, once
inside the guard in `_skip_if_no_pwsh`. Consolidated to a single module-level
import alongside the existing block, leaving the two helpers symmetric. Behaviour
identical; re-verified by a full re-run of all six groups.

**A finding I withdraw:** I first flagged the two trailing-whitespace lines the
worker introduced. The file carried **118 such lines before it and 120 after** —
that is the file's own norm, not a deviation, and no CI job lints style. Not a
defect; nothing changed.

## Carried

- **The one premise I cannot prove from here:** the new step fails the job if
  `command -v pwsh` finds nothing on `ubuntu-latest`. GitHub's Ubuntu runner images
  do ship PowerShell 7, but **I have not measured it** and cannot from this machine.
  If that assumption is wrong the job turns permanently red on the first push — a
  loud failure rather than a silent one, which is the intended direction, but it is
  the one claim here resting on documentation instead of a measurement. It is
  checked for free on the first CI run this branch ever gets.
- The `python-tests` job is a 3-way matrix over Python 3.10/3.11/3.12, so the
  assertion runs three times per push. Intended, not free.
- Property 2 still has no mutation coverage; the clobber mutation only visits
  *approved* skills and the foreign entry is deliberately not approved.
- `test_self_heal_integration.py:586` still fails on its own hard-coded absolute
  path. Pre-existing, fails on `main`, untouched.
- Properties 3/6/9/10/11/14/16/21 still have no mutation coverage.

## The thing this loop is actually about

The previous loop's finding was that three instruments were green over nothing. The
finding here is narrower and worse: **the obvious fix for that contained a fourth
instance of it**, and the harness written to verify the fix contained a fifth.

The rule survives contact with the evidence: these failures live wherever a check's
subject is a string it built, and the only reliable defence is to run every check in
both directions and require it to *change*. Every green in this document is paired
with a red from the same check.
