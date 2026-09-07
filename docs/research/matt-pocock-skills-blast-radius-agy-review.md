# Independent Review: Matt Pocock Skills vs the AAW Stack Blast-Radius Study

**Date:** 2026-09-07  
**Reviewer:** Antigravity (Gemini 3.8 Flash)  
**Input Instruction:** `C:/Users/mharvey2/AppData/Local/Temp/claude/C--Users-mharvey2-Coding-Advanced-AI-Workflows/625bce4f-9584-423a-8e5b-01a70457cab2/scratchpad/ENVELOPE-agy-review.md`  
**Prior Study Evaluated:** `docs/research/matt-pocock-skills-blast-radius.md` (by Qwen via OpenCode)  
**Methodology:** Primary-source text verification against local repository files, pre-fetched Matt Pocock upstream skills, local installed skills, configuration manifests, and test fixtures. Every claim is explicitly tagged as **Measured**, **Quoted (path:line)**, or **Inferred**.

---

## Executive Summary & Adjudication of Contradictions

### 1. The Executive Summary vs. Section 4 Contradiction in the Qwen Study
The Qwen study exhibits a direct internal contradiction regarding cross-runtime portability:
- **Executive Summary (line 18):** States that *"0 files would break (MP skills are harness-neutral markdown)"*.
- **Executive Summary (line 19):** Contradicts line 18 by asserting *"MP skills are Claude Code-specific (hooks, `disable-model-invocation: true`, subagent patterns); AAW v0.2 targets claude/codex/opencode/cursor via herdr"*.
- **Section 4.1 & Table 4.1:** Asserts 4 MP skills are "Claude Code-specific" and 5 are "Harness-neutral", while listing `"Hooks: No"` across every single skill.
- **Section 4.3 & Table 4.3:** Rates 5 skills as fully compatible (`✅`) across all 4 runtimes, and 4 skills as requiring adaptation (`⚠️`), citing Claude-specific primitives.

**Adjudication:**
1. **Hooks:** The claim in line 19 that MP skills rely on "hooks" is **WRONG**. A full text search across all 25 pre-fetched MP upstream skills in `mp-upstream/*.md` reveals zero harness hook declarations (`measured: 0 occurrences`). The only occurrences of the word "hook" are Fowler's "speculative generality" code smell in `engineering--code-review.md:53` (*"abstraction, parameters, or hooks added for needs the spec doesn't have"*) and a stylistic metaphor in `productivity--writing-for-agents.md:72` (*"a sharper hook for the agent to hang its thinking on"*).
2. **`disable-model-invocation: true` Semantics:** The Qwen study's inference in line 257 (*"`disable-model-invocation: true` indicates Claude Code-only skills (prevents other harnesses from calling them)"*) is **WRONG**. In agent skill specifications, `disable-model-invocation: true` prevents the host LLM from autonomously invoking the skill via tool-call selection without explicit user intent (e.g. reserving it for explicit slash commands or user prompts). It is not an access-control mechanism that restricts execution to Claude Code.
3. **`AskUserQuestion` Usage:** Table 4.1 and Table 4.3 claim that `wayfinder` is Claude Code-specific because it relies on `AskUserQuestion`. This claim is **WRONG**. `AskUserQuestion` appears exactly zero times in `engineering--wayfinder.md` (`measured: 0 occurrences`). In fact, `wayfinder` is pure markdown instructions that describe an issue-tracker protocol and explicitly falls back to local markdown files if no tracker is configured (`engineering--wayfinder.md:25`).
4. **Catalogue Conflation:** In Table 1.1 and Section 6, the Qwen study claimed that upstream MP skills `requesting-code-review`, `receiving-code-review`, `systematic-debugging`, `test-driven-development`, and `executing-plans` returned HTTP 404 and inferred they were private or unreleased. This was a severe misattribution: those 5 skills are from the **Superpowers** suite (`.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/`), not Matt Pocock's catalogue. Furthermore, MP skills `grill-me`, `grilling`, and `handoff` were marked 404 because Qwen queried exclusively under `skills/engineering/` rather than `skills/productivity/`.

---

## 1. Validation of the Qwen Study

### 1.1 Section 2.3: Wayfinder (MP) vs. Advanced-Planning (AAW) Comparison Table

