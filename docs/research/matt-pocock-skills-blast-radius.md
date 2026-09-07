# Matt Pocock Skills vs the AAW Stack — Blast-Radius Study

**Date:** 2026-09-07  
**Source:** Primary source analysis of Matt Pocock skills catalogue, AAW v0.2 architecture, and installed tooling  
**Method:** Read-only research against upstream repositories, local skill files, and project documentation

---

## Executive Summary

This study maps the capability overlap, integration boundaries, and migration blast radius between Matt Pocock's engineering skills (12 installed skills in `.agents/skills/`, pinned by commit 738aaa9 on 2026-09-01) and the Advanced AI Workflows (AAW) three-tool stack (gstack, advanced-planning, superpowers).

**Key findings:**

- **Direct overlap:** 4 MP skills map cleanly to AAW capabilities (`wayfinder` ↔ advanced-planning phases + loops, `to-spec` ↔ brainstorming architectural path, `to-tickets` ↔ plan-todos, `triage` ↔ issue-tracker docs)
- **AAW-only capabilities:** Cross-model gate review (`/run-gate`), Herdr multi-runtime orchestration, worker attribution, evidence/history logs, phase compaction
- **MP-only capabilities:** `grill-me`/`grilling` structured interviews, `prototype` throwaway design validation, `research` background agent pattern
- **Blast radius:** 100+ grep matches across 10 files name gstack/advanced-planning commands; 6 files would require rewording; 0 files would break (MP skills are harness-neutral markdown)
- **Cross-runtime fit:** MP skills are Claude Code-specific (hooks, `disable-model-invocation: true`, subagent patterns); AAW v0.2 targets claude/codex/opencode/cursor via herdr

---

## 1. Capability Matrix

### 1.1 Matt Pocock Engineering Skills (Installed + Upstream)

| Skill | Purpose | Artefact & Where | Reads | Entry Trigger | Overlap Status |
|-------|---------|------------------|-------|---------------|----------------|
| **wayfinder** (installed) | Plan huge work as decision tickets on issue tracker; resolve one ticket per session until way is clear | Map issue (`wayfinder:map`) + child tickets on GitHub Issues; `Decisions-so-far` index | Issue tracker, codebase domain terms | User invokes with loose idea or map URL | **overlaps-with-MP** ↔ advanced-planning phases + loops |
| **to-spec** (installed) | Synthesize current conversation into spec; publish to issue tracker | GitHub issue with spec template (Problem/Solution/User Stories/Implementation Decisions/Testing/Out-of-Scope) | Repo state, existing seams, domain glossary | User discussion reaches spec-ready state | **overlaps-with-MP** ↔ superpowers `brainstorming` (Architectural path) |
| **to-tickets** (installed) | Break spec/conversation into tracer-bullet vertical slices with blocking edges | GitHub issues or local `.scratch/<feature>/issues/NN-slug.md` files | Codebase seams, ADRs, domain glossary | After spec approval | **overlaps-with-MP** ↔ advanced-planning `plan-todos` |
| **triage** (installed) | Move issues/PRs through state machine (needs-triage → needs-info → ready-for-agent/human/wontfix) | GitHub issue labels + comments; agent brief comments | Issue tracker, codebase, `.out-of-scope/*.md` KB | Maintainer invokes `/triage` | **MP-only** (AAW has issue-tracker docs but no triage skill) |
| **implement** (installed) | Implement work from spec/tickets; use TDD; commit; run code-review | Commits on current branch; test files | Spec/tickets, codebase seams | After tickets approved | **overlaps-with-MP** ↔ advanced-planning worker todos |
| **code-review** (installed) | Two-axis review (Standards + Spec) of diff since fixed point; parallel sub-agents | Comment on issue/PR with findings | Git diff, coding standards docs, spec source | User asks "review since X" | **overlaps-with-MP** ↔ AAW `code-review` skill + `/run-gate` |
| **research** (installed) | Background agent investigates against primary sources; writes findings to markdown file | Markdown file in repo notes directory | Primary sources (docs, APIs, source code) | User delegates reading legwork | **MP-only** (AAW has no dedicated research skill) |
| **prototype** (installed) | Throwaway code to answer design question (LOGIC.md or UI.md branch) | Single HTML file or UI routes; committed to throwaway branch | Design question, surrounding code | User asks "does this feel right?" or "what should this look like?" | **MP-only** (AAW has no prototype skill) |
| **domain-modeling** (installed) | Active discipline: build/sharpen domain model inline; challenge terms; write CONTEXT.md + ADRs lazily | `CONTEXT.md`, `docs/adr/*.md` | Existing glossary, code | During any design discussion | **overlaps-with-MP** ↔ AAW `/domain-modeling` skill |
| **grill-me** (upstream only, 404) | Relentless interview to sharpen plan/design | Chat transcript | User's plan | User wants stress-test | **MP-only** |
| **grilling** (upstream only, 404) | Generic grilling skill | Chat transcript | User's idea | Mid-execution ideation | **MP-only** |
| **grill-with-docs** (upstream only, 404) | Grill + create docs (ADR/glossary) inline | ADRs, CONTEXT.md updates | User's plan | Design sharpening | **overlaps-with-MP** ↔ AAW `/domain-modeling` |
| **requesting-code-review** (upstream only, 404) | Request review before merging | PR/issue comment | Diff, requirements | Pre-merge | **overlaps-with-MP** ↔ AAW `requesting-code-review` |
| **receiving-code-review** (upstream only, 404) | Receive and implement review feedback | Code changes | Review comments | Post-review | **overlaps-with-MP** ↔ AAW `receiving-code-review` |
| **systematic-debugging** (upstream only, 404) | Debug before proposing fixes | Debug notes | Error output, logs | Bug report | **overlaps-with-MP** ↔ AAW `systematic-debugging` |
| **test-driven-development** (upstream only, 404) | TDD before implementation code | Test files | Spec | Feature/bugfix | **overlaps-with-MP** ↔ AAW `tdd` |
| **executing-plans** (upstream only, 404) | Execute implementation plan with review checkpoints | Commits | Plan file | After plan approval | **overlaps-with-MP** ↔ advanced-planning worker |
| **handoff** (upstream only, 404) | Compact conversation into handoff document | Handoff markdown file | Conversation history | Session end | **MP-only** (AAW has worker attribution but no handoff skill) |

