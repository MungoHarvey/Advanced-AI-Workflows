# AAW value review (cursor)

**Question:** with all this planning, what are we gaining? Is Advanced-AI-Workflows wasted energy, and what is the simplest thing that still delivers the owner's wants (off-the-shelf skills, session handoffs, herdr worker spawn/manage; planning from skill context, not a planning framework)?

**Checkout:** `review/value-cursor` at `a401f06`. Read-only except this file.

**Verdict:** AAW as a product is wasted energy. The repo's measurable output is a planning-and-packaging archive about itself. v0.3 still proposes five AAW additions on top of Matt Pocock's skills; four of those five should not be built. The phase → ralph-loop → todo engine in `C:\Users\mharvey2\Coding\advanced-planning` (261 commits, v0.19.0) is the same waste one layer down: keep a handful of principles, delete the loops and the bus. AAW and advanced-planning should collapse into one instruction-file section plus herdr-ops. Neither should remain a product.

Claims are tagged `measured`, `quoted`, or `inferred`.

---

## A. Value audit

### What a user can actually run today

Shipped version is still **v0.1.0**. `measured:` `VERSION` is the single line `0.1.0`.

The documented user path is still the **v0.1/v0.2 three-tool stack**, not the v0.3 map. `quoted:` `README.md` opening: "An integrated planning-review-execution system built from three composable open-source tools — gstack, advanced-planning, and superpowers." `quoted:` `CHANGELOG.md` unreleased heading: "Work towards v0.2.0 — Herdr-managed multi-runtime orchestration." `quoted:` `ROADMAP.md`: v0.2 "implementation-ready design, not yet built" and phases 6–9 "deferred".

Runnable artefacts in this tree:

| Artefact | What it does | Evidence |
|---|---|---|
| `.claude/skills/setup-with-claude/SKILL.md` | Interactive installer for gstack + advanced-planning + superpowers + routing + manifest | `measured:` 923 non-blank lines in that skill tree. `quoted:` frontmatter still says "gstack + advanced-planning + superpowers". |
| `.claude/skills/setup-with-claude/references/claude-md-routing.md` | Fenced routing block installed into CLAUDE.md/AGENTS.md | `measured:` 197 non-blank lines. Seven front-door rules still name `/office-hours`, `/plan-and-phase`, `/new-phase`, `/run-gate`, `gstack-to-plans`. |
| `.claude/skills/gstack-to-plans/SKILL.md` | Copy gstack design docs into `.advanced-plans/specs/` | `measured:` 70 non-blank lines. |
| `.aaw/detect.py`, `installed.schema.json`, `tools/aaw-audit.py` | Prove which of those three tools is installed | `measured:` `.aaw/` 592 non-blank lines; `tools/` 526; `tests/packaging/fixtures/manifest/` 24 files. Schema still keys components as gstack / advanced-planning / superpowers (`quoted:` routing block lines 22–23). |
| `tools/herdr-env.sh` / `.ps1` | Pin HOME from USERPROFILE so herdr sees integrations | `quoted:` `docs/herdr-windows-operations.md` §1.1. This is real Windows-domain lore, not a framework. |
| `.agents/skills/*` + `skills-lock.json` | Pinned Matt Pocock (and Cursor pstack) skills | `measured:` 12 SKILL.md files, 825 non-blank lines. Lock pins 12 skills: 7 from `mattpocock/skills`, 5 from `cursor/plugins`. One commit: `738aaa9 Agent skills setup…`. |
| `docs/agents/worker-attribution.md` | Trailer convention for worker commits | `quoted:` enforced "In the worker envelope, at dispatch. Not afterwards." |
| `docs/herdr-windows-operations.md`, `docs/worktree-ownership.md`, kickoff prompt | How this programme uses herdr | Operating docs. `quoted:` herdr-ops file still says "Advanced Planning remains the planner." |

None of that is a planning engine a stranger would choose. The installer installs **other people's** tools and then a 197-line router that only makes sense if those tools are present.

