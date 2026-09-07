# loop-002-4 — fixtures for both run contracts, and the validator they needed

**Todo:** `loop-002-4` (phase-6, ralph-loop-002). `allowed_paths: ["platforms/python/tests/"]`.
**Outcome asked for:** *"The schemas are enforced rather than published, and each rule has a case
that proves it fires."*

**Executed by:** opencode / Qwen3.5 397B (ELM), herdr agent `envelope-schema`, same worktree and
branch. **Result:** commits `bcbd871` (validator) and `48f5c19` (fixtures), merged fast-forward
into `fix/shared-runtime-reachability`. Local only.

Split into two dispatches — the validator first, under its own tests, before anything depended on
it. Qwen's 8k output cap makes a single 1,500-line dispatch unreliable, and a fixture suite built
on an unproven validator is worth nothing.

---

## First: this todo's own check #4 cannot fail

The check reads *"ast_check still reports dependency-free"*. It cannot report otherwise here:

```
ci.yml:85   python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/
```

`platforms/python/tests/` is the **only** directory this todo is allowed to write to, and it is
exactly the directory the dependency check excludes. `core/constraints.json` says so in its own
notes: *"Test files under platforms/python/tests/ are exempt from this constraint (pytest is
allowed in tests)."*

So a worker could have imported `jsonschema` into the validator and CI would still have printed
`0 violations`. This is the third check in this loop that reports green over ground it does not
examine — after job 2's `json.loads` (002-1) and the worker's own six-rule self-report (002-2).
The dependency claim below is therefore established by **grepping the diff**, not by the check
that nominally covers it. Verified: `re`, `typing`, `json`, `pathlib`, `pytest` only.

## Part 1 — the validator, and the failure that would have gone to CI

`platforms/python/tests/minischema.py` (374 lines) plus `test_minischema.py` (548 lines, 73
tests). Hand-written because `jsonschema` is a production dependency this repository does not have
and the todo explicitly says to prefer a hand-written validator over raising one.

Its keyword set is **closed, and measured** — I enumerated what the two schemas actually use
before writing the envelope, rather than letting the worker guess a subset:

> assertions: `type enum const required properties additionalProperties items contains minItems
> minLength maxLength pattern allOf anyOf if/then/else` — annotations parsed and ignored:
> `$schema title description default format`

**Anything else raises `UnsupportedKeyword`.** That is the whole point of writing it by hand. Job
2 today calls `json.loads` and nothing more, so `{"requried": ["run_id"]}` parses and the
constraint silently does not exist — 002-1 proved that by running it. A permissive validator would
reproduce the same hole one level up: every invalid fixture would still "fail validation", for the
wrong reason, and the suite would stay green over nothing. `oneOf` is deliberately excluded too,
since 002-2 showed it was the wrong tool for rule 2.

### The worker reported "73 passed". The tests did not import.

Run the way CI runs them (`ci.yml:81`, `python -m pytest platforms/python/tests/` from the
repository root):

```
platforms\python\tests\test_minischema.py:18: in <module>
    from minischema import (
E   ModuleNotFoundError: No module named 'minischema'
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.92s
```

Note **Interrupted**. This is not one red file — collection aborts, so all 527 previously-passing
tests run **zero** times. The worker's 73 was genuine but produced from a different working
directory, one where `platforms/python/tests/` happened to be on `sys.path`. Fixed to
`from platforms.python.tests.minischema import ...`, the form every other module here already uses.

**Second defect, also invisible to CI:** `minischema.py:7` had `from __future__ import
annotations`. `core/constraints.json` does not merely omit `__future__` — it lists it under
`explicitly_excluded`, with the reason recorded. The AST check that would have caught it is the
one excluded above. Removed in favour of the `typing` forms, so the file would pass unchanged if
that exemption were ever lifted.

### Verified controller-side: 34 of 34 against the real library

Not the worker's harness, and not the worker's cases — the **same** case sets already measured in
002-2 and 002-3, re-run with `minischema` and `jsonschema` side by side:

```
external-task-envelope   14 of 14 agree
collected-evidence       20 of 20 agree

a typo'd keyword: {'requried': [...]}       raises UnsupportedKeyword: 'requried' at root
an unknown type value: {'type': 'objekt'}   raises UnsupportedKeyword: Unrecognised type value
oneOf, deliberately unsupported             raises UnsupportedKeyword: 'oneOf' at root
a typo nested inside properties             raises UnsupportedKeyword: 'maxLenght' at /properties/x
a typo inside an allOf branch               raises UnsupportedKeyword: 'reqired' at /allOf/0
a non-schema object: {'hello': 'world'}     raises UnsupportedKeyword: 'hello' at root

both real schemas: no unsupported keyword
```

The two cases 002-1 ran through job 2's logic and watched pass — `{"requried": [...]}` and
`{"hello": "world"}` — now fail loudly, and so do typos nested inside `properties` and `allOf`,
which is the part a shallow guard misses.

## Part 2 — the fixtures, and why the obvious assertion was wrong