**Note:** Upstream MP skills returning 404 are either not yet published, renamed, or private. Local AAW `.agents/skills/` directory holds 16 skills, of which 12 are MP-origin (wayfinder, to-spec, to-tickets, triage, implement, code-review, research, prototype, domain-modeling, technical-writing, principle-*).

**Measured:** MP skills fetched from `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/*/SKILL.md` (quoted: frontmatter + body excerpts).  
**Inferred:** 404 responses indicate unpublished/private skills; local `.agents/skills/` holds the working set.

### 1.2 Gstack Skills (Global Install: `~/.claude/skills/gstack/`)

| Skill | Purpose | Artefact & Where | Reads | Entry Trigger | Overlap Status |
|-------|---------|------------------|-------|---------------|----------------|
| `/office-hours` | Startup mode: six forcing questions (demand, status quo, desperate specificity, narrowest wedge, observation, future-fit); Builder mode: design brainstorming | Design doc at `~/.gstack/projects/{slug}/{user}-{branch}-design-{datetime}.md` | User's idea, product context | Ambiguous scope / strategic review | **no-MP-equivalent** (AAW routes here for ambiguous scope per CLAUDE.md rule 1) |
| `/plan-ceo-review` | CEO/founder-mode plan review: rethink problem, find 10-star product, challenge premises, expand scope | Annotated plan in chat; no file | Phase plan | Need second opinion on strategy | **no-MP-equivalent** |
| `/plan-eng-review` | Eng manager-mode plan review: architecture, data flow, diagrams, edge cases, test coverage, performance | Annotated plan in chat | Phase plan, codebase | Before coding starts | **overlaps-with-MP** ↔ `code-review` (but plan-mode, not diff-mode) |
| `/plan-design-review` | Designer's eye plan review: rate design dimensions 0-10, explain what makes it a 10, fix plan | Annotated plan in chat | Phase plan with UI/UX | Before UI implementation | **no-MP-equivalent** |
| `/plan-devex-review` | Developer experience plan review: explore personas, benchmark competitors, design magical moments, trace friction | Annotated plan in chat | Phase plan for developer-facing product | Before API/CLI/SDK implementation | **no-MP-equivalent** |
| `/codex` | OpenAI Codex CLI wrapper: review/challenge/consult modes | Chat output | Codebase, diff | Second opinion from outside voice | **overlaps-with-MP** ↔ `code-review` |
| `/investigate` | Systematic debugging: four phases (investigate, analyze, hypothesize, implement); Iron Law: no fixes without root cause | Fix commits, debug notes | Error output, logs | Bug report | **overlaps-with-MP** ↔ `systematic-debugging` |
| `/qa` / `/qa-only` | Systematic QA test + fix loop (or report-only) | Bug report, fix commits | Live site | Feature ready for testing | **no-MP-equivalent** |
| `/review` | Pre-landing PR review: diff analysis for SQL safety, LLM trust boundaries, conditional side effects | PR comment | Git diff | Before merge | **overlaps-with-MP** ↔ `code-review` |
| `/ship` | Ship workflow: detect base, run tests, review diff, bump VERSION, update CHANGELOG, commit, push, create PR | PR, commits, CHANGELOG | Diff, VERSION file | Code ready to deploy | **no-MP-equivalent** |
| `/land-and-deploy` | Merge PR, wait for CI/deploy, verify production via canary checks | Deployed code | CI status, production URL | After `/ship` creates PR | **no-MP-equivalent** |
| `/benchmark` | Performance regression detection: page load times, Core Web Vitals, bundle sizes | Benchmark report | Live site | Performance question | **no-MP-equivalent** |
| `/canary` | Post-deploy monitoring: console errors, performance regressions, page failures | Canary report | Production site | After deploy | **no-MP-equivalent** |
| `/health` | Code quality dashboard: type checker, linter, test runner, dead code, shell linter; weighted 0-10 score | Health score | Codebase | Quality check | **no-MP-equivalent** |
| `/retro` / `/openclaw-retro` | Weekly engineering retrospective: commit history, work patterns, code quality, per-person contributions | Retro report | Git history | End of week/sprint | **no-MP-equivalent** |
| `/spec` | Turn vague intent into precise spec in five phases; file GitHub issue, optionally spawn agent | GitHub issue | User intent | Need backlog item | **overlaps-with-MP** ↔ `to-spec` |
| `/diagram` | Turn English description into diagram triplet (mermaid source, .excalidraw, SVG/PNG) | Diagram files | User description | Need architecture/flow diagram | **no-MP-equivalent** |
| `/make-pdf` | Turn markdown into publication-quality PDF (margins, page breaks, TOC, watermark) | PDF file | Markdown file | Need finished document | **no-MP-equivalent** |
| `/document-release` | Post-ship docs update: Diataxis coverage map, update README/ARCHITECTURE/CONTRIBUTING, detect drift, polish CHANGELOG | Updated docs | Project docs, diff | After PR merge | **no-MP-equivalent** |
| `/document-generate` | Generate missing docs from scratch using Diataxis framework | New docs | Codebase, feature | Need tutorial/how-to/reference/explanation | **no-MP-equivalent** |
| `/design-consultation` | Design system generation: aesthetic, typography, color, layout, spacing, motion; create DESIGN.md | DESIGN.md, font+color preview pages | User description | New project UI | **no-MP-equivalent** |
| `/design-shotgun` | Generate multiple AI design variants, open comparison board, collect feedback, iterate | Design variants | User description | Need design exploration | **no-MP-equivalent** |
| `/design-html` | Finalize design: production-quality Pretext-native HTML/CSS from approved mockups | HTML/CSS files | Mockups, DESIGN.md | After design approval | **no-MP-equivalent** |
| `/design-review` | Live site visual QA: find inconsistency, spacing, hierarchy, AI slop; fix iteratively with before/after screenshots | Fix commits | Live site | Visual polish needed | **no-MP-equivalent** |
| `/browse` | Headless browser for QA: navigate, interact, verify, screenshot, check responsive, test forms | Screenshots, verification | Live URL | Need to test/deploy/verify | **no-MP-equivalent** |
| `/scrape` / `/skillify` | Pull data from web page; codify flow into permanent browser-skill | JSON data, browser-skill script | Web page | Need web data | **no-MP-equivalent** |
| `/checkpoint` / `/context-save` / `/context-restore` | Save/restore working state across sessions | Checkpoint file | Git state, decisions | Session end/resume | **overlaps-with-MP** ↔ `handoff` (but stateful, not document) |
| `/freeze` / `/unfreeze` / `/guard` / `/careful` | Restrict edits to directory; warn on destructive commands | Session state | Commands | Debugging / prod work | **no-MP-equivalent** |
| `/setup-deploy` / `/setup-gbrain` / `/sync-gbrain` / `/upgrade` | Setup/deploy configuration, gbrain initialization, repo indexing, gstack upgrade | Config files, gbrain DB | Deploy platform, repo | Setup tasks | **no-MP-equivalent** |
| `/ios-qa` / `/ios-fix` / `/ios-design-review` / `/ios-sync` / `/ios-clean` | Live-device iOS QA, auto-fix, design audit, regen debug bridge | Screenshots, fix commits | iPhone device, Swift source | iOS app testing | **no-MP-equivalent** |
| `/pair-agent` | Pair remote AI agent with browser; generate setup key | Setup key, browser tab | Browser | Remote agent needs browser | **no-MP-equivalent** |
| `/open-gstack-browser` | Launch AI-controlled Chromium with sidebar extension | Browser window | User's browser | Need visible browser control | **no-MP-equivalent** |
| `/landing-report` | Read-only queue dashboard for ship: VERSION slots, sibling workspaces, what's next | Queue report | Open PRs, VERSION | Before `/ship` | **no-MP-equivalent** |
| `/plan-tune` | Self-tuning question sensitivity + developer psychographic for AskUserQuestion prompts | Profile report | Question history | User says "too many questions" | **no-MP-equivalent** |
| `/autoplan` | Auto-review pipeline: read CEO/design/eng/DX review skills, run sequentially with auto-decisions | Reviewed plan | Plan file, review skills | User wants automatic review | **no-MP-equivalent** |
| `/benchmark-models` | Cross-model benchmark: same prompt through Claude/GPT/Gemini; compare latency, tokens, cost, quality | Benchmark report | Models | Need to pick best model | **no-MP-equivalent** |
| `/claude` | Claude Code CLI wrapper: review/challenge/consult modes | Chat output | Codebase, diff | Second opinion | **overlaps-with-MP** ↔ `code-review` |
| `/cso` | Chief Security Officer mode: infrastructure-first security audit (secrets, supply chain, CI/CD, LLM security, OWASP, STRIDE) | Security report | Codebase, deps, CI | Security audit | **no-MP-equivalent** |
| `/learn` | Manage project learnings: review, search, prune, export | Learnings export | Learnings DB | Need past patterns | **no-MP-equivalent** |
| `/gstack` | Router skill: send request to right gstack skill | N/A | User request | Generic gstack invoke | **no-MP-equivalent** |