`CLAUDE.md` is **not in this checkout**. `measured:` `.gitignore` line 20 lists `CLAUDE.md`; `Test-Path CLAUDE.md` is false. The envelope asked for the installed routing block plus Matt Pocock's `## Agent skills` block. The source of the routing block is the reference file above. The Agent-skills block was not readable here.

### What the repo spent its mass on (scaffolding about itself)

| Bucket | Size | Evidence |
|---|---|---|
| `.advanced-plans/` | 143 files, 23 673 non-blank lines | `measured` |
| `history.jsonl` | 173 181 bytes, 71 lines | `measured` |
| gate-verdicts | 41 files | `measured` |
| evidence | 69 files | `measured` |
| phases | 9 phase directories | `measured` |
| git history | **249** commits | `measured:` `git rev-list --count HEAD` |
| commits touching `.advanced-plans/` | **195** | `measured:` `git log --oneline -- .advanced-plans` |
| commits touching `.claude/skills/setup-with-claude` | **19** | `measured` |
| commits touching `tests/` | **20** | `measured` |
| commits touching `docs/` | **23** | `measured` |
| commits touching `.aaw/` | **7** | `measured` |
| commits touching `tools/` | **4** | `measured` |
| commits touching `.agents/skills` | **1** | `measured` |
| commits touching `gstack-to-plans` | **1** | `measured` |

**About 78% of commits touched the planning archive.** `inferred` from 195/249. That is the central quantitative fact.

