# Deferred: Upstream PRs

Two upstream-PR branches were prepared during phase-1 (ralph-loops 004 and 005). PR 2 (superpowers) shipped on 2026-06-04 — see https://github.com/obra/superpowers/pull/1684. PR 1 (advanced-planning) is held until after the v0.1 smoke test in case REG-1..6 reveals additional stale STRUCTURE.md references worth folding into the same diff.

These are real fixes — both correct stale-path bugs that contradict advanced-planning v0.11.0. They should ship, but the decision to push is the user's, not Claude's.

## Status

Both branches exist locally only. No `git push`, no `gh pr create` has been run. The branches will rot if left indefinitely — recommended action is either push within the next two weeks or formally re-confirm deferral.

---

## Branch 1 — advanced-planning STRUCTURE.md path fixes

**Repo:** `C:\Users\mharvey2\Documents\Coding\advanced-planning\`
**Branch:** `meta-project/fix-structure-md-stale-paths`
**Commit:** `fa799d3`
**Diff size:** +20 / -16, single file (`STRUCTURE.md`)

**Why:** `STRUCTURE.md` still documents the pre-v0.11.0 `plans/` layout. The current runtime root is `.advanced-plans/`. The stale doc misleads anyone reading the repo to understand the system. Specific stale references corrected:

- lines 127–140: `plans/` block → `.advanced-plans/`
- line 153: naming-table entry
- line 157: `plans/gate-verdicts` → `.advanced-plans/gate-verdicts`
- line 164: `.claude/plans/` → `.advanced-plans/`

**Push command (when ready):**

```bash
cd C:\Users\mharvey2\Documents\Coding\advanced-planning
git push -u origin meta-project/fix-structure-md-stale-paths
gh pr create \
  --title "docs: STRUCTURE.md — reflect v0.11.0 .advanced-plans/ layout" \
  --body "$(git log -1 --format=%B)"
```

---

## Branch 2 — superpowers brainstorming AP-default-path — **SHIPPED**

**Status:** Pushed and PR opened — https://github.com/obra/superpowers/pull/1684 (2026-06-04)
**Repo:** `C:\Users\mharvey2\Documents\Coding\planning-architectures\superpowers\`
**Branch:** `meta-project/fix-brainstorming-ap-default-path`
**Commit:** `fde9f97`
**Diff size:** +2 / -2, single file (`skills/brainstorming/SKILL.md`)

**Why:** When brainstorming detects advanced-planning is installed, it currently writes to `.claude/plans/` — the pre-v0.11.0 location. This means a fresh install + brainstorm session lands the design doc in the wrong place, invisible to all v0.11.0 tooling. Fix updates the AP-detected default from `.claude/plans/` to `.advanced-plans/specs/`.

Lines changed:

- line 30 (default-path mention)
- line 123 (AP-detection branch)
- line 125 (user-preference override) — **untouched**, preserves the free-prose override mechanism

**Push command (when ready):**

```bash
cd C:\Users\mharvey2\Documents\Coding\planning-architectures\superpowers
git push -u origin meta-project/fix-brainstorming-ap-default-path
gh pr create \
  --title "fix(brainstorming): update AP-detected default from .claude/plans/ to .advanced-plans/specs/" \
  --body "$(git log -1 --format=%B)"
```

---

## Provenance

- Decided in this session's design doc: `~/.gstack/projects/MungoHarvey-Advanced-AI-Workflows/mharvey2-main-design-20260521-144453.md` (CEO+ENG cleared, items #1A and #3A/#3b)
- Branches built in ralph-loops 004 and 005 of phase-1
- Deferral choice recorded in conversation: user selected "Prepare branches + diffs, hold off on push/PR"

## Recommended decision point

After phase-1 closeout (smoke test PASS → `/run-gate phase-1` → `/phase-compact 1`), revisit:

1. Push both branches and open PRs against upstream, OR
2. Re-confirm deferral to v0.2 and document the new target date here

Doing neither leaves the branches stale and the meta-project docs slightly contradictory to upstream behaviour.
