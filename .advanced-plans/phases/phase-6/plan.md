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