Phases 1–5 have `complete.md` (`quoted:` PLANS-INDEX: 1 complete, 2–5 passed / passed-with-open-item). Phases 6–9 were supposed to stay "planned, loops deferred" (`quoted:` `ROADMAP.md` lines 103–104; `quoted:` phase-6 `plan.md` "Planned, not decomposed"). **They did not stay deferred.** `measured:` `git log --oneline -60` is dominated by `loop-006-*` through `loop-009-*`, phase-6 gate attempts 1–4, and then v0.3 research merges. Latest gate commit: `64ca08d gate: phase 6 attempt 4 — five of six criteria met, criterion 1 still fails`. Phase 6 never closed. Then the v0.3 map retired the engine that work was extending (`quoted:` issue #1 Notes: "advanced-planning: the phase → ralph-loop → todo engine is **retired**. Salvaged: the cross-model gate and worker attribution only.").

So the expensive thing AAW produced — a filesystem planning bus, adapters, path policy, evidence_gate — is already declared dead in the current map, except two souvenirs. The souvenirs still have open grilling tickets (#6, #7).

### What v0.3 has produced (as of this HEAD)

Not a product. A wayfinder map plus research:

- Issue #1 open, destination = "an **approved spec**", explicitly "Executing the pivot … is a fresh effort" (`quoted:` issue #1 Out of scope).
- Closed research/grilling/prototype: #3, #4, #5, #8, #9, #11, #12. Open: #2 (GitLab half), #6, #7, #10.
- Research markdown under `docs/research/` (this file's siblings). `measured:` those files exist and were read.
- Prototype `/setup-aaw` lives on another branch (`quoted:` #9: `prototype/setup-aaw`, commit `732a273`). **Not in this checkout.** `measured:` glob `**/*setup-aaw*` = 0 files.

### Net

`inferred:` A user who clones this repo today gets (1) an installer for a stack the owner no longer wants, (2) 23k lines of retired plan state, (3) a lockfile of skills they could have installed with `npx skills add mattpocock/skills --all --yes` (`quoted:` `docs/research/skills-cli.md`, measured 37 skills in one command). The unique operational knowledge that is actually scarce — domain Windows HOME vs USERPROFILE, herdr launchers, worker trailers, worktree ownership — is a handful of docs and two scripts, not a configurator product.

The gate *did* catch real defects (example: `quoted:` `19a6496 gate: phase 6 attempt 3 fails, and codex was right where the in-house agents were not`). That is value. It does not require AAW to own a verdict schema, a Python aggregator, or a second `run-gate-pr` command.

---

## B. Is v0.3 still too much?

Yes. The five AAW additions are a smaller cake with the same icing. Issue #1 still wants "skill pack + `/setup-aaw`" plus gate + attribution + routing + re-targeted manifest (`quoted:` issue #1 Destination and Notes). That is still a product with an installer, a component taxonomy (`quoted:` `CONTEXT.md`: four components `mp-skills`, `gstack`, `aaw-tools`, `tracker`), and packaging tests rewritten around it (`quoted:` #8 resolution).

### 1. Cross-model gate — **replace-with-a-doc-line** (keep the *habit*, drop the *machinery*)

Keep: "the reviewer is a different CLI/model from the implementer; findings are waived by a human." `quoted:` ROADMAP ACC-18; routing rule 7; issue #1 "Gate attaches **per PR** … and **per map**."

Drop: salvaging `evidence_gate.py`, `run-gate`, phase-goals-agent, verdict JSON, history events. Issue #4 already says the Python core is generic but the **orchestration is phase-coupled** and a PR gate needs a new entry point, new prompts, schema extensions, new file names (`quoted:` `docs/research/gate-implementation.md` §5 and §8). That is a rebuild. Issue #6 (operating model: which model, where the verdict lives, who runs it) is still **open** with zero comments. `measured:` `gh issue view 6`.

Matt Pocock already has `code-review` (two-axis, parallel sub-agents). `quoted:` `.agents/skills/code-review/SKILL.md`. Cross-model is a **dispatch choice in herdr** (start a cursor/codex/agy worker on the PR), not a framework AAW must own.

### 2. Worker-attribution convention — **keep as a doc-line** (already is)

`quoted:` `docs/agents/worker-attribution.md`: the only enforcement that works is the envelope `COMMIT:` line. There is no CI check in this repo that I found. Making it a manifest component (`aaw-tools` = gate skill + this doc, `quoted:` #8/#9) turns a trailer string into install-time ceremony.

Keep the file or fold it into herdr-ops. Do not pin it, hash it, or detect it.

Change `Loop:` to `Ticket: #n` as issue #1 already settled — that is a one-line envelope edit, not a component.

### 3. Routing block — **drop**

The current block is 197 non-blank lines of gated fallbacks for a stack v0.3 deletes. Issue #5 replaces seven situation-rules with a lifecycle table that "mirrors MP's own router (`ask-matt`)" plus "two AAW sections" and "one AAW addition, the escalate-to-wayfinder rule" (`quoted:` #5 resolution; #1 Decisions-so-far). That is still an AAW-owned router sitting on top of a skill set that already has `ask-matt`.

If the spine is the whole MP catalogue (`quoted:` #5), the routing *is* the catalogue. A fenced AAW block will rot the moment MP changes `ask-matt`, which is how the current block already looks versus README/ROADMAP/CONTEXT.

Replace with at most a short paragraph in whatever instruction file the harness already reads: "Use Matt Pocock skills as installed; do not invent `/plan-and-phase`. If the work is foggy, wayfinder. Different model reviews the PR."

### 4. Manifest (`.aaw/installed.json`, detect, audit, packaging fixtures) — **drop**

This layer exists because AAW's installer lied in both directions (data dir vs install; `~` vs USERPROFILE). `quoted:` `setup-with-claude/SKILL.md` Step 1 and schema description in `installed.schema.json`. That is a problem **created by having an installer that probes other tools**.

v0.3 re-targets it to four components (`quoted:` #8). `mp-skills` is already proven by `skills-lock.json` hashes. `gstack` is a global clone you either have or don't. `tracker` is "a markdown file exists". `aaw-tools` is the circular case: AAW detects AAW.

24 invalid/valid JSON fixtures and a schema that forbids tildes are serious engineering for the wrong object. `measured:` 24 files under `tests/packaging/fixtures/manifest/`.

### 5. `/setup-aaw` wrapper — **drop**

#9 confirms a two-turn handoff around `/setup-matt-pocock-skills`, then offer gstack, pin aaw-tools, write routing, write manifest. Skills CLI research (#12) already shows pinning the spine is one npx command. Wrapping MP's own setup so AAW can write a routing block and a manifest is how you get a second `setup-with-claude` — the current one is already 923 lines of tilde-trap archaeology.

`inferred:` A wrapper that must pause for another skill, then rewrite CLAUDE.md, will accumulate the same edge cases (incomplete fences, dual instruction files, plugin-vs-path) that v0.2 spent phases 4–5 on.

---

## C. Simplest architecture that matches the stated wants

**AAW should not exist as a product.** It should be a **CLAUDE.md/AGENTS.md section plus herdr-ops**. No skill pack, no `/setup-aaw`, no `.aaw/`, no fenced router, no gate CLI.

### Lean on these skill sets (cite)

1. **Matt Pocock `mattpocock/skills` — the spine.** Already partially pinned here. `quoted:` issue #1 main flow `grilling` → `wayfinder` → `to-spec` → `to-tickets` → `implement` / `code-review`. Skills CLI: `npx skills@latest add mattpocock/skills --all --yes` (`quoted:` skills-cli.md). Then run MP's `/setup-matt-pocock-skills` so tracker docs and instruction-file blocks are *theirs*, not a fork.

2. **Handoffs from the same catalogue.** MP `handoff` is in the #5 spine list (`quoted:` #5). Wayfinder's map `Decisions so far` is the multi-session index (`quoted:` `.agents/skills/wayfinder/SKILL.md`). Git is the code handoff. That is enough. Do not resurrect `history.jsonl` / `loop-complete.json` (`quoted:` issue #1 Out of scope already rejects carrying those into v0.3 — honour it by not replacing them with equivalent AAW files).

3. **gstack only if you personally want `/ship`, `/qa`, `/design-review`, `/investigate`.** Install **whole**. `quoted:` #11: setup links every skill; no `--skills` flag; browser skills share one compiled binary. Do not fork gstack to subset. Do not rewrite `/qa` on Playwright MCP unless you want to maintain QA skills (`quoted:` #3/#10: not a shim; #10 still open). If native Playwright is enough, use the Playwright MCP you already enable and skip gstack's `$B` dialect. Strategy skills (`/office-hours`, `/plan-*-review`, `gstack-to-plans`) are already replaced by grilling + to-spec on the map (`quoted:` issue #1). Let that replacement be "don't type those commands", not a routing table.

4. **superpowers: dropped.** `quoted:` issue #1. Agree. Don't keep `using-git-worktrees` as an AAW page either; herdr worktrees are herdr-ops (`quoted:` `docs/worktree-ownership.md` is programme-specific and can shrink to a paragraph in herdr-ops).

5. **herdr** is the worker manager. `quoted:` issue #1: "no plugin API — herdr plugin means a herdr-aware skill pack, nothing more"; "Dispatch: a claude **controller session** runs the frontier query, creates the worktree, starts and prompts the worker. No dispatcher daemon." That is already the simple design. ROADMAP workstream 4 (`aaw` CLI, SQLite registry, `dispatch`/`collect`/`review`) is the opposite. Do not build it.

### How the three wants fit (no extra framework)

| Want | Mechanism |
|---|---|
| Planning in context | Grill / wayfinder / to-spec / to-tickets *are* the planning. They write GitHub issues. Agents load the skill when the user is foggy. |
| Handoffs between sessions | Map issue + closed-ticket comments + `handoff` skill + git. Worker envelope names the ticket. |
| Herdr spawn/manage | Controller in herdr: frontier query (`quoted:` `docs/agents/issue-tracker.md` wayfinding ops), `herdr worktree create`, prompt worker, wait, read. Attribution trailers in the envelope. Cross-model review = start a second worker on a different CLI against the PR. |

`docs/agents/issue-tracker.md` and `triage-labels.md` can stay **in each project** as MP's setup already expects. They are not AAW.

### What this repo becomes

Archive or freeze. Do not keep developing a configurator. Optionally publish a **gist or herdr-ops page**: "pin MP skills; envelopes carry Co-Authored-By; review on another model; don't use `.advanced-plans`." That is the entire remaining AAW-shaped object.

---

## D. What to stop doing now

### Tickets (wayfinder map #1)

If the proposal above is adopted, **do not execute the map's destination** (an AAW v0.3 spec for a skill pack + `/setup-aaw`). Close or retitle #1 as "won't build; value review".

| Issue | State now | Action |
|---|---|---|
| #1 Map: AAW v0.3 as MP-first configurator | OPEN | Close: destination withdrawn. |
| #2 Forge dependencies / GitLab | OPEN (GitHub half done) | Close unless you need GitLab this month. Wayfinder already has a markdown fallback (`quoted:` issue-tracker.md). |
| #3 Native browser tooling | CLOSED | Leave closed. Do not graduate into an AAW rewrite (#10). |
| #4 Gate implementation | CLOSED | Leave closed. Do not build `run-gate-pr`. |
| #5 Routing block rewrite | CLOSED | Do not implement the lifecycle table. |
| #6 Gate operating model | OPEN | Close: answered by herdr-ops one-liner, not a ticket. |
| #7 Herdr worker ops on tracker | OPEN | Close: put claim comment + race "re-query after assign" in issue-tracker.md **in projects that use herdr**, or in herdr-ops. Not an AAW component. |
| #8 Manifest re-target | CLOSED | Do not implement four-component detect.py. |
| #9 `/setup-aaw` prototype | CLOSED | Do not productise the stub. Delete the prototype branch when convenient. |
| #10 Browser keep vs rewrite | OPEN | Close: keep gstack browse if you install gstack; otherwise use Playwright MCP without gstack QA skills. |
| #11 gstack subset | CLOSED | Do not fork gstack setup. |
| #12 skills CLI | CLOSED | Useful facts; consume from npx, not from `/setup-aaw`. |

Do not comment on these issues from this review (`ENVELOPE-review.md` constraint). This section is advice in-repo only.

### Files / trees to stop feeding (delete or archive later; not done in this review)

- `.advanced-plans/` (143 files) — retired state store. `quoted:` issue #1. Stop appending `history.jsonl`, evidence, gate-verdicts, new phases.
- `.claude/skills/setup-with-claude/` — installs the retired stack. Stop pointing README Quick Start at it.
- `.claude/skills/gstack-to-plans/` — glue for a path v0.3 already dropped.
- `.aaw/` schema/detector and `tests/packaging/` as currently written — they encode gstack/AP/superpowers. Do not rewrite them for mp-skills.
- Root product docs that still sell the three-tool flow: `README.md`, `ARCHITECTURE.md`, `SETUP.md`, `ROADMAP.md` workstreams 2–5, `DESIGN-RATIONALE.md`. Either mark archived or replace with a short "this repo is frozen" README. Do not rewrite them into a v0.3 architecture doc.

### Workstreams to kill

`quoted:` `ROADMAP.md` workstreams **2–5**: AP adapters, multi-host routing installer, **AAW registry + CLI**, cross-host E2E release. Phase 6 is already failing its last criterion and the map retired the engine. Workstream 1A fork-sync of gstack/superpowers is only needed if you keep those as AAW-owned forks; if AAW is not a product, stop maintaining the forks for integration.

Stop the v0.3 "re-target the audit" path (#8) and stop treating blast-radius rewording of seven markdown files as a deliverable. If AAW is not a product, those files are history.

---

## E. Confidence and blind spots

**Confidence: 0.75** that "do not build v0.3 AAW" is the right call from this repo's evidence. **0.85** that v0.2 planning machinery consumed most of the git history relative to user-facing installers. Lower on herdr-ops completeness because that repo was not in the envelope.

### Not read / not present

- **`CLAUDE.md` in this worktree** — gitignored, absent. Did not see the live `## Agent skills` block.
- Full `.advanced-plans/evidence/*` and most gate-verdict JSON (sampled index + git log + issue #4 study).
- `prototype/setup-aaw` branch SKILL.md (cited from #9 only).
- Issue #5 resolution beyond the truncated first comment (jq 1200-char cap in this pass). Spine list and "drop the seven rules" were captured.
- `ARCHITECTURE.md` / `SETUP.md` beyond openings (line counts measured; blast-radius study and agy review already quoted them).
- Local `~/.claude/skills/gstack/setup` — relied on `docs/research/gstack-subset.md`.
- `~/Coding/herdr-ops` — cited by `docs/herdr-windows-operations.md`, not opened.
- Every MP skill body; read wayfinder, implement, to-tickets, prototype, research, triage in full or near-full; code-review via the earlier skill load.
- Did not run `/setup-with-claude`, packaging tests, or `aaw-audit.py`.
- Did not fetch GitLab APIs for #2.
- **advanced-planning** (addendum): read README, STRUCTURE, CLAUDE.md (through adapters/runtime), `docs/decisions.md`, `docs/concepts.md`, `docs/architecture.md` opening, `core/schemas/handoff.schema.md`, `core/agents/{worker,orchestrator,gate-reviewer}.md`, `core/state/README.md`, `constraints.json`, envelope schema header, `git log --oneline -80`. Did not read all 14 slash-command bodies, Python test suite, or every adapter.

### What would change the answer

- If herdr-ops is empty or the owner has nowhere else to put worker envelopes, a **single** herdr operations markdown in some repo is justified — still not a skill pack.
- If multiple labs must install the same stack identically, a **gist** of npx commands beats `.aaw/`.
- If cross-model review without a shared verdict file has actually let bad merges through in this programme, a tiny "different-CLI reviews the PR" checklist could stay — still not `evidence_gate.py`.
- If the owner needs AAW as a **name to teach others**, a README that says "use MP skills + herdr" is the product. The current 249-commit repo is not that README.

---

## F. Advanced-planning: keep the principles, drop the loops

**Scope:** read-only at `C:\Users\mharvey2\Coding\advanced-planning` (GitHub `MungoHarvey/advanced-planning`). `measured:` `git rev-list --count HEAD` = **261** (matches the addendum). `measured:` `VERSION` = `0.19.0`. `measured:` `core/` 34 files; `platforms/` 193 files; `platforms/claude-code/commands/` **14** slash-command files; `docs/` 18 markdown files. Recent log (`measured:` first 80) is installers, path audits, adapter expansion, vacuous-guard fixes, markdownlint — not new planning insight.

`quoted:` README introduction: long-running agents fail by context fill, scope drift, unverifiable outputs, and no resume path. The advertised fix is bounded ralph loops, inter-phase gates, three-field handoffs, per-todo skill injection, a filesystem state bus, and Opus→Sonnet→Haiku tiers.

The owner's new position (ralph loops unnecessary once herdr exists and models are stronger) matches the engine's own later patches. `quoted:` advanced-planning `CLAUDE.md` Phase 16: `/next-loop` already **skips spawning the orchestrator** via `state_manager.prepare_loop_ready` for populated loops ("~26–32k tokens saved per loop"). The two-agent pattern remains "the documented architecture" while the common path bypasses it. That is the architecture admitting the orchestrator was overhead.

### F1. Principles to keep vs mechanisms that can go

**Keep** (the general principles; each cited to a home):

| Principle | Where it lives | Why it still earns its keep |
|---|---|---|
| One skill in context per task; don't preload the catalogue | `docs/decisions.md` Decision 1; `docs/concepts.md` Targeted Skill Injection; `core/agents/worker.md` "Targeted Skill Injection Protocol" | Still true with strong models: contradictory skill text pollutes. Herdr/MP already do this by loading one `SKILL.md`. |
| Skills are instruction sets, not agents; no `model:` on skills | `docs/decisions.md` Decision 10 | Portable across claude/codex/cursor. |
| Between sessions, carry three sentences: done / failed / needed — artefacts, not effort | `docs/decisions.md` Decision 4; `core/schemas/handoff.schema.md`; `docs/concepts.md` Handoff Summary | This is the resume path. Wayfinder comments + MP `handoff` are the same idea. Do not keep four storage locations (`quoted:` handoff schema "Where Handoffs Live": loop frontmatter, CLAUDE.md, loop-complete.json, history.jsonl). |
| Don't advance on "todos complete"; check stated success criteria, on a **different** pass than the implementer | `docs/decisions.md` Decision 9; `core/agents/gate-reviewer.md` | Keep the habit. Drop verdict JSON, versioned `loops-v2.md`, self-heal, Codex extract_and_validate. |
| The controller sequences work; workers do not spawn the next worker | `docs/decisions.md` Decision 2; `docs/architecture.md` Two-Agent Pattern ("orchestrator and worker never spawn each other") | Herdr **is** that main thread. The AP "main thread" was a Claude Code session running `/next-loop`. |
| Bound the work unit (one session, explicit done) | `docs/concepts.md` Ralph Loop ("bounded unit… fixed maximum… completion conditions"); README table row "Context fills" | Keep **bounding**. The bound is a GitHub ticket / one herdr worker, not `max_iterations` on a YAML loop. |
| Don't ship repo settings that pre-approve writes | `quoted:` README §0 Permissions — `.claude/settings.json` no longer pre-approves `.advanced-plans/**` because it blocks unattended multi-agent runs | Operational, still true under herdr. |

**Drop** (exist to compensate for weaker models, missing orchestrator, or Claude-Code-only spawn rules):

| Mechanism | Home | Why it can go |
|---|---|---|
| Ralph loops, `max_iterations`, `on_max_iterations` | `core/schemas/ralph-loop.schema.md`; `docs/concepts.md` | Iteration budgets for models that wander. Herdr wait + a ticket is the bound. |
| Three-tier phase → loop → todo, Opus-for-phase | README hierarchy; `docs/architecture.md`; `docs/model-tier-strategy.md`; Decision 5 | Decision 5 assigns **by frequency to save money on Haiku**, and says skill injection "compensates for Haiku's lower baseline". That is the weak-model bargain. Today's default worker is already a strong model. |
| Orchestrator agent + `loop-ready.json` | `core/agents/orchestrator.md`; `core/state/` | Preparation spawn for a planner that couldn't hold the loop. AP itself fast-paths it away (`quoted:` CLAUDE.md Phase 16). Herdr's envelope is the assignment. |
| Worker protocol tied to loop files + git checkpoint-before-loop | `core/agents/worker.md` Startup Protocol | Replaced by worktree + ticket claim. |
| Filesystem state bus | Decision 3; `core/state/README.md` | Decision 3: sandboxed agents "cannot share in-memory state across spawning boundaries." Herdr shares by **writing the prompt and reading the checkout**. JSON bus is a multiplexer for people who didn't have herdr. |
| `plan-todos` / `plan-skill-identification` / `plan-subagent-identification` | `core/skills/` | Extra planning agents so weaker models get a filled YAML todo list. `to-tickets` + `implement` replace this. |
| `/next-loop --auto`, `/next-phase --auto`, 14 slash commands | `platforms/claude-code/commands/` (`measured:` 14 files) | Chaining in one Claude session because nothing else spawned workers. |
| Self-heal, frozen-criteria hashes, remediation_controller, gate-review-mode sentinels | `CLAUDE.md` Phases 12–15 | Compensates for agents gaming the gate and for review happening inside the same planning tree. A PR on another CLI does not need this. |
| Phase compaction (`complete.md`, `handoff.md`, context_meter, PreCompact) | `CLAUDE.md` compaction; `docs/phase-complete.schema.md` | Compensates for context fill **inside a long Claude Code conversation**. Herdr starts a **new** session per ticket. |
| Host adapters (claude-code, cowork, codex, opencode), install/uninstall, path_audit, ownership registry | `platforms/` 193 files | Exists so the engine can be copied into every harness. If the engine is gone, adapters are ballast. |
| `external-task-envelope.schema.json` (required: run_id, allowed_paths, forbidden_paths, acceptance_checks, …) | `core/state/external-task-envelope.schema.json` | AAW v0.2 attempt to make the bus herdr-shaped. A markdown envelope in herdr-ops is enough; this schema is the framework growing a new skin. |

`inferred:` Ralph loops were a **poor person's herdr**: serialize work, persist YAML, respawn with a three-line memory. You have herdr. Do not keep a second serializer.

### F2. Smallest portable form

**Not** a trimmed advanced-planning install. **Not** two or three AP skills (`phase-plan-creator` etc. only make sense with loops).

**One instruction-file section, ~80–120 lines, copied into `CLAUDE.md` and/or `AGENTS.md` at the repo root** (every target harness already reads at least one of those). Optionally the **same text** as `.agents/skills/working/SKILL.md` (~same length) so Cursor/Codex skill discovery picks it up without a slash command — **one file, two placements if you want both**, not two different doctrines.

Contents, and only these:

1. Bound: one ticket (or one PR) per worker session; stop when the ticket's question is answered.
2. Load at most one specialist skill for the current task; don't dump the catalogue.
3. On finish, write done/failed/needed (one sentence each) as the GitHub/GitLab comment or PR summary — `quoted:` rules from `handoff.schema.md` Writing Rules 2–5, without the YAML-in-loops.md part.
4. Implementer does not mark the map/PR done; a **different CLI** reviews against the ticket's acceptance lines.
5. Workers do not spawn the next worker; the human/herdr controller does.
6. Commit trailers as in `docs/agents/worker-attribution.md` (AAW), injected by the envelope.

**Where it lives so it travels:**

- **Between repos:** paste into that repo's `AGENTS.md` (or `CLAUDE.md`). No installer, no `.advanced-plans/`, no `core/`.
- **Between harnesses:** AGENTS.md is the portable name; Claude also reads CLAUDE.md — duplicate the same fenced section if both files exist (AAW already learned dual-file pain; keep the section short so duplication is cheap).
- **Herdr-specific spawn/wait/read:** stays in `~/Coding/herdr-ops` (already cited by AAW `docs/herdr-windows-operations.md`). Do not merge that into the portable section.

Do **not** ship `core/schemas/handoff.schema.md` as a 124-line schema with four write-targets. The portable object is the **five writing rules**, ~15 lines.

MP skills (`implement`, `code-review`, `handoff`, `wayfinder`) remain the catalogue. This section does not replace them; it is the standing bias so an agent applies them without `/new-phase`.

### F3. Silent guidance

What an agent reads **without being told:**

- `AGENTS.md` / `CLAUDE.md` at session start (harness default).
- `CONTEXT.md` if present (MP domain-modeling already says so).
- The herdr envelope (ticket URL, trailers, worktree path) — the human never types `/next-loop`.
- Skill `description` frontmatter when the harness auto-suggests skills.

What a human **never invokes:** `/plan-and-phase`, `/new-phase`, `/new-loop`, `/next-loop`, `/run-gate`, `/next-phase`, `/phase-compact`, `/loop-status`, `/check-execution`, `/model-check`, `/run-closeout`, `/sync-plans`. `measured:` those are the 14 command files. The human starts a herdr worker, or types an ordinary prompt. Cross-model review is starting a second worker, not `/run-gate`.

Silent ≠ hidden policy in Python. Silent = already in the files the agent loads first.

### F4. One small thing, not two products

**Recommend: collapse AAW and advanced-planning into that instruction section + herdr-ops.** Neither repo continues as a shipping framework.

- Advanced-planning's remaining value is Decisions 1, 4, 9, 10 and the handoff writing rules. That fits in the section in F2. The 261-commit tree (adapters, bus, gates, compaction, self-heal) does not.
- AAW's remaining value is herdr Windows lore, attribution trailers, and "don't install a planning engine." Same section, plus herdr-ops.
- A third name (`working` skill pack, `aaw-lite`, slim-AP) would be another product. Don't.

Archive both git histories for archaeology. Stop releasing `advanced-planning` 0.20 and stop the AAW v0.3 skill pack.

---

## Bottom line

The owner's suspicion is right. AAW grew a planning architecture for a stack and a model generation that the same repo is already walking away from. v0.3 keeps the organisational habit (components, setup skill, routing fence, salvaged gate) after discarding the engine. Advanced-planning is that engine: ralph loops were a multiplexer for weaker models and for not having herdr. You have herdr and stronger models.

Keep: one skill per task, three-sentence handoff, different-CLI review, controller sequences workers. Put that in ~100 lines of `AGENTS.md`. Pin Matt Pocock. Stop both products.
