# Fork-internal fixes (formerly "upstream PRs")

Two fix branches were prepared during phase-1 (ralph-loops 004 and 005) to correct stale-path references contradicting advanced-planning v0.11.0. Scope decision: these land in **our forks/repos only** — no PRs against external upstreams (e.g. `obra/superpowers`) for v0.1. Promotion to public upstreams is an explicit, separate decision deferred to v0.2 or later.

## Status summary

| Fix | Target repo | Status | Reference |
|-----|-------------|--------|-----------|
| Fix 1 — STRUCTURE.md path layout | `MungoHarvey/advanced-planning` (standalone, not a fork) | Held | Local branch `meta-project/fix-structure-md-stale-paths` @ `fa799d3` |
| Fix 2 — brainstorming AP-default path | `MungoHarvey/superpowers` (fork of obra/superpowers) | **Shipped to fork main** (2026-06-04) | Merged ff-only as `fde9f97`; upstream PR `obra/superpowers#1684` closed |

---

## Fix 1 — advanced-planning STRUCTURE.md path fixes — **HELD**

**Held until:** after v0.1 smoke test (REG-1..6) in case additional stale STRUCTURE.md references surface and should be folded into the same diff.

**Repo:** `C:\Users\mharvey2\Documents\Coding\advanced-planning\` → `MungoHarvey/advanced-planning` (standalone, no parent — PR is internal)
**Branch:** `meta-project/fix-structure-md-stale-paths`
**Commit:** `fa799d3`
**Diff size:** +20 / -16, single file (`STRUCTURE.md`)

**Why:** `STRUCTURE.md` still documents the pre-v0.11.0 `plans/` layout. The current runtime root is `.advanced-plans/`. Specific stale references corrected:

- lines 127–140: `plans/` block → `.advanced-plans/`
- line 153: naming-table entry
- line 157: `plans/gate-verdicts` → `.advanced-plans/gate-verdicts`
- line 164: `.claude/plans/` → `.advanced-plans/`

**Ship command (post-smoke-test):**

```bash
cd C:\Users\mharvey2\Documents\Coding\advanced-planning
git push -u origin meta-project/fix-structure-md-stale-paths
# Then either open a fork-internal PR for review record:
gh pr create \
  --title "docs: STRUCTURE.md — reflect v0.11.0 .advanced-plans/ layout" \
  --body "$(git log -1 --format=%B)"
# Or, since it's your own repo and a 1-file doc fix, fast-forward into main directly:
git checkout main && git merge --ff-only meta-project/fix-structure-md-stale-paths && git push origin main
```

---

## Fix 2 — superpowers brainstorming AP-default-path — **SHIPPED**

**Status:** Merged into `MungoHarvey/superpowers` main as `fde9f97` on 2026-06-04. Feature branch deleted locally and on remote. Upstream PR `obra/superpowers#1684` was opened in error and closed.

**Repo:** `C:\Users\mharvey2\Documents\Coding\planning-architectures\superpowers\` → `MungoHarvey/superpowers` (fork of `obra/superpowers`)
**Merged commit:** `fde9f97`
**Diff size:** +2 / -2, single file (`skills/brainstorming/SKILL.md`)

**What it fixed:** when brainstorming detected advanced-planning installed, it wrote design docs to `.claude/plans/` (the pre-v0.11.0 location). Now writes to `.advanced-plans/specs/`. The user-preference override branch on the following line is preserved bit-for-bit.

**Promotion-to-upstream decision:** deferred to v0.2 or later. If we want this fix in public `obra/superpowers`, re-open a PR from a fresh branch off `MungoHarvey:main` then. For v0.1 the meta-project only consumes our fork, so no upstream dependency exists.

---

## Provenance

- Decided in this session's design doc: `~/.gstack/projects/MungoHarvey-Advanced-AI-Workflows/mharvey2-main-design-20260521-144453.md` (CEO+ENG cleared, items #1A and #3A/#3b)
- Branches built in ralph-loops 004 and 005 of phase-1
- Initial deferral: user selected "Prepare branches + diffs, hold off on push/PR"
- Scope clarification (2026-06-04): user clarified these are fork-internal only, not for upstream promotion in v0.1

## Recommended decision point

After phase-1 closeout (smoke test PASS → `/run-gate phase-1` → `/phase-compact 1`), revisit Fix 1:

1. Ship to `MungoHarvey/advanced-planning` main (fast-forward merge or internal PR), OR
2. Fold in any new stale references discovered during smoke test, then ship

Promotion of either fix to public upstream (`obra/superpowers`, etc.) is a separate v0.2+ decision.
