# Superpowers behaviour matrix — 2026-08-26

**Loop**: `phase-5` / `ralph-loop-001` — todo `loop-001-2`
**Provider**: controller (Claude Opus, AAW controller checkout)
**Base evidence**: `.advanced-plans/evidence/2026-08-26-fork-divergence-reaudit.md`
(`origin/main fde9f97`, `upstream/main b36e082`, merge-base `f2cbfbe`, net patch
73 insertions / 10 deletions across exactly two files)
**Governing design**: `2026-08-26-herdr-multi-runtime-orchestration-design.md`
§7.3 (host-neutral detection) and §13.3 (Superpowers migration decision)

---

## What this document is for

The fork's net patch is two files. Two files is small enough to copy and large
enough to misread. This matrix decomposes it into the four things it actually
*does*, so implementation works from stated intent rather than from inferring
purpose out of a diff. Each intent gets a port / do-not-port verdict, and every
do-not-port verdict names where that behaviour goes instead.

Nothing here is implementation. The verdicts are the specification that
`ralph-loop-002` implements, and that `loop-001-4` reviews before it may start.

---

## The four intents

### SP-1 — Design-document location

**What it does.** Routes the design document that `brainstorming` produces to
`.advanced-plans/specs/YYYY-MM-DD-<topic>-design.md` when Advanced Planning is
present, instead of upstream's `docs/superpowers/specs/`.

**Where it lives.** `skills/brainstorming/SKILL.md`. Introduced by fork commit
`fde9f97`, which describes it as changing the *AP-detected default*.

**Detection.** Existence of `.claude/skills/phase-plan-creator/SKILL.md`.

**Verdict: PORT — as behaviour, into AAW-owned routing, not into the fork.**

**Reason.** This is AAW policy about where AAW keeps its own artefacts. It has
no business being maintained as a patch on somebody else's skill file, and it is
the exact case design §13.3(2) describes: a small AAW routing block that names
AAW's own conventions. The `.claude/…` probe must be replaced by the
installation manifest (§7.3) — see *Dependency* below.

---

### SP-2 — Terminal-state routing

**What it does.** Changes where `brainstorming` hands off when it finishes: to
`phase-plan-creator` when Advanced Planning is present, rather than upstream's
`writing-plans`. The fork applies this in four places within the one file — the
numbered step list, the flow digraph, the terminal-state prose, and the
Implementation section — which is why a naive partial port would leave the skill
self-contradictory.

**Where it lives.** `skills/brainstorming/SKILL.md`.

**Detection.** Existence of `.claude/skills/phase-plan-creator/SKILL.md`.

**Verdict: PORT — as behaviour, into AAW-owned routing, not into the fork.**

**Reason.** Same argument as SP-1, and the same manifest substitution.

**Constraint added by `loop-001-3`** (see
`2026-08-26-upstream-superpowers-drift.md`). At the merge-base, `brainstorming`
had one path and one terminal state, so "redirect the terminal state" was
unambiguous. Upstream v6.3.0 now runs a **three-path router** — Spike, Bounded,
Architectural — with three distinct terminal states, and only the Architectural
path ends at `writing-plans`. Spike ends at a reported recommendation; Bounded
ends at direct implementation with no plan document at all.

**SP-2 therefore attaches to the Architectural path only.** An unconditional
redirect would pull every feasibility probe and one-file fix into a full phase
decomposition — precisely the over-process outcome upstream added the router to
prevent. The routing rule to implement is: *Architectural path + AP present ->
`phase-plan-creator`; Architectural path + no AP -> `writing-plans`; Spike and
Bounded -> untouched.*

---

### SP-3 — AskUserQuestion in brainstorming

**What it does.** Adds three inline bullets plus a roughly 25-line *"Asking
Questions with AskUserQuestion"* section, directing the brainstorming skill to
present choices as structured options rather than freeform prose. Introduced by
fork commit `f2d65a6`.

**Where it lives.** `skills/brainstorming/SKILL.md`.

**Detection.** None. It is unconditional.

**Verdict: DO NOT PORT into AAW-owned routing.**

**Where it goes instead: upstream, as a standalone contribution to
`obra/superpowers`.** It is not an Advanced Planning integration and never was —
it improves brainstorming for every Superpowers user, conditional on nothing.
Carrying it in AAW-owned routing would be a category error: AAW routing exists to
say what AAW wants, and this says nothing about AAW.

**Interim position.** It stays in the fork patch until upstream accepts or
declines it. That is the one and only intent for which `patch` state is a holding
position rather than a design decision, and it should be recorded as such in the
compatibility manifest (§13.1) so it is not later mistaken for AAW behaviour. If
upstream declines, re-open the verdict — do not silently keep it.

---

### SP-4 — Companion-tools section

