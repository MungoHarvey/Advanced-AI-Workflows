# Deprecating Plannotator

**Status:** accepted amendment to the v0.2 design
**Date:** 2026-08-26
**Amends:** [`.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md`](../.advanced-plans/specs/2026-08-26-herdr-multi-runtime-orchestration-design.md) §7.4
**Decision by:** repository owner

---

## Decision

Plannotator is **deprecated as a component of Advanced AI Workflows**. It is removed from the
installed stack, from the routing contract, and from the documented setup path.

The human review gate it provided moves to a **cross-model gate reviewer**: a reviewer agent
running on a different model from the implementer, whose findings must be resolved or explicitly
waived by a human before a phase can advance.

The stack goes from four tools to three:

| Before | After |
|---|---|
| gstack + advanced-planning + superpowers + plannotator | gstack + advanced-planning + superpowers |

This is a **minor** version bump under [docs/releasing.md](releasing.md) — a component is
deprecated, but no documented install path is broken for existing users, who simply keep whatever
Plannotator install they already have.

---

## Why

### 1. It was the weakest link on the target platforms

The v0.2 design commits AAW to four agent runtimes. Plannotator's review integration degrades
sharply across them, and §7.4 of the design had already been reduced to a table of fallbacks:

| Host | Plannotator review path in the design |
|---|---|
| Claude Code | plugin/hook, plus a direct command fallback |
| OpenCode | plugin, plus a direct command fallback |
| Codex | **no automatic review** — upstream documents Codex hooks as disabled on native Windows |
| Cursor | **no integration** — terminal command only |

On half the target runtimes the "integration" was a human being told to run a command. The design's
own non-goals forbid claiming a review path upstream does not provide, so the honest version of
§7.4 was already: *one gate mechanism, two hosts, two manual workarounds.*

### 2. A stronger gate was already required

ACC-18 already requires that "the gate reviewer is a different model from the implementer, and
findings are resolved or explicitly waived by a human". That is a **stricter** gate than visual
annotation: it is adversarial, it is automatable, it runs identically on all four runtimes, and it
produces a machine-readable verdict that the controller can record as evidence.

Once ACC-18 is implemented, Plannotator is a second, weaker, host-dependent gate sitting alongside
a stronger host-neutral one. Keeping both means maintaining four fallback paths for a mechanism
that no longer carries the decision.

### 3. Version drift with no owner

Three different Plannotator versions are live on the development machine simultaneously:

| Location | Version |
|---|---|
| `MungoHarvey/plannotator` fork | 0.19.21 |
| Installed Claude plugin | 0.15.5 |
| Upstream `backnotprop/plannotator` | 0.27.8 |

The fork carries **zero** fork-only commits — it is a clean ancestor with no AAW-specific change.
It exists only to be synced. That is pure maintenance cost for no differentiated behaviour: AAW
was carrying a fork-sync workstream for a component it had never modified.

### 4. It removes a workstream rather than adding one

Deprecation is net-negative work. Workstream 1A drops from three fork syncs to two. The §7.4
per-host fallback matrix, and the Workstream 2 and 3 exit-gate criteria that depend on it,
disappear rather than needing implementation.

---

## What replaces it

**A cross-model gate reviewer**, as the single human-review mechanism at phase boundaries.

| Property | Requirement |
|---|---|
| Reviewer model | Must differ from the model that implemented the work. |
| Input | The phase's changed-path list, diff, check output, and the phase plan's success criteria. |
| Output | A structured verdict — pass, fail, or findings — written to `.advanced-plans/gate-verdicts/`. |
| Human role | Every finding is resolved or **explicitly waived by a human**. A waiver is recorded with its reason. |
| Advancement | A phase advances only after the verdict is recorded and outstanding findings are closed. |
| Host neutrality | Identical on Claude Code, Codex, OpenCode, and Cursor — no host-specific hook required. |

Advanced Planning's `/run-gate` already spawns gate agents and writes verdicts to
`.advanced-plans/gate-verdicts/`, and the phase-2 record shows a Codex reviewer catching a defect a
same-model reviewer had missed. The mechanism is proven in this repository; what v0.2 adds is
making the *different-model* property mandatory rather than incidental, and making the human waiver
step explicit.

This preserves design principle 9 — *human review at irreversible boundaries* — with a gate that is
stronger, uniform across hosts, and produces evidence rather than an annotation session.

---

## Scope of the change

### Removed

- Plannotator from the installed component set and from `setup-with-claude`.
- `references/install-plannotator.md` install instructions.
- Plannotator detection and routing lines from the CLAUDE.md routing template.
- Plannotator from `docs/upstream-sync-playbook.md` — no longer a synced fork.
- The Superpowers fork's Plannotator companion recommendation (intent **SP-4**, Plannotator half
  only; the Advanced Planning half is retained). See §2.4.1 of the baseline audit.

### Retained unchanged

Historical records are **not** rewritten. Plannotator was genuinely part of v0.1 and the record
must continue to say so:

- `.advanced-plans/phases/phase-1/` and `phase-2/` — phase plans and loop records.
- `.advanced-plans/programme-closeout.md` — the v0.1 programme narrative.
- `tests/v0.1-smoke-report.md`, `tests/v0.1-smoke-test-runbook.html` — v0.1 test evidence.
- `references/upstream-baseline-2026-08-26.json` — a dated snapshot; snapshots are not edited.
- The v0.2 design spec — amended by *this document*, not by silent edits to its text.
- The `v0.1.0` tag and its changelog entry.

### Not affected

- The `MungoHarvey/plannotator` fork on GitHub. It is left as it is. Deprecation is a decision
  about **this** project's dependencies, not a deletion of the fork.
- Any existing Plannotator install on a user's machine. Nothing is uninstalled. `setup-with-claude
  --uninstall` removes AAW's own artefacts, and no longer touches Plannotator either way.

---

## Migration for existing users

If you installed the v0.1 four-tool stack, nothing breaks. Plannotator keeps working as a
standalone tool; AAW simply stops installing, detecting, and routing to it.

To align with the three-tool stack:

1. Re-run `setup-with-claude --refresh`. The regenerated CLAUDE.md fenced block no longer contains
   Plannotator routing.
2. Optionally remove the plugin: `/plugin uninstall plannotator@plannotator`.
3. Optionally remove `~/.claude/commands/plannotator-*.md`.

Steps 2 and 3 are optional and reversible. If you like Plannotator, keep it — it just is not part
of this stack's contract any more.

---

## Consequences accepted

- **A visual annotation workflow is lost.** Reviewing a plan in a browser UI is a genuinely
  different experience from reading a reviewer's structured verdict. Users who value it should keep
  Plannotator installed independently.
- **The gate now depends on model availability.** A cross-model reviewer needs a second runtime
  configured. On a machine with only one provider, the gate degrades to same-model review, which
  must be recorded as such in the verdict rather than silently accepted.
- **This is reversible.** Nothing is deleted upstream and the fork is untouched. If the cross-model
  gate proves insufficient in practice, Plannotator can be reinstated as an optional review path
  without recovering anything.
