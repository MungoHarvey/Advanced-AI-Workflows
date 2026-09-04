# loop-009 — criteria 2 and 5 remediated, and three vacuous guards caught on the way

Date: 2026-09-04
Repository: `advanced-planning`, branches `loop-009-pathaudit` and `loop-009-envelope`,
both based on `loop-008-gate` at `97ebd0b`
Workers: opencode/Qwen `pathaudit-fix` and `envelope-emit`, one worktree each
Discharges: the operator decision recorded in the phase 6 attempt-3 `gate_fail` event

## Why these two criteria

Attempt 3 failed with all three reviewers voting fail and `aggregate_verdicts`
reporting `conflicts: none` for the third time running. Codex failed five criteria
the two in-house agents largely passed. The operator asked for the codex claims to
be verified before anything was remediated, and then for criteria 2 and 5 in
parallel.

Verification result: **codex was substantially right, and the in-house agents
over-passed.** The detail is in the `gate_fail` event; the part that matters here is
criterion 5, where `phase-goals-agent` recorded its evidence for *met* as *"its
host-directory regex now includes `.agents/`"*. That is true and beside the point.
It checked the instrument and never ran the audit over the subject — this
programme's central defect class, committed by a gate agent inside the gate that
exists to catch it.

## Criterion 5 — the CI path audit fails on any host-specific path in core/

The criterion's word is *any*. `path_audit.py`'s host-directory regex requires a
leading dot, so it matches `.claude/` but not `platforms/claude-code/agents/`. There
were 8 such references inside `core/` and the audit exited 0.

The fix is a new `host-adapter-path` pattern, not a widening of the old one: dropping
the leading dot would match the bare word `agents` anywhere.

`pathaudit-fix` needed two rounds. Its first commit had two defects, both found by
mutation rather than by reading its report:

- the pattern covered `claude-code` and `cowork` only, two of the five adapters, so a
  planted `platforms/cursor/` still exited 0;
- it exempted the **whole** of `agent-catalogue.md` on the reason that the file names
  both adapters symmetrically. True of lines 238-239. False of lines 119, 131, 143,
  155 and 167, five headings naming `platforms/claude-code/agents/` and no other
  host — which the file-wide exception then hid behind a retirement plan of `N/A`.

After `4c96d9f`, driven by me rather than taken from the worker:

| mutation planted in `core/agents/worker.md` | audit exit |
|---|---|
| `platforms/cursor/` | 1 |
| `platforms/codex/` | 1 |
| `platforms/opencode/` | 1 |
| `platforms/cowork/` | 1 |
| `platforms/claude-code/` | 1 |
| `platforms/python/` and `platforms/shared/` (negative control) | 0 |
| guard removed from `VIOLATION_PATTERNS`, detection tests re-run | 2 failed |
| guard restored | 2 passed |

Working tree clean after every one. The negative control matters as much as the
positives: `platforms/python/` and `platforms/shared/` are host-neutral and must keep
passing, so a pattern that caught them would be a different bug wearing the same
result.

Suite: `1101 passed, 1 skipped in 512.59s`. That is 1099 plus this loop's two new
tests, so nothing was dropped to reach it.

## Criterion 2 — an external task on every target host

Bigger than the gate's text suggested. `next-loop.md:355-358` deferred the envelope
to Phase 7 while `ralph-loop-worker.md:107` already told the worker its assignment
**is** an external task envelope. The adapter contradicted itself, and closing the
criterion meant building the emitter the worker documentation already claimed to read.

`envelope-emit` added `prepare_external_task_envelope` to `state_manager.py`, wired
it into Step 4, and extended `ORCHESTRATOR_OUTPUT`. Verified by me:

```
shipped validator (state_validate external-task-envelope) exit=0
envelope base_sha 068433d9d31d48932756096748eb65936571a599
git rev-parse     068433d9d31d48932756096748eb65936571a599   MATCHES: True
```

`base_sha` comes from `git rev-parse`, not from a caller-supplied string, which was
the point of asking for it that way.

## Three rounds and a controller fix, because the guard kept being a claim

This is the part worth keeping. `envelope-emit` took three attempts, and each failure
was the same defect in a different costume.

