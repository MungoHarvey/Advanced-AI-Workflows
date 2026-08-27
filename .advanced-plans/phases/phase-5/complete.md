---
phase: 5
title: "Superpowers Behavioural Port"
status: passed
gate_verdict_ref: .advanced-plans/gate-verdicts/phase-5-attempt-1-*.json
gate: attempt-1 PASS — codex 91, code-review-agent 78, phase-goals-agent 84; zero failed criteria, no loops to revert
anchor_sha: 74252ee
end_sha: (this commit)
loop_count: 2
todos: 11/11
created: 2026-08-26T20:55:00Z
---

## Goals met

- **The fork carries no patch at all.** The whole point of the phase inverted itself early: all
  four Superpowers intents (SP-1 spec location, SP-2 terminal-state routing, SP-3
  AskUserQuestion, SP-4 companion tools) are delivered by an AAW-owned fenced block in the
  user's instruction file, so nothing needs to be forked. `git diff upstream/main..mirror/upstream-2026-08-26`
  is empty; the mirror and upstream are the same commit. A port whose measured patch is zero is
  the strongest form of the deliverable, not a failure to deliver it.
- **The block is delivered, not merely written.** Verified 2026-08-26 that opencode auto-loads a
  project `AGENTS.md` before the first user message — a context probe quoted the block back
  verbatim having run no tool at all. The installer merges it into `AGENTS.md` as well as
  `CLAUDE.md`, idempotently, preserving user content byte-for-byte.
- **Behaviour is proven in both directions, not asserted.** Seven acceptance rounds against
  fixtures with and without Advanced Planning. SP-1 puts an approved design in
  `.advanced-plans/specs/` when AP is present and in the upstream default when it is not; SP-2
  routes the terminal step to phase planning or to `writing-plans` on the same predicate.
- **Detection is host-neutral and manifest-driven.** The installation predicate is
  `.aaw/installed.json` → `components["<name>"]["installed"] == true`. The block contains zero
  `.claude/`, `.cursor/`, `.opencode/` or `.agents/` paths, and says in terms that a
  `.advanced-plans/` directory is data, not an installation — proven against a decoy fixture
  that holds exactly that directory and is correctly ignored.
- **Every companion-tool route is gated, with a default-deny rule behind it.** Closed at the
  gate's predecessor review — see below.
- **Plannotator is gone from the routing surface**, present only as an explicit do-not-use
  instruction.

Suite at the end of the phase: packaging 4/4, idempotency 56/56 — re-run independently by the
gate's `phase-goals-agent` rather than taken from the loop record, and the mutation evidence
(`grep -c MUTANT project_ops.py` → 0) re-derived with it.

## Exit gate

**PASS on attempt 1**, three reviewers on three backends, none of them the implementer: codex
(`gpt-5.6-terra`/medium, 91), opencode/Qwen3.5-397B as `code-review-agent` (78), and claude/Opus
as `phase-goals-agent` (84). All three returned `pass_with_findings`. **No reviewer failed a
criterion and none named a loop to revert.**

One **major** finding, from the Claude reviewer alone, and it was real: a second, tracked copy of
the fenced routing block still shipping at the repository root as
`references/claude-md-routing.md` — 87 lines, CRLF, last touched at `2f17deb`, carrying three
`.claude/` probes and seven ungated route arrows. Both of the defect classes this phase exists
to eliminate, preserved intact in a file nobody had opened.

Verified by the controller rather than taken on trust, then traced. That file and
`references/settings-snippet.json` were **phase-1 loop-001 outputs**, written when the repo root
was where reference material lived. Phase 4's packaging repair moved the canonical copies under
`.claude/skills/setup-with-claude/references/` and made those the shipped, tested,
`required-sources.txt`-enforced ones — and left the originals behind. The snippet stayed
byte-identical to its twin; the routing block drifted, because every improvement from the port
landed on the canonical copy and none landed on the orphan.

Both superseded copies removed. `references/upstream-baseline-2026-08-26.json` stays: it is live
evidence, cited by `CHANGELOG.md:50` and by the baseline audit. Afterwards, no tracked file
carries an ungated route arrow except the evidence file quoting the old text as a
before-example, and the suites still pass. The fix landed *after* the reviewers saw the tree; the
user accepted the gate on that basis rather than re-gating, on the grounds that removing a file
that never shipped through the installer strictly improves a tree that had already passed.

## Findings carried forward

- **An unreferenced duplicate does not stay a duplicate.** The settings snippet is simply the
  copy that had not drifted yet. Two files, same orphaning event, and only the one anybody kept
  improving diverged. Any future "move the canonical copy" should delete the original in the
  same commit, not leave it as a courtesy.
- **The reviewer that found it was the one briefed on the criteria, not on the artefact.** The
  other two reviewed the work that had been done; the criteria-led reviewer went looking for
  every file a criterion could be about, and found one nobody had been working in. This is the
  phase-4 lesson in a new shape — convergence between models is only worth something when they
  looked in different places, and the brief is what decides where they look.