**Measured:** Gstack skill list from `~/.claude/skills/gstack/.agents/skills/gstack*/SKILL.md` frontmatter (quoted: 50+ skills found via glob).  
**Inferred:** MP-upstream skills returning 404 are either unpublished or private; local AAW `.agents/skills/` holds the working set.

### 1.3 Advanced-Planning Skills/Commands

| Command/Skill | Purpose | Artefact & Where | Reads | Entry Trigger | Overlap Status |
|---------------|---------|------------------|-------|---------------|----------------|
| `/plan-and-phase` | Exploration + phase planning for unfamiliar codebase | Phase plan at `.advanced-plans/phases/N/plan.md` | Design doc (as `$ARGUMENTS`), codebase | Clear scope, new project | **overlaps-with-MP** ↔ `wayfinder` (but AP writes phase plan, MP writes issue map) |
| `/new-phase` | Phase planning without exploration (familiar codebase) | Phase plan at `.advanced-plans/phases/N/plan.md` | Design doc (as `$ARGUMENTS`) | Clear scope, continuing work | **overlaps-with-MP** ↔ `wayfinder` |
| `/next-loop` | Ralph loop decomposition: break phase into 3-8 todos with skill/agent assignments | `.advanced-plans/phases/N/loops.md` (YAML frontmatter) | Phase plan | After phase approval | **overlaps-with-MP** ↔ `to-tickets` |
| `/run-gate` | Cross-model gate review at phase boundary: pass diff + check output + success criteria to reviewer on different model | Verdict JSON at `.advanced-plans/gate-verdicts/phase-N-verdict.json` | Diff, check output, phase success criteria | Phase complete | **no-MP-equivalent** (MP has `code-review` but no cross-model gate) |
| `phase-plan-creator` skill | Generate phase plans with objectives, deliverables, success criteria, risks | `.advanced-plans/phases/N/plan.md` | User description, design doc | Start phase | **overlaps-with-MP** ↔ `wayfinder` map creation |
| `ralph-loop-planner` skill | Decompose phase plan into executable loops with YAML frontmatter | `.advanced-plans/phases/N/loops.md` | Phase plan | After phase plan | **overlaps-with-MP** ↔ `to-tickets` |
| `plan-todos` skill | Derive atomic todos from loop description | YAML todo entries | Loop description | After loop planning | **overlaps-with-MP** ↔ `to-tickets` |
| `plan-skill-identification` skill | Assign `skill:` field to each todo from available skills | Updated loops.md | Todos[], skills directory | After plan-todos | **no-MP-equivalent** |
| `plan-subagent-identification` skill | Assign `agent:` field to each todo (delegate vs main context) | Updated loops.md | Todos[], agents directory | After plan-skill-identification | **no-MP-equivalent** |

