# Design: v0.1 smoke-findings fix-pack

**Date:** 2026-06-05
**Status:** Approved design — ready for phase planning
**Origin:** Five non-blocking findings from the 2026-06-05 live v0.1 smoke test (REG-1..7 all PASS), recorded in `tests/v0.1-smoke-report.md`, plus the held advanced-planning STRUCTURE.md fix ("Fix 1").

---

## Goal

Clear all five smoke-test findings and land held Fix 1, touching the fewest files and respecting the fork-first architecture: each fix lands in its source-of-truth repo first, then redeploys to the environment. No public-upstream promotion.

## Context

The smoke test surfaced five findings. Investigation collapsed them into three groups plus one mechanical merge:

- **Group A (stale global deployments):** the source-of-truth is already correct; the *deployed copies* drifted. Findings #1 and #2.
- **Group B (genuine logic gaps):** real edits to the meta-project `setup-with-claude` `--uninstall` procedure. Findings #3 and #4.
- **Group C (non-issue):** environmental, document-only. Finding #5.
- **Fix 1:** fast-forward merge of an already-prepared docs branch in the advanced-planning fork.

**Why Group A drifted:** installs are point-in-time copies (global `setup-with-claude` is curl'd from `raw.githubusercontent.com/MungoHarvey/advanced-ai-workflows/main/...`; sub-package agents are copied by `install.sh`). Nothing re-syncs them. `setup-with-claude` already exposes a `--refresh` mode (currently only re-detects tools) — the natural home for a sync step. Approach chosen: **extend `--refresh`** (rejected alternatives: symlink installs, version-stamp+verify — see Out of Scope).

---

## Work items

### Work item 1 — Group A: refresh stale installs + extend `--refresh`

**1a. Refresh global `setup-with-claude`.**
The stale `~/.claude/skills/setup-with-claude/SKILL.md` is the old 3-tool version (header "Three tools"; 0 occurrences of `--uninstall`/`integrations.json`/`aaw-routing`; 289 lines). Replace it with the current 4-tool source (meta-project `.claude/skills/setup-with-claude/SKILL.md`, 478 lines).
- Primary method: `cp` from the meta-project local source (deterministic, offline-safe).
- Documented method: re-run the SETUP.md Step 1 curl — now valid because the 4-tool version was pushed to main.
- **Sequencing:** perform *after* 1c so the refreshed global copy already contains the new `--refresh` and `--uninstall` logic.

**1b. Refresh stale `phase-goals-agent`.**
The runtime agent the smoke test used had `tools: Read, Glob, Grep` (no Write), a copy predating advanced-planning commit `ce37ebe` ("agent permission fixed"). The fork source — both `main` and the Fix-1 branch — already declares `tools: Read, Glob, Grep, Write`. No source change required.
- Implementation step one: **locate where the runtime copy is registered** (not in `~/.claude/agents/`, not in meta `.claude/agents/` — likely an advanced-planning `--global` install target or a project-scoped copy created during smoke REG-1).
- Then refresh that copy from advanced-planning fork `main`.

**1c. Extend `--refresh` (durable fix).**
Edit the meta-project `setup-with-claude/SKILL.md` `--refresh` path so it:
- re-fetches the canonical `setup-with-claude` skill,
- re-runs each *detected* sub-package's installer (e.g. advanced-planning `install.sh`),
- reports what changed.
This is the mechanism that prevents future silent drift. It stays within the "instructions Claude reads" model — no new executable script.

### Work item 2 — Group B: `--uninstall` fixes

Both edits land in the meta-project `setup-with-claude/SKILL.md` `--uninstall` procedure (~lines 315-405).

**2a. (#3) Global glue cleanup.** Uninstall currently removes only project-local glue. Add a step that surfaces and offers to remove the *globally*-installed glue as well, so a user who installed globally during setup can fully tear down.

**2b. (#4) Empty CLAUDE.md deletion.** When removing the fenced routing block leaves `CLAUDE.md` empty or whitespace-only, **delete the file** rather than leaving a 0-byte stub. Guard: only delete if the file is empty/whitespace after block removal; never delete a CLAUDE.md that still has other content.

### Work item 3 — #5: document the hook-restart caveat

Add a note to the setup post-install message (and/or SETUP.md): the PostToolUse hook registers at **session startup**, so after first-time `settings.json` creation a **session restart** is required before the hook fires live. Document-only; no code change.

### Work item 4 — Land held Fix 1

The advanced-planning fork is checked out on branch `meta-project/fix-structure-md-stale-paths` at `fa799d3` (STRUCTURE.md reflects the `.advanced-plans/` layout). The smoke test surfaced no new STRUCTURE.md stale-path issues, so it is clear to land.
- Fast-forward merge the branch into fork `main`, push to `MungoHarvey/advanced-planning`.
- Fork-internal only; no PR ceremony (self-authored docs fix), no public upstream.

---

## Landing map (fork-first)

| Item | Repo | Action |
|------|------|--------|
| 1c, 2a, 2b, 3 | meta-project `Advanced-AI-Workflows` | edit → commit → push |
| 1a, 1b | local environment | redeploy (cp / locate+refresh) — *after* 1c lands |
| 4 | `MungoHarvey/advanced-planning` | ff-merge branch → main → push |

## Sequencing constraints

1. Edit meta-project source (1c, 2a, 2b, 3) first; commit.
2. Then redeploy global `setup-with-claude` (1a) so it carries the new logic.
3. Locate + refresh `phase-goals-agent` (1b) — independent of the meta edits; can run in parallel.
4. Land Fix 1 (4) — independent; can run any time.

## Success criteria

- `~/.claude/skills/setup-with-claude/SKILL.md` is the 4-tool version (contains `--uninstall`, `integrations.json`, `aaw-routing`; header no longer says "Three tools").
- The runtime `phase-goals-agent` reports `Write` in its toolset and can write its own verdict (no main-thread contingency needed).
- `setup-with-claude --refresh` re-fetches the canonical skill and re-runs detected sub-package installers, reporting changes.
- `setup-with-claude --uninstall` offers to remove globally-installed glue and deletes an emptied `CLAUDE.md`.
- The hook-restart caveat is documented where a first-time installer will see it.
- advanced-planning `main` contains the STRUCTURE.md fix; the feature branch is merged.
- `tests/v0.1-smoke-report.md` findings section updated to reference resolution.

## Out of scope (deliberately)

- **Symlink installs** (rejected approach B): only advanced-planning's installer supports `--symlink`; the curl'd global skill can't be symlinked; Windows symlink perms are fragile.
- **Version-stamp + verify** (rejected approach C): most new machinery; only detects drift, still needs a refresh action; overkill for v0.1.
- **Public-upstream promotion** of any fix — separate, explicit v0.2+ decision.
- **Multi-runtime support** — v0.2+ ROADMAP item.
