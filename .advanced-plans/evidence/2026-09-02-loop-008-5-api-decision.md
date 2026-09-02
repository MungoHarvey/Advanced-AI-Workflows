# loop-008-5 - what the evidence gate's public API is

**Date:** 2026-09-02
**Provider:** codex, `gpt-5.6-sol`, `model_reasoning_effort=high`
**Shape:** `codex exec -s read-only`, prompt on stdin. The todo decides and does not edit,
so a one-shot read-only probe is the whole of it - no worktree, no pane, no trust gate.
**Subject:** `advanced-planning`, worktree `loop-007-acc08`, branch `loop-007-integration`,
commit `9fd6796`.
**Quota before dispatch:** 78% of codex's 10080-minute window, read from the last
`rate_limits` event of the newest of 819 rollouts.

## The controller answered first, on purpose

The probe's answer was not read until the controller's own was written down. That file is
`controller_position_008_5.md`, timestamped while `codex exec` was still running, and it
exists so that what follows is a comparison of two independent answers rather than one
answer and a reaction to it. Agreement reached this way is worth something; agreement
reached by reading first is not evidence of anything.

| question | controller, written first | probe | outcome |
|---|---|---|---|
| 1 - interface | neither signature as posed; two sites differ; scope from `default_worker_scope`, not an envelope | same, and adds `--baseline GIT_REF` as where `changed_paths` comes from, plus an explicit verdict-intent flag | **agree; the probe is more complete** |
| 2 - `can_advance_loop` | delete; costs zero coverage because each of its three tests has a `validate_advancement` twin | delete; same seven sites | **agree** |
| 3 - reachability | derive from `__all__`, never enumerate; vacuity-guard it | derive from `__all__` against a dispatch registry, plus behavioural wiring tests | **agree; the probe is more specific** |

Two places the probe was better, and both are now in the loop:

- **Where `changed_paths` comes from.** The controller said scope should come from
  `default_worker_scope` and left the changed-path side vague. The probe named it: a
  `--baseline` git ref, with committed and uncommitted paths measured from it. Without that
  the `loop-complete` subcommand has no way to fill the argument that makes gate 3 run.
- **An absent verdict list must be an assertion, not a default.** Both validators today
  turn an omitted or empty `verdict_paths` into a fabricated pass
  (`evidence_gate.py:219` and `:400`, both verified). So a router that merely failed to
  find the verdict files would read as *"no review was requested"*. The probe's
  `--verdict PATH ...` exclusive-or `--no-verdicts-requested` forces the caller to say
  which it means. The controller had not seen this at all.

## Every citation was opened

Not a formality: a review earlier in this programme produced fabricated line numbers that
survived because two models agreed on the conclusion they supported.

| cited | what is actually there | verdict |
|---|---|---|
| `evidence_gate.py:219`, `:400` | the `# Gate 2: Policy gates` comment, with the fabricating `else` a few lines below | correct, block-heading convention |
| `evidence_gate.py:415` | the `# Gate 3` comment saying path scope is not checked when `changed_paths` is None | correct |
| `ap_launcher.py:403` | the `resolve()` call; `EXIT_UNREACHABLE = 3` is defined at line 86 | correct in substance, cites the use rather than the definition |
| `SKILL.md:143`, `:157`, `:185` | step 7, `#### gate current`, `**External task dispatch**` | **exact, not offset** |
| `test_evidence_gate.py:720` | `class TestIntegrationWiring` | correct |
| `test_evidence_gate.py:226`, `:268`, `:297` | the three `can_advance_loop` tests | correct, and independently confirmed as the only ones |

Worth recording: **008-1 cited step headings about three lines above the command, and
008-5's `SKILL.md` citations are exact.** The convention is not stable across probes, so a
uniform offset cannot be assumed - each citation has to be opened. That is the same
conclusion as last time, reached from the opposite direction.

## Its own correction of the record

The probe qualified the loop's phrasing: `validate_advancement` has *many* callers if tests
count - 14 call sites in `test_evidence_gate.py` alone. Its sole **production** caller is
the unreachable boolean wrapper, which is what the loop meant and now says.

## The finding that changes 008-2's scope

The probe raised one defect the loop did not have, and the controller reproduced it rather
than accepting it.

A `collected-evidence` document may record `policy.independent_review_passed: false` and
remain schema-valid: `core/state/collected-evidence.schema.json:113` *requires* all three
policy booleans to be present, and its description says a missing gate must fail rather
than default to true - it guards against **absent**, which is right, and says nothing about
**false**, which is a value a worker must be able to report honestly. A fixture carrying
exactly that ships in the repository, under `tests/fixtures/run-contracts/`**`valid/`**.

`evidence_gate.py` never reads it. Grepping the module for `independent_review_passed`,
`tests_passed` and `path_scope_passed` returns docstrings only; every `policy` reference in
the code concerns **verdict files**, not the evidence document's own policy block.

