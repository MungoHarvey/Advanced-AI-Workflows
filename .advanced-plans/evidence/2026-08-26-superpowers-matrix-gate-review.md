# Cross-model design gate — Superpowers behaviour matrix

**Loop**: `phase-5` / `ralph-loop-001` — todo `loop-001-4`
**Gate**: human (ACC-18 cross-model review). **Status: PASSED 2026-08-26** — reviewer verdict was BLOCKED; both blocking findings resolved and the major finding decided at the human gate.

| Role | Provider | Model |
|---|---|---|
| Matrix author | `claude` (AAW controller session) | **Claude Opus 5** |
| Upstream evidence | `opencode` (herdr `spread3`, pane `w2:p4`) | **Qwen3.5 397B** (`elm/Qwen/Qwen3.5-397B-A17B-FP8`) |
| **Gate reviewer** | `codex` (herdr `spgate2`, pane `w2:p6`) | **GPT-5.6 Sol** (Codex CLI v0.149.1) |

Author and reviewer are different providers and different models. **ACC-18
satisfied.**

**Documents reviewed**: `2026-08-26-superpowers-behaviour-matrix.md` and
`2026-08-26-upstream-superpowers-drift.md`, both in full.

---

## Reviewer verdict: **BLOCKED**

Two blocking findings, one major, two explicit no-findings.

---

## Findings, and the controller's assessment of each

### F1 — Q1 coverage — **no finding**

Reviewer: *"SP-1 through SP-4 have explicit verdicts; SP-4 is explicitly split
into 4a and 4b. SP-3 names upstream as its destination, and SP-4b explicitly says
it is dropped."*

Controller: agreed. `loop-001-2`'s two checks are met.

**Resolution: none required.**

---

### F2 — **BLOCKING** — Finding 1's "only hook point" claim is not established

Reviewer, against the matrix's *Finding 1*: the claim rests on the evidence
document, which only shows that upstream's `skills/` tree has no AP references.
It *"does not examine AAW/harness-level instruction injection, startup
instructions, installation-time routing registration, or other mechanisms that
can instruct an agent to read an AAW-owned routing skill before or alongside
brainstorming. Such a mechanism could affect behaviour without modifying
Superpowers."*

**Controller: the reviewer is right, and the defect is worse than it states.**
The mechanism is not merely unexamined — **the programme's own design spec
already specifies it**:

- §7.2 host table (spec lines 206-209): *"fenced block in `CLAUDE.md`"* for
  Claude Code, *"fenced block in `AGENTS.md`"* for Codex, OpenCode and Cursor.
- Spec line 281: *"`aaw init` merges a fenced routing block into existing
  `AGENTS.md` and/or `CLAUDE.md`; it does not replace user-authored content.
  Re-running it is idempotent."*
- Spec lines 598-599 name exactly that deliverable: *"small fenced `AGENTS.md`
  routing block shared by Codex/OpenCode/Cursor; updated fenced `CLAUDE.md` block
  for Claude-only mechanics."*

A fenced routing block in the host instruction file is read **before any skill
is loaded**, in every supported harness, and is installed by AAW's own installer
rather than patched into somebody else's repository. It can carry SP-1, SP-2
(Architectural path only) and SP-4a's companion pointer without touching
Superpowers at all.

**Consequence: Finding 1 was wrong, and its conclusion inverts.** Zero-patch is
not contingent on upstream accepting anything. It is achievable with a mechanism
the design already mandates. SP-4a stops being load-bearing and becomes a
*redundant* fork patch — the fenced block supersedes it.

The matrix has been corrected accordingly (see *Corrections applied* below). The
correction is recorded rather than quietly folded in, because the original claim
would have committed the port to a permanent fork patch that the design does not
need.

**Proposed resolution: ACCEPT — corrected.** Requires human confirmation.

---

### F3 — Q3 internal consistency — **no finding**

Reviewer: *"The prose and consolidated table agree. The Architectural-only SP-2
constraint follows from the quoted router: only Architectural proceeds to a
written spec and writing-plans; Spike and Bounded have distinct terminal
outcomes."*

Controller: agreed — and this independently corroborates the `loop-001-3`
refinement.

**Resolution: none required.**

---

### F4 — **MAJOR** — SP-3's disposition is indefinite

Reviewer: SP-3 is labelled *do not port*, but its actual disposition is
indefinite retention in the fork pending an upstream decision. *"That does not
resolve the fork divergence or provide a decision if upstream is silent."* The
matrix covers acceptance and rejection but is silent on non-response, timing,
ownership, and the criterion for retention versus removal.

