# Phase 6: Advanced Planning Multi-Runtime Adapters

Workstream 2 of the v0.2 design.

> **Planned, not decomposed.** Loops are written when Phase 5 passes its gate. The kickoff scope
> is to plan later workstreams in full at phase level and execute only Workstreams 0, 1A, and 1B.

## Objective

Make Advanced Planning usable from every target runtime, with the controller remaining the sole
writer of programme state, so that a worker on any host can be given an immutable task and return
evidence that is validated before it advances anything.

## Scope

### Included

- Move host-neutral skills and schemas into canonical core locations.
- Add Codex, OpenCode, and Cursor adapter installers alongside the existing `claude-code` and
  `cowork` platforms.
- Add the immutable external-task envelope schema and the collected-evidence schema (design §9.2, §9.3).
- Teach the orchestration skills to emit an external task rather than mutate state from a worker.
- Add path and schema tests, and a CI path audit.

### Explicitly NOT included

- The `aaw` CLI, registry, or dispatcher. Phase 8.
- Per-host Plannotator fallback text. Deprecated; the cross-model gate is host-neutral and needs none.
- Gemini CLI. Out of the v0.2 runtime set.

## Scope correction from the baseline audit

The design (§7.1) proposes creating a `core/` + `platforms/` portable layout. **That layout already
exists** in `MungoHarvey/advanced-planning` at `v0.16.0`: `core/` holds 9 host-neutral skills plus
schemas, constraints, agents, and state; `platforms/` holds `claude-code`, `cowork`, and `python`;
`docs/adapting-to-new-platforms.md` is already the contract.

So this phase is **not** a from-scratch restructure. It is: add three platforms alongside the two
that exist, add the two run-contract schemas, and add the CI path audit. Estimate accordingly.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Codex adapter | Installer + platform dir | `advanced-planning`: `platforms/codex/`, `setup/codex/` |
| OpenCode adapter | Installer + platform dir | `advanced-planning`: `platforms/opencode/`, `setup/opencode/` |
| Cursor adapter | Installer + platform dir | `advanced-planning`: `platforms/cursor/`, `setup/cursor/` — only if Cursor survives the Phase 3 decision |
| External task envelope | JSON Schema | `advanced-planning`: `core/schemas/` |
| Collected evidence schema | JSON Schema | `advanced-planning`: `core/schemas/` |
| Path audit | CI check | `advanced-planning` CI |

## Success Criteria

- ✓ Every target host discovers the same named core planning skills — not host-specific copies
  that drift.
- ✓ A fixture programme can create one phase, one loop, and one external task on every target host.
- ✓ Only the control checkout updates programme state; a worker attempting a planning-state edit
  fails collection — ACC-08.
- ✓ Collected evidence advances a loop only after both schema validation and gate validation pass.
- ✓ The CI path audit fails on any host-specific path in `core/`.
- ✓ No adapter duplicates a core skill's content; adapters install and register, they do not fork.

## Dependencies

### Must complete before this phase

- **Phase 4 (packaging repair).** The installation manifest is what adapters register into and what
  host-neutral detection reads. Without it, every adapter reinvents path probing.
- Phase 3 — the runtime set must be settled before three adapters are written for it.

### Blocked by

- The Phase 3 Cursor decision. Writing a Cursor adapter for a CLI that is not installed produces
  an adapter nobody can test — and the design's non-goals forbid claiming an untested integration.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| An adapter is written but never exercised on its host | Medium | High | Every adapter needs the fixture programme run on its actual host, or it does not ship |
| Core skills drift into host-specific assumptions | Medium | High | The CI path audit is the enforcement; a review note is not enough |
| The worker/controller boundary is documented but not enforced | Medium | High | ACC-08 must be an executed test, not a policy statement |
| Advanced Planning's own release cadence conflicts with the AAW programme | Low | Medium | AAW pins a tested Advanced Planning commit in the compatibility manifest |

## Notes / Design Decisions

- Advanced Planning is an **owned repository with no external upstream**, so this phase has no
  fork-sync risk — unlike Phases 4 and 5.
- Release target on completion: **Advanced Planning v0.17.0**.

## Ralph Loops

To be decomposed after the Phase 5 gate passes.

