# Phase 5: Superpowers Behavioural Port

Workstream 1A (Superpowers half) of the v0.2 design. Deliberately a separate, higher-risk review
lane from the gstack sync.

## Objective

Preserve the integration behaviour the Superpowers fork carries, without replaying its stale files
over an upstream that has moved underneath them. The preferred outcome is that the behaviour moves
into AAW-owned routing and the fork becomes a pure mirror with zero patch.

## Scope

### Included

- Write and review the behaviour matrix before any implementation begins.
- Create the port branch from current `upstream/main`, never by copying the stale fork files.
- Reimplement SP-1, SP-2, and the Advanced Planning half of SP-4 — preferably as AAW-owned routing
  rather than as a fork patch.
- Prove the current upstream three-path router is preserved.
- Verify behaviour both with and without Advanced Planning present — ACC-04 and ACC-05.

### Explicitly NOT included

- **SP-3** (use `AskUserQuestion` for clarifying questions). Host-generic UX, not AAW-specific.
  Propose it upstream separately; do not carry it as a fork patch.
- **The Plannotator half of SP-4.** Deprecated 2026-08-26. The companion-tools recommendation keeps
  the Advanced Planning half only.
- Host-specific `.claude/…` detection probes. Design §7.3 forbids them in host-neutral core; the
  port needs the installation manifest from Phase 4.

## Key Deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Behaviour matrix (reviewed) | Markdown | `.advanced-plans/evidence/<date>-superpowers-behaviour-matrix.md` |
| Port branch | Git branch | `superpowers`: `port/aaw-routing-<date>` |
| AAW-owned routing | Markdown skills/guidance | `.claude/skills/` and `.agents/skills/` in AAW |
| With/without-AP test evidence | Markdown | `.advanced-plans/evidence/<date>-superpowers-port.md` |

## Success Criteria

- ✓ The behaviour matrix is written and reviewed **before** any implementation todo starts.
- ✓ The port branch's first commit is current `upstream/main`, provable with `git log`.
- ✓ SP-1 holds: an approved design lands in `.advanced-plans/specs/` when Advanced Planning is
  present, and in the upstream default location when it is not.
- ✓ SP-2 holds: the terminal state routes to phase planning when Advanced Planning is present, and
  to upstream `writing-plans` when it is not.
- ✓ SP-4 (AP half only) holds: the companion-tools recommendation names Advanced Planning and does
  not name Plannotator.
- ✓ The upstream "Three Paths" router present at current upstream head is intact — verified by
  diffing the section, not by asserting it.
- ✓ ACC-05: with Advanced Planning absent, no AAW path is fabricated anywhere in the output.
- ✓ Detection is host-neutral: no `.claude/…` probe remains in any ported logic.
- ✓ A provider different from the implementer reviewed the port and its verdict is recorded.

## Amendment — 2026-08-26, after the loop-001 design gate

The behaviour matrix and its cross-model gate (reviewer `codex`/GPT-5.6 Sol, author `claude`/Opus 5)
changed three things this plan had assumed. The original text above is left intact for provenance;
where the two disagree, **this amendment governs, and it is what the phase-5 gate checks.**

**1. There is no port branch, because there is no patch.** The plan assumed SP-4a had to be carried
as a fork patch so that something inside Superpowers would point at AAW's routing. Design spec
lines 206-209, 281 and 598-599 already mandate a fenced routing block that `aaw init` merges into
`AGENTS.md` and/or `CLAUDE.md`, read before any skill loads, in every supported harness. That block
is the hook, AAW owns it, and it makes the fork patch zero. `port/aaw-routing-<date>` is therefore
replaced by a local mirror branch plus a backup tag on the pre-port fork head `fde9f97`.

**2. SP-3 is delivered, not given away.** "Explicitly NOT included" above is superseded by the
gate's F4 resolution and the operator's decision: the `AskUserQuestion` instruction goes into the
same fenced block. It is an instruction about how an agent talks to a user, and the host instruction
file is exactly where AAW may say that. An upstream PR to `obra/superpowers` becomes optional
generosity rather than a dependency.

**3. SP-4a is not ported.** "the Advanced Planning half of SP-4" is reversed to do-not-port for the
same reason as (1) — the fenced block is read earlier than any Superpowers skill, so a companion
pointer inside the fork is redundant. Upstream Advanced Planning already ships its own
`core/skills/companion-detection/SKILL.md`, which is the mirror image of SP-4 and still names the
deprecated Plannotator; that is a defect to report against `advanced-planning`, not something to
duplicate here.

### Amended deliverables

