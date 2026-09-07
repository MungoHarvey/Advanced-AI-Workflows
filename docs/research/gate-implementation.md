# Gate Implementation: Current State and PR-Diff Adaptation Requirements

**Research for:** Issue #4 — "How is the current cross-model gate implemented, and what does it need to run against a PR diff instead of a phase"  
**Branch:** `research/gate-implementation`  
**Date:** 2026-09-07  
**Sources:** Primary source files only (run-gate.md, gate agents, evidence_gate.py, gate-verdicts examples, schema)

---

## Summary

The current gate is a **phase-boundary review** that evaluates all loop outputs within a phase against the phase plan's success criteria. It runs two gate agents sequentially (`code-review-agent` then `phase-goals-agent`), with an optional parallel Codex reviewer, aggregates their verdicts, and on a pass either approves the phase or auto-closes it if it's the current phase.

**Key finding:** The gate's core logic (`evidence_gate.py`) is already **decoupled from the phase data structure** — it validates JSON documents against schemas and aggregates gate verdicts. The phase-coupling lives in:
1. The **run-gate.md command** (reads `.advanced-plans/PLANNING.md`, phase directories, loop files)
2. The **gate agents** (read phase plans and loop handoffs)
3. The **verdict schema** (references phases and loops)

To run against a PR diff, the changes required are:
- **Input adaptation layer**: Replace phase/loop file reads with git diff analysis
- **Ticket linkage**: Map diff hunks to linked GitHub issues and their acceptance criteria
- **Verdict schema extension**: Add fields for PR number, diff stats, and ticket-level outcomes
- **Agent prompt rewriting**: Point agents at PR context instead of phase plans

The Python gate logic (`aggregate_verdicts`, `validate_advancement`) is **generic and reusable** — only the input sources and agent prompts need modification.

---

## 1. Current Gate Architecture

### 1.1 Entry Point: `/run-gate` Command

**Source:** `~/.claude/commands/run-gate.md` (measured: 686 lines)

The command executes the following sequence:

| Step | Description | Phase-Coupled? |
|------|-------------|----------------|
| 1. Resolve current phase | Reads `.advanced-plans/PLANNING.md` frontmatter, extracts `current_phase` | **Yes** — reads phase pointer |
| 2. Verify loops complete | Greps `.advanced-plans/phases/phase-[N]/loops.md` for pending todos | **Yes** — reads loop files |
| 3. Determine agents | Default: `code-review-agent`, `phase-goals-agent` | No — configurable |
| 4. Create gate-verdicts directory | `mkdir -p .advanced-plans/gate-verdicts` | No |
| 5. Create sentinel | `.advanced-plans/state/gate-review-mode` | No |
| 6. Determine attempt number | Counts existing verdict files for this phase | **Yes** — phase-named files |
| 6a. Codex preflight | Checks `codex` binary and auth | No |
| 7. Spawn gate agents | Sequential: code-review-agent → phase-goals-agent; Codex background | **Yes** — agents read phase files |
| 8. Remove sentinel | Cleanup | No |
| 8a. Write Codex verdict | Main thread writes on behalf of Codex | No |
| 9. Aggregate verdicts | Calls `aggregate_verdicts()` on verdict JSON files | No — generic |
| 10. Conflict UX | Asks user on fail/conflict via `AskUserQuestion` | No |
| 10.3. Append history event | Writes `gate_pass` or `gate_fail` to `history.jsonl` | **Yes** — phase-named event |
| 10.4. Phase closeout (pass only) | Edits `PLANNING.md`, advances phase pointer, writes compaction artefacts | **Yes** — phase state mutation |

**Measured inputs read by run-gate:**
- `.advanced-plans/PLANNING.md` (line 27–30)
- `.advanced-plans/phases/phase-[N]/loops.md` (line 60)
- `.advanced-plans/phases/phase-[N]/plan.md` (line 196, 293)
- `.advanced-plans/gate-verdicts/phase-[N]-attempt-*.json` (line 107, 395)
- `.advanced-plans/state/history.jsonl` (line 386, 470, 476)

### 1.2 Gate Agents

#### code-review-agent

