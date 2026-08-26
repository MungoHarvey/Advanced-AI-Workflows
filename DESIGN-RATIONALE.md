# Design Rationale

This document explains the decisions behind Advanced AI Workflows — why these four tools, why this integration approach, and the key trade-offs accepted along the way.

It is the companion to [ARCHITECTURE.md](ARCHITECTURE.md), which describes *what* the system does. This document describes *why* it is built this way.

> **Version scope:** this records the v0.1 Claude Code design rationale. The [v0.2 orchestration design](.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md) retains boundary integration while adding Herdr, explicit fork policy, deterministic packaging, and multi-runtime adapters. Its decisions supersede v0.1 statements about execution sessions, status ownership, and the absence of package patches.

---

## Why Four Tools?

No single tool covers the full think, plan, review, execute, review cycle. Each of the four tools solves a distinct problem well and stops where the next tool begins.

**gstack** is the high-level strategic planner and reviewer. Commands like `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, and `/codex` front the pipeline. Gstack writes design docs to `~/.gstack/projects/{slug}/` — durable, project-independent, kept across machine sessions. It does not decompose work into phases or todos; it produces the strategic input that feeds the execution machinery.

**advanced-planning** owns execution structure. Its three-tier hierarchy (Phases, Ralph Loops, Todos) decomposes large programmes into bounded, resumable units of work. The filesystem state bus (`.advanced-plans/state/`) enables crash recovery and session resumption without relying on agent memory. Plans live in the local project (`.advanced-plans/`), not in a remote service.

**superpowers** is a tactical helper, not the main planning engine. Brainstorming, TDD, systematic debugging, and code review as modular skills. Invoked contextually throughout execution — each skill injects focused instructions for exactly one todo, then gets out of the way. Superpowers' skill library is the integration currency that advanced-planning consumes: any skill file in `.claude/skills/` or `~/.claude/skills/` can be assigned to a todo.

**plannotator** is the human-in-the-loop checkpoint. Browser-based annotation UI for visual plan and code review. When plannotator is installed as a Claude Code plugin, review integration is entirely automatic — no glue, no extra configuration.

### Why not three tools?

The prior three-tool framing (advanced-planning + superpowers + plannotator) left a gap at the strategic layer. There was no dedicated high-level planner with review commands (`/plan-ceo-review`, `/plan-eng-review`, `/codex`). Design docs were produced by superpowers brainstorming and written to a non-standard path that advanced-planning could not reliably consume. Adding gstack fills the strategic gap cleanly and gives the four-tool system a single front door for ambiguous problems.

---

## Why Boundary Integration?

The deliberate choice was to integrate at boundaries — file handoffs, hook protocols, markdown documents — rather than merging the four codebases into one or forking sub-packages.

### Benefits

**Independent utility.** Each tool works alone. A team that only wants visual plan review uses plannotator. A team that only wants hierarchical planning uses advanced-planning. The integrated workflow is the highest-value configuration, but it is not the only valid one.

**No patches required.** The integration is entirely via routing, preference overrides, and one glue skill. The sub-packages are unmodified — this is a locked design decision (Tension 1: pure markdown SKILL.md, no executable helpers, no sub-package patches). This means upstream improvements pull cleanly with zero merge conflict overhead.

**Testability.** Each integration boundary is a well-defined interface: a markdown file, a JSON payload on stdin/stdout, a `SKILL.md` in a known directory. Each tool's test suite remains fast, focused, and self-contained.

### Trade-offs

**Configuration surface.** Four tools means four detections, four optional installs, and more things that can be misconfigured. The `setup-with-claude` skill mitigates this by walking Claude through detection and install interactively.

**Best-effort compliance.** The glue skill (gstack-to-plans) instructs Claude to perform file operations. Claude reads the SKILL.md and executes the steps. When Claude is unsure — multiple matches, destination exists, unexpected pattern — it invokes `AskUserQuestion` for permission rather than guessing. This trades deterministic file-tool semantics for a contract Claude can actually honour turn-to-turn.

---

## Key Architectural Decisions

### gstack at the strategic layer

**Context.** Before gstack was added, the system had no dedicated strategic planner. Superpowers brainstorming was being used as a substitute — but brainstorming is a tactical helper, not a strategic planning engine. It lacks the review commands (`/plan-ceo-review`, `/plan-eng-review`, `/codex`) that validate a plan before committing to implementation.

**Decision.** gstack is the front door for ambiguous problems and quality reviews. It sits at the top of the pipeline and at quality gates. All other tools are downstream of a gstack design session.

**Rationale.** The pipeline now has a clear shape: gstack produces strategic input → glue copies it to the project → advanced-planning structures execution → superpowers provides methodology → plannotator reviews output. Each tool has a non-overlapping role. The system's "single front door" property comes from gstack, not from the meta-project itself.

**Trade-off.** gstack requires a separate install and writes to `~/.gstack/projects/` outside the project repo. Users who do not have gstack can still use advanced-planning directly; the glue layer is just bypassed. The dual-write property (gstack origin immutable, `.advanced-plans/specs/` is the project-resident copy) means the design doc travels with the repo even though gstack itself is global.

**Locked decision reference:** Premise 1 — "gstack is the high-level strategic planner and reviewer — sits at the front of the pipeline and at quality gates."

### One glue skill is enough

**Context.** The integration between gstack and advanced-planning requires bridging two different write locations: gstack writes to `~/.gstack/projects/{slug}/`, advanced-planning reads from `.advanced-plans/specs/`. Multiple approaches were considered: a deterministic shell script, a complex webhook, an automated sync daemon.

**Decision.** A single pure markdown `SKILL.md` (`gstack-to-plans`) handles the bridge. Claude reads it, finds the relevant design doc, and copies it to `.advanced-plans/specs/`. An auto-trigger `PostToolUse` hook in `.claude/settings.json` surfaces the suggestion to run `/gstack-to-plans` when a gstack write is detected, but the fallback (manual command + CLAUDE.md routing instruction) means the hook is not the sole mechanism.

**Rationale.** The glue needs to handle edge cases (multiple design docs, destination exists, detached HEAD) — and these edge cases are best handled by asking the user, not by automating a guess. A markdown skill with `AskUserQuestion` at every ambiguous branch is more robust than a script that makes silent decisions. The hook adds ergonomics without making the system fragile if the hook misfires.

**Trade-off.** Best-effort compliance — Claude must be present to run the glue. A fully automated daemon would not require Claude, but it would require installation of a background process, adding runtime complexity and defeating the "no sub-package modification" constraint.

**Locked decision reference:** Issue 3A — "divergence policy is abort + AskUserQuestion presenting diff and three choices (overwrite / skip / view full diff). No silent overwrites." Tension 1 — "pure markdown SKILL.md, no executable helpers."

### Instructions-not-scripts for setup

**Context.** The original `setup-with-claude` was a shell script. Shell scripts are fast and deterministic — but they are brittle across the heterogeneous environments (Windows/macOS/Linux, different plugin install methods, different existing configurations) that external users will have. A script that works on the developer's macOS may silently fail or destructively overwrite on a user's Windows PowerShell session.

**Decision.** `setup-with-claude` is instructions-Claude-reads-and-executes, not a deterministic script. The `SKILL.md` walks Claude through detection, install, routing-block wiring, permissions grant, glue install, and verification — asking for confirmation before any destructive step.

**Rationale.** Claude is the agent running the setup. Claude can adapt to the user's environment, ask clarifying questions, and recover from unexpected states in ways a script cannot. The meta-project is Claude-native by scope (v0.1 is Claude Code only), so the tradeoff — losing some determinism in exchange for environment robustness — is acceptable. The fenced markers in CLAUDE.md (`<!-- aaw-routing:begin -->` / `<!-- aaw-routing:end -->`) preserve safety: the setup skill never overwrites silently and the uninstall path is clean.

**Locked decision reference:** Tension 3 — "`setup-with-claude` is instructions Claude reads and executes, not a deterministic script."

### Why no exploration-notes integration

**Context.** Advanced-planning's `/plan-and-phase` Step 2 writes exploration notes to `.advanced-plans/exploration-notes.md`. The question arose whether the gstack design doc should be copied there (alongside `.advanced-plans/specs/`) so that `phase-plan-creator` could read it as part of the Step 2 exploration context.

**Decision.** No exploration-notes integration. The design doc reaches `phase-plan-creator` via `$ARGUMENTS` to `/plan-and-phase` or `/new-phase` only. The glue's final action is to print the archived path and tell the user the next command to run.

**Rationale.** The `exploration-notes.md` channel is owned by advanced-planning's own explore step — it writes discovery notes about the codebase. Injecting a gstack design doc into that channel would mix two different kinds of context: codebase-exploration notes (what `/plan-and-phase` Step 2 writes) and high-level design intent (what gstack produces). Keeping them separate means `phase-plan-creator` receives a clean `$ARGUMENTS` context with the design doc content, without mixing in codebase notes that may not be relevant to every planning session.

**Locked decision reference:** Issue 1A — "archive-only handoff. No exploration-notes integration. Design doc reaches phase-plan-creator via `$ARGUMENTS` only."

---

## Why Boundary Integration?

### Benefits

**Independent utility.** Each tool works alone. A team that only wants visual plan review uses plannotator. A team that only wants hierarchical planning uses advanced-planning. A team that only wants methodology skills uses superpowers. The integrated workflow is the highest-value configuration, but it is not the only valid one.

**Upstream sync without pain.** No sub-package patches are required for v0.1. All integration is via routing, preference overrides, and one glue skill. This means upstream improvements from advanced-planning, superpowers, plannotator, and gstack pull cleanly with zero fork-maintenance overhead.

**Contributor isolation.** Contributing to advanced-planning requires understanding its planning model. Contributing to superpowers requires understanding markdown skill design. Contributing to plannotator requires understanding the hook protocol. Contributing to the meta-project requires understanding how to wire tools together. These are different skill sets; boundary integration preserves the separation so contributors do not need to understand all four domains to make a change in one.

**Testability.** Each integration boundary is a well-defined interface: a markdown file, a JSON payload, a `SKILL.md`. These interfaces can be tested in isolation.

### Trade-offs

**Configuration surface.** Four tools means four detections, four optional installs, and more things that can be misconfigured. `setup-with-claude` mitigates this by walking Claude through all of it interactively.

**Hook conflicts.** Multiple tools interact with Claude Code's hook system. The meta-project's `PostToolUse` hook is scoped strictly to `~/.gstack/projects/` writes to avoid spurious invocations. Plannotator's `ExitPlanMode` hook fires more broadly. The known gap (plannotator popup noise on short planning sequences) is documented in SETUP.md.

**Conceptual overlap.** Both gstack and superpowers have opinions about what a design document should contain. The meta-project resolves this by assigning non-overlapping roles: gstack produces strategic design docs (front of pipeline, quality gates), superpowers produces tactical plans and explorations (during execution). They write to the same archive (`.advanced-plans/specs/`) for unified discoverability.

---

## Open Questions

1. **Multi-runtime support (v0.2+).** The integrated four-tool flow is Claude Code only in v0.1. CLAUDE.md routing, `.claude/skills/` install paths, and `.claude/settings.json` permission grants are Claude-specific. Advanced-planning supports both Claude Code and OpenCode independently; the meta-project integration with OpenCode is not yet designed. See ROADMAP.md for the v0.2+ trajectory.

2. **Gate-to-gstack-review glue.** Deferred to v0.2. When `/run-gate` produces a verdict, invoking gstack's `/plan-eng-review` or `/codex` for a second opinion is the natural next step. This requires a `gate-to-gstack-review` glue skill analogous to `gstack-to-plans`.

3. **Programmatic plannotator detection refinement.** Currently detection relies on checking for `.claude/commands/plannotator-annotate.md`. A more robust detection mechanism is on the ROADMAP.

These questions are tracked in [ROADMAP.md](ROADMAP.md).