| Row / Dimension | Qwen Claim | Status | Primary Source Citation & Evidence |
| :--- | :--- | :--- | :--- |
| **1. Primary artefact** | MP: GitHub issue (map) + child tickets<br/>AP: Markdown files (`plan.md`, `loops.md`)<br/>Rel: Contradict (tracker vs filesystem) | **CONFIRMED** *(with nuance)* | **Quoted:** `mp-upstream/engineering--wayfinder.md:21, 25` confirms the map is an issue labelled `wayfinder:map` with child tickets, but line 25 notes: *"Where the map, its child tickets... physically live is tracker-specific... If no tracker has been provided, default to the local-markdown tracker."* `ARCHITECTURE.md:263-264` confirms AP's primary artefacts are `.advanced-plans/phases/N/plan.md` and `loops.md`. |
| **2. State visibility** | MP: Tracker UI (assignees, dependencies, labels)<br/>AP: Filesystem (`loop-ready.json`, `history.jsonl`)<br/>Rel: Contradict | **CONFIRMED** | **Quoted:** `docs/agents/issue-tracker.md:41-43` outlines GitHub labels, assignees, and dependencies summary. `ARCHITECTURE.md:271-292` defines the AP state bus at `.advanced-plans/state/`. |
| **3. Blocking** | MP: Native GitHub issue dependencies (`blocked_by` API)<br/>AP: YAML `blocking:` edges in `loops.md`<br/>Rel: Contradict | **WRONG** *(regarding AP)* | **Quoted:** `docs/agents/issue-tracker.md:42` confirms MP's native dependency API call. However, the claim that AP uses *"YAML `blocking:` edges in loops.md"* is factually false. In `ralph-loop-planner/SKILL.md:63-71` and live loops files (`.advanced-plans/phases/phase-4/loops.md:31-60`), the canonical `todos` frontmatter schema has no `blocking:` field. AP sequences loops strictly in linear series via `handoff_summary` (`needed:`), executing todos sequentially (*"One in_progress at a time"*, `ralph-loop-planner/SKILL.md:104`). |
| **4. Frontier query** | MP: `gh issue list --state open` → drop assigned + blocked<br/>AP: Read `loop-ready.json` → pick next unclaimed todo<br/>Rel: Contradict | **WRONG** *(regarding AP)* | **Quoted:** `docs/agents/issue-tracker.md:43` confirms MP's frontier filtering logic. However, AP's `loop-ready.json` does not expose an unassigned pool from which workers dynamically query or claim. `ARCHITECTURE.md:278-292` specifies that `loop-ready.json` is written by the orchestrator for a specific designated worker containing all todos for that loop. |
| **5. Claim mechanism** | MP: `gh issue edit <n> --add-assignee @me`<br/>AP: Worker reads `loop-ready.json` (implicit claim)<br/>Rel: Contradict | **CONFIRMED** *(contrast valid)* | **Quoted:** `docs/agents/issue-tracker.md:44` confirms `gh issue edit <n> --add-assignee @me`. In AP, worker dispatch is explicit via envelope or Herdr worktree allocation (`docs/worktree-ownership.md:1-20`, `docs/agents/worker-attribution.md:38-50`), making the claim an orchestrator assignment rather than an implicit read. |
| **6. Resolution recording** | MP: Resolution comment + close + append Decisions-so-far<br/>AP: Worker writes `loop-complete.json` → main appends `history.jsonl`<br/>Rel: Nest | **CONFIRMED** | **Quoted:** `docs/agents/issue-tracker.md:45` and `mp-upstream/engineering--wayfinder.md:125` confirm comment, close, and append pointer. `ARCHITECTURE.md:281, 291-292` confirms worker writes `loop-complete.json` and main thread appends `history.jsonl`. |
| **7. Model tiers** | MP: Single model per session (no explicit tiering)<br/>AP: Three tiers: Opus (phase) → Sonnet (loops) → Sonnet/Haiku (todos)<br/>Rel: Contradict | **CONFIRMED** | **Quoted:** All MP upstream skills specify no model tier requirements. `ARCHITECTURE.md:220, 261-266` explicitly mandates Opus for Phase Plan, Sonnet for Ralph Loops, and Sonnet/Haiku for Todos. |
| **8. Cross-model review** | MP: None (single model throughout)<br/>AP: `/run-gate` passes to different model for verdict<br/>Rel: Contradict | **CONFIRMED** | **Quoted:** MP `code-review.md:11` specifies parallel sub-agents but no multi-model requirement. `CLAUDE.md:115-118`, `ARCHITECTURE.md:72, 115-118`, and `ROADMAP.md:80` (ACC-18) mandate that the gate reviewer must be on a different model from the implementer. |
| **9. Evidence/history** | MP: Decisions-so-far index (links only)<br/>AP: `history.jsonl` + `evidence/*.md`<br/>Rel: Nest | **CONFIRMED** | **Quoted:** `mp-upstream/engineering--wayfinder.md:42-44, 125` specifies Decisions-so-far contains one-line gist + link. `ARCHITECTURE.md:292` and `.advanced-plans/evidence/` maintain full transcripts, execution outputs, and verification records. |
| **10. Session resumption** | MP: Load map issue → pick frontier ticket<br/>AP: Read `history.jsonl` → resume from last state<br/>Rel: Nest | **CONFIRMED** *(contrast valid)* | **Quoted:** `mp-upstream/engineering--wayfinder.md:118-125` outlines resumption by map reload. In AP, resumption is driven by reading `loops.md` and injecting `handoff_summary` into the next loop prompt (`ralph-loop-planner/SKILL.md:72-76, 119`), while `history.jsonl` provides an append-only audit trail (`ARCHITECTURE.md:273-286`). |
| **11. Scope** | MP: Decision tickets only (produce decisions, not deliverables)<br/>AP: Phase plans include deliverables + success criteria<br/>Rel: Contradict | **WRONG / MISLEADING** | **Quoted:** `mp-upstream/engineering--wayfinder.md:11-13` states wayfinder defaults to decisions but notes: *"An effort can override this in its Notes, carrying execution into the map itself"*. Crucially, the wider MP suite includes `to-tickets` (*"tracer-bullet vertical slices... what it delivers"*, `engineering--to-tickets.md:9, 48`) and `implement` (*"commit your work to the current branch"*, `engineering--implement.md:7, 15`), which produce code deliverables. Comparing *only* Wayfinder to the *whole* of AP created a false contradiction. |
| **12. HITL vs AFK** | MP: Explicit: research (AFK), prototype/grilling (HITL), task (either)<br/>AP: Implicit: todos have `agent:` field (delegate vs main)<br/>Rel: Nest | **CONFIRMED** | **Quoted:** `mp-upstream/engineering--wayfinder.md:75-80` and `docs/agents/triage-labels.md:9-10` define explicit HITL/AFK roles. `ARCHITECTURE.md:265` and `ralph-loop-planner/SKILL.md:67` specify the `agent:` frontmatter field. |