Run against the two unmodified fixtures:

```
evidence policy block as shipped: {"path_scope_passed": true, "tests_passed": true,
                                   "independent_review_passed": false}

validate_advancement ok      = True
reasons                      = []
schema_errors                = []
scope_violations             = []
```

A worker that reports its own review as failed is advanced by the gate that exists to stop
it. That is a **third** silent pass, distinct from the two already recorded, and it sits
inside the very function 008-2 was about to expose as a CLI - so shipping the CLI first
would have wired in a known-broken gate and let 008-4's tests pin the wrong behaviour as
correct. It is now `loop-008-7`, placed ahead of 008-2.

## A defect in the controller's own todo, found while amending it

008-2's check 5 requires closing the dispatch path in `ap_launcher.py`, and 008-2's
`allowed_paths` named only `evidence_gate.py` and `tests/`. The todo forbade the file its
own check demanded, and the path-scope gate would have blocked the worker for doing exactly
what it was told. `platforms/python/ap_launcher.py` has been added to the list.

## What changed in loop-008

- 008-5 marked `completed`, carrying the three decisions.
- **008-7 opened** for the policy-block defect, placed between 008-5 and 008-2 so the CLI
  is built on fixed semantics. Ids stay out of sequence by the convention already recorded
  above `todos:`.
- 008-2 gains the decided CLI shape as a check - the implementer is not to redesign it -
  and the refusal of a bare `loop-complete` invocation, which would be a second schema
  check presented as a joined gate.
- 008-2's `allowed_paths` corrected, and its `base_sha` moved to `loop-008-7`.
- A sixth success criterion added for the policy block.

Re-parsed after the amendment: `ok`, five pending todos, `phase-6`, task name intact.

## The report, verbatim

---

## Decision

### 1. Interface

Use two explicit CLI subcommands. Do not expose either Python signature unchanged:

```text
ap.py evidence_gate collected-evidence EVIDENCE ENVELOPE
    (--verdict VERDICT ... | --no-verdicts-requested)

ap.py evidence_gate loop-complete LOOP_COMPLETE --baseline GIT_REF
    (--verdict VERDICT ... | --no-verdicts-requested)
```

The first routes to `validate_advancement`. The second computes the worker's committed and uncommitted paths since `GIT_REF`, obtains `default_worker_scope(".")`, and routes those values to `validate_loop_complete_advancement`.

The explicit verdict choice matters. Both functions currently turn an omitted or empty verdict list into a fabricated pass ([evidence_gate.py:219](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:219), [evidence_gate.py:400](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:400)). Accidental failure to discover verdict files must not mean "review not requested."

Neither shared-router site currently supplies verdict paths:

- `loop next` has only `loop-complete.json` at the advancement point ([SKILL.md:143](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:143)). Review verdicts belong to the separate `gate current` workflow ([SKILL.md:157](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:157)). That invocation may therefore use `--no-verdicts-requested`.
- External dispatch has `<envelope-path>` before dispatch and `<evidence-path>` afterwards, but names no verdict file ([SKILL.md:185](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/shared/agent-skills/advanced-planning/SKILL.md:185)). If the envelope requests `review`, the router must collect and pass the resulting verdict paths. If it cannot, advancement must stop. Otherwise it may use `--no-verdicts-requested`.

A plain `evidence_gate loop-complete LOOP_COMPLETE` command is unacceptable. Step 7 has already schema-validated that file, and without verdicts or changed paths the narrow validator skips every other check ([evidence_gate.py:415](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:415)). It would be a duplicate schema check presented as a joined gate.

### 2. `can_advance_loop`

Delete it. It only returns `validate_advancement(...).ok` ([evidence_gate.py:150](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:150)), discards the reasons needed for an operator diagnostic, has no production caller, and its own docstring directs callers to the richer function ([evidence_gate.py:148](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/evidence_gate.py:148)).

Delete with it:

- `__all__` entry at current line 72.
- Module-header import and boolean example at current lines 34 and 36-38.
- Test import at current line 41.
- `TestSchemaInvalidGatePassing::test_case_a_can_advance_loop_false`, current lines 226-246.
- `TestSchemaValidGateFailing::test_case_b_can_advance_loop_false`, current lines 268-274.
- `TestBothPass::test_case_c_can_advance_loop_true`, current lines 297-303.  
  These are the only test references ([test_evidence_gate.py:226](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/tests/test_evidence_gate.py:226)).

### 3. Reachability

Make reachability an executable contract.

Define a production dispatch registry containing both public advancement validators, and make `main()` dispatch through that registry. Add a test which derives the exported names matching `validate_*advancement` from `__all__` and asserts that they equal the registry's validator names. A newly exported but unrouted validator then fails immediately.

Also retain behavioral wiring tests which:

