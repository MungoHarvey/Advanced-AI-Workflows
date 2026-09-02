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