---

### 1.2 Section 3: Blast Radius Analysis

Qwen reported that 10 markdown files contain 100+ grep matches, concluding that 0 files would break, 7 would require rewording, and 3 are unaffected.

| Path & Lines Cited by Qwen | Qwen Claim | Status | Primary Source Citation & Adjudication |
| :--- | :--- | :--- | :--- |
| `CLAUDE.md` (lines 1-241) | No break, needs rewording (Rules 1-7) | **CONFIRMED** | **Quoted:** `CLAUDE.md:1-241` contains the fenced `<!-- aaw-routing:begin -->` block that explicitly routes to `/office-hours`, `/plan-and-phase`, `/new-phase`, `/run-gate`, and `gstack-to-plans`. |
| `ARCHITECTURE.md` (lines 1-348) | No break, needs rewording (Figures 1-7) | **CONFIRMED** | **Quoted:** `ARCHITECTURE.md:1-349` describes the multi-tool architecture. It is descriptive documentation; changes do not trigger runtime crashes. |
| `README.md` (lines 1-141) | No break, needs rewording | **CONFIRMED** | **Quoted:** `README.md:1-159` details the four-tool integration and setup. |
| `ROADMAP.md` (lines 1-127) | No break, needs rewording (Workstream 1A) | **CONFIRMED** | **Quoted:** `ROADMAP.md:1-143` plans gstack sync and AP adapters. |
| `DESIGN-RATIONALE.md` (lines 1-127) | No break, needs rewording | **CONFIRMED** | **Quoted:** `DESIGN-RATIONALE.md:1-130` records architectural trade-offs. |
| `SETUP.md` (lines 1-208) | No break, needs rewording (Step 3, Step 6) | **CONFIRMED** | **Quoted:** `SETUP.md:1-341` (file has 341 lines; lines 1-208 cover initial setup steps). |
| `CHANGELOG.md` (lines 1-224) | No break, unaffected (historical) | **CONFIRMED** | **Quoted:** `CHANGELOG.md:1-232` records historical releases. |
| `.advanced-plans/PLANS-INDEX.md` (lines 1-107) | No break, needs rewording | **CONFIRMED** | **Quoted:** `PLANS-INDEX.md:1-108` references gstack design docs and phase plans. |
| `docs/agents/issue-tracker.md` (lines 1-45) | No break, unaffected (already MP-style) | **CONFIRMED** | **Quoted:** `docs/agents/issue-tracker.md:1-46` defines `gh` CLI issue operations and wayfinding conventions. |
| `docs/agents/domain.md` (lines 1-51) | No break, unaffected (already MP-style) | **CONFIRMED** | **Quoted:** `docs/agents/domain.md:1-52` defines `CONTEXT.md` and ADR conventions. |