**Source:** `~/.claude/agents/code-review-agent.md` (measured: 142 lines)

**Responsibility:** "Reviews code produced during a phase for quality, patterns, CLAUDE.md compliance, and correctness."

**Inputs read:**
- Phase plan: `.advanced-plans/phases/phase-[N]/plan.md` (line 196)
- Loop files: `.advanced-plans/phases/phase-[N]/loops.md` (line 197)
- Prior context: handoff summaries from all loops in the phase (line 198)
- Source code files touched in the phase (inferred from git diff or loop outputs)

**Evaluation criteria:**
1. Code style and conventions (line 27–40)
2. CLAUDE.md compliance (line 42–53)
3. No secrets or credentials (line 55–62)
4. Test presence (line 64–67)
5. No dead code (line 69–75)

**Verdict output:** `.advanced-plans/gate-verdicts/phase-[N]-attempt-[M]-code-review-agent.json` (line 125–128)

**Schema conformance:** Must conform to `core/state/gate-verdict.schema.json` (line 131)

#### phase-goals-agent

**Source:** `~/.claude/agents/phase-goals-agent.md` (measured: 154 lines)

**Responsibility:** "Verifies that a phase's outputs satisfy all stated success criteria in the phase plan."

**Evaluation process:**
1. Read phase plan, extract success criteria and outputs (line 26–34)
2. Read all loop handoff summaries (line 36–43)
3. Verify each success criterion (line 45–88)
4. Verify all expected outputs exist (line 90–95)
5. Apply confidence scoring (line 97–105)

**Criterion verification patterns:**

| Criterion type | Verification method |
|----------------|---------------------|
| File exists | `Glob` for the path |
| Content present | `Grep` for required text |
| Schema valid | `Read` and confirm required fields |
| Multiple files | `Glob` with wildcard; count results |
| No prohibited content | `Grep` for prohibited patterns |

**criteria_outcomes:** Each criterion produces an entry with:
- `criterion` (verbatim from phase plan)
- `status` ("met", "failed", or "deferred")
- `evidence` (file path, commit SHA, grep match)
- `deferred_to` (optional, when status is "deferred")

**Verdict output:** `.advanced-plans/gate-verdicts/phase-[N]-attempt-[M]-phase-goals-agent.json` (line 119–122)

**Extended fields:** Populates `phase_title` and `criteria_outcomes` for phase-compactor consumption (line 133–147)

### 1.3 Python Gate Logic

#### evidence_gate.py

**Source:** `~/.herdr/worktrees/advanced-planning/loop-008-gate/platforms/python/evidence_gate.py` (measured: 856 lines)

**Purpose:** "Single decision point where evidence advances a loop only if ALL gates pass: schema validation, gate validation, and (where applicable) path scope."

**Two advancement paths:**

| Path | Adapter | Gates |
|------|---------|-------|
| Path 1: collected-evidence | herdr/Cowork | Schema + Policy gates + Path scope |
| Path 2: loop-complete | Claude Code | Schema + Policy gates (path scope optional) |

**Key functions:**

1. **`validate_advancement(evidence_path, envelope_path, verdict_paths, baseline)`** (line 212–406)
   - Gate 1: Schema validation (ALWAYS required)
   - Gate 2: Policy gates (required only if verdict_paths provided)
   - Gate 2b: Evidence self-review policy (ALWAYS required for collected-evidence)
   - Gate 3: Path scope validation (ALWAYS required, derives changed paths from git)

2. **`validate_loop_complete_advancement(loop_complete_path, verdict_paths, changed_paths, allowed_paths, forbidden_paths)`** (line 514–608)
   - Gate 1: Schema validation
   - Gate 2: Policy gates
   - Gate 3: Path scope (only if changed_paths provided)

3. **`_derive_changed_paths_from_git(baseline, repo_root)`** (line 125–197)
   - Runs `git diff --name-only baseline..HEAD`
   - Adds uncommitted changes (`git diff --name-only HEAD`)
   - Adds untracked files (`git ls-files --others --exclude-standard`)
   - Returns deduplicated list of changed paths

