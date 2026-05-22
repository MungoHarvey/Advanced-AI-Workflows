# Roadmap

---

## v0.1 — Done

**Four-tool integration: gstack + advanced-planning + superpowers + plannotator (Claude Code only)**

- **gstack-to-plans glue skill** — pure markdown `SKILL.md` with no executable helpers. Copies gstack design docs from `~/.gstack/projects/{slug}/` to `.advanced-plans/specs/`. Ask-when-unsure semantics at every ambiguous branch (multiple source matches, destination exists, unexpected filename pattern).
- **PostToolUse auto-trigger hook** — `PostToolUse Write` matcher scoped strictly to `~/.gstack/projects/`. Surfaces `/gstack-to-plans` suggestion in Claude's next turn when a gstack design doc is written. Fallback: manual `/gstack-to-plans` command + CLAUDE.md closing instruction.
- **CLAUDE.md routing template** — four-tool front-door rules with superpowers preference overrides (brainstorming and writing-plans save to `.advanced-plans/specs/`). Fenced begin/end markers for clean install/uninstall.
- **setup-with-claude** rewritten as instructions-Claude-reads — walks Claude through detect, install, wire routing, grant permissions, install glue, write integrations.json, verify. Supports `--uninstall` and `--refresh`.
- **Five repo doc rewrites** (README, ARCHITECTURE, DESIGN-RATIONALE, SETUP, ROADMAP) — four-tool framing, updated Mermaid diagrams, handoff contract table, honest Claude-only positioning.
- **Upstream PR: advanced-planning STRUCTURE.md** — fixes stale path references (`plans/`, `.claude/plans/`, `PLANS-INDEX.md` → `.advanced-plans/`). Pure documentation fix.
- **Upstream PR: superpowers brainstorming default path** — updates the AP-detected default from `.claude/plans/` to `.advanced-plans/specs/`. Behavioural change, trivially correct. CLAUDE.md preference override is the v0.1 workaround if merge is delayed.

---

## v0.2 — Deferred

### gate-to-gstack-review glue skill

When `/run-gate` produces a verdict, invoking gstack's `/plan-eng-review` or `/codex` for a second opinion is the natural next step. v0.1 leaves this gap open: gate verdicts are text-only and do not surface to gstack automatically.

The v0.2 `gate-to-gstack-review` glue skill would mirror `gstack-to-plans` in the other direction: read the gate verdict JSON from `.advanced-plans/phases/phase-N/gate-verdicts/`, format it as a gstack-compatible summary, and invoke `/plan-eng-review` or `/codex` with the relevant context. The same ask-when-unsure semantics apply — Claude asks before invoking a review that will consume gstack capacity.

### Multi-runtime support (OpenCode, Gemini CLI)

v0.1 is Claude Code only. CLAUDE.md routing, `.claude/skills/` install paths, Claude plugin install for plannotator/superpowers, and `.claude/settings.json` permission grants are all Claude Code-specific.

For v0.2+ multi-runtime support, the following needs to change:

- **Routing rules** — OpenCode uses `.opencode/` config; Gemini CLI uses its own config format. The routing template would need per-runtime variants or a runtime-agnostic format both support.
- **Install paths** — `.claude/skills/` is Claude Code-specific. OpenCode uses `.opencode/skills/` or similar. The `setup-with-claude` skill would need detection logic and per-runtime copy targets.
- **Permission grants** — `.claude/settings.json` permission entries are Claude Code-specific. OpenCode uses `opencode.json`; Gemini CLI has its own permission model.
- **Hook mechanism** — the `PostToolUse` hook is a Claude Code plugin protocol. OpenCode supports hooks via `opencode.json` with a different schema. The auto-trigger for `gstack-to-plans` would need a parallel OpenCode hook entry.
- **Plugin install** — plannotator's Claude Code plugin (`/plugin install`) has no direct OpenCode equivalent. The manual install path (Bun build + slash command install) would be the OpenCode route until upstream OpenCode support lands.

The meta-project's boundary-integration design means the underlying tools (gstack, advanced-planning) can already work on OpenCode independently. The v0.2 work is porting the glue and routing layer to be runtime-aware, not re-architecting the integration contracts.

### Fixture-driven acceptance tests + CI workflow

v0.1 has no automated tests. REG-1 through REG-7 are run manually against a fresh project. v0.2 would add:

- Fixture project state for each REG scenario (pre-populated `.advanced-plans/state/`, mock gstack output, etc.)
- CI workflow (GitHub Actions) that runs the setup skill and verifies the expected state at each step
- Pinned sub-package version matrix testing (minimum + current for each sub-package)

### Programmatic plannotator-detection refinement

v0.1 detects plannotator by checking for `.claude/commands/plannotator-annotate.md`. This is fragile — plannotator could be installed with a different command path, or a non-plannotator tool could install the same file. v0.2 would add a more robust detection mechanism, possibly checking for the hook entry in `.claude/settings.json` or for a plannotator-specific marker file.

---

## Skipped (will not happen)

- `/aaw-status` cross-tool status command — companion-detection in advanced-planning already handles superpowers + plannotator detection at natural trigger points. gstack is implicit when gstack commands run. No need for parallel command.
- `/aaw-flow` umbrella command — rebuilds what individual tools already do well.
- Plannotator-on-design-doc glue — plannotator's plan-mode hooks already cover review needs.
- First-run guided tour skill — scope creep without clear payoff.
