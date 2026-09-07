# loop-008-2 — the gate gets a CLI, and the dispatch path that hid it is closed

Date: 2026-09-02
Repository: advanced-planning
Branch: `loop-008-gate` (base `loop-007-integration` at `9fd6796`)
Worktree: `~/.herdr/worktrees/advanced-planning/loop-008-gate`
Provider: opencode / Qwen3.5 397B, herdr worker `gate-impl` in `w23:p1`
Discharges: criterion 4

## What landed

| commit | author | change |
|---|---|---|
| `794059b` | worker | Part A: the CLI — `collected-evidence` and `loop-complete` subcommands |
| `512a409` | worker | Part B: `ap_launcher` rejects a module with no `__main__` instead of exiting 0 |
| `f1cf589` | worker | three defects found by controller verification, plus one latent quote-style bug |
| `b9e00cd` | worker | a fifth defect: `default_worker_scope` called but never imported |
| `1ddda86` | worker | four regression tests for `f1cf589` |
| `e7b04ed` | controller | two of those four tests could not fail; rebuilt so they can |

Every worker commit carries both required trailers, verified by grep on each.

## Part B, verified independently

The worker's own before-measurement had stopped testing Part B: it used
`evidence_gate` as the CLI-less subject, and Part A had just given that module a
CLI. Re-run with subjects the controller chose, base launcher against current,
same fake runtime root:

| module | base `9fd6796` | after `512a409` |
|---|---|---|
| `scope_policy` | rc 0, silent | **rc 3** + diagnostic |
| `minischema` | rc 0, silent | **rc 3** + diagnostic |
| `no_such_module_xyz` | rc 3 | rc 3 (unchanged control) |
| `evidence_gate` | rc 2 | rc 2 (positive control) |

## Five defects found by controller verification

All five were found here, none taken from the worker's report. Each is the same
class the loop exists to remove: a check whose subject is a value the checker
supplied rather than a fact read off the machine.

1. **The mutually-exclusive verdict flags were an OR, not a XOR.** Passing both
   exited 1 and proceeded, silently preferring `--verdict`, so
   `--no-verdicts-requested` could be passed and have no effect. Now rc 2,
   naming both flags.
2. **A failing `git diff` became an empty measurement.** `subprocess.run(...,
   check=False)` with `returncode` never read turned a nonexistent ref into
   empty stdout, printed as VACUOUS — the identical message a legitimately empty
   diff produces. An operator revises the baseline for one and distrusts the
   worker for the other. Now rc 1 `BAD BASELINE` carrying git's own stderr.
3. **Part B deleted the `ImportError` handler.** The file-existence pre-check
   covers "module absent" but not "module present, its own import fails" — a
   stale checkout, which is what the deleted handler was written for. Proven
   against a fake root: base rc 3 with a diagnostic, `512a409` an uncaught
   `ModuleNotFoundError` exiting 1, breaking the exit-code contract in the one
   case it was written to hold.
4. **A latent quote-style false negative.** The `__main__` detection required a
   double-quoted `"__main__"`, so a single-quoted module would be rejected as
   CLI-less. No module in the tree uses single quotes today, so it was latent.
5. **`default_worker_scope` was called but never imported.** Every
   `loop-complete` invocation reaching past the VACUOUS early return raised
   `NameError` — present and inert since `794059b`, with the suite green
   throughout. Nothing invoked `main(["loop-complete", ...])` on a path that got
   that far, and the only mention of the name in the tests asserted it appears
   as a **string in a markdown document**. A test that checks a name is written
   down, while nothing runs it, is the same silent-pass class as the gate being
   fixed.

Defect 5 was reachable only *because* defect 2 was fixed: both earlier probes
returned at the VACUOUS branch and neither got to the call. The controller's own
instrument had been masking it.

## Final state, measured at `e7b04ed`

`collected-evidence`:

| invocation | result |
|---|---|
| both flags | rc 2 "mutually exclusive", naming both |
| neither flag | rc 2 usage |
| `--no-verdicts-requested` alone | rc 1 `policy_self_review` |

`loop-complete`, three distinguishable outcomes as the todo required:

| baseline | result |
|---|---|
| `nosuchref_xyz` | rc 1 `BAD BASELINE: git diff failed with exit code 128: fatal: ambiguous argument …` |
| `HEAD` | rc 1 `VACUOUS: changed_paths is empty …` |
| `9fd6796` (real) | **rc 0**, silent |

`ap_launcher` against a fake runtime root: broken import → rc 3 + diagnostic;
single-quoted `__main__` → the module's own exit 7 propagates.

## The tests, and why two of them did not work

`1ddda86` added four tests, one per fix. Two of them could not fail.

`test_single_quote_main_accepted` ended on

    assert result.returncode != 3 or "no __main__ block" not in result.stderr

one line after asserting that same right-hand side, so the disjunction was
already true — a check that cannot fail, inside the loop whose subject is checks
that cannot fail. Its docstring said it asserts the module "returns its own exit
code"; nothing asserted any exit code.

`test_bad_baseline_says_bad_baseline_not_vacuous` ran in a bare `tmp_path`,
which is not a git repository, so **both** git calls failed and the assertion was
satisfied by the uncommitted-diff branch rather than the baseline branch it
names. Measured: mutating the baseline returncode check away left the test
**green**.

Both rebuilt in `e7b04ed` — an assertion on exit code 42, and a real repo with
two commits so `git diff` succeeds while `git diff <bad-ref> HEAD` exits 128.

## Mutation proof — controller-run, all four

Each case carries `TestPolicySelfReview` as a positive control in the same run,
and restores the source byte-exact with a sha256 comparison rather than by eye.
The harness refuses to run when the pattern count differs from the expected
number of sites, which is what caught D1 having two guard sites, not one.

| mutation | mutated | restored | verdict |
|---|---|---|---|
| D1 verdict-flag XOR (2 sites) | 1 failed, 8 passed | 9 passed | PINNED |
| D2 baseline returncode read | 1 failed, 8 passed | 9 passed | PINNED |
| D3 `ImportError` handler | 1 failed, 8 passed | 9 passed | PINNED |
| D4 quote-style match | 1 failed, 8 passed | 9 passed | PINNED |

`evidence_gate.py` sha256 `6f58914fb3e90f71210d7cdf5e9d8f7fe6f9f10a9c1faf290e700261e6115f77`
and `ap_launcher.py` sha256 `acb8b1c71eafc1dd18c3143fc918baf3b421e7f3155928191ecd9f2e96b257ed`
identical before and after every case.

## Suite

Controller-run, whole directory, on a tree with no worker activity:

    1ddda86   1076 passed, 1 skipped in 515.28s
    e7b04ed   1076 passed, 1 skipped in 479.82s

The worker reported **975 passed, 6 failed, 96 skipped** from its own pane on
`1ddda86`. Its pane has no Git Bash, so roughly a hundred tests skip or fail
there for environmental reasons. This is not a defect in the code and not
dishonesty in the worker — but it is a standing fact about verification here:
**a worker's suite number is not comparable to the controller's, and cannot be
accepted in place of one.** The worker had twice previously reported the
two-file figure (83) as though it were the directory.

## Findings recorded, not fixed

- `test_evidence_gate.py:713` asserts `"default_worker_scope"` appears as a
  string in a markdown step. It is not a test of behaviour and it is what let
  defect 5 survive. Left in place; the CLI tests added here cover the execution.
- The missing-policy-block branch added by 008-7 is still unreachable
  (recorded in that loop's evidence, deliberately left).
- Both new launcher tests assert on `"is not in the runtime"`, which
  `ap_launcher` emits from **two** branches — the module-absent pre-check and
  the `ImportError` handler. The assertion cannot say which fired. It still
  discriminates the mutation it was written for, so it works as a guard, but a
  broken fixture would pass it silently.

## What did not happen

No push, no tag, no PR, no merge. The six commits sit unpushed on
`loop-008-gate` in the worktree. Both times the worker raised an
"Access external directory" dialog for `%TEMP%`, the dialog was surfaced to the
operator and answered by them; neither was answered by the controller.