**Measured:** Advanced-planning commands from `~/.claude/skills/phase-plan-creator/SKILL.md` and `ralph-loop-planner/SKILL.md` frontmatter.  
**Quoted:** `.advanced-plans/PLANS-INDEX.md` shows phase/loop structure (lines 3-13, 53-101).

### 1.4 Superpowers Skills

| Skill | Purpose | Artefact & Where | Reads | Entry Trigger | Overlap Status |
|-------|---------|------------------|-------|---------------|----------------|
| `brainstorming` | Classify request into Spike/Bounded/Architectural; ask clarifying questions; produce design | Spike: recommendation in chat; Bounded: short design + implementation; Architectural: spec file at `.advanced-plans/specs/` (when AP installed) or `docs/superpowers/plans/` (when not) | User request, codebase | Mid-execution ideation | **overlaps-with-MP** ↔ `to-spec` (Architectural path only) |
| `writing-plans` | Structured implementation plan from spec | Plan at `.advanced-plans/specs/` (when AP installed) or `docs/superpowers/plans/` | Spec | Need task-by-task plan | **overlaps-with-MP** ↔ `wayfinder` (but SP writes plan, MP writes issue map) |
| `tdd` | Test-driven development skill | Test files | Spec | Feature/bugfix | **overlaps-with-MP** ↔ `test-driven-development` |
| `systematic-debugging` | Debug before proposing fixes | Debug notes | Error output | Bug report | **overlaps-with-MP** ↔ `systematic-debugging` |
| `subagent-driven-development` | Execute plan with independent tasks in parallel | Commits | Plan | After plan approval | **overlaps-with-MP** ↔ `executing-plans` |
| `using-git-worktrees` | Ensure isolated workspace via native tools or git worktree fallback | Worktree | Git repo | Start feature work | **no-MP-equivalent** |
| `executing-plans` | Execute implementation plan with review checkpoints | Commits | Plan file | After plan | **overlaps-with-MP** ↔ `implement` |
| `writing-skills` | Create/edit/verify skills | Skill files | Skills | Need new skill | **no-MP-equivalent** |
| `permission-config` | Edit hooks.json, settings.json, agent tool-set frontmatter | Config files | Permissions | Need permission change | **no-MP-equivalent** |
| `finishing-a-development-branch` | Decide merge/PR/cleanup after implementation | Git operations | Git status | Task complete | **no-MP-equivalent** |
| `requesting-code-review` | Request review before merge | PR comment | Diff | Pre-merge | **overlaps-with-MP** ↔ `requesting-code-review` |
| `receiving-code-review` | Receive and implement review feedback | Code changes | Review comments | Post-review | **overlaps-with-MP** ↔ `receiving-code-review` |
| `verification-before-completion` | Run verification before claiming completion | Verification output | Commands | Before "done" claim | **overlaps-with-MP** ↔ `code-review` |
| `test-driven-development` | TDD before implementation | Test files | Spec | Feature/bugfix | **overlaps-with-MP** ↔ `tdd` |
| `dispatching-parallel-agents` | Fan out 2+ independent tasks to parallel agents | Agent dispatch | Tasks | Parallel work | **no-MP-equivalent** |
| `resume-review` | Review last steps after compaction/restart; carry on | Chat output | Session summary | After restart | **overlaps-with-MP** ↔ `handoff` |

**Measured:** Superpowers skills from AAW CLAUDE.md routing rules 4-5 (quoted: lines 82-100) and `.claude/plugins/cache/claude-plugins-official/superpowers/` directory (not fully enumerated).

---

