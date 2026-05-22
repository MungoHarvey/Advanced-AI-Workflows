# Phase 1: Four-Tool Integration v0.1

## Objective

Ship the v0.1 meta-project that knits gstack, superpowers, advanced-planning, and plannotator into a coherent think → plan → review → execute → review loop, via routing rules and one thin glue skill, without modifying any sub-package.

## Scope

### Included:
- `gstack-to-plans` glue skill (pure markdown SKILL.md, ask-when-unsure semantics, archive-only handoff to `.advanced-plans/specs/`)
- CLAUDE.md routing template with fenced markers (`<!-- aaw-routing:begin --> ... <!-- aaw-routing:end -->`), four-tool front-door rules, superpowers preference override, closing-instruction fallback, reference to advanced-planning's `companion-detection`
- Auto-trigger hook entry for `.claude/settings.json` — `Stop` / `PostToolUse` matcher scoped tightly to `~/.gstack/projects/`, invoking `/gstack-to-plans`
- `setup-with-claude` rewritten as instructions-Claude-reads (SKILL.md + `references/`), supporting `--uninstall` and `--refresh`, including the `.claude/settings.json` permission grant on `.advanced-plans/`
- Structural rewrites (NOT additive diffs) of: README.md, ARCHITECTURE.md, DESIGN-RATIONALE.md, SETUP.md, ROADMAP.md
- Two upstream PRs: (a) advanced-planning `STRUCTURE.md` cleanup, (b) superpowers `brainstorming` stale default-path fix
- End-to-end smoke test covering REG-1 through REG-7 from the eng-review test plan

### Explicitly NOT included:
- Multi-runtime support (OpenCode, Gemini CLI, Copilot CLI, Codex, Pi) — v0.2+
- `gate-to-gstack-review` glue skill for second opinion at gate boundaries — v0.2+
- Fixture-driven acceptance tests + CI workflow — v0.2+
- `/aaw-status` cross-tool status command — skipped permanently (companion-detection covers it)
- `/aaw-flow` umbrella command — rejected by design
- Sub-package source patches — not v0.1; upstream PRs are the only sub-package-touching work
- New design-doc work on adjacent tools beyond the two PRs

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Glue skill | SKILL.md (markdown) | `.claude/skills/gstack-to-plans/SKILL.md` |
| CLAUDE.md routing block (template) | Markdown fragment | `references/claude-md-routing.md` (consumed by setup skill) |
| Settings.json hook + permissions snippet | JSON fragment | `references/settings-snippet.json` (consumed by setup skill) |
| Setup-with-claude rewrite | SKILL.md + `references/` | `.claude/skills/setup-with-claude/` |
| README rewrite | Markdown | `README.md` |
| ARCHITECTURE rewrite | Markdown | `ARCHITECTURE.md` |
| DESIGN-RATIONALE rewrite | Markdown | `DESIGN-RATIONALE.md` |
| SETUP rewrite | Markdown | `SETUP.md` |
| ROADMAP rewrite | Markdown | `ROADMAP.md` |
| Upstream PR to advanced-planning | Git branch + PR | `advanced-planning` repo |
| Upstream PR to superpowers | Git branch + PR | `superpowers` repo |
| Smoke-test report | Markdown | `tests/v0.1-smoke-report.md` |

## Success Criteria

Each verifiable against a concrete check:

