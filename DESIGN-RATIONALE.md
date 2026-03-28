# Design Rationale

This document explains the decisions behind Advanced AI Workflows -- why these three tools, why boundary integration instead of a monolith, and the key trade-offs accepted along the way.

It is the companion to [ARCHITECTURE.md](ARCHITECTURE.md), which describes *what* the system does. This document describes *why* it is built this way. Where ARCHITECTURE.md shows data flows and component boundaries, this document shows the reasoning that shaped them.

---

## Why Three Tools?

No single tool covers the full brainstorm, plan, review, execute, review cycle. Each of the three tools solves a distinct problem well and stops where the next tool begins. The question was never "which tool is best?" but "which tool is best at each stage?" The profiles below explain what each tool contributes and, critically, where it stops -- because the gaps are what motivate the integration.

**Advanced Planning** solves planning and execution. Its three-tier hierarchy (Phases, Ralph Loops, Todos) decomposes large programmes into bounded, resumable units of work. The filesystem state bus (three JSON files) enables crash recovery and session resumption without relying on agent memory. Gate review agents verify phase success criteria before advancing. The two-agent handoff pattern (orchestrator prepares, worker executes) keeps context focused at each level.

**Where it stops:** plan approval is CLI-only -- the gate review agents produce text verdicts, but there is no visual interface for a human reviewer to see the plan as a structured document, navigate its hierarchy, or attach annotations to specific sections. It also provides no development methodology of its own. The worker executes whatever skills are assigned, but Advanced Planning does not supply brainstorming, TDD, or code review patterns. It is a planning and execution engine, not a methodology framework.

**Plannotator** solves review. Its browser-based annotation UI supports five structured annotation types: deletion, insertion, replacement, comment, and global comment. Each annotation targets a specific part of the plan document, producing feedback that is precise enough for the agent to act on without interpretation. Structured feedback flows back to the agent as a deny message with formatted annotations. Code review mode handles git diffs and PRs. Programme mode adds hierarchical navigation across phases and loops, showing where the current plan sits in the broader programme.

**Where it stops:** it cannot plan or execute. Plannotator is purely a quality gate -- it renders artefacts produced by other tools and collects human judgement, but produces no artefacts of its own. It has no concept of task decomposition, skill injection, or agent orchestration.

**Superpowers** solves methodology. Composable skills trigger automatically via the `using-superpowers` bootstrap skill loaded at session start: brainstorming (Socratic intent exploration), TDD (test-first implementation), systematic debugging (hypothesis-driven investigation), subagent-driven development (isolated execution contexts), and code review (two-stage spec compliance then quality). The skill library serves as the integration currency that other tools consume -- each skill is a self-contained markdown file that can be loaded into any agent context.

**Where it stops:** its `writing-plans` skill produces flat task lists, not multi-phase programmes with hierarchy, bounded loops, handoff summaries, or gate reviews. There is no concept of session resumption, context isolation between planning tiers, or model-tier routing. It has no visual review capability -- code review is text-based, not browser-based.

### Gap Analysis

| Capability | Advanced Planning | Plannotator | Superpowers |
|------------|:-:|:-:|:-:|
| Hierarchical decomposition (phases/loops/todos) | Yes | -- | -- |
| Bounded execution loops with handoffs | Yes | -- | -- |
| Visual plan review | -- | Yes | -- |
| Structured annotation feedback | -- | Yes | -- |
| Development methodology (TDD, debugging) | -- | -- | Yes |
| Composable skill library | -- | -- | Yes |
| Quality gates (human-in-the-loop) | Partial (text) | Yes (visual) | -- |
| Resumption after interruption | Yes | -- | -- |

The table makes the case: no single column has "Yes" in every row. The integrated system does.

Each tool fills gaps the others cannot. Advanced Planning provides the structural backbone (hierarchy, state, resumption). Plannotator provides the human checkpoint (visual review, structured annotations). Superpowers provides the methodology layer (how to brainstorm, how to test, how to review code). Remove any one and a critical capability disappears from the workflow.

---

## Why Boundary Integration?

The deliberate choice was to integrate at boundaries -- file handoffs, hook protocols, markdown documents -- rather than merging the three codebases into one. This was not a default; it was an evaluated decision with specific reasons.

