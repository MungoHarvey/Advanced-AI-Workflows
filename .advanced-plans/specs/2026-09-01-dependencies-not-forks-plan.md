# Dependencies, not forks — execution plan

**Status:** PROPOSED. Not accepted, not scheduled, nothing implemented.
**Date:** 2026-09-01
**Amends:** [`2026-08-26-herdr-multi-runtime-orchestration-design.md`](2026-08-26-herdr-multi-runtime-orchestration-design.md) §8, §13.1, §13.2, §13.3
**Relates to:** Phase 7 (routing and installer), Phase 9 (§13.2 half only). **Not** Phase 8.

---

## 1. The problem, in the owner's words

> "Editing forks and the packaged dependencies requires constant updating to the specific tools
> inside those but that can be clunky and could require heavy adjustment each update. I wonder if
> our main package can help configure each of these together rather than specific edits to the
> packages? That way these can be dependencies."

The intuition is correct and it is already the design's stated intent. What follows is a plan to
close the gap between that intent and what is actually on disk.

## 2. What is actually true today

Measured 2026-09-01 against the working copies on this machine, not inferred from the design.

| Component | Fork state in substance | Local patch | Verdict |
|---|---|---|---|
| **gstack** | true `mirror` | **none** | Already a dependency. Not the problem. |
| **superpowers** | `patch` | **73 insertions, 2 files** | **This is the entire problem.** |
| **advanced-planning** | `owned` | n/a | A dependency AAW installs; no upstream to track. |
| **plannotator** | deprecated 2026-08-26 | n/a | Out of the stack. |
| **AAW** | `owned` | n/a | The integrator. |

**The finding that reframes the work: there is only one fork patch, and it is 73 lines.**

The installed gstack (`~/.claude/skills/gstack`, v1.60.1.0) sits exactly at `origin/main` from
`garrytan/gstack` — zero fork-only commits, zero net diff, one modified generated file
(`gstack/llms.txt`). Updating it costs nothing today. The `MungoHarvey/gstack` fork exists as a
remote and carries nothing that is needed.

Superpowers is the exception, and it is worse than merely being a patch:

```
fde9f97 fix(brainstorming): update AP-detected default from .claude/plans/ to .advanced-plans/specs/
b874847 Merge pull request #1 from obra/main
f2d65a6 feat: use AskUserQuestion tool for brainstorming questions
dfd7ff5 feat: conditional integration with Advanced Planning and Plannotator

 skills/brainstorming/SKILL.md     | 61 ++++++++++++++++++++++++++++++-----
 skills/using-superpowers/SKILL.md | 22 +++++++++++++-
```

**That patch is already stale in two independent ways**, which is the clunkiness the owner
describes, arriving on schedule:

1. It advertises **Plannotator** to the user as a companion tool to install. Plannotator was
   deprecated from this stack on 2026-08-26. The fork still recommends it.
