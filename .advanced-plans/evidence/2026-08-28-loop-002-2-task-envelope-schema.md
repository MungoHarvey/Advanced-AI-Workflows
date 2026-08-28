# loop-002-2 — the immutable external-task envelope schema

**Todo:** `loop-002-2` (phase-6, ralph-loop-002). `provider: opencode`, `worktree_owner: herdr`.
**Deliverable asked for:** *"The schema file and a field-by-field mapping to §9.2."*
**Outcome asked for:** *"A dispatched task has a contract that can be validated before it is
sent, not after it has gone wrong."*

**Executed by:** opencode / **Qwen3.5 397B** (ELM, on-campus), herdr agent `envelope-schema`,
pane `wR:p1`, in worktree `.herdr/worktrees/advanced-planning/loop-002-envelope` branched from
`fix/shared-runtime-reachability`. Self-reported model corroborated by the pane's own status line.

**Result:** `core/state/external-task-envelope.schema.json`, 191 lines, draft-07. Merged
fast-forward into `fix/shared-runtime-reachability` at `27b951b`. Local only — no push has ever
been approved for `advanced-planning`.

---

## The headline: 002-1's predicted defect class arrived on the very next todo

loop-002-1 recorded that CI job 2 proves only that a file *parses*, and named the danger as
**a schema that parses but does not mean what it says**. That was written before any schema
existed. The worker's first draft was exactly that, unprompted:

**The file contained two top-level `"if"` keys and two top-level `"then"` keys.** JSON has no
duplicate keys — the last silently wins. Measured on the actual file:

```
top-level keys after json.load():  ... 'if', 'then' ...   (one each, not two)
surviving if   -> {"properties": {"kind": {"enum": ["sync", "release"]}}}
surviving then -> {"properties": {"allowed_paths": {"minItems": 1}}, "required": [...]}
RULE 2 present in the parsed schema?  False
```

So **rule 2 — the worktree-isolation rule, the most safety-relevant of the six — was not
merely broken, it was absent from the parsed document.** And `json.loads` raised nothing, so
**CI job 2 would have reported the file as a valid schema and shipped it.**

This is the strongest possible argument for what 002-1 said loop-002-5 must do. It is no longer
a hypothetical defect class; it is a defect that actually occurred, on the first schema written
after the prediction, and the existing check waved it through.

## Rule 2 was also inverted, independently of the duplicate key

Lifting the rule-2 block out and testing it in isolation — with the duplicate-key problem
already removed, so this is a *second, separate* fault — against `jsonschema` 4.26:

```
implementation + worktree                     want PASS  got FAIL   <- correct envelope REJECTED
implementation + shared, no override          want FAIL  got PASS   <- the violation ACCEPTED
implementation + shared + override=true       want PASS  got PASS   ok
implementation + worktree + override=true     want PASS  got FAIL   <- WRONG
review + shared                               want PASS  got PASS   ok
                                              2 of 5 correct
```

**The rule rejected the compliant case and admitted the exact case it exists to block.** Two
causes:

1. **`oneOf` instead of `anyOf`.** `oneOf` requires *exactly one* branch to match, so an
   envelope that is both isolated *and* carries the override failed.
2. **A vacuous branch.** `{"properties": {"override_with_shared_write": {"const": true}}}`
   passes when that field is simply **absent** — `properties` does not constrain a key that is
   not there. So the "unless overridden" escape hatch was open by default.

## The worker's self-report was confidently wrong

Asked to state, per rule, whether it was *expressed* or only *documented* — and told
explicitly *"do not claim a rule is expressed if you only described it in a description
string"* — the worker returned a table marking **all six "Expressed"**, with rule 2 attributed
to `if/then` + `oneOf`.

It was not deceiving; it had written that construct. It simply never executed it. **This is the
whole reason the controller reads the diff and runs the checks rather than accepting the
summary** — the standing rule that a worker's own account is never the evidence. Both faults
were found by measurement, and neither was visible in the worker's prose.

## The correction, and the verified end state

The worker was sent the three defects with the measured failure table and a corrected shape:
both conditionals inside a single top-level `allOf`, `anyOf` in place of `oneOf`, and an
explicit `required` on every conditional branch **and** inside each `if` (so an envelope
omitting `kind` cannot trigger a branch vacuously). It amended its commit.

Re-verified **controller-side**, against the real file, with an independent harness — not the
worker's:

