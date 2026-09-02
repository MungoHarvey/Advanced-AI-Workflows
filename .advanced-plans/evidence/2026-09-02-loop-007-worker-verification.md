# loop-007 worker verification — controller-side, 2026-09-02

Two Qwen workers (opencode) ran in parallel on disjoint streams off base `6f363a6`.
This record is the controller's **independent** verification. Nothing here is taken from
a worker's own summary; every claim below was produced by a command run in this session,
and each is labelled `measured` or `read`.

| Worker | Branch | Commit | Scope |
|---|---|---|---|
| `pathaudit` | `loop-007-audit` | `9603fca` | loop-007-4 — path_audit roots + controls |
| `acc08` | `loop-007-acc08` | `3f98cbd` | loop-007-1 + 007-2 — ACC-08 caller + tests |

---

## pathaudit — ACCEPTED with two gaps closed by the controller

### What the worker delivered

**measured.** Four roots added to `DEFAULT_SCANNED_ROOTS`: `core/schemas`, `core/state`,
`platforms/cursor`, `setup/cursor`. The audit's own per-root output now reports
`core/schemas (5 files)`, `core/state (7 files)`, `platforms/cursor (1 files)`,
`setup/cursor (4 files)`.

**measured.** Those counts match `find <root> -type f | wc -l` exactly — 5, 7, 1, 4. The
coverage is complete for each root, not a partial glob. `platforms/cursor` genuinely holds
only a README; that is the adapter's real size, not an audit gap.

**measured.** Suppressions went 7 → 20, all three new ones printed with a reason and a
retirement plan. No silent suppression.

### Gap 1 — the controls were asserted, not measured

**read.** The worker's `TestDefaultScannedRoots` asserts that a Python list contains four
strings. That is a check whose subject is a value the test itself supplied: it stays green
whether or not the audit can read a file beneath those roots. Adding a root to a list is
not evidence of coverage — the same defect class the phase exists to eliminate.

**read.** The pre-existing `TestNewRoots` tests pass an explicit `scanned_roots=[...]`, so
they would still pass if the root were dropped from the defaults entirely. The pin and the
behaviour test never meet.

**measured — controller ran the four controls the envelope asked for.** One plant per root,
each through the real audit as a subprocess, each restored byte-for-byte:

| Root | Planted | RED | GREEN after restore |
|---|---|---|---|
| `core/schemas` | `deprecated-token` | exit 1, `handoff.schema.md:125` | exit 0 |
| `core/state` | `doubled-prefix` | exit 1, `loop-ready.schema.json:54` | exit 0 |
| `platforms/cursor` | `deprecated-token` | exit 1, `README.md:186` | exit 0 |
| `setup/cursor` | `wrong-nesting` | exit 1, `install.sh:776` | exit 0 |

All four named the planted file and the expected pattern. Final tree exit 0.

**Controller added `TestNewRootsAreCovered`** — the same four controls as permanent tests,
run against the **default** root list rather than an override, so dropping a root fails the
behaviour test as well as the pin. Plus a clean-tree positive control, so a red from any of
the four cannot be an audit that flags everything.

**measured — mutation proof of the joined control.** Removing `"core/schemas"` from
`DEFAULT_SCANNED_ROOTS` turns three tests RED:
`test_required_core_roots_are_present`, `test_total_root_count`, and
`TestNewRootsAreCovered::test_core_schemas_root_goes_red`. Restore returns 37 passed and
`cmp` exit 0.

> **Instrument note, worth keeping.** The first mutation attempt silently did nothing: the
> byte pattern ended `,\n` and the file is CRLF, so it matched zero times and the suite's
> "37 passed" was an unmutated run. Only the `assert count == 1` caught it. A mutation
> whose patch did not apply reads exactly like a mutation the tests survived.

### Gap 2 — envelope item 4 not done

**read.** The worker did not touch the argparse description; `git diff` over
`path_audit.py` shows no change to it.

**Controller fixed it.** The old text read *"Exit 0 = clean, exit 1 = violations found"*,
which is false in the way this phase cares about: exit 0 also covers
`PASSED WITH 20 SUPPRESSED`. The replacement says so explicitly and tells the reader to
read the last line rather than the exit code.

### Finding recorded, not fixed — `core/schemas/todo.schema.md`

**read.** Of the three new suppressions, two are clearly legitimate: naming hosts inside a
cross-platform comparison table (`core/state/README.md`) and naming a host to place it
out of scope (`core/schemas/phase-plan.schema.md`).

