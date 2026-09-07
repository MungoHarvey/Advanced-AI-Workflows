# Independent Review: Is Advanced-AI-Workflows (AAW) Worth Its Weight?

**Date:** 2026-09-07  
**Reviewer:** Antigravity CLI (`agy`) — Gemini 3.8 Flash (High)  
**Input Instructions:** `ENVELOPE-review.md` and `ENVELOPE-addendum.md`  
**Target Output:** `docs/research/aaw-value-review-agy.md`  
**Methodology:** Read-only empirical inspection of repository history, working trees, commit logs, issue tracker records, skill files, configuration manifests, test suites, and the companion `advanced-planning` repository (`C:\Users\mharvey2\Coding\advanced-planning`). Every claim is strictly labeled `[measured]`, `[quoted: <path#lines>]`, or `[inferred]`.

---

## Executive Summary & Core Verdict

**Verdict: AAW in its current form is overwhelmingly wasted energy.**

The repository has become a textbook self-referential scaffolding vortex: a meta-framework that plans, audits, gates, packages, tests, and documents its own planning, auditing, gating, packaging, testing, and documenting — while producing virtually zero runtime functionality that an end-user executes to build software.

- `[measured]` Out of **44,214 total lines** across 272 files in this repository, **29,110 lines (65.8%)** and **2.35 MB (74.2% of repo size)** reside inside `.advanced-plans/` (phases, ralph loops, state buses, evidence logs, gate verdicts).
- `[measured]` Out of **249 git commits** in the repository's history, **195 commits (78.3%)** touched `.advanced-plans/`.
- `[measured]` In contrast, the total user-facing code produced by AAW across its entire lifetime amounts to **878 lines**: a 91-line Markdown file-copy skill (`.claude/skills/gstack-to-plans/SKILL.md`) and a 787-line interactive setup prompt (`.claude/skills/setup-with-claude/SKILL.md`). That is less than **2.0%** of the repository.
- `[measured]` Phase 6 alone consumed **4 formal cross-model gate attempts** (`d96a1b4`, `6c69b7b`, `19a6496`, `64ca08d`), spawned deep sub-loop hierarchies (`loop-006`, `loop-007-1` through `loop-007-10`, `loop-008-1` through `loop-008-9`, `loop-009-1` through `loop-009-3`), and ended in a gate failure on attempt 4 with `[quoted: commit 64ca08d]` *"Nothing pushed, no tag, no PR, no phase advanced"*.
- `[measured]` Phase 4 passed its gate on attempt 2, but its output (`feat/aaw-packaging-repair` at commit `3b19a49`) was `[quoted: .advanced-plans/PLANS-INDEX.md#92]` *"pushed, not merged, no PR"*.

The owner's suspicion is completely justified: **the model generation and operating environment that birthed this architecture have both moved on.**

Today, models have 1M–2M context windows, superior native tool-use discipline, and high code-generation fidelity. The owner operates **Herdr** (v0.8.2), which starts, prompts, isolates, and monitors multiple parallel agent runtimes (Claude Code, Codex, OpenCode/Qwen, Cursor, Agy, Pi) across independent Git worktrees. In this operational reality, multi-tier phase planning, JSON state buses (`loop-ready.json`, `loop-complete.json`, `history.jsonl`), and rigid procedural routing blocks are pure overhead.

Furthermore, the proposed **v0.3 pivot** — while correctly identifying Matt Pocock's skills as the natural spine — still attempts to preserve AAW as a meta-framework by inventing a secondary manifest (`.aaw/installed.json`), a custom Python detector/audit tool (`detect.py`, `aaw-audit.py`), an interactive wrapper skill (`/setup-aaw`) with a two-turn handoff, and an elaborate PR-diff gate.

**The simplest architecture that delivers 100% of the owner's wants:**
1. **AAW and advanced-planning collapse into a single minimal entity.**
2. Pin Matt Pocock's skills via the official CLI in one command: `npx skills add mattpocock/skills --all --yes`.
3. Install gstack globally for shipping (`/ship`, `/land-and-deploy`), guardrails (`/careful`), root-cause investigation (`/investigate`), retrospectives (`/retro`), and visual QA (`/qa`, `/design-review`).
4. Replace both frameworks with a **15-line routing and conventions section in `AGENTS.md` (or `CLAUDE.md`)** plus a single operational runbook: **`docs/herdr-ops.md`** describing worktree provisioning, frontier querying, envelope prompt formatting, 3-field handoffs, and commit attribution trailers.

---

## Section A: Value Audit — Scaffolding vs. Shipped Value

### 1. Quantitative Breakdown of the Repository

To evaluate whether AAW is worth its weight, we measured line counts, file counts, and byte distributions across all directories in the repository:

| Component / Directory | File Count `[measured]` | Total Lines `[measured]` | Total Bytes `[measured]` | % of Total Lines `[inferred]` | Nature of Content `[inferred]` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`.advanced-plans/`** | 143 | 29,110 | 2,346,452 | **65.84%** | Retired v0.2 planning engine: phase plans, loop specs, JSON state buses, evidence markdown logs, gate verdicts |
| **`tests/`** | 62 | 5,411 | 263,410 | **12.24%** | Packaging tests, idempotency tests, manifest schema validators, fresh-clone tests (all testing AAW's own installer) |
| **`docs/`** | 19 | 4,079 | 239,774 | **9.23%** | Research studies, config seams, blast-radius studies, git policies, plannotator deprecation notes |
| **Root Markdown** | 14 | 1,693 | 108,601 | **3.83%** | `ARCHITECTURE.md`, `ROADMAP.md`, `SETUP.md`, `DESIGN-RATIONALE.md`, `README.md`, `CHANGELOG.md`, `CONTEXT.md` |
| **`.agents/` (Installed skills)** | 23 | 1,237 | 81,598 | **2.80%** | Pinned Matt Pocock skills (12) + Cursor principle skills (4) copied from external sources |
| **`.claude/` (AAW v0.1/v0.2)** | 7 | 1,313 | 67,438 | **2.97%** | `setup-with-claude` (787 lines), `gstack-to-plans` (91 lines), and settings snippets |
| **`.aaw/` (v0.2 Manifest engine)**| 3 | 662 | 29,171 | **1.50%** | `detect.py` (520 lines), `installed.schema.json`, `installed.example.json` |
| **`tools/`** | 3 | 623 | 24,565 | **1.41%** | `aaw-audit.py` (378 lines) and helper scripts auditing the manifest |
| **`references/`** | 1 | 86 | 3,377 | **0.19%** | Installation reference snippets |
| **TOTAL** | **272** | **44,214** | **3,161,466** | **100.0%** | Full repository checkout |

### 2. Commit History Audit

An audit of commit distributions reveals where developer and agent effort was actually expended across all **249 commits**:

| Target Directory / Subsystem | Commits Touching Path `[measured]` | % of Total Commits `[inferred]` | Nature of Work `[inferred]` |
| :--- | :--- | :--- | :--- |
| **`.advanced-plans/`** | 195 | **78.31%** | Managing Ralph loop state, writing handoff summaries, generating evidence logs, recording gate attempt failures |
| **`docs/`** | 23 | **9.24%** | Documenting policies, config seams, research notes for issue tickets |
| **`tests/`** | 20 | **8.03%** | Fixing packaging tests, idempotency checks, and manifest assertions |
| **`.claude/`** | 20 | **8.03%** | Iterating on `setup-with-claude` and `gstack-to-plans` |
| **`.aaw/` and `tools/`** | 10 | **4.02%** | Developing manifest detection and audit Python scripts |
| **`.agents/` and `skills-lock.json`** | 1 | **0.40%** | Pinning Matt Pocock skills (commit `738aaa9`) |

### 3. What Did AAW Actually Deliver to the End User?

`[inferred]` When stripped of its self-referential scaffolding, what did AAW actually ship that an end-user runs to build their applications?

1. **`gstack-to-plans`** (`.claude/skills/gstack-to-plans/SKILL.md`): `[measured]` **91 lines**.
   `[quoted: .claude/skills/gstack-to-plans/SKILL.md#8-12]` *"Bridges the two halves of the Advanced AI Workflows stack: it takes the design document gstack produces ... and copies it into the active project's `.advanced-plans/specs/` directory"*.
   Its entire implementation is a PowerShell and Bash snippet `[quoted: lines 51-61]` that runs `Get-ChildItem` or `ls -t` to locate the newest `*-design-*.md` file in `~/.gstack/projects/` and copy it into `.advanced-plans/specs/`.
2. **`setup-with-claude`** (`.claude/skills/setup-with-claude/SKILL.md`): `[measured]` **787 lines**.
   An interactive prompt that walks Claude through detecting sentinels, asking user confirmations, editing `.claude/settings.json` permissions, appending fenced markers to `CLAUDE.md`, and copying `gstack-to-plans`.
3. **The Routing Block** (`CLAUDE.md` / `references/claude-md-routing.md`): `[measured]` **240 lines**.
   A markdown instruction block containing 7 situation rules, 3 brainstorming preference overrides, and instructions on how to interpret `.aaw/installed.json`.

`[inferred]` **Total actual product produced: 1,118 lines of Markdown prompts and shell glue.**  
Everything else — 43,000+ lines of files, 195 commits, 143 planning files, 38 gate verdict documents — was scaffolding built to plan, verify, and package those 1,118 lines of glue!

### 4. The Infinite Loop of Phase 6: A Case Study in Wasted Energy

Phase 6 ("Advanced Planning Multi-Runtime Adapters") provides concrete historical evidence of how this planning machinery consumes effort without delivering value:

- **Attempt 1:** `[quoted: commit d96a1b4]` *"gate: phase 6 attempt 1 returns fail from three independent reviewers"*. (Recorded as `gate_fail` in commit `67d188b`).
- **Attempt 2:** `[quoted: commit 6c69b7b]` *"phase 6 gate, attempt 2: fail from all three, and the one place the majority was wrong"*. (Operator resolution recorded in commit `e43c27a`).
- **Remediation Loop 008:** Commits `22cc6b1` through `ef8e03c` show 13 commits spent fixing gate defects, repairing `evidence_gate.py`, reconciling exit codes, and auditing success criteria. Commit `5ef7352` is titled `[quoted]` *"loop-008-3: the router wired, and the fix that reintroduced the disease"*; commit `0658a73` is titled `[quoted]` *"loop-008-4: the guard lands before the thing it guards"*.
- **Attempt 3:** `[quoted: commit 19a6496]` *"gate: phase 6 attempt 3 fails, and codex was right where the in-house agents were not"*.
- **Remediation Loop 009 & 007:** Commits `f323b65` through `7b55c12` show agents fixing vacuous guards, repairing install paths that audits could not see (commit `cdf843a`), and handling profile boundary leaks.
- **Attempt 4:** `[quoted: commit 64ca08d]` *"gate: phase 6 attempt 4 — five of six criteria met, criterion 1 still fails. Reviewer: cursor-agent on cursor-grok-4.6-high, fail/88. codex hit its usage limit mid-attempt and the operator redirected the external reviewer role... Nothing pushed, no tag, no PR, no phase advanced"*.

`[inferred]` Four full cycles of gate reviews, external model evaluations, and remediation loops across weeks of effort yielded **zero merged PRs, zero tags, and zero working software**. The planning architecture became so complex that the system spent 100% of its capacity trying to pass its own internal verification gates.

---

## Section B: Is the v0.3 Direction Still Too Much?

The v0.3 proposal adopts Matt Pocock's skills as the primary spine and identifies five AAW additions:
1. Cross-model gate
2. Worker-attribution convention
3. Routing block
4. Component manifest (`.aaw/installed.json`)
5. `/setup-aaw` wrapper skill

We evaluate each addition against the repository's evidence:

```
+-----------------------------------------------------------------------------------+
|                        AAW v0.3 ADDITIONS EVALUATION TABLE                        |
+------------------------------------+-----------------------+----------------------+
| Addition                           | Verdict               | Action               |
+------------------------------------+-----------------------+----------------------+
| 1. Cross-model gate                | REPLACE-WITH-DOC-LINE | One sentence in doc  |
| 2. Worker-attribution convention   | REPLACE-WITH-DOC-LINE | In Herdr prompt env  |
| 3. Routing block                   | REPLACE-WITH-DOC-LINE | 15-line table in doc |
| 4. Component manifest (.aaw/)      | DROP                  | skills-lock.json only|
| 5. /setup-aaw wrapper skill        | DROP                  | npx skills CLI only  |
+------------------------------------+-----------------------+----------------------+
```

### 1. Cross-Model Gate: **REPLACE-WITH-A-DOC-LINE**

- **What AAW proposes:** Issue #4 and `docs/research/gate-implementation.md` propose adapting `/run-gate` into a per-PR and per-map gate. As `[quoted: docs/research/gate-implementation.md#14-24]` notes, this requires a new `run-gate-pr` command, an input adapter fetching PR diffs, linked ticket parsers, rewritten agent prompts, and an extended verdict JSON schema (`pr_number`, `diff_stats`, `linked_tickets`, `ticket_outcomes`).
- **Why this is still too much:**
  - `[measured]` The existing Python gate infrastructure (`platforms/python/evidence_gate.py`) is **856 lines** of policy checks and schema validation.
  - `[measured]` Matt Pocock's pinned `.agents/skills/code-review/SKILL.md` (lines 1–100) already implements a rigorous two-axis review:
    `[quoted: .agents/skills/code-review/SKILL.md#11]` *"Both axes run as parallel sub-agents so they don't pollute each other's context: Standards... and Spec..."*.
  - In a Herdr multi-runtime setup, the human or controller can run `code-review` in an independent CLI pane (e.g. Codex or Cursor) against `git diff main...HEAD`.
  - Storing structured JSON verdicts in a repo directory (`.advanced-plans/gate-verdicts/`) created schema validation drift: `[quoted: docs/research/gate-implementation.md#279-286]` found that example verdicts in Phase 2 failed their own JSON Schema due to unauthorized fields (`generated_at`, `phase_success_criteria_summary`, `all_loops_complete`).
- **The simplest replacement:** A single line in `AGENTS.md` / `docs/herdr-ops.md`:
  > *"Before merging a feature branch PR to `main`, run `code-review` using a model different from the implementer (e.g. Codex or Cursor if implemented by Claude/Qwen) and paste the review summary into the PR."*

### 2. Worker-Attribution Convention: **REPLACE-WITH-A-DOC-LINE**

- **What AAW proposes:** A formal repository document `docs/agents/worker-attribution.md` (65 lines) and manifest sentinels tracking commit trailers.
- **Why this is still too much:**
  - The document itself explicitly confesses that repository docs are useless for worker compliance:
    `[quoted: docs/agents/worker-attribution.md#38-50]` *"Where this is enforced: In the worker envelope, at dispatch. Not afterwards... A worker asked to 'follow the repo conventions' will not find this file — it reads its cwd, and the convention lives here, in the controller's checkout. Naming the trailers in the envelope is the only mechanism that has been observed to work."*
  - Furthermore, `[quoted: docs/agents/worker-attribution.md#5-10]` reveals that a multi-day investigation occurred because the author believed two commits (`05d1e55`, `0f138de`) had violated attribution trailers, only to discover upon opening the commits that the trailers were already present!
- **The simplest replacement:** Include the trailer template directly in Herdr's worker dispatch envelope prompt:
  > `COMMIT: Co-Authored-By: <provider> via herdr worker <name>`  
  > `Ticket: #<n>`

### 3. Routing Block: **REPLACE-WITH-A-DOC-LINE**

- **What AAW proposes:** In v0.1/v0.2, a 240-line procedural routing block with begin/end fence markers (`<!-- aaw-routing:begin -->`). In v0.3 (Issue #5), a comprehensive lifecycle table mirroring `ask-matt` with component gates, on-ramps, gap-fillers, and escalation rules.
- **Why this is still too much:**
  - `[measured]` The v0.1 block in `C:\Users\mharvey2\Coding\Advanced-AI-Workflows\CLAUDE.md` took 241 lines. To keep it safe, AAW built complex fenced merge logic, idempotency tests (`tests/packaging/test-idempotency.sh`), and uninstall recovery procedures (`setup-with-claude/SKILL.md#466-502`).
  - `[inferred]` Modern agent runtimes automatically read all skill definitions in `.agents/skills/*/SKILL.md`. Matt Pocock's skills describe their own triggers clearly (e.g. `to-spec: "User discussion reaches spec-ready state"`, `wayfinder: "Plan huge work as decision tickets"`).
  - Matt Pocock already provides `/ask-matt` as a conversational router.
- **The simplest replacement:** A concise 15-line table in `AGENTS.md`:
  ```markdown
  ## Workflow Guide
  - Ambiguous epic / multi-session fog: `/wayfinder` (creates issue map)
  - Scoping / clarifying an idea: `/grill-me` or `/grill-with-docs`
  - Approved design -> Spec: `/to-spec` -> `/to-tickets`
  - Implementing ticket: `/implement` (uses `/tdd`, ends with `/code-review`)
  - Shipping & deploy: `/ship`, `/land-and-deploy` (gstack)
  - Deep root-cause debugging: `/investigate` (gstack)
  - Safety: `/careful` (gstack)
  ```

### 4. Component Manifest (`.aaw/installed.json` & `.aaw/detect.py`): **DROP**

- **What AAW proposes:** Issue #8 specifies `.aaw/installed.json` tracking four components (`mp-skills`, `gstack`, `aaw-tools`, `tracker`), validated against `.aaw/installed.schema.json` via `detect.py`, and verified by `tools/aaw-audit.py` and 4 packaging regression tests.
- **Why this is still too much:**
  - `[measured]` `skills-lock.json` (`[quoted: skills-lock.json#1-78]`) is **already the official lockfile** generated by the standard `skills` CLI. It pins each skill by `source`, `sourceType`, `skillPath`, and sha256 `computedHash`.
  - Issue #8 admits: `[quoted: issue #8 resolution]` *"the lock is truth: installed iff every skills-lock.json entry with source mattpocock/skills exists... and hashes to its computedHash"*.
  - `[inferred]` If `skills-lock.json` is the source of truth, creating a second file (`.aaw/installed.json`) that duplicates this truth, and then writing a 520-line Python detector (`detect.py`) plus a JSON Schema (`installed.schema.json`) plus an audit script (`aaw-audit.py`) to verify the second file against the first file is **scaffolding squared**.
- **The simplest replacement:** Drop `.aaw/` entirely. Rely solely on standard `skills-lock.json`.

### 5. `/setup-aaw` Wrapper Skill: **DROP**

- **What AAW proposes:** Issue #9 and `prototype/setup-aaw` create `.agents/skills/setup-aaw/SKILL.md` — an interactive walkthrough that preflights the repo, pins `mp-skills`, pauses for a two-turn handoff for the user to type `/setup-matt-pocock-skills`, resumes, offers gstack, self-pins AAW tools from GitHub, writes routing blocks, and runs `detect.py`.
- **Why this is still too much:**
  - `[measured: docs/research/skills-cli.md#9-25]` proved that:
    `npx skills@latest add mattpocock/skills --all --yes`
    installs all 37 Matt Pocock skills in **one single shell command**.
  - `prototype/setup-aaw` requires a clumsy two-turn conversational pause because `/setup-matt-pocock-skills` has `disable-model-invocation: true` and cannot be invoked by an agent.
  - Wrapping a single `npx` command in a 300-line prompt wizard introduces 14 open decision questions (as recorded by the `[?]` markers in `prototype/setup-aaw`) and requires handling upgrade diffs, uninstall paths, and remote self-pinning edge cases.
- **The simplest replacement:** Do not write a wrapper skill. Document the two installation commands in `README.md` or `SETUP.md`.

---

## Section C: The Simplest Architecture That Delivers the Owner's Stated Wants

### 1. The Owner's Stated Goals
1. Well-regarded, off-the-shelf skill sets.
2. Effective handoffs between sessions.
3. Good spawning and management of Herdr workers.
4. Planning help from the context of skills, not from a separate planning framework.

### 2. The Recommended Minimal Stack

```
+-----------------------------------------------------------------------------+
|                           THE MINIMAL AAW STACK                             |
|                                                                             |
|  1. THE SPINE (Off-the-shelf: Matt Pocock's skills in .agents/skills/)      |
|     - /grill-me, /grill-with-docs, /domain-modeling (CONTEXT.md + ADRs)     |
|     - /wayfinder (Map & child tickets on GitHub Issues)                     |
|     - /to-spec (Issue spec template)                                        |
|     - /to-tickets (Tracer-bullet sub-issues with native blocked_by)         |
|     - /implement (TDD) & /code-review (Two-axis subagent review)           |
|     - /handoff (Session compaction)                                         |
|                                                                             |
|  2. OPERATIONAL GAP-FILLERS (Off-the-shelf: gstack, global install)         |
|     - /ship & /land-and-deploy (Release verification, canary, PR)           |
|     - /careful (Destructive command guardrails)                             |
|     - /investigate (4-phase root cause debugging)                           |
|     - /retro (Weekly engineering retrospectives)                            |
|     - /qa & /design-review (Live site testing via gstack's browse daemon)   |
|                                                                             |
|  3. ORCHESTRATION & RUNBOOK (AAW: A single doc, NOT a software product)     |
|     - AGENTS.md (15-line workflow guide)                                    |
|     - docs/herdr-ops.md (Worker envelopes, worktrees, claims, attribution) |
+-----------------------------------------------------------------------------+
```

### 3. How the Pieces Fit Together

#### A. Planning in Context (Zero Planning Framework)
- **Foggy idea / epic:** Run `/wayfinder`. Creates a single GitHub issue labelled `wayfinder:map` with Destination, Decisions-so-far, and child decision tickets.
- **Sharpening a feature:** Run `/grill-me` or `/grill-with-docs`. Updates `CONTEXT.md` and `docs/adr/` directly.
- **Specification:** Run `/to-spec`. Synthesizes discussion into a published GitHub spec issue.
- **Decomposition:** Run `/to-tickets`. Generates tracer-bullet sub-issues linked to the parent issue with GitHub's native `blocked_by` dependencies (`[measured: docs/research/forge-dependencies.md#11-40]`).
- **No filesystem plans:** No `.advanced-plans/`, no `phases/`, no `loops.md`, no `plan-todos`. The tracker *is* the plan.

#### B. Effective Handoffs Between Sessions
- **Session boundary during planning:** Use `/handoff` (from Matt Pocock's suite) to compact conversation context into a clean markdown handoff.
- **Working state persistence:** Use gstack's `/context-save` and `/context-restore` to capture git state, uncommitted thoughts, and remaining work.
- **Macro state:** The GitHub Map issue's `## Decisions so far` section maintains a one-line gist and link for every closed ticket (`[quoted: .agents/skills/wayfinder/SKILL.md#40-44]`). Resuming a map simply means reloading the map issue and picking the next open ticket from the frontier.

#### C. Spawning and Managing Herdr Workers
In Herdr (v0.8.2), multi-worker dispatch is simple, fast, and tracker-native:

1. **Frontier Discovery:** The human operator or controller Claude session queries GitHub Issues:
   `gh issue list --state open` filtered by `issue_dependencies_summary.blocked_by == 0` and unassigned.
2. **Worktree Provisioning:** Herdr provisions an isolated git worktree:
   `git worktree add ../worktrees/ticket-104 -b feat/ticket-104`
3. **Dispatch with Envelope:** Herdr launches the designated worker CLI (e.g. `opencode`, `codex`, `cursor`, `agy`) in that worktree, injecting a standard envelope:
   ```markdown
   <ENVELOPE>
   Task: Implement Ticket #104 (Fix SQLite deadlock on concurrent writes)
   Acceptance Criteria: [quoted from issue body]
   Context: Read CONTEXT.md and docs/adr/0002-sqlite-concurrency.md
   Trailers:
     Co-Authored-By: opencode (Qwen) via herdr worker sqlite-fix
     Ticket: #104
   Workflow:
     1. Claim issue: gh issue edit 104 --add-assignee @me
     2. Implement test-first (/tdd)
     3. Run /code-review before finishing
     4. Commit on branch, do not push
     5. Close issue: gh issue close 104 --comment "Resolved in commit abc..."
   </ENVELOPE>
   ```
4. **Concurrency without Collisions:**
   - The worker runs `gh issue edit 104 --add-assignee @me` as its first action (`[quoted: docs/agents/issue-tracker.md#44]`). This atomically locks the ticket from other concurrent workers.
   - Closing the ticket upon completion automatically decrements `issue_dependencies_summary.blocked_by` for downstream child tickets in GitHub's native dependency graph (`[measured: docs/research/forge-dependencies.md#16-20]`), instantly expanding the frontier for the next worker.

#### D. Cross-Model Gate at Integration Points
- When a worker finishes a ticket or feature branch, it opens a PR.
- Before merging, the controller or human spawns a review worker running a **different model** (e.g. Codex or Cursor if implemented by Claude):
  `gh pr diff 12 | codex exec "Review this diff against the acceptance criteria of Ticket #104 and repo coding standards."`
- No `evidence_gate.py`, no custom JSON schema, no verdict file persistence. Standard PR review comments on GitHub.

---

## Section D: What to Stop Doing Now

Adopting this minimal architecture requires terminating existing over-engineered workstreams, closing dead tickets on the wayfinder map, and pruning dead files.

### 1. Tickets to Close on the Wayfinder Map (Issue #1)

| Issue # | Title | Recommended Action | Justification |
| :--- | :--- | :--- | :--- |
| **#1** | Map: AAW v0.3 as a Matt Pocock-first configurator | **CLOSE AS COMPLETED** | Close with the architectural resolution defined in this review report. |
| **#2** | Do native sub-issues and blocked_by work, what does GitLab offer | **CLOSE AS WONTFIX** | `[measured: docs/research/forge-dependencies.md#11-40]` confirmed GitHub native dependencies work. Designing abstract forge parity for GitLab is unneeded speculative complexity. |
| **#6** | Gate operating model: which model reviews, where verdict lives | **CLOSE AS WONTFIX** | Do not build a custom gate engine. Cross-model review is conducted via standard PR reviews in Herdr panes. |
| **#7** | Herdr worker operations on tracker: claim, attribution, race handling | **CLOSE AS COMPLETED** | Record the convention directly in `docs/herdr-ops.md` as described in Section C. |
| **#8** | Component manifest for v0.3: what installed.json lists | **CLOSE AS WONTFIX** | Drop `.aaw/installed.json` entirely. `skills-lock.json` is the sole standard lockfile. |
| **#9** | Prototype the /setup-aaw walkthrough as a stub SKILL.md | **CLOSE AS WONTFIX** | Delete `prototype/setup-aaw`. Do not build a wrapper skill for a one-line `npx skills add` command. |
| **#10**| Browser for /qa & /design-review: keep gstack or Playwright MCP | **CLOSE AS COMPLETED** | Decision: **Keep gstack's browser**. `[quoted: docs/research/native-browser-tooling.md#180-188]` proved rewriting on Playwright MCP is a 70–90% rewrite for worse performance. |

### 2. Files and Directories to Delete or Archive

1. **Delete `.advanced-plans/` (`143 files, 29,110 lines`)**:
   - The entire retired phase/loop/todo/gate engine. Archive to a cold historical branch (e.g. `archive/v0.2-advanced-plans`) or `docs/history/` and remove from `main`.
2. **Delete `.aaw/` (`3 files, 662 lines`)**:
   - Delete `detect.py`, `installed.schema.json`, `installed.example.json`.
3. **Delete `tools/` (`3 files, 623 lines`)**:
   - Delete `aaw-audit.py` and manifest validation tooling.
4. **Delete `tests/packaging/` (`tests/` holds 62 files, 5,411 lines)**:
   - Delete `test-audit.sh`, `test-idempotency.sh`, `test-fresh-clone.sh`, `test-hook-path.sh`, `validate-manifest.py`.
5. **Delete `.claude/skills/setup-with-claude/` (`787 lines`)**:
   - Obsolete; superseded by `npx skills add mattpocock/skills --all`.
6. **Delete `.claude/skills/gstack-to-plans/` (`91 lines`)**:
   - Obsolete; there is no `.advanced-plans/specs/` directory to copy design docs into.
7. **Prune Stale Branches**:
   - `feat/aaw-packaging-repair` (unmerged Phase 4 packaging branch)
   - `prototype/setup-aaw` (abandoned wrapper stub)
   - `research/forge-dependencies`, `research/gate-implementation`, `research/gstack-subset`, `research/native-browser-tooling`, `research/skills-cli` (all findings are merged into `docs/research/`).

### 3. Workstreams to Terminate Immediately
- **Stop writing manifest detectors and validators.** Do not maintain Python scripts that audit whether Markdown files exist.
- **Stop designing multi-runtime adapters for Advanced Planning.** (Phase 6 is dead; do not resurrect it).
- **Stop writing installation wizards.** Let package managers (`npx skills`) install packages.
- **Stop writing procedural routing fences.** Modern models read skill descriptions and domain context natively.

---

## Section E: Confidence and Blind Spots

### 1. Confidence Level
**High (95%).** The quantitative audit is based on exact repository measurements (line counts, file counts, commit hashes, byte sizes). The failure modes of the planning machinery are documented directly in git commit logs and gate verdict files in this checkout. Upstream CLI capabilities (`skills add --all`) were measured directly in test environments (`docs/research/skills-cli.md`).

### 2. What Was NOT Read (Blind Spots)
1. **Full contents of all 143 files in `.advanced-plans/`:** We read the index (`PLANS-INDEX.md`), sample phase plans, sample loops, gate verdicts (`phase-2`, `phase-4`, `phase-6`), and closeout records, but did not read all 29,110 lines of historical handoff logs.
2. **Live Herdr process orchestration:** We evaluated Herdr's documented conventions, worktree structures, commit trailers, and worker envelopes (`docs/worktree-ownership.md`, `docs/agents/worker-attribution.md`), but did not benchmark Herdr under a 10-worker concurrent load.
3. **GitLab Issues API:** We did not run live API tests against GitLab (`glab`), as this repository is hosted on GitHub.
4. **Proprietary source of all 50+ gstack skills:** We inspected the setup script, browse binary architecture, and core skills (`browse`, `qa`, `design-review`, `ship`, `careful`, `investigate`), but did not audit every individual gstack skill.

### 3. What Would Change This Assessment?
- **Enterprise Regulatory / Audit Compliance Requirements:** If the user were operating in a regulated medical, financial, or aerospace environment where every autonomous agent step must be cryptographically signed, hash-chained, and committed to git for offline audit immutability (which GitHub Issues comments cannot guarantee due to editability), an in-repo audit trail might be justified. However, even in that scenario, the solution would be a git-backed audit log, not an over-engineered Ralph Loop state bus.
- **Herdr Requiring Binary Plugin Manifests:** If a future version of Herdr required registered JSON manifests to discover tools, a manifest would be necessary. However, as `[quoted: issue #1 Notes]` measured on Herdr 0.8.2: *"no plugin API — 'herdr plugin' means a herdr-aware skill pack, nothing more"*.

---

## Section F: Addendum — Slimming Advanced-Planning and Collapsing the Stack

Per `ENVELOPE-addendum.md`, we extended our review to the owner's `advanced-planning` repository (`C:\Users\mharvey2\Coding\advanced-planning`, `[measured]` 261 commits on `main`, release `0.19.0` at commit `171d193`).

The owner's new stance is: *"with herdr (spawning, waiting on, and reading many agents) and today's models, the ralph loops are unnecessary. The aim is to guide agents almost silently: keep the general principles of advanced-planning, but slim the architecture into something small and portable."*

```
+-----------------------------------------------------------------------------------+
|                     ADVANCED-PLANNING PRINCIPLES SLIMMING MATRIX                  |
+------------------------------------+-----------------------+----------------------+
| Principle / Mechanism              | Status                | Action / Replacement |
+------------------------------------+-----------------------+----------------------+
| 3-field handoff summaries          | KEEP                  | Standard in AGENTS.md|
| Adversarial cross-model review     | KEEP                  | PR-level Herdr check |
| Verifiable outcome conditions      | KEEP                  | Issue accept criteria|
| Targeted skill injection           | KEEP                  | Standard skill loader|
| Ralph loops & todo schemas         | OBSOLETE              | GitHub Issue tickets |
| Filesystem state bus (JSON)        | OBSOLETE              | Herdr prompts + git  |
| Two-agent micro-split              | OBSOLETE              | Direct Herdr worker  |
| Sentinel write-blocking hooks      | OBSOLETE              | Git worktrees        |
| Versioned retry files (-v2.md)     | OBSOLETE              | Reopened issues      |
| Install ownership registries       | OBSOLETE              | npx skills lockfile  |
+------------------------------------+-----------------------+----------------------+
```

### F1. Principles Worth Keeping vs. Obsolete Compensation Mechanisms

#### A. Principles Worth Keeping (The Core Methodology)

1. **Three-Field Handoff Summaries (`done` / `failed` / `needed`)**:
   - *Primary Location:* `[quoted: core/schemas/handoff.schema.md#1-49]`, `[quoted: docs/concepts.md#27-49]`.
   - *Evidence & Justification:* Forcing session handoffs into three crisp sentences (`done`: artefact produced; `failed`: blockers/defects; `needed`: immediate next action) prevents context bloat. `[quoted: docs/concepts.md#35]` *"Forcing a summary into one sentence per field prevents context bloat. An agent that must summarise its work in one sentence is forced to prioritise the essential."* This principle is timeless and independent of model tier.
2. **Adversarial Verification / Cross-Model Quality Gates**:
   - *Primary Location:* `[quoted: docs/gate-review-architecture.md#1-50]`, `[quoted: docs/concepts.md#216-232]`.
   - *Evidence & Justification:* The principle that an authoring model must not be the sole judge of its own work. Single-model reviews suffer from confirmation bias and self-blindness. Having an independent model review a diff against explicit acceptance criteria with a high confidence threshold (≥80 confidence to block) catches real bugs.
3. **Observable Outcome Conditions on Every Task**:
   - *Primary Location:* `[quoted: core/schemas/todo.schema.md#15-25]`, `[quoted: README.md#19]`.
   - *Evidence & Justification:* Every work item must declare a verifiable completion condition (e.g. test command output, file creation, schema match), never a vague aspirational verb.
4. **Targeted Skill Injection (Ephemeral Context Hygiene)**:
   - *Primary Location:* `[quoted: docs/skill-injection.md#1-60]`, `[quoted: docs/concepts.md#52-73]`.
   - *Evidence & Justification:* Loading specialist instructions only when relevant and unloading them when the task finishes prevents instruction cross-contamination and context degradation.

#### B. Mechanisms That Only Compensated for Weaker Models or Lack of Herdr (Can GO)

1. **Ralph Loops and Micro-Todo Schemas (`core/schemas/ralph-loop.schema.md`, `todo.schema.md`)**:
   - *Why it can go:* Invented in early 2024 when Claude 3 Sonnet would hallucinate or derail after 5–10 steps without rigid YAML frontmatter constraints (`id`, `skill`, `agent`, `outcome`, `status`, `max_iterations: 3`, `on_max_iterations: rollback`). Modern models have 1M–2M context windows and maintain focus across extensive multi-file changes. Herdr dispatches workers against discrete vertical-slice tickets; internal micro-loops are redundant.
2. **The Filesystem State Bus (`loop-ready.json`, `loop-complete.json`, `history.jsonl`)**:
   - *Primary Location:* `[quoted: core/state/#1-53]`, `[quoted: platforms/python/state_manager.py#1-320]`.
   - *Why it can go:* Built because there was no process orchestrator or multi-window manager to coordinate agents. In Herdr, the controller spawns a worker CLI directly, feeds its prompt envelope via stdin or initial prompt, waits on the process, and inspects the resulting git branch upon exit. The JSON state bus files are unnecessary serialization overhead.
3. **The Two-Agent Micro-Split (Orchestrator vs. Worker)**:
   - *Primary Location:* `[quoted: core/agents/orchestrator.md]`, `[quoted: core/agents/worker.md]`.
   - *Why it can go:* `advanced-planning` itself had to build an "Orchestrator fast-path" in Phase 16 (`[quoted: CLAUDE.md#144-149]`) to skip spawning `ralph-orchestrator` because wasting ~30,000 tokens just to copy YAML todos into `loop-ready.json` was pure waste. Herdr handles worker dispatch directly.
4. **Sentinel-Based Write-Blocking Hooks (`planning-mode`, `gate-review-mode`)**:
   - *Primary Location:* `[quoted: platforms/claude-code/settings.json]`, `[quoted: docs/concepts.md#121-142]`.
   - *Why it can go:* Built to prevent a single Claude session from accidentally modifying source code while planning or gating. In Herdr, write isolation is enforced physically by Git worktrees (`git worktree add`). An agent in a scratch or read-only worktree cannot touch `main` regardless of what tools it calls.
5. **Versioned Retry Files (`phase-N-ralph-loops-v2.md`) & Compaction Manifests**:
   - *Primary Location:* `[quoted: platforms/python/versioning.py]`, `[quoted: docs/phase-complete.schema.md]`.
   - *Why it can go:* An elaborate mechanism to emulate a database of execution attempts in the filesystem. On GitHub Issues, an issue reopened with review comments or a new PR commit provides native history and audit trails.
6. **Installer Ownership Registries (`skill-ownership.json`, `install_audit.py`)**:
   - *Primary Location:* `[quoted: platforms/claude-code/install.sh]`, `[quoted: git log commits 7300f26, 462037b, 8571ac1]`.
   - *Why it can go:* Dozens of commits in `advanced-planning` were spent fixing uninstaller regressions where `skill-ownership.json` deleted too much or failed closed. The official `skills` CLI already manages installation and uninstallation deterministically via `skills-lock.json`.

---

### F2. The Smallest Portable Form of the Principles

The slimmed architecture consists of **exactly two files totaling ~120 lines**, requiring zero Python runtimes, zero JSON schemas, and zero platform adapters:

#### 1. The Global Agent Guide: `AGENTS.md` (Repo root, ~35 lines)
Portable across Claude Code, Codex, OpenCode, Cursor, Agy, and Pi.
```markdown
# Agent Instructions

## Principles
- **TDD & Seams**: Implement changes test-first at agreed architectural seams. Run existing test suite before claiming completion.
- **Observable Outcomes**: Every task must have a verifiable condition (passing test, verified command output, diff check).
- **Session Handoff Protocol**: When ending any session or handing off work, output exactly three sentences:
  - `Done`: [One sentence describing artefacts produced]
  - `Failed`: [One sentence describing errors, blockers, or failed assertions; empty if none]
  - `Needed`: [One sentence naming the immediate next action for the incoming agent]

## Context
- Read `CONTEXT.md` for domain glossary.
- Read `docs/adr/` before modifying architectural boundaries.

## Workflow Triggers
- Exploring / Scoping: `/grill-me` or `/wayfinder`
- Specification: `/to-spec` -> `/to-tickets`
- Execution: `/implement` (TDD) -> `/code-review`
- Release & QA: `/ship`, `/qa` (gstack)
```

#### 2. The Herdr Operations Guide: `docs/herdr-ops.md` (~85 lines)
Describes how human operators or controller sessions coordinate parallel workers:
```markdown
# Herdr Operations Guide

## 1. Ticket Frontier Query
Controller or human inspects open, unblocked, unassigned tickets:
```bash
gh issue list --state open --json number,title,assignees,issue_dependencies_summary \
  --jq '[.[] | select((.assignees | length == 0) and (.issue_dependencies_summary.blocked_by == 0))]'
```

## 2. Worktree Provisioning
Create dedicated worktree for the ticket:
```bash
git worktree add ../worktrees/ticket-<n> -b feat/ticket-<n>
```

## 3. Worker Dispatch Envelope
Prompt the worker in Herdr pane with:
- Task: Issue title, body, and acceptance criteria.
- Context: Pointers to `CONTEXT.md` and relevant ADRs.
- Commit Trailers:
  `Co-Authored-By: <provider> via herdr worker <name>`
  `Ticket: #<n>`
- Protocol:
  1. Claim issue: `gh issue edit <n> --add-assignee @me`
  2. Implement test-first
  3. Run `/code-review`
  4. Emit 3-field handoff (`Done`, `Failed`, `Needed`) in final output
  5. Close issue on completion

## 4. Integration & Cross-Model Gate
1. Worker pushes branch and opens PR.
2. Independent model (different from implementer) runs PR review:
   `gh pr diff <pr> | codex exec "Review against ticket #<n> criteria and AGENTS.md"`
3. If review passes: merge and prune worktree.
```

---

### F3. How the Slim Form Guides Agents "Silently"

This slim architecture achieves "silent guidance" through natural runtime discovery rather than procedural commands:

1. **What an agent reads without being told:**
   - **Automated Root Context:** Every major coding CLI (Claude Code, Cursor, Codex, OpenCode, Agy) automatically reads `AGENTS.md` and/or `CLAUDE.md` from the project root at startup.
   - The agent ingests the 3-field handoff protocol, the domain glossary rules, and the TDD requirements before processing the user's first prompt.
   - When a worker is launched in a Herdr worktree, its dispatch envelope provides the exact scope, trailers, and task boundaries directly in its prompt.
2. **What a human never has to invoke:**
   - The human never invokes `/new-phase`, `/next-loop`, `/plan-todos`, `/plan-skill-identification`, `/plan-subagent-identification`, `/run-gate`, `/next-phase`, `/phase-compact`, `/sync-plans`, or `/check-execution`.
   - The human never reviews or troubleshoots JSON state files (`loop-ready.json`), never debugs failed schema validations, and never manages sentinel lock files.
   - The human simply monitors Herdr terminal panes, reads the 3-sentence handoff summaries, and clicks "Merge" on PRs that pass automated CI and cross-model code review.

---

### F4. Recommendation: Collapse AAW and Advanced-Planning into ONE Thing

**Recommendation: AAW and advanced-planning should COLLAPSE into a single repository.**

Keeping them separate is an accident of history:
- `advanced-planning` was built as a standalone phase/loop/todo engine for Claude Code.
- `Advanced-AI-Workflows` was created as the "meta-repo" to glue `advanced-planning`, `gstack`, and `superpowers` together.
- In practice, as demonstrated by the git logs of both repos, the two projects became locked in mutual maintenance: AAW spent Phase 4 syncing gstack and repairing packaging for AP, Phase 6 writing multi-runtime adapters for AP, and Phase 5 porting superpowers for AP.
- Meanwhile, `advanced-planning` spent releases `0.12.0` through `0.19.0` trying to adapt its internal Ralph Loops to Herdr runtimes (Codex, OpenCode), fighting uninstall registries, and managing adapter duplication.

Once Ralph Loops, JSON state buses, packaging sentinels, and custom installers are discarded:
- There is **no planning engine** left in `advanced-planning` to justify a separate framework repository.
- There is **no glue code** left in `Advanced-AI-Workflows` to justify a separate meta-repo.
- **They are the same thing**: a lightweight, Herdr-centric multi-agent operational standard.

**Action Plan:**
1. **Archive `advanced-planning`**: Tag the repository at `v0.19.0`, mark it archived/read-only, and state in its README that it has been succeeded by the Herdr-native operational standard.
2. **Transform this repository (`Advanced-AI-Workflows`)**:
   - Delete `.advanced-plans/`, `.aaw/`, `tools/`, and old installer skills.
   - Adopt the minimal 2-file architecture: `AGENTS.md` + `docs/herdr-ops.md`.
   - Keep `skills-lock.json` pinning Matt Pocock's skills and gstack.
   - This turns AAW from an over-engineered software framework into a lean, elegant, battle-tested operational template for multi-agent software engineering.

---

## Decision Summary Table

| Question Asked | Finding | Recommended Action |
| :--- | :--- | :--- |
| **Is AAW worth its weight?** | No. 78% of commits and 66% of lines are planning scaffolding for 878 lines of glue. | Retire the planning framework entirely. |
| **Is the v0.3 direction still too much?** | Yes. The 5 AAW additions attempt to keep AAW alive as a meta-framework. | Drop manifest & setup wrapper; reduce gate, attribution, and routing to doc lines. |
| **What is the simplest architecture?** | Matt Pocock spine + gstack execution + Herdr worktrees + 15-line `AGENTS.md` guide. | Delete `.advanced-plans/`, `.aaw/`, `tools/`, and installer skills. |
| **Are Ralph loops still necessary?** | No. Models and Herdr have moved on. Micro-loops and state buses are pure overhead. | Discard Ralph loops; use GitHub Issues tracer bullets. |
| **Which AP principles survive?** | 3-field handoffs, adversarial cross-model review, observable outcomes, targeted skill injection. | Embed in `AGENTS.md` and `docs/herdr-ops.md`. |
| **Should AAW and AP remain separate?** | No. Keeping both maintains duplicate scaffolding for a problem already solved. | Collapse both into one lightweight runbook repository. |