13 fixtures under `platforms/python/tests/fixtures/run-contracts/`: 2 valid, 11 invalid. The
schemas are read from `core/state/` on disk — **not copied into the fixture tree**, because a copy
drifts and then the suite tests the copy.

The todo's check says each invalid fixture must assert *the specific* error, since a fixture that
merely "fails validation" would still fail after a typo in the field name and would silently stop
testing the rule in its own filename. My first instinct was to require exactly one error per
fixture. **Measuring first showed that would have been wrong**: two of the five mandatory cases
legitimately produce two errors.

```
sync task, allowed_paths missing   n=2  required @/required  AND  required @/allOf/1/then/required
implementation, isolation=shared   n=1  anyOf @/allOf/0/then/anyOf
credential-shaped extra field      n=1  additionalProperties @/api_key
base_ref with no base_sha          n=1  required @/required
policy omits a gate                n=1  required @/policy
abbreviated base_sha               n=2  minLength AND pattern, both on /base_sha
```

So each fixture carries two assertions instead: the named error is **present** (matched on
`schema_path`, never on message text), and — the one that matters — **repairing the single named
defect makes the document completely valid, zero errors.** A typo elsewhere survives the repair
and leaves the document invalid, so the suite fails and says the fixture is not testing what its
name claims.

### A finding about rule 3, from measuring rather than assuming

`allowed_paths` is already in the schema's **root** `required` list. So the mandatory fixture —
a sync task with `allowed_paths` absent — fails twice over, and rule 3's conditional is
**redundant for the absence case**. The conditional does unduplicated work only for the empty
array, via `minItems: 1`.

Both fixtures are kept: `envelope-sync-allowed-paths-missing.json` because the todo names it, and
`envelope-release-allowed-paths-empty.json` because that is the one that actually isolates the
rule.

### The design defect is now pinned by a test, not a note

`evidence-status-review-required.json` is design §9.3's worked example **verbatim**, filed as
*invalid* — because §9.3 sets `"status": "review_required"` and §10's state machine has no such
state. 002-3 resolved that in favour of §10. Now anyone who runs the suite sees the contradiction,
instead of it living only in an evidence file. **Correcting §9.3 in the design document is still
outstanding** — outside this todo's `allowed_paths` in both loops. Carried.

### Verified controller-side against an independent oracle

Every fixture re-validated with `jsonschema` — not with the worker's validator, so the fixtures
are checked by something that shares no code with the thing under test:

```
valid/    2 of 2 valid
invalid/ 11 of 11 invalid, across 8 distinct keywords:
          required  minLength  additionalProperties  contains
          const     minItems   type                  enum
```

Eight distinct failure reasons over eleven fixtures, against a requirement of five.

### The two guard assertions were mutation-tested, not accepted

The worker said it had broken a fixture on purpose and seen the repair test fail. Checked directly
rather than believed, both mutations applied and reverted in the worktree:

```
remove a root-required field from envelope-credential-field.json
  -> FAILED test_invalid_fixture_is_valid_once_repaired[envelope-credential-field.json]
     1 failed, 25 passed

add an unregistered fixture file to invalid/
  -> FAILED test_every_invalid_file_is_in_the_table
     1 failed, 25 passed

restored: git status clean, 26 passed
```

Without the first, the whole suite could be vacuous and look green. Without the second, a fixture
could quietly stop being asserted on.

## Suite

**626 passed, 1 failed**, and the arithmetic closes exactly: 527 before this todo, plus 73
validator tests = 600, plus 26 fixture tests = 626. The single failure is the pre-existing
`test_sandbox_leaves_real_working_tree_untouched`, which fails identically on `main`.
`ast_check`: `NONE -- 15 file(s) checked, 0 violations`.

The worker reported "598 passed, 1 failed, 28 skipped". The real numbers are 626 passed and
**zero** skipped. Its artefacts were sound; its arithmetic was not — which is the third time in
this loop its self-report has diverged from measurement, and the third time it did not matter,
because the controller measures.

## Routing note

The correction pattern held again: send the **measured failing output and the fix's shape**, not a
verdict. One round each time. Worth noting what the two rounds were actually about — neither was a
reasoning failure. 002-2's was a JSON Schema semantics error; 4a's was an environment error, a test
that passed from one working directory and could not even import from the one CI uses. Both are
cheap for a controller to catch and expensive to discover in CI, which is a reasonable division of
labour rather than a reason to reroute.

## Carried

- Correcting §9.3's `review_required` in the design document — now named in two evidence files and
  one fixture, still not done.
- `checks` still has no `minItems: 1` (raised in 002-3); an empty array remains valid, so no
  fixture covers it.
- The `--exclude tests/` blind spot itself: `minischema.py` is a library module living under
  `tests/` and is unreachable by the dependency check. Nothing is wrong today, and the todo's
  `allowed_paths` left no alternative location, but the exemption is worded as being about pytest
  and now covers 374 lines of non-test code.
- **002-5 inherits its real work from 002-1 and now has the tool for it.** Job 2 proves only that
  a file parses. `minischema.check` raises on exactly the class of defect job 2 waves through, and
  the two schemas are proven to be fully within its supported set.