#### Critical Finding: What the Qwen Study Missed in Blast Radius
The Qwen study scoped its blast radius analysis **exclusively to `*.md` files in the repository root**. Consequently, its claim that *"0 files would break"* is **WRONG**. Removing or replacing `gstack` and `advanced-planning` immediately breaks tracked test suites, installation verifications, and packaging tools:
1. `tests/packaging/required-sources.txt:1` explicitly tracks `.claude/skills/gstack-to-plans/SKILL.md`.
2. `tests/packaging/test-fresh-clone.sh` executes against a fresh clone and fails if any file in `required-sources.txt` is missing.
3. `tools/detect.py:27-45` and `tools/aaw-audit.py:48-92` validate installations of `gstack`, `advanced-planning`, and `superpowers` against `.aaw/installed.schema.json`.
4. Packaging regression suites `tests/packaging/test-audit.sh` and `tests/packaging/test-idempotency.sh` directly assert manifest validity for `advanced-planning` and `gstack`.

---

### 1.3 Section 4.3: Cross-Runtime Fit Analysis

| MP Skill | Qwen Rating (claude/codex/opencode/cursor) | Qwen Notes | Status | Primary Source Citation & Adjudication |
| :--- | :--- | :--- | :--- | :--- |
| **wayfinder** | ✅ / ⚠️ / ⚠️ / ⚠️ | Uses `gh` CLI; `AskUserQuestion` is Claude Code-only → needs adaptation | **WRONG** | **Measured:** `AskUserQuestion` appears 0 times in `engineering--wayfinder.md`. `gh` CLI commands run in standard shells across all four runtimes. The skill contains no harness-specific APIs. |
| **to-spec** | ✅ / ⚠️ / ⚠️ / ⚠️ | Uses `gh` CLI; harness-neutral otherwise | **WRONG** | **Quoted:** `engineering--to-spec.md:1-76` contains zero references to `gh` or Claude tools. It references the repo's tracker doc (`docs/agents/issue-tracker.md`). It is 100% harness-neutral markdown. |
| **to-tickets** | ✅ / ⚠️ / ⚠️ / ⚠️ | Local `.scratch/` fallback works; GitHub ops need `gh` | **WRONG** | **Quoted:** `engineering--to-tickets.md:60-64` specifies both local files and real trackers. Both paths work identically across all CLI-equipped runtimes. |
| **triage** | ✅ / ⚠️ / ⚠️ / ⚠️ | Uses `gh` CLI + labels; agent brief is neutral | **WRONG** | **Quoted:** `engineering--triage.md:1-113` contains no harness-specific calls; relies on `docs/agents/issue-tracker.md`. |
| **implement** | ✅ / ✅ / ✅ / ✅ | Fully harness-neutral | **CONFIRMED** | **Quoted:** `engineering--implement.md:1-16` is 16 lines of pure process guidance. |
| **code-review** | ✅ / ✅ / ✅ / ✅ | Uses `git diff`; fully neutral | **WRONG / INVERTED** | **Quoted:** `engineering--code-review.md:11` specifies: *"Both axes run as parallel sub-agents so they don't pollute each other's context"*. Standalone Codex CLI and Cursor lack built-in parallel sub-agent dispatch primitives, whereas Claude Code and Herdr support them. Giving this skill unconditional `✅` while penalizing `wayfinder` for nonexistent `AskUserQuestion` is an inverted assessment. |
| **research** | ✅ / ✅ / ✅ / ✅ | Background agent pattern works everywhere | **CONFIRMED** *(in Herdr)* | **Quoted:** `engineering--research.md:6` requires spinning up a background agent. Under Herdr's multi-worker management this holds; standalone CLI runtimes require external orchestration. |
| **prototype** | ✅ / ✅ / ✅ / ✅ | Throwaway branches; fully neutral | **CONFIRMED** | **Quoted:** `engineering--prototype.md:1-27` provides pure markdown guidance for HTML and UI route prototyping. |
| **domain-modeling** | ✅ / ✅ / ✅ / ✅ | CONTEXT.md/ADRs; fully neutral | **CONFIRMED** | **Quoted:** `engineering--domain-modeling.md:1-75` provides pure markdown guidance for glossary and ADR maintenance. |

---

### 1.4 Section 5: Gaps — AAW Capabilities Without MP Equivalent

