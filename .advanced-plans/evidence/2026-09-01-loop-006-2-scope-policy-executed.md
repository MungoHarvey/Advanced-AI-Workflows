# ACC-08 stops being a sentence, and the guard that enforces it fails open

**Date:** 2026-09-01
**Todo:** `loop-006-2` (phase 6, make ACC-08 an executed test: a worker that attempts a
planning-state edit fails collection, and programme state does not advance)
**Repository:** advanced-planning, herdr worktree `loop-005-cursor`, branch `loop-005-cursor`
**Worker:** `env062`, opencode / Qwen3.5-397B, pane `w2:p2C`
**Base:** `68b6902` (loop-006-1 HEAD, the declared `base_sha`)
**Commits:** `7777227` (worker, the module), `896f13c` (worker, the boundary fix)
**Criteria under test:** ACC-08 and ACC-13, from
`.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md` §15

---

## The outcome, first

The programme risk register says *"the worker/controller boundary is documented but not
enforced"*, and names this todo as the mitigation. It is now enforced by
`platforms/python/scope_policy.py`, keyed on **the envelope's own** `allowed_paths` and
`forbidden_paths` — so a different envelope produces a different verdict — with 37 tests
that execute it rather than describe it.

| | at `68b6902` | at `7777227` | at `896f13c` |
|---|---|---|---|
| full suite | 950 passed | 975 passed | **987 passed, 1 skipped, exit 0** |
| tests in the new module | — | 25 | **37** |

The substance of this record is not that the module landed. It is that a **green
975-test suite concealed a fail-open hole in the very guard the todo exists to build**,
and that the hole was found only by driving the function with inputs the worker had not
chosen.

---

## Findings

**F31 — a comment that says "ensure" above code that ensures nothing.** `_pattern_match`
matched by bare string prefix:

```python
if path.startswith(pattern):
    # Ensure it's a proper directory prefix (e.g., "foo/" matches "foo/bar")
    return True
```

Measured against the delivered `7777227`:

```
validate_path_scope(["platforms/pythonista/evil.py"], ["platforms/python"], FORBIDDEN)
-> (True, [])
```

A sibling directory whose name merely begins with an allowed path read as **in scope**.
This fails **open**, on the **allow** side, which is the dangerous direction — the forbid
side over-matching would merely have been strict.

It is reachable, not theoretical: `external-task-envelope.schema.json` constrains
`allowed_paths` items to `{"type": "string", "minLength": 1}` and nothing else. No
trailing slash is required, so an envelope written without one is perfectly valid and
silently widens the worker's scope to every sibling sharing the prefix.

The comment is the finding. A guard whose documentation asserts a check its code skips is
the risk register's own sentence — *documented but not enforced* — reproduced inside the
mitigation for that sentence. Fixed in `896f13c`: a prefix match now requires a `/`
boundary, and the docstring describes what the code does.

**F32 — the traversal case was synthetic, and only the schema could say so.**
`validate_path_scope(["platforms/python/../.advanced-plans/state/x.json"], …)` returns
`ok=True`; `_normalise` converts backslashes and resolves no `..`. That looks identical to
F31 from the outside, and the tempting move was to fix both.

It is not a defect, and the reason is one level down in the schema:

- `git`: *"Git state computed independently by the collector — **not trusted from worker
  prose**"*
- `git.changed_paths`: *"Paths modified in this run, **computed from git diff by the
  collector**"*

`git diff --name-only` emits no `..` segments, so the input cannot occur. Guarding it
would have been dead code defending against a shape the pipeline cannot produce. **The
distinction between F31 and F32 came entirely from reading the schema description to the
end** — the same field's description had been truncated mid-sentence in an earlier dump,
and the truncated half was where the answer lived. The module now records the dependency
in its docstring rather than testing for it.

**F33 — three instrument faults in one verification pass, and the positive control caught
the worst.** The controller's own verifier reported reds against a module that was fine,
three separate times:

| Reported | Actually |
|---|---|
| `import failed: No module named 'platforms'` ×3 | `sys.path[0]` is the *script's* directory, not cwd |
| `(False, 'not_allowed')` on all three cases | bound `is_path_in_scope` (one path) and fed it a **list** |
| `FAILED on 1/10 — precedence` | the traversal probe of F32, mislabelled |

The middle one is the instructive one. The verifier discovered its callable from the diff
— correctly refusing to assume a name — then **guessed the signature by position**, fell
through a `TypeError` into a second guess, and got a function that answers `not_allowed`
to everything. Every case failed, *including the positive control*, and that is the only
reason it was visible as an instrument fault rather than believed as a subject fault. A
verifier without a positive control would have reported a broken guard and been believed.

Binding is now by **parameter name** via `inspect.signature`, with a check that fails
VACUOUS if no discovered callable accepts `changed_paths` at all.

**F34 — the worker's own report is not recoverable from the pane.** `agent read` at
`--lines 400` across `recent-unwrapped`, `recent`, `visible`, `scrollback` and `all`
returns exactly one surviving line of env062's report: `Commit SHA: 896f13c`. The
narrative — which module it chose, which node ids it added, its own suite lines — is gone
from the buffer.

So **no comparison between the worker's claims and the measurements was possible**, and
none is asserted here. Every number in this document is controller-measured from the diff,
the driven function, and unpiped pytest runs. That is the stronger position, but it was
not a choice; it should not be recorded as one.

---

## What was independently driven

Not a re-run of the worker's suite — a suite can be green while asserting the wrong thing.
Two drivers, both with instrument self-tests that assert the harness can see a pass *and*
a failure before any subject case runs.

`drive_062.py` — **9/9**. ACC-08 across three programme-state paths (`loop-complete.json`,
`PLANNING.md`, `history.jsonl`), ACC-13 for merely-out-of-scope and sibling-directory
paths, two positive controls, a mixed diff, an empty diff. Every failure names the
offending path, which ACC-13 requires in its own words.

`drive_062b.py` — **12/12**, written for the boundary fix and deliberately two-directional.
Six cases assert the sibling is now rejected on both the allow and forbid sides; six assert
the fix did **not** over-correct — descendants still match with and without a trailing
slash on the pattern, exact matches still hold, and forbidden still beats allowed. A
boundary fix that stopped matching descendants would have traded a fail-open for a
fail-closed, and the worker's own suite, written in the same turn by the same model, is the
least likely thing to notice that.

---

## Two things found before dispatch

**The worker could not read its own acceptance criteria.** ACC-08 and ACC-13 live in the
AAW controller checkout, which the advanced-planning worktree cannot see, and they appear
nowhere in the advanced-planning repository. They were quoted verbatim into the envelope
rather than referenced.

**The enforcement did not exist.** `platforms/python/remediation_controller.py` has
`validate_diff_allowlist(changed_paths) -> (ok, violations)` with violations
`never_touch` / `not_allowlisted` — close enough to look like the job was done. It is not:
its lists are **hardcoded module constants** scoped to gate remediation, so it cannot
express an envelope's scope, and every envelope would get the same answer. Recording the
near-miss matters, because a reviewer skimming for "is there a path check" would have
found one and stopped.