*(Decomposed 2026-08-27 — see `loops.md`: 6 loops, 30 todos. The line above is left as
written; it describes the plan's state at authoring, not now.)*

## Amendment — 2026-08-28, after loop-002-1

Loop-002-1 settled where the two run-contract schemas live, and found that this plan's own
Key Deliverables table sends them to the wrong directory. The original text above is left
intact for provenance; where the two disagree, **this amendment governs.**

**The location is wrong; the form is right.** The table gives:

| External task envelope | JSON Schema | `advanced-planning`: `core/schemas/` | ← wrong |
| Collected evidence schema | JSON Schema | `advanced-planning`: `core/schemas/` | ← wrong |

Both belong in `core/state/`, as draft-07 JSON Schema:

- `core/state/external-task-envelope.schema.json`
- `core/state/collected-evidence.schema.json`

Two reasons, and the second is the decisive one.

1. **The split is by role, not by file type.** `core/schemas/` holds prose specifications of
   documents a human or agent **authors** — `handoff`, `phase-plan`, `ralph-loop`, `todo`.
   `core/state/` holds JSON Schema for contracts exchanged at a **process boundary** —
   `loop-ready`, `loop-complete`, `gate-verdict`, `gate-failure-context`. `core/state/README.md`
   is titled *"State Bus Protocol"* and its Files table names the writer and reader of each.
   Mutability is not the line: `gate-verdict` is immutable and lives in `core/state/` regardless.
   Both new artefacts are boundary contracts — the envelope validated before dispatch, the
   collected evidence before it advances any state.

2. **`core/schemas/` is validated by nothing.** CI job 2 (`schema-validation`) globs
   `core/state/*.json` and only that. A `.json` file placed in `core/schemas/` would be checked
   by no job at all, while also being the only JSON file in a directory of prose. So the
   original location would have founded a third convention *and* left the result unvalidated.

**Consequently `ci.yml` needs no change** for these two files — which is a property of the
corrected location, not a coincidence.

**A defect in job 2, found while establishing that.** The job calls `json.loads()` and nothing
else. Run against its exact logic, a schema with a typo'd keyword (`"requried"`) and a plain
`{"hello": "world"}` both pass. It proves a file is JSON, not that it is a valid JSON Schema,
and it never loads a fixture. This matters for loop-002-4, whose ≥5 invalid fixtures must each
fail for a *different named reason* — a typo'd keyword makes every one of those assertions
vacuous while the suite still reports green. **Loop-002-5's work is therefore strengthening
that check, not extending the glob**, and its success criterion should be read that way.

**Not changed by this amendment:** `docs/*.schema.md` remains a legitimate third convention —
LOCKED compaction contracts, a status marker none of the four `core/schemas/` files carries.
Neither new schema belongs there; neither is a compaction artefact and neither is frozen.

Full reasoning, including the independent cross-model review and where the controller's own
first answer was wrong: `.advanced-plans/evidence/2026-08-28-loop-002-1-schema-location.md`.

## Amendment — 2026-08-28, after loop-003-1

Loop-003-1 read `platforms/python/path_audit.py` and found that **loop-003-2 as scoped cannot be
completed without leaving the test suite red.** The original loop text is left intact for
provenance; where the two disagree, **this amendment governs.**

`platforms/python/tests/test_path_audit.py:237-252` is
`TestFalsePositiveGuard::test_claude_skills_ref_is_not_flagged`. It writes
``Load skill from `.claude/skills/plan-todos/SKILL.md`.`` into `core/agents/worker.md` and asserts
**no violation**, under a test name and docstring that call the reference *legitimate*.

That is precisely the behaviour design §7.3 forbids — a host directory inside `core/` — and
precisely what loop-003-2 exists to start failing. The test is not hypothetical either:
`core/agents/worker.md` is one of five real files under `core/` carrying host tokens today.

Loop-003-2's `allowed_paths` were `["platforms/python/path_audit.py", "docs/path-conventions.md"]`.
The test file does not become writable until loop-003-4, so the todo had no way to land a green
suite.

**Two changes, both to loop-003-2:**

1. `allowed_paths` gains `platforms/python/tests/test_path_audit.py`.
2. A check is added requiring that the guard be **inverted and renamed, not deleted.** A test
   asserting the old wrong behaviour must become one asserting the new right behaviour, so the
   guard survives the change rather than being removed by it. Deleting it would leave the new rule
   with no test of its most important boundary.

Nothing else in loop-003 changes. In particular loop-003-4 keeps its own mutation test: 003-2's
inverted guard proves the rule fires on a fixture, and 003-4 proves it fires end-to-end through the
CLI and exits 1.

**A decision loop-003-2 must name rather than make silently.** Only `core/agents/` and
`core/skills/` are scanned roots. `core/schemas/` and `core/state/` are canonical parts of `core/`
per `docs/path-conventions.md:31-36` and are outside every root, so "core files must contain no
host directory" is not enforced over all of `core/`. Widening the roots is a larger change than
adding a rule and will surface hits in files nobody has looked at. Whether to do it now is a call
for that todo to state and justify, either way.


---

## Amendment — 2026-08-28, after loop-003-5, before loop-004-1

**Loop 004 specifies five adapter contracts. `docs/adapting-to-new-platforms.md` defines six.**

Found by reading the doc against the loop that cites it, before dispatching loop-004-1.

`### Contract 6 — Shared Python Runtime` appears in that document at line 77 and is absent from
loop-004-1's checks, from loop-004-2's, and from loop-004-3's. It is not a minor contract: five of
the twelve items in the doc's own *Minimum Adapter Checklist* concern it, and it is the contract
that decides whether an adapter works anywhere other than the source checkout.

**Why the omission is dangerous rather than untidy.** Contract 6 is the manifest-and-launcher rule
— the installer writes `.advanced-plans/runtime.json`, copies `platforms/python/ap_launcher.py`
to `.advanced-plans/bin/ap.py`, and does both *outside* any "planning data already exists, skip
the scaffold" guard. That is exactly the defect **ralph-loop-001 of this phase** was created to
fix, after finding the shared Python runtime unreachable from every installed project and thirteen
dead call sites across six installed commands. Two adapters built to loop-004 as written would
reproduce that defect on two new hosts, and it would not be visible in either tree: the failure
appears only when the adapter is installed somewhere and a module is run.

**Why it was omitted — the cause is datable, and it is ours.** Design §7.3 reads *"Each adapter
must implement five contracts already described conceptually in
`docs/adapting-to-new-platforms.md`"*. That paragraph was written on 2026-08-26. **Contract 6 was
added to the doc on 2026-08-27, by loop-001's own fix.** The plan inherited the design's "five" and
nothing propagated the sixth contract forward. The phase created a new adapter obligation and did
not tell its own later loops about it — which is the same class of failure as a check that reports
green over ground it does not examine, expressed across documents rather than inside one.

**Changes, all to loop-004:**

1. `task_name`, `loop-004-1.content` and the loop `prompt` say **six** contracts, with the reason.
2. `loop-004-1` gains a Contract 6 check requiring the specification to state the manifest, the
   launcher, the scaffold-guard rule, and the three extra `--global` obligations.
3. `loop-004-2` and `loop-004-3` each gain a Contract 6 check that must be proven by **installing
   into a scratch project and running a module there**, not by reading the installer. Reading the
   installer is how this survived thirteen call sites the first time.
4. The loop's success criteria gain the same item.

**A second, smaller correction in the same place.** `loop-004-1.content` said *"the four extra
requirements in design §7.3"*. §7.3 lists **five** — discovery, invocation, delegation, state I/O,
human gate — and the loop's own check line already enumerated all five. Corrected to five.

**Carried, not fixed here:** design §7.3's "five contracts" sentence is now false about the
document it cites. A dated correction note is added at that paragraph rather than a rewrite, since
the design is the programme's signed artefact and §9.3's earlier correction was made under an
explicit decision. Whether §7.3 should be restated properly is a call for the phase gate.


---

## Amendment — 2026-08-28, after loop-004-1, before loop-004-2

**The specification loop-004-1 produced cannot be built under loop-004-2's `allowed_paths`.**

Found by reading the specification against the loops that consume it, before dispatching 004-2.
Two independent instances, same shape.

**1. The shared skill payload.** The envelope asked loop-004-1 to *decide* what happens when both
adapters install into the same project rather than discover it in loop-004-4. It decided: one
shared, byte-identical copy at `platforms/shared/agent-skills/advanced-planning/`, created by
004-2, consumed unchanged by 004-3, with a digest conflict rather than a silent overwrite, and an
uninstall that must not remove a copy the other adapter still registers. That is the right answer
and it is not buildable: `platforms/shared/` was in neither build loop's `allowed_paths`. A builder
obeying its constraints — the mechanism by which these loops are actually bounded — would have had
to violate them or make two diverging copies, which is the outcome the decision exists to prevent.

**2. §7.3 requirement 4 has never been implementable.** The specifier checked whether production
code validates state against the canonical schemas instead of assuming it does.
`platforms/python/state_manager.py` serialises, parses and checks one completion enum; it validates
nothing. The repository's real validator is `minischema.py`, a 374-line library under
`platforms/python/tests/` — the one directory the AST check excludes. So *"validate the same core
JSON schemas without rewriting paths to a host-private state directory"* is a requirement that no
adapter can satisfy by wiring itself to code that exists. A shared production module,
`platforms/python/state_validate.py`, is a prerequisite for both adapters. `platforms/python/` was
also outside both build loops' `allowed_paths`.

This is a requirement the plan has carried since it was written, and it was found by reading the
code the requirement would have to call.

**Changes, all to loop-004:**

1. `loop-004-2.allowed_paths` gains `platforms/shared/` and `platforms/python/`, with the reason.
   It gains two checks: the shared payload created once and installed byte-identical with a
   conflict on mismatch; and `state_validate.py` existing, standard-library only, resolving schemas
   from the recorded `source_root`, and reached through `ap.py`.
2. `loop-004-3` gains a check that it consumes the shared payload rather than forking it, reuses
   the validator rather than writing a second one, and that installing in either order leaves one
   identical tree. `platforms/shared/` is read, not written, for that todo.
3. `loop-004-4`'s fixture run gains the both-orders install as an explicit case — the only place
   the collision decision is exercised on a host rather than asserted.

`core/` remains forbidden to every build todo. Nothing here relaxes the no-fork rule; both changes
widen a path constraint to accommodate a shared location, which is the opposite of forking.

**Carried, not fixed here:** `DEFAULT_SCANNED_ROOTS` does not include `platforms/codex/`,
`platforms/opencode/` or `platforms/shared/`. Two of the three directories loop-004 creates will be
invisible to the audit ralph-loop-003 spent five todos building — the same scan-surface gap as
`core/schemas/` and `core/state/`, now named in six places and still not scheduled.