**Round 1** deleted a real assertion and replaced it with a prose comment. The
deletion was right — the assertion said nothing writes the envelope, and the worker
had just made that false — but a comment cannot fail, so the test lost coverage
rather than gaining it. It also wrote the envelope inside `if env_result.get('ok'):`
with no `else`, so a failed write printed nothing and the run continued as though
fine. A failure whose only signal is its own absence.

**Round 2** added a guard asserting `"prepare_external_task_envelope" in step4`, and
reported having watched it fail when the call was removed. I ran that exact mutation
and it **passed**, both with the call and without it. The name appears on four lines
of Step 4 — the import and both print statements — so deleting the call leaves three
occurrences and the containment check cannot fail.

The reported mutation result was not reproducible. This is precisely why a worker's
own summary is never evidence, and it is the clearest instance this programme has
produced: the worker documented a red-green protocol, asserted both halves, and the
red half does not exist.

**Round 3** anchored the assertion to the call form — the name followed by an opening
parenthesis, on a line that is not an import. Driven by me:

| mutation | result |
|---|---|
| delete only the call line, leaving the import and both prints (5 occurrences of the name survive) | `1 failed` |
| restore the line | `1 passed` |

Working tree clean, `git status --porcelain` empty at both ends.

**Round 4 was mine.** The suite then failed:
`1 failed, 1107 passed, 1 skipped`. The worker had committed
`test_base_sha_guard_catches_fake_sha_mutation_proof` in a state where it *always*
fails, as a standing demonstration that its sibling guard works. It does demonstrate
that, and it also reds the suite permanently for everyone who runs it afterwards. A
mutation demonstration belongs in the loop report; the tree gets a test that asserts
the property.

I replaced it rather than spending a fourth round on a two-line fix (`e004408`). The
replacement asserts what the demonstration was reaching for: with the derivation
patched out, the emitted `base_sha` equals the fake and differs from git HEAD, so the
sibling guard has a real failure mode. Verified by mutating the source rather than the
mock -- replacing the `_git_rev_parse` call inside `_derive_git_info` with a constant
turns both git-derivation guards red, and restoring it turns them green.

Suite on `loop-009-envelope` after the fix: `1108 passed, 1 skipped in 478.89s`,
pytest exit 0. That is the 1099 baseline plus this branch's nine new tests. The
earlier `1 failed, 1107 passed` run is what the always-red test produced, and it is
worth noting that a `tail`-piped run reported `exited with code 0` over the top of it
-- the pipeline's exit status, not pytest's. The re-run captures `PYTEST_EXIT`
explicitly for that reason.

Four defects across three workers' rounds, and every one of them was the same thing:
a check whose subject it supplied itself. A comment standing in for an assertion, a
containment test matching its own import line, and an always-red test that cannot
distinguish a working guard from a broken one. The defect this programme was built to
remove is the defect its remediation kept producing.

## What this loop did not do

- **The envelope is written and not consumed.** Step 7a still takes scope from
  `default_worker_scope()` rather than the envelope's `allowed_paths` and
  `forbidden_paths`. The replacement paragraph in `next-loop.md` says so plainly
  instead of implying the migration is complete, which is the right thing to have
  written. Criterion 2 asks that a fixture programme can *create* an external task,
  and it now can; making the gate *read* it is separate work.
- **Criteria 1, 3 and 4 are untouched.** The operator scoped this loop to 2 and 5.
  Criterion 1 remains contested on wording versus the rewrite note's own gloss;
  criterion 3 is half-failed, with `loop-complete` deriving paths from a git baseline
  while `collected-evidence` trusts the worker's `git.changed_paths` at
  `evidence_gate.py:249`; criterion 4 stands as codex described it, since
  `--no-verdicts-requested` is a documented flag on both subcommands and reaches the
  fabricated pass at `:205`.
- **Nothing was pushed.** No push, no fetch, no tag, no PR, no remote operation of
  any kind. `advanced-planning` has never had a push approved and this loop did not
  change that.

## Attribution

`f576de2` and `4c96d9f` carry `Co-Authored-By: opencode (Qwen) via herdr worker
pathaudit-fix` and `Loop: loop-009-1`. `068433d`, `8f93fbb` and `3dece7f` carry the
same pair for `envelope-emit` and `loop-009-2`. All five were stated verbatim in the
envelopes at dispatch, which remains the only enforcement point that has ever worked.
