# Phase 2: v0.1 Smoke-Findings Fix-Pack

## Objective
Resolve the five v0.1 smoke-test findings and land held Fix 1 by fixing each in its source-of-truth repo and redeploying, so the integration's global installs match their sources and the uninstall path is clean.

## Scope

### Included:
- Group A — refresh the two stale global deployments (`setup-with-claude`, `phase-goals-agent`) and extend `setup-with-claude --refresh` to re-fetch the canonical skill + re-run sub-package installers (the durable anti-drift fix).
- Group B — fix the meta-project `setup-with-claude` `--uninstall` to (a) remove globally-installed glue, (b) delete an emptied `CLAUDE.md`.
- Group C — document the PostToolUse hook session-restart caveat.
- Fix 1 — fast-forward merge the advanced-planning `STRUCTURE.md` branch (`fa799d3`) into fork `main`.
- Update `tests/v0.1-smoke-report.md` findings section to reference resolution.

### Explicitly NOT included:
- Symlink-based installs (rejected approach B) — fragile across the four-tool mix / Windows.
- Version-stamp + verify machinery (rejected approach C) — v0.2+ if ever.
- Public-upstream promotion of any fix — separate explicit v0.2+ decision.
- Multi-runtime support — v0.2+ ROADMAP item.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Extended `--refresh` + fixed `--uninstall` | Markdown (SKILL.md) | `.claude/skills/setup-with-claude/SKILL.md` |
| Hook-restart caveat note | Markdown | setup post-install message + `SETUP.md` |
| Refreshed global setup skill | Deployed file | `~/.claude/skills/setup-with-claude/SKILL.md` |
| Refreshed `phase-goals-agent` copy | Deployed file | (runtime registration path — located in loop 003) |
| Fix 1 merged | git merge | `MungoHarvey/advanced-planning` `main` |
| Updated findings status | Markdown | `tests/v0.1-smoke-report.md` |

## Success Criteria

- ✓ `~/.claude/skills/setup-with-claude/SKILL.md` is the 4-tool version: `grep -c` for `--uninstall`, `integrations.json`, and `aaw-routing` each return ≥1; header no longer says "Three tools".
- ✓ The runtime `phase-goals-agent` declares `Write` in its tools line and can write its own verdict without the main-thread contingency.
- ✓ `setup-with-claude --refresh` section documents re-fetching the canonical skill and re-running detected sub-package installers, with a change report.
- ✓ `setup-with-claude --uninstall` section instructs removing globally-installed glue and deleting an emptied/whitespace-only `CLAUDE.md` (with a guard against deleting a non-empty file).
- ✓ The hook-restart caveat appears where a first-time installer will see it.
- ✓ `MungoHarvey/advanced-planning` `main` contains the STRUCTURE.md fix; the feature branch is merged (ff).
- ✓ `tests/v0.1-smoke-report.md` findings section marks #1–#5 resolved (or #5 documented) and references this phase.

## Dependencies

### Must Complete Before This Phase:
- Phase 1 (meta-project build + v0.1 smoke test PASS) — provides the findings and the verified four-tool source. Complete.

### Blocked By:
- Nothing. All source-of-truth repos are local and current; the meta-project main is pushed.

### Optional (nice to have):
- ssh-agent fix for SSH pushes — not required; HTTPS-via-GCM works for meta-project, and advanced-planning push uses its own configured remote.

## Skills Required (Broad Categories)
- `markdown-editing`: editing SKILL.md / SETUP.md / report prose.
- `git-operations`: ff-merge + push in the advanced-planning fork.
- `shell/deploy`: cp / locate / verify global install refresh.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| `phase-goals-agent` runtime copy hard to locate | Medium | Medium | Loop 003 step one is an explicit search across all Claude agent load paths; fork main is the known-good source to copy from. |
| Refreshed global setup-with-claude predates the new `--refresh`/`--uninstall` edits | Medium | Medium | Sequencing: loop 003 (deploy) runs only after loop 001 (source edits) lands. |
| `--uninstall` deletes a CLAUDE.md that still has user content | Low | High | Explicit guard: delete only if file is empty/whitespace-only after block removal. |
| Fix 1 merge conflicts with advanced-planning main | Low | Low | Branch is a docs-only fast-forward from a recent main; verify ff before merge. |

## Assumptions
- `Fork main is correct for phase-goals-agent`: validated — `git show main:platforms/claude-code/agents/phase-goals-agent.md` shows `tools: Read, Glob, Grep, Write` (commit `ce37ebe`).
- `Global setup-with-claude refresh is a file replace`: validated — SETUP.md Step 1 installs it via a single curl to one path; a local `cp` is equivalent and deterministic.
- `Fix 1 is fast-forwardable`: the fork is checked out on the branch at `fa799d3`, one docs commit ahead of a recent main.

## Notes / Design Decisions
- **Extend `--refresh` (approach A)** chosen over symlink (B) and version-stamp (C): lowest new surface, reuses existing curl/install.sh machinery, single UX entry point, stays in the "instructions Claude reads" model. (User decision, 2026-06-05.)
- **Fork-first**: every fix lands in its source repo (`MungoHarvey/Advanced-AI-Workflows` or `MungoHarvey/advanced-planning`); no public-upstream targeting. See `feedback-fork-default-target` memory.
- **Loop ordering**: 001 (meta source edits) → 003 (redeploy, depends on 001). 002 (Fix 1) is independent and slots between for a clean, atomic fork change.

## Ralph Loops (3)

| Loop | Name | Type | Key Outputs |
|------|------|------|-------------|
| 001 | meta-source-fixes | Implementation | Extended `--refresh` (1c), fixed `--uninstall` global-glue removal (2a) + empty-CLAUDE.md deletion (2b), hook-restart doc note (#5) — committed + pushed to meta `main` |
| 002 | land-fix-1 | Migration | advanced-planning `STRUCTURE.md` branch ff-merged into fork `main` and pushed |
| 003 | redeploy-and-verify | Implementation | Global `setup-with-claude` refreshed (1a), `phase-goals-agent` runtime copy located + refreshed (1b), success criteria verified, `v0.1-smoke-report.md` findings marked resolved |
