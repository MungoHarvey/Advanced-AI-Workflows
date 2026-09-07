# Post-loop-002 — the design's two worked examples now validate against the schemas they describe

**Not a todo.** A carried item from ralph-loop-002, closed between loops on the operator's
instruction ("fix §9.3 first, then 003"). Every todo in loops 001 and 002 was scoped away from the
design document, so this could not have been done inside one without widening a worker's
`allowed_paths` to the spec that every other document defers to.

**Changed:** `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md` (AAW,
commit below) and two now-stale cross-references in advanced-planning (`b3f1b8f`, local).

---

## What was carried

§9.3's worked example set `"status": "review_required"`. §10's state machine defines nine states
and that is not one of them. 002-3 resolved the contradiction in favour of §10, 002-4 pinned it as
an invalid fixture, and by the end of the loop it was cited in four evidence files, one schema
description, one fixture and one test table — none of which is the document that was wrong.

## Fixed, and then the fix was checked rather than assumed

`"review"` is the value: §10 has the run in `Review` at exactly the point a collected result is
written, before the gates are evaluated. §9.3 now also states the rule the example was silently
carrying:

> `status` takes its value from the §10 run lifecycle, lower-cased: one of `declared`, `prepared`,
> `running`, `blocked`, `review`, `completed`, `failed`, `interrupted`, `cancelled`. […] There is
> no separate `review_required` status; §10 is the single definition of the state set, and
> `core/state/collected-evidence.schema.json` enforces it.

Then — the part that mattered — **the corrected example was extracted from the markdown and
validated against the real schema**, rather than being eyeballed. It still failed, four times over:

```
as corrected (status=review)      minischema: 4 error(s)
      /git/head_sha            minLength   String length 15, minimum is 40
      /git/head_sha            pattern     does not match '^[0-9a-f]{40}$'
      /checks/0/output_sha256  minLength   String length 6, minimum is 64
      /checks/0/output_sha256  pattern     does not match '^[0-9a-f]{64}$'
                                  jsonschema: the same 4
```

`"head_sha": "full-result-sha"` and `"output_sha256": "digest"` are prose placeholders sitting in a
document whose neighbouring field, `base_sha`, carries a real 40-character SHA. The status was
**one of three defects in that block, not one**, and only the first had been noticed in four
evidence files. Both replaced with correctly-shaped deterministic values.

## And the check found a fourth defect, in the section nobody was looking at

Having built the harness, running §9.2's example through the envelope schema cost nothing:

```
9.2 task envelope, as written     minischema: 1 error   /  required  Missing required property: 'base_sha'
                                  jsonschema: 1 error
```

§9.2 is headed **"Required fields:"**, and its own validation rules, printed six lines below the
example, say:

> the base ref is recorded as a full commit SHA alongside its human-readable ref in the database.

The example showed `"base_ref": "upstream/main"` and no `base_sha` — demonstrating the exact
anti-pattern that 002-2 wrote rule 4 to forbid and that
`platforms/python/tests/fixtures/run-contracts/invalid/envelope-base-ref-without-sha.json` exists
to reject. Fixed by adding the `base_sha` from §9.3's example, since the two blocks share a
`run_id` and are the same run; that they disagreed is itself the finding.

## Final state, measured

```
9.3 collected result, corrected   minischema 0 error(s)   jsonschema 0 error(s)
9.2 task envelope, corrected      minischema 0 error(s)   jsonschema 0 error(s)
same run_id in both examples: True
```

Two independent validators, one of which (`jsonschema`) shares no code with the other. Both
examples are now copy-pasteable, which is the only useful property a worked example has.

## The follow-through in advanced-planning

Correcting the design left two places asserting a defect that no longer exists — the sort of stale
cross-reference that makes the next reader distrust both documents:

- `core/state/collected-evidence.schema.json`, the `status` description;
- the registered `reason` for the `evidence-status-review-required` fixture.

Both reworded. **The fixture itself is unchanged.** It was never only a record of a documentation
defect — it pins that `review_required` is not a member of §10's state set, which remains true and
is now the only thing stopping the name coming back. Removing it because the document was fixed
would have deleted the guard and kept the note.

`626 passed, 1 failed` (the pre-existing failure, identical on `main`); `ast_check` 0 violations;
all six schemas pass job 2's structural check.

## The pattern this closes, and the one it opens

Loop 002 found three checks reporting green over ground they did not examine. This is the fourth
and the largest: **the design document was never validated against the schemas written from it.**
The schemas were derived from §9.2 and §9.3 by hand, tested exhaustively against fixtures written
by hand, wired into CI — and in all of that, nobody ran the source text through the result. One
throwaway script found three defects the whole loop had missed.

Worth making permanent rather than repeating: a test that extracts every `json` fence in the design
document's run-contract sections and validates it against `core/state/`. Nothing enforces it today,
so §9.2 and §9.3 can drift from the schemas again the next time either is edited. That belongs in
advanced-planning under `platforms/python/tests/`, and it is a real candidate for the next loop —
noted, not scheduled.

## Still carried

- `minischema.py` is a library module under `platforms/python/tests/` that CI job 2 imports, in the
  one directory `ast_check` excludes.
- `checks` has no `minItems: 1`, so a collected result with zero checks can still assert
  `policy.tests_passed`.
- Where the shared-write override is authoritatively recorded (envelope field vs `history.jsonl`),
  and whether `required_evidence`'s enum should be closed to §9.2's four values — the schema
  currently also allows `screenshots` and `logs`, which the worker invented.