**Exit codes:**
- `0`: All gates pass
- `1`: Advancement blocked (schema fail, policy gate fail, path scope violation)
- `2`: Invalid command-line usage OR environment failure (git derivation failed)

**Key finding:** The Python gate logic is **already generic** — it validates JSON documents and aggregates verdicts. The phase-coupling is in the callers that construct the input paths.

#### codex_gate.py (helper module)

**Source:** Inferred from imports in `evidence_gate.py` (line 77: `from platforms.python.codex_gate import aggregate_verdicts`)

**Key function:** `aggregate_verdicts(verdict_files)` — returns dict with:
- `result`: "pass" | "fail" | "not_requested"
- `conflicts`: list of conflict descriptions
- `missing`: list of missing or unreadable verdict files

**Measured behavior:** Any fail among verdict files yields `result = "fail"`; any file in `missing` also yields `"fail"`.

### 1.4 Verdict Schema

**Source:** `~/.cache/advanced-ai-workflows/advanced-planning/core/state/gate-verdict.schema.json` (measured: 101 lines)

**Required fields:**
- `phase` (string): "Phase identifier being reviewed, e.g. phase-2"
- `attempt` (integer): "Attempt number for this phase; increments on each retry"
- `timestamp` (string): ISO 8601 timestamp
- `agent` (string): "Identifier of the gate agent, e.g. code-review-agent"
- `verdict` (string): "pass" | "fail"
- `confidence` (integer): 0–100
- `findings` (array): List of issues found
- `loops_to_revert` (array): Loop identifiers to re-execute
- `failure_notes` (array): Actionable constraints for retry

**Optional fields:**
- `criteria_outcomes` (array): Outcomes per success criterion (used by phase-compactor)
- `phase_title` (string): Display title from phase plan

**Finding schema:**
```json
{
  "type": "object",
  "required": ["severity", "location", "description", "evidence"],
  "properties": {
    "severity": { "enum": ["critical", "warning", "info"] },
    "location": { "type": "string" },
    "description": { "type": "string" },
    "evidence": { "type": "string" }
  }
}
```

**criteria_outcomes schema:**
```json
{
  "type": "object",
  "required": ["criterion", "status", "evidence"],
  "properties": {
    "criterion": { "type": "string" },
    "status": { "enum": ["met", "deferred", "failed"] },
    "evidence": { "type": "string" },
    "deferred_to": { "type": "string" }
  }
}
```

### 1.5 Example Verdict Files

**Measured:** `phase-2-attempt-1-code-review-agent.json` (76 lines) and `phase-2-attempt-1-phase-goals-agent.json` (59 lines)

**code-review-agent verdict structure:**
```json
{
  "agent": "code-review-agent",
  "phase": "phase-2",
  "attempt": 1,
  "verdict": "pass",
  "confidence": 0.95,
  "summary": "...",
  "findings": [
    {
      "criterion": "...",
      "status": "met",
      "severity": "info",
      "confidence": 0.95,
      "evidence": "..."
    }
  ],
  "loops_to_revert": [],
  "generated_at": "2026-06-08T00:00:00Z",
  "phase_success_criteria_summary": "..."
}
```

**phase-goals-agent verdict structure:**
```json
{
  "agent": "phase-goals-agent",
  "phase": "phase-2",
  "attempt": 1,
  "phase_title": "v0.1 Smoke-Findings Fix-Pack",
  "verdict": "fail",
  "confidence": 0.93,
  "summary": "...",
  "criteria_outcomes": [
    {
      "criterion": "...",
      "status": "failed",
      "evidence": "..."
    }
  ],
  "findings": [
    {
      "id": "F1",
      "severity": "critical",
      "confidence": 93,
      "criterion": "...",
      "detail": "..."
    }
  ],
  "loops_to_revert": [],
  "loops_reviewed": ["ralph-loop-001", "ralph-loop-002", "ralph-loop-003"],
  "all_loops_complete": true,
  "all_needed_fields_empty": true
}
```