- ✓ `gstack-to-plans` SKILL.md exists at `.claude/skills/gstack-to-plans/SKILL.md`, contains no executable helpers (no `bin/`, no shell scripts), and explicitly instructs `AskUserQuestion` for: multiple-match source selection, dest-exists divergence, source-pattern unexpected.
- ✓ `references/claude-md-routing.md` includes all four front-door rules, the superpowers `brainstorming` + `writing-plans` preference override pointing to `.advanced-plans/specs/`, the closing-instruction fallback, the `companion-detection` reference, and the fenced begin/end markers.
- ✓ `references/settings-snippet.json` defines a `Stop` or `PostToolUse` matcher with a path filter limited to `~/.gstack/projects/`. The matcher does NOT fire on writes elsewhere (verified in REG-7).
- ✓ `setup-with-claude` SKILL.md walks Claude through: detect-each-sub-package → install-missing → wire-routing → grant-permissions → install-glue → write-integrations.json → verify. Supports `--uninstall` and `--refresh`. Includes `references/install-{tool}.md` for each of the four sub-packages.
- ✓ README.md states "Four Tools" framing, includes the v0.1 flow diagram (gstack → glue → advanced-planning → plannotator/superpowers), and contains an explicit "Claude Code only in v0.1" statement.
- ✓ ARCHITECTURE.md contains a "Glue Layer" section, the four-tool boundary table from the design doc, and zero references to `plans/` or `PLANS-INDEX.md` (replaced by `.advanced-plans/`).
- ✓ DESIGN-RATIONALE.md adds subsections: "gstack at the strategic layer", "one glue skill is enough", "instructions-not-scripts for setup", "why no exploration-notes integration".
- ✓ SETUP.md contains a version compatibility matrix (advanced-planning ≥ v0.11.0; pinned minimums for gstack, superpowers, plannotator), the exact `.claude/settings.json` permission entries, and the plannotator-is-automatic note.
- ✓ ROADMAP.md marks v0.1 done; deferred list includes `gate-to-gstack-review`, multi-runtime support (with concrete description of what changes), CI/fixtures, programmatic plannotator-detection refinement.
- ✓ Two upstream PRs opened (URLs recorded in smoke-test report). v0.1 release does NOT block on merge.
- ✓ Smoke test report shows REG-1 through REG-7 all PASS in a fresh project. Specifically REG-7 confirms the hook fires on `~/.gstack/projects/` writes and does NOT fire on writes elsewhere.

## Dependencies

### Must Complete Before This Phase:
- Design doc CEO+ENG cleared at `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-design-20260521-144453.md` — done (commit 5351ad1)
- Eng-review test plan with REG-1..REG-7 at `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-eng-review-test-plan-20260521-152241.md` — done
- Global install of advanced-planning v0.11.0 commands + skills — done this session (synced from local checkout; backup at `~/.claude/_ap-sync-backup-20260521-171809`)

### Blocked By:
- Nothing. All four sub-packages installed and verified locally.

### Optional (nice to have):
- Codex CLI available for ad-hoc second-opinion checks during build (already installed at `/c/Users/mharvey2/AppData/Roaming/npm/codex`)

## Skills Required (Broad Categories)