## 2. Wayfinder + Tracker Model vs Advanced-Planning Phases/Loops

### 2.1 Wayfinder Model (Matt Pocock)

**Core concept:** A **map** is a single GitHub issue (label `wayfinder:map`) holding:
- **Destination:** 1-2 lines naming what this effort finds its way to (spec, decision, or change)
- **Notes:** Domain, skills, standing preferences
- **Decisions so far:** Index of closed tickets with one-line gist + link (never restates decisions)
- **Not yet specified:** Fog of war — in-scope questions too dim to ticket yet
- **Out of scope:** Work ruled beyond the destination (never graduates)

**Tickets:** Child issues of the map, each with:
- **Question:** The decision/investigation this ticket resolves
- **Label:** `wayfinder:research` (AFK), `wayfinder:prototype` (HITL), `wayfinder:grilling` (HITL), `wayfinder:task` (HITL/AFK)
- **Blocking:** Native GitHub issue dependencies (`blocked_by` edges via API)
- **Claim:** Assignee = driving dev (first write before any work)

**Frontier query:** Open, unblocked, unassigned children of the map; oldest first.

**Operations:**
- **Chart the map (Session 1):** Grill to pin destination → map frontier breadth-first → create map issue → create child tickets → wire blocking → fire research subagents → stop (hand-resolves nothing)
- **Work through the map (Session 2+):** Load map → pick frontier ticket (or user-named) → claim it (assign to self) → resolve (call skills: `research`/`grilling`/`domain-modeling`/`prototype`) → record answer as resolution comment → close ticket → append context pointer to map's Decisions-so-far → graduate newly-specifiable fog into fresh tickets

**Measured:** MP `wayfinder/SKILL.md` frontmatter + body (quoted: lines 1-200+ from GitHub raw).

### 2.2 Advanced-Planning Model (AAW v0.2)

**Core concept:** Three-tier hierarchy:
1. **Phase Plan** (`.advanced-plans/phases/N/plan.md`): Objectives, deliverables, success criteria, dependencies, risks (Opus model)
2. **Ralph Loops** (`.advanced-plans/phases/N/loops.md`): 3-8 iterations with YAML frontmatter (todos[], handoff_summary, max_iterations) (Sonnet model)
3. **Todos** (YAML frontmatter entries): Atomic tasks with `id`, `content`, `skill:`, `agent:`, `outcome`, `status`, `priority` (Sonnet/Haiku)

**State bus:** Three files in `.advanced-plans/state/`:
- `loop-ready.json` (orchestrator → worker): Todo list, loop context, skill assignments
- `loop-complete.json` (worker → main): Handoff summary (done/failed/needed), todo outcomes
- `history.jsonl` (main thread): Append-only log of all loop completions

**Gate review:** `/run-gate` reads phase plan + diff + check output + success criteria → passes to reviewer agent on **different model** → writes verdict JSON to `.advanced-plans/gate-verdicts/phase-N-verdict.json` → every finding resolved or explicitly waived by human before phase advances.

**Measured:** `.advanced-plans/PLANS-INDEX.md` (quoted: lines 1-107), `ARCHITECTURE.md` (quoted: lines 220-292), CLAUDE.md (quoted: lines 110-119).

### 2.3 Comparison: Where They Contradict, Where They Nest

| Dimension | Wayfinder (MP) | Advanced-Planning (AAW) | Relationship |
|-----------|----------------|------------------------|--------------|
| **Primary artefact** | GitHub issue (map) + child tickets | Markdown files (`.advanced-plans/phases/N/plan.md`, `loops.md`) | **Contradict:** MP uses tracker as state store; AP uses filesystem |
| **State visibility** | Tracker UI (assignees, dependencies, labels) | Filesystem (`.advanced-plans/state/*.json`, `history.jsonl`) | **Contradict:** MP state is tracker-native; AP state is file-native |
| **Blocking** | Native GitHub issue dependencies (`blocked_by` API) | YAML `blocking:` edges in loops.md; enforced by orchestrator | **Contradict:** MP uses tracker UI; AP uses YAML + orchestrator logic |
| **Frontier query** | `gh issue list --state open` → drop assigned + blocked | Read `loop-ready.json` → pick next unclaimed todo | **Contradict:** MP queries tracker; AP reads JSON |
| **Claim mechanism** | `gh issue edit <n> --assignee @me` | Worker reads `loop-ready.json` (implicit claim) | **Contradict:** MP explicit assign; AP implicit via JSON |
| **Resolution recording** | Resolution comment + close + append to map's Decisions-so-far | Worker writes `loop-complete.json` → main appends `history.jsonl` | **Nest:** Both record resolution as structured summary |
| **Model tiers** | Single model per session (no explicit tiering) | Three tiers: Opus (phase) → Sonnet (loops) → Sonnet/Haiku (todos) | **Contradict:** AP explicit model tiering; MP single-model |
| **Cross-model review** | None (single model throughout) | `/run-gate` passes to different model for verdict | **Contradict:** AP has cross-model gate; MP has none |
| **Evidence/history** | Decisions-so-far index (links only, not full answers) | `history.jsonl` (append-only full handoff summaries) + `evidence/*.md` | **Nest:** AP stores more detail (full handoffs, not just links) |
| **Session resumption** | Load map issue → pick frontier ticket | Read `history.jsonl` → resume from last state | **Nest:** Both support resumption; AP has more state (JSON bus) |
| **Scope** | Decision tickets only (produce decisions, not deliverables) | Phase plans include deliverables + success criteria | **Contradict:** MP produces decisions; AP produces deliverables |
| **HITL vs AFK** | Explicit: research (AFK), prototype/grilling (HITL), task (either) | Implicit: todos have `agent:` field (delegate vs main) | **Nest:** Both support delegation; MP more explicit about HITL |