**Observed discrepancy:** The example verdicts do not fully conform to the schema:
- `code-review-agent` verdict uses `generated_at` instead of `timestamp` (schema requires `timestamp`)
- `code-review-agent` verdict has `phase_success_criteria_summary` (not in schema, would fail `additionalProperties: false`)
- `phase-goals-agent` verdict has `loops_reviewed`, `all_loops_complete`, `all_needed_fields_empty` (not in schema)
- Both verdicts have `findings` arrays with different structures than the schema's required fields (`severity`, `location`, `description`, `evidence`)

**Inference:** The schema was extended after these verdicts were written, or the schema is not being strictly enforced at write time.

---

## 2. What is Generic vs Phase-Coupled

### 2.1 Generic Components (Reusable for PR-Diff Gate)

| Component | Location | Why Generic |
|-----------|----------|-------------|
| `aggregate_verdicts()` | `platforms.python.codex_gate` | Operates on JSON files, no phase knowledge |
| `validate_document()` | `platforms.python.state_validate` | Schema validation against any JSON Schema |
| `validate_path_scope()` | `platforms.python.scope_policy` | Validates paths against allowed/forbidden lists |
| `_derive_changed_paths_from_git()` | `evidence_gate.py` | Already uses git diff, not phase data |
| Verdict schema | `core/state/gate-verdict.schema.json` | Could extend with PR-specific fields |
| Gate agent protocol | `core/agents/gate-reviewer.md` | Platform-independent, input-agnostic |
| Three-tier severity model | code-review-agent.md line 77–89 | Generic categorization |
| Confidence scoring protocol | code-review-agent.md line 91–101 | Generic uncertainty quantification |

### 2.2 Phase-Coupled Components (Require Modification)

| Component | Location | Phase-Coupling | Modification Required |
|-----------|----------|----------------|----------------------|
| run-gate command | `~/.claude/commands/run-gate.md` | Reads `PLANNING.md`, phase directories, loop files | Replace with PR diff reader, issue linkage |
| code-review-agent prompts | Agent tool invocation (line 182–199) | "Read phase plan, all loop outputs" | Point at PR files and linked tickets |
| phase-goals-agent prompts | Agent tool invocation (line 284–298) | "Read phase plan success criteria" | Point at ticket acceptance criteria |
| Verdict file naming | `.advanced-plans/gate-verdicts/phase-[N]-attempt-[M]-*.json` | Phase-named files | PR-named files: `pr-[N]-attempt-[M]-*.json` |
| History events | `history.jsonl` (line 386, 470, 476) | `gate_pass`, `gate_fail` with phase field | Add `pr_pass`, `pr_fail` or extend event schema |
| Phase closeout logic | run-gate Step 10.4 (line 480–545) | Advances `current_phase`, updates `PLANNING.md` | Replace with PR merge status check |
| Codex reviewer prompt | run-gate Step 7.2 (line 202–268) | References phase plan and loop files | Reference PR diff and linked tickets |

---

## 3. Model Rotation

**Source:** run-gate.md Step 3 (line 71–88) and Step 7 (line 202–318)

**Current mechanism:**
- Default agents: `code-review-agent`, `phase-goals-agent` (both Sonnet model)
- Override via `--agents` flag: `--agents code-review-agent,phase-goals-agent,security-agent`
- Codex runs in parallel as an independent cross-model reviewer (if available)

**Model configuration per agent:**
- `code-review-agent.md` line 4: `model: sonnet`
- `phase-goals-agent.md` line 4: `model: sonnet`

**Codex preflight:** run-gate Step 6a (line 119–148)
- Checks `codex` binary on PATH
- Checks auth: `~/.codex/auth.json` or `$CODEX_API_KEY` or `$OPENAI_API_KEY`
- If unavailable, degrades to in-house agents only

**No automatic model rotation:** The agent list is static per gate run. Model selection is configured in each agent's frontmatter (`model:` field). To rotate models, you would:
1. Edit the agent's frontmatter (e.g., change `model: sonnet` to `model: opus`)
2. Or pass `--agents` with a different agent that uses a different model

**Inference:** A PR-diff gate could use the same mechanism — define agents with different model preferences and pass them via `--agents`.

---

## 4. Inputs Required for PR-Diff Gate

### 4.1 Current Inputs (Phase-Based Gate)