2. It detects Advanced Planning by **Claude-only paths** —
   `.claude/commands/plan-and-phase.md` and `.claude/skills/phase-plan-creator/SKILL.md`. The
   design forbids exactly this (§13.3: detect "through a manifest or `aaw doctor`, not Claude-only
   paths"), because it makes the integration invisible to Codex, OpenCode and Cursor, and because
   a stale directory left behind by an uninstall reads as a live installation.

So the patch is not a working local customisation that merely costs maintenance. It is 73 lines
that are **already wrong**, and no mechanism exists that would have told us.

### 2.1 What is missing on the AAW side

| Artefact | Specified in | Exists? |
|---|---|---|
| `.aaw/project.toml` | §8 | **No** |
| Compatibility manifest (tested tag + SHA) | §13.2 | **No** |
| Root `AGENTS.md` | Phase 7 | **No** |
| Root `CLAUDE.md` fenced block | Phase 7 | **No** |
| Component detection | — | Yes, but **descriptive and hardcoded** |

`.aaw/detect.py` reports what happens to be installed by probing sentinel paths listed as Python
literals in `component_specs()`. It is honest about what it finds. But **the component list is
itself hardcoded in a package file** — the same clunkiness the owner is describing, one level up.
Adding or retiring a component means editing Python.

`references/upstream-baseline-2026-08-26.json` is the compatibility manifest's ancestor: a dated
snapshot, self-marked `refresh_required_before_execution: true`, which still records
advanced-planning at `v0.16.0` (it is now `v0.19.0`). It records divergence counts but not the
things §13.2 requires — tested tag, adapter version, install method per host, or the date and
result of the compatibility suite.

And `docs/upstream-sync-playbook.md` §11 step 4 instructs the operator to "update AAW's
compatibility manifest" — **an artefact that does not exist.** A documented step that cannot be
performed is the same defect class this programme has spent three releases removing.

## 3. The constraint that decides the design

The seam is **overlay-by-adjacent-file, not setting-a-setting.**

Almost none of these tools expose a configuration hook for the behaviour AAW needs to change:

- **herdr** regenerates its `SKILL.md` verbatim from the binary on every upgrade, so an edit there
  is destroyed by the next `herdr --skill`. The working override lives in the user's `CLAUDE.md`
  and says so explicitly. **This is a proven overlay on this machine** and is the model for the
  rest.
- **gstack** skills have no documented override hook.
- **superpowers** routing lives in a `SKILL.md`, which is why the current answer was to edit it.

Therefore the universal seam is the **project instruction file** (`CLAUDE.md` / `AGENTS.md`) plus
an **AAW-owned skill installed alongside** the dependency. Per-tool configuration is the
exception, not the rule — and which tools are exceptions has never been written down. Stage 0
exists to write it down, because it is cheap and it decides everything after it.

## 4. Non-goals

- **The `aaw` registry and CLI (Phase 8).** The kickoff prompt is explicit: do not implement it
  yet. Nothing here depends on it. Where this plan needs a command it uses `aaw doctor`'s
  behaviour, which can be a script until Phase 8 gives it a home.
- **Vendoring dependencies into AAW.** Pinning is not copying.
- **Contributing the superpowers behaviour upstream.** Desirable, tracked separately in
  `deferred-v0.2/upstream-prs.md`; not a prerequisite.
- **Touching gstack.** It is already a mirror. Leave it alone.

---

## 5. The plan

Five stages. Each has a gate that must be satisfied by evidence, not by review.

### Stage 0 — Inventory the seams (read-only)

**Why first:** every later stage assumes a seam exists. That assumption has never been tested,
and if a tool has no seam, its behaviour cannot move to the AAW boundary and the honest answer is
a documented patch rather than a pretence.

For each of gstack, superpowers, advanced-planning, herdr, and each target host (Claude Code,
Codex, OpenCode, Cursor), establish and record:

- a config file it reads, if any, and whether an upgrade preserves it;
- an environment variable it honours;
- a hook or extension directory;
- an adjacent-file overlay that survives upgrade;
- or **nothing** — in which case that is the finding.

**Deliverable:** `docs/config-seams.md` — one row per tool, each cell citing the file, flag, or
command that proves it, and each "nothing" citing what was tried.

**Gate:** every row cites evidence. A row reading "probably supports X" fails the gate.

**Cost:** hours, read-only, no external writes.

### Stage 1 — Make the manifest the source of truth

Two files, one principle: **AAW declares, the installer obeys, and nothing is hardcoded in
Python.**

1. `.aaw/project.toml` — schema, parser, and validation, per §8. Component entries carry
   repository, upstream, fork state (`mirror` / `patch` / `owned`), and the sentinel by which the
   component is detected.
2. `.aaw/compatibility.json` — generated, per §13.2: repository URL, upstream URL, **tested tag
   and full commit SHA**, adapter version, installation method per host, and the date and result
   of the compatibility suite that produced it.
3. `detect.py` reads its component list from the manifest instead of `component_specs()`
   literals.

**The single most important rule in this stage:** the compatibility manifest is **generated by
the suite that tested it**, never hand-edited. A hand-maintained manifest drifts, and a drifted
manifest reports a tested SHA that nobody tested — a check that reports something nobody measured,
which is the exact defect class of the last three releases.

**Gate:**

- ✓ `detect.py` produces byte-identical output before and after the refactor, on a machine where
  the components are installed — proving the manifest replaced the literals faithfully.
- ✓ Deleting a component from the manifest removes it from the audit output; adding one adds it.
  **Both directions tested**, so the manifest is shown capable of changing the answer.
- ✓ A manifest whose recorded SHA does not match the installed tree is **reported as drift**, and
  a test proves it can report drift by inducing it.

### Stage 2 — Move the 73 lines to the AAW boundary

This is the stage that turns superpowers from a fork into a dependency. It runs in the order
below and not in any other order.

1. **Write the behaviour matrix as tests, against the patched fork, and watch them pass.**
   `docs/upstream-sync-playbook.md` §6 already specifies the matrix: Advanced Planning absent;
   installed via manifest; stale `.advanced-plans/` only; Claude Code; Codex/OpenCode/Cursor; and
   upstream's three-path router retained in all cases. Tests written after the patch is removed
   would only prove that the new thing does what the new thing does.
2. **Build the AAW-owned replacement** — a routing skill installed to both `.agents/skills/` and
   `.claude/skills/`, plus the fenced `AGENTS.md` / `CLAUDE.md` block. Detection goes through the
   manifest from Stage 1. The Plannotator recommendation is **dropped**, not ported.
3. **Run the same tests against upstream superpowers + the AAW boundary.** They must pass
   unchanged. Any behaviour that cannot be expressed at the boundary is documented as a retained
   patch with its reason, per §13.3 — an honest patch, not a hidden one.
4. **Retire the fork patch**: reset `MungoHarvey/superpowers` to a clean mirror of
   `obra/superpowers`, on a reviewed PR, with the pre-sync head preserved as a backup tag per
   playbook §2.

**Gate:**

- ✓ The matrix tests pass against the patched fork **and** against mirror + boundary. Two runs,
  both recorded.
- ✓ `git diff upstream/main...HEAD` on the superpowers fork is **empty**, or every surviving
  hunk is named in the manifest with its §13.3 justification.
- ✓ No detection path in the shipped result contains `.claude/` for a non-Claude host — checked
  by a test, not by reading.
- ✓ A stale `.advanced-plans/` directory with no installation reads as **absent**.

### Stage 3 — Pin, and refuse to drift silently

- Installers default to the tested manifest, **not floating `main`** (§13.2).
- `aaw doctor --latest` reports newer upstream releases and **must not silently upgrade**.
- The fenced-block contract test: user-authored content placed immediately above and below the
  fences survives install, refresh, and uninstall **byte-identically**. Phase 7 already names this
  as its highest-consequence test and says to write it first; that instruction stands.

**Gate:**

- ✓ A fresh clone installs the pinned SHAs, and the resulting tree matches the manifest.
- ✓ `--latest` reports an available upgrade without performing one — proven by running it against
  a deliberately outdated pin.
- ✓ The fenced-block test fails when the guard is removed. Restore-and-rerun, the discipline used
  throughout 0.19.0.

### Stage 4 — Close the documentation gaps this opens

- `docs/upstream-sync-playbook.md` §11 step 4 now names a manifest that exists.
- `references/upstream-baseline-2026-08-26.json` is superseded by the generated manifest, or
  regenerated and dated. It currently records advanced-planning at `v0.16.0`; the released
  version is `v0.19.0`.
- `docs/config-seams.md` from Stage 0 becomes the reference the routing block cites.
- README / ARCHITECTURE / SETUP describe what was observed. Every integration claim cites the
  test that exercised it.

**Gate:** ✓ No document instructs an operator to use an artefact or command that does not exist.
Checked by walking every imperative step in `docs/`, not by reading for tone.

---

## 6. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The compatibility manifest becomes a check that cannot fail | **High** | **High** | Generated by the suite, never hand-edited; a test induces drift and asserts it is reported |
| Removing the superpowers patch silently loses behaviour | Medium | High | Matrix tests written first and passing against the patched fork **before** removal |
| Fenced-block rewriting eats user-authored content | Medium | **High** | Byte-identical survival test across install / refresh / uninstall, written first |
| Stage 0 finds most tools have no seam | Medium | Medium | That is a finding, not a failure: the boundary approach then applies universally and per-tool config is dropped from scope |
| Two gstack clones diverge | **Observed** | Low | `~/Coding/gstack` is at v1.58.4.0 with no `fork` remote; the install is at v1.60.1.0. Same stale-clone class as the known `M:/Coding/planning/superpowers`. Reconcile or retire in Stage 4 |
| Scope creeps into the Phase 8 registry | Medium | Medium | Non-goal §4, restated at each gate |

## 7. What this does not fix

Pinning makes updates **deliberate**; it does not make them **free**. When upstream superpowers
redesigns its router again, the AAW routing block may still need work — the difference is that it
will be one AAW-owned file with tests, rather than a 73-line diff inside somebody else's
repository that nothing checks and that has already gone stale twice.

## 8. Sequencing against the existing programme

This is **Phase 7 plus the §13.2 half of Phase 9**. It is not a competing plan and should not
become a new phase number.

`PLANNING.md` has `current_phase: 6`, in progress. Phase 7 is written but explicitly
"Planned, not decomposed — loops are written when Phase 6 passes its gate."

Two honest options, and they are the owner's call:

1. **Decompose this into Phase 7's loops when Phase 6 gates.** Respects the existing dependency
   order. Costs nothing now.
2. **Pull Stage 0 forward immediately.** It is read-only, it cannot break Phase 6, and it is the
   only stage whose result could change the shape of everything after it.

Stage 0 is the one piece with a genuine argument for being done out of order.
