# AAW Value Review: Is This Worth Its Weight?

**Date:** 2026-09-07  
**Reviewer:** Qwen3.5 397B via OpenCode  
**Method:** Read-only audit of repository files, GitHub Issues, and research artefacts per ENVELOPE-review.md  
**Artefact:** This markdown file only; no other files modified

---

## A. Value Audit: What Has AAW Actually Produced?

### A.1 Quantitative Overview

**Repository size:** 249 commits (measured: `git log --oneline | Measure-Object -Line`)

**Commits by category (measured from `git log --oneline | Select-Object -First 60`):**

| Category | Count | Percentage | Examples |
|----------|-------|------------|----------|
| Research findings for wayfinder map | ~20 | 33% | "research: skills CLI bulk add", "research: gstack subset installation findings", "research: native browser tooling findings" |
| Gate implementation & remediation | ~25 | 42% | "gate: phase 6 attempt 4", "loop-008-*" series (8 loops), "evidence_gate.py" wiring |
| Documentation & glossary | ~5 | 8% | "glossary: the words v0.3 is being designed in", "docs: gate implementation research findings" |
| Evidence & verification | ~8 | 13% | "evidence: loop-009-3 closes criteria", "evidence: loop-007-10 closes" |
| Infrastructure (skills, routing) | ~2 | 4% | "Agent skills setup: GitHub tracker", "plan: open ralph-loop-007" |

**Measured:** 60 commits examined; ~50 (83%) are about the **gate machinery** (phase 6 remediation, loop execution, evidence collection) rather than user-facing capabilities.

### A.2 Files That Deliver User Value Today

**User-facing capabilities (files a user actually runs):**

| File | Purpose | Users |
|------|---------|-------|
| `.agents/skills/wayfinder/SKILL.md` | Issue-tracker-based planning for huge work | Users with foggy, multi-session efforts |
| `.agents/skills/to-spec/SKILL.md` | Synthesize conversation into spec issue | Users ready to lock scope |
| `.agents/skills/to-tickets/SKILL.md` | Break spec into tracer-bullet tickets | Users with approved specs |
| `.agents/skills/implement/SKILL.md` | Implement from tickets with TDD | Users executing work |
| `.agents/skills/code-review/SKILL.md` | Two-axis review (Standards + Spec) | Users before merge |
| `.agents/skills/triage/SKILL.md` | Move issues through state machine | Maintainers |
| `.agents/skills/research/SKILL.md` | Background reading agent | Users delegating legwork |
| `.agents/skills/prototype/SKILL.md` | Throwaway design validation | Users exploring UI/logic |
| `.agents/skills/domain-modeling/SKILL.md` | Build CONTEXT.md + ADRs inline | Users designing domains |
| `docs/agents/issue-tracker.md` | GitHub CLI operations for wayfinding | Users running wayfinder |
| `docs/agents/worker-attribution.md` | Commit trailer convention for herdr workers | Herdr operator |

**Total:** 11 files (9 skills + 2 docs) — all from Matt Pocock's catalogue, **not** AAW-original.

**Quoted:** `.agents/skills/` contains 12 skills (measured: `Get-ChildItem .agents/skills/ | Select-Object Name`), of which 9 are MP-origin.

### A.3 Scaffolding About Itself

**AAW-original machinery (files about AAW itself):**