```
top-level combinators: ['allOf']          (no 'if'/'then' at top level, no duplicates)

rule 2  implementation + worktree                    ok
rule 2  implementation + shared, NO override         ok  (rejected)
rule 2  implementation + shared + override=true      ok
rule 2  implementation + worktree + override=true    ok
rule 2  sync + shared, no override                   ok  (rejected)
rule 2  review + shared                              ok  (rule does not apply)
rule 1  empty run_id                                 ok  (rejected)
rule 3  sync task, allowed_paths absent              ok  (rejected)
rule 3  release task, EMPTY allowed_paths            ok  (rejected)
rule 4  forbidden_paths without .advanced-plans/state/  ok  (rejected)
rule 5  a credential-shaped extra field (api_key)    ok  (rejected)
rule 6  abbreviated base_sha                         ok  (rejected)
rule 6  uppercase base_sha                           ok  (rejected)
        supersedes_run_id accepted when present      ok
                                                     14 of 14
```

`jsonschema` was used **only** as a throwaway controller-side check. It is not imported by any
committed file and no requirements file was added — the diff was grepped for
`jsonschema|requirements|pip install|import` and returns nothing. The repository remains
strictly zero-dependency. CI job 2's logic run over the whole directory: all five schemas parse.

## How the six rules are expressed

| Rule | Construct | Expressed or documented |
|---|---|---|
| 1. `run_id`, repository, base SHA, branch resolved before dispatch | all four in `required`, each `minLength: 1`; `base_sha` additionally patterned | **Expressed** |
| 2. implementation/sync must use `worktree` unless overridden | `allOf` → `if` (`kind` enum + `required`) → `then` `anyOf` of two branches, each with its own `required` | **Expressed** (after correction) |
| 3. `allowed_paths` cannot be absent for sync/release | second `allOf` branch: `required: ["allowed_paths"]` + `minItems: 1` | **Expressed** |
| 4. `forbidden_paths` contains the controller's planning state | `"contains": {"const": ".advanced-plans/state/"}` | **Expressed** |
| 5. no credential or secret field | `additionalProperties: false` at root | **Expressed** |
| 6. base ref recorded as a full SHA alongside the human ref | new `base_sha`, `pattern: ^[0-9a-f]{40}$`, `base_ref` retained | **Expressed** |

Immutability is carried by `supersedes_run_id` (optional, same pattern as `run_id`) plus a
root `description` stating that amendment creates a new envelope rather than editing one.
That part is **documented, not expressed** — JSON Schema cannot police the write history of a
file, and this note says so rather than implying the schema enforces it.

## Fields added beyond the §9.2 example, and why

- **`base_sha`** — rule 6 requires the full SHA "alongside its human-readable ref", but the
  §9.2 example carries only `base_ref: "upstream/main"`. Named to match design §9.3's `git.base_sha`
  rather than inventing a third spelling.
- **`supersedes_run_id`** — named in §9.2's prose but absent from its example.
- **`override_with_shared_write`** — rule 2's "unless" is not representable without a field to
  hang it on. A bare `isolation` enum cannot express "unless the controller records an override".

## Open questions the worker raised that this note does not settle

Its ambiguity list was good and is carried forward rather than resolved silently:

1. **Where is the shared-write override actually recorded?** §9.2 says "the controller records
   an explicit shared-write override" but not where. A boolean in the envelope makes the rule
   checkable, but if the authoritative record is meant to be `history.jsonl`, the envelope field
   is a duplicate of it and they can disagree. **Needs a decision.**
2. **`required_evidence` enum is invented.** §9.2 shows four values; the worker constrained the
   field to six, adding `screenshots` and `logs`. If the set is open-ended this should be
   unconstrained strings. **Needs a decision.**
3. **Should implementation tasks also require non-empty `allowed_paths`?** §9.2's example
   includes them for an implementation task, but rule 3 names only sync and release.
4. `spec_paths` optionality is unstated in the design; the worker made it required-but-emptiable.
5. `kind` and `provider` enums are inferred from the single example plus this programme's fleet;
   the design never enumerates either.

## Routing note

Qwen3.5 via opencode is the declared workhorse and was correct for this: free, off-quota, and
the only runtime in the fleet verified to run unattended and commit from a linked worktree. It
produced a well-shaped 191-line schema and a genuinely useful ambiguity list on the first pass.

The failure was **not** in generating the schema but in *verifying* it — it asserted six rules
worked without executing one. That is a specific, cheap-to-close gap: the correction prompt
carried the measured failure table and a target shape, and the second attempt was correct in
one round. Worth reusing that shape — **give the worker the failing cases, not the verdict**.
