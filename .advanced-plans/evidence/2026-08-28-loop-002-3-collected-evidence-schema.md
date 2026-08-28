# loop-002-3 — the collected-evidence schema

**Todo:** `loop-002-3` (phase-6, ralph-loop-002). `provider: opencode`, `worktree_owner: herdr`.
**Outcome asked for:** *"Evidence has a shape the controller can check, and the schema itself
says the worker's prose is not the evidence."*

**Executed by:** opencode / Qwen3.5 397B (ELM), herdr agent `envelope-schema`, same worktree and
branch as 002-2. **Result:** `core/state/collected-evidence.schema.json`, 145 lines, draft-07,
commit `e7dff56`, merged fast-forward into `fix/shared-runtime-reachability`. Local only.

---

## Verified controller-side, 20 of 20

Run with an independent harness against the real file — not the worker's own script:

```
status enum   : declared prepared running blocked review completed failed interrupted cancelled
policy required: path_scope_passed  tests_passed  independent_review_passed
root required : schema_version run_id status agent git checks policy agent_summary collected_at
additionalProperties (root): False

the valid §9.3 example (status corrected to 'review')   PASS  ok
policy missing independent_review_passed                FAIL  ok
policy missing tests_passed                             FAIL  ok
policy missing path_scope_passed                        FAIL  ok
policy omitted entirely                                 FAIL  ok
status 'review_required' (the §9.3 typo)                FAIL  ok
status 'done'  / status 'idle' (Herdr observations)     FAIL  ok
status 'interrupted' accepted (ACC-11)                  PASS  ok
all nine §10 states accepted                            PASS  ok
git.base_sha abbreviated to 7 chars                     FAIL  ok
extra top-level api_key                                 FAIL  ok
credential field smuggled into agent{}                  FAIL  ok
checks[].exit_code as a string                          FAIL  ok
                                                        20 of 20
```

**Clean on the first attempt**, unlike 002-2. The difference was the envelope: it carried the
two defects 002-2 had actually committed (duplicate keys, vacuously-passing branches) as named
traps. The worker also *ran* its own verification this time and reported real output whose
results match the controller's independently — the correction changed its behaviour, not just
its prose.

## The four requirements

1. **Nested `git`, `checks`, `policy`, `agent` match §9.3.** Each has its own `properties` with
   types; both SHAs are patterned `^[0-9a-f]{40}$`; `checks[].exit_code` is an integer.
   `additionalProperties: false` on the nested objects too, which is what makes the
   smuggled-credential case fail inside `agent{}` rather than only at the root. **Expressed.**

2. **`agent_summary` is one evidence item and is not trusted.** **Documented, not expressed** —
   correctly, and the schema says so itself rather than leaving the reader to notice:

   > *"Worker-supplied prose summary. This is ONE evidence item and is NOT trusted — the
   > collector independently computes changed paths, diff summary, commit identity, and check
   > exit codes. Documented here because JSON Schema cannot encode trust boundaries; consumers
   > must treat this as untrusted self-report."*

   This satisfies the todo's outcome literally: the schema itself says the worker's prose is not
   the evidence.

3. **`status` drawn from the §10 lifecycle, including `interrupted`.** All nine states, and it
   rejects both the §9.3 typo and Herdr's own vocabulary. **Expressed.**

4. **All three policy gates required**, and `policy` itself required at the root, so a result
   cannot be silent about a gate it did not run. **Expressed.**

## A design defect fixed, not worked around

Design **§9.3's worked example sets `"status": "review_required"`. §10's lifecycle names that
state `Review`.** There is no `review_required` state in the state machine.

loop-002-1 flagged this and deliberately deferred it here rather than settling it in a location
decision. The resolution: **§10 governs, and `review_required` is an error in §9.3's example.**
§10 is the normative state machine and this todo's own check requires the enumeration to be
"drawn from the §10 lifecycle". The schema uses `review`, and the invalid-fixture set now pins
that — `review_required` is a *rejected* value, so the design's own example would fail
validation.

**The design document still contains the wrong value at §9.3.** Correcting the spec is not in
this todo's `allowed_paths` and is not done here. It is carried.

§10 also states that `completed`, `failed` and `cancelled` are the only *terminal* states, and
that `idle`, `done`, `blocked` and `unknown` are Herdr lifecycle observations rather than AAW
states. Note `blocked` **is** a valid AAW status — it appears in the state diagram; it is merely
not terminal. It is retained in the enum, and the terminal/non-terminal distinction is recorded
in the field description rather than encoded.

## Carried, from the worker's ambiguity list

1. **`checks` may be an empty array.** It is required, but has no `minItems`, so a result can
   carry zero checks while `policy.tests_passed` still asserts a verdict. The todo did not ask
   for `minItems`, so this is not a defect against the spec — but it is a gap worth an invalid
   fixture in **002-4**, and a decision on whether zero checks is ever legitimate.
2. **`agent.native_session_id` format is unconstrained.** §9.3's value
   (`"reported-by-herdr-integration"`) is plainly a placeholder, not a format. Left as a
   non-empty string.
3. **`git.head_sha` when a run fails.** Whether it should equal `base_sha` for a failed run is
   unstated; the schema permits either.

Carried from **002-2** and still open: where the shared-write override is authoritatively
recorded, and whether `required_evidence`'s enum should be closed at all.

## State after this todo

`core/state/` now holds six schemas; CI job 2's logic parses all six. The advanced-planning
branch is 13 commits ahead of `main`, **entirely local — no push has ever been approved for
that repository**. Suite: **527 passed, 1 failed**, the failure being
`test_sandbox_leaves_real_working_tree_untouched`, which fails identically on `main` and points
at an unrelated checkout path.

Next: **002-4** (≥5 invalid fixtures, each failing for a different named reason, no new
dependency) and **002-5** (CI wiring). 002-1 and 002-2 have between them already established
what 002-5's real work is — job 2 proves only that a file parses, and a schema that parses while
silently dropping a rule is not hypothetical: it happened in 002-2 and would have shipped.