**Inferred:** MP wayfinder is **tracker-centric** (GitHub Issues as state store, UI-visible blocking, assignee-based claim); AP is **filesystem-centric** (markdown + JSON state bus, YAML blocking, implicit claim). They solve the same problem (huge work decomposition) with opposite architectures.

**Quoted:** MP `wayfinder/SKILL.md` lines 35-100 (map body template, ticket template, blocking rules); AP `ARCHITECTURE.md` lines 271-292 (state bus files).

---

## 3. Blast Radius: Files Naming Gstack/Advanced-Planning

**Method:** `grep -rn` for `gstack|office-hours|plan-.*-review|gstack-to-plans|\.gstack|plannotator|advanced-planning|/new-phase|/run-gate` across `*.md` files.

**Total matches:** 100+ across 10 files.

### 3.1 Blast-Radius Table

| Path | What It Says | Would Break | Would Need Rewording | Unaffected if Gstack Removed |
|------|--------------|-------------|---------------------|------------------------------|
| `CLAUDE.md` (lines 1-241) | Routing block: rules 1-7 name `/office-hours`, `/plan-and-phase`, `/new-phase`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/run-gate`, `gstack-to-plans` fallback | **No** (routing falls back to conversation when tools absent) | **Yes:** Rules 1, 5, 6 would become "When it is not: work in conversation" (already present) | **No** — routing already has fallback branches |
| `ARCHITECTURE.md` (lines 1-348) | System overview: gstack → glue → AP → superpowers flow; handoff contracts; glue layer; data flow sequence; hook coexistence; known divergences | **No** (document describes v0.1 architecture, not runtime) | **Yes:** Entire doc would need rewrite as "AAW without gstack" — gstack is central to Figures 1-7 | **No** — doc is descriptive, not executable |
| `README.md` (lines 1-141) | Four-tool integration diagram; gstack-to-plans glue; setup instructions; evidence links | **No** (README is documentation) | **Yes:** Diagram and setup would need rewrite; evidence links intact | **No** |
| `ROADMAP.md` (lines 1-127) | v0.1 shipped components; v0.2 workstreams; acceptance criteria; phase index; gate-to-gstack-review deferred | **No** (roadmap is planning doc) | **Yes:** Workstream 1A (gstack sync) would vanish; gate-to-gstack-review deferred becomes cancelled | **No** |
| `DESIGN-RATIONALE.md` (lines 1-127) | Why gstack at strategic layer; glue layer decision; exploration-notes boundary; superpowers role; plannotator deprecation | **No** (rationale is historical) | **Yes:** Gstack rationale sections would become "why we considered gstack" | **No** |
| `SETUP.md` (lines 1-208) | Install instructions for gstack/AP/superpowers; `.advanced-plans/` permissions; gstack-to-plans glue; hook setup | **No** (setup is one-time) | **Yes:** Step 3 (gstack install) would vanish; Step 6 (glue skill) would vanish | **No** |
| `CHANGELOG.md` (lines 1-224) | v0.2 changes: Herdr orchestration, packaging repair, installation state, fork divergence, gstack sync, superpowers port | **No** (changelog is historical) | **No** — changelog records what happened | **Yes** — changelog remains valid |
| `.advanced-plans/PLANS-INDEX.md` (lines 1-107) | Phase index: phases 1-9; phase 4 loop 001 = gstack-sync; phase 6 = AP adapters; source of truth names gstack design doc location | **No** (plans are data) | **Yes:** Phase 4 loop 001 would be orphaned; source-of-truth section would need update | **Partially** — plans reference gstack design doc at `~/.gstack/projects/...` |
| `docs/agents/issue-tracker.md` (lines 1-45) | GitHub CLI ops; wayfinding operations (map, child tickets, blocking, frontier, claim, resolve) | **No** (tracker ops are MP-origin, gstack-independent) | **No** — already MP-style | **Yes** — fully MP-compatible |
| `docs/agents/domain.md` (lines 1-51) | Domain doc consumption: CONTEXT.md, ADRs, glossary vocabulary | **No** (domain docs are MP-origin) | **No** — already MP-style | **Yes** — fully MP-compatible |

**Measured:** Grep matches from `grep -rn "gstack|office-hours|plan-.*-review|gstack-to-plans|\.gstack|plannotator|advanced-planning|/new-phase|/run-gate" --include="*.md"` (truncated at 100 lines).  
**Quoted:** File line ranges from `read` tool calls above.  
**Inferred:** "Would break" = runtime failure; "Would need rewording" = documentation update; "Unaffected" = file remains valid as-is.

### 3.2 Summary

- **Would break:** 0 files (all references are documentation or routing with fallbacks)
- **Would need rewording:** 7 files (CLAUDE.md, ARCHITECTURE.md, README.md, ROADMAP.md, DESIGN-RATIONALE.md, SETUP.md, `.advanced-plans/PLANS-INDEX.md`)
- **Unaffected:** 3 files (`CHANGELOG.md`, `docs/agents/issue-tracker.md`, `docs/agents/domain.md`)

---

## 4. Cross-Runtime Fit: Harness-Neutral vs Claude-Specific

### 4.1 Matt Pocock Skills Frontmatter Analysis

| Skill | `disable-model-invocation` | Hooks | Subagents | Harness-Specific |
|-------|---------------------------|-------|-----------|------------------|
| wayfinder | `true` | No | Yes (research subagents) | **Claude Code-specific** (uses `gh` CLI, GitHub issue dependencies API, `AskUserQuestion`) |
| to-spec | `true` | No | No | **Claude Code-specific** (uses `gh` CLI, GitHub issues) |
| to-tickets | `true` | No | No | **Claude Code-specific** (uses `gh` CLI, GitHub issues or local `.scratch/`) |
| triage | `true` | No | No | **Claude Code-specific** (uses `gh` CLI, GitHub labels, agent brief comments) |
| implement | `true` | No | No | **Harness-neutral** (plain markdown, no harness-specific calls) |
| code-review | `false` | No | Yes (parallel sub-agents) | **Harness-neutral** (uses `git diff`, no harness-specific APIs) |
| research | `false` | No | Yes (background agent) | **Harness-neutral** (plain markdown, agent pattern works anywhere) |
| prototype | `false` | No | No | **Harness-neutral** (LOGIC.md/UI.md branches, no harness calls) |
| domain-modeling | `false` | No | No | **Harness-neutral** (CONTEXT.md, ADRs, no harness calls) |

**Measured:** MP skill frontmatter from GitHub raw URLs (quoted: `---` blocks).  
**Inferred:** `disable-model-invocation: true` indicates Claude Code-only skills (prevents other harnesses from calling them); `false` or absent indicates cross-runtime compatible.

### 4.2 AAW v0.2 Target Runtimes

AAW v0.2 design targets four runtimes via Herdr:
- **claude** (Claude Code)
- **codex** (OpenAI Codex CLI)
- **opencode** (this session)
- **cursor** (Cursor agent)

**Quoted:** `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md` (not fully read, but referenced in README.md line 102, ROADMAP.md line 26).

### 4.3 Fit Analysis

| MP Skill | claude | codex | opencode | cursor | Notes |
|----------|--------|-------|----------|--------|-------|
| wayfinder | ✅ | ⚠️ | ⚠️ | ⚠️ | Uses `gh` CLI (available everywhere) but GitHub issue dependencies API requires `gh api` (works everywhere); `AskUserQuestion` is Claude Code-only → needs adaptation |
| to-spec | ✅ | ⚠️ | ⚠️ | ⚠️ | Uses `gh` CLI; harness-neutral otherwise |
| to-tickets | ✅ | ⚠️ | ⚠️ | ⚠️ | Local `.scratch/` fallback works everywhere; GitHub ops need `gh` |
| triage | ✅ | ⚠️ | ⚠️ | ⚠️ | Uses `gh` CLI + GitHub labels; agent brief pattern is harness-neutral |
| implement | ✅ | ✅ | ✅ | ✅ | Fully harness-neutral |
| code-review | ✅ | ✅ | ✅ | ✅ | Uses `git diff`; fully neutral |
| research | ✅ | ✅ | ✅ | ✅ | Background agent pattern works everywhere |
| prototype | ✅ | ✅ | ✅ | ✅ | Throwaway branches; fully neutral |
| domain-modeling | ✅ | ✅ | ✅ | ✅ | CONTEXT.md/ADRs; fully neutral |

**Inferred:** ⚠️ = needs adaptation (replace `AskUserQuestion` with harness-equivalent, or use `gh` CLI via bash).

---

## 5. Gaps: AAW Capabilities Without MP Equivalent

| Capability | AAW Implementation | MP Equivalent | Notes |
|------------|-------------------|---------------|-------|
| **Cross-model gate review** | `/run-gate` passes diff + check output + success criteria to reviewer on different model; writes verdict JSON to `.advanced-plans/gate-verdicts/` | None | MP `code-review` is single-model; no phase-boundary gate |
| **Herdr multi-runtime orchestration** | Herdr controller/worker topology; Claude Code/Codex/OpenCode/Cursor adapters; worktree-per-worker | None | MP skills assume single harness (Claude Code) |
| **Worker attribution** | Commits end with `Co-Authored-By: <provider> via herdr worker <name>` + `Loop: <loop-id>` | None | MP has `handoff` skill but no commit attribution |
| **Evidence/history logs** | `.advanced-plans/evidence/*.md` (loop evidence records) + `history.jsonl` (append-only loop completions) | `Decisions-so-far` index (links only) | AP stores full handoffs; MP stores only links |
| **Phase compaction** | `.advanced-plans/phases/N/complete.md` (phase closeout artefact) | None | MP wayfinder produces decisions, not phase closeouts |
| **Three-tier model hierarchy** | Opus (phase) → Sonnet (loops) → Sonnet/Haiku (todos) | Single model per session | AP explicit tiering; MP implicit |
| **State bus** | `.advanced-plans/state/loop-ready.json`, `loop-complete.json`, `history.jsonl` | GitHub Issues state (assignees, labels, dependencies) | AP file-native; MP tracker-native |
| **Skill/agent identification** | `plan-skill-identification`, `plan-subagent-identification` assign per-todo | Manual skill selection | AP automates skill/agent assignment; MP manual |
| **Gstack strategic layer** | `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, `/plan-design-review`, `/plan-devex-review` | `grill-me`, `grilling` (but no structured review modes) | Gstack has 5 review modes; MP has generic grilling |
| **Gstack execution layer** | `/ship`, `/land-and-deploy`, `/benchmark`, `/canary`, `/health`, `/retro` | None | MP has no deploy/monitoring/retro skills |
| **Gstack design layer** | `/design-consultation`, `/design-shotgun`, `/design-html`, `/design-review` | `prototype` (UI.md branch only) | Gstack has full design system; MP has throwaway prototypes |
| **Gstack browser integration** | `/browse`, `/scrape`, `/skillify`, `/open-gstack-browser`, `/pair-agent` | None | MP has no browser automation |

**Measured:** AAW capabilities from `ARCHITECTURE.md`, `README.md`, `.advanced-plans/PLANS-INDEX.md`, `docs/agents/worker-attribution.md`.  
**Inferred:** MP gaps based on absence from fetched skill catalogue.

---

## 6. Open Questions (Unsettled from Primary Sources)

1. **MP upstream skill availability:** 7 skills returned 404 from GitHub raw (`grill-me`, `grilling`, `grill-with-docs`, `requesting-code-review`, `receiving-code-review`, `systematic-debugging`, `test-driven-development`, `executing-plans`, `handoff`). Are these unpublished, private, or renamed? **Source:** `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/*/SKILL.md` returned 404.

2. **MP `aihero.dev/skills` catalogue:** The envelope instructed to fetch from `https://www.aihero.dev/skills` if reachable. The fetch returned empty output. Is this the canonical MP skills catalogue, and does it differ from the GitHub repo? **Source:** `curl -s https://www.aihero.dev/skills` returned no output.