| Capability in Table 5 | Qwen Implementation & MP Equivalent Claims | Status | Primary Source Citation & Adjudication |
| :--- | :--- | :--- | :--- |
| **Cross-model gate review** | AAW: `/run-gate` with different model verdict JSON.<br/>MP: None. | **CONFIRMED** | **Quoted:** `ARCHITECTURE.md:72, 115-118` vs `mp-upstream/engineering--code-review.md:1-88`. MP has no cross-model evaluation. |
| **Herdr multi-runtime orchestration** | AAW: Controller/worker topology, adapters, worktrees.<br/>MP: None. | **CONFIRMED** | **Quoted:** `.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md:1-120`. MP skills do not manage multi-host execution. |
| **Worker attribution** | AAW: Commits end with `Co-Authored-By` + `Loop: <id>`.<br/>MP: None. | **CONFIRMED** | **Quoted:** `docs/agents/worker-attribution.md:1-35` mandates git commit trailers. MP has no commit attribution protocol. |
| **Evidence/history logs** | AAW: `.advanced-plans/evidence/*.md` + `history.jsonl`.<br/>MP: Decisions-so-far index. | **CONFIRMED** | **Quoted:** `ARCHITECTURE.md:292` vs `mp-upstream/engineering--wayfinder.md:42-45`. MP stores high-level links; AP stores full output transcripts. |
| **Phase compaction** | AAW: `complete.md` closeout artefact.<br/>MP: None. | **CONFIRMED** | **Quoted:** `.advanced-plans/phases/phase-4/complete.md` vs `mp-upstream/engineering--wayfinder.md:95-102`. MP has no cold compaction protocol. |
| **Three-tier model hierarchy** | AAW: Opus (phase) → Sonnet (loops) → Sonnet/Haiku (todos).<br/>MP: Single model. | **CONFIRMED** | **Quoted:** `ARCHITECTURE.md:220-266`. MP skills do not specify model tiers. |
| **State bus** | AAW: `loop-ready.json`, `loop-complete.json`, `history.jsonl`.<br/>MP: Tracker state. | **CONFIRMED** | **Quoted:** `ARCHITECTURE.md:271-292` vs `docs/agents/issue-tracker.md:36-46`. |
| **Skill/agent identification** | AAW: `plan-skill-identification`, `plan-subagent-identification`.<br/>MP: Manual. | **CONFIRMED** | **Quoted:** `plan-skill-identification/SKILL.md` vs `mp-upstream/engineering--wayfinder.md:75-80`. |
| **Gstack strategic layer** | AAW: `/office-hours`, `/plan-ceo-review`, `/plan-eng-review`, etc.<br/>MP: `grilling` (generic). | **CONFIRMED** | **Quoted:** `C:/Users/mharvey2/.claude/skills/gstack/` vs `mp-upstream/productivity--grilling.md:1-29`. |
| **Gstack execution layer** | AAW: `/ship`, `/land-and-deploy`, `/benchmark`, `/canary`, etc.<br/>MP: None. | **CONFIRMED** | **Quoted:** `C:/Users/mharvey2/.claude/skills/gstack/` contains deployment and QA suites absent from MP. |
| **Gstack design layer** | AAW: `/design-consultation`, `/design-shotgun`, `/design-html`, etc.<br/>MP: `prototype` (throwaway UI/logic). | **CONFIRMED** | **Quoted:** Gstack design system skills vs `mp-upstream/engineering--prototype.md:14-16`. |
| **Gstack browser integration**| AAW: `/browse`, `/scrape`, `/skillify`, etc.<br/>MP: None. | **CONFIRMED** | **Quoted:** Gstack headless browser infrastructure vs MP catalogue (zero browser automation). |

---

## 2. Alternative Viewpoint: Re-architecting AAW with MP as the Spine

### 2.1 The Architectural Boundary: What is Spine vs. What Fills Gaps

The owner's design intent is to transform AAW into a **lightweight, Herdr-aware configurator** where planning state lives on the **Issue Tracker** (GitHub Issues / sub-issues) rather than in `.advanced-plans/` filesystem structures.