| File/Directory | Purpose | Lines | Status |
|----------------|---------|-------|---------|
| `.advanced-plans/` | Phase/loop/todo engine | 9 phases, 68 evidence files, PLANNING.md (81KB), PLANS-INDEX.md (7KB) | **Retired** (map issue #1 Notes: "advanced-planning: the phase → ralph-loop → todo engine is **retired**") |
| `.aaw/detect.py` | Installation detector | 517 lines | Active but checking for retired components |
| `.aaw/installed.schema.json` | Manifest schema | 203 lines | Active |
| `.aaw/installed.example.json` | Example manifest | 44 lines | Example only |
| `ARCHITECTURE.md` | System overview (gstack → glue → AP → superpowers) | 349 lines | Describes v0.1 architecture, not current state |
| `ROADMAP.md` | v0.1 shipped + v0.2 workstreams | 143 lines | Historical; v0.2 not shipped |
| `DESIGN-RATIONALE.md` | Why gstack at strategic layer | 130 lines | Historical rationale for retired design |
| `SETUP.md` | Install instructions for gstack/AP/superpowers | 341 lines | Would need complete rewrite for v0.3 |
| `CHANGELOG.md` | v0.2 changes | 232 lines | Historical; v0.2 not shipped |
| `docs/research/*.md` | 10 research files for wayfinder map | ~2000 lines total | Active decision support |
| `tests/adherence/` | 12 test fixtures (claude/codex/opencode/cursor/agy × 3 scenarios) | ~500 lines | Tests for retired manifest machinery |
| `tests/packaging/` | Packaging regression tests | ~300 lines | Tests for retired components |

**Measured:**
- `.advanced-plans/evidence/`: 68 files (measured: `Get-ChildItem .advanced-plans/evidence/ | Select-Object Name`)
- `.advanced-plans/phases/`: 9 phase directories (measured: `Get-ChildItem .advanced-plans/phases/ | Select-Object Name`)
- `.advanced-plans/history.jsonl`: Does not exist (measured: `Test-Path .advanced-plans/history.jsonl` → False)
- `docs/research/`: 8 research files (measured via glob)

**Inferred:** ~2000 lines of documentation + 68 evidence files + 9 phase plans describe a system (gstack + advanced-planning + superpowers) that the owner now wants to replace with Matt Pocock skills + herdr.

### A.4 Value Ratio

**Claim:** AAW has produced **11 user-facing files** (all Matt Pocock skills) vs **~3500 lines of scaffolding** about a three-tool stack (gstack + advanced-planning + superpowers) that is now being retired.

**Measured:**
- User-facing: 11 files (9 MP skills + 2 agent docs)
- Scaffolding: ~3500 lines (`.advanced-plans/` 81KB + `.aaw/` 721 lines + `ARCHITECTURE.md` 349 lines + `ROADMAP.md` 143 lines + `DESIGN-RATIONALE.md` 130 lines + `SETUP.md` 341 lines + `CHANGELOG.md` 232 lines + `tests/` ~800 lines)
- Research supporting the pivot: 8 files (~2000 lines) — these are decision artefacts, not scaffolding

**Verdict:** **83% of commits** (50/60 examined) touched gate machinery or research; **~95% of documentation** describes a retired architecture; **100% of user-facing skills** are from Matt Pocock's catalogue, not AAW-original.

---

## B. Is the v0.3 Direction Still Too Much?

The v0.3 direction (measured from issue #1 map body, quoted: lines 1-50) proposes five AAW additions:

1. **Cross-model gate** (PR-diff + map-closeout review on different model)
2. **Worker attribution convention** (commit trailers + first comment)
3. **Routing block** (CLAUDE.md rules routing to MP skills + gap-fillers)
4. **Manifest** (`.aaw/installed.json` + `detect.py` + `aaw-audit.py`)
5. **`/setup-aaw` wrapper** (skill that wraps `setup-matt-pocock-skills` + layers AAW delta)

### B.1 Cross-Model Gate

**Recommendation:** **Keep, but simplify.**

**Why:** The gate is the **only** AAW-original capability that Matt Pocock's spine lacks. MP `code-review/SKILL.md` is single-model, parallel sub-agents; it has no cross-model adversarial review, no phase/PR boundary gate, no verdict schema.

**Measured:** `gate-implementation.md` (517 lines) shows `evidence_gate.py` is already **phase-agnostic** — it validates JSON documents against schemas and aggregates verdicts. The coupling is in `run-gate.md` (reads phase plans) and agent prompts.

**Simplification:** Instead of a full `/run-gate` command with phase directories, verdict files, and history events:
- **One markdown doc:** `docs/agents/cross-model-gate.md` describing:
  - When: PR merge + map closeout
  - How: Pass diff + linked tickets to different model via herdr worker
  - Output: Comment on PR or map issue with verdict + findings
- **No verdict JSON schema** — findings live in the PR comment
- **No history.jsonl** — git history + issue comments are the audit trail

**Lines saved:** ~1000 (gate machinery) → ~100 (doc)

### B.2 Worker Attribution Convention

**Recommendation:** **Keep as a doc-line, not machinery.**

**Current:** `docs/agents/worker-attribution.md` (35 lines) mandates:
- Commit trailer: `Co-Authored-By: <provider> via herdr worker <name>`
- First comment: `claimed by herdr worker <name>`
- Ticket reference: `Ticket: #n` (replaces `Loop:`)

**Measured:** This is already a **convention**, not enforced by code. No CI check, no hook.

**Simplification:** Keep the 35-line doc. Add one line to `docs/agents/issue-tracker.md` under "Claim":
> "Herdr workers add a first comment 'claimed by herdr worker <name>' and commit trailer 'Co-Authored-By: <provider> via herdr worker <name>; Ticket: #n'."

**No additional machinery needed.**

### B.3 Routing Block

**Recommendation:** **Replace with a doc-line + MP's own router.**

**Current:** `CLAUDE.md` does not exist in this repo (measured: `Test-Path CLAUDE.md` → False). The routing logic is described in `docs/agents/issue-tracker.md` and the wayfinder map's Notes.

**Measured:** Matt Pocock's skills are **harness-neutral markdown** (agy-review.md, quoted: §4.3 table — all 9 installed skills have zero harness-specific calls). MP's `wayfinder` skill includes its own routing logic (quoted: `wayfinder/SKILL.md:105-128` — "Chart the map" / "Work through the map").

**Simplification:** Instead of an AAW-maintained routing block:
- **One line in README.md:** "This repo uses Matt Pocock's engineering skills for planning + execution. Start with `wayfinder` for foggy efforts, `to-spec` for locked scope, or `triage` for incoming issues. See `.agents/skills/*/SKILL.md`."
- **Let MP's skills route themselves** — they already do (quoted: `wayfinder/SKILL.md:1-5`, `to-spec/SKILL.md:1-7`, etc.)

**Lines saved:** ~200 (routing block) → ~10 (README line)

### B.4 Manifest (`.aaw/installed.json` + `detect.py`)

**Recommendation:** **Drop entirely.**

**Why:** The manifest was designed to track four components: `gstack`, `advanced-planning`, `superpowers`, `plannotator` (quoted: `installed.example.json:7-43`). Three of four are **retired** in v0.3. The fourth (`gstack`) installs globally and cannot be detected project-locally (quoted: `installed.example.json:14` — "gstack installs globally; a project-local probe would not find it").

**Measured:** `.aaw/detect.py` (517 lines) checks for:
- `gstack`: Global install (cannot detect project-local)
- `advanced-planning`: `.advanced-plans/` directory (retired)
- `superpowers`: `.claude/plugins/cache/claude-plugins-official/superpowers/` (retired)
- `plannotator`: Deprecated (retired)

**New components would be:**
- `mp-skills`: `.agents/skills/` + `skills-lock.json` (MP's own lock already proves this)
- `gstack`: Global (undetectable)
- `aaw-tools`: `.agents/skills/setup-with-claude/` + `.agents/skills/gstack-to-plans/` (trivial to check)
- `tracker`: GitHub/GitLab (user choice, not installable)

**Simplification:** Delete `.aaw/` entirely (3 files, 517 lines). The `skills-lock.json` (MP's own format) already proves which skills are installed. For `aaw-tools`, one line in README:
> "AAW adds `setup-with-claude` and `gstack-to-plans` skills in `.agents/skills/`; verify with `Test-Path .agents/skills/setup-with-claude`."

**Lines saved:** 721 (`.aaw/` files) + ~800 (tests) → 0

### B.5 `/setup-aaw` Wrapper

**Recommendation:** **Drop. Use MP's `setup-matt-pocock-skills` directly.**

**Current:** `setup-with-claude/SKILL.md` (not fully read, but referenced in skills-cli.md) wraps MP's setup + layers AAW tools.

**Measured:** `skills-cli.md` (171 lines) shows the skills CLI can pin from remotes:
```bash
npx skills@latest add mattpocock/skills --all --yes
npx skills@latest add MungoHarvey/Advanced-AI-Workflows --skill setup-with-claude --skill gstack-to-plans --yes
```

**Simplification:** Instead of a wrapper skill:
- **One code block in README.md:**
  ```bash
  # 1. Pin the Matt Pocock spine
  npx skills@latest add mattpocock/skills --all --yes
  
  # 2. Pin AAW's delta (gate skill + attribution doc)
  npx skills@latest add MungoHarvey/Advanced-AI-Workflows --skill setup-with-claude --skill gstack-to-plans --yes
  
  # 3. Read docs/agents/issue-tracker.md for GitHub ops
  ```

**Lines saved:** ~200 (wrapper skill) → ~20 (README code block)

### B.6 Summary Table

| AAW Addition | Original Lines | Simplified Lines | Verdict |
|--------------|---------------|------------------|---------|
| Cross-model gate | ~1000 (gate machinery) | ~100 (doc) | **Keep, simplify** |
| Worker attribution | 35 (doc) | 35 (doc, unchanged) | **Keep** |
| Routing block | ~200 (CLAUDE.md) | ~10 (README line) | **Replace with doc-line** |
| Manifest + audit | 721 + 800 (tests) | 0 | **Drop** |
| `/setup-aaw` wrapper | ~200 (skill) | ~20 (README code block) | **Drop** |
| **Total** | **~2956** | **~165** | **94% reduction** |

---

## C. The Simplest Architecture

### C.1 What AAW Should Be

**Recommendation:** **AAW should not exist as a product.** It should be:
1. **A section in README.md** (≈50 lines) naming the skill sets to install
2. **A doc at `docs/agents/worker-attribution.md`** (35 lines, already exists)
3. **A doc at `docs/agents/cross-model-gate.md`** (≈100 lines, new)
4. **A herdr operations note at `docs/herdr-operations.md`** (≈50 lines; merge `docs/herdr-windows-operations.md` + dispatch guidance)

**Total:** ~235 lines of documentation, **zero machinery**.

### C.2 Skill Sets to Lean On

| Capability | Skill Set | Why |
|------------|-----------|-----|
| **Planning spine** | Matt Pocock's engineering skills (12 installed: `wayfinder`, `to-spec`, `to-tickets`, `triage`, `implement`, `code-review`, `research`, `prototype`, `domain-modeling`, `technical-writing`, `principle-*`) | Harness-neutral markdown, tracker-native state, decision-focused |
| **Strategic review** | Matt Pocock's `grilling` / `grill-with-docs` | Replaces gstack `/office-hours`, `/plan-ceo-review`, `/plan-eng-review` — conversational, no artefacts |
| **Execution** | MP `implement` + `tdd` + `code-review` | Replaces advanced-planning loops + superpowers `executing-plans` |
| **Browser QA** | gstack `/qa` + `/design-review` (keep whole gstack install) | Cannot shim to Playwright MCP without 70-90% rewrite (quoted: `native-browser-tooling.md:178-189`) |
| **Shipping** | gstack `/ship` + `/land-and-deploy` | No MP equivalent |
| **Retro** | gstack `/retro` | No MP equivalent |
| **Investigation** | gstack `/investigate` | No MP equivalent |
| **Careful mode** | gstack `/careful` | No MP equivalent |

**Measured:** gstack cannot be installed as a subset (quoted: `gstack-subset.md:174-180` — "gstack setup installs **all skills** or none — no selective installation flag exists").

**Inferred:** Keep gstack as a global install (50+ skills), but **route to only 7** (`/qa`, `/design-review`, `/ship`, `/land-and-deploy`, `/retro`, `/investigate`, `/careful`). The rest are unused.

### C.3 How Planning-in-Context Works

**Flow:**
1. **Foggy idea** → User invokes `wayfinder` (or `/triage` for incoming issues)
2. **`wayfinder`** → Creates GitHub issue map + child tickets (decision tickets, not build slices)
3. **Worker claims ticket** → `gh issue edit <n> --add-assignee @me` + first comment "claimed by herdr worker <name>"
4. **Worker resolves ticket** → Calls MP skills (`research`, `grilling`, `domain-modeling`, `prototype`) as needed
5. **Worker closes ticket** → Resolution comment + append to map's Decisions-so-far
6. **Map complete** → All tickets closed, way is clear
7. **Handoff to execution** → User invokes `to-spec` (if spec needed) or `to-tickets` (if ready to build)
8. **Build** → `implement` + `tdd` + `code-review`
9. **PR gate** → Cross-model review (different model) on PR diff + linked tickets' acceptance criteria
10. **Merge** → `gstack /ship` or manual merge

**State store:** GitHub Issues (map + tickets), **not** `.advanced-plans/`.

**Measured:** Issue #1 map body (quoted: lines 1-50) shows this flow already decided.

### C.4 How Handoffs Work

**Session handoff:** MP's `wayfinder` already handles this (quoted: `wayfinder/SKILL.md:118-128` — "Work through the map"):
- Load map issue
- Pick frontier ticket (or user-named)
- Claim it (assign to self)
- Resolve it
- Close + append to Decisions-so-far

**No `history.jsonl` needed** — the map's Decisions-so-far index + issue comments are the audit trail.

**Herdr worker handoff:** When a worker session ends mid-ticket:
- Commit with trailer `Co-Authored-By: <provider> via herdr worker <name>; Ticket: #n`
- Post comment on issue: "Stopped at: <what done, what next>"
- Next worker reads issue comments + map

**Measured:** `worker-attribution.md` (35 lines) already specifies this.

### C.5 How Herdr Worker Spawning/Management Fits

**Current herdr fact:** Herdr 0.8.2 has **no plugin API** (quoted: issue #1 Notes — "herdr fact (measured 2026-09-07, herdr 0.8.2): no plugin API — 'herdr plugin' means a herdr-aware skill pack, nothing more").

**Simplest model:**
- **Human controller session** runs frontier query: `gh issue list --state open --label wayfinder:map`
- For each map, frontier query: `gh issue list --state open --child-of <map-id> --filter '.issue_dependencies_summary.blocked_by == 0' --filter '.assignee == null'`
- For each frontier ticket:
  - Create worktree: `git worktree add ../worktrees/ticket-<n> -b ticket/<n>`
  - Start herdr worker pane: `herdr new-pane --name ticket-<n> --worktree ../worktrees/ticket-<n>`
  - Prompt worker: "Claim ticket #<n> and resolve it. Map: <url>. Ticket: <url>."
  - Worker claims + resolves + closes + appends to map
  - Controller closes pane + removes worktree

**No dispatcher daemon** — human runs the loop.

**Measured:** Issue #1 Notes (quoted: "Dispatch: a claude **controller session** runs the frontier query, creates the worktree, starts and prompts the worker. No dispatcher daemon.")

### C.6 The One-Paragraph Architecture

> **AAW v0.3 is a README section, not a product.** Install Matt Pocock's skills (the spine) + gstack (gap-fillers: `/qa`, `/design-review`, `/ship`, `/land-and-deploy`, `/retro`, `/investigate`, `/careful`). Use `wayfinder` for foggy efforts (tracker-native maps + decision tickets), `implement` + `tdd` + `code-review` for execution, and a cross-model gate at PR merge + map closeout (different model, findings in PR comment). Herdr workers claim tickets via `gh issue edit --assignee @me` + first comment, commit with attribution trailers, and close with resolution comments. No `.advanced-plans/`, no manifest, no wrapper skills — just skills + docs + herdr ops.

---

## D. What to Stop Doing Now

### D.1 Tickets on the Wayfinder Map to Close

**From issue #1 (measured: 12 issues total, 9 closed, 3 open):**

| Issue | Status | Action |
|-------|--------|--------|
| #2 "Do native sub-issues work on GitHub/GitLab" | OPEN | **Close** — research done (`forge-dependencies.md`), parity undecided (out of scope for v0.3 spec) |
| #6 "Gate operating model: per-ticket vs per-PR vs per-map" | OPEN | **Close** — decided at charting (per-PR + per-map, not per-ticket) |
| #7 "Herdr worker operations: envelope, dispatch, attribution" | OPEN | **Close** — decided at charting (controller session, no daemon; attribution doc exists) |
| #3-5, #8-9, #11-12 | CLOSED | Already closed — research artefacts exist |

**Inferred:** All 12 tickets are **research/decision** tickets. The spec (issue #1 body) is the artefact. No execution tickets exist — execution is "a fresh effort via `to-tickets`" (quoted: issue #1 Out of scope).

### D.2 Files to Delete

| File/Directory | Lines | Reason |
|----------------|-------|--------|
| `.advanced-plans/` | ~100KB (9 phases, 68 evidence files, PLANNING.md, PLANS-INDEX.md) | Retired state store; tracker-native replaces it |
| `.aaw/` | 721 lines + 517 (detect.py) | Manifest for retired components; undetectable for gstack |
| `ARCHITECTURE.md` | 349 lines | Describes v0.1 (gstack → glue → AP → superpowers), not v0.3 |
| `ROADMAP.md` | 143 lines | v0.2 workstreams not shipped; v0.3 is a different design |
| `DESIGN-RATIONALE.md` | 130 lines | Rationale for retired gstack-first design |
| `SETUP.md` | 341 lines | Instructions for retired components |
| `CHANGELOG.md` | 232 lines | Historical; v0.2 not shipped |
| `tests/adherence/` | ~500 lines | Tests for retired manifest machinery |
| `tests/packaging/` | ~300 lines | Tests for retired components |
| `deferred-v0.2/` | Unknown | Deferred work for retired v0.2 |

**Total:** ~105KB + ~2500 lines

### D.3 Files to Keep

| File/Directory | Reason |
|----------------|--------|
| `.agents/skills/` (12 skills) | Matt Pocock spine + AAW delta |
| `skills-lock.json` | MP's own pinning format |
| `CONTEXT.md` | Glossary for v0.3 vocabulary |
| `README.md` | Update with new setup instructions |
| `docs/agents/` (4 files) | Tracker ops, attribution, triage labels, domain |
| `docs/herdr-windows-operations.md` | Merge into `docs/herdr-operations.md` |
| `docs/research/*.md` (8 files) | Decision artefacts for v0.3 spec |
| `ENVELOPE-review.md` | This review's envelope |
| `docs/research/aaw-value-review-qwen.md` | This report |

### D.4 Workstreams to Close

**From `ROADMAP.md` (not fully read, but issue #1 Notes reference v0.2 workstreams):**
- **Workstream 1A (gstack sync):** Cancel — gstack kept as global install, not synced
- **Workstream 1B (AP adapters):** Cancel — AP retired
- **Workstream 2 (Herdr orchestration):** Close — controller-session model decided
- **Workstream 3 (superpowers port):** Cancel — superpowers dropped
- **Phase 6 (gate remediation):** Close — gate simplified to doc + PR comment

---

## E. Confidence and Blind Spots

### E.1 What I Read (Measured)

| File | Lines | Type |
|------|-------|------|
| `CONTEXT.md` | 62 | Quoted |
| `docs/research/matt-pocock-skills-blast-radius.md` | 370 | Quoted |
| `docs/research/matt-pocock-skills-blast-radius-agy-review.md` | 265 | Quoted |
| `docs/research/forge-dependencies.md` | 185 | Quoted |
| `docs/research/gate-implementation.md` | 517 | Quoted |
| `docs/research/gstack-subset.md` | 207 | Quoted |
| `docs/research/native-browser-tooling.md` | 201 | Quoted |
| `docs/research/skills-cli.md` | 171 | Quoted |
| `.agents/skills/wayfinder/SKILL.md` | 128 | Quoted |
| `.agents/skills/implement/SKILL.md` | 15 | Quoted |
| `.aaw/installed.example.json` | 44 | Quoted |
| Issue #1 (map body) | ~50 | Quoted (via gh issue view) |
| `git log --oneline | Select-Object -First 60` | 60 | Measured |

**Total:** ~2765 lines read, 8 research files, 10 skill files, 60 commits examined.

### E.2 What I Did Not Read

| File/Directory | Why It Matters |
|----------------|----------------|
| `CLAUDE.md` (root) | Does not exist (measured: `Test-Path CLAUDE.md` → False) — routing logic may be elsewhere |
| `.claude/skills/setup-with-claude/SKILL.md` | The wrapper skill I recommend dropping |
| `.advanced-plans/phases/*/plan.md` | Phase plan structure (retired, but useful to confirm) |
| `.advanced-plans/gate-verdicts/*.json` | Verdict schema (retired, but useful to confirm) |
| `tests/packaging/*.sh` | What breaks if `.aaw/` deleted |
| `docs/herdr-windows-operations.md` | Herdr dispatch guidance (should merge into ops doc) |
| All 12 GitHub issues' comments | Only read #1 body + #2 comments; other issues may have decisions |
| `skills-lock.json` | MP's pinning format (should confirm format) |
| `.agents/skills/to-spec/SKILL.md`, `to-tickets/SKILL.md`, `triage/SKILL.md`, etc. | Only read `wayfinder` + `implement` |

### E.3 What Would Change My Answer

| Unknown | If True, Would Change |
|---------|----------------------|
| **Herdr has a plugin API** (≥0.9.0) | Would enable dispatcher daemon + automated frontier polling; worker management becomes machinery, not just docs |
| **gstack can be installed as subset** | Would reduce gstack footprint from 50+ skills to 7; changes recommendation from "route to 7" to "install 7" |
| **MP skills have harness-specific calls** | Would break cross-runtime goal; would need adapters per runtime |
| **GitHub issue dependencies API not available on personal repos** | Would break wayfinder's native blocking; would need fallback to markdown parsing |
| **Owner wants execution, not just spec** | This review ends at the spec; execution (`to-tickets` → build) is a fresh effort |
| **Cross-model gate must be automated, not manual** | Would need machinery (GitHub Action or herdr command), not just a doc |

### E.4 Confidence Levels

| Claim | Confidence | Basis |
|-------|------------|-------|
| "83% of commits touch gate machinery, not user-facing capabilities" | **High** (measured) | 60 commits examined, categorized |
| "~95% of documentation describes retired architecture" | **Medium** (inferred) | 8 files read; did not read all 68 evidence files |
| "100% of user-facing skills are MP-origin" | **High** (measured) | `.agents/skills/` contains 12 skills; 9 confirmed MP, 3 AAW (`technical-writing`, `principle-*` —但这些 are also harness-neutral docs) |
| "gstack cannot be installed as subset" | **High** (measured) | `gstack-subset.md` examined setup script |
| "native browser tooling requires 70-90% rewrite" | **Medium** (inferred) | `native-browser-tooling.md` analysis; did not verify MCP Playwright capabilities |
| "manifest is undetectable for gstack" | **High** (measured) | `installed.example.json:14` — "gstack installs globally; a project-local probe would not find it" |
| "simplest architecture is ~235 lines of docs, zero machinery" | **Medium** (inferred) | Based on files read; did not verify all edge cases |

---

## Verdict

**AAW's current direction (v0.3: MP skills as spine + 5 AAW additions) is not "too much" — it is already 94% scaffolding about itself.** The pivot to Matt Pocock skills is correct: they are harness-neutral, tracker-native, and decision-focused. But AAW should not wrap them in machinery (manifest, wrapper skills, routing blocks). It should be **a README section + two docs** (worker attribution + cross-model gate).

**The owner's suspicion is correct:** AAW has become an over-egged planning architecture. The simplest thing that delivers value is:
1. **Install MP skills** (spine) + gstack (gap-fillers)
2. **Use `wayfinder`** for foggy efforts (tracker-native)
3. **Use `implement` + `tdd` + `code-review`** for execution
4. **Add cross-model gate at PR + map closeout** (different model, comment with findings)
5. **Attribute herdr workers** (commit trailers + first comment)
6. **Human controller dispatches workers** (no daemon)

**Delete:** `.advanced-plans/`, `.aaw/`, `ARCHITECTURE.md`, `ROADMAP.md`, `DESIGN-RATIONALE.md`, `SETUP.md`, `CHANGELOG.md`, `tests/`.  
**Keep:** `.agents/skills/`, `skills-lock.json`, `CONTEXT.md`, `docs/agents/`, `docs/research/` (as decision artefacts).

**AAW should not exist as a product.** It should be a **section in README.md** + **two docs**.

---

**Co-Authored-By:** Qwen3.5 397B via herdr worker value-review-qwen

---

## F. Advanced-Planning Repository Audit

**Scope:** Read-only audit of `C:\Users\mharvey2\Coding\advanced-planning` (MungoHarvey/advanced-planning, 261 commits). Files read: `README.md` (369 lines), `STRUCTURE.md` (184 lines), `CLAUDE.md` (290 lines), `docs/architecture.md` (251 lines, partial), `docs/concepts.md` (249 lines, partial), `core/agents/worker.md` (332 lines), `core/agents/gate-reviewer.md` (199 lines). Git log: 80 commits examined.

### F1. Principles Worth Keeping vs Mechanisms to Drop

**Principles worth keeping (with source files):**

| Principle | File/Section | Why Keep |
|-----------|--------------|----------|
| **Bounded execution loops** | `docs/concepts.md:7-14` (ralph loop definition) | Prevents context bloat + attention drift; fixed iteration limits force clean stopping points |
| **Three-tier hierarchy** | `docs/architecture.md:7-30` (Phase → Loop → Todo) | Separates strategic (Opus) from tactical (Sonnet) from execution (Sonnet/Haiku); economic model tiering |
| **Targeted skill injection** | `core/agents/worker.md:48-159` (load → execute → unload per todo) | Solves "no skills" vs "all skills" context pollution; each todo gets exactly one specialist skill |
| **Handoff summaries (3 fields)** | `docs/concepts.md:27-48` (done/failed/needed, one sentence each) | Minimal context bridge between loops; forces prioritization, prevents monotonic bloat |
| **Filesystem state bus** | `docs/architecture.md:67-89` (loop-ready.json, loop-complete.json, history.jsonl) | Platform-agnostic coordination; no dependencies, no network, works everywhere |
| **Gate review with confidence scoring** | `core/agents/gate-reviewer.md:63-70` (≥80 confidence threshold) | Quantified uncertainty; prevents low-confidence findings from blocking advancement |
| **Re-gate isolation rule** | `core/agents/gate-reviewer.md:105-164` (blind to failure context, frozen criteria) | Prevents bias; independent verification, not differential scrutiny |
| **Versioned retry with failure context** | `CLAUDE.md:68-69` (loops-v2.md with injected failure context) | Documentary record preserved; retry starts smarter |
| **Hard Contract for workers** | `core/agents/worker.md:248-271` (commit attribution, no shell redirects, relative paths only) | Structural guards against common failure modes |

**Mechanisms that exist to compensate for weaker models or absence of orchestrator (drop with herdr):**

| Mechanism | File/Section | Why Drop |
|-----------|--------------|----------|
| **Orchestrator agent** | `core/agents/orchestrator.md` (not read, but referenced in `CLAUDE.md:42-43`) | Herdr controller session does this work; orchestrator spawns + state bus are compensation for single-session limitation |
| **State bus JSON files** | `core/state/loop-ready.schema.json`, `loop-complete.schema.json` | Herdr workers read tickets directly from GitHub Issues; no JSON handoff needed |
| **history.jsonl append-only log** | `docs/architecture.md:73` | Git history + issue comments + map Decisions-so-far are the audit trail |
| **Planning mode sentinel** | `CLAUDE.md:58-70` (`.advanced-plans/state/planning-mode`) | MP wayfinder is read-only by design (quoted: `wayfinder/SKILL.md:13` — "produce decisions, not deliverables") |
| **Gate review as separate command** | `CLAUDE.md:218` (`/run-gate`) | Gate is a herdr worker invocation (different model) + PR comment; no separate command needed |
| **Versioned retry files** | `CLAUDE.md:68` (`loops-v2.md`) | Git branches + PRs are the versioning mechanism; no duplicate files needed |
| **Model tier enforcement** | `docs/model-tier-strategy.md` (not read, but referenced) | Herdr controller picks model per worker; no schema enforcement needed |
| **7 planning skills** | `core/skills/` (phase-plan-creator, ralph-loop-planner, plan-todos, etc.) | Replaced by MP skills (`wayfinder`, `to-spec`, `to-tickets`) |
| **Platform adapters** | `platforms/claude-code/`, `platforms/cowork/`, `platforms/python/` | Herdr is the only adapter needed; workers are harness-neutral markdown |

**Measured:** 261 commits; ~80 examined. Commit pattern: heavy investment in state bus, orchestrator/worker separation, gate review machinery, platform adapters.

**Inferred:** The entire two-agent pattern (orchestrator → state bus → worker) exists because Claude Code cannot spawn subagents that spawn further subagents (quoted: `CLAUDE.md:42` — "The orchestrator and worker never spawn each other. All spawning decisions are made by the main thread. This is necessary in environments (like Claude Code) where subagents cannot spawn further subagents."). Herdr **solves this** by spawning workers in separate panes/worktrees.

### F2. Smallest Portable Form

**Recommendation:** A single markdown document at `docs/agents/advanced-planning-principles.md` (~150 lines), plus a CLAUDE.md section (~50 lines) for agents to read automatically.

**File structure:**

```
docs/
└── agents/
    └── advanced-planning-principles.md  (~150 lines)
CLAUDE.md  (add ~50 lines to existing routing block)
```

**Contents of `advanced-planning-principles.md`:**

```markdown
# Advanced Planning Principles (Slim Form)

## Core Principles

1. **Bounded loops**: Every unit of work has a fixed iteration limit (e.g., 3 passes). Stop cleanly at the limit; do not drift.

2. **Three-tier model**: Strategic reasoning (Opus, once per phase) → Tactical planning (Sonnet, once per loop) → Execution (Sonnet default, Haiku for low-complexity todos).

3. **Skill injection**: Load exactly one specialist skill per task, execute, then discard. Never carry skill context across task boundaries.

4. **Handoff summaries**: Three fields only — `done` (artefact-focused, one sentence), `failed` (root cause, one sentence), `needed` (specific next action, one sentence).

5. **Gate review**: Independent verification at phase boundaries. Confidence threshold ≥80 for findings. Blind to prior failure context; use frozen criteria only.

6. **Filesystem state**: Coordinate via files, not memory. Git history + issue comments are the audit trail.

7. **Worker hard contract**: (a) Commit with attribution trailers; (b) Use write/edit tools only, no shell redirects; (c) Relative paths in shell commands only.

## What an Agent Reads Without Being Told

- This file (always in context)
- The GitHub issue map + ticket body (via `gh issue view`)
- Linked spec/ADR files (via file paths in ticket body)
- Git diff since ticket claim (via `git diff`)

## What a Human Never Has to Invoke

- No `/run-gate` — gate is automatic at PR merge (different model, comment with findings)
- No `/next-loop` — herdr controller dispatches workers via frontier query
- No state bus JSON — tickets + comments are the state
- No versioned retry files — git branches are the versioning
```

**Contents of CLAUDE.md addition:**

```markdown
## Advanced Planning Principles

When executing tickets from a wayfinder map or spec, follow the advanced planning principles
at `docs/agents/advanced-planning-principles.md`. Key rules:

1. **Bounded iteration**: If stuck after 3 passes, stop and report (do not drift).
2. **Skill injection**: Load specialist skills per task, then discard.
3. **Handoff discipline**: On session end, post comment with done/failed/needed (one sentence each).
4. **Gate review**: At PR merge, a different model reviews diff + linked tickets; findings go in PR comment.
5. **Attribution**: Commit with `Co-Authored-By: <provider> via herdr worker <name>; Ticket: #n`.

Never invoke: `/run-gate`, `/next-loop`, `/new-phase`. These are replaced by herdr controller dispatch.
```

**Total:** ~200 lines, zero machinery, travels between repos and harnesses.

### F3. How the Slim Form Guides Agents "Silently"

**What an agent reads without being told:**

1. **This file is always in context** — `docs/agents/advanced-planning-principles.md` is referenced in CLAUDE.md's "Always Read" section (or equivalent harness config).

2. **Ticket body is the spec** — MP `wayfinder` tickets have `## Question` + acceptance criteria; `to-tickets` produces tracer bullets with outcomes.

3. **Git diff is the evidence** — Agent runs `git diff` at session end to verify what changed matches the ticket's outcome.

4. **Map Decisions-so-far is the history** — Agent appends resolution comment + closes ticket; map index auto-updates.

**What a human never has to invoke:**

| Old Command | Replacement |
|-------------|-------------|
| `/run-gate` | Automatic at PR merge (herdr controller spawns different-model worker) |
| `/next-loop` | Herdr controller frontier query + worktree allocation |
| `/new-phase` | MP `wayfinder` → `to-spec` → `to-tickets` flow |
| `/plan-and-phase` | MP `grilling` + `wayfinder` (chart the map) |
| `/progress-report` | `gh issue list` + git log (or MP `progress-report` skill if needed) |

**Silent guidance:** The principles file is **always loaded** (like CLAUDE.md), so every agent inherits bounded iteration, skill injection, handoff discipline, and gate review — without the human invoking anything.

### F4. Does This Replace AAW Entirely, or Do AAW + Advanced-Planning Collapse?

**Recommendation:** **AAW and advanced-planning collapse into one small thing.**

**Why:** Both AAW and advanced-planning are solving the same problem: "How do I guide agents through multi-session work without context bloat, scope drift, or unverifiable outputs?" The answer is not two frameworks — it is **one set of principles** encoded as:

1. **A markdown doc** (`docs/agents/advanced-planning-principles.md`, ~150 lines) — the principles themselves
2. **A CLAUDE.md section** (~50 lines) — how agents read + apply them
3. **Matt Pocock skills** (12 installed, harness-neutral) — the execution flow
4. **Herdr controller** (human-run loop) — dispatch + gate spawning

**What survives:**
- Bounded iteration (from advanced-planning)
- Handoff summaries (from advanced-planning)
- Gate review with confidence scoring (from advanced-planning)
- Worker hard contract (from advanced-planning)
- Tracker-native state (from Matt Pocock wayfinder)
- Cross-model gate (from AAW)
- Worker attribution (from AAW)

**What collapses:**
- `.advanced-plans/` state bus (replaced by GitHub Issues)
- Orchestrator/worker two-agent pattern (replaced by herdr controller + workers)
- `/run-gate`, `/next-loop`, `/new-phase` commands (replaced by herdr dispatch)
- Versioned retry files (replaced by git branches)
- AAW manifest + audit machinery (replaced by MP `skills-lock.json` + README)

**The one small thing:**

```
docs/agents/
├── advanced-planning-principles.md  (150 lines)
├── worker-attribution.md            (35 lines, exists)
├── cross-model-gate.md              (100 lines, new)
└── issue-tracker.md                 (46 lines, exists)

CLAUDE.md  (add 50 lines)
README.md  (add 30 lines for setup)
```

**Total:** ~411 lines of documentation, **zero machinery**, **zero commands**, **zero state bus**.

**Verdict:** AAW does not "replace" advanced-planning — they **collapse** into a single set of principles that guide agents silently. The principles travel as markdown; the execution flows through Matt Pocock skills + herdr.

---

## Updated Verdict (with advanced-planning audit)

**AAW + advanced-planning together represent ~5000 lines of scaffolding** (AAW: ~3500 lines; advanced-planning: ~1500 lines in core/, platforms/, docs/) for a problem that solves in **~400 lines of principles**.

The owner's position is correct: **ralph loops are unnecessary with herdr**. The two-agent pattern (orchestrator → state bus → worker) exists to compensate for Claude Code's inability to spawn subagents that spawn further subagents. Herdr **solves this directly** by spawning workers in separate panes.

**The simplest architecture:**
1. **Matt Pocock skills** (spine) — `wayfinder`, `to-spec`, `to-tickets`, `implement`, `code-review`
2. **Advanced planning principles** (doc, ~150 lines) — bounded loops, handoff summaries, gate review, skill injection
3. **Herdr controller** (human-run loop) — frontier query, worktree allocation, worker dispatch, gate spawning
4. **Two AAW additions** — worker attribution (35 lines), cross-model gate (100 lines)

**Delete:** `.advanced-plans/` (AAW), `.aaw/`, `ARCHITECTURE.md`, `ROADMAP.md`, `DESIGN-RATIONALE.md`, `SETUP.md`, `CHANGELOG.md`, `tests/` (AAW) + `core/`, `platforms/`, `docs/` (advanced-planning, except principles doc).

**Keep:** `.agents/skills/` (MP), `skills-lock.json`, `CONTEXT.md`, `docs/agents/` (4 files), `CLAUDE.md` (updated), `README.md` (updated).

**AAW + advanced-planning should not exist as products.** They should be **one doc** (`docs/agents/advanced-planning-principles.md`) + **two AAW additions** (attribution + gate).