**What it does.** Adds a *"Companion Tools (check once per session)"* section
telling a Superpowers session that two things exist: Advanced Planning and
Plannotator. It also adds a flow-graph diamond, `"Advanced Planning available?"`
-> `"Defer to /plan-and-phase"`. Introduced by fork commit `dfd7ff5`.

**Where it lives.** `skills/using-superpowers/SKILL.md` — the skill Superpowers
instructs an agent to read once per session.

**Detection.** Two different probes, in the same patch: the AP entry uses
`.claude/skills/phase-plan-creator/SKILL.md`, while the flow-graph diamond is
labelled `yes (.claude/commands/plan-and-phase.md exists)`. The Plannotator entry
probes `.claude/commands/plannotator-annotate.md` OR a registered plugin.

This intent splits, and the two halves get opposite verdicts.

#### SP-4a — the Advanced Planning entry

**Verdict: DO NOT PORT into the fork.**

**Where it goes instead: the fenced routing block in the host instruction file**
(`AGENTS.md` / `CLAUDE.md`), installed by `aaw init`. See *Finding 1*.

**Reason.** A companion-tools paragraph inside `using-superpowers` exists to get
AAW's routing read at session start. The host instruction file is read at session
start unconditionally, in every supported harness, and AAW's own installer owns
it. SP-4a is therefore redundant once the fenced block exists — keeping it would
mean maintaining a patch on somebody else's repository to duplicate something
AAW already controls.

*(This verdict was reversed at the `loop-001-4` gate. The first draft called
SP-4a load-bearing and the only possible hook; the reviewer showed that claim was
unfounded and the design spec already mandates the better mechanism. See
`2026-08-26-superpowers-matrix-gate-review.md` F2.)*

#### SP-4b — the Plannotator entry

**Verdict: DO NOT PORT.**

**Where it goes instead: nowhere. It is dropped.** AAW deprecated Plannotator on
2026-08-26; there is no destination for it, and that is the correct outcome
rather than an omission. Recorded explicitly so a later reader does not reinstate
it as a porting oversight.

**Consequence outside this repository.** Upstream Advanced Planning v0.16.0 ships
`core/skills/companion-detection/SKILL.md`, which still recommends Plannotator to
AP users. Dropping SP-4b here does not touch that. Raise it as a separate defect
against `advanced-planning`; it is out of scope for this loop and must not be
fixed by widening this port.

---

## Findings that change the implementation plan

### Finding 1 — the hook already exists, and it is not in Superpowers

**This finding replaces a wrong one.** The first draft argued that SP-4a was the
only possible hook point, because Superpowers has no override mechanism and
skills take effect only when an agent is told to read them — so AAW-owned routing
could not influence `brainstorming` unless something inside Superpowers pointed
at it. The `loop-001-4` reviewer (GPT-5.6 Sol) rejected that as unestablished:
the evidence showed only that upstream's `skills/` tree has no AP references,
which says nothing about harness-level instruction injection.

The reviewer was right, and the design spec had already answered it:

- §7.2 host table (spec lines 206-209): *"fenced block in `CLAUDE.md`"* for
  Claude Code; *"fenced block in `AGENTS.md`"* for Codex, OpenCode and Cursor.
- Spec line 281: *"`aaw init` merges a fenced routing block into existing
  `AGENTS.md` and/or `CLAUDE.md`; it does not replace user-authored content.
  Re-running it is idempotent."*
- Spec lines 598-599 name the deliverable directly.

**The host instruction file is read before any skill loads, in every supported
harness, and AAW's installer owns it.** That is the hook. It can carry SP-1,
SP-2 (Architectural path only), and the AP-companion pointer, with no patch on
Superpowers at all.

Two consequences, both inverting the original conclusion:

- **Zero-patch is the expected end state, not an upstream-dependent hope.** It
  does not require `obra/superpowers` to accept anything. §13.3's *"preferably
  `mirror`"* is reachable under AAW's own control.
- **SP-4a is redundant, not load-bearing.** Keeping it would mean maintaining a
  patch on another project's repository to duplicate a mechanism AAW already
  installs. Its verdict flips to do-not-port.

After this correction the fork patch reduces to **SP-3 alone** — an
unconditional brainstorming improvement with no AAW content. See F4 of the gate
review: SP-3 is now the entire remaining obstacle to `mirror` state.

### Finding 2 — the patch uses two different AP detection probes