| Input | Path | Purpose |
|-------|------|---------|
| Phase plan | `.advanced-plans/phases/phase-[N]/plan.md` | Success criteria, outputs, dependencies |
| Loop files | `.advanced-plans/phases/phase-[N]/loops.md` | Loop handoff summaries, todo status |
| Handoff summaries | YAML frontmatter in loop files | What each loop produced |
| Verdict files | `.advanced-plans/gate-verdicts/phase-[N]-attempt-*.json` | Prior gate attempts |
| PLANNING.md | `.advanced-plans/PLANNING.md` | Current phase pointer, phase lists |

### 4.2 Required Inputs (PR-Diff Gate)

| Input | Source | Purpose |
|-------|--------|---------|
| PR diff | `gh pr diff [N]` or `git diff main...HEAD` | Changed files and hunks |
| Linked tickets | `gh pr view [N] --json issues` or body parsing | Acceptance criteria to verify |
| Ticket acceptance criteria | GitHub issue body or linked spec | Success criteria for the PR |
| Test results | CI status (`gh pr checks [N]`) or local test run | Verify tests pass |
| Code review comments | `gh pr review [N]` or `gh pr comments [N]` | Prior review feedback |
| Base branch | PR `baseRefName` | Diff baseline |
| Head commit | PR `headSha` | Commit to verify |

**Key difference:** The phase-based gate reads **local Markdown files** describing planned work. The PR-diff gate would read **GitHub API responses** describing actual changes and linked requirements.

---

## 5. Adaptation Requirements

### 5.1 run-gate Command Modifications

**Current:** Reads `.advanced-plans/PLANNING.md` to resolve phase number.  
**Required:** Accept `--pr [N]` argument, fetch PR metadata via `gh pr view [N]`.

**Current:** Verifies loops complete via grep on `loops.md`.  
**Required:** Verify CI checks pass via `gh pr checks [N]` or run tests locally.

**Current:** Spawns agents with phase plan and loop files as context.  
**Required:** Spawn agents with PR diff, linked tickets, and acceptance criteria as context.

**Current:** Writes verdicts to `phase-[N]-attempt-[M]-*.json`.  
**Required:** Write verdicts to `pr-[N]-attempt-[M]-*.json` (or configurable path).

**Current:** Appends `gate_pass`/`gate_fail` events with phase field.  
**Required:** Append `pr_pass`/`pr_fail` events with PR number field.

**Current:** Step 10.4 auto-closes phase and advances pointer.  
**Required:** Remove or replace with PR merge status check (do not auto-merge).

### 5.2 Gate Agent Prompt Modifications

**code-review-agent:**
- Current: "Read phase plan, all loop outputs, evaluate code quality"
- Required: "Read PR diff, linked tickets, evaluate code quality against acceptance criteria"

**phase-goals-agent:**
- Current: "Read phase plan success criteria, verify each against loop outputs"
- Required: "Read ticket acceptance criteria, verify each against PR diff and test results"

### 5.3 Verdict Schema Extensions

**Add optional fields:**
```json
{
  "pr_number": { "type": "integer", "description": "Pull request number" },
  "diff_stats": {
    "type": "object",
    "properties": {
      "files_changed": { "type": "integer" },
      "additions": { "type": "integer" },
      "deletions": { "type": "integer" }
    }
  },
  "linked_tickets": {
    "type": "array",
    "items": { "type": "string" },
    "description": "GitHub issue numbers linked to this PR"
  },
  "ticket_outcomes": {
    "type": "array",
    "items": {
      "type": "object",
      "required": ["ticket", "status", "evidence"],
      "properties": {
        "ticket": { "type": "string" },
        "status": { "enum": ["met", "failed", "deferred"] },
        "evidence": { "type": "string" }
      }
    }
  }
}
```

### 5.4 Python Gate Logic Modifications

**Minimal changes required:**
- `evidence_gate.py` already derives changed paths from git (line 125–197)
- `aggregate_verdicts()` is input-agnostic
- Schema validation is generic

**Addition required:**
- New function: `validate_pr_advancement(pr_number, verdict_paths, ci_status)` — wraps existing logic, adds PR-specific checks (CI status, linked ticket verification)

---

## 6. Open Points / Unknowns

