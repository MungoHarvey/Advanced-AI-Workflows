# loop-002-5 — CI job 2 now validates the schemas it claimed to validate

**Todo:** `loop-002-5` (phase-6, ralph-loop-002). `allowed_paths: [".github/workflows/ci.yml"]`.
**Outcome asked for:** *"A malformed schema stops the build instead of shipping."*

**Executed by:** opencode / Qwen3.5 397B (ELM), herdr agent `envelope-schema`. **Result:** commit
`a81a0a6`, merged fast-forward into `fix/shared-runtime-reachability`. Local only. One correction
round.

---

## The todo's first check was already satisfied when the loop began

*"job 2 currently globs `core/state/*.json` only — after the change it covers the new files"* —
it already did. loop-002-1 established that on day one, which is why it recorded `ci_yml_change:
none` for the location decision, and why both schemas were written to `core/state/` rather than
the `core/schemas/` the phase plan's deliverable table named.

So this todo's real work was the second check, and 002-1 said so before any schema existed:

> *"loop-002-5's real work is STRENGTHENING the check, not extending the glob. Its stated
> outcome — 'a malformed schema stops the build instead of shipping' — is currently only half
> true."*

002-2 then proved it was not half true but barely true at all: the worker's first envelope schema
had duplicate `if`/`then` keys, `json.loads` silently kept the last, the worktree-isolation rule
vanished from the parsed document, and job 2 would have called the file valid and shipped it.

## The change

Job 2 keeps its parse check and adds a structural one, importing the validator 002-4 built:

```python
from platforms.python.tests.minischema import validate, UnsupportedKeyword
```

`validate({}, schema)` walks the schema and raises on any keyword or `type` value outside the
closed set. Parse failures and structural failures are reported distinctly, because a file that
does not parse and a file that parses but is not a schema are different problems.

**The `*.json` glob is kept deliberately, and that is now a feature.** 002-1 flagged the loose
glob as a latent hole — a fixture placed in `core/state/` would be silently counted as a validated
schema. Tightening to `*.schema.json` would have made such a file silently *skipped* instead. With
the structural check in place the broad glob becomes an enforced invariant: a non-schema file
dropped into `core/state/` now fails the build, because its data keys are not schema keywords.
Loud beats silent, and the rationale is recorded in a YAML comment so it does not get tidied away.
(The comment trails the step rather than heading it — a cosmetic nit, not worth a third round.)

## Verified controller-side: 5 of 5

The step body was **extracted from `ci.yml` and fed to `python -` on stdin**, exactly as the
heredoc does — so this exercises what CI will run, not a transcription of it:

```
1. baseline, untouched                      exit=0 want=0 ok
      OK: core\state\loop-ready.schema.json
      All 6 schema files valid.
2. unparseable: truncated mid-object        exit=1 want=1 ok
      PARSE FAIL: gate-verdict.schema.json: Unterminated string starting at: line 51
3. "required" -> "requried"                 exit=1 want=1 ok
      STRUCTURAL FAIL: gate-verdict.schema.json: Unsupported keyword: 'requried' at root
4. {"hello": "world"} in core/state/        exit=1 want=1 ok
      STRUCTURAL FAIL: not-a-schema.json: Unsupported keyword: 'hello' at root
5. restored                                 exit=0 want=0 ok
git status: (clean)
```

**Case 3 is the whole point.** That file is still perfectly valid JSON. Run through the *old* job
2's logic in the same session, for comparison:

```
old job 2 (json.loads only): OK -- exits 0, the constraint silently does not exist
```

Case 4 confirms the deliberate glob decision behaves as intended rather than as argued.

All six schemas in `core/state/` were checked against the strict validator **before** the envelope
was written, so the worker was not dispatched into a red build: `collected-evidence`,
`external-task-envelope`, `gate-failure-context`, `gate-verdict`, `loop-complete` and `loop-ready`
all pass.

## The correction round: a change to make the build fail, that made the build file malformed

The worker's first commit put the heredoc body at column 0:

```yaml
        run: |
          python - <<'PY'
import json          <- column 0
```

Inside a `run: |` block scalar, YAML takes the block's indentation from its first non-empty line —
here 10 spaces — and any later line indented *less* terminates the scalar. Measured:

```
yaml.scanner.ScannerError: while scanning a simple key
  in ".github/workflows/ci.yml", line 46, column 1
could not find expected ':'
```

**`ci.yml` was no longer valid YAML.** GitHub Actions parses the whole file before running
anything, so this would not have broken job 2 — it would have broken every job in the workflow. A
change whose entire purpose is to fail the build on malformed input had instead made the build
file itself malformed.

The fix is mechanical and not a workaround: indent the whole heredoc body to the block's
indentation. YAML strips the common indentation when building the scalar, so bash still receives
column-0 Python. Verified after the fix by parsing `ci.yml` and printing the reconstructed step
body.

**Why the worker's own four proofs missed it:** it ran the Python logic directly and never parsed
the file it had edited. The logic was never in doubt; the YAML was. The correction added a fifth
check and put it first — parse the workflow before testing what it contains.

That is the same shape as 002-4's first defect, where tests passed from one working directory and
could not import from the one CI uses. Twice now the worker has verified the *thing* and not the
*wiring*, and both times the wiring was what broke. Worth carrying into future envelopes as a
standing instruction rather than a per-task warning.

## My own harness was wrong first, and said so

The first run of my verification reported `3 of 5`, with the baseline case failing on
`ModuleNotFoundError: No module named 'platforms'`. That was my harness, not the step: I wrote the
extracted script to a temp file, which puts the temp directory on `sys.path` instead of the
repository root. `python - <<'PY'` reads from stdin, where Python puts the current directory on
the path. Three of the "ok" results in that run were false positives — they exited 1 for the wrong
reason. Re-run through stdin, 5 of 5.

Recorded because the baseline case is what caught it. A verification harness with only
failure-expecting cases would have reported success.

## State after this todo

`ralph-loop-002` is **complete, 5 of 5**. Suite: **626 passed, 1 failed** — the failure is the
pre-existing `test_sandbox_leaves_real_working_tree_untouched`, which fails identically on `main`.
`ast_check`: `NONE -- 15 file(s) checked, 0 violations`. `ci.yml` parses.
`fix/shared-runtime-reachability` is 16 commits ahead of `main` and **has never had a push
approved**.

## Carried

- **Correcting design §9.3's `review_required`** — named in three evidence files and pinned by an
  invalid fixture, still not done. It needs a write to the design spec, which no todo in this loop
  was scoped for.
- **`minischema.py` lives under `platforms/python/tests/`** and CI job 2 now imports it. That is an
  odd home for something the build depends on, and it sits in the one directory `ast_check`
  excludes, so its own dependency-freedom is unchecked. The obvious move to `platforms/python/`
  was outside the `allowed_paths` of both 002-4 and 002-5. Worth a todo of its own.
- **`checks` still has no `minItems: 1`** (raised in 002-3): a collected-evidence document with
  zero checks remains valid while `policy.tests_passed` asserts a verdict.
- The open envelope questions from 002-2 — where the shared-write override is authoritatively
  recorded, and whether `required_evidence`'s enum should be closed — remain open.