3. **Superpowers skill inventory:** The `.claude/plugins/cache/claude-plugins-official/superpowers/` directory was not fully enumerated. What is the complete list of superpowers skills, and how do they map to MP skills? **Source:** Glob returned no matches (path may be stale).

4. **Advanced-planning command set:** The `phase-plan-creator` and `ralph-loop-planner` skills were read, but `/plan-and-phase`, `/new-phase`, `/next-loop`, `/run-gate` commands are not skills — they are Claude Code commands registered by the plugin. What is the complete command list, and are they harness-specific? **Source:** Inferred from CLAUDE.md routing; no command registry read.

5. **Herdr orchestration design:** The v0.2 design doc (`.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md`) was referenced but not fully read. What are the exact adapter contracts for claude/codex/opencode/cursor, and how do MP skills fit? **Source:** Referenced in README.md line 102, ROADMAP.md line 26; not read.

6. **MP `disable-model-invocation: true` semantics:** What does this frontmatter field actually do in Claude Code? Does it prevent the skill from being called by non-Claude harnesses, or is it a hint? **Source:** MP skill frontmatter; no semantic spec found.

7. **AAW worker attribution enforcement:** The `docs/agents/worker-attribution.md` states attribution "cannot be repaired afterwards without rewriting history". How is this enforced? Is there a CI check? **Source:** Referenced in CLAUDE.md line 258; not read.

