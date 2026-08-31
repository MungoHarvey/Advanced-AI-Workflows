# The Plannotator deprecation did not reach the claude-code adapter

**Date:** 2026-08-31
**Found by:** controller, during post-F11 verification
**Status:** open — not fixed, because fixing it changes a branch head already approved for push

---

## The claim

Two documents assert this work is done.

`docs/plannotator-deprecation.md`, under **Scope of the change → Removed**:

> The Superpowers fork's Plannotator companion recommendation (intent **SP-4**,
> Plannotator half only; the Advanced Planning half is retained).

`ARCHITECTURE.md:166`:

> In v0.1, advanced-planning's `/plan-and-phase` Step 5b auto-detected plannotator and
> invoked `/plannotator-annotate` on the phase plan, and `setup-with-claude` installed the
> Claude Code plugin. **Both were removed** when plannotator was deprecated on 2026-08-26.

Half of that is true. `setup-with-claude` was genuinely cleaned: every one of AAW's own
live surfaces now carries a deprecation notice rather than a reference, and `.aaw/detect.py`
records plannotator in a `DEPRECATED` dict rather than a detector. AAW is clean.

Step 5b was **not** removed. It is still in advanced-planning.

---

## What is actually on disk (branch `loop-004-f7`)

| File | Line | What it does |
|---|---|---|
| `platforms/claude-code/commands/plan-and-phase.md` | 94-113 | `### Step 5b: PLANNOTATOR REVIEW (conditional)` — detects `.claude/commands/plannotator-annotate.md` and invokes `/plannotator-annotate` on the phase plan |
| `core/skills/companion-detection/SKILL.md` | 40-53 | Recommends installing it, with `git clone https://github.com/MungoHarvey/plannotator.git` |
| `core/skills/companion-detection/SKILL.md` | 3, 67 | Frontmatter description and Key Principles both name Plannotator as a companion |
| `CLAUDE.md` | 38 | describes `companion-detection` as scanning "todos for Plannotator review opportunities" |
| `core/skills/plan-skill-identification/references/skill-catalogue.md` | 169 | same description, in the catalogue the skill-assignment step reads |

This is not a stale mention. It is a live promotion: a user creating a plan without
Plannotator installed is told to clone it.

---

## Why this is the phase's own defect class

`loop-004-f7` adds two adapter READMEs that make an explicit negative claim:

- `platforms/codex/README.md:178` — "**No Plannotator**: The deprecated review companion is not installed or invoked"
- `platforms/opencode/README.md:163` — identical

Both are true of their own adapter. Neither is true of `platforms/claude-code`, whose
`plan-and-phase` command invokes it. Two adapters assert a property the third violates,
and nothing in the suite compares them — the same shape as F7, F8 and F11, discovered
the same way: by reading what the adapters actually say rather than what the record
claims they say.

Note the direction. Codex and opencode are clean not because anyone removed anything
from them, but because they were written after the deprecation. The claude-code adapter
predates it and was never revisited. A "zero Plannotator references remain" check would
pass vacuously for the two adapters that never had any.

---

## Why it is not fixed here

The fix belongs on `loop-004-f7`, because that is where the contradicting READMEs live —
neither exists on `main`. But `77ef4b3` is a head the operator has already approved for
push, on a branch whose gate findings were closed and recorded as complete. Moving it
after that record was written is the operator's call, not the controller's.

Scope of the fix, if authorised: delete Step 5b (20 lines), remove section 2 of
`companion-detection/SKILL.md` and renumber, and correct four descriptions. No code.