**Controller: correct.** The gap is real. Note it also interacts with F2: once
the fenced-block mechanism removes SP-1, SP-2 and SP-4a from the patch, **SP-3
becomes the *entire* remaining reason the fork is not a pure mirror.** An
unbounded "pending upstream" on SP-3 therefore blocks the §13.1 `mirror` state
indefinitely, on a change that has nothing to do with AAW.

This one is a genuine judgement call and is **for the human to decide** — see the
options presented at the gate.

**Proposed resolution: HUMAN DECISION REQUIRED.**

---

### F5 — **BLOCKING** — no integration contract

Reviewer: an implementer must guess how AAW-owned routing is *"discovered,
loaded, and made authoritative relative to brainstorming"*. Also unspecified:
the manifest query that establishes AP presence, the supported harnesses, and
how the routing instruction preserves upstream's three-path flow while changing
only the Architectural terminal handoff.

**Controller: correct, and partly resolved by F2's correction.** Discovery,
loading and precedence are now answered — the fenced block in the host
instruction file, installed by `aaw init`, per the §7.2 host table. Supported
harnesses are that table's four rows. What remains genuinely unspecified:

1. **The manifest predicate.** Exactly which `.aaw/installed.json` field, read
   how, means "Advanced Planning is present". This is blocked on the unmerged
   `.aaw/detect.py` from phase-4 loop-003 — already recorded in the matrix's
   *Dependency* section as a hard precondition.
2. **Acceptance criteria.** The with-AP / without-AP behavioural tests that
   prove the Architectural handoff changed and Spike/Bounded did not. §13.3(4)
   requires these before the fork state can move to `mirror`.

Both are `ralph-loop-002` scope, but the reviewer is right that the matrix
should say so rather than leave it implicit.

**Proposed resolution: ACCEPT — partly corrected, remainder assigned to
`ralph-loop-002` as explicit entry criteria.** Requires human confirmation.

---

## Corrections applied to the matrix

Applied by the controller after the review, before the human gate:

1. **Finding 1 rewritten.** The "only hook point" claim is withdrawn and
   replaced with the fenced `AGENTS.md` / `CLAUDE.md` routing block, cited to
   spec lines 206-209, 281 and 598-599. Zero-patch is now the expected end
   state, not an upstream-dependent hope.
2. **SP-4a's verdict changed** from *port, load-bearing* to *do not port — the
   fenced routing block supersedes it*, with the destination named.
3. **Consolidated verdict table** updated to match.
4. **"What implementation must not assume"** updated: the "nothing loads it"
   warning is removed as false; the manifest predicate and the with/without-AP
   acceptance tests are added as explicit `ralph-loop-002` entry criteria.

The matrix as reviewed is recoverable at tag `checkpoint/loop-001`.

---

## Human resolution — 2026-08-26

| Finding | Severity | Proposed | Human resolution |
|---|---|---|---|
| F1 coverage | none | — | — |
| F2 hook-point claim | blocking | Accept — corrected | **Accepted.** Matrix Finding 1 rewritten; SP-4a's verdict reversed to do-not-port |
| F3 consistency | none | — | — |
| F4 SP-3 disposition | major | Human decision | **Resolved: put SP-3 in the fenced routing block.** See below |
| F5 integration contract | blocking | Accept — partly corrected, rest to loop-002 | **Accepted.** Discovery/loading/precedence answered in Finding 1; manifest predicate, precedence rule and with/without-AP acceptance tests written into the matrix as explicit `ralph-loop-002` entry criteria |

### F4 as decided

SP-3's substance — *present choices as structured options rather than prose* — is
an instruction about how to talk to a user, and the host instruction file is where
AAW is entitled to say that. It goes in the fenced `AGENTS.md` / `CLAUDE.md`
block, the same mechanism as SP-1, SP-2 and SP-4a's pointer. No deadline, no
owner, no dependency on a third party, because nothing is being held anywhere.

An upstream PR to `obra/superpowers` remains worth offering — the improvement is
genuinely general — but it is now optional generosity. Nothing in AAW waits on it.

**Consequence: the fork patch goes to zero.** All four intents are delivered by
AAW-owned mechanisms; Superpowers becomes a §13.1 `mirror` with no holding
position. That is the design's stated preferred end state (§13.3), reached
without needing upstream to accept anything.

**Gate status: PASSED.** Both blocking findings resolved, the major finding
decided. `ralph-loop-002` is unblocked on design grounds — it remains blocked on
the packaging-repair merge (the manifest dependency), which is a separate matter.
