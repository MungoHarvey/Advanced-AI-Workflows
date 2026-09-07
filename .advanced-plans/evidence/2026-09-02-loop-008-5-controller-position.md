# Controller's independent answer to loop-008-5, written BEFORE reading the probe

Written 2026-09-02 while `codex exec` was still running, so the comparison afterwards is
between two answers rather than one answer and a reaction to it. Everything below was read
off the worktree at `9fd6796`, not recalled.

## Q1 — the interface

**Neither shape as the envelope posed it.** The constraint is what each site can supply,
and the two sites differ:

- **Site 1, `loop next` step 7 (SKILL.md 143-153).** The loop verb never names an
  envelope. Verified: no occurrence of the token `envelope` anywhere in SKILL.md lines
  100-160. It has `loop-complete.json` and nothing else. So a CLI whose scope input is an
  *envelope path* cannot be invoked here at all.
- **Site 2, external dispatch (SKILL.md 187-196).** This one does have an envelope — it
  validates it at line 190 before dispatch, and validates collected evidence at 196. Both
  paths are in hand.
- **Neither site has verdict paths.** Verdicts are produced by `gate current`, not by the
  loop verb, and the external-dispatch block names none.

**The repository has already solved site 1's problem, and the solution is not an
envelope.** `platforms/claude-code/commands/next-loop.md:397` calls
`default_worker_scope('.')` (from `platforms/python/scope_policy.py:73`) to derive
allowed/forbidden lists from the repository itself, and pairs them with `changed_paths`
from git. `validate_loop_complete_advancement` takes scope as **lists**, not as an
envelope path — signature at `evidence_gate.py:314-320`. That design exists precisely
because nothing in the Claude adapter writes an envelope, which
`test_evidence_gate.py:734` states outright in its own name:
*"test_next_loop_gate_does_not_read_the_envelope_that_nobody_writes"*. Until 2026-09-02
that step opened `external-task-envelope.json` with a bare `open()` and would have raised
`FileNotFoundError` on its first real run.

**So the CLI should take the evidence document positionally, and scope from either
source:** an `--envelope <path>` for site 2, or a `--default-scope` deriving from
`default_worker_scope` for site 1, with `--verdict <path>` repeatable and optional.
Exposing `validate_advancement`'s raw three-path signature would hand site 1 an argument
it cannot fill — and the envelope's own phrasing applies: a gate that cannot be given its
inputs is not a gate.

One trap the CLI must not inherit quietly: with scope absent,
`validate_loop_complete_advancement` skips the path-scope gate entirely and returns a
clean result, so the gate would be **present and inert** — the second assertion at
`test_evidence_gate.py:752` exists to catch exactly that. An empty `changed_paths` is
already rejected rather than passed (docstring, `evidence_gate.py:338-341`). The CLI needs
the same distinction between *not checked* and *checked and clean*, visible in its output.

## Q2 — `can_advance_loop`

**Delete it.** Beyond the reasons already in the loop, one that decides it: **deletion
costs zero coverage.** The three tests that name it —
`test_case_a_can_advance_loop_false` (226), `test_case_b_can_advance_loop_false` (268),
`test_case_c_can_advance_loop_true` (297) — each has a twin covering the same case against
`validate_advancement` directly: `test_case_a_does_not_advance` (186),
`test_case_b_does_not_advance` (254), `test_case_c_does_advance` (282). The three
`can_advance_loop` tests re-assert cases A, B and C through a wrapper that discards the
reasons. Removing them removes duplicates, not checks.

Everything that goes with it, from a full grep (`--include=*.py --include=*.md`, pycache
excluded): the module docstring example at `evidence_gate.py:34` and `:37`, the `__all__`
entry at `:72`, the definition at `:113`, the cross-reference at `:146`, the test import at
`test_evidence_gate.py:41`, and the three test methods above. Seven sites, one file each.

## Q3 — the reachability trap

A derived test, not an enumerated one: read `__all__` from `evidence_gate`, and for each
name assert a caller exists **outside** the module. That is the only form that survives a
future export being added, because it does not carry a second copy of the list that can be
forgotten the same way. Enumerating the two current names is a list that drifts — the
defect this phase keeps finding.

It must also be vacuity-guarded. A search that finds nothing and a search that is looking
in the wrong place produce the same green, so the test needs a positive control: a name
known to have a caller must be found to have one, in the same run.