The alternative (merging into a monolith) was considered and rejected. A merged codebase would mean a single install, a single configuration, and no hook conflicts. Those are real advantages. But the costs outweigh them.

### Benefits

**Independent utility.** Each tool works alone. A team that only wants visual plan review uses Plannotator. A team that only wants hierarchical planning uses Advanced Planning. A team that only wants methodology skills uses Superpowers. The integrated workflow is the highest-value configuration, but it is not the only valid one. Merging codebases would force every user to accept all three tools or none -- and the three tools have different runtime requirements (Python, Bun, markdown-only) that not every environment can satisfy simultaneously.

**Upstream sync.** Plannotator and Superpowers are forked from actively maintained upstream repositories. Keeping the forks structurally close to upstream means improvements -- bug fixes, new annotation types, new skills -- can be pulled with minimal merge conflict. A deep merge would make upstream sync impractical within months, cutting off the most valuable source of ongoing improvement.

**Contributor isolation.** Contributing to Advanced Planning requires understanding Python, state machines, and multi-agent orchestration. Contributing to Plannotator requires understanding Bun, TypeScript, and browser UI. Contributing to Superpowers requires understanding markdown skill design and prompt engineering. These are different skill sets with different communities. No contributor should need to understand all three domains to make a change in one tool. Boundary integration preserves this separation.

**Testability.** Each integration boundary is a well-defined interface: a markdown file, a JSON payload on stdin/stdout, a SKILL.md file in a known directory. These interfaces can be tested with fixtures in isolation. A Plannotator test can feed it a plan string and assert on the rendered UI without running Advanced Planning. An Advanced Planning test can provide a mock skill file without installing Superpowers. A Superpowers test can validate a design document without knowing what will consume it. This means each tool's test suite remains fast, focused, and self-contained.

### Trade-offs

These are genuine costs, not hypothetical risks.

**Configuration surface.** Three tools means three installations, three hook registrations, and three sets of configuration. The setup instructions are longer than they would be for a monolith, and there are more things that can be misconfigured. A missing hook registration is silent -- the tool simply does not intercept the expected event, and the failure mode is confusion rather than an error message.

**Hook conflicts.** Both Superpowers and Advanced Planning respond to the intention to enter plan mode. Superpowers intercepts `EnterPlanMode` to route through brainstorming; Advanced Planning expects to receive plan mode control for `phase-plan-creator`. Without the fork modification (conditional routing based on detected tools), both tools fight for the same hook event. The resolution works but adds maintenance burden on every upstream sync.

**Conceptual duplication.** Both Advanced Planning and Superpowers have opinions about what comes after brainstorming. Superpowers chains brainstorming to its own `writing-plans` skill, producing flat task lists. Advanced Planning expects brainstorming output to feed into `phase-plan-creator`, producing hierarchical phase plans. This overlap is manageable with explicit routing decisions in the fork, but it means two tools carry code for a handoff that only one of them should own in the integrated configuration.

---

## Key Architectural Decisions

Five decisions shape the system's architecture. Each is presented with the context that motivated it, the decision itself, the rationale, and the trade-offs accepted.

### Decision 1: Fork-and-Adjust, Not Rebuild

**Context.** Plannotator and Superpowers are mature, actively maintained projects with established user bases and working test suites. Rebuilding their functionality from scratch would duplicate months of effort and lose the benefit of ongoing upstream improvements.

**Decision.** Fork both repositories. Make targeted adjustments at integration boundaries only. Leave internals untouched.

**What the Superpowers fork changes:**
- Conditional routing in the `brainstorming` skill: when Advanced Planning is detected (by checking for its skills directory), brainstorming redirects to `phase-plan-creator` instead of `writing-plans`
- Conditional `EnterPlanMode` interception in the `using-superpowers` bootstrap: defers to Advanced Planning's slash commands when they are available
- `AskUserQuestion` integration for brainstorming to use structured user input

**What the Plannotator fork changes:**
- Programme mode: renders `PLANS-INDEX.md` hierarchy with breadcrumb navigation across phases and loops
- Section context injection into the annotation UI so reviewers see where they are in the programme