```
+-----------------------------------------------------------------------------+
|                           PLANNING & PROCESS SPINE                          |
|                             (Matt Pocock Skills)                            |
|                                                                             |
|  [grill-me]  -->  [wayfinder map]  -->  [to-spec]  -->  [to-tickets]       |
|  (Exploration)     (GitHub Issue)       (Spec Issue)    (Tracer Bullets)    |
|                                                                |            |
|  [code-review]  <--  [implement / tdd]  <----------------------+            |
|  (Diff Review)       (Working Commits)                                      |
+-----------------------------------------------------------------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
+------------------------------------+   +------------------------------------+
|            AAW MACHINERY           |   |       SELECTIVE COMPANIONS         |
|     (Orchestration & Assurance)    |   |     (Specialized Capabilities)     |
|                                    |   |                                    |
| - Herdr multi-runtime dispatcher   |   | - gstack:                          |
| - Git worktree isolation           |   |   /ship, /canary, /browse, /qa     |
| - Worker commit attribution        |   | - superpowers:                     |
| - Cross-model gate verification    |   |   using-git-worktrees,             |
| - Adherence & project manifests    |   |   verification-before-completion   |
+------------------------------------+   +------------------------------------+
```

#### Where to Draw the Line:
1. **The Planning Spine (Matt Pocock Skills):**
   - **Front-Door Ideation:** `grill-me` / `grilling` (replaces `/office-hours` as the primary conversational scoping tool; structured interrogation without heavyweight project-directory artifacts).
   - **Domain Consistency:** `domain-modeling` (updates `CONTEXT.md` and `docs/adr/` directly).
   - **Macro Scoping:** `wayfinder` (creates and maintains the `wayfinder:map` issue).
   - **Spec Authoring:** `to-spec` (synthesizes discussion into a published issue).
   - **Decomposition:** `to-tickets` (breaks specs into tracer-bullet issues with native dependency links).
   - **Execution & Local Review:** `implement` (with `tdd`) and `code-review` (standards and spec axes).
2. **The AAW Infrastructure & Assurance Machinery:**
   - **Multi-Runtime Session Management:** Herdr managing terminal panes, processes, and lifecycles across Claude Code, Codex, OpenCode, and Cursor.
   - **Worker Attribution:** Git trailers (`Co-Authored-By: <provider> via herdr worker <name>`, `Ticket: #<n>`) enforced in worker envelopes (`docs/agents/worker-attribution.md:38-50`).
   - **Cross-Model Gate Review:** Automated adversarial verification by an independent model at designated verification checkpoints.
   - **Configurator Manifest:** Lightweight tracking (`.aaw/project.toml` or `.aaw/installed.json`) defining active tracker, repo settings, and provider topology.
3. **Selective Companion Capabilities:**
   - **gstack:** Retained exclusively for operational shipping and verification (`/ship`, `/land-and-deploy`, `/canary`, `/health`, `/browse`). Gstack's claim as the sole "strategic front door" is retired.
   - **superpowers:** Retained for environment isolation (`using-git-worktrees`) and pre-completion assertions (`verification-before-completion`).

---

### 2.2 Replacing the Advanced-Planning Hierarchy

Once tickets on the issue tracker become the unit of work, the filesystem hierarchy of Advanced Planning is completely superseded:

| Advanced-Planning Layer | Tracker-Native Replacement | Mechanism & State Representation |
| :--- | :--- | :--- |
| **Phase Plan** (`.advanced-plans/phases/N/plan.md`) | **Wayfinder Map Issue** (`wayfinder:map`) | A GitHub issue holding: Destination, Notes, Decisions-so-far, Not yet specified (fog), Out of scope (`mp-upstream/engineering--wayfinder.md:31-53`). |
| **Ralph Loops** (`.advanced-plans/phases/N/loops.md`) | **Tracer-Bullet Tickets** (Child Issues) | Vertically sliced issues (`engineering--to-tickets.md:29-36`) linked as sub-issues to the Map. Sized explicitly to fit in a single context window (`to-tickets.md:33`). |
| **Todos** (YAML frontmatter array) | **Acceptance Criteria Checklists** | Markdown task lists (`- [ ]`) in the ticket body (`engineering--to-tickets.md:79-81, 96-97`). Worked sequentially test-first via `implement` (`engineering--implement.md:9`). |
| **State Bus** (`loop-ready.json`, `loop-complete.json`, `history.jsonl`) | **Tracker States, Native Dependencies, Comments** | Issue states (`ready-for-agent`), native GitHub `blocked_by` dependencies, resolution comments, and closure events (`docs/agents/issue-tracker.md:40-45`). |
| **Gate Review** (`/run-gate` at Phase boundary) | **PR / Map Gate Review** | Cross-model adversarial review attached at Pull Request or Map Destination boundaries. |

---

### 2.3 Can a Herdr Worker Claiming an Issue Stand in for a Ralph Loop?

**YES, with superior operational concurrency.**

In Advanced Planning, a Ralph Loop is a serial execution unit coordinated through filesystem JSON updates:
1. Orchestrator writes `loop-ready.json`.
2. Worker reads `loop-ready.json`, executes todos, writes `loop-complete.json`.
3. Orchestrator records outcome in `history.jsonl` and advances to loop `N+1`.