The third is weaker. `core/schemas/todo.schema.md` carries a **Sync Protocol** whose steps
read *"Call TodoWrite with all loop todos"* and *"Update status via TodoWrite"*. Those are
imperatives naming a Claude Code tool, in a `core/` file, not a mapping description — an
adapter without that tool is told to call it. The section is scoped (*"For platforms with a
native todo sidebar (Claude Code, Cowork)"*), which is what makes it arguable.

Not changed here: what `core/` may name is a contract question affecting every adapter, and
the audit now *sees* and *reports* it as a named suppression rather than hiding it, which is
what criterion 5 asks for. Flagged for the operator.

---

## acc08 — LIBRARY ACCEPTED, PRODUCTION WIRING REJECTED

### What is good

**read.** `validate_loop_complete_advancement` gained `changed_paths` / `allowed_paths` /
`forbidden_paths` and runs `validate_path_scope` as a third gate. The docstring's old
admission — *"There is no commit-stage path-scope enforcement today"* — is replaced with an
accurate description, including that an omitted `changed_paths` means *not checked* rather
than *checked and clean*.

**read.** The negative-assertion test was genuinely rewritten.
`TestNegativeAssertion_ProductionCaller` now calls `validate_loop_complete_advancement`, the
real entry point, instead of passing an unrelated path string to a pure function and
byte-comparing a file the function never opens. There is a positive-control class beside it.

**measured — mutation proof.** Disabling gate 3 (`if changed_paths is not None:` →
`if False:`) turns three tests RED:
`test_loop_complete_json_path_rejected_forbidden`,
`test_out_of_scope_path_rejected_not_allowed`,
`test_multiple_violations_all_named`.
Restore → 40 passed, `cmp` exit 0. These assertions can fail; the ones they replaced could not.

**measured.** `test_scope_policy.py` + `test_evidence_gate.py`: 67 passed.

### Why the wiring is rejected — three defects, all measured

The worker wired the gate into `next-loop.md` Step 7a. As written it cannot discharge
criterion 3.

**1. It reads an artefact nothing writes.** The caller does a bare
`open('.advanced-plans/state/external-task-envelope.json')` with no existence check.
**measured:** this repository's own live `.advanced-plans/state/` holds `history.jsonl`,
`loop-complete.json` and `loop-ready.json` — and **no envelope file**. `grep` finds exactly
one occurrence of `external-task-envelope` in `next-loop.md`, and it is that read. The
command never writes one. First real run raises `FileNotFoundError`.

**2. An empty path list passes the gate vacuously.** **measured:**
`validate_path_scope([], allowed, forbidden)` returns `ok=True, violations=[]`. The envelope
required that *"a caller that supplies no path information must not silently report a pass"*.
The worker handled `changed_paths is None` (visibly not-checked) but not `changed_paths == []`
(checked, over nothing). **read:** `test_scope_policy.py:569` now *asserts* `result.ok` for
the empty case — the vacuous pass is enshrined as correct.

**3. The path source is conditionally empty.** **read:** the gate runs at Step 7a; the main
thread's commit is Step 9, two steps later. `git diff --name-only checkpoint/next-loop HEAD`
therefore sees an empty diff unless the worker self-committed. `ralph-loop-worker.md:27-36`
says the worker *may* commit and that the main thread commits otherwise — so the same
document offers a path on which the diff is empty, and defect 2 then passes it. `check=True`
on the subprocess also means a missing `checkpoint/next-loop` tag raises rather than reports.

### The finding underneath all three

This is one defect, not three, and it is one level up from anything the gate reviewers
stated. **`next-loop.md` was never migrated to the loop-006-1 contract.**

**measured:** `grep` for `envelope` and `collected-evidence` in `next-loop.md` returns zero
hits before this change. **read:** `state_manager.py`'s module docstring still says
*"loop-complete.json — written by worker"*. Loop-006-1 rewrote the worker's **role
documents** (`core/agents/worker.md`, `platforms/claude-code/agents/ralph-loop-worker.md`)
to say the worker emits collected-evidence and never writes programme state — and left the
command that spawns the worker, and the state module it uses, running the old protocol.

So the worker is told by its own definition to emit collected-evidence, and by the command
that spawns it to write `loop-complete.json`. The path-scope gate has no production caller
*because* the artefact it validates is never produced. Criteria 3 and 4 fail together for
this one reason.

**Corollary for the record:** a contract rewritten in a role document, while the command
that executes the role is never migrated, is the same defect class as a mechanism that is
fully unit-tested and never called. Asking *"does the contract say the right thing"*
instead of *"does anything execute it"* is how a check that cannot fail survives review.

### Not resolvable by the controller alone

Fixing the wiring requires choosing between migrating the adapter up to the declared
contract and revising the contract down to what the code does. That changes the tool's main
execution path, so it is put to the operator rather than decided here.

### Post-commit note — two pinned roots do not exist in this repo

**measured.** `DEFAULT_SCANNED_ROOTS` pins 17 roots; the audit's summary line names 15.
The two absent ones are `.claude/commands` and `.claude/agents` — install-target paths that
exist in a project the framework has been installed into, not in the framework repo itself.
Both predate this loop.

A root that is silently skipped when absent is the shape of a check that cannot fail, so it
is worth naming rather than leaving implicit. It is tolerable here for two reasons: the
summary line reports the roots it actually scanned, so a reader can see 15 rather than 17;
and `TestNewRootsAreCovered` joins the four roots this loop added to real behaviour, so
those cannot go nominal without a test going red. The two `.claude/` roots have no such
joint. Left as a finding.

### Line endings

**measured.** `test_path_audit.py` was mixed after my addition — CR=747 LF=839 CRLF=747, the
92-line difference being exactly the new class written with bare LF into a CRLF file.
Normalised to 839/839/839 with no stray `\r\r`, then re-verified: 37 passed, audit exit 0.
`path_audit.py` was already uniform at 515/515/515.

### Retired

Panes `w10:p1` and `w21:p1` closed after their work was collected and committed. Both
worktrees are left in place: `loop-007-audit` holds `9603fca` and `d09c440`, and
`loop-007-acc08` holds `3f98cbd`, none of them pushed.

---

## Controller work, 2026-09-02: wiring the gate to a scope the system can produce

This section covers my own changes rather than a worker's, and it is here because the
finding it answers was that a block had never been run. A record that repeats that mistake
would be worthless.

### The finding, restated

`next-loop.md` step 7a read `.advanced-plans/state/external-task-envelope.json` with a bare
`open()`. **measured:** nothing in the running system writes that file. The live state
directory holds `loop-ready.json` and `loop-complete.json` and no envelope, and
`loop-ready.schema.json` has eight properties, none of them paths, with
`additionalProperties` absent — so the orchestrator could not add one without a schema
change. The block's first real invocation would have raised `FileNotFoundError`.

Every reviewer who passed that block read it. None ran it. That is the whole defect class.

### What replaced it

`default_worker_scope(repo_root)` in `platforms/python/scope_policy.py` derives the pair the
gate needs from the repository itself. The allow-list is the load-bearing half and it is
**derived, not enumerated**: every top-level entry except `.advanced-plans/` is allowed, and
two carve-outs are added back (`phases/`, and `state/loop-complete.json`). A programme-state
file invented tomorrow is therefore `not_allowed` on the day it appears, with no list for
anyone to remember to update. An enumerated forbidden list has the opposite property — it
permits whatever nobody listed, which is a check that cannot fail.

`_ALWAYS_FORBIDDEN` names six paths that the derivation already refuses. It is belt and
braces: it makes the violation report say `forbidden` rather than `not_allowed` for the
paths that matter most, and a future widening of the allow-list cannot quietly expose them.

**measured.** `test_default_worker_scope.py`, 22 tests, all green. Two of them are the
instrument check — an empty allow-list would make every rejection test pass for the wrong
reason, so the file asserts first that something is accepted. The load-bearing test is
`test_an_unlisted_state_file_is_refused_too`, which asserts the refusal reason is
`not_allowed` rather than `forbidden`: if that ever flips, the general property has been
quietly replaced by a specific one.

**Mutation-proved.** Changing the exclusion from `(".git", ".advanced-plans")` to
`(".git",)` turns `test_an_unlisted_state_file_is_refused_too` and
`test_the_carve_out_is_a_file_not_the_directory` red. Restored byte-exact afterwards.

### The block was executed, in three scenarios

**measured.** A harness extracted the python block **from the shipped markdown** rather than
from a copy — a harness that runs its own transcription proves nothing about what ships — and
ran it in three throwaway git repositories. The single substitution was the
`.advanced-plans/bin/ap.py` bootstrap line, which does not exist in the framework repo
because it is installed into a consuming project; a `sys.path` insert does the same job.

| Scenario | Expected | Result |
|---|---|---|
| worker edited `core/file.md` | pass | exit 0, "gate passed over 1 path(s)" |
| worker wrote `.advanced-plans/state/history.jsonl` | fail | exit 1, `path_scope`, the path named, reason `forbidden` |
| worker changed nothing | fail | exit 1, `path_scope: VACUOUS` |

Scenario 1 is the positive control. Without it a gate that refused everything would score
two out of three and look correct.

### One deliberate deviation from the approved option

The option chosen sketched moving step 7a to after step 9 so the diff would be non-empty. I
kept it at 7a. Steps 8 and 9 are the **main thread's** writes — `PLANNING.md` and
`history.jsonl` — and both are forbidden to the worker, so a gate that ran after them would
report the controller's own writes as worker violations on every single loop. The intent
behind the move (never hand the gate an empty list) is met a different way: the measurement
is now committed changes since the checkpoint tag **union** the dirty tree, which is
non-empty on both of the paths `ralph-loop-worker.md` offers the worker.

Two smaller changes went in with it. A missing checkpoint tag is now a stated failure naming
what to do about it, rather than a traceback from `check=True`. And `loop-ready.json` is
excluded by name because the orchestrator wrote it at step 4, before the worker existed —
that exclusion is deliberately one path wide, so any *other* state file appearing in the
measurement still fires the gate.

### What this does not fix

The role documents and the commands still disagree. `core/agents/worker.md` and
`ralph-loop-worker.md` say the worker emits collected-evidence and never writes programme
state; `next-loop.md` and `state_manager.py` still run the loop-complete.json protocol. The
`.advanced-plans/state/loop-complete.json` carve-out and
`test_loop_complete_is_writable_and_this_is_the_divergence` are the two in-code markers for
that gap. When the adapter is migrated they should both be **deleted, not amended** — an
amended carve-out is how a temporary hole becomes permanent. Recorded as a Phase 7 finding:
*role docs declare a contract the commands do not execute*.

### Two measurements that bear on the remaining loop-007 todos

**One production call site, and it is now the wired one.** A repo-wide grep for
`validate_loop_complete_advancement`, `validate_path_scope` and `default_worker_scope`,
excluding tests and the two library modules themselves, returns exactly one executable
caller: `platforms/claude-code/commands/next-loop.md`. Everything else is a CHANGELOG line
or prose. So the criterion "the gate is load-bearing at every production call site" is
satisfied trivially — there is one, and it now runs.

That is a weaker result than it sounds, and the reason is the second measurement.

**Three of the five host adapters are README-only.** `platforms/codex/`,
`platforms/cursor/` and `platforms/opencode/` each contain a single `README.md` and nothing
else. `platforms/cowork/` has two agent prompts, a `checkpoint.sh` and a SKILL, but no
command that drives a loop. Only `platforms/claude-code/` has an executable loop at all.

This matters for the two remaining human-gated todos. A fixture programme "on all four
hosts" presumes four hosts that can run one; on this measurement, one can. Whether the
right answer is to build the missing adapters, to narrow the criterion to the hosts that
exist, or to treat the READMEs as the deliverable is an operator decision, not something to
settle by rewording a success criterion. Recorded, not fixed.

**63 `external-task-envelope` references remain**, all of them in role documents, host
prompts, the schema itself, and two `evidence_gate.py` docstrings describing a parameter.
None of them open a file. The one executable reader is gone. That is the same divergence
recorded above, seen from the other side: the contract is documented in five places across
every host and executed in none.

### Two things the first pass left open, closed the same day

**The call-site pin could not fail on the defect it was written for.**
`TestIntegrationWiring` asserted three strings appear in step 7a. All three appeared in the
broken version too — it imported the gate, called it, and checked the result, and would
still have died on `FileNotFoundError` before reaching any of that. So the pin proved a gate
is *mentioned*, not that it can run. Two tests were added: one asserts the block does not
name `external-task-envelope` and does obtain a scope, the other that it names all three
failure modes an operator has to tell apart. **Mutation-proved individually** — renaming
`default_worker_scope` reddens the first, removing the word `VACUOUS` reddens the second,
and `next-loop.md` restored byte-identical (sha256 checked) after each.

**The derived allow-list let a worker rewrite its own permissions.**
**measured.** `default_worker_scope('.')` on the real repository returns 22 allowed entries,
one of which is `.claude`. `git ls-files .claude` returns exactly one file:
`.claude/settings.json` — this repository's own permission grants. A worker able to edit it
can widen what the next worker may do, which is the single change a path-scope gate exists
to prevent, and it is the same move the operating rules forbid me under "broaden provider
permissions".

`.claude/settings.json` is now in `_ALWAYS_FORBIDDEN`. The shipped template,
`platforms/claude-code/settings.json`, is a different file and stays allowed — a worker
improving what gets installed into a consuming project is doing ordinary work, and a gate
that blocked it would be refusing real work to look strict. Both directions are pinned and
both mutation-proved in isolation: dropping the entry reddens only the refusal test, and
pointing it at the template reddens only the permissiveness test.

The tmp fixture now creates `.claude/` as well. Without it the path was `not_allowed`
whatever the forbidden list said, and the new entry would have been carrying no weight in
its own test.

**This is a judgement call, and a narrowing.** If a loop legitimately needs to edit the live
settings, the gate now blocks it and names the path, and an operator widens the list
deliberately. The previous default resolved itself silently, which is the worse direction
for a permission file. One line reverses it.

### Landed

`e49506d` on `loop-007-acc08`, four files: `scope_policy.py`,
`tests/test_default_worker_scope.py` (new), `tests/test_evidence_gate.py`,
`platforms/claude-code/commands/next-loop.md`. Working tree clean afterwards.

**measured.** Full suite `1044 passed, 1 skipped in 531.74s`, against `1018 passed, 1
skipped` before this loop's work — the difference is the 24 tests in the new file and the 2
added to `TestIntegrationWiring`. The suite was re-run after the `.claude/settings.json`
narrowing, not before it, because the narrowing touched a module a hundred other tests
import.

Nothing pushed. `loop-007-acc08` now holds `3f98cbd`, `6cca55c` and `e49506d`, none of them
on a remote.

## The gate had no tree to read, and that was measured before it was fixed

`/run-gate` reviews a working tree. Loop 007's remediation was not in one. `main` sat at
`171d193` (v0.20.0 staged) and contained none of it; the six commits were spread across
three branches off that same base, and no branch contained any other:

| Branch | Tip | Unique to it |
|---|---|---|
| `loop-005-cursor` | `06434b7` | 007-5 |
| `loop-007-audit` | `d09c440` | 007-4, plus `9603fca` |
| `loop-007-acc08` | `e49506d` | 007-3, 007-2, `3f98cbd` (007-1) |

`git merge-tree --write-tree` reported both merges clean before either was made, which is
the point of running it first: the alternative is discovering a conflict with a half-built
branch on disk. Both merges then went through with no conflict, and the local branch
`loop-007-integration` now carries all six commits plus two merge commits (`1b54294`,
`b684dfc`). It was never pushed and `main` was never touched -- merging to a default branch
is outside this session's authorisation, and an integration branch for a reviewer to read
is not a release.

Each piece was checked on the merged tree rather than assumed to have survived:

| Todo | Check on the integrated tree | Result |
|---|---|---|
| 007-1 | non-test callers of `validate_path_scope` | `evidence_gate.py:242` and `:437` |
| 007-2 | the rewritten negative assertion | targets the production caller, mutation-proved |
| 007-3 | step 7a: no envelope, has a scope, names three failures | all four checks hold |
| 007-4 | per-root red-green tests | four, one per new root |
| 007-5 | `run-gate.md` instructs `deferred` | fixed in source |

## The command the gate would have run is the one 007-5 fixed

`~/.claude/commands/run-gate.md` -- the INSTALLED copy, which is what `/run-gate` executes
-- still instructs the Codex reviewer to emit `criteria_outcomes.status: 'not_applicable'`.
The schema enum is `["met", "deferred", "failed"]` with `additionalProperties: false`, so a
reviewer that obeys produces a verdict which fails `extract_and_validate` and is logged as
a skipped reviewer rather than as a defect in the instruction. That is exactly the defect
loop-007-5 was opened for, and it is fixed in `platforms/claude-code/commands/run-gate.md`
on the integration branch. The installed copy is stale because nothing has been released or
re-installed since.

So attempt 2 is driven from the SOURCE text, not the installed command. Had it not been,
the gate would have reproduced its own known defect while nominally testing the fix for it,
and the Codex verdict would have gone missing for the second attempt running. Diff of the
two, verbatim:

```
-  status to 'not_applicable' with evidence 'main-thread-verified (isolation rule forbids
+  status to 'deferred' with evidence 'main-thread-verified (isolation rule forbids
```

Recorded, not fixed: refreshing `~/.claude/commands/` is a user-profile write outside both
repositories and outside this task's scope.

## What the loop file said, and what was true

All seven loop-007 todos still read `status: pending`, which would have stopped `/run-gate`
at its step 2 precondition. Five were done and on branches. The file now records each with a
`landed:` line naming the commit, because a status word on its own is the reviewer taking
the controller's word for it.

007-6 and 007-7 stay `pending`. They are `gate: human`, they are not done, and `cancelled`
would have bought a green precondition with a false statement. They carry criteria 1 and 2,
so attempt 2 is expected to fail on those two; the gate is told so explicitly rather than
being allowed to discover it as a surprise.

## Gate attempt 2: what three reviewers found, and where two of them were wrong

Run 2026-09-02 against the local branch `loop-007-integration` at `b684dfc`. Sentinel
`.advanced-plans/state/gate-review-mode` was up for the whole run and removed at Step 8.
Nothing was pushed; `main` is untouched at `171d193`.

| Reviewer | Verdict | Confidence | loops_to_revert |
|---|---|---|---|
| codex `gpt-5.6-sol` effort high, `-s read-only` | fail | 99 | `["ralph-loop-007"]` |
| code-review-agent | fail | 95 | `[]` |
| phase-goals-agent | fail | 90 | `[]` |

Per criterion, as each reviewer wrote it:

| # | Criterion | codex | code-review-agent | phase-goals-agent |
|---|---|---|---|---|
| 1 | every host DISCOVERS the same core skills | deferred | failed | failed |
| 2 | fixture programme on every host | failed | failed | failed |
| 3 | ACC-08, only the controller writes programme state | failed | met | met |
| 4 | evidence advances only after schema AND gate validation | failed | met | failed |
| 5 | CI path audit fails on host-specific paths in `core/` | failed | met | met |
| 6 | no adapter duplicates a core skill | met | met | met |

Each reviewer stands alone in exactly one place. On criterion 5 the lone reviewer is the
correct one, which is the result worth keeping: a majority vote would have passed a
criterion that a controlled mutation shows is not met.

### Criterion 5: the token the four new tests could not catch

`platforms/python/path_audit.py:95-98` matches host directories with
`re.compile(r"\.(claude|cursor|opencode|codex|gemini)/")`. `docs/path-conventions.md:150`
and `:163` both name `.agents/` as a forbidden host directory. It is absent from the regex.

Mutation through the default CI path, against `core/agents/worker.md`
(17103 bytes, sha256 `f59d70b8cd7828c9...`), instrument checked before subject:

| Planted token | Documented forbidden | In the regex | Audit exit | Named in output |
|---|---|---|---|---|
| `.claude/skills/x` (positive control) | yes | yes | 1 | yes |
| `.agents/skills/x` | yes | **no** | **0** | **no** |

File restored byte-exact afterwards; sha256 unchanged, worktree clean.

**The finding under the finding: widening a check's ROOTS does not widen its TOKENS.**
loop-007-4 added four scanned roots (`core/schemas`, `core/state`, `platforms/cursor`,
`setup/cursor`) and wrote a red-green test per root. Every one of those tests planted a
token the regex already matched, so all four passed on a regex that misses `.agents/`.
Two of three reviewers checked the roots, confirmed the tests were real red-green pairs,
and marked the criterion met. Neither checked the token list the roots are scanned for.
`.agents/` is the worst one to miss: it is the shared skills root codex, opencode and agy
all read.

### The loop-007-5 record overstated what landed

`code-review-agent` found the todo's FIRST check was never done. `next-loop.md` Steps 6
and 7 still instruct the worker to write and then read `loop-complete.json`, while
`core/agents/worker.md` says the worker writes no programme state. Both instructions are
still live in the same adapter. Commit `06434b7` discharged only the second check, the
`run-gate.md` status enum, and the controller marked the whole todo `completed` on the
strength of the commit message rather than the checks. That is this phase's own defect
class applied to its bookkeeping.

Corrected in `phase-6/loops.md`: `status: in_progress`, with a `not_landed:` line stating
what is outstanding. The status enum is `pending | in_progress | completed | cancelled |
frozen` (`core/schemas/todo.schema.md:31`); there is no `partial`.

### Three machinery findings the gate produced as a by-product

1. **`aggregate_verdicts` cannot see per-criterion disagreement.** It returned
   `{"result": "fail", "conflicts": [], "missing": []}` while the three reviewers
   disagreed on three of six criteria. `codex_gate.py:315-329` compares only the
   top-level `verdict` word between codex and each subagent, so an empty `conflicts`
   list here means the three agreed on the word "fail", not on the phase. Reading it as
   agreement would be wrong every time the disagreement is where it actually matters.

2. **A todo left `in_progress` is invisible to the next worker.**
   `state_manager.py:272` builds `pending_todos` with `status == "pending"` exactly, and
   `todos_count` is `len(pending_todos)`. Measured on a throwaway copy: loop-007 reports
   `todos_count: 2` with 007-5 `in_progress`, the same as when it read `completed`. So a
   half-finished todo is neither counted nor scheduled. The 007-5 leftover is therefore
   also named in the loop's `needed:` handoff, where something will read it.

3. **The `yaml` fences in `phase-6/loops.md` are not valid YAML.** Fence 7 fails
   `yaml.safe_load_all` with `while scanning a simple key` at the indented prose section
   `## What this loop is for`. This is pre-existing and reproduces identically on the
   `HEAD` version of the file, so it is not an artefact of this edit. It does not break
   anything today because `state_manager` does not use a YAML parser, it line-scans
   (`state_manager.py:170`, comment: "Inline minimal YAML parsing"). It would break any
   tool that took the fence label at its word. Verified after editing by running the
   framework's own reader against a temporary copy with a throwaway state dir: seven
   todos parsed, `ok: true`.

### What criterion 4 rests on

Not disputed by the controller: `evidence_gate.validate_advancement` has zero production
callers, every call site being in `test_evidence_gate.py`, and
`validate_loop_complete_advancement` is called from exactly one adapter. Independently
measured earlier in this window: `platforms/codex`, `platforms/opencode` and
`platforms/cursor` each hold exactly one tracked file, `README.md`, and
`platforms/shared/agent-skills/advanced-planning/SKILL.md` (the router codex, cursor and
opencode use) contains no reference to `evidence_gate`, `validate_advancement`, or
`validate_loop_complete_advancement`. The gap that loop-007-3's own todo required to be
written down is recorded only here, in a controller note, and not in any shipped document.

## Closing criterion 5: the token, and proof that the tests for it are tests

The operator's decision was to fix `.agents/` inside loop 007 rather than open a loop for
it. What follows is what landed and how each claim was established.

### The change

`platforms/python/path_audit.py`, host-directory rule. The regex read
`(claude|cursor|opencode|codex|gemini)` and now reads
`(agents|claude|codex|cursor|gemini|opencode)`; the pattern label was relabelled to match,
and three named `EXCEPTIONS` entries were added for the files under
`platforms/shared/agent-skills/advanced-planning/` that legitimately name the cross-host
discovery root -- `SKILL.md`, `references/orchestrator-prompt.md`,
`references/worker-prompt.md`. Named exceptions print on every run and an excepted file
still fails every rule it was not excepted for, so this is a declaration and not a
suppression. Their retirement plans are `N/A`: those files are host-routing documents and
naming the root is their job.

The rule's scope is unchanged. `core_only=True` means `core/` and `platforms/shared`
(`path_audit.py:376-377`), so `platforms/claude-code/` may still say `.claude/`, which is
the entire point of an adapter.

### The audit, on the real repository

| Run | Exit | Result |
|---|---|---|
| before the change | 0 | PASSED WITH 20 SUPPRESSED |
| after the change | 0 | PASSED WITH 24 SUPPRESSED |

Four is exactly the number of declared `.agents/` occurrences across the three
`platforms/shared/` files. The audit stays green because the new violations are declared,
not because the rule was weakened.

### The tests, and whether they are tests

Two were added to `TestNewRootsAreCovered`:

- `test_a_planted_agents_path_goes_red` plants `.agents/skills/...` in a `core/` file and
  runs `audit(repo_root=root)` with **no `scanned_roots` override** -- the default CI path,
  which is what the four loop-007-4 tests already used and what made their silence
  meaningful.
- `test_every_documented_host_directory_is_in_the_regex` **derives** the forbidden token
  list from the Host directories row of `docs/path-conventions.md` and requires the
  host-directory regex to match every token in it. A test that enumerated the six tokens
  itself would be a second copy of the list that was already forgotten once, forgettable in
  the same way. Deriving it means a host directory added to the documentation fails here
  until the code catches up. It parses the row's forbidden column only, asserts exactly one
  such row exists, and asserts at least five tokens parsed, so a row whose format changed
  fails loudly rather than sweeping over nothing.

Both were mutation-proved by removing the token from the regex and running them, with the
subject restored byte-exact afterwards (sha256 `56e322396468bc01`, unchanged):

| Test | token present | token removed |
|---|---|---|
| `test_a_planted_agents_path_goes_red` | pass | **fail** -- "a core/ file naming .agents/ was not flagged" |
| `test_every_documented_host_directory_is_in_the_regex` | pass | **fail** -- "forbids `['.agents/']` ... regex does not match them" |
| `test_the_clean_tree_is_green` (positive control) | pass | pass |

The control is what separates "these tests can see the defect" from "the audit is broken
and failing everything". The drift test naming `['.agents/']` in its own failure message is
the point of deriving it: nothing told it which token to look for.

### Where it came from

Not loop-007-4. The origin is **loop-003-2**, and its own first check reads:

> "host directories flagged under core/: `.claude/`, `.cursor/`, `.opencode/`, `.codex/`,
> `.agents/`, `.gemini/`"

Six named; five implemented. The todo's `evidence` field asked for "the diff and the rule
list", and the rule list was never read against the check that specified it. The
documentation was correct in both places throughout, so no source of truth had to be
consulted -- only the two artefacts the todo already named.

It then survived loop-007-4, which added four roots and four red-green tests, because
every one of those tests planted a token the regex already matched. **Widening a check's
roots does not widen its tokens**, and a test suite can grow while the hole stays exactly
the same size.

### The reviewer split, kept on the record

Two of three reviewers marked criterion 5 met; both had checked the roots. The one that
marked it failed had checked the tokens. A majority vote would have passed a criterion a
controlled mutation shows was not met. Consensus raised confidence in the wrong
conclusion, which is the second time in this programme it has done so -- and the reason
the resolution here was a mutation rather than an adjudication.

## The operator's resolution of attempt 2

Two decisions were taken on 2026-09-02 after the three verdicts were in, and both are
recorded here because neither is derivable from the verdicts themselves.

**Criterion 3 -- MET, the carve-out stands.** codex marked it failed; the two subagent
reviewers marked it met. The operator ruled it met on the grounds that a carve-out which
is declared, documented and tested satisfies the criterion. The divergence codex objected
to -- `.advanced-plans/state/loop-complete.json` being writable by the worker while
`core/agents/worker.md` says the worker writes no programme state -- is real and is
already tracked as the Phase 7 finding. Its in-code markers are the `_STATE_CARVE_OUTS`
entry and `test_loop_complete_is_writable_and_this_is_the_divergence`, and when the
adapter migrates they are to be **deleted, not amended**. A carve-out that survives its own
cause is how a divergence becomes permanent.

**Criterion 5 -- fix it inside loop 007.** Rather than open a loop-008 for a defect that
is one token wide. Done, and documented in the section above.

### Where the six criteria stand after that

| # | Criterion | State | What it turns on |
|---|---|---|---|
| 1 | every host discovers the same core skills | failed | 007-6, gate: human, open |
| 2 | fixture programme on every host | failed | 007-7, gate: human, open |
| 3 | ACC-08, only the controller writes programme state | **met** | operator ruling above |
| 4 | evidence advances only after schema and gate validation | failed | adapter wiring; no loop opened |
| 5 | CI path audit fails on host-specific paths in core/ | **met** | fixed and mutation-proved |
| 6 | no adapter duplicates a core skill | met | all three reviewers |

Three met, three failed, so the phase 6 gate remains a fail. Two of the three failures are
the human-gated todos and were expected. The third, criterion 4, is not gated on anything
external: `evidence_gate.validate_advancement` still has zero production callers, and the
shared router the other three hosts use names no gate at all. It is the one open criterion
that a loop could close.

## Loop 008 opened, and the measurement that scoped it

The operator's ruling left criterion 4 as the only open criterion not gated on manual
host work, and opened loop 008 for it. Before a single todo was written I measured the
gap, because the two reviewers who failed the criterion both described it as *"the gate
is not wired into three adapters"*, and a loop written on that phrasing would have fixed
the wrong thing.

Two facts contradict the phrasing.

The shared router **does** validate. `platforms/shared/agent-skills/advanced-planning/SKILL.md`
runs `ap.py state_validate` at three points in the loop verb (`loop-ready` at steps 3 and 5,
`loop-complete` at step 7) and once more in the gate verb. What it never runs is the *gate*
half of the criterion, whose wording is schema **and** gate validation. So the criterion
fails on one half, not both, and only the gate half is loop 008's business.

The second fact is worse than "unwired". `ap_launcher.py:428-430` dispatches with
`runpy.run_module(module, run_name="__main__", alter_sys=True)` and applies no allow-list,
so it will run whatever module name a router writes. `evidence_gate.py` has no `__main__`.
Dispatched exactly that way, with the same argument shape:

| module | result |
|---|---|
| `platforms.python.state_validate` | `SystemExit(2)` - prints usage |
| `platforms.python.evidence_gate` | **returned normally** - no `SystemExit` |

A normal return is exit 0 at the launcher. So the gate is not absent from the three
non-Claude hosts; it is **callable there and silently green**. A router wired to call it
today would read "gate passed" from a module that never looked at anything, and every
check downstream of that read would inherit the lie. That is the programme's own defect
class - a check whose subject is something it supplied itself - sitting inside the
mechanism built to catch it.

Two smaller measurements set the loop's edges. `validate_loop_complete_advancement` has
exactly one production caller, `platforms/claude-code/commands/next-loop.md` at lines 366
and 400. `validate_advancement`, also exported in `__all__`, has **zero** anywhere outside
tests. Todo 008-5 exists to decide which of those two things it is.

### The six todos, and why they are in that order

008-1 is read-only and goes to codex, because the first job is to reproduce or refute the
measurement above rather than inherit it. 008-2 gives the module a CLI whose three failure
modes an operator can act on differently, and 008-3 wires it into the router at the point
that already validates `loop-complete.json` - executing the shipped block in three
scenarios, the pass first as the positive control, because loop-007-3 established that a
gate every reviewer had *read* raised `FileNotFoundError` on its first real invocation.
008-4 closes the class rather than the instance: a test that derives module names by
parsing the shipped commands and asserts each has a `__main__`, with a vacuity guard, so
that the next inert module fails on the day it is wired. 008-5 resolves the dead-code
question. 008-6 proves the criterion on opencode against an installed copy, forced to fail
as well as pass, with the invocation manifest read off the host's own datastore.

### Verification of the edit itself

The loop block was inserted at the seam before `## Loop order and why`, which was checked
unique before the write. `loops.md` went 1208 to 1382 lines with zero CR bytes, and three
index edits landed alongside it: the loop-order row, the criterion-4 discharge row, and a
new paragraph recording attempt 2 and the operator's two rulings.

The parser was then run against the edited file rather than assumed to still work, with
`state_dir` redirected into the scratchpad so no programme state was written - the md5 of
`.advanced-plans/state/loop-ready.json` was identical before and after. It returns
`ralph-loop-007` with two pending todos, which is correct: 007-6 and 007-7 are the
human-gated ones and still open. On a scratch copy with those retired it stops at 007
anyway, because 007-5 is `in_progress` and an `in_progress` todo is unschedulable - the
already-recorded finding at `state_manager.py:272`, reproduced here rather than
rediscovered. With that cleared too, the scanner reaches loop 008 and reports six populated
todos under the right phase and task name. So the block parses, and the one thing standing
between it and execution is a defect that predates it.