| Deliverable | Format | Location |
|-------------|--------|----------|
| Backup tag + local mirror branch | Git refs | `superpowers`, local only — no remote write in this phase |
| AAW-owned routing | Fenced block, two host variants | `.claude/skills/setup-with-claude/references/` in AAW |
| With/without-AP test evidence | Markdown | `.advanced-plans/evidence/<date>-superpowers-port.md` |

### Amended success criteria

- ✓ Supersedes "the port branch's first commit is current `upstream/main`":
  `git diff upstream/main..<mirror branch>` is **empty**. A non-empty diff is a failed port.
- ✓ Supersedes "SP-4 (AP half only) holds": SP-4a is **absent** from the fork, and the fenced block
  carries the companion recommendation instead, naming Advanced Planning and not Plannotator.
- ✓ Added: SP-3 is present in the fenced block.
- ✓ Added: SP-2 attaches to the **Architectural** path only. Spike- and Bounded-classified requests
  must produce no spec file and must not invoke phase planning — tested, not asserted.
- ✓ Added: detection reads `.aaw/installed.json` → `components["advanced-planning"]["installed"]`.
  A `.advanced-plans/` directory is data, not an installation, and does not satisfy the predicate.
- ✓ Added: the installer merges the block idempotently — a second run leaves the instruction file
  byte-identical, and user-authored content survives verbatim.
- ✓ Unchanged and still binding: SP-1, SP-2 with/without AP (ACC-04, ACC-05), the Three Paths router
  intact, host-neutral detection, and a different-provider review (ACC-18).

**Not authorised by this amendment.** Publishing the mirror requires force-pushing `origin/main` in
the Superpowers fork, which the kickoff prompt places outside the controller's authority. Phase 5
prepares and proves the mirror locally and stops at a human gate.

## Dependencies

### Must complete before this phase

- Phase 3 — the execution layer.
- **Phase 4 loop 003** — the installation manifest. Host-neutral detection has nothing to read
  until it exists. Starting the port before it forces a `.claude/…` probe back in.

### Blocked by

- The behaviour matrix review. The design is explicit: do not begin the implementation port until
  the matrix is written and reviewed.

### Optional

- Upstream promotion of SP-3. A separate conversation with `obra/superpowers`, not part of v0.2.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Replaying the stale fork files destroys the upstream three-path router | **High if attempted** | High | Branch from upstream and reimplement. Never copy the fork files. Diff the router section explicitly as a check |
| The AAW-owned routing does not actually fire, so SP-1/SP-2 silently regress | Medium | High | Test the behaviour, not the file contents: run the flow with and without Advanced Planning and check where the output lands |
| Host-neutral detection is not ready and a `.claude/` probe creeps back | Medium | Medium | Phase 4 loop 003 is a hard dependency; a grep for `.claude/` in ported logic is a check, not a review note |
| The fork ends up with a patch anyway | Medium | Low | Acceptable if the patch is the smallest host-neutral one against current upstream and is justified in writing. Mirror is preferred, not mandatory |
| Upstream moves during the port | Medium | Medium | Re-fetch and re-record at execution time; rebase the port onto current upstream rather than merging stale state forward |

## Assumptions

- `The fork's net patch is exactly two skill files` — validated in baseline audit §2.4 against the
  fresh clone; re-verify at execution time.
- `Upstream contains zero references to advanced-planning or plannotator` — validated by inspection;
  this is why the port cannot be a file copy.
- `AAW-owned routing can express SP-1 and SP-2` — to be proven by the with/without-AP tests, not
  assumed. If it cannot, a minimal fork patch is the fallback and must be justified.

## Notes / Design Decisions

- **Behaviour matrix first.** This phase's whole risk is that someone treats a two-file diff as a
  two-file copy. Writing down what the diff *means* before touching anything is the mitigation.
- **The fork as a mirror is the goal, not the requirement.** If a patch survives review as genuinely
  necessary, it is acceptable — as long as it is host-neutral, minimal, and against current upstream.
- **SP-3 is being given away, not dropped.** It is good UX that belongs upstream where everyone gets
  it, rather than in a private fork where it is maintenance cost.

## Ralph Loops (2)

| Loop | Name | Type | Key Outputs |
|------|------|------|-------------|
| 001 | behaviour-matrix | Investigation | The four intents documented and reviewed, with an explicit port/do-not-port verdict and the reason for each |
| 002 | routing-port | Implementation | SP-1, SP-2, SP-3 and the companion pointer delivered through the fenced AGENTS.md/CLAUDE.md block; fork taken to a zero-patch mirror locally; with/without-AP behaviour proven; cross-model review recorded (see the 2026-08-26 amendment) |
