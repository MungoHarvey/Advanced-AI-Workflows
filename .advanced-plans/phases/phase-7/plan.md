# Phase 7: AAW Multi-Host Routing and Deterministic Installer

Workstream 3 of the v0.2 design.

> **Planned, not decomposed.** Loops are written when Phase 6 passes its gate.

## Objective

Make AAW's routing and installation host-neutral, so no runtime is detected only by another
runtime's private path, and so installing or refreshing never destroys guidance a user wrote
themselves.

## Scope

### Included

- A tracked `.aaw/project.toml` schema and parser.
- A small fenced `AGENTS.md` routing block shared by Codex, OpenCode, and Cursor.
- An updated fenced `CLAUDE.md` block carrying only Claude-specific mechanics.
- Canonical AAW skills installed to both `.agents/skills/` and `.claude/skills/`.
- Component detection driven by the installation manifest and package commands.
- README, ARCHITECTURE, SETUP, DESIGN-RATIONALE, and ROADMAP brought current.

### Explicitly NOT included

- Runtime-specific Plannotator fallbacks. The design listed these; they are withdrawn with the
  deprecation. The cross-model gate needs no per-host fallback.
- The registry and `aaw` CLI. Phase 8.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Project config | TOML + parser + schema | `.aaw/project.toml` |
| Shared routing block | Markdown, fenced | `AGENTS.md` |
| Claude-specific block | Markdown, fenced | `CLAUDE.md` |
| Canonical skills | Markdown | `.agents/skills/`, `.claude/skills/` |
| Manifest-driven detection | Implementation | `setup-with-claude` + `.aaw/` |
| Current documentation set | Markdown | Repository root and `docs/` |

## Success Criteria

- ✓ No host is detected only by another host's private path — the v0.1 failure mode where
  `.claude/commands/…` stood in for a component being installed.
- ✓ Install and refresh preserve user-authored guidance outside the fenced blocks — proven by a
  test with user content deliberately placed adjacent to the fences.
- ✓ Cursor and OpenCode can use `AGENTS.md`; Codex discovers `.agents/skills/`; Claude discovers
  `.claude/skills/`.
- ✓ The three-tool flow works end to end on Claude Code.
- ✓ At least the planning-to-task portion works on every other target host.
- ✓ ACC-01: a fresh Windows install into a path containing spaces passes `doctor`, and every
  configured host discovers the intended guidance.
- ✓ Every user-facing document describes what was observed, not what was designed.

## Dependencies

### Must complete before this phase

- Phase 4 — the installation manifest and the deterministic audit.
- Phase 5 — the AAW-owned routing this phase generalises across hosts.
- Phase 6 — the adapters this phase's detection registers.

### Blocked by

- Nothing beyond those. This phase is where the three earlier strands converge.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Fenced-block rewriting eats user content | Medium | **High** | A test that places user content immediately above and below the fences and asserts byte-identical survival across install, refresh, and uninstall |
| `AGENTS.md` and `CLAUDE.md` drift apart | Medium | Medium | Generate both from one source; a divergence check in CI |
| Documentation claims an integration only simulated | Medium | High | The design's non-goals forbid it. Each claim cites the test that exercised it |
| Paths containing spaces break the installer | Medium | High | ACC-01 tests exactly this; the Phase 3 pilot already used such a path |

## Notes / Design Decisions

- The fenced-block contract is the highest-consequence thing in this phase: it is the one place
  where AAW writes into a file the user also owns. Its test deserves to be written first.

## Ralph Loops

To be decomposed after the Phase 6 gate passes.
