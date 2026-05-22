# Phase 1: Four-Tool Integration v0.1 — Ralph Loops

---
name: "ralph-loop-001"
task_name: "Glue Skill + Routing + Hook"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: "Three artifacts produced: .claude/skills/gstack-to-plans/SKILL.md (pure markdown, 4 AskUserQuestion branches), references/claude-md-routing.md (fenced markers, 4 front-door routes, closing instruction, superpowers overrides), references/settings-snippet.json (PostToolUse hook scoped to ~/.gstack/projects/, 4 canonical .advanced-plans/** permission entries). Both open questions resolved: Q2 superpowers override is free-prose (brainstorming SKILL.md line 125, writing-plans SKILL.md line 19); Q3 permission schema sourced verbatim from advanced-planning/platforms/claude-code/settings.json lines 16-19."
  failed: ""
  needed: ""

todos:
  - id: "loop-001-1"
    content: "Read superpowers brainstorming + writing-plans SKILL.md source to confirm preference-override syntax (free-prose vs structured marker)"
    skill: "NA"
    agent: "Explore"
    outcome: "Open question resolved: exact format the override block must use is documented in working notes; cited line(s) in superpowers source"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-2"
    content: "Read advanced-planning's platforms/claude-code/settings.json (or equivalent) to extract canonical permission entries for granting read/edit/write on .advanced-plans/"
    skill: "permission-config"
    agent: "Explore"
    outcome: "Open question resolved: exact JSON entries copied verbatim into working notes; ready to drop into references/settings-snippet.json"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-3"
    content: "Write .claude/skills/gstack-to-plans/SKILL.md as pure markdown with ask-when-unsure semantics covering source-selection, dest-exists, and unexpected-pattern branches"
    skill: "skill-creator"
    agent: "NA"
    outcome: ".claude/skills/gstack-to-plans/SKILL.md exists; contains explicit AskUserQuestion callouts at all three ambiguous branches; zero executable helpers (no bin/, no shell scripts)"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-4"
    content: "Write references/claude-md-routing.md with four-tool front-door rules, superpowers preference override, closing-instruction fallback, companion-detection reference, and fenced begin/end markers"
    skill: "NA"
    agent: "NA"
    outcome: "references/claude-md-routing.md exists; contains <!-- aaw-routing:begin --> and <!-- aaw-routing:end --> markers; all four front-door routes present; closing instruction for /gstack-to-plans fallback present"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-5"
    content: "Write references/settings-snippet.json combining the auto-trigger hook (Stop or PostToolUse, path-filtered to ~/.gstack/projects/) and the .advanced-plans/ permission entries"
    skill:
      - "permission-config"
      - "update-config"
    agent: "NA"
    outcome: "references/settings-snippet.json exists; hook matcher includes ~/.gstack/projects/ path filter and no broader scope; permission entries match the canonical schema from loop-001-2"
    status: completed
    complexity: medium
    priority: high
  - id: "loop-001-6"
    content: "Verify the three artifacts cross-reference correctly: routing template's closing instruction matches the slash command in SKILL.md; settings snippet's hook calls the same slash command"
    skill: "verification-before-completion"
    agent: "NA"
    outcome: "grep across the three files confirms identical slash-command name (/gstack-to-plans) in all references; no name drift; fenced markers parse"
    status: completed
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Produce the meta-project's three primary artifacts: the gstack-to-plans glue skill, the CLAUDE.md routing template, and the .claude/settings.json auto-trigger hook + permissions snippet.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-001"

  ## Success criteria
  - [ ] `.claude/skills/gstack-to-plans/SKILL.md` exists, pure markdown, no executable helpers, explicitly invokes AskUserQuestion at every ambiguous branch (multiple sources, dest exists, unexpected pattern)
  - [ ] `references/claude-md-routing.md` contains four-tool front-door rules, superpowers preference override to `.advanced-plans/specs/`, closing-instruction fallback, companion-detection reference, fenced begin/end markers
  - [ ] `references/settings-snippet.json` defines a Stop or PostToolUse matcher scoped strictly to `~/.gstack/projects/` PLUS the permission entries granting read/edit/write on `.advanced-plans/`
  - [ ] Open questions resolved by reading source: superpowers preference-override syntax (free-prose vs marker) and `.claude/settings.json` permission schema (cross-reference advanced-planning's `platforms/claude-code/settings.json`)

  ## Required skills
  - `skill-authoring`: Write pure-markdown SKILL.md with ask-when-unsure semantics
  - `claude-code-config`: Hook matcher syntax + permission entries

  ## Inputs
  - Design doc: `C:\Users\mharvey2\.gstack\projects\MungoHarvey-Advanced-AI-Workflows\mharvey2-main-design-20260521-144453.md` (Section: Components, Next Steps 1+2+2b)
  - Eng-review test plan: `mharvey2-main-eng-review-test-plan-20260521-152241.md` (REG-1, REG-2, REG-3, REG-7)
  - Reference for permission schema: `C:\Users\mharvey2\Documents\Coding\advanced-planning\platforms\claude-code\settings.json` (if present) or equivalent
  - Reference for superpowers preference syntax: `C:\Users\mharvey2\Documents\Coding\planning-architectures\superpowers\` brainstorming + writing-plans skill sources

  ## Expected outputs
  - `.claude/skills/gstack-to-plans/SKILL.md`
  - `references/claude-md-routing.md`
  - `references/settings-snippet.json`

  ## Constraints
  - No executable helpers — markdown only
  - Fenced markers `<!-- aaw-routing:begin -->` / `<!-- aaw-routing:end -->` must wrap the routing block
  - Hook matcher must NOT fire on writes outside `~/.gstack/projects/`
  - Divergence policy = abort + AskUserQuestion (overwrite / skip / view diff) — no silent overwrites

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-001 — glue skill, routing template, hook + permissions"
  2. Update handoff_summary (done / failed / needed)
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
Produces the core integration surface: the glue skill that copies gstack design docs to `.advanced-plans/specs/`, the CLAUDE.md routing template installed by `setup-with-claude`, and the matching `.claude/settings.json` snippet (auto-trigger hook + permissions). Everything downstream depends on these three artifacts.

## Success Criteria
- ✓ Glue skill markdown-only, ask-when-unsure: grep the SKILL.md for `AskUserQuestion` and confirm it covers source-selection, dest-exists, and unexpected-pattern branches
- ✓ Routing template has all four front-door rules, the override block, the closing instruction, and fenced markers
- ✓ Settings snippet matcher restricted to `~/.gstack/projects/` (REG-7 negative path will validate this in loop 006)
- ✓ Permission entries on `.advanced-plans/` modelled after advanced-planning's canonical schema

## Skills Required

### Broad (from phase plan):
- `skill-authoring`: Pure-markdown SKILL.md with ask-when-unsure
- `claude-code-config`: Hook + permission entries

### Specific (refined for this loop):
- `claude-code-config`: Stop/PostToolUse matcher syntax with path filters

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Design doc | `~/.gstack/projects/MungoHarvey-Advanced-AI-Workflows/mharvey2-main-design-20260521-144453.md` | Markdown |
| Test plan | same dir, REG-1/2/3/7 | Markdown |
| AP permission schema | `Coding/advanced-planning/platforms/claude-code/settings.json` | JSON |
| Superpowers prefs | `Coding/planning-architectures/superpowers/.claude/skills/brainstorming/SKILL.md` | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Glue skill | `.claude/skills/gstack-to-plans/SKILL.md` | Markdown |
| Routing template | `references/claude-md-routing.md` | Markdown |
| Settings snippet | `references/settings-snippet.json` | JSON |

## Dependencies

### Must Complete Before
- Phase plan approved (done)

### Blocked By
- Nothing

### Parallelisable
- None — this is foundational

## Complexity
**Scope**: Medium
**Estimated effort**: 2–3 hours
**Key challenges**:
1. Getting the hook matcher scope tight enough to never spuriously fire
2. Resolving the two open questions (permission schema, superpowers preference syntax) by reading source

## Rationale
Bundling the three artifacts in one loop keeps the routing/hook/glue contract internally consistent — the glue references the routing instruction, the routing references the closing-instruction-as-fallback, the hook drives the same `/gstack-to-plans` command.

---
name: "ralph-loop-002"
task_name: "Setup-with-Claude Rewrite"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-002-1"
    content: "Write references/install-{gstack,advanced-planning,superpowers,plannotator}.md — one per sub-package, each containing canonical install command per platform (Windows/macOS/Linux) sourced from the upstream README/setup docs"
    skill: "NA"
    agent: "NA"
    outcome: "Four install-{tool}.md files exist under .claude/skills/setup-with-claude/references/; each contains commands verified against the sub-package's actual README, not invented"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-2"
    content: "Replace existing .claude/skills/setup-with-claude/SKILL.md with instructions-Claude-reads form covering the pipeline: detect → install missing → wire routing → grant permissions → install glue → write integrations.json → verify"
    skill: "skill-creator"
    agent: "NA"
    outcome: "SKILL.md is pure markdown; walks Claude through each pipeline step; no executable helpers; each destructive step gated by AskUserQuestion"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-3"
    content: "Specify the --uninstall flow in SKILL.md: remove fenced routing block, glue skill, integrations.json, permission additions; refuse on missing markers"
    skill: "skill-creator"
    agent: "NA"
    outcome: "SKILL.md contains a labelled '--uninstall' section; explicitly states that fenced-marker absence aborts with manual-recovery instructions; states sub-package installs are never touched"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-002-4"
    content: "Specify the --refresh flow in SKILL.md: re-detect each sub-package, update integrations.json, no install actions"
    skill: "skill-creator"
    agent: "NA"
    outcome: "SKILL.md contains a labelled '--refresh' section; explicitly limited to detection + integrations.json update"
    status: pending
    complexity: low
    priority: medium
  - id: "loop-002-5"
    content: "Copy or reference loop-001's claude-md-routing.md and settings-snippet.json into .claude/skills/setup-with-claude/references/ so the setup skill is self-contained"
    skill: "NA"
    agent: "NA"
    outcome: "References directory contains both files; SKILL.md reads from these relative paths, not from loop-001's original location"
    status: pending
    complexity: low
    priority: high
  - id: "loop-002-6"
    content: "Verify the rewritten setup skill by walking it through mentally with the four-tool flow as a fresh-project scenario; document any blocking gaps"
    skill: "verification-before-completion"
    agent: "NA"
    outcome: "Dry-run walkthrough recorded in working notes; zero blocking gaps remain or any gaps are explicitly added to handoff_summary.needed"
    status: pending
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Rewrite the existing `setup-with-claude` skill as instructions-Claude-reads (SKILL.md + references/), supporting --uninstall and --refresh, integrating the artifacts from loop-001.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-002"

  ## Success criteria
  - [ ] `.claude/skills/setup-with-claude/SKILL.md` is instructions-Claude-reads (no shell scripts, no `bin/`)
  - [ ] Walks Claude through: detect → install → wire routing (fenced) → grant permissions → install glue → write integrations.json → verify
  - [ ] `references/install-gstack.md`, `install-advanced-planning.md`, `install-superpowers.md`, `install-plannotator.md` each contain the canonical install command per platform
  - [ ] `--uninstall` removes only meta-project artifacts (routing block via fenced markers, glue skill, integrations.json, permission additions); never touches sub-package installs
  - [ ] `--uninstall` refuses to edit CLAUDE.md when fenced markers are missing — prints manual-recovery instructions instead
  - [ ] `--refresh` re-runs detection only

  ## Required skills
  - `skill-authoring`: Pure-markdown SKILL.md
  - `claude-code-config`: Reading and writing settings.json safely

  ## Inputs
  - Design doc section: "5. `setup-with-claude` — instructions Claude reads"
  - Loop-001 outputs: `references/claude-md-routing.md`, `references/settings-snippet.json`
  - Existing setup skill at `.claude/skills/setup-with-claude/` (replace, do not append)

  ## Expected outputs
  - `.claude/skills/setup-with-claude/SKILL.md`
  - `.claude/skills/setup-with-claude/references/install-{gstack,advanced-planning,superpowers,plannotator}.md`
  - `.claude/skills/setup-with-claude/references/claude-md-routing.md` (copy from loop-001 or reference)
  - `.claude/skills/setup-with-claude/references/settings-snippet.json` (copy from loop-001 or reference)

  ## Constraints
  - Instructions-Claude-reads, not a deterministic script
  - Detection logic must work cross-platform (Windows/macOS/Linux)
  - Never silent-overwrites CLAUDE.md; always fenced + AskUserQuestion on refresh

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-002 — setup-with-claude rewritten as instructions"
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
Rewrites the existing `setup-with-claude` skill into instructions-Claude-reads form, consuming the artifacts from loop-001 and shipping per-tool install references for each of the four sub-packages.

## Success Criteria
- ✓ SKILL.md walks the detection → install → wire → grant → install-glue → write-integrations → verify pipeline
- ✓ Four `references/install-{tool}.md` files exist with canonical commands per platform
- ✓ --uninstall preserves sub-packages; refuses on missing markers
- ✓ Settings.json edit uses AskUserQuestion before write

## Skills Required

### Broad (from phase plan):
- `skill-authoring`
- `claude-code-config`

### Specific (refined for this loop):
- `claude-code-config`: Safe settings.json read/edit/merge

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Design doc step 5 | `~/.gstack/projects/...design-...md` | Markdown |
| Routing template | loop-001 output `references/claude-md-routing.md` | Markdown |
| Settings snippet | loop-001 output `references/settings-snippet.json` | JSON |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Setup skill | `.claude/skills/setup-with-claude/SKILL.md` | Markdown |
| Install references | `.claude/skills/setup-with-claude/references/install-*.md` | Markdown |
| Embedded routing template | `.claude/skills/setup-with-claude/references/claude-md-routing.md` | Markdown |
| Embedded settings snippet | `.claude/skills/setup-with-claude/references/settings-snippet.json` | JSON |

## Dependencies

### Must Complete Before
- ralph-loop-001: needs the routing template and settings snippet

### Blocked By
- Nothing else

### Parallelisable
- ralph-loop-003 (doc rewrites): can run concurrently if writers are coordinated to avoid stepping on README/SETUP at the same time as setup-skill references

## Complexity
**Scope**: Medium
**Estimated effort**: 2–3 hours
**Key challenges**:
1. Capturing canonical install commands for four tools across three platforms without inventing flags
2. --uninstall safety: refusing on missing markers without leaving the user stuck

## Rationale
Setup is the entry point for external users; getting it right gates open-source adoption. Instructions-Claude-reads honours Tension 3 and works on the heterogeneous Windows/macOS/Linux environments external users will have.

---
name: "ralph-loop-003"
task_name: "Structural Doc Rewrites"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-003-1"
    content: "Rewrite README.md with Four-Tools framing, updated flow diagram (Mermaid) showing gstack → glue → advanced-planning → plannotator/superpowers, and explicit 'Claude Code only in v0.1' statement"
    skill: "markdown-mermaid-writing"
    agent: "NA"
    outcome: "README.md contains 'Four Tools' heading; Mermaid diagram renders gstack at top and glue layer; Claude-only-v0.1 statement appears in scope or intro section"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-2"
    content: "Rewrite ARCHITECTURE.md System Overview and Integration Boundaries sections; add 'Glue Layer' section; copy the four-tool boundary table from the design doc"
    skill: "markdown-mermaid-writing"
    agent: "NA"
    outcome: "ARCHITECTURE.md has 'Glue Layer' section; four-tool boundary table present verbatim; grep finds zero occurrences of 'plans/' (other than '.advanced-plans/') or 'PLANS-INDEX.md'"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-3"
    content: "Rewrite DESIGN-RATIONALE.md adding four subsections: 'gstack at the strategic layer', 'one glue skill is enough', 'instructions-not-scripts for setup', 'why no exploration-notes integration'"
    skill: "NA"
    agent: "NA"
    outcome: "DESIGN-RATIONALE.md contains all four labelled subsections; each cites the relevant locked decision from the design doc"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-4"
    content: "Rewrite SETUP.md with full four-sub-package install walkthrough, version compatibility matrix, exact .claude/settings.json permission entries, plannotator-is-automatic note, and documentation of the two critical gaps"
    skill: "NA"
    agent: "NA"
    outcome: "SETUP.md contains a version compatibility matrix; settings.json permission JSON block; explicit notes for both critical gaps (permission failure mode, plannotator ExitPlanMode popups)"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-5"
    content: "Rewrite ROADMAP.md marking v0.1 done; deferred list (gate-to-gstack-review, multi-runtime with concrete description of what changes, CI/fixtures, programmatic plannotator-detection refinement)"
    skill: "NA"
    agent: "NA"
    outcome: "ROADMAP.md shows v0.1 status as done; multi-runtime entry has at least a paragraph describing what changes for v0.2+; deferred list complete"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-003-6"
    content: "Run cross-doc consistency check: grep all five docs for legacy terms ('Three Tools', 'plans/' without '.advanced-plans/' prefix, 'PLANS-INDEX.md', 'OpenCode' in any current-state context) and remove every remaining occurrence"
    skill: "verification-before-completion"
    agent: "NA"
    outcome: "Grep across the five rewritten docs returns zero occurrences of legacy terms in current-state contexts (ROADMAP multi-runtime descriptions of future state excluded)"
    status: pending
    complexity: low
    priority: high

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Rewrite the five primary repo docs (README, ARCHITECTURE, DESIGN-RATIONALE, SETUP, ROADMAP) to reflect the four-tool framing — section rewrites, not additive diffs.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-003"

  ## Success criteria
  - [ ] README.md uses "Four Tools" framing; flow diagram shows gstack → glue → advanced-planning → plannotator/superpowers; explicit "Claude Code only in v0.1" statement
  - [ ] ARCHITECTURE.md has "Glue Layer" section + four-tool boundary table from design doc; zero references to `plans/` or `PLANS-INDEX.md`
  - [ ] DESIGN-RATIONALE.md adds: "gstack at the strategic layer", "one glue skill is enough", "instructions-not-scripts for setup", "why no exploration-notes integration"
  - [ ] SETUP.md: version compatibility matrix; exact `.claude/settings.json` permission entries; plannotator-is-automatic note; documents the two critical gaps (permission failure mode, plannotator ExitPlanMode popups)
  - [ ] ROADMAP.md: v0.1 marked done; deferred list (gate-to-gstack-review, multi-runtime with concrete description, CI/fixtures, programmatic plannotator-detection refinement)

  ## Required skills
  - `technical-writing`: Structural rewrites without legacy contradictions
  - `markdown-mermaid-writing`: Updated flow diagram

  ## Inputs
  - Design doc: Architecture diagram, Components, Handoff contracts table
  - CEO plan: `ceo-plans/2026-05-21-four-tool-integration.md` for positioning language
  - Existing repo docs (to be rewritten, not appended)

  ## Expected outputs
  - `README.md`, `ARCHITECTURE.md`, `DESIGN-RATIONALE.md`, `SETUP.md`, `ROADMAP.md` — all rewritten

  ## Constraints
  - Section rewrites, NOT additive diffs (Codex flagged contradictions in additive approach)
  - No aspirational multi-runtime framing — honest Claude-only positioning
  - All path references = `.advanced-plans/` (not `plans/` or `.claude/plans/`)

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-003 — five doc rewrites for four-tool framing"
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
Rewrites the repo's user-facing and contributor-facing docs to the four-tool framing. The eng review flagged that additive diffs leave contradictions; this loop addresses the docs structurally.

## Success Criteria
- ✓ Five docs rewritten; zero references to `plans/` or `PLANS-INDEX.md` in any of them
- ✓ Updated flow diagram in README + ARCHITECTURE
- ✓ Compatibility matrix in SETUP

## Skills Required

### Broad (from phase plan):
- `technical-writing`

### Specific (refined for this loop):
- `markdown-mermaid-writing`: Flow diagram updates

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Design doc | `~/.gstack/projects/...design-...md` | Markdown |
| CEO plan | `~/.gstack/projects/.../ceo-plans/2026-05-21-four-tool-integration.md` | Markdown |
| Legacy docs | `README.md`, `ARCHITECTURE.md`, `DESIGN-RATIONALE.md`, `SETUP.md`, `ROADMAP.md` (to be rewritten) | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Five rewritten docs | repo root | Markdown |

## Dependencies

### Must Complete Before
- ralph-loop-001 and ralph-loop-002: docs reference the install steps and artifacts produced there

### Blocked By
- Nothing else

### Parallelisable
- ralph-loop-004, ralph-loop-005: upstream PRs don't touch these files

## Complexity
**Scope**: Medium-High (5 doc rewrites, with cross-references)
**Estimated effort**: 3–4 hours
**Key challenges**:
1. Avoiding contradictions across the five docs as the framing changes
2. Being honest about Claude-only without underselling the design

## Rationale
Documentation is the user's first contact. The structural rewrites are the public artifact of the design's locked decisions, and they're the basis on which open-source adopters decide whether the project is worth their time.

---
name: "ralph-loop-004"
task_name: "Upstream PR — advanced-planning STRUCTURE.md"
max_iterations: 2
on_max_iterations: checkpoint

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-004-1"
    content: "Read current advanced-planning/STRUCTURE.md and enumerate every stale path occurrence (plans/, .claude/plans/, PLANS-INDEX.md) with line numbers"
    skill: "NA"
    agent: "Explore"
    outcome: "Working notes contain a complete table of stale-path occurrences with line numbers; ready to drive the rewrite"
    status: pending
    complexity: low
    priority: high
  - id: "loop-004-2"
    content: "Create a branch in the local advanced-planning checkout (or fork if upstream write access requires it) and rewrite STRUCTURE.md replacing every stale path with the v0.11.0 canonical equivalent"
    skill: "NA"
    agent: "NA"
    outcome: "Branch exists; STRUCTURE.md contains zero references to plans/, .claude/plans/, or PLANS-INDEX.md (only .advanced-plans/ and its sub-paths); diff scoped to STRUCTURE.md only"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-004-3"
    content: "Commit + push the branch; open a PR with a description referencing the meta-project's audit as discovery context and v0.11.0 commands/skills as ground truth"
    skill: "ship"
    agent: "NA"
    outcome: "PR opened; URL captured; description names the meta-project (Advanced-AI-Workflows) and cites at least two v0.11.0 command files showing the canonical paths"
    status: pending
    complexity: low
    priority: high
  - id: "loop-004-4"
    content: "Record the PR URL in handoff_summary.done for downstream loops to reference"
    skill: "NA"
    agent: "NA"
    outcome: "handoff_summary.done contains the PR URL"
    status: pending
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Open a PR against advanced-planning that updates STRUCTURE.md to reflect the v0.11.0 runtime layout (`.advanced-plans/`, not `plans/`/`.claude/plans/`/`PLANS-INDEX.md`).

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-004"

  ## Success criteria
  - [ ] Branch created on a fork or local clone of advanced-planning
  - [ ] STRUCTURE.md updated with v0.11.0 paths; commit message clear; rebased on main
  - [ ] PR opened (URL recorded in handoff_summary.done)
  - [ ] PR description references the meta-project as discovery context and the v0.11.0 commands/skills as ground truth

  ## Required skills
  - `upstream-contribution`: Minimal-surface PR with clear discovery context

  ## Inputs
  - Local advanced-planning checkout: `C:\Users\mharvey2\Documents\Coding\advanced-planning\`
  - Design doc Audit Findings section: lists the stale paths
  - Current STRUCTURE.md in that repo

  ## Expected outputs
  - Branch in advanced-planning fork/clone
  - PR URL recorded in handoff_summary

  ## Constraints
  - Documentation-only change in this PR; no behavioural touches
  - Do not push to upstream main directly; PR only

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-004 — advanced-planning STRUCTURE.md PR opened"
  2. Update handoff_summary with PR URL in `done`
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
First of two ecosystem-citizenship PRs. Pure docs fix in advanced-planning so other consumers of the package don't trip over the stale STRUCTURE.md the way the meta-project did during audit.

## Success Criteria
- ✓ PR opened (URL recorded)
- ✓ Diff scoped to STRUCTURE.md only
- ✓ PR description cites the meta-project's discovery context

## Skills Required

### Broad (from phase plan):
- `upstream-contribution`

### Specific (refined for this loop):
- None

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Stale STRUCTURE.md | `Coding/advanced-planning/STRUCTURE.md` | Markdown |
| Audit findings | design doc Audit Findings section | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| PR URL | recorded in handoff_summary.done | URL string |

## Dependencies

### Must Complete Before
- Nothing in this phase blocks this loop

### Blocked By
- Network access to GitHub; gh auth configured

### Parallelisable
- ralph-loop-005 (the other PR)

## Complexity
**Scope**: Low
**Estimated effort**: 30–45 minutes
**Key challenges**:
1. Identifying every stale-path occurrence in STRUCTURE.md
2. Framing the PR so the maintainer accepts it without context-switching

## Rationale
Pure docs PR, low merge risk. v0.1 release does not block on merge — the meta-project already treats v0.11.0 commands/skills as ground truth regardless of STRUCTURE.md.

---
name: "ralph-loop-005"
task_name: "Upstream PR — superpowers brainstorming default"
max_iterations: 2
on_max_iterations: checkpoint

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-005-1"
    content: "Read superpowers brainstorming SKILL.md (and writing-plans for symmetry); locate the exact lines that set the AP-detected default to .claude/plans/"
    skill: "NA"
    agent: "Explore"
    outcome: "Working notes cite line numbers for the AP-detected default and confirm the user-preference override branch is logically separate (will be preserved)"
    status: pending
    complexity: low
    priority: high
  - id: "loop-005-2"
    content: "Create a branch in the local superpowers checkout (or fork) and update the AP-detected default path from .claude/plans/ to .advanced-plans/specs/; leave user-preference override branch untouched"
    skill: "NA"
    agent: "NA"
    outcome: "Branch exists; diff modifies only the AP-detected default; user-preference override behaviour bit-for-bit preserved as verified by re-reading the modified file"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-005-3"
    content: "Commit + push the branch; open a PR with description explaining: (a) AP v0.11.0 moved off .claude/plans/, (b) meta-project's CLAUDE.md preference override is the v0.1 workaround, (c) PR makes that workaround redundant for AP-detected case"
    skill: "ship"
    agent: "NA"
    outcome: "PR opened; URL captured; description names the meta-project, cites the AP v0.11.0 path, and explains the workaround relationship"
    status: pending
    complexity: low
    priority: high
  - id: "loop-005-4"
    content: "Record the PR URL in handoff_summary.done"
    skill: "NA"
    agent: "NA"
    outcome: "handoff_summary.done contains the PR URL"
    status: pending
    complexity: low
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Open a PR against superpowers updating the brainstorming skill's stale default save path from `.claude/plans/` to `.advanced-plans/specs/` when advanced-planning is detected.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-005"

  ## Success criteria
  - [ ] Branch created on a fork or local clone of superpowers
  - [ ] brainstorming SKILL.md updated; only the AP-detected default changes — user-preference override behaviour preserved
  - [ ] PR opened (URL recorded)
  - [ ] PR description explains the rationale: AP v0.11.0 moved off `.claude/plans/`; default should follow

  ## Required skills
  - `upstream-contribution`

  ## Inputs
  - Local superpowers checkout: `C:\Users\mharvey2\Documents\Coding\planning-architectures\superpowers\`
  - Design doc Audit Findings → Superpowers section

  ## Expected outputs
  - Branch in superpowers fork/clone
  - PR URL recorded in handoff_summary

  ## Constraints
  - Behavioural change, but trivially correct
  - Do not weaken or remove the user-preference override behaviour
  - PR description must explain v0.1 workaround is preserved (CLAUDE.md preference override) so the PR is non-blocking for the meta-project

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-005 — superpowers brainstorming default-path PR opened"
  2. Update handoff_summary with PR URL in `done`
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
Second ecosystem-citizenship PR. Touches behaviour but trivially — the existing default is to write somewhere AP no longer reads. Even if the maintainer is conservative about behavioural changes, the PR's framing as a "fix to match AP v0.11.0" is hard to argue with.

## Success Criteria
- ✓ PR opened (URL recorded)
- ✓ User-preference override behaviour preserved (verified by re-reading skill text)
- ✓ Diff scoped to brainstorming SKILL.md (and possibly writing-plans if symmetry warrants)

## Skills Required

### Broad (from phase plan):
- `upstream-contribution`

### Specific (refined for this loop):
- None

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Stale brainstorming SKILL.md | `Coding/planning-architectures/superpowers/.claude/skills/brainstorming/SKILL.md` | Markdown |
| Audit findings | design doc Audit Findings → Superpowers | Markdown |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| PR URL | recorded in handoff_summary.done | URL string |

## Dependencies

### Must Complete Before
- Nothing in this phase blocks this loop

### Blocked By
- Network access to GitHub; gh auth configured

### Parallelisable
- ralph-loop-004 (the other PR)

## Complexity
**Scope**: Low
**Estimated effort**: 45–60 minutes
**Key challenges**:
1. Confirming the override pathway is untouched
2. Framing the PR so the behavioural change reads as a fix, not a feature

## Rationale
Behavioural correctness — superpowers' current default points at a path AP no longer uses. Fixing it makes the meta-project's CLAUDE.md preference override redundant for the AP-detected case, simplifying future maintenance.

---
name: "ralph-loop-006"
task_name: "End-to-End Smoke Test (REG-1..REG-7)"
max_iterations: 3
on_max_iterations: escalate

handoff_summary:
  done: ""
  failed: ""
  needed: ""

todos:
  - id: "loop-006-1"
    content: "Create a fresh test project directory outside the meta-repo (e.g. scratch/aaw-smoketest-{datetime}/) for REG-1; do not pollute the meta-repo's own state"
    skill: "NA"
    agent: "NA"
    outcome: "Fresh empty git repo exists at scratch path; no sub-package installs or .claude/ directory present yet"
    status: pending
    complexity: low
    priority: high
  - id: "loop-006-2"
    content: "Run REG-1 (E2E install + four-tool flow): /setup-with-claude → /office-hours → /gstack-to-plans → /plan-and-phase → /next-loop → /run-gate → /next-phase; capture artifact paths at each step"
    skill: "verify"
    agent: "NA"
    outcome: "Every step produces the documented artifact at the documented path; evidence (path + content excerpt) captured per step in working notes"
    status: pending
    complexity: high
    priority: high
  - id: "loop-006-3"
    content: "Run REG-2, REG-3, REG-4, REG-5, REG-6 follow-on checks against the smoke-test project; capture PASS/FAIL + evidence per REG"
    skill: "verify"
    agent: "NA"
    outcome: "Each of REG-2..REG-6 has a PASS/FAIL verdict with concrete evidence (file state, command output, AskUserQuestion firing confirmed) in working notes"
    status: pending
    complexity: high
    priority: high
  - id: "loop-006-4"
    content: "Run REG-7 (auto-trigger hook scope): write a file under ~/.gstack/projects/{slug}/ matching the design-doc pattern (hook should fire); write an unrelated file outside ~/.gstack/projects/ (hook should NOT fire); two writes in quick succession (one invocation, not two)"
    skill: "verify"
    agent: "NA"
    outcome: "REG-7 has PASS verdict on all four sub-cases (a,b,c,d) with concrete evidence — hook trace logs or observed /gstack-to-plans invocations"
    status: pending
    complexity: high
    priority: high
  - id: "loop-006-5"
    content: "Write tests/v0.1-smoke-report.md combining REG-1..REG-7 verdicts and evidence; commit to the meta-repo"
    skill: "NA"
    agent: "NA"
    outcome: "tests/v0.1-smoke-report.md exists in the meta-repo; contains a verdict table (REG # / status / evidence) and an overall pass/fail line; committed"
    status: pending
    complexity: medium
    priority: high
  - id: "loop-006-6"
    content: "On any FAIL: loop back to the affected build loop (001/002/003), fix the artifact, re-run the affected REG, and update the report"
    skill: "NA"
    agent: "NA"
    outcome: "Report shows all REGs PASS at the time of commit; any fix iterations documented in the report's history section"
    status: pending
    complexity: medium
    priority: medium

prompt: |
  ## Context from prior loop
  Done: [inject prior.handoff_summary.done]
  Failed: [inject prior.handoff_summary.failed]
  Needed: [inject prior.handoff_summary.needed]

  ## Objective
  Run the v0.1 end-to-end smoke test in a fresh project and produce a report covering REG-1 through REG-7.

  ## Git checkpoint (run first)
  git add -A && git commit -m "checkpoint: before ralph-loop-006"

  ## Success criteria
  - [ ] REG-1: Fresh-project install end-to-end — `/setup-with-claude` → `/office-hours` → `/gstack-to-plans` → `/plan-and-phase` → `/next-loop` → `/run-gate` → `/next-phase` works; artifacts land at the documented paths
  - [ ] REG-2: Re-run idempotency — second `/gstack-to-plans` with no intervening writes is a no-op
  - [ ] REG-3: Divergence detection — edit project-side archive, re-run, glue invokes AskUserQuestion
  - [ ] REG-4: CLAUDE.md merge safety — routing block appears once after two `/setup-with-claude` runs
  - [ ] REG-5: Clean uninstall — only meta-project artifacts removed
  - [ ] REG-6: Superpowers preference honoured — brainstorming writes to `.advanced-plans/specs/`
  - [ ] REG-7: Auto-trigger hook scope — fires on `~/.gstack/projects/` writes; does NOT fire on writes elsewhere; debounces double-writes
  - [ ] `tests/v0.1-smoke-report.md` written with PASS/FAIL + evidence per REG

  ## Required skills
  - `integration-testing`: Driving the four-tool flow manually and capturing evidence

  ## Inputs
  - Test plan: `~/.gstack/projects/MungoHarvey-Advanced-AI-Workflows/mharvey2-main-eng-review-test-plan-20260521-152241.md`
  - All artifacts produced by loops 001–003
  - Fresh test project (created during this loop or scratch directory)

  ## Expected outputs
  - `tests/v0.1-smoke-report.md`: PASS/FAIL + evidence per REG
  - Any bugs discovered → fixed in the affected loop's artifacts (loop back if needed)

  ## Constraints
  - Use a fresh project for REG-1 — do NOT smoke test against this repo's own state
  - Capture concrete evidence (path of file, content excerpt, command output) for each REG verdict
  - On any FAIL, fix the affected loop's artifact and re-run — do not paper over

  ## On completion
  1. git add -A && git commit -m "complete: ralph-loop-006 — v0.1 smoke test report (REG-1..REG-7)"
  2. Update handoff_summary
  3. Mark all todos completed

  Begin. Mark todos in_progress before starting each task. One in_progress at a time.
---

## Overview
Final loop. Validates the integration end-to-end on a fresh project, producing the v0.1-release readiness report. Any FAIL here means looping back to the affected loop and re-running this one.

## Success Criteria
- ✓ All seven REGs PASS with documented evidence
- ✓ Report file committed

## Skills Required

### Broad (from phase plan):
- `integration-testing`

### Specific (refined for this loop):
- None

### Discovered (new, identified during planning):
- None

## Inputs
| Input | Source | Format |
|-------|--------|--------|
| Test plan | `~/.gstack/projects/.../mharvey2-main-eng-review-test-plan-...md` | Markdown |
| All built artifacts | repo + `.claude/skills/` | Mixed |
| Fresh test project | created during loop | Directory |

## Outputs
| Output | Location | Format |
|--------|----------|--------|
| Smoke report | `tests/v0.1-smoke-report.md` | Markdown |

## Dependencies

### Must Complete Before
- ralph-loop-001 (artifacts), ralph-loop-002 (setup skill), ralph-loop-003 (docs for setup reference)

### Blocked By
- Nothing else

### Parallelisable
- None — runs last

## Complexity
**Scope**: Medium
**Estimated effort**: 2–3 hours
**Key challenges**:
1. REG-1 end-to-end requires actually running the four-tool flow against a fresh project
2. REG-7 requires writing a deliberate negative-path test for hook scope
3. FAIL recovery: discovering an issue here means looping back through 001/002/003 and re-testing
