# loop-003-4 — mutation-testing the audit, and the two tests that asserted nothing

**Todo:** `loop-003-4` (phase-6, ralph-loop-003).
**Repository:** `advanced-planning`, branch `loop-003-hostneutral`, commits `93c698b` (worker),
`f35b4a6` (controller).
**Executed by:** `opencode`, Qwen3.5 397B (ELM), agent `hostneutral`, pane `wS:p1`.
**Outcome asked for:** *"The audit is proven to fail, which is what makes a green run mean anything
— a check that never fails is not a check."*

The todo as written was the mutation test. Reading the suite before dispatching it turned up
something larger: **two of the tests already there did not do what their names said, and one of them
was the test I had accepted, in writing, as the proof of the exception mechanism.**

---

## Correction to loop-003-3's evidence

`2026-08-28-loop-003-3-core-made-host-neutral.md` says of the exception mechanism:

> covered by `test_excepted_file_fails_on_different_rule`, which proves an excepted file still fails
> on a rule it was not excepted for. Without that test the mechanism would be unproven, and an
> allow-list nobody has tried to slip past is not an allow-list, it is a hope.

**That was wrong when I wrote it.** The test existed, was named that, had a docstring saying exactly
that — and did not do it. Its body wrote to `core/skills/test-skill/SKILL.md`. The only key in
`EXCEPTIONS` is `("core/skills/permission-config/SKILL.md", "host-permission-syntax (…)")`, and the
lookup is on the repo-relative posix path (`path_audit.py:336`), so the fixture never matched an
exception at all. The test wrote a **non-excepted** file, got a violation, and passed for a reason
with nothing to do with suppression. It duplicated coverage that already existed three tests above
it.

So for the duration of loop-003-3 the exception mechanism had **zero** test coverage, and I had
recorded the opposite. I accepted it on the strength of its name and its docstring, which is the
precise failure this phase keeps documenting in other people's work. A dated correction note now
sits on that paragraph in the 003-3 evidence.

## The second one, which was worse and more obvious

```python
    def test_main_returns_zero_with_suppressed_only(self, tmp_path):
        """main() returns exit code 0 when only suppressed exceptions exist (no violations)."""
        # The main() function prints suppressed but exits 0 if no violations
        # This is tested implicitly by the clean tree test since exceptions are file-specific
        pass
```

A docstring making a claim, a comment explaining why the claim needs no code, and `pass`. It was
counted among the 21 tests reported as passing in the 003-3 evidence, including by me.

The worker gave it a real body rather than deleting it — it now asserts `main()` returns 0 **and**
that `SUPPRESSED` and `permission-config` appear in stdout, so it covers the printing requirement
that 003-3 introduced and nothing had checked.

**This is the sixth check in phase 6 found reporting green over ground it does not examine**, after
CI job 2's `json.loads`, the worker's six-rule self-report, `ast_check --exclude tests/`, the design
document never validated against its own schemas, and the near-miss `CLEAN` headline in 003-3. It is
the first one that was in a test file, and the first that was mine.

## The proof I demanded, and then ran myself

A test for an allow-list that still passes with the allow-list deleted is not testing the allow-list.
So rather than accept the rewritten test on its name — again — I emptied `EXCEPTIONS` and ran the
suite:

```
EXCEPTIONS: dict = {}          (temporarily)

FAILED  TestCleanTreePasses::test_main_returns_zero_with_suppressed_only
FAILED  TestExceptionMechanism::test_excepted_file_fails_on_different_rule
2 failed, 20 passed

restored → 22 passed, git status clean
```

Both suppression tests are now load-bearing: remove the mechanism and they go red. Neither did
before this todo.

The rewritten `test_excepted_file_fails_on_different_rule` writes to the **exact** excepted path
under `tmp_path` and asserts both halves, which is what makes it a test of the mechanism rather than
of the rule:

- the `settings.json` line appears in `suppressed` with its reason and **not** in `violations`;
- the `.claude/skills/` line **on the same file** is a violation.

An exception that suppresses one rule while another still fires on the same file is the entire
claim of a `(file, rule)` key. Nothing had tested it.

## The mutation itself

**Live, on a real file** — the loop asks for this and it is not the same as a fixture:

```
plant  .cursor/rules/ in a core/skills SKILL.md   → exit 1, "VIOLATIONS -- 2 found"
revert                                            → exit 0, "PASSED WITH 7 SUPPRESSED"
git status --short                                → empty
```

I ran my own independently during 003-3 against
`core/skills/companion-detection/SKILL.md`: exit 1 naming `companion-detection\SKILL.md:70`, restore,
exit 0, clean tree.

**Permanent, as a fixture** — `TestMainExitCodes::test_main_exits_one_on_host_directory_violation`.
The gap it fills is specific: every host-neutrality test in the suite called `audit()` and inspected
the returned list. `main()` was exercised only for a clean tree and for a deprecated-token hit, so
**nothing asserted that the command exits 1 on a host-neutrality violation** — the thing CI actually
depends on. It now builds a `core/skills` fixture with a `.cursor/` reference, asserts
`main(["--root", …]) == 1`, and captures stdout to assert the file name, the line number and the
rule name are printed.

## The half the fixture test was missing

As delivered it asserted the red half and stopped. A check that has only ever been seen going red on
a tree built to make it go red has not been shown to distinguish the two states — which is the whole
claim a mutation test exists to support, and the loop puts it as *"a check that never fails is not a
check."* The symmetric hazard is a check that never passes.

Added in `f35b4a6`: the same test rewrites the file without the token, on the same tree, and asserts
the same command returns 0. That is the round trip the todo asked for, expressed as one test rather
than two halves that could drift apart.

Also noted and left alone: the line-number assertion is `"1:" in captured.out or ":1:" in
captured.out`, which is weak — `"1:"` matches any line number ending in 1, and could match part of a
path. It does not make the test wrong, and tightening it is not worth a fifth round trip on this
worker. Recorded so it is not discovered later as a surprise.

## Verification — controller-side

```
git log --oneline -3     f35b4a6, 93c698b, 99a937d on loop-003-hostneutral
git status --short       clean            ← the live mutation left nothing behind
git diff --stat 99a937d  platforms/python/tests/test_path_audit.py only, +61/-14 (worker)
```

Only the test file was changed. `core/` is untouched, which is the check the todo's
*"git status is clean afterwards; the mutation leaves nothing behind"* asks for, and it is the one
place a mutation test can quietly corrupt the thing it is testing.

```
python -m pytest platforms/python/tests/test_path_audit.py -q
    22 passed in 0.81s                       (12 → 19 → 21 → 22 across this loop)

python -m pytest platforms/python/tests/ -q          # repository root
    1 failed, 636 passed in 33.37s

python -m platforms.python.ast_check platforms/python/ --exclude tests/ --exclude examples/
    NONE -- 15 file(s) checked, 0 violations

python -m platforms.python.path_audit ; echo $?
    exit 0   (7 suppressed, all core/skills/permission-config/SKILL.md)
```

The single failure remains the pre-existing `test_self_heal_integration.py::
TestFullSyntheticRemediationTrace::test_sandbox_leaves_real_working_tree_untouched`, identical on
`main`.

## A note on how both defects were found

Neither was found by reading the worker's reply, and neither would have been. Both were found by
reading the test file before writing the envelope — the same move that found the scoping defect
before 003-2 and the `\bTask\b` false positives after it. The pattern across this loop is
consistent: **the failures are in the checks, not in the code the checks cover**, and they are
visible only to someone who reads the check itself rather than its result.

## Carried into 003-5 and beyond

- The line-number assertion in the new fixture test is weaker than it looks.
- `test_main_returns_zero_with_suppressed_only` now asserts on stdout containing `SUPPRESSED` and
  `permission-config`. That couples a test to the exception table's *contents*: retiring the
  permission-config exception — which is the stated goal — will break it. That is arguably correct
  (retiring an exception should require touching its test), but it should be a deliberate choice
  rather than a surprise when someone does the relocation.
- Everything still open from 003-1 to 003-3 stands: the `core/schemas/` + `core/state/` gap, the
  `permission-config` relocation, the `PreToolUse`/`PostToolUse` vocabulary hole, and the nine
  `path_audit.py` module defects — of which the silently swallowed `OSError` and `_is_excluded`'s
  unanchored substring matching can still make a green run mean nothing.