`.claude/skills/phase-plan-creator/SKILL.md` (SP-1, SP-2, and SP-4a's entry)
versus `.claude/commands/plan-and-phase.md` (SP-4a's flow-graph diamond). Both
targets exist in Advanced Planning v0.16.0, so neither branch is currently dead
and the inconsistency has never produced a visible fault. It is still a defect:
two probes for one question can disagree the moment either file moves, and the
failure would be a silent half-integration.

The port collapses both to **one** manifest query. Recorded here so that collapse
reads as a deliberate fix rather than as the porter dropping a condition they did
not understand.

### Finding 3 — upstream AP already ships the mirror image of SP-4

`core/skills/companion-detection/SKILL.md` in Advanced Planning v0.16.0 detects
Superpowers and Plannotator and recommends them once per session. It states that
integration *"happens automatically via the brainstorming skill's conditional
terminal state"* and *"via plan-and-phase Step 5b"* — i.e. it already documents
SP-2 as an assumed part of the system, from the other side.

Two consequences:

1. **The two directions are complementary, not duplicates.** AP -> Superpowers is
   handled by `companion-detection`; Superpowers -> AP is SP-4a and has no other
   home. A Superpowers session with no AP installed will never load an AP skill,
   so `companion-detection` cannot substitute for SP-4a. This is independent
   corroboration of Finding 1.
2. **`companion-detection` uses `.claude/…` probes too**, so it carries the same
   §7.3 host-neutrality problem. Out of scope for this loop; worth a follow-on
   against `advanced-planning`, alongside the Plannotator issue from SP-4b.

---

## Consolidated verdict table

| Intent | File | Detection today | Verdict | Destination |
|---|---|---|---|---|
| SP-1 design-doc location | `brainstorming` | `.claude/skills/phase-plan-creator/SKILL.md` | **Port** | Fenced routing block in `AGENTS.md` / `CLAUDE.md`; manifest detection |
| SP-2 terminal state | `brainstorming` | `.claude/skills/phase-plan-creator/SKILL.md` | **Port — Architectural path only** | Fenced routing block; manifest detection. Spike and Bounded paths untouched (`loop-001-3`) |
| SP-3 AskUserQuestion | `brainstorming` | none (unconditional) | **Do not port** | Upstream `obra/superpowers` contribution; held in the fork patch until upstream rules |
| SP-4a AP companion entry | `using-superpowers` | two probes (Finding 2) | **Do not port** | Superseded by the fenced routing block, which is read earlier and is AAW-owned (Finding 1) |
| SP-4b Plannotator entry | `using-superpowers` | `.claude/commands/plannotator-annotate.md` OR plugin | **Do not port** | Nowhere — dropped; Plannotator deprecated 2026-08-26. Upstream AP's `companion-detection` still names it: separate defect |

---

## Dependency, and what implementation must not assume

**Every "manifest detection" above depends on the installation manifest from
phase-4 loop-003** — `.aaw/detect.py`, `.aaw/installed.schema.json`,
`.aaw/installed.example.json`, `tools/aaw-audit.py`. Those exist only on
`origin/feat/aaw-packaging-repair` and are **not merged into
`docs/herdr-v0.2-import`**. Starting `ralph-loop-002` without them forces a
`.claude/…` probe back in, which §7.3 forbids. That merge is a hard precondition,
not a convenience.

Three things implementation must not do:

1. **Do not copy the two patched files.** They are forked from `f2cbfbe`;
   upstream has moved 241 commits since. A copy would revert upstream's evolved
   router. `loop-001-3` quantifies exactly what would be lost.
2. **Do not apply SP-2 to all three router paths.** `loop-001-3` has reported:
   it attaches to the Architectural path only. Spike and Bounded must be left
   exactly as upstream has them.
3. **Do not put AAW routing in a skill file and assume it gets read.** It goes in
   the fenced `AGENTS.md` / `CLAUDE.md` block that `aaw init` merges (Finding 1).
   A skill nobody is told to load has no effect.

## Entry criteria for `ralph-loop-002`

Raised by the `loop-001-4` reviewer (F5) as things an implementer would otherwise
have to guess. All three must be settled before the port starts:

1. **The manifest predicate.** Which field of `.aaw/installed.json`, read how,
   means "Advanced Planning is present". Blocked on the unmerged `.aaw/detect.py`
   above.
2. **Fenced-block precedence.** What the block says when the host instruction file
   already carries user-authored guidance that conflicts — `aaw init` is specified
   as idempotent and non-replacing, so the routing text must be additive and must
   not assert authority over user instructions.
3. **Acceptance criteria.** The with-AP and without-AP behavioural tests that
   prove the Architectural handoff changed and that Spike and Bounded did not.
   §13.3(4) requires these to pass before the fork state may move to `mirror`.

---

## Check satisfaction

| Check | Where satisfied |
|---|---|
| all four intents present with a verdict each | SP-1, SP-2, SP-3, SP-4 (split 4a/4b) above; verdict table |
| each do-not-port verdict states where that behaviour goes instead | SP-3 -> upstream `obra/superpowers`; SP-4b -> dropped, with the reason and the separate upstream-AP defect named |