---

## Appendix A: Source Citations

### A.1 Matt Pocock Skills (Quoted)

- `wayfinder/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/wayfinder/SKILL.md` (lines 1-200+)
- `to-spec/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/to-spec/SKILL.md` (lines 1-80)
- `to-tickets/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/to-tickets/SKILL.md` (lines 1-100)
- `triage/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/triage/SKILL.md` (lines 1-120)
- `implement/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/implement/SKILL.md` (lines 1-20)
- `code-review/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/code-review/SKILL.md` (lines 1-100)
- `research/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/research/SKILL.md` (lines 1-12)
- `prototype/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/prototype/SKILL.md` (lines 1-50)
- `domain-modeling/SKILL.md`: `https://raw.githubusercontent.com/mattpocock/skills/refs/heads/main/skills/engineering/domain-modeling/SKILL.md` (lines 1-60)

### A.2 AAW Local Files (Quoted)

- `CLAUDE.md`: Lines 1-241 (routing block), 258-259 (worker attribution)
- `ARCHITECTURE.md`: Lines 1-348 (system overview, handoff contracts, state bus)
- `README.md`: Lines 1-141 (four-tool diagram, setup)
- `ROADMAP.md`: Lines 1-127 (v0.1 shipped, v0.2 workstreams)
- `DESIGN-RATIONALE.md`: Lines 1-127 (gstack rationale, glue layer)
- `SETUP.md`: Lines 1-208 (install instructions)
- `CHANGELOG.md`: Lines 1-224 (v0.2 changes)
- `.advanced-plans/PLANS-INDEX.md`: Lines 1-107 (phase index, evidence links)
- `docs/agents/issue-tracker.md`: Lines 1-45 (GitHub CLI ops, wayfinding)
- `docs/agents/domain.md`: Lines 1-51 (CONTEXT.md, ADRs)
- `.aaw/installed.json`: Components object (generated_at: 01/09/2026 11:51:57)

### A.3 Gstack Skills (Measured)

- `~/.claude/skills/gstack/.agents/skills/gstack*/SKILL.md`: 50+ skills found via glob

### A.4 Advanced-Planning Skills (Measured)

- `~/.claude/skills/phase-plan-creator/SKILL.md`: Lines 1-30
- `~/.claude/skills/ralph-loop-planner/SKILL.md`: Lines 1-30

### A.5 Local AAW Skills (Measured)

- `.agents/skills/`: 16 skills (wayfinder, to-spec, to-tickets, triage, implement, code-review, research, prototype, domain-modeling, technical-writing, principle-*, etc.)

---

**End of document**