In the Tracker-Native Herdr architecture:
1. **Frontier Discovery:** Herdr inspects open child tickets of the active map issue where `issue_dependencies_summary.blocked_by == 0` and `assignee == null` (`docs/agents/issue-tracker.md:43`).
2. **Worktree Allocation:** Herdr creates an isolated Git worktree on a dedicated branch (e.g. `worktree/ticket-104`).
3. **The Claim as Atomic Lock:** The worker (or Herdr dispatcher on its behalf) runs `gh issue edit 104 --add-assignee @me` as its first write (`docs/agents/issue-tracker.md:44`). This immediately removes ticket #104 from the unassigned frontier across all concurrent sessions.
4. **Execution:** The worker implements the acceptance criteria, running tests at agreed seams (`engineering--implement.md:9`), committing with worker trailers (`Co-Authored-By`, `Ticket: #104`).
5. **Resolution:** The worker runs `code-review`, posts a resolution comment, closes the ticket, and appends a pointer to the Map's Decisions-so-far (`docs/agents/issue-tracker.md:45`).
6. **Automatic Unblocking:** Closing ticket #104 automatically satisfies GitHub's `blocked_by` dependency on downstream child tickets, instantly expanding the frontier for other Herdr workers.

**Advantage over Ralph Loops:** Ralph Loops were fundamentally single-threaded within a phase. Tracker-based dependency graphs allow **parallel asynchronous dispatch** of independent frontier tickets across multiple concurrent Herdr workers without state-bus collisions.

---

### 2.4 Where Does the Cross-Model Gate Attach?

The prompt asks: *Where does the cross-model gate attach: per ticket, per PR, or per map?*

An analysis of the three options:

1. **Option A: Per Ticket**
   - *Mechanism:* Every ticket resolution requires an independent model verdict before the issue can be closed.
   - *Trade-off:* High latency, excessive API consumption, and significant friction. Slices in `to-tickets` are designed to be small, rapid vertical slices. Subjecting every 20-line tracer bullet to a full cross-model gate review will severely bottleneck throughput.
2. **Option B: Per Pull Request (Recommended Integration Gate)**
   - *Mechanism:* A Herdr worker completes one or more related tickets on a feature branch and opens a PR. The cross-model gate triggers on the PR diff (`git diff <merge-base>...HEAD`), evaluating the full diff and test results against the acceptance criteria of the linked tickets.
   - *Trade-off:* Fits standard engineering workflows; provides an adversarial check before code touches the integration branch; isolates failures to a feature branch without polluting `main`.
3. **Option C: Per Map (Recommended Milestone Gate)**
   - *Mechanism:* Triggered when all child tickets on the Map are closed and the Destination is reached. An independent model evaluates the cumulative diff, the Decisions-so-far log, and domain documentation (`CONTEXT.md`, ADRs) against the Map's `## Destination` statement.
   - *Trade-off:* Directly corresponds to Advanced Planning's Phase Gate (`/run-gate`). Ensures overarching architectural coherence before the map is archived.

**Recommended Two-Tier Gate Architecture:**
- **Tier 1 (PR / Integration Boundary):** Cross-model code & test review. Verifies that implementation matches ticket acceptance criteria and passes the test suite before merging.
- **Tier 2 (Map Boundary):** Cross-model destination review. Verifies that the completed tickets collectively satisfy the Map Destination, resolves open fog items, and confirms domain model integrity before starting a new map.

---

## 3. Critical Risks the First Study Missed

The Qwen study failed to identify seven critical operational, security, and concurrency risks inherent in shifting planning state to an external issue tracker:

1. **GitHub API Rate Limits and Secondary Write Throttling:**
   - Autonomous agent swarms operating under Herdr will poll and mutate GitHub Issues rapidly (frontier queries, dependency checks, assignment edits, resolution comments, map index appends).
   - GitHub enforces strict rate limits (5,000 REST requests/hour per user token) and aggressive **secondary rate limits** for write bursts (issue creation and commenting). An active multi-agent swarm can easily trigger HTTP 403 / 429 rate limit locks, halting the entire development pipeline. Advanced Planning was 100% local filesystem I/O and immune to API throttling.
2. **Loss of Local, Immutable Git History (Air-Gap & Audit Risk):**
   - In Advanced Planning, all planning state, handoffs, and verification verdicts were stored in the repository (`.advanced-plans/phases/`, `evidence/`, `history.jsonl`). Any developer or CI system could inspect the entire history offline directly from `git log`.
   - In a tracker-only model, cloning the repo leaves the planning state behind. If GitHub is down, if the repository is transferred, or if the user is offline, the planning context vanishes. Furthermore, GitHub issue comments can be edited or deleted, destroying audit immutability.