**What forks do not change.** Core annotation UI, annotation engine, skill execution, hook mechanisms, build systems, and test suites all remain upstream-identical. The forks are additive, not invasive.

**Trade-off.** Fork maintenance when upstream ships improvements. Each upstream pull requires checking that fork-specific changes (conditional routing, programme mode) still apply cleanly. The narrower the fork diff, the lower this cost.

### Decision 2: Skills as the Integration Currency

**Context.** The three tools need a common unit of exchange -- something Advanced Planning can assign, Superpowers can provide, and the worker agent can consume, without any tool needing to understand the other's internals.

**Decision.** Markdown skill files (`SKILL.md`) with YAML frontmatter serve as the universal exchange format.

**Why markdown.** Several properties make it uniquely suited:

- *Human-readable.* Contributors can review, write, and edit skills without specialised tooling.
- *Agent-consumable.* Language models handle markdown natively -- it is the format they are most reliably trained on.
- *Version-controllable.* Standard git diff shows meaningful changes in skill content.
- *Tool-agnostic.* Any runtime that reads text files can consume skills. No SDK, no parsing library, no serialisation format.
- *Discoverable.* Glob for `SKILL.md` in known directories. No registry, no manifest, no build step.

**How it works.** The `plan-skill-identification` skill scans project-local (`.claude/skills/`) and global (`~/.claude/skills/`) directories, matches skills to todos based on task descriptions, and writes the skill name into each todo's YAML frontmatter. At execution time, the worker agent loads the single referenced `SKILL.md` before each todo and discards it immediately after -- targeted injection, not blanket loading. This keeps the worker's context window focused: one methodology at a time, with maximum token budget available for the actual implementation work.

**Trade-off.** Skills are untyped. There is no schema enforcement beyond convention -- a skill file could contain anything from a two-line prompt to a multi-page methodology specification. Quality depends entirely on skill authoring discipline and the community catalogue ecosystem. There is also no dependency resolution: if skill A assumes skill B has already run, nothing enforces that ordering.

### Decision 3: Filesystem State Bus Over IPC

**Context.** The orchestrator and worker agents need to coordinate handoffs -- the orchestrator produces a todo list, the worker executes it, and the main thread needs to know the outcome. These agents are ephemeral language model sessions that are spawned, do their work, and exit. They are not long-running processes that can hold open connections.

**Decision.** Three JSON files serve as the complete state bus: `loop-ready.json` (orchestrator to worker), `loop-complete.json` (worker to main thread), and `history.jsonl` (append-only audit log).

**Why files, not IPC or a database.**

- *Simplicity.* Agents are ephemeral. IPC requires both ends to be alive simultaneously; files do not.
- *Debuggability.* When something fails, `cat loop-ready.json` shows exactly what the orchestrator produced. The state bus *is* the debug log.
- *Agent-agnostic.* Any runtime that reads JSON can participate -- Python, TypeScript, shell scripts, or a human with a text editor.
- *Crash recovery.* Files reflect the last completed transition. The main thread can inspect state and resume from the exact point of failure. Either a file was written completely or it was not written at all.
- *Auditability.* `history.jsonl` is append-only. Every loop completion is recorded with its handoff summary, providing a complete documentary record for gate review and programme closeout.

**Trade-off.** No real-time coordination. Agents run sequentially, not concurrently. The state bus is inherently single-user -- there is no locking, no conflict resolution, and no support for parallel loop execution. This is acceptable for the current single-developer workflow but would need rethinking for team use.

### Decision 4: Model-Tier Routing

**Context.** AI model capabilities and costs vary dramatically. Opus excels at broad strategic reasoning but is slower and more expensive. Sonnet handles structured decomposition well at moderate cost. Haiku is fast and cheap but limited in complex reasoning. Using the wrong tier wastes either money (Opus for trivial tasks) or capability (Haiku for strategic planning).

**Decision.** Match the model to the cognitive demands of each role in the hierarchy.

| Role | Model | Reasoning |
|------|-------|-----------|
| Phase plan creation | Opus | Requires holding full project context, reasoning about cross-phase dependencies, making scope trade-offs |
| Ralph loop planning | Sonnet | Narrower scope, more concrete reasoning, structured YAML output constrains hallucination |
| Loop orchestration | Sonnet | Reads phase plan, assigns skills and agents, produces structured `loop-ready.json` |
| Todo execution | Sonnet/Haiku | Focused implementation guided by injected skill; context window freed from planning overhead |

