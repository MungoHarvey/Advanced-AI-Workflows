# Phase 9: Cross-Host End-to-End Tests and Release

Workstream 5 of the v0.2 design. The final phase.

> **Planned, not decomposed.** Loops are written when Phase 8 passes its gate.

## Objective

Establish that every claim the released documentation makes was actually observed, on this
platform, from a fresh clone — and then cut AAW v0.2.0 and Advanced Planning v0.17.0 against the
exact commits that were tested.

## Scope

### Included

- A Windows-native compatibility matrix.
- Fixture repositories and recorded commands for every target host.
- A fork/update regression suite.
- An install / refresh / uninstall regression suite.
- A full design-to-gate scenario exercised with two different providers.
- Release notes and a tested compatibility manifest.
- The `v0.2.0` and Advanced Planning `v0.17.0` tags, after all gates pass.

### Explicitly NOT included

- Any new feature. If something is missing at this point it is v0.3, not a late addition here.
- Merging without review. Default branches are protected by reviewed PRs.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Compatibility matrix | Markdown + generated manifest | `docs/`, `.aaw/compatibility.json` |
| Fixture repositories | Git fixtures + recorded commands | `tests/fixtures/` |
| Regression suites | Tests | `tests/` |
| End-to-end scenario record | Markdown | `.advanced-plans/evidence/` |
| Release notes | Markdown | `CHANGELOG.md` |
| Tags | Annotated Git tags | `v0.2.0`; advanced-planning `v0.17.0` |

## Success Criteria

- ✓ Every critical acceptance scenario (ACC-01 to ACC-18) passes **from a fresh clone**, not from
  a developer's warm working tree.
- ✓ Default branches are protected and every change landed through a reviewed PR.
- ✓ No document claims an integration that was only simulated. Each claim names the test that
  exercised it.
- ✓ The release commits match the compatibility manifest SHAs exactly.
- ✓ `VERSION`, the `CHANGELOG` heading, and the tag agree — the release rule from `docs/releasing.md`.
- ✓ The full design-to-gate scenario ran with two genuinely different providers, and which model
  played which role is recorded — ACC-18.

## Dependencies

### Must complete before this phase

- Phases 3 through 8, all gated.

### Blocked by

- **The external-write gate.** Pushing branches, pushing tags, opening PRs, and merging are human
  gates under `docs/releasing.md`. An agent may prepare the entire release and may not perform it.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| A scenario passes on a warm tree but fails from a fresh clone | Medium | **High** | Every acceptance run starts from `git clone` into a temporary directory. This is exactly how the v0.1 packaging defect escaped |
| Documentation outruns the evidence | Medium | High | Each user-facing claim carries a pointer to the test that produced it; unbacked claims are cut, not softened |
| Tags are pushed before gates pass | Low | High | `docs/releasing.md` rule 3: push and release are human gates. The tag is prepared locally and waits |
| A late "small fix" lands untested | Medium | Medium | Feature freeze at phase entry; anything new becomes v0.3 |

## Notes / Design Decisions

- **This phase's real product is the evidence, not the tag.** The tag is cheap; the claim that the
  tag is trustworthy is what took eight phases.
- v0.1's lesson is embedded in the first success criterion: it shipped documentation for an install
  source that was never in the repository, because nobody tested from a fresh clone. Phase 4 fixes
  the defect; this phase makes the class of defect impossible to ship again.

## Ralph Loops

To be decomposed after the Phase 8 gate passes.