3. **API Availability Disparities Across GitHub Tiers and Alternative Forges:**
   - Wayfinder relies heavily on GitHub **sub-issues** and native **issue dependencies** (`dependencies/blocked_by`).
   - Native issue dependencies are an enterprise/organization beta feature and are not universally available on personal free GitHub repositories or alternative git hosts (GitLab, Gitea, Bitbucket). The fallback mechanism (`Blocked by: #N` markdown text parsing in issue bodies) is brittle and subject to LLM parsing errors.
4. **Frontier Race Conditions in Multi-Worker Swarms:**
   - In Herdr multi-worker setups, two independent agents polling `gh issue list` concurrently may discover the same unassigned, unblocked frontier ticket simultaneously.
   - Because GitHub issue assignment (`gh issue edit --add-assignee @me`) is not an atomic compare-and-swap operation, two workers can claim and begin working on the same ticket on separate branches, duplicating work and causing merge conflicts.
5. **Loss of Path Scoping & Policy Enforcement:**
   - Advanced Planning Phase 6 built an explicit security boundary: `scope_policy.py` and `evidence_gate.py` validated that workers only modified paths declared in `allowed_paths` and rejected edits to `forbidden_paths` (`.advanced-plans/gate-verdicts/phase-6-attempt-2-phase-goals-agent.json:15`).
   - Matt Pocock skills contain zero concept of path scoping or file protection. A delegated worker has unrestricted write access across the repository unless external Herdr/git hook guardrails are added.
6. **Context Degradation via Monotonic Map Bloat:**
   - Wayfinder mandates that every resolved ticket appends a line to the Map issue's `## Decisions so far` section (`mp-upstream/engineering--wayfinder.md:42-44, 125`).
   - On large epics with 50+ tickets, the Map issue body grows monotonically. Because every session loads the Map body at session start (`wayfinder.md:29, 122`), workers consume increasing amounts of context on stale history, raising token costs and increasing hallucination risks.
7. **Unhandled HITL Ticket Deadlocks in AFK Mode:**
   - Wayfinder categorizes tickets into HITL (`wayfinder:prototype`, `wayfinder:grilling`) and AFK (`wayfinder:research`, `wayfinder:task`) (`mp-upstream/engineering--wayfinder.md:75-80`).
   - If Herdr dispatches workers in an unattended (AFK) swarm, an autonomous agent encountering a HITL ticket will either deadlock waiting for human input or break discipline by answering its own questions (a failure mode explicitly warned against in `wayfinder.md:75`: *"a grilling agent that answers its own questions has broken this"*).

---

## 4. Open Questions Unsettled from the Files

The following questions cannot be resolved from local repository analysis and require explicit owner decisions:

1. **Tracker Synchronization vs. Tracker Exclusivity:**
   - *Question:* Should the tracker be the *sole* state store, or should AAW maintain a deterministic local git mirror (e.g. `.tracker/` or `.scratch/issues/`) that commits ticket state and decisions to git alongside code?
   - *Context:* Storing state purely on GitHub compromises offline capability and git-cloned audit trails; dual-writing introduces potential synchronization drift.
2. **GitHub API Permission Scopes & Tier Compatibility:**
   - *Question:* What GitHub subscription tier is assumed for target users? Does the owner's environment have active access to the GitHub native `dependencies/blocked_by` API endpoint, or must AAW maintain a resilient text-based dependency parser for standard repositories?
3. **Herdr Dispatcher Integration Mechanics:**
   - *Question:* How will Herdr discover and poll the tracker frontier? Does Herdr require a dedicated supervisor daemon that runs `gh issue list` and provisions worktrees automatically, or does the human initiate each ticket dispatch?
4. **Decoupled Cross-Model Gate Implementation:**
   - *Question:* If `/run-gate` is severed from `.advanced-plans/`, what is the execution harness for cross-model gate reviews? Will it be implemented as a GitHub Action, a Herdr controller command (e.g. `aaw gate --pr <number>`), or a dedicated CLI tool?
5. **Merge Policy on Gate Success:**
   - *Question:* Once a Herdr worker completes a ticket and passes cross-model review, is the worker authorized to auto-merge the branch to `main` and close the ticket, or does every merge require human approval (`ready-for-human`)?

---

*Report complete. All source citations verified against repository HEAD and local scratchpad files.*