**Trade-off.** These assignments are heuristics, not guarantees. A particularly complex todo might benefit from Sonnet over Haiku; a straightforward phase plan might not need Opus. The `complexity` field in todo YAML allows per-task override, and the `/model-check` command lets users verify routing at any point. But the defaults are fixed in the skill definitions, so changing the heuristic across the board requires editing multiple skills. There is also no automatic escalation -- if Haiku fails a todo, the system does not retry with Sonnet unless a human intervenes.

### Decision 5: Human-in-the-Loop Gates

**Context.** Autonomous execution without checkpoints produces drift. An agent that plans, executes, and advances through phases without human verification can compound errors across phase boundaries -- a flawed assumption in phase 1 becomes structural debt by phase 3.

**Decision.** Every phase boundary requires explicit human approval. Gate review agents evaluate success criteria, but the final verdict passes through Plannotator's visual review UI before the system advances.

**Why visual, not text.** Plans are structured documents where formatting, section hierarchy, and relationships between components matter. A text-based approval prompt shows a flat string; a visual review shows the plan as the agent will interpret it -- with navigation, section headings, and the ability to annotate specific parts.

The five annotation types map directly to the kinds of feedback a reviewer naturally gives:

- *Deletion:* remove this scope item, it is out of bounds
- *Insertion:* add this requirement, it was missed
- *Replacement:* rephrase this criterion, it is ambiguous
- *Comment:* flag this concern for the planner's attention
- *Global comment:* overall feedback that applies to the plan as a whole

Versioning shows what changed between review rounds. Programme mode shows where this plan sits in the broader hierarchy, preventing the reviewer from losing sight of the programme-level context.

**Trade-off.** Visual review requires a browser. Headless environments (SSH sessions, CI runners) cannot open the Plannotator UI. The fallback is text-based gate verdicts written directly to the state bus, which works but loses the structured annotation capability. This is an acceptable degradation -- headless environments are typically automated pipelines where human review is not the primary interaction mode.

---

## Open Questions

These are genuinely unresolved items that affect the system's long-term viability. They are listed here because they represent real architectural constraints, not aspirational features. Each one has been identified through actual use of the integrated system.

1. **Skill catalogue integration workflow.** There is no standard way to discover, evaluate, and pull skills from ecosystem repositories (awesome-agent-skills, claude-scientific-skills, anthropic/skills). The `plan-skill-identification` skill scans local directories, but there is no mechanism for fetching skills on demand from remote catalogues. A team starting a new project must manually curate their local skill directory before the planning pipeline can assign skills effectively.

2. **OpenCode parity.** The full three-tool integration has been developed and tested on Claude Code. OpenCode support exists in Plannotator (the review UI works on both runtimes), but the complete planning-review-execution cycle -- including hook interception, state bus coordination, and gate review -- is untested on OpenCode. Hook protocol differences between runtimes may surface as subtle behavioural bugs.

3. **Upstream divergence risk.** Fork maintenance burden grows with time. If Plannotator upstream ships a major UI refactor or Superpowers upstream restructures its skill format, the fork patches may require non-trivial rework. The mitigation (keeping forks minimal and additive) reduces but does not eliminate this risk. The longer the forks remain unmerged upstream, the higher the cost of each sync.

4. **Gate review feedback loop.** When a gate review fails and produces a versioned retry, the retry does not automatically re-trigger visual review via Plannotator. The retry loop is text-based, which means iterative gate failures lose the structured annotation capability that makes the first review valuable. Closing this loop would require the gate review agent to invoke the Plannotator hook directly, which crosses the current boundary integration design.

5. **Multi-user workflows.** The filesystem state bus is single-user by design. There is no locking, no concurrent loop execution, and no merge resolution for simultaneous edits to state files. Teams with multiple agents or developers working on the same programme would need external coordination -- a shared state bus would require at minimum file locking and conflict detection, which are not planned.

These questions are tracked in [ROADMAP.md](ROADMAP.md) alongside planned features and integration milestones.
