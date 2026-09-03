# loop-007-9 — the launcher's upward walk, and the guard that only worked here

Date: 2026-09-03
Repository: `advanced-planning`, worktree `loop-008-gate`
Commits: `0f138de` (opencode/Qwen worker `aplaunch-fix`), `9854ade` (controller)
Discharges: the one check loop-007-8 could not close

## The question the loop was opened to answer

loop-007-8 finished with five `test_ap_launcher.py` failures that pre-dated it and
reproduced at `05d1e55^`. They appeared only after loop-007-7 installed the framework
globally — the supported installation — so the suite was red on any machine where the
product is installed the normal way. The loop asked one thing before any fix: **is that a
test-isolation gap or a product defect?**

## The verdict: both, and the split is the finding

Four of the five are a **product defect**. `find_manifest` checks for a manifest at
`ap_launcher.py:234` *before* the project boundary at `:236` and the repo boundary at
`:238`. Once `~/.advanced-plans/runtime.json` exists, the upward walk reaches the profile
and returns the **global** record as though it were a project manifest.

The design had already ruled that out in writing. `Boundary`'s docstring
(`ap_launcher.py:190-200`) says both boundary kinds mean *"stop looking upward for a
project manifest; the global record is consulted next"* — the global record is reached
through `resolve()`'s explicit `global_manifest()` call at `:298-299`, and by no other
route. The walk finding it is the silent borrowing the boundary mechanism exists to
refuse, arrived at by a path nobody guarded.

`test_find_manifest_walks_up_and_stops` predicted it in its own comment: *"without the
boundary stop, any uninstalled project on such a machine would adopt whatever manifest the
home directory came to hold."* The home directory came to hold one.

The fifth, `test_missing_manifest_is_reported_as_such`, is a genuine **isolation gap**. It
ran the launcher without a clean environment, so it fell through to the developer's real
global install — which is correct product behaviour, wrongly observed. It now passes
`env=_clean_env(tmp_path / "empty-home")`.

I had predicted a single verdict. The split is the worker's, and it is right.

## The fix

`find_manifest` stops when the walk reaches the profile directory, returning `None` rather
than raising `Boundary`. That distinction matters and was the first thing checked: a
`Boundary(home, "project")` would have failed the very test it was meant to fix, because
that test's `except` branch asserts no `runtime.json` at the boundary directory — and at
the profile, that file now exists.

A second branch stops the walk at any strict ancestor of the profile. It fires only for a
caller starting at or above `C:\Users`, so it is close to unreachable; it is not wrong, and
it is left alone rather than churned.

## The guard was a coincidence, not a check

The worker's commit message claims the fix is *"necessary and sufficient"*. It is
necessary **on this machine**. Measured:

```
FIX REMOVED, fixtures under the profile (this machine):
  4 failed, 45 passed
FIX REMOVED, fixtures outside the profile (--basetemp C:\Temp\aptest, the CI case):
  49 passed
```

Those four tests only fail where the profile holds a global record *and* pytest's
`tmp_path` sits beneath it. On CI the fix could be reverted and nothing would notice. A
check that needs the developer's machine to be installed a particular way is not a check —
it is this programme's central defect class, one level down from where it was found.

So the controller added `test_the_walk_refuses_the_profile_record_on_any_machine`, which
**builds** the situation instead of borrowing it: a temporary profile holding a global
record, an uninstalled project beneath it, `USERPROFILE`/`HOME` pointed at it, and the walk
required to refuse.

**Mutation check, in the case that matters:**

| mutation | fixtures | result |
|---|---|---|
| remove the profile boundary | outside the profile (CI) | `test_the_walk_refuses_the_profile_record_on_any_machine` FAILED — the only failure of 50 |
| restore it | outside the profile (CI) | 50 passed |

The 49 pre-existing tests pass straight through that regression. The new one is what
catches it.

## The suite

Green for the first time since loop-007-6. Was 5 failed, 1092 passed; 1092 + 5 + the
one new test = 1098, so nothing was quietly dropped to get there.

```
1098 passed, 1 skipped in 541.73s (0:09:01)
```

## Attribution

**Corrected 2026-09-03, during the phase 6 gate.** This section previously said that
`0f138de` carried no `Co-Authored-By: opencode (Qwen) via herdr worker aplaunch-fix`
trailer and that `05d1e55` had the same gap. Both statements are false. Running
`git log -1 --format=%B` on each commit shows both trailers present, and `git reflog`
shows every entry as `commit:` with author date equal to commit date, so the trailers
were there at creation and were not amended in later.

The error was found by the gate's own `code-review-agent`, which opened the commits.
I had not. That is this programme's central defect class committed by its controller:
a claim about an artefact, asserted without reading the artefact. The convention itself
is sound and still holds, but the observation that motivated writing it down was wrong,
and there was no attribution gap to record.