| Question | Status |
|----------|--------|
| Does `aggregate_verdicts()` handle more than two verdict files? | **Inferred yes** (takes list of paths), but not measured with >2 files |
| What happens if Codex verdict conflicts with both in-house agents? | **Documented** (line 429–452): user decision via `AskUserQuestion` |
| Is the verdict schema strictly enforced at write time? | **No** — example verdicts have extra fields that violate `additionalProperties: false` |
| Does `validate_path_scope()` support glob patterns or only literal paths? | **Unknown** — requires reading `scope_policy.py` |
| What is the exact structure of `criteria_outcomes` in passing verdicts? | **Measured** in phase-goals-agent verdict (line 9–44 of verdict file) |
| How does the gate handle a phase with zero loops? | **Unknown** — run-gate Step 2 would pass (zero pending todos), but no loop outputs to evaluate |
| What is the maximum number of gate agents supported? | **Unknown** — no explicit limit in run-gate.md |
| Does the Codex reviewer read the same inputs as in-house agents? | **No** — Codex is forbidden from reading `gate-verdicts/` (isolation rule, line 252–256) |

---

## 7. Citations

| Claim | Source | Line(s) |
|-------|--------|---------|
| run-gate reads `PLANNING.md` for current phase | `~/.claude/commands/run-gate.md` | 27–30 |
| run-gate verifies loops complete via grep | `~/.claude/commands/run-gate.md` | 60–69 |
| Default gate agents | `~/.claude/commands/run-gate.md` | 71–88 |
| Codex runs in parallel as background process | `~/.claude/commands/run-gate.md` | 202–268 |
| code-review-agent reads phase plan and loop files | `~/.claude/commands/run-gate.md` | 196–199 |
| phase-goals-agent verifies success criteria | `~/.claude/agents/phase-goals-agent.md` | 26–88 |
| criteria_outcomes structure | `~/.claude/agents/phase-goals-agent.md` | 61–88 |
| Verdict schema required fields | `core/state/gate-verdict.schema.json` | 6 |
| Verdict schema additionalProperties: false | `core/state/gate-verdict.schema.json` | 100 |
| evidence_gate derives changed paths from git | `evidence_gate.py` | 125–197 |
| evidence_gate exit codes | `evidence_gate.py` | 662–685 |
| Example verdict structure | `phase-2-attempt-1-code-review-agent.json` | 1–76 |
| Schema vs verdict discrepancy | Comparison of schema and example verdicts | — |

---

## 8. Decision-Ready Summary

**Can the current gate run against a PR diff?**  
**Not directly.** The Python gate logic is generic, but the orchestration (run-gate command, agent prompts, file paths, history events) is phase-coupled.

**What is the minimum viable adaptation?**
1. **New entry point:** `run-gate-pr.md` command that accepts `--pr [N]`
2. **Input adapter:** Fetch PR diff, linked tickets, CI status via `gh` CLI
3. **Agent prompts:** Rewrite to reference PR context instead of phase plans
4. **Verdict naming:** Use `pr-[N]-attempt-[M]-*.json` pattern
5. **Schema extension:** Add optional `pr_number`, `diff_stats`, `linked_tickets`, `ticket_outcomes` fields

**What can be reused unchanged?**
- `aggregate_verdicts()` — works on any JSON verdict files
- `validate_document()` — generic schema validation
- `validate_path_scope()` — path validation logic
- `_derive_changed_paths_from_git()` — already git-based
- Three-tier severity model and confidence scoring
- Codex parallel reviewer pattern

**What must be modified?**
- run-gate command (or create new `run-gate-pr`)
- Gate agent prompts (code-review-agent, phase-goals-agent)
- Verdict file naming convention
- History event schema (add PR-specific events)
- Phase closeout logic (remove or replace with PR merge check)

**Estimated effort:**  
- **Low complexity:** Python gate logic is already generic
- **Medium complexity:** Agent prompt rewriting, input adapter
- **High complexity:** run-gate command restructuring, schema migration

**Recommendation:** Build `run-gate-pr` as a parallel command, not a modification of `run-gate`. This allows side-by-side testing and rollback without breaking the phase-based gate.