- Run each CLI mode with the underlying validator patched and prove the expected validator was called.
- Read the shared `SKILL.md` and prove the loop gate occurs after schema validation but before `history_log`.
- Prove the external block supplies both evidence and envelope.
- Prove both blocks stop on any nonzero gate result.

This complements the existing test that pins the Claude command directly to the narrow validator ([test_evidence_gate.py:720](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/tests/test_evidence_gate.py:720)).

## Exact change for 008-2

In `evidence_gate.py`:

1. Make the deletions listed above.
2. Add `main(argv=None)`, the two subcommands, and the `if __name__ == "__main__": raise SystemExit(main())` block.
3. For `loop-complete`, resolve `--baseline`, collect both `git diff --name-only BASELINE HEAD` and porcelain paths, normalize separators, exclude the orchestrator-owned `loop-ready.json`, and pass the result with `default_worker_scope(".")`. Reject an absent baseline and the existing `VACUOUS` empty-path result.
4. Make `--verdict` repeatable and mutually exclusive with required `--no-verdicts-requested`.
5. Print every `(gate_name, reason)` and every scope violation on failure.

Add this exact paragraph after the `verdict_paths` parameter description in both validator docstrings:

```text
None or an empty list is an explicit assertion that no policy review was
requested. It must not be used merely because the caller failed to discover
the verdict files. The CLI makes that choice explicit with either --verdict
or --no-verdicts-requested.
```

Add this exact block to the module docstring after the two Python usage examples:

```text
Command-line usage::

    python ".advanced-plans/bin/ap.py" evidence_gate collected-evidence \
        <evidence-path> <envelope-path> \
        (--verdict <verdict-path> ... | --no-verdicts-requested)

    python ".advanced-plans/bin/ap.py" evidence_gate loop-complete \
        <loop-complete-path> --baseline <git-ref> \
        (--verdict <verdict-path> ... | --no-verdicts-requested)

Exit status is 0 when every applicable gate passes, 1 when advancement is
blocked, and 2 for invalid command-line usage. ap_launcher reserves exit 3
for an unreachable shared runtime.
```

Exit codes:

- `0`: advancement allowed.
- `1`: schema, policy, scope, missing-required-review, baseline, or vacuous-measurement failure.
- `2`: malformed CLI invocation or contradictory flags.
- `3`: unchanged launcher-level runtime resolution failure. The launcher already reserves this behavior ([ap_launcher.py:403](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/ap_launcher.py:403)).

In the shared router:

- Immediately before spawning the loop worker, record `git rev-parse HEAD` as the worker baseline.
- After the existing loop-complete schema check and before `history_log`, invoke:

```text
python ".advanced-plans/bin/ap.py" evidence_gate loop-complete \
  .advanced-plans/state/loop-complete.json \
  --baseline <worker-base-sha> \
  --no-verdicts-requested
```

- Replace the external schema-only command with:

```text
python ".advanced-plans/bin/ap.py" evidence_gate collected-evidence \
  <evidence-path> <envelope-path> \
  --verdict <verdict-path>
```

Repeat `--verdict` for every requested review. Use `--no-verdicts-requested` only when the envelope did not request review.

Add these tests:

- `TestEvidenceGateCLI::test_collected_evidence_routes_full_contract`
- `TestEvidenceGateCLI::test_loop_complete_routes_with_measured_scope`
- `TestEvidenceGateCLI::test_verdict_intent_is_required`
- `TestEvidenceGateCLI::test_blocked_result_exits_one_and_prints_reasons`
- `TestEvidenceGateCLI::test_usage_error_exits_two`
- `TestIntegrationWiring::test_shared_loop_gate_precedes_history_advance`
- `TestIntegrationWiring::test_shared_external_gate_receives_evidence_and_envelope`
- `TestReachability::test_every_exported_advancement_validator_has_a_cli_route`

## Contradictions and qualifications

The background is correct when "caller" means production caller. Literally, `validate_advancement` has many test callers, not exactly one; examples include [test_evidence_gate.py:219](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/tests/test_evidence_gate.py:219) and [test_evidence_gate.py:528](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/tests/test_evidence_gate.py:528). Its sole production caller is indeed the unreachable boolean wrapper.

One related defect is not stated in the background: collected-evidence policy values may be `false` while remaining schema-valid ([collected-evidence.schema.json:113](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/core/state/collected-evidence.schema.json:113)), and the repository contains such a valid fixture ([evidence-review-complete.json:20](C:/Users/mharvey2/.herdr/worktrees/advanced-planning/loop-007-acc08/platforms/python/tests/fixtures/run-contracts/valid/evidence-review-complete.json:20)). `validate_advancement` never evaluates those booleans. Verdict-less external advancement therefore needs an explicit trust-policy decision; it must not silently claim that policy passed.

No files or Git state were changed.