- `skill-authoring`: Write pure-markdown SKILL.md files with ask-when-unsure semantics for glue + setup
- `claude-code-config`: Settings.json hook + permission entries; CLAUDE.md routing with fenced markers
- `technical-writing`: Structural doc rewrites (README/ARCHITECTURE/DESIGN-RATIONALE/SETUP/ROADMAP)
- `upstream-contribution`: Open + frame PRs to adjacent repos with minimal-surface changes
- `integration-testing`: Manual smoke-test driving the full four-tool flow end-to-end

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| `.claude/settings.json` permission grant missing or malformed → glue silently fails to write to `.advanced-plans/` | Medium | High | REG-1 explicitly verifies the grant is applied and writes succeed; setup-with-claude refuses to finish if the grant cannot be confirmed. Document the failure mode + recovery in SETUP.md. (Critical gap #1 from eng review.) |
| Plannotator `ExitPlanMode` hook fires spurious popups on gstack plan-mode skills (e.g. `/office-hours`) | Medium | Low (UX-only) | Document the behaviour in SETUP.md with a "what to expect when both plannotator and gstack are installed" note; no code workaround in v0.1. (Critical gap #2 from eng review.) |
| Auto-trigger hook matcher scope too loose → fires on writes outside `~/.gstack/projects/` | Medium | Medium | REG-7 negative-path test: write a file outside `~/.gstack/projects/` and assert the hook does NOT invoke `/gstack-to-plans`. Tight glob in the matcher, validated by the smoke test. |
| Compliance drift — Claude doesn't follow the markdown skill exactly (best-effort by design) | Medium | Medium | Ask-when-unsure is the safety net. SKILL.md uses explicit `AskUserQuestion` callouts at every ambiguous branch (multiple sources, dest exists, unexpected pattern). REG-2 and REG-3 verify the ambiguity branches actually prompt. |
| Sub-package versions drift faster than the meta-project's compatibility matrix | Low | Medium | Pin minimum versions in SETUP.md; setup-with-claude's verify-step prints actual vs expected. Mismatch is a warning, not a hard stop. |
| Upstream PRs not accepted by adjacent maintainers | High | Low | Meta-project's existing workarounds (CLAUDE.md preference override, glue archive path) carry forward regardless. PRs ship even if not merged. |
| Structural doc rewrite leaves contradictions with legacy text | Medium | Medium | Rewrites are scoped section-by-section per design doc step 4; reviewer (manual) reads diffs end-to-end before commit. |
| `setup-with-claude --uninstall` damages a CLAUDE.md whose fenced markers are missing or corrupted | Low | High | Skill refuses to edit CLAUDE.md when markers are absent; prints a manual-recovery instruction instead. REG-5 covers this. |

## Assumptions

- `advanced-planning v0.11.0 is the authoritative version`: Globally synced this session; backup at `~/.claude/_ap-sync-backup-20260521-171809`. Validated by the `.advanced-plans/` path appearing in the synced `new-phase.md` and `phase-plan-creator/SKILL.md`.
- `Plannotator hook behaviour stable`: `PreToolUse:EnterPlanMode` (5s timeout, `plannotator improve-context`) and `PermissionRequest:ExitPlanMode` (96h timeout, full visual review) — verified by reading plannotator's `apps/hook/hooks/hooks.json`.
- `Gstack design-doc filename pattern stable`: `{user}-{branch}-design-{datetime}.md` under `~/.gstack/projects/{slug}/` — verified by current session's artifacts.
- `Superpowers brainstorming + writing-plans honour user-preference overrides`: Skills explicitly state "User preferences for ... location override [the default]" — verified by reading skill source.
- `External users have Claude Code available`: v0.1 is Claude-only by scope statement. Multi-runtime is v0.2+.
- `Two critical gaps stay UX-only in v0.1`: Permission failure mode and plannotator popup noise are documented, not code-fixed, in v0.1.

## Notes / Design Decisions

- **Why one glue skill, not several**: archive-only handoff means the only non-trivial seam is gstack → `.advanced-plans/specs/`. Superpowers goes there via preference override (no glue). Plannotator is already wired by advanced-planning's `/plan-and-phase` Step 5b (no glue). Gate→second-opinion is deferred to v0.2.
- **Why markdown SKILL.md, not a script**: Locked Tension 1. Best-effort compliance with ask-when-unsure semantics. Robust to platform variation, fewer moving parts, the meta-project is Claude-native by scope.
- **Why no exploration-notes integration**: Locked Issue 1A. `/plan-and-phase` Step 2 OVERWRITES `.advanced-plans/exploration-notes.md`. Archive-only handoff routes the design doc via `$ARGUMENTS` instead, which is non-destructive.
- **Why dual trigger (hook primary + manual fallback)**: Locked Issue 2A + CEO Expansion #1A. The hook removes the "user forgets" UX risk; the manual + routing fallback covers hook misfires or environments where the hook isn't installed.
- **Why honest Claude-only positioning**: CEO Expansion #4A. Multi-runtime is real future work but undelivered in v0.1; framing it aspirationally damages adoption trust.
- **Open question (carried into Loop 1)**: exact JSON schema for the `.claude/settings.json` permission entry on `.advanced-plans/`. Resolve by reading advanced-planning's `platforms/claude-code/settings.json` for the canonical pattern. Source: design doc Open Question #3.
- **Open question (carried into Loop 1)**: superpowers preference-override syntax — free-prose vs structured marker. Resolve by reading superpowers' `brainstorming` and `writing-plans` skill source. Source: design doc Open Question #2.

## Ralph Loops (6)

| Loop | Name | Type | Key Outputs |
|------|------|------|-------------|
| 001 | Glue skill + routing + hook | Implementation | `gstack-to-plans/SKILL.md`, `references/claude-md-routing.md`, `references/settings-snippet.json` |
| 002 | Setup-with-claude rewrite | Implementation | `setup-with-claude/SKILL.md` + `references/install-{gstack,advanced-planning,superpowers,plannotator}.md` + canonical settings.json entries |
| 003 | Structural doc rewrites | Implementation | New README.md, ARCHITECTURE.md, DESIGN-RATIONALE.md, SETUP.md, ROADMAP.md |
| 004 | Upstream PR — advanced-planning STRUCTURE.md | Migration | Branch + PR URL fixing path references in adjacent repo |
| 005 | Upstream PR — superpowers brainstorming default | Migration | Branch + PR URL updating skill's stale default path |
| 006 | End-to-end smoke test | Validation | `tests/v0.1-smoke-report.md` with REG-1..REG-7 verdicts |