- **Two reviewers can be confidently wrong about the same thing.** At the loop-002-7 review,
  Qwen explicitly denied the ungated-route finding that codex had made and would, alone, have
  closed the gate with a clean bill on the very thing that was wrong. The controller read
  `claude-md-routing.md:42-86` and recorded which reviewer was right. **A gate that averages its
  reviewers is not a gate.**
- **A defect fixed as an instance is not a defect fixed.** F1 gated one route; R1 later found
  that eight others were ungated and that the six acceptance rounds could not have caught it,
  because every fixture had a well-formed manifest. The fix that closed it states the gate at
  the point of use with a named fallback, plus a default-deny rule so a future missed route
  fails safe.
- **A fixture stub that points outside itself is not a stub.** A sentinel reading "See the real
  copy; this is a sentinel only" sent a worker out of its own directory and into a permission
  dialog. Fixtures must be self-contained and say so.
- **An agent's self-reported model is not evidence.** codex named `gpt-5.6-sol` twice in this
  programme against `gpt-5.6-terra` in both `config.toml` and the `argv` echoed at start.

## Reconciliation with the plan

The plan's original success criteria assumed a fork carrying a patch. Two of them —
*"the port branch's first commit is current `upstream/main`"* and *"SP-4 (AP half only)
holds"* — were superseded by the **Amendment of 2026-08-26**, written after the loop-001 design
gate established that the right shape was a zero-patch mirror plus an AAW-owned block. Both
reviewers who reached those criteria marked them `not_applicable` and cited the amendment. The
supersession is recorded in `plan.md` where the reviewers could see it, not applied silently.

`phase-goals-agent` flagged, correctly, that **two acceptance checks were reinterpreted after
the run they judge, by the party that produced the result** (loop-002-5's grep scope; loop-002-4's
assertion) and one was amended mid-loop (loop-002-2's Plannotator check). It judged each
legitimate on its merits and flagged the pattern rather than the instances. The pattern is the
finding and it is recorded here rather than argued away.

## Opened

- **Every behavioural round measured one harness.** All seven acceptance rounds ran under
  opencode. The block is installed for Claude Code and for any `AGENTS.md` reader too, and
  neither has been measured. All three gate reviewers named this independently and all three
  judged it non-disqualifying; the Claude reviewer named the five criteria it touches (SP-1,
  SP-2, ACC-05, the amended Architectural-path-only criterion, and ACC-04 by extension). It
  weakens confidence in each without failing any.
- **The behavioural evidence is not independently re-derivable.** The fixtures, the
  `ACC-RESULT.md` reports and the worker transcripts live in the session scratchpad, so a later
  reviewer has the narrative and not the artefacts. The strongest argument yet for tracking the
  fixtures under `tests/`.
- **The mirror is prepared, not published.** `origin/main` in the superpowers fork is still
  `fde9f97` and still carries all four intents. Publishing needs
  `git push origin mirror/upstream-2026-08-26:main --force-with-lease`, which is outside the
  controller's authority and is the user's to run.
- **The branch picture recorded here was wrong, and was corrected on 2026-08-27.**
  `fix/install-audit-diverged-state` does not exist, locally or on the remote — its
  work (`3ae6121`, `6e94cf5`) is inside `feat/aaw-packaging-repair`. That branch's
  pushed tip `360ab3c` is already an ancestor of `docs/herdr-v0.2-import`, so a pull
  request from it to `main` would be a strict subset of the controller branch. What is
  genuinely unlanded is a single local commit, `3b19a49`, which resolves every
  installer-owned global path from `%USERPROFILE%` instead of `~`; it is unpushed and
  in neither branch. `main` is 50 commits behind the controller branch and adds
  nothing to it. So there is **one** pull request to open, not two.
- **Two block defects were found after the gate, on 2026-08-27, and fixed in `cd920df`.**
  The cross-runtime adherence round that closes the one-harness limitation above also found
  that the Closing Instruction gated `/gstack-to-plans` on **gstack** rather than on
  `gstack-to-plans` — the R1 class at a twelfth site, missed because the route *was* gated,
  just on the wrong component — and that the block named a literal `~/.gstack/...` path,
  which resolves to the `M:` network drive on this machine. Both were found by a runtime
  rather than a reviewer, and the first was caught by loop-002-7's default-deny catch-all
  paying out on a gate that was already wrong when it was written. Recorded post-gate on
  the same precedent as the orphan-file removal above; suites re-run and installer delivery
  re-verified. See `.advanced-plans/evidence/2026-08-27-cross-runtime-adherence.md`.
- **The glue skill still has zero AskUserQuestion callouts** although phase 1 accepted it on
  having them at three ambiguous branches. Carried from phase 4, unchanged.
- **`.advanced-plans/installed.json` schema question left open by `63f029a`**: whether the
  manifest should carry `data_directories`.
